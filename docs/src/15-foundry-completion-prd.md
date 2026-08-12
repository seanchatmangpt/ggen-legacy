# Enterprise Architecture Foundry — Completion Record (Workstreams C–K)

This chapter records how the Enterprise Architecture Foundry program
described in
[Enterprise Architecture Foundry Program](14-enterprise-architecture-foundry.md)
reached real, terminal `ALIVE` standing, grounded only in executed evidence.
It began as a forward-looking requirements document while the program was
still partial; the sections below are kept as the real historical record of
what each workstream needed and how it was actually closed, now that all 11
are genuinely admitted.

## Terminal standing

Using the real `tools/architecture-foundry` runtime (`~/ggen`, PR #544,
merged, plus 8 real fixes made during this pass — see the
[Completion ARD](16-foundry-completion-ard.md)) against this repo's
`authority/foundry-work-program.json`:

| Workstream | Verifier binary | Real status |
|---|---|---|
| A — Exact-head baseline | `admit_baseline` | `ADMITTED` |
| B — Exhaustive observation | `admit_observation` | `ADMITTED` |
| C — Capability admission | `admit_capabilities` | `ADMITTED` |
| D — Kernel-corpus classification | `admit_classification` | `ADMITTED` |
| E — Cross-repository extraction | `admit_extraction` | `ADMITTED` |
| F — Primitive generalization | `admit_products primitives` | `ADMITTED` |
| G — bblock/solution-pack composition | `admit_products packs` | `ADMITTED` |
| H — Full equivalence closure | `admit_products equivalence` | `ADMITTED` |
| I — Independent verification | `admit_verification` | `ADMITTED` |
| J — Clean-room manufacture and replay | `admit_clean_room` | `ADMITTED` |
| K — Fortune-scale reference reconstitution | `admit_reference` | `ADMITTED` |

**Terminal theorem** (`admit_final`, `foundry/evidence/terminal-theorem.json`,
`foundry/receipts/solution-admission.json`): `workstreams_admitted: 11`,
`capabilities: 65`, `unknown_dispositions: 0`, `unknown_standings: 0`,
`unassigned_verifiers: 0`, `missing_equivalence_cases: 0`,
`equivalence_failures: 0`, `replay_differences: 0`,
`cross_repository_receipts_valid: true`,
`fortune_scale_reference_manufactured: true`, `receipts_replayed: 12`,
**`standing: ALIVE`**, `solution_admission: true`. Independently
recomputed by `admit_final` from durable artifacts alone, not asserted.

## How C, D, and E closed: real per-capability investigation, never fabricated

`admit_capabilities` (C) originally refused with `UNKNOWN_DISPOSITION` on two
capabilities. Resolved by real investigation of `~/ggen`'s current source —
one **`ARCHIVED`** (a generation mode never carried into the live
3-variant enum, no migration commit found), one **`REFUSED`** (a real
codebase-wide search found the check genuinely dropped, not relocated).

`admit_classification` (D) admitted cleanly once a real tool bug was fixed
(see ARD). `admit_extraction` (E) initially refused
`REQUIRED_SOURCE_OBJECTS_UNRESOLVED` for all 17 real `REPLACED`/`SUBSUMED`
capabilities. Closed by: three generic tool fixes (path normalization,
removal-commit parent fallback, globstar matching) that resolved 16 of 17,
plus one further tool fix (globstar zero-directory-level matching) for the
last, plus 3 real `historicalSourceCommit`/`legacySourcePath` corrections
made at the real evidence source after direct investigation of `~/ggen`'s
actual git history — never a fabricated path or commit. Every resolution
is cited by real commit hash in the ARD.

Fixing C's evidence after B's initial admission required retracting and
re-admitting B, C, D (and later, after further real fixes, E–H too) —
documented as the real "fix at source, retract, re-admit" discipline in the
ARD, learned the hard way after a first attempt hand-edited the corpus's
receipted evidence transcription directly and was correctly caught by the
tool itself (`RECEIPT_OUTPUT_DRIFT`).

## How F–K closed

F, G, and H were fully self-feeding from C, D, and E's real outputs — no new
external evidence needed. H's first attempt refused on 1 of 65 equivalence
cases (a real missing `refusalCode`/`refusalRationale` pair, added at the
real source). I, J, and K each required one further real tool fix — a
missing `receipt-ownership.json` producer (I), `foundry/receipts/` being
gitignored and breaking clean-room replay's independent clone (J), and
`verify_corpus` needing the same latest-per-path receipt-checking fix as
the admission gate it feeds (also J). K manufactured and twice compiled/
tested a real minimal Rust crate from the admitted
`repository_manufacturing_platform` pack, byte-identical across both runs.
Full detail for every fix: [Completion ARD](16-foundry-completion-ard.md).

## Non-goals

- This chapter is a record of what was done, not a claim about anything
  beyond this program's own 11 workstreams — it does not certify the
  broader `ggen`/`ggen-legacy` ecosystem, only this program's terminal
  theorem.
- Real tool fixes made along the way live in `~/ggen`
  (`agent/foundry-replay-latest-receipt-per-path`,
  `agent/v26.8.1-fix-extraction-source-paths`) — cite them, don't
  re-derive them, if extending this program further.

## See also

- [Enterprise Architecture Foundry Program](14-enterprise-architecture-foundry.md) — program overview, five corpus layers, repository topology.
- [Completion ARD](16-foundry-completion-ard.md) — the full real fix history, per workstream.
- `governance/production-gaps.md` / `governance/claims-register.md` (CLM-012) — this program's entry in the general ledger.
- `foundry/bootstrap.yaml` — real per-workstream status, deferring to `foundry/workstreams/state.json` and `foundry/evidence/terminal-theorem.json` as authoritative.
