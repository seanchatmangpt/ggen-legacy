# stardf-arrow — ArrowArrayStream Reconstitution

Ticket: [GL-STARDF-001](../../../tickets/GL-STARDF-001.md) · Plan docs:
[`../docs/jira/v26.10.31/`](../docs/jira/v26.10.31/) · Authority:
`authority/stardf/stardf_contract.ttl`

## What This Is

`stardf-arrow` is the Arrow seam of the stardf reconstitution (ticket
GL-STARDF-001): it reconstitutes the `fn_avec_export_stream` family as a real
`ArrowArrayStream` producer, targeting consumption by [avec](https://github.com/seanchatmangpt/avec)
(`avec-ffi`). `ArrowArrayStream` does not exist in avec, purrdf.h, or anywhere
upstream — this is a new contract, not reconstitution of a found symbol
(`01-master-plan.md`, W3). Genre: strangler-fig — route to purrdf by default,
shift per family as each is admitted.

Four crates (the bench crate was promoted to a workspace member by lane 7 —
`crates/stardf-arrow-bench` resolves via `cargo build -p stardf-arrow-bench`
from the root and contributes its bin target to `cargo test --workspace`):

- `crates/stardf-arrow-core` — `#![no_std]` core: Quad64 batch arena and
  C Data Interface export. Consumes the physical layer (TermId=u32,
  `Quad64` `repr(C, align(64))`, MMU-style arena) through `avec-arrow`.
- `crates/stardf-arrow-capi` — C ABI membrane (`cdylib` + `rlib`), modeled
  on avec-ffi's export style; all state crosses as opaque caller-owned
  handles. Status codes follow the purrdf convention (OK=0, NULL_POINTER=1,
  INVALID_ARGUMENT=3, ARENA_FULL=16).
- `crates/stardf-arrow-bench` — perf-fence crate (workspace member since lane
  7; emits `BENCH_BASELINE.json`-shaped min-of-5 payloads).
- `crates/stardf-columnar` — vendored five-table byte-deterministic Parquet
  codec (purrdf-columnar at rev 0da05783, u32 term-id seam;
  `#![forbid(unsafe_code)]`; golden-bytes + seam courts; see
  [`docs/COLUMNAR-ARD.md`](docs/COLUMNAR-ARD.md)).

## Standing

Updated 2026-10-31 (lane 8, truth pass #3) from gates re-run on this tree this
session; supersedes the lane-11 truth pass #2 table where a later run differs.
No status below is claimed ALIVE without a command receipt; every receipt
below cites a real command + exit run this session on the final tree.

| Component | Standing | Receipt (command → exit, 2026-10-31, lane 8) | Court that closes it |
|---|---|---|---|
| stardf-arrow-core (arena/layout/release/stream) | PARTIAL_ALIVE (lib ALIVE) | `cargo test -p stardf-arrow-core` → exit 0, 33 passed / 0 failed (re-witnessed in the workspace run) | workspace `ci-all` clean + census gate |
| stardf-arrow-capi (lib + all 5 integration targets) | PARTIAL_ALIVE | workspace run: unit 22, `alloc_identity` 2, `c_smoke` 1, `columnar_integration` 1, `cross_allocator_court` 2, `stream_courts` 6 — all passed, exit 0 | W3 one-real-avec-test gate (avec-side consumer test, outside this tree) |
| stardf-columnar (vendored five-table codec) | PARTIAL_ALIVE | `cargo test -p stardf-columnar` → exit 0: lib 3, `golden_bytes` 6 (5 + 1 ignored regen helper), `seam_courts` 4; `cargo test -p stardf-arrow-capi --test columnar_integration` → exit 0, 1 passed | W4 purrdf-vs-stardf differential digest-equality court (KD-10) + structured-error corpus port (KD-13) |
| stardf-arrow-bench | PARTIAL_ALIVE | `cargo run --release` in `crates/stardf-arrow-bench/` → exit 0 (lane-11 receipt: min-of-5 40.141 GiB/s-quad); payload self-labeled `UNVERIFIED-local-min-of-5` | CI-qualified rerun vs `docs/BENCH_BASELINE.json` |
| anti_vacuity court | PARTIAL_ALIVE (repaired) | workspace run: 3 passed / 0 failed, exit 0 — the prior `ontology_pristine.ttl` fixture drift was repaired by its owning lane; lane 8 witnesses the green run | fixture refresh landed + 3/3 pass (witnessed) |
| Workspace ladder (`cargo test --workspace --no-fail-fast`) | PARTIAL_ALIVE | exit 0 — every target green: 82 tests, 0 failed, 1 ignored across 12 targets; `cargo fmt --all -- --check` and clippy `-D warnings` were exit 0 at lane-11 receipt time (not re-run by lane 8) | `just ci-all` clean |
| Substrate verifier | ALIVE (local gate) | `python3 scripts/verify.py` ×2 → 0/0 byte-identical (lane-11 + columnar-wave receipts, sha `cb57ce4e…`); `--mutate drop-export` → exit 1 (flip witnessed) | CI-hosted rerun |
| BLAKE3 single-identity gate | PARTIAL_ALIVE | `bash scripts/verify_blake3_identity.sh` → exit 0: "exactly 1 blake3 identity: blake3 v1.8.7"; WARN version skew Cargo.toml 1.8.5 vs lock 1.8.7 | KD-12 digest-parity court + purrdf golden comparison |
| Columnar oracle (DuckDB read gate) | ALIVE (local gate) | `bash scripts/check-columnar-oracle.sh` → exit 0: DuckDB reads the fixture (counts=6,3,0,0,2) | CI-hosted rerun |
| avec integration edge | OPEN | no command run — avec-ffi consumer test is outside this tree | path-dep build + consumer court |
| Equivalence to purrdf classes | OPEN | no `abi_signatures`/`abi`/`vectors/` target exists in this tree | W4 header-freeze / golden replay |
| CI determinism + receipt | OPEN | `ci/` workflow committed; no two-run replay receipt exists | W5 SHA-pinned two-run replay |

Superseded lane-11 table kept for the register (truth pass #2, 2026-10-31;
every row below that differs from the table above is superseded by it):

| Component | Standing | Receipt (command → exit, 2026-10-31, lane 11) | Court that closes it |
|---|---|---|---|
| stardf-arrow-core (arena/layout/release/stream) | PARTIAL_ALIVE (lib ALIVE) | `cargo test -p stardf-arrow-core` → exit 0, 33 passed / 0 failed + 0 doctests. The earlier SIGTRAP is GONE — full target (lib + doctests) exits 0 | workspace `ci-all` clean + census gate |
| stardf-arrow-capi (lib + all 4 integration targets) | PARTIAL_ALIVE | `cargo test -p stardf-arrow-capi` → exit 0: unit 22 passed, `alloc_identity` 2 passed, `c_smoke` 1 passed, `cross_allocator_court` 2 passed, `stream_courts` 6 passed / 0 failed. All targets green; `court_5_use_after_release` passes via the typed dead state (`core_of` returns None on NULL private_data, `src/stream_c.rs:69-75`) | W3 one-real-avec-test gate (avec-side consumer test, outside this tree) |
| stardf-arrow-bench | PARTIAL_ALIVE | `cargo run --release` in `crates/stardf-arrow-bench/` → exit 0; min-of-5 stream drain 40.141 GiB/s-quad; payload self-labeled `UNVERIFIED-local-min-of-5` | CI-qualified rerun vs `docs/BENCH_BASELINE.json` |
| anti_vacuity court | BUILD_BROKEN | `cargo test -p stardf-arrow --test anti_vacuity` → exit 1, 1 passed / 2 failed: `ontology_pristine.ttl` drifted from `ontology.ttl` (artifact edited post-receipt without fixture refresh; failure reproduces across runs) | fixture refresh + 3/3 pass |
| Workspace ladder (`cargo test --workspace --no-fail-fast`) | PARTIAL_ALIVE | exit 1 — every target green except anti_vacuity (1/3). `cargo fmt --all -- --check` → 0; `cargo clippy --workspace --all-targets -- -D warnings` → 0 | anti_vacuity fixture refresh + `just ci-all` |
| Substrate verifier | ALIVE (local gate) | `python3 scripts/verify.py` ×2 → 0/0, outputs byte-identical (`cmp` 0): 13 header declarations == 13 `#[no_mangle]` exports, set equality; `--mutate drop-export` → exit 1 (flip witnessed). `--emit-receipt` flag now landed (`scripts/verify.py:136,287`) | CI-hosted rerun |
| avec integration edge | OPEN | no command run — avec-ffi consumer test is outside this tree | path-dep build + consumer court |
| Equivalence to purrdf classes | OPEN | no `abi_signatures`/`abi`/`vectors/` target exists in this tree | W4 header-freeze / golden replay |
| CI determinism + receipt | OPEN | `ci/` workflow committed; no two-run replay receipt exists | W5 SHA-pinned two-run replay |

Honest history (superseded rows kept for the register): the lane-13 table's
SIGTRAP, `alloc_identity` BUILD_BROKEN (10 compile errors), stream_courts 5/6
(court_5 panic at `stream_c.rs:68`), the verify.py 15-vs-13 parser artifact,
the stream_c.rs:213 fmt diff, and the alloc_identity clippy error were all
stale against the final receipts — each was repaired mid-wave by its owning
lane (see `evidence/wave-finish-lane16-2026-10-31.json` errors[] history and
the W8/F2/W10 receipts) and re-witnessed green by lane 11 above. The last red
gate, anti_vacuity fixture drift (introduced when `ontology.ttl` was
re-generated after the lane-16 receipt), was repaired by its owning lane and
is now witnessed green: `cargo test --workspace --no-fail-fast` → exit 0 with
anti_vacuity 3/3 (lane 8, 2026-10-31).

## Quickstart

```bash
just build      # debug build of all workspace members
just check      # cargo check across the workspace
just test       # test suite across the workspace
just clippy     # clippy, warnings denied
just fmt        # rustfmt across the workspace
just ci-all     # fmt + clippy + check + test (default verify ladder)
```

Toolchain: floating nightly (`rust-toolchain.toml`), same posture as purrdf.
Targets cover the cross gates: `wasm32-unknown-unknown` (footprint) and
`aarch64-unknown-linux-gnu` (simd/cross).

## Avec Integration Plan

Per `../docs/jira/v26.10.31/01-master-plan.md` (W3):

1. **Path-dep edge.** `avec-ffi` (rlib) consumes `stardf-arrow-capi` by path
   dependency — this workspace is never published; the workspace pins
   `avec-arrow` by git rev (`20248e4`, mirroring the purrdf root manifest).
2. **Consumer court.** `avec-ffi` grows a court modeled on `alloc_courts.rs`:
   `cross_allocator_court` — produce a stream on the stardf side, release it
   on the avec side, prove the free crosses the allocator boundary correctly
   (R2 falsifier).
3. **Gate.** ONE real avec integration test passing. No slice of this
   workspace is claimed integrated until that test exits 0 on the exact
   subject.

## Constraint Register

All constraints OPEN until their closing court's receipt lands.

### R1 — License Skew

purrdf is MIT/Apache-2.0/MulanPSL conjunct; avec is P28-SIL sovereign. A
compatibility receipt is required BEFORE the avec dependency edge is admitted.
Conjunct notices (Unicode-3.0 for the Unicode data, BSD-3-Clause where
present) travel with the receipt so every per-file notice is accounted for.

### R2 — Cross-Allocator Release

Memory allocated under stardf's arena and released through avec's allocator
(or the reverse) is UB. Closed only by `cross_allocator_court` plus the
`mutant-cross-alloc` positive-control — a court that cannot flip is FAIL.

### R3 — Borrowed-Pointer Lifetimes

Exported rowcursor views borrow arena memory; a view held past arena reset is
a dangling pointer. Poison/guard court required.

### R4 — Quad 64-Byte Alignment

`Quad64` is `repr(C, align(64))`; compile-time asserts exist and stay pinned.
Any new export path must re-assert, not assume.

## See Also

- [`../docs/jira/v26.10.31/01-master-plan.md`](../docs/jira/v26.10.31/01-master-plan.md)
  — waves W1-W5, risk register
- [`../docs/jira/v26.10.31/04-falsifiers.md`](../docs/jira/v26.10.31/04-falsifiers.md)
  — court falsifiers
- [`docs/PRD.md`](docs/PRD.md) / [`docs/ARD.md`](docs/ARD.md) — product/architecture refs
- [`evidence/README.md`](evidence/README.md) — receipt conventions
