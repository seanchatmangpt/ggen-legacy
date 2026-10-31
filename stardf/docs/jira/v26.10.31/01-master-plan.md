# stardf Reconstitution Plan — v26.10.31

Ticket: GL-STARDF-001 (PARTIAL_ALIVE) · Authority: authority/stardf/stardf_contract.ttl
Predecessor: ~/purrdf (126 C ABI exports, ABI 0.16.0, cbindgen) · Substrate: ~/avec (ALIVE, ~310 tests pass)
bcinr: registered-non-consumer (AGENTS.md:351 declares RDF out of scope) — no work order.

## Standing summary (as-built truth pass, 2026-10-31; plan-update lane 1)
Grounded in on-disk receipts only — `stardf/arrow/evidence/*.json`
(wave-consolidated / columnar-wave / manufacturing / w1-closure, 2026-10-31),
`stardf/arrow/docs/RECEIPTS.md` (LANE-9/11/16 rows),
`stardf/arrow/docs/ABI-FREEZE.md`.
No gate re-run by this lane; citations, not re-derivations.
- Frozen ABI: 13 `stardf_*` exports, ALIVE per `stardf/arrow/docs/ABI-FREEZE.md`
  (nm + header syntax + c_smoke receipts in-file). verify.py three-way parity
  13==13==13 witnessed exit 0 with byte-identical `--emit-receipt` replay pair
  (sha `cb57ce4e…`) across trees 50→58→93 files
  (`evidence/wave-consolidated-2026-10-31.json`, `columnar-wave-…json`,
  `w1-closure-…json`).
- Workspace ladder: NOT green on the latest receipts. capi courts green
  (stream 6/6, cross-alloc 2/2, c_smoke 1, alloc_identity 2; core 33 pass;
  clippy/fmt exit 0 — `docs/RECEIPTS.md` LANE-11 row), but `cargo test
  --workspace` witnessed exit 101: capi lib cfg(test) E0308 x2 compile-abort
  under nightly 1.101 (manufacturing receipt, `commands` block), and
  anti_vacuity 1/3 (fixture-drift class) is the latest consistent witness.
- Columnar: LANDED as a vendored workspace member — `crates/stardf-columnar`
  with own `Cargo.toml`, vendored from purrdf `0da05783` with the u32 term-id
  seam, licenses preserved (`crates/stardf-columnar/PROVENANCE.md`; member
  list in `stardf/arrow/Cargo.toml`, lane-9 comment). No gate receipt for the
  vendored crate yet — standing PARTIAL_ALIVE (code), gate UNVERIFIED.
- W1 contract closure: gate machinery LANDED (type census + `--mutate
  drop-type` in `scripts/verify_stardf_ontology.py`; the 5 struct mappings
  present in `authority/stardf/stardf_contract.ttl`). The F1 ladder (FAIL →
  extract → PASS → mutate-refused) is recorded RUN-UNWITNESSED — no on-disk
  receipt of the full ladder (`evidence/w1-closure-2026-10-31.json` nonclaims
  + K3). `authority/stardf/` remains untracked; receipts bind to tree digests,
  not SHAs.
- Integration edge: avec gate NOT RUN — avec-arrow now consumed as a git-rev
  dep (`rev 67c0ec1`, `stardf/arrow/Cargo.toml` [workspace.dependencies]) but
  no avec integration test witnessed; R1 license gate witnessed exit 1,
  PENDING-OPERATOR (`docs/DECISION-BRIEFS/R1-blake3-receipt-admission.md`).
  W3 stays BLOCKED-on-R1. BLAKE3 KD-08 PENDING-SIGN-OFF
  (`docs/DECISION-BRIEFS/D10-blake3-flip.md`). No commit landed; parent HEAD
  still `c9f8028`, stardf/ untracked.
- SQL/duckdb: PLANNED-NOT-BUILT per
  `stardf/docs/jira/v26.10.31/07-port-master-plan.md` (B0–B3 blocker chain;
  no SQL or duckdb artifact or gate witnessed).
- Standing vocabulary preserved: every ALIVE above is a LOCAL gate witness,
  never external production standing; no CI Actions run witnessed.

## Waves (as-built statuses, 2026-10-31 truth pass)
W1 (contract closure): PARTIAL. Gate machinery landed — type census (opaque +
  anonymous, two-directional, rename invariant) and `--mutate drop-type` in
  `scripts/verify_stardf_ontology.py`; the 5 struct mappings
  (StardfTermView, StardfGraphMatch, StardfQueryGovernors,
  StardfGovernorEvidence, StardfPartialCertificate) present in
  `authority/stardf/stardf_contract.ttl`. NOT witnessed: the full F1 ladder
  (FAIL → extract → PASS → drop-type refused) has no on-disk receipt
  (`evidence/w1-closure-2026-10-31.json`, nonclaims + K3); the closing git
  commit of `authority/stardf/` is not executed — receipts still bind to tree
  digests, not SHAs.

W2 (scaffold): LANDED as PARTIAL_ALIVE (local). 13-export frozen ABI per
  `stardf/arrow/docs/ABI-FREEZE.md` (ALIVE; nm/header/c_smoke receipts
  in-file). Gate receipts: verify.py exit 0 with 13==13==13 three-way parity
  + byte-identical `--emit-receipt` pair sha `cb57ce4e…` (wave-consolidated /
  columnar-wave / w1-closure receipts); core 33 pass, stream 6/6, cross-alloc
  2/2, c_smoke 1, alloc_identity 2 (docs/RECEIPTS.md LANE-11 + manufacturing
  receipt). Residual reds on the same receipts: capi lib cfg(test) E0308 x2
  compile-abort (nightly 1.98→1.101 drift), anti_vacuity 1/3 fixture drift.

W3 (first integration slice): BLOCKED-on-R1. avec-arrow pinned as git-rev dep
  (rev 67c0ec1) but no avec integration test witnessed anywhere in the
  receipts; R1 license gate witnessed exit 1, PENDING-OPERATOR
  (`docs/DECISION-BRIEFS/R1-blake3-receipt-admission.md`). Gate remains: ONE
  real avec integration test passing.

W4 (equivalence ladder): OPEN. `abi_signatures`/`abi`/`vectors/` targets do
  not exist (`docs/RECEIPTS.md` nonclaims) — no header-freeze court, no
  golden-master replay, no GTS vector run witnessed.

W5 (CI + receipt): OPEN. `ci/stardf-arrow-reconstitution.yml` never witnessed
  executing in Actions; all gate standing is local runs only (all four
  evidence receipts' nonclaims). Two-run replay IS witnessed locally
  (`--emit-receipt` pairs, sha `cb57ce4e…`); SHA-pinned CI determinism court
  and the `authority/stardf/` commit remain unlanded.

Columnar wave (added per 07-port-master-plan): LANDED — vendored workspace
  member (`crates/stardf-columnar/`, purrdf `0da05783`, u32 term-id seam,
  licenses preserved per `PROVENANCE.md`). Gate receipt for the vendored
  crate: NONE on disk — G_COL_EXIT evidence not yet witnessed.

SQL wave / duckdb-scan wave: PLANNED-NOT-BUILT (07-port-master-plan §2–3;
  gated behind G_COL_EXIT / G_SQL_EXIT; B3 PENDING-OPERATOR).

W2 (scaffold): ggen-project stardf-core + stardf-capi from the TTL via clap-noun-verb-crate-pack
  /wasi-json-abi-pack; handle-first families: buffer, dataset, cursor, error (what avec needs:
  interning, pattern match, term view). Hand-written residue in custom_handlers.rs only.

W3 (first integration slice): fn_avec_export_stream → ArrowArrayStream producer in stardf-capi;
  consumer court in avec-ffi modeled on alloc_courts.rs with a cross-allocator release test
  (R2 falsifier). Gate: ONE real avec integration test passing.

W4 (equivalence ladder): port abi_signatures.snapshot as header-freeze court; replay purrdf
  golden-master classes; c_smoke-style real-C-host test; GTS vectors as byte-frozen oracles.

W5 (CI + receipt): SHA-pinned determinism court modeled on dsrust-reconstitution job; fix
  hardcoded /Users/sac/purrdf path in verifier; update .github/expected-workflows.txt if a
  workflow file is added; evidence/stardf/ receipts + two-run byte-identical replay.

## Risks (lane 19)
R1 license skew: purrdf MIT/Apache/MulanPSL vs avec P28-SIL sovereign — needs compatibility
   receipt gate. R2 cross-allocator release mismatch at Arrow boundary (W3 court). R3
   rowcursor borrowed-pointer lifetime (poison/guard court). R4 quad 64-byte alignment
   assumptions (compile-time asserts exist; keep pinned).

## Law
Every wave ends with a manufacturing receipt (commands, exits, SHA). No slice claimed ALIVE
without the real gate output. Genre: strangler-fig — route to purrdf by default, shift per
family as each is admitted.
