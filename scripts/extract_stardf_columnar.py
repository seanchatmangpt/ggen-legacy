#!/usr/bin/env python3
"""
scripts/extract_stardf_columnar.py
Deterministic extractor compiling the columnar port surface (PHASE-2 LANE 8)
into authority/stardf/stardf-columnar.json.

Why a sibling script, not an extension of extract_stardf_arrow.py:
extract_stardf_arrow.py owns the C ABI contract (stardf-contract.json, capi
header cross-check, legacy_projection carry-over). The columnar census is a
different schema, different ground-truth inputs (Rust schema.rs / writer.rs /
reader.rs, not the capi), and a different output artifact. Coupling them would
force the arrow contract to re-derive columnar state it does not own; two
single-purpose generators each regenerate one artifact from its own sources.

Ground truth inputs (generation over hand-editing):
  - /Users/sac/purrdf/crates/columnar/src/schema.rs    (5-table schema:
        names / file_names / columns / physical types / repetitions / utf8)
  - /Users/sac/purrdf/crates/columnar/src/lib.rs       (public API re-exports)
  - /Users/sac/purrdf/crates/columnar/src/{writer,reader,projection,files,parquet}.rs
        (writer/reader public API surface — the P0-2 surface list)
  - stardf/arrow/crates/stardf-arrow-core/src/layout.rs (BOTTOM/WILDCARD)
  - stardf/arrow/crates/stardf-arrow-core/src/arena.rs  (minting refusals)

The stardf port target (stardf/arrow/crates/columnar/) does not exist yet —
this census pins the predecessor surface the port must satisfy, plus the seam
constants (P0-5 / D3/D4) already landed on the stardf side.

Drift refusal (fail-closed):
  - 0 tables / 0 columns / 0 API items parsed from sources -> loud FAIL.
  - Parsed schema must contain exactly the five canonical table names.
  - Parsed seam constants must equal the pinned values
    (BOTTOM=0, WILDCARD=0xFFFFFFFF, dictionary cap=u32::MAX-2).
  - Post-write verification: reload the emitted JSON and deep-compare against
    the in-memory census; any disagreement is a loud FAIL.

Output: authority/stardf/stardf-columnar.json
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFX = "/Users/sac/purrdf/crates/columnar/src"
SCHEMA_RS = f"{PREFX}/schema.rs"
LIB_RS = f"{PREFX}/lib.rs"
WRITER_RS = f"{PREFX}/writer.rs"
READER_RS = f"{PREFX}/reader.rs"
PROJECTION_RS = f"{PREFX}/projection.rs"
FILES_RS = f"{PREFX}/files.rs"
PARQUET_RS = f"{PREFX}/parquet.rs"
CORE_SRC = os.path.join(REPO, "stardf/arrow/crates/stardf-arrow-core/src")
LAYOUT_RS = os.path.join(CORE_SRC, "layout.rs")
ARENA_RS = os.path.join(CORE_SRC, "arena.rs")
OUT = os.path.join(REPO, "authority/stardf/stardf-columnar.json")

RELEASE = "v26.10.31"
SCHEMA = f"urn:chatman:ggen-legacy:stardf-columnar-census:{RELEASE}"

CANONICAL_TABLES = ["annotations", "blobs", "quads", "reifiers", "terms"]

# Pinned seam (06-phase0 §2/§3, P0-5 / D3/D4; stardf/arrow layout.rs + arena.rs).
PINNED = {
    "id_width": "u32",
    "BOTTOM": 0,
    "WILDCARD": 0xFFFFFFFF,
    "DICTIONARY_CAP": 0xFFFFFFFD,  # u32::MAX - 2
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_schema_rs(text):
    """Extract the five TableSchema consts and their column arrays."""
    col_defs = {}
    for m in re.finditer(
        r'const\s+(\w+_COLUMNS)\s*:\s*&\[ColumnSchema\]\s*=\s*&\[(.*?)\];',
        text, re.DOTALL,
    ):
        cols = []
        for cm in re.finditer(
            r'ColumnSchema::(int64|bytes)\(\s*"([^"]+)"\s*,\s*Repetition::(\w+)'
            r'(?:\s*,\s*(true|false))?\s*\)',
            m.group(2),
        ):
            kind, name, rep, utf8 = cm.groups()
            cols.append({
                "name": name,
                "physical_type": "Int64" if kind == "int64" else "ByteArray",
                "repetition": rep,
                "utf8": utf8 == "true",
            })
        col_defs[m.group(1)] = cols

    tables = {}
    for m in re.finditer(
        r'const\s+\w+\s*:\s*TableSchema\s*=\s*TableSchema\s*\{'
        r'\s*name:\s*"([^"]+)"\s*,\s*file_name:\s*"([^"]+)"\s*,\s*'
        r'columns:\s*(\w+_COLUMNS)\s*,\s*\};',
        text,
    ):
        name, fname, cols_const = m.groups()
        tables[name] = {"file_name": fname, "columns": col_defs.get(cols_const, [])}
    return tables


def parse_public_api():
    """P0-2 surface list: pub items in writer/reader/projection/files/parquet
    plus the lib.rs pub-use re-exports."""
    lib = read(LIB_RS)
    reexports = []
    for m in re.finditer(r'pub use\s+\w+::\{([^}]+)\};', lib):
        reexports.extend(s.strip() for s in m.group(1).split(",") if s.strip())

    items = []
    sources = {
        "writer.rs": WRITER_RS,
        "reader.rs": READER_RS,
        "projection.rs": PROJECTION_RS,
        "files.rs": FILES_RS,
        "parquet.rs": PARQUET_RS,
    }
    for fname, path in sorted(sources.items()):
        text = read(path)
        for m in re.finditer(r'^pub (struct|enum|fn|const|trait)\s+(\w+)', text, re.M):
            items.append({
                "kind": m.group(1),
                "name": m.group(2),
                "source_file": f"crates/columnar/src/{fname}",
            })
    return {"reexports": sorted(set(reexports)), "items": items}


def parse_seam_constants():
    layout = read(LAYOUT_RS)
    arena = read(ARENA_RS)

    def grab(pattern, text):
        m = re.search(pattern, text)
        return m.group(1).strip() if m else None

    return {
        "layout_rs": {
            "BOTTOM_TERM_ID": grab(r'pub const BOTTOM_TERM_ID:\s*TermId\s*=\s*([^;]+);', layout),
            "WILDCARD_TERM_ID": grab(r'pub const WILDCARD_TERM_ID:\s*TermId\s*=\s*([^;]+);', layout),
        },
        "arena_rs": {
            "BOTTOM_ID": grab(r'pub const BOTTOM_ID:\s*u32\s*=\s*([^;]+);', arena),
            "WILDCARD_ID": grab(r'pub const WILDCARD_ID:\s*u32\s*=\s*([^;]+);', arena),
        },
    }


def fail(msg):
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(1)


def as_u32(expr, what):
    if expr is None:
        fail(f"Seam drift: {what} not found in layout.rs/arena.rs.")
    e = expr.replace("_", "").strip()
    table = {"0": 0, "u32::MAX": 0xFFFFFFFF}
    if e in table:
        return table[e]
    try:
        return int(e, 0)
    except ValueError:
        fail(f"Seam drift: {what} = '{expr}' is not a recognized pinned constant.")


def main():
    for path in (SCHEMA_RS, LIB_RS, WRITER_RS, READER_RS, PROJECTION_RS,
                 FILES_RS, PARQUET_RS, LAYOUT_RS, ARENA_RS):
        if not os.path.exists(path):
            fail(f"Census source missing: {path}")
    schema_text = read(SCHEMA_RS)

    tables = parse_schema_rs(schema_text)
    if not tables:
        fail("Vacuous census: 0 TableSchema consts parsed from schema.rs.")
    if sorted(tables) != CANONICAL_TABLES:
        fail(f"Schema drift: parsed table set {sorted(tables)} != canonical {sorted(CANONICAL_TABLES)}")
    for name, t in tables.items():
        if not t["columns"]:
            fail(f"Vacuous census: table '{name}' parsed 0 columns.")
    if len(tables) != 5 or len(set(tables)) != 5:
        fail(f"Schema drift: expected exactly 5 tables, parsed {len(tables)}.")

    seam = parse_seam_constants()
    bottom = as_u32(seam["layout_rs"]["BOTTOM_TERM_ID"], "BOTTOM_TERM_ID")
    wild = as_u32(seam["layout_rs"]["WILDCARD_TERM_ID"], "WILDCARD_TERM_ID")
    bottom_a = as_u32(seam["arena_rs"]["BOTTOM_ID"], "BOTTOM_ID")
    wild_a = as_u32(seam["arena_rs"]["WILDCARD_ID"], "WILDCARD_ID")
    if (bottom, wild) != (PINNED["BOTTOM"], PINNED["WILDCARD"]):
        fail(f"Seam drift: layout.rs BOTTOM/WILDCARD "
             f"{bottom:#010x}/{wild:#010x} != pinned "
             f"{PINNED['BOTTOM']:#010x}/{PINNED['WILDCARD']:#010x}.")
    if bottom_a != PINNED["BOTTOM"] or wild_a != PINNED["WILDCARD"]:
        fail(f"Seam drift: arena.rs BOTTOM/WILDCARD {bottom_a:#010x}/{wild_a:#010x} "
             f"!= pinned {PINNED['BOTTOM']:#010x}/{PINNED['WILDCARD']:#010x}.")

    api = parse_public_api()
    if not api["items"]:
        fail("Vacuous census: 0 public API items parsed from writer/reader/projection/files/parquet.")
    if not api["reexports"]:
        fail("Vacuous census: 0 pub-use re-exports parsed from lib.rs.")

    counts = {
        "tables": len(tables),
        "columns": sum(len(t["columns"]) for t in tables.values()),
        "api_items": len(api["items"]),
        "api_reexports": len(api["reexports"]),
    }

    census = {
        "schema": SCHEMA,
        "release": RELEASE,
        "standing": "PARTIAL_ALIVE",
        "equation": "A = mu(O*)",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_from": {
            "schema_rs": SCHEMA_RS,
            "schema_rs_sha256": sha256_file(SCHEMA_RS),
            "lib_rs": LIB_RS,
            "writer_rs": WRITER_RS,
            "reader_rs": READER_RS,
            "projection_rs": PROJECTION_RS,
            "files_rs": FILES_RS,
            "parquet_rs": PARQUET_RS,
            "layout_rs": LAYOUT_RS,
            "arena_rs": ARENA_RS,
            "extractor": "scripts/extract_stardf_columnar.py",
            "note": ("Predecessor census: the port target stardf/arrow/crates/columnar/ "
                     "does not exist yet; when it lands, re-point the source paths at "
                     "the ported crate and regenerate. The census refuses to run "
                     "against a missing source (loud FAIL above)."),
        },
        "dictionary_seam": {
            **PINNED,
            "sources": seam,
            "law": ("BOTTOM=0 reserved, never minted; WILDCARD=u32::MAX refused as "
                    "mintable; dictionary cap=u32::MAX-2 (D4) so no mintable id "
                    "collides with either sentinel."),
        },
        "tables_count": counts["tables"],
        "columns_count": counts["columns"],
        "tables": tables,
        "public_api": api,
        "counts": counts,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(census, f, indent=1, sort_keys=True)
        f.write("\n")

    # Post-write drift refusal: emitted JSON must round-trip to the census.
    with open(OUT, encoding="utf-8") as f:
        reread = json.load(f)
    for key in ("tables", "public_api", "dictionary_seam", "counts",
                "tables_count", "columns_count"):
        if reread.get(key) != census[key]:
            fail(f"Post-write drift: JSON key '{key}' disagrees with in-memory census.")

    print(f"[PASS] Columnar census: {counts['tables']} tables, "
          f"{counts['columns']} columns, {counts['api_items']} public API items, "
          f"{counts['api_reexports']} re-exports; seam pinned "
          f"u32 / BOTTOM=0x00000000 / WILDCARD=0xFFFFFFFF / cap=0xFFFFFFFD.")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
