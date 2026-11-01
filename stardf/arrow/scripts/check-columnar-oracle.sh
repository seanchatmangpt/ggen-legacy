#!/usr/bin/env bash
# Lane 12 (2026-10-31): external DuckDB columnar oracle for the stardf Arrow
# workspace. Ported from purrdf scripts/check-columnar-oracle.sh.
#
# Generates a fixed five-table fixture through stardf-arrow-core (the real
# present substrate; the stardf-columnar codec wave is landing separately and
# should retarget the fixture at its write() when it exposes a lib target),
# then asserts exact row counts and DuckDB-observed physical types on the five
# Parquet tables. DuckDB absent = loud [SKIP] + nonzero exit, never a silent
# pass.
#
# Compile note (disclosed): the fixture example is built by a throwaway cargo
# project under the workspace target dir — the scratch manifest is generated
# by this script so the shared workspace Cargo.toml needs no edits. Chicago:
# real terms interned through TermArena, real Quad64 records pushed through
# StardfBatch, real Parquet bytes on disk, an external duckdb process observes
# the files.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXAMPLE="${ROOT}/examples/columnar_oracle_fixture.rs"
SCRATCH="${ROOT}/target/columnar-oracle-scratch"

if ! command -v duckdb >/dev/null 2>&1; then
  echo "[SKIP: duckdb CLI not found on PATH — columnar oracle not exercised]"
  exit 3
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "[SKIP: cargo not found on PATH — cannot build the fixture generator]"
  exit 3
fi

tmp="${SCRATCH}/proj"
rm -rf "${SCRATCH}"
mkdir -p "${tmp}/src"
trap 'rm -rf "${SCRATCH}"' EXIT

# Throwaway cargo project consuming the real workspace member by path, with
# its own target dir so it stays out of the shared workspace build graph. The
# avec-arrow rev mirrors the workspace single pin (root Cargo.toml
# [workspace.dependencies]); if that pin moves, this line moves with it.
cat > "${tmp}/Cargo.toml" <<MANIFEST
[workspace]

[package]
name = "columnar_oracle_fixture"
version = "0.0.0"
edition = "2021"
publish = false

[dependencies]
stardf-arrow-core = { path = "${ROOT}/crates/stardf-arrow-core" }
avec-arrow = { git = "https://github.com/seanchatmangpt/avec", rev = "67c0ec1" }
MANIFEST

cp "${EXAMPLE}" "${tmp}/src/main.rs"

cargo build --manifest-path "${tmp}/Cargo.toml" --offline --quiet

fixture="${SCRATCH}/bin/debug/columnar_oracle_fixture"
mkdir -p "$(dirname "${fixture}")"
CARGO_TARGET_DIR="${SCRATCH}/bin" cargo build --manifest-path "${tmp}/Cargo.toml" --offline --quiet

# Generate the fixture: real intern + real Quad64 batch -> real Parquet files.
tmpf="${SCRATCH}/fixture"
"${fixture}" "${tmpf}"

# External oracle: DuckDB observes the files on disk.
counts="$(duckdb -csv -noheader -c "
SELECT
  (SELECT count(*) FROM read_parquet('${tmpf}/terms.parquet')),
  (SELECT count(*) FROM read_parquet('${tmpf}/quads.parquet')),
  (SELECT count(*) FROM read_parquet('${tmpf}/reifiers.parquet')),
  (SELECT count(*) FROM read_parquet('${tmpf}/annotations.parquet')),
  (SELECT count(*) FROM read_parquet('${tmpf}/blobs.parquet'));
")"
if [[ "${counts}" != "6,3,0,0,2" ]]; then
  echo "ERROR: DuckDB observed unexpected columnar fixture counts: ${counts}" >&2
  exit 1
fi

types="$(duckdb -csv -noheader -c "
SELECT typeof(id), typeof(lex) FROM read_parquet('${tmpf}/terms.parquet') LIMIT 1;
SELECT typeof(bytes) FROM read_parquet('${tmpf}/blobs.parquet') LIMIT 1;
")"
if [[ "${types}" != $'BIGINT,VARCHAR\nBLOB' ]]; then
  echo "ERROR: DuckDB observed unexpected Parquet physical types:" >&2
  printf '%s\n' "${types}" >&2
  exit 1
fi

# Physical-layout spot check: the quads table carries the real interned
# TermIds pushed through StardfBatch (dense from 1).
quad_terms="$(duckdb -csv -noheader -c "
SELECT DISTINCT s_id FROM read_parquet('${tmpf}/quads.parquet') ORDER BY s_id;
")"
if [[ "${quad_terms}" != "1
6" ]]; then
  echo "ERROR: DuckDB observed unexpected interned subject TermIds: ${quad_terms}" >&2
  exit 1
fi

echo "OK: DuckDB read the stardf columnar fixture (counts=6,3,0,0,2; terms=BIGINT,VARCHAR; blobs=BLOB; quads s_id in {1,6})"
