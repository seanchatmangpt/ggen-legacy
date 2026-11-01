# RECEIPTS

Manufacturing receipts for this branch. Law: no slice claimed ALIVE without the
real gate output (`stardf/arrow/evidence/README.md`); every wave ends with a
receipt carrying commands, exits, and SHA.

## Standing table

| id | subject | standing | receipt | commands / exits | SHA | replay |
|----|---------|----------|---------|------------------|-----|--------|
| LANE-9 | `stardf/arrow` verify.py substrate gate | PARTIAL_ALIVE (local gate only) | `schema: ggen.legacy.stardf.arrow.receipt.v1`, `receipt_sha256: 1b29abcdedfcb4a330a0a0c0845c48fc4dfced26fb246414c9a6365d7ad7d5f9` | `python3 scripts/verify.py` → 0; `python3 scripts/verify.py --mutate drop-export` → 1 (flip witnessed) | receipt file sha256 `b0ad32811cac3f1eb93ea496efa099838110a550fefb9efc738cab1a4800e154` (both runs) | WITNESSED: two `--emit-receipt` runs byte-identical (`cmp` exit 0) |
| LANE-16 | wave-finish full ladder, receipt-time tree | PARTIAL_ALIVE | `evidence/wave-finish-lane16-2026-10-31.json` (schema `ggen.legacy.stardf.arrow.receipt.v1`, tree_digest `332392fa…`) | `cargo test --workspace --no-fail-fast` → 101 (stream_courts court_2 5/6); clippy → 101 (alloc_identity); fmt → 1; verify.py ×2 → 0/0 byte-identical; `--mutate drop-export` → 1; c_smoke 0; cross_allocator 0; core 0 | parent HEAD `c9f8028…`, tree_digest `332392fa9da7…` | WITNESSED (manual cmp of two stdout captures; `--emit-receipt` flag had not landed at receipt time) |
| LANE-11 | completion truth pass #2 on the final tree | PARTIAL_ALIVE | this row + README standing table (2026-10-31) | `cargo test -p stardf-arrow-core` → 0 (33 passed, SIGTRAP gone); `cargo test -p stardf-arrow-capi` → 0 (22+2+1+2+6, all targets green); `cargo test --workspace --no-fail-fast` → 1 (anti_vacuity 1/3, fixture drift — only red); `cargo fmt --all -- --check` → 0; `cargo clippy --workspace --all-targets -- -D warnings` → 0 (final run; an earlier same-session run exited 101 on bench doc-comment overindent before a concurrent lane's fix landed); `python3 scripts/verify.py` ×2 → 0/0, `cmp` → 0, 13==13 parity; `--mutate drop-export` → 1 (flip witnessed); bench `cargo run --release` → 0, min-of-5 40.141 GiB/s-quad | parent HEAD `c9f8028…`; `stream_c.rs` sha256 `6a84c661…`, `ontology.ttl` sha256 `cfdd8a75…` at receipt time | WITNESSED for verify.py pair (`/tmp/l11_v1.out` vs `/tmp/l11_v2.out`, byte-identical) |
| LANE-8 | columnar truth pass #3: contract gates re-run on the landed columnar tree; docs reconciled to as-built | PARTIAL_ALIVE | this row + README standing table + `docs/DIVERGENCES.md` status table + `docs/COLUMNAR-ARD.md` header (2026-10-31) | `cargo test -p stardf-columnar --test golden_bytes` → 0 (6 passed / 0 failed); `cargo test -p stardf-arrow-capi --test columnar_integration` → 0 (1 passed); `cargo test -p stardf-columnar` → 0 (3 lib + 6 golden + 4 seam); `cargo test --workspace --no-fail-fast` → 0 (82 passed / 0 failed / 1 ignored across 12 targets — anti_vacuity 3/3 witnessed green, prior fixture drift repaired by its owning lane); `bash scripts/verify_blake3_identity.sh` → 0 (1 blake3 identity v1.8.7; WARN Cargo.toml 1.8.5 vs lock 1.8.7); `bash scripts/check-columnar-oracle.sh` → 0 (DuckDB reads fixture, counts=6,3,0,0,2) | parent HEAD `c9f8028…` (unchanged; stardf/ untracked in parent); no git operations by lane 8 | WITNESSED for all listed runs (outputs quoted in the README table and DIVERGENCES status rows this lane wrote) |

Nonclaims: no external production standing; no CI-gate standing (local runs
only); the avec integration edge, W4 equivalence ladder (`abi_signatures`/
`abi`/`vectors/` targets do not exist) and W5 two-run CI replay have no
receipt — OPEN; the anti_vacuity fixture repair is its owning lane's
landing (lane 8 only witnesses the green run); the W4 purrdf-vs-stardf
differential digest-equality court has NOT run — KD-10's differential half and
KD-12's digest-parity court remain OPEN; no git operations performed by
lanes 11 or 8.
