# Enterprise Architecture Foundry — Completion PRD (Workstreams C–K)

This chapter states what remains to finish the Enterprise Architecture Foundry
program described in
[Enterprise Architecture Foundry Program](14-enterprise-architecture-foundry.md),
grounded only in real, executed evidence — no workstream past what has
actually been run is described as done, and no unresolved gap is described as
closed.

## Real standing as of this pass

Using the real `tools/architecture-foundry` runtime (`~/ggen`, PR #544,
merged) against this repo's `authority/foundry-work-program.json` and
`foundry/workstreams/state.json` (the authoritative source per
`foundry/bootstrap.yaml`'s own `workstreams_authority_note`):

| Workstream | Verifier binary | Real status |
|---|---|---|
| A — Exact-head baseline | `admit_baseline` | `ADMITTED` |
| B — Exhaustive observation | `admit_observation` | `ADMITTED` |
| C — Capability admission | `admit_capabilities` | `ADMITTED` |
| D — Kernel-corpus classification | `admit_classification` | `ADMITTED` |
| E — Cross-repository extraction | `admit_extraction` | `BLOCKED` |
| F — Primitive generalization | `admit_products` (stage 1) | not attempted |
| G — bblock/solution-pack composition | `admit_products` (stage 2) | not attempted |
| H — Full equivalence closure | `admit_products` (stage 3) | not attempted |
| I — Independent verification | `admit_verification` | not attempted |
| J — Clean-room manufacture and replay | `admit_clean_room` | not attempted |
| K — Fortune-scale reference reconstitution | `admit_reference` | not attempted |

A, B, and C admitted for real, with real evidence commits and digest chains
recorded in `foundry/bootstrap.yaml`'s `admitted_evidence` blocks and
`foundry/receipts/workstream-{A,B,C}.json`.

## Closed: the two DISPOSITION_UNKNOWN capabilities

`admit_capabilities` originally refused with
`UNKNOWN_DISPOSITION: DISPOSITION_UNKNOWN`. Two of the 65 real legacy
capabilities carried `ggen:hasDisposition ggen:DISPOSITION_UNKNOWN`:

- A capability about a `mode = "Append"` generation-mode variant. Resolved
  **`ARCHIVED`**: `~/ggen`'s current `GenerationMode` enum
  (`crates/ggen-config/src/manifest/types.rs`) has exactly 3 variants
  (Create/Overwrite/Merge), no Append; that file was created wholesale in
  the ggen-core-retirement commit (`cbf173f82`), so Append was never
  carried forward and no migration commit links it to a current variant.
- A capability about a mutation-kill-rate/budget-threshold exit-code check.
  Resolved **`REFUSED`**: a real search of `~/ggen`'s current codebase
  found zero matches for the check under any name or exit code — genuinely
  dropped in the v5 unified-sync consolidation, not relocated.

Both resolutions were made at the real source
(`~/ggen`'s `ontology/v26.8.1/legacy-capabilities.ttl`, commit `b7db94e8e`
on `agent/v26.8.1-resolve-2-dispositions`), not by hand-editing the
corpus's receipted transcription — an initial attempt to fix the corpus
copy directly was caught by the tool itself (`RECEIPT_OUTPUT_DRIFT`) and
reverted; see `foundry/bootstrap.yaml`'s workstream B `admitted_evidence`
note for the full account. See the companion
[Completion ARD](16-foundry-completion-ard.md) for the architecture lesson
this drew out.

## D closed; the real, current blocker (E)

Workstream D admitted cleanly once a real tool bug was found and fixed:
`replay_all_receipts` checked every receipt's output digests independently
against current corpus state, so `initialize-corpus`'s stale seed-catalog
digest for `capabilities.json` permanently conflicted with C's legitimate
real replacement of that file. Fixed to check only the causally-latest
receipt per output path (see ARD). D then admitted all 65 capabilities
cleanly, zero unclassified, zero conflicts.

`admit_extraction` (E) refuses `REQUIRED_SOURCE_OBJECTS_UNRESOLVED` for all
17 real `REPLACED`/`SUBSUMED` capabilities. A second real tool bug was
found and fixed along the way (a double-slash path-matching bug for
directory-shaped source paths) but did not resolve any of the 17 — real
investigation of one shows the deeper issue: several `historical_source_commit`
values are the capability's *removal* commit, not a commit where the source
still exists (content lives at the parent, a convention already encoded in
`admit_classification.rs`'s `recovery_command()` but not applied by
`admit_extraction.rs`'s tree resolution), and several `legacy_source_path`
values are genuinely prose comparisons, not single literal git paths. See
the [Completion ARD](16-foundry-completion-ard.md) for the full, real
per-capability breakdown.

## Requirement (now for E–K)

Workstream E's real blocker requires per-capability investigation of the
same character as C's two disposition unknowns, at larger scope (17
capabilities, several genuinely ambiguous) — not a single code fix. F
through K admit only when the same discipline already applied to A–D
repeats: read the real verifier binary, determine what real evidence or
real decision it requires, obtain that evidence for real (never hand-edit
a receipted corpus artifact — fix at the real source and re-run the
admitting binary; never invent a resolution to force a green run), run it,
record the real result. This PRD does not pre-certify that F–K's real
evidence exists; see the ARD.

## Non-goals

- This document does not resolve the two `DISPOSITION_UNKNOWN` capabilities.
- This document does not assert D–K's real evidence requirements are known,
  satisfiable, or currently available — that is exploration work, tracked in
  the ARD, not assumed here.
- This document does not change `authority/foundry-work-program.json`,
  `foundry/bootstrap.yaml`, or run any `admit_*` binary.

## See also

- [Enterprise Architecture Foundry Program](14-enterprise-architecture-foundry.md) — program overview, five corpus layers, repository topology.
- [Completion ARD](16-foundry-completion-ard.md) — architecture/engineering requirements for closing each remaining workstream.
- `governance/production-gaps.md` — this repo's general ledger of what remains and who/what closes it; this program's gap is cross-linked there.
- `foundry/bootstrap.yaml` — the real, current per-workstream status (`workstreams` array, deferring to `foundry/workstreams/state.json` as authoritative).
