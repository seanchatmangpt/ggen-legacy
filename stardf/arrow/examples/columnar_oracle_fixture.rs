//! Lane 12 (2026-10-31): deterministic five-table Parquet fixture for the
//! external DuckDB columnar oracle (`stardf/arrow/scripts/check-columnar-oracle.sh`).
//!
//! Ported from purrdf's `write_oracle_fixture.rs` +
//! `crates/columnar/src/{parquet,compact}.rs` hand-rolled Data Page V2 /
//! Thrift-compact writer. stardf-columnar (the full five-table codec wave) is
//! landing concurrently; until it exposes a lib target, this fixture
//! generates through the real present substrate — `stardf-arrow-core`
//! (`TermArena::intern` + `StardfBatch::push` of `Quad64`) — and serializes
//! the five purrdf-shaped tables itself with the same minimal writer design
//! (uncompressed, PLAIN, Data Page V2, required-only columns).
//!
//! Chicago discipline: real terms interned, real quads pushed, real bytes on
//! disk; DuckDB observes the physical file, never our in-memory claim.

// Compiled by the oracle script via `rustc --extern` against the built
// `stardf-arrow-core` rlib; referenced by canonical crate name only.

use std::env;
use std::fs;
use std::path::PathBuf;

use avec_arrow::layout::Quad64;
use stardf_arrow_core::arena::{Resident, TermArena};
use stardf_arrow_core::batch::StardfBatch;

// ---------------------------------------------------------------------------
// Minimal deterministic Parquet writer (subset port of purrdf columnar
// parquet.rs + compact.rs: uncompressed, PLAIN, Data Page V2, required-only).
// ---------------------------------------------------------------------------

const PARQUET_MAGIC: &[u8; 4] = b"PAR1";
const PARQUET_TYPE_INT64: i32 = 2;
const PARQUET_TYPE_BYTE_ARRAY: i32 = 6;
const REPETITION_REQUIRED: i32 = 0;
const CONVERTED_TYPE_UTF8: i32 = 0;
const ENCODING_PLAIN: i32 = 0;
const CODEC_UNCOMPRESSED: i32 = 0;
const PAGE_TYPE_DATA_V1: i32 = 0;
const FILE_VERSION: i32 = 1;

// -- Thrift compact protocol (port of purrdf compact.rs writer half) -------

const TYPE_STOP: u8 = 0;
const TYPE_I32: u8 = 5;
const TYPE_I64: u8 = 6;
const TYPE_BINARY: u8 = 8;
const TYPE_LIST: u8 = 9;
const TYPE_STRUCT: u8 = 12;

fn write_varint(out: &mut Vec<u8>, mut value: u64) {
    loop {
        let byte = (value & 0x7f) as u8;
        value >>= 7;
        if value == 0 {
            out.push(byte);
            break;
        }
        out.push(byte | 0x80);
    }
}

fn zigzag_encode(value: i64) -> u64 {
    ((value << 1) ^ (value >> 63)) as u64
}

#[derive(Default)]
struct CompactWriter {
    bytes: Vec<u8>,
    last_fields: Vec<i16>,
}

impl CompactWriter {
    fn root(build: impl FnOnce(&mut Self)) -> Vec<u8> {
        let mut writer = Self::default();
        writer.write_struct(build);
        writer.bytes
    }

    fn write_struct(&mut self, build: impl FnOnce(&mut Self)) {
        self.last_fields.push(0);
        build(self);
        self.bytes.push(TYPE_STOP);
        self.last_fields.pop().expect("balanced struct stack");
    }

    fn field_header(&mut self, id: i16, field_type: u8) {
        let previous = *self.last_fields.last().expect("inside a struct");
        let delta = id - previous;
        if (1..=15).contains(&delta) {
            self.bytes.push(((delta as u8) << 4) | field_type);
        } else {
            self.bytes.push(field_type);
            write_varint(&mut self.bytes, zigzag_encode(i64::from(id)));
        }
        *self.last_fields.last_mut().expect("inside a struct") = id;
    }

    fn i32_field(&mut self, id: i16, value: i32) {
        self.field_header(id, TYPE_I32);
        write_varint(&mut self.bytes, zigzag_encode(i64::from(value)));
    }

    fn i64_field(&mut self, id: i16, value: i64) {
        self.field_header(id, TYPE_I64);
        write_varint(&mut self.bytes, zigzag_encode(value));
    }


    fn string_field(&mut self, id: i16, value: &str) {
        self.field_header(id, TYPE_BINARY);
        write_varint(&mut self.bytes, value.len() as u64);
        self.bytes.extend_from_slice(value.as_bytes());
    }

    fn struct_field(&mut self, id: i16, build: impl FnOnce(&mut Self)) {
        self.field_header(id, TYPE_STRUCT);
        self.write_struct(build);
    }

    fn list_i32_field(&mut self, id: i16, values: &[i32]) {
        self.field_header(id, TYPE_LIST);
        self.list_header(values.len(), TYPE_I32);
        for &value in values {
            write_varint(&mut self.bytes, zigzag_encode(i64::from(value)));
        }
    }

    fn list_string_field(&mut self, id: i16, values: &[&str]) {
        self.field_header(id, TYPE_LIST);
        self.list_header(values.len(), TYPE_BINARY);
        for value in values {
            write_varint(&mut self.bytes, value.len() as u64);
            self.bytes.extend_from_slice(value.as_bytes());
        }
    }

    fn list_struct_field<T>(
        &mut self, id: i16, values: &[T], mut write: impl FnMut(&mut Self, &T),
    ) {
        self.field_header(id, TYPE_LIST);
        self.list_header(values.len(), TYPE_STRUCT);
        for value in values {
            self.write_struct(|writer| write(writer, value));
        }
    }

    fn list_header(&mut self, len: usize, element_type: u8) {
        if len < 15 {
            self.bytes.push(((len as u8) << 4) | element_type);
        } else {
            self.bytes.push(0xf0 | element_type);
            write_varint(&mut self.bytes, len as u64);
        }
    }
}

// -- Column encoding --------------------------------------------------------

enum ColumnValues {
    Int64(Vec<i64>),
    ByteArray(Vec<Vec<u8>>),
}

impl ColumnValues {
    fn len(&self) -> usize {
        match self {
            ColumnValues::Int64(values) => values.len(),
            ColumnValues::ByteArray(values) => values.len(),
        }
    }

    fn physical_type(&self) -> i32 {
        match self {
            ColumnValues::Int64(_) => PARQUET_TYPE_INT64,
            ColumnValues::ByteArray(_) => PARQUET_TYPE_BYTE_ARRAY,
        }
    }

    fn encode_plain(&self) -> Vec<u8> {
        let mut out = Vec::new();
        match self {
            ColumnValues::Int64(values) => {
                for value in values {
                    out.extend_from_slice(&value.to_le_bytes());
                }
            }
            ColumnValues::ByteArray(values) => {
                for value in values {
                    out.extend_from_slice(&(value.len() as u32).to_le_bytes());
                    out.extend_from_slice(value);
                }
            }
        }
        out
    }
}

struct Column {
    name: &'static str,
    utf8: bool,
    values: ColumnValues,
}

struct EncodedChunk {
    physical_type: i32,
    name: &'static str,
    num_values: i64,
    total_uncompressed_size: i64,
    total_compressed_size: i64,
    data_page_offset: i64,
    file_offset: i64,
}

/// Serialize one table to Parquet bytes: magic, one row group (absent when
/// the table is empty), compact-protocol FileMetaData footer.
fn write_table_parquet(columns: &[Column]) -> Vec<u8> {
    let row_count = columns[0].values.len();
    for column in columns {
        assert_eq!(column.values.len(), row_count, "ragged column");
    }

    let mut body: Vec<u8> = Vec::new();
    body.extend_from_slice(PARQUET_MAGIC);

    let mut chunks: Vec<EncodedChunk> = Vec::new();
    for column in columns {
        let plain = column.values.encode_plain();
        let header = CompactWriter::root(|writer| {
            writer.i32_field(1, PAGE_TYPE_DATA_V1);
            writer.i32_field(2, plain.len() as i32);
            writer.i32_field(3, plain.len() as i32);
            // DataPageHeader V1, written at the same delta-2 position and
            // field order parquet-cpp emits (byte pattern proven readable by
            // DuckDB 1.4.1 against a pyarrow plain file): num_values,
            // num_nulls, encoding PLAIN, def/rep level encodings RLE.
            writer.struct_field(5, |writer| {
                writer.i32_field(1, row_count as i32);
                writer.i32_field(2, 0); // num_nulls
                writer.i32_field(3, 3); // encoding = RLE (parquet-cpp pattern)
                writer.i32_field(4, 3); // definition_level_encoding = RLE
                writer.i32_field(5, 3); // repetition_level_encoding = RLE
            });
        });
        let page_start = body.len() as i64;
        body.extend_from_slice(&header);
        body.extend_from_slice(&plain);
        chunks.push(EncodedChunk {
            physical_type: column.values.physical_type(),
            name: column.name,
            num_values: row_count as i64,
            total_uncompressed_size: header.len() as i64 + plain.len() as i64,
            total_compressed_size: (body.len() as i64) - page_start,
            data_page_offset: page_start, // points at the page header start
            file_offset: 0,
        });
    }

    // ColumnChunk file_offsets: absolute positions; chunks sit back-to-back
    // after the magic, so walk the compressed sizes.
    let chunks: Vec<EncodedChunk> = chunks
        .into_iter()
        .scan(PARQUET_MAGIC.len() as i64, |offset, mut chunk| {
            chunk.file_offset = *offset;
            *offset += chunk.total_compressed_size;
            Some(chunk)
        })
        .collect();

    let footer = CompactWriter::root(|writer| {
        writer.i32_field(1, FILE_VERSION);
        // Schema: root node, then one SchemaElement per column.
        let nodes: Vec<Option<&Column>> = std::iter::once(None)
            .chain(columns.iter().map(Some))
            .collect();
        writer.list_struct_field(2, &nodes, |writer, node| match node {
            None => {
                writer.string_field(4, "schema");
                writer.i32_field(5, columns.len() as i32);
            }
            Some(column) => {
                writer.i32_field(1, column.values.physical_type());
                writer.i32_field(3, REPETITION_REQUIRED);
                writer.string_field(4, column.name);
                if column.utf8 {
                    writer.i32_field(6, CONVERTED_TYPE_UTF8);
                }
            }
        });
        writer.i64_field(3, row_count as i64);
        // Always emit exactly one row group (zero-row when the table is
        // empty): DuckDB's thrift reader refuses a metadata-only footer with
        // no row_groups field (TProtocolException, witnessed 2026-10-31).
        {
            let empty_group: Vec<EncodedChunk> = if row_count > 0 {
                Vec::new()
            } else {
                // Zero-row group: same chunk metadata, num_values 0, sizes 0,
                // offsets at end-of-body (no pages follow).
                let end = body.len() as i64;
                columns
                    .iter()
                    .enumerate()
                    .map(|(i, column)| EncodedChunk {
                        physical_type: column.values.physical_type(),
                        name: column.name,
                        num_values: 0,
                        total_uncompressed_size: 0,
                        total_compressed_size: 0,
                        data_page_offset: end,
                        file_offset: end + i as i64,
                    })
                    .collect()
            };
            let group: &[EncodedChunk] = if row_count > 0 {
                &chunks
            } else {
                &empty_group
            };
            writer.list_struct_field(4, std::slice::from_ref(&group), |writer, chunk_group| {
                writer.list_struct_field(1, chunk_group, |writer, chunk| {
                    writer.i64_field(2, chunk.file_offset);
                    writer.struct_field(3, |writer| {
                        writer.i32_field(1, chunk.physical_type);
                        writer.list_i32_field(2, &[ENCODING_PLAIN]);
                        writer.list_string_field(3, &[chunk.name]);
                        writer.i32_field(4, CODEC_UNCOMPRESSED);
                        writer.i64_field(5, chunk.num_values);
                        writer.i64_field(6, chunk.total_uncompressed_size);
                        writer.i64_field(7, chunk.total_compressed_size);
                        writer.i64_field(9, chunk.data_page_offset);
                    });
                });
                writer.i64_field(
                    2,
                    chunk_group.iter().map(|c| c.total_uncompressed_size).sum(),
                );
                writer.i64_field(3, row_count as i64);
                writer.i64_field(5, PARQUET_MAGIC.len() as i64);
                writer.i64_field(6, chunk_group.iter().map(|c| c.total_compressed_size).sum());
            });
        }
    });

    let mut out = body;
    out.extend_from_slice(&footer);
    out.extend_from_slice(&(footer.len() as u32).to_le_bytes());
    out.extend_from_slice(PARQUET_MAGIC);
    out
}

fn main() {
    let output = env::args_os()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| panic!("usage: columnar_oracle_fixture OUTPUT_DIRECTORY"));
    fs::create_dir_all(&output).expect("output directory");

    // Real fixture data through stardf-arrow-core: intern six terms, push
    // three real Quad64 records into a batch.
    let mut arena = TermArena::new(Resident);
    let lexemes = [
        "https://example.org/subject",
        "https://example.org/predicate",
        "https://example.org/object-integer",
        "https://example.org/graph",
        "https://example.org/object-string",
        "https://example.org/reifier",
    ];
    let mut ids = Vec::new();
    for lex in lexemes {
        ids.push(arena.intern(lex).expect("intern"));
    }
    assert_eq!(ids, vec![1, 2, 3, 4, 5, 6], "arena ids are dense from 1");

    let mut batch = StardfBatch::new();
    let digest: [u8; 32] = core::array::from_fn(|i| (i as u8) + 1);
    let quads = [
        Quad64::new(ids[0], ids[1], ids[2], ids[3], 1_000, 1, 0x3, digest),
        Quad64::new(ids[0], ids[1], ids[4], 0, 2_000, 2, 0x3, digest),
        Quad64::new(ids[5], ids[1], ids[2], 0, 3_000, 3, 0x1, digest),
    ];
    for quad in quads {
        batch.push(quad).expect("batch push");
    }
    assert_eq!(batch.len(), 3);

    // Five tables, purrdf shape. reifiers/annotations are deterministic
    // empty tables (schema-only files, zero row groups).
    let term_lex: Vec<Vec<u8>> = lexemes.iter().map(|s| s.as_bytes().to_vec()).collect();
    // Columns carry the three pushed quads row-for-row.
    let s_col: Vec<i64> = quads.iter().map(|q| i64::from(q.s_id)).collect();
    let p_col: Vec<i64> = quads.iter().map(|q| i64::from(q.p_id)).collect();
    let o_col: Vec<i64> = quads.iter().map(|q| i64::from(q.o_id)).collect();
    let g_col: Vec<i64> = quads.iter().map(|q| i64::from(q.g_id)).collect();

    let tables: Vec<(&str, Vec<Column>)> = vec![
        (
            "terms",
            vec![
                Column {
                    name: "id",
                    utf8: false,
                    values: ColumnValues::Int64((1..=6).map(i64::from).collect()),
                },
                Column {
                    name: "lex",
                    utf8: true,
                    values: ColumnValues::ByteArray(term_lex),
                },
            ],
        ),
        (
            "quads",
            vec![
                Column {
                    name: "s_id",
                    utf8: false,
                    values: ColumnValues::Int64(s_col.clone()),
                },
                Column {
                    name: "p_id",
                    utf8: false,
                    values: ColumnValues::Int64(p_col.clone()),
                },
                Column {
                    name: "o_id",
                    utf8: false,
                    values: ColumnValues::Int64(o_col.clone()),
                },
                Column {
                    name: "g_id",
                    utf8: false,
                    values: ColumnValues::Int64(g_col.clone()),
                },
            ],
        ),
        (
            "reifiers",
            vec![Column {
                name: "id",
                utf8: false,
                values: ColumnValues::Int64(Vec::new()),
            }],
        ),
        (
            "annotations",
            vec![Column {
                name: "id",
                utf8: false,
                values: ColumnValues::Int64(Vec::new()),
            }],
        ),
        (
            "blobs",
            vec![
                Column {
                    name: "id",
                    utf8: false,
                    values: ColumnValues::Int64(vec![1, 2]),
                },
                Column {
                    name: "bytes",
                    utf8: false,
                    values: ColumnValues::ByteArray(vec![
                        b"first payload".to_vec(),
                        b"second payload".to_vec(),
                    ]),
                },
            ],
        ),
    ];

    for (name, columns) in tables {
        let bytes = write_table_parquet(&columns);
        fs::write(output.join(format!("{name}.parquet")), bytes).expect("write table");
    }
}
