# Enterprise Architecture Foundry — Completion ARD (Workstreams C–K)

Architecture requirements for closing the gap named in the
[Completion PRD](15-foundry-completion-prd.md). Each section names the real
verifier binary in `~/ggen/tools/architecture-foundry/src/bin/`, the real
refusal codes it can return (read directly from its source this session),
and what is and is not yet known about whether its real evidence exists.
Nothing here pre-guesses an answer a real investigation hasn't produced.

## C — Capability admission (`admit_capabilities.rs`)

**Blocking now.** Real refusal: `UNKNOWN_DISPOSITION: DISPOSITION_UNKNOWN`.

Requirement to close: a real, verified disposition for the two capabilities
named in the PRD (`foundry/evidence/B/legacy-capabilities.ttl` lines 577 and
1595). Concretely:

- Line 577 (`Append` generation-mode variant): check
  `ggen_config::manifest::types::GenerationMode`'s current real definition in
  `~/ggen` (`git grep -n "enum GenerationMode"` or equivalent) — does an
  `Append` variant exist today, under any name? If not, was it ever added
  and removed (`git log -p` on the enum), or never implemented at all?
- Line 1595 (mutation-kill-rate/budget-threshold exit-code check): check
  whether the real, current v5 unified `ggen sync` command
  (`git log --all -p -S'fail_on_threshold'` or equivalent, per the
  capability's own `evidenceFixtures` hint) still exposes an equivalent
  check under any exit code.

Both are answerable from `~/ggen`'s real git history — this is real
investigation work, not a design decision, and not something an ARD
performs on its own.

The binary's other real refusal codes (`CAPABILITY_PROPERTY_EMPTY`,
`REPLACEMENT_OWNER_MISSING`, `TURTLE_STRING_UNTERMINATED`) were not hit this
pass — no claim is made about whether the remaining 63 capabilities would
pass those checks; only that the run got as far as
`UNKNOWN_DISPOSITION` before refusing.

## D — Kernel-corpus classification (`admit_classification.rs`)

**Not attempted.** Real refusal codes present in source:
`CLASSIFICATION_DISPOSITION_UNKNOWN`. Its real required inputs (beyond
`--program --source --corpus`) were not read this pass. **Unverified**
whether real evidence for this workstream exists anywhere in `~/ggen`'s
history the way B's did.

## E — Cross-repository extraction (`admit_extraction.rs`)

**Not attempted.** Real refusal codes present in source:
`CLASSIFICATION_ID_CONFLICT`, `DESTINATION_PATH_ESCAPES_CORPUS`,
`DESTINATION_PATH_INVALID`, `EXTRACTION_INPUT_COUNT_MISMATCH`. Depends on D
being admitted first (per `foundry/workstreams/state.json`'s dependency
graph). **Unverified** what real extraction inputs it expects.

## F, G, H — Primitive/pack/equivalence (`admit_products.rs`, 3 stages)

**Not attempted.** One binary, three internal stages
(`require_stage`/`finish_stage` helpers). Real refusal codes present in
source: `EQUIVALENCE_DISPOSITION_UNKNOWN`, `PACK_INPUT_PRIMITIVES_EMPTY`,
`PRIMITIVE_ADMISSION_REFUSED`. Depends on E. **Unverified** real inputs for
any of the three stages.

## I — Independent verification (`admit_verification.rs`)

**Not attempted.** Real refusal codes present in source:
`RECEIPT_OUTPUT_DRIFT`, `RECEIPT_PORTFOLIO_INCOMPLETE`,
`RECEIPT_REPOSITORY_INVALID`, `RECEIPT_SCHEMA_INVALID`,
`RECEIPT_SUBJECT_DIGEST_INVALID`, `SYSTEM_EVIDENCE_MISSING`,
`SYSTEM_EVIDENCE_NEGATIVE_CONTROL_FAILED`,
`SYSTEM_EVIDENCE_RECEIPT_PORTFOLIO_INCOMPLETE`. Depends on G and H. This is
the richest refusal surface found in the binary set — likely requires a
complete, consistent receipt DAG across every prior workstream, which by
construction cannot be assembled until D–H are real.

## J — Clean-room manufacture and replay (`admit_clean_room.rs`)

**Not attempted.** Real refusal code present in source:
`CLEAN_ROOM_HEAD_MISMATCH`. Depends on I.

## K — Fortune-scale reference reconstitution (`admit_reference.rs`)

**Not attempted.** Real refusal code present in source:
`REFERENCE_PACK_PRIMITIVES_INVALID`. Depends on J. This is also the last
workstream before `admit_final.rs`'s terminal 11/11 admission — not read in
detail this pass.

## Sequencing requirement

Per `foundry/workstreams/state.json`'s real dependency graph
(`A→B→C→D→E→F→G(→H)→I→J→K`, with H also depending on F), each workstream
must be attempted in order — a later workstream cannot honestly be
investigated in isolation before its dependencies are real, since its own
verifier binary requires the prior workstream's real `ADMITTED` state and
receipt chain as input. This ARD therefore does not attempt to front-load
D–K's evidence requirements beyond what their source already reveals; each
gets the same one-at-a-time treatment C just received, in order.

## See also

- [Completion PRD](15-foundry-completion-prd.md) — requirements and current real standing.
- [Enterprise Architecture Foundry Program](14-enterprise-architecture-foundry.md) — program overview.
- `governance/production-gaps.md` — general ledger this program's gap is cross-linked into.
