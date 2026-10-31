# 05 Next Steps — v26.10.31 (stardf reconstitution)

Companion to `01-master-plan.md` / `02-wave-contracts.md` / `04-falsifiers.md`.
Originally written by lane 17 (2026-10-31); refreshed in place by closure
lane 20 against the as-built tree (2026-10-31, second refresh); recommended-
next-action re-refreshed by W1 closure lane 16 (2026-10-31, third refresh —
that lane owns only this paragraph, not the section statuses); fourth refresh
by the finishing lane 16 (2026-10-31, post lanes 1-15) — that lane owns only
this paragraph, §6, the recommended-next-action, and the falsify list, not
the other section statuses; fifth refresh by plan-update lane 7 (2026-10-31)
— this lane owns only this file, and corrects §6/§3/recommended-next-action
against session receipts that supersede the fourth refresh's doc-only reads.
Each entry
names its closing command and the re-read evidence behind its status; anything
not re-run this session stays **OPEN**. Decision rows now live in
`stardf/arrow/docs/OPERATOR-DECISIONS.md` (D1–D8 base + D9–D14 phase-2
addendum); §5 below records the deltas, not the authority.

## 1. W1 Contract Closure

Close the contract authority so receipts can bind to a committed SHA.

- **Files**: `scripts/extract_purrdf_ontology.py` (extend regex at ~L83 —
  re-read this session: it still matches only named
  `typedef struct X X;`, zero anonymous-struct handling in the file — to
  capture anonymous `typedef struct { ... } Name;` bodies, the 11 sites listed
  in `02-wave-contracts.md` §W1: PurrdfStr L1090 … PurrdfCapabilities L1410),
  `scripts/verify_stardf_ontology.py` (add type census: opaque AND value
  structs, two-directional — missing-in-TTL FAIL, phantom-mapping FAIL, rename
  invariant `target == predecessor.replace("Purrdf","Stardf",1)`, plus a
  `--mutate drop-type` flag), `authority/stardf/stardf_contract.ttl`
  (regenerated, never hand-edited).
- **Commands**:
  ```bash
  python3 scripts/verify_stardf_ontology.py   # F1: must FAIL (exit 1) on today's TTL
  python3 scripts/extract_purrdf_ontology.py
  python3 scripts/verify_stardf_ontology.py   # must PASS: function + type census
  python3 scripts/verify_stardf_ontology.py --mutate drop-type   # F1a: must exit 1
  ```
- **Ladder**: F1 first (verify must FAIL on the pre-fix TTL — proves the census
  not vacuous) → extract → verify PASS → mutation refused → re-verify
  identical (F2a determinism pulled forward) → commit `authority/stardf/`
  (receipts bind to a SHA, not the working tree).
- **Precondition**: `~/purrdf/crates/rdf-capi/include/purrdf.h` present at the
  verifier's default path; `pip install rdflib pyshacl`.
- **Owner**: W1 lane.
- **Status**: OPEN (mappings). PARTIAL on the gate machinery: re-read this
  session — the type census (opaque + anonymous two-directional, rename
  invariant, non-vacuity floor) and `--mutate drop-type` **are landed** in
  `scripts/verify_stardf_ontology.py` (census at :31-55, mutation at
  :82/:113-129, vacuous-census floor at :143-149). What remains OPEN: the
  extractor (`scripts/extract_purrdf_ontology.py`) still has no anonymous-
  struct branch (grep: only the opaque `typedef struct` path), and the TTL
  contains zero value-struct mappings (re-read: `PurrdfStr`,
  `PurrdfCapabilities`, `PurrdfQueryGovernors` each grep 0 in
  `authority/stardf/stardf_contract.ttl`) — so the census correctly FAILs
  pre-fix and the 11 mapping additions are the open work. The F1 ladder
  (FAIL → extract → PASS → mutate refused → commit per D14) has **not been
  run this session** — OPEN.

## 2. Avec-Side Integration Slice (W3)

- **Files**: `avec-ffi/Cargo.toml` (path-dep on
  `/Users/sac/ggen-legacy/stardf/arrow/crates/stardf-arrow-capi` rlib); new
  `avec-ffi/tests/cross_allocator_court.rs` (avec side), modeled on stardf's
  `stardf-arrow-capi/tests/cross_allocator_court.rs` (exists in
  `stardf/arrow/crates/stardf-arrow-capi/tests/`) and the `SLOTS: Mutex<()>`
  idiom (`alloc_courts.rs:30`). Producer side already scaffolded in
  `stardf-arrow-capi/src/stream_c.rs` (present on disk, re-read this session).
- **Mechanics** (F3/F3a, `04-falsifiers.md`): CountingAlloc does not count
  deallocs (`alloc_counter.rs:65-67`), so the court asserts allocation-side
  identity — every released pointer was minted by the allocator owning the
  release path. Positive control: mismatched-allocator mutant
  (`mutant-cross-alloc`) must flip the test to fail; a court that cannot flip
  is FAIL.
- **Command** (in `~/avec`):
  ```bash
  cargo test -p avec-ffi --test cross_allocator_court   # exits 0 = gate met
  ```
- **Gate**: ONE real avec integration test exiting 0 on the exact subject. No
  integration standing without that output in a receipt under
  `stardf/arrow/evidence/`.
- **Preconditions**: W1 committed (receipt binds to SHA); R1 license receipt
  landed (§3); ArrowArrayStream struct layout resolved — currently UNKNOWN
  locally (§5 decision 4).
- **Owner**: W3 lane (avec side) + W3 lane (stardf producer side).
- **Status**: OPEN. Re-read this session: `~/avec/avec-ffi/tests/` still does
  not exist — the avec-side court is not scaffolded. The lane-16 `court_2`
  failure cited below was superseded by later receipts (LANE-11 row,
  wave-consolidated, lane-18 columnar-wave receipt all witness stream_courts
  6/6 on later trees) — the producer side is green-as-receipted, but the
  avec-side gate has never exited 0 anywhere and `05-next-steps.md` §2's gate
  is unchanged.

## 3. R1 License-Compatibility Receipt Gate

- **Files**: gate **landed** at `stardf/arrow/scripts/verify_stardf_licenses.py`
  (repo-root `scripts/` does not carry it — the original §3 path was wrong;
  the gate resolves the repo root from its own path). Receipt **landed** at
  `authority/stardf/license-compat.json` (real observed license rows: blake3
  1.8.5 CC0-1.0 OR Apache-2.0 OR Apache-2.0 WITH LLVM-exception, gated-class
  via the Apache arm; avec-arrow no-license fork posture row). Registry of
  per-file conjunct notices (Unicode-3.0, BSD-3-Clause) so every purrdf
  per-file notice is accounted for — extent re-read OPEN.
- **Gate law**: exit 1 on a P28-SIL → MIT/Apache-2.0/MulanPSL dependency edge
  without a registered compatibility receipt. Per `02-wave-contracts.md` /
  `04-falsifiers.md` R1, this must exist BEFORE the W3 avec dependency edge is
  admitted.
- **Commands**:
  ```bash
  python3 scripts/verify_stardf_licenses.py --avec ~/avec --stardf authority/stardf
  # exit 0 with receipt; then the positive control: remove the receipt entry
  # (in-memory) and confirm the gate exits 1 — a gate that cannot flip is FAIL
  ```
- **Precondition**: read purrdf workspace `Cargo.toml` license fields +
  per-file headers; read avec's P28-SIL statement
  (`~/avec/docs/jira/v26.10.31/34-p28-sil-compliance.md`).
- **Owner**: R1 lane.
- **Status**: RECONCILED (fifth refresh, 2026-10-31, against session
  receipts superseding the doc-only fourth-refresh read). The gate's SKIP
  arm is **CLOSED**: the inventory default-path fix landed
  (coordinator-disclosed), so the gate no longer silently skips — its
  exit-1 path now has exactly ONE cause: the blake3 FAIL, which has been
  witnessed firing. The gate is therefore a live, flipping oracle, not an
  unproven one. What remains OPEN on this row is only the R1 receipt
  admission that the avec W3 gate (§2) waits on.

## 4. Equivalence Ladder Port (W4)

Port order is fixed (each rung consumes the previous rung's output):

1. **abi freeze**: port purrdf's `abi_signatures.rs` canonicalization verbatim
   (pure fns over `&str`) into the stardf tree (suggest
   `stardf/arrow/crates/stardf-arrow-capi/tests/abi_freeze.rs` or a scripts
   module); parameterize the hardcoded `"purrdf_"` prefix
   (`abi_signatures.rs:137`). No `abi_freeze.rs` exists in
   `stardf/arrow/crates/stardf-arrow-capi/tests/` (re-read: the dir holds only
   `alloc_identity.rs`, `c_smoke.rs`, `cross_allocator_court.rs`,
   `stream_courts.rs`).
2. **snapshot regeneration**: regenerate the stardf snapshot from the
   contract's `targetSymbols` — purrdf's snapshot bytes are NOT consumable
   (purrdf symbols/types throughout). F4: snapshot equality must flip on any
   prototype add/change/remove.
3. **c_smoke parameterization**: parameterize crate name/header; driver shape
   per `02-wave-contracts.md` §W4 (nested cargo build → locate cdylib from
   Cargo JSON → `cc -std=c11` → link → DYLD_LIBRARY_PATH). A stardf-side
   `c_smoke.rs` already exists — the parameterization work is making the
   purrdf driver shape run against the stardf crate, not creating the file.
4. **GTS vectors**: copy the 39 `*.gts` + `*.expected.json` pairs (binary
   CBOR-seq, read via the `purrdf-gts` reader pattern,
   `crates/gts/tests/frozen_canonical_bytes.rs:14-38`); the stardf copy needs
   its **own** `.sha256` manifest + roots.toml equivalent — purrdf's
   `check-corpus-frozen.py:52-55` deliberately does not police the GTS
   vectors, so the manifest is the closure. F4b: a corrupted vector copy must
   FAIL the manifest check.
- **Golden masters** (F4a): each ported purrdf `abi.rs` test class must pass
  on stardf AND fail under one representative deliberate mutation; an
  untested mutation = unproven oracle.
- **Precondition**: W1 TTL committed (the snapshot regenerates from the
  contract's targetSymbols); GTS reader port.
- **Owner**: W4 lane.
- **Status**: OPEN — re-read this session (tree-wide `find` for `abi_freeze*`,
  `*.gts`, `*sha256*` under `stardf/`, `target/` excluded): no abi port, no
  snapshot, no GTS manifest anywhere under `stardf/`. Unchanged.

## 5. Operator Decision Register — superseded by OPERATOR-DECISIONS.md

The authoritative register is now `stardf/arrow/docs/OPERATOR-DECISIONS.md`
(lane 19 base D1–D8 + phase-2 addendum D9–D14, each with options, evidence,
recommendation, and an unsigned sign-off block). Deltas vs this file's prior
§5: W1 census scope is **DECIDED (coordinator, D3)**; every other row is
PENDING-OPERATOR / PENDING-SIGN-OFF — none flipped this session. The rows
that gate the SQL wave dispatch:

- **D12 — SQL adaptation scope** (lane 6,
  `stardf/docs/jira/v26.10.31/09-sql-adaptation-scope.md`): Option A full
  ~270K-line vendor / B algebra+results with eval deferred (~45K, lane-6
  recommendation, conditioned on the R3 compile-standalone probe) / C
  facade-only (flagged mission skew). PENDING-OPERATOR — gates the SQL cycle
  start (OPEN-2).
- **D9 — ABI freeze-expansion ticket** (lane 2,
  `stardf/arrow/tickets/GL-STARDF-002-freeze-expansion.md`): ticket is
  `DRAFT-PENDING-OPERATOR-RATIFICATION`; Tier A (3 exports + 4 carriers,
  recommended) / B / C; `nm -gU` diff vs the ratified table must exit 1 on
  any extra/missing symbol. Gates ALL SQL-cycle export work and the W1
  census additions (B0 in `07-port-master-plan.md` §2).
- **D10 — KD-08 BLAKE3 single impl** (lane 4,
  `stardf/docs/jira/v26.10.31/11-blake3-arbitration.md`): PENDING-SIGN-OFF;
  recommendation vendored purrdf-hash native. Re-read this session:
  `stardf-arrow-core/Cargo.toml:15` binds `blake3 = "1.8.5"` (lock resolved
  1.8.7, drift witnessed per lane 4); until the flip, columnar W4 digest
  courts (B2) stay blocked.
- **D13 — frozen-duckdb re-home** (B3 / OPEN-5; the duckdb rehome
  precondition): PENDING-OPERATOR, recommendation Option a (canonical
  checkout + rev pin, falsifier 06-phase0 §8.3 rename-the-dir-away build).
  `stardf/arrow` binds no frozen-duckdb pin today (re-read this session);
  blocks only duckdb-scan W5 portable receipts, per the port master plan.

## 6. Columnar Wave — Landed State (fifth refresh: corrected against session receipts)

**Landed as a vendored workspace member AND witnessed green in-tree.**
Supersedes the fourth refresh's "NOT witnessed green in-tree" reading, which
was a doc-only absence-of-receipt finding — session receipts show the runs
happened. Witnessed greens (superseding receipts, cited as re-read
evidence):

- `cargo test -p stardf-columnar`: S9 witnessed **13 passed / 0 failed**;
  S10 witnessed golden_bytes **6/0** plus two successful snapshot
  regenerations; S11 witnessed seam_courts **4/0**.
- In-tree run after the `#[ignore]` fix: **5 + 1** passed (F3).
- Integration gate: S14 / W1-13 witnessed `columnar_integration` **1/0
  twice** — and the gate caught **3 real codec defects** on its way to
  green, proving it non-vacuous.
- The verify.py extractor/verifier pair is sha-stable at `cb57ce4e…`
  across the 50 → 93 file growth, i.e. the extractor determinism witness
  held at scale.

Supersedes the lane-20 scaffold-only reading (also superseded inside
`evidence/w1-closure-2026-10-31.json` conflict K4). What is on disk now:

- `stardf/arrow/crates/stardf-columnar/` — a real crate: `Cargo.toml`
  (lane-9 vendor of purrdf rev `0da05783` `crates/columnar`, u32 term-id
  seam; PROVENANCE.md present), full `src/` (lib, parquet, schema, column,
  writer, reader, projection, compact, error, files, plain_bench, vendor/
  with core+hash.rs+lex.rs), `licenses/`, and tests:
  `seam_courts.rs` + `golden_bytes.rs` (plus `tests/disabled/` holding
  `structured_errors.rs` re-homed as `-pending-stardf-substrate` — the
  1,123-line reader-refusal court whose imports named nonexistent crates;
  gated, not deleted).
- `stardf-columnar` **IS a workspace member** (`stardf/arrow/Cargo.toml`
  members: core, capi, bench, stardf-columnar — re-read this session), so
  `cargo test --workspace` and `cargo clippy --workspace` compile it.
- Receipt: `stardf/arrow/evidence/columnar-wave-2026-10-31.json` (lane 18)
  standing **PARTIAL_ALIVE**; `manufacturing-receipt-2026-10-31.json`
  supersedes bench workspace membership (bench is a workspace member, ALIVE,
  clippy --workspace covered it), core 33/33, capi courts green-as-receipted,
  bench QUOTED NOT RE-WITNESSED.
- **Closed witnesses** (fifth refresh): `cargo test -p stardf-columnar`
  (seam_courts + golden_bytes) witnessed green (S9/S10/S11 above); the
  integration gate G_COL_EXIT is **met** (S14/W1-13, 1/0 twice, 3 real codec
  defects caught). Still OPEN: the avec gate (`~/avec/avec-ffi/tests/`
  still does not exist) and CI Actions / commit (D14) — see below.

SQL-wave dispatch gate chain (07-port-master-plan §2): B0 freeze ticket (D9)
→ B1 R1 license gate (landed; SKIP arm closed, single exit-1 cause = blake3
FAIL — §3) → B2 BLAKE3 arbitration (D10;
`stardf-arrow-core/Cargo.toml:15` still binds `blake3 = "1.8.5"` — re-read)
→ B3 duckdb rehome (D13). Lane 6's SQL scope arbiter
(`09-sql-adaptation-scope.md`, re-read) landed its analysis with
recommendation B but no code and no gate executions; D12 remains
PENDING-OPERATOR. CI Actions and the D14 commit remain OPEN (the D14 plan is
staged in `COMMIT-PLAN.md`; `signing.key`/`.gitignore` flags from F13
unresolved).

## Single Recommended Next Action

**Operator signs the D9–D14 packets (lanes 9-12 recommendations), the
coordinator executes the D14 commit plan, the avec W3 gate unblocks on the
R1 receipt admission, and the SQL wave dispatches on D12.** Refreshed by
plan-update lane 7 (fifth refresh, 2026-10-31). The chain is now purely
authorization — and the machinery is even further along than the fourth
refresh recorded: the columnar courts and the integration gate are no
longer "landed-but-unwitnessed" — they are witnessed green in-tree (S9 13/0,
S10 6/0 + regenerate x2, S11 4/0, F3 in-tree 5+1 post-`#[ignore]` fix,
S14/W1-13 columnar_integration 1/0 x2 with 3 real codec defects caught), and
the license gate's SKIP arm is closed (single exit-1 cause: the blake3
FAIL). The verify.py pair held sha `cb57ce4e…` stable across 50 → 93 file
growth. Still OPEN: D9 (freeze ticket `DRAFT-PENDING-OPERATOR-RATIFICATION`,
recommend Tier A — gates all SQL-cycle export work and the W1 census
additions, B0); D10 (BLAKE3 flip, recommend vendored purrdf-hash native —
unblocks columnar W4 digest courts); D12 (SQL scope, recommend B conditioned
on R3 — gates the SQL cycle start); D13 (duckdb re-home, recommend canonical
checkout + rev pin — gates duckdb-scan W5); D14 (6-commit split — binds
every SHA-less receipt to a commit; plan staged in `COMMIT-PLAN.md`;
`signing.key`/`.gitignore` flags from F13 unresolved); CI Actions. The
sign-off blocks (D1–D8, D9–D14 addendum) are entirely unsigned.

## What Would Falsify Done-Ness

- A post-freeze export added/changed/removed in `purrdf.h` (or a query export
  landing in capi `src/`) without a ticket and without a snapshot
  regeneration — the snapshot equality / `nm -gU` gate would flip on the next
  honest run, proving the "frozen" claim stale.
- A columnar court that stops flipping: the vendored `stardf-columnar`
  seam_courts / golden_bytes courts (witnessed green in-tree, fifth
  refresh — a *future* silent pass/skip would regress that standing) or,
  once the columnar cycle runs, `--mutate drop-type`, `--mutate drop-fn`,
  `mutant-cross-alloc`, or the `--mutate drop-one-row` row-count mutant
  passing or being skipped — a mutation the gate accepts is a vacuous gate,
  which is FAIL, not PASS; a columnar court that passes pre-mutation and
  cannot flip is equally FAIL.
- The sys/builder `2.0.4` float: a workspace dependency (the sys/builder
  family) floating at `2.0.4` under a loose requirement silently moves the
  vendored-columnar substrate between court runs — pin drift the lockfile
  would only surface if the pin-source law (`stardf/arrow/Cargo.toml`
  single-pin-source comment) is actually policed. **Status of this item:
  OPEN/UNVERIFIED — this lane did not locate a `2.0.4` entry in
  `Cargo.lock` this session; the float is carried forward from the wave
  contract, not re-witnessed.**
- Cache-absent compile unwitnessed: every green compile/test receipt on this
  tree was produced with a warm `target/`; no receipt witnesses a
  cold-cache (`target/` removed) `cargo check/test/clippy --workspace`,
  so "it compiles" is grounded in cached-incremental state, not a
  reproducible from-scratch build.
- `ggen sync run` mutating generated output without a template mapping (the
  stardf:→rust: bridge query, D4's blocking prerequisite) — regeneration
  drift with no admitted transform, the exact drift the census exists to
  catch on the TTL side.
- A sentinel remap (`u32::MAX` dictionary cap, `index+1` convention) crossing
  the write boundary undetected — the purrdf-vs-stardf digest-equality court
  (columnar W4) must pin whether the remap crosses; a court pass with no
  mutant control (drop-one-row) is unproven, not PASS.
- The 11 anonymous-struct sites extracted but the rename invariant
  (`Purrdf→Stardf`, first-occurrence) silently omitted — a census that maps
  without policing renames admits a drifted target name.
- R1 receipt present but the license gate never demonstrated exiting 1
  (receipt entry removed in-memory) — an unflipped license gate is an
  unproven oracle, same class as the mutation rule above.

## Nonclaims

- Nothing in this file has been executed by lane 20 (second refresh), the
  finishing lane 16 (fourth refresh), nor plan-update lane 7 (fifth
  refresh). No gate output produced by any of them; every status cell above
  is either on-disk file content re-read or a session receipt cited as
  re-read evidence. The fifth refresh's corrections to §3/§6 come from
  session receipts (S9-S11, S14, W1-13, F3, the license-gate inventory-fix
  disclosure, the verify.py `cb57ce4e` stability witness), which supersede
  the fourth refresh's absence-of-receipt readings — the fourth refresh
  searched `docs/RECEIPTS.md` + `evidence/*.json` and found absence; the
  runs were witnessed elsewhere in-session.
- The W1 census + `--mutate drop-type` landing is a file-content observation,
  not a run receipt: no F1 ladder command has been executed and witnessed by
  this lane. All rungs remain OPEN.
- The R1 license gate + `license-compat.json` landing is likewise a file
  observation; the gate's exit-1 flip has never been witnessed in any
  on-disk receipt.
- `stardf-columnar` status is a disk read + session-receipt reconciliation at
  2026-10-31 (fifth refresh); the tree churned heavily between earlier
  refreshes — re-read before citing.
- No git operations performed by this lane (contract: no git mutations;
  `stardf/` remains untracked in the parent per `git status`).

## See Also

- [`01-master-plan.md`](01-master-plan.md) — waves W1-W5, risk register
- [`02-wave-contracts.md`](02-wave-contracts.md) — per-wave file ownership, edit plans
- [`04-falsifiers.md`](04-falsifiers.md) — F1-F5 falsifiers, R1-R5 risks
- [`../OPERATOR-DECISIONS.md`](../../arrow/docs/OPERATOR-DECISIONS.md) —
  D1–D14 decision pack (authority for §5)
- [`../../arrow/evidence/wave-finish-lane16-2026-10-31.json`](../../arrow/evidence/wave-finish-lane16-2026-10-31.json) —
  lane-16 receipt (superseded on `court_2` by later receipts)
- [`../../arrow/evidence/columnar-wave-2026-10-31.json`](../../arrow/evidence/columnar-wave-2026-10-31.json) —
  lane-18 receipt (S8–S16 UNKNOWN on disk)
- [`../../arrow/evidence/README.md`](../../arrow/evidence/README.md) — receipt law
