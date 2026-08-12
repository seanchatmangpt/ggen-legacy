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
| C — Capability admission | `admit_capabilities` | `BLOCKED` |
| D — Kernel-corpus classification | `admit_classification` | not attempted |
| E — Cross-repository extraction | `admit_extraction` | not attempted |
| F — Primitive generalization | `admit_products` (stage 1) | not attempted |
| G — bblock/solution-pack composition | `admit_products` (stage 2) | not attempted |
| H — Full equivalence closure | `admit_products` (stage 3) | not attempted |
| I — Independent verification | `admit_verification` | not attempted |
| J — Clean-room manufacture and replay | `admit_clean_room` | not attempted |
| K — Fortune-scale reference reconstitution | `admit_reference` | not attempted |

A and B admitted for real, with real evidence commits and digest chains
recorded in `foundry/bootstrap.yaml`'s `admitted_evidence` blocks and
`foundry/receipts/workstream-{A,B}.json`.

## The real, current blocker (C)

`admit_capabilities` refuses with `UNKNOWN_DISPOSITION: DISPOSITION_UNKNOWN`.
Two of the 65 real legacy capabilities admitted in workstream B
(`foundry/evidence/B/legacy-capabilities.ttl`) carry
`ggen:hasDisposition ggen:DISPOSITION_UNKNOWN`:

- **Line 577** — a capability about a `mode = "Append"` generation-mode
  variant. Its own `ggen:defaultBehavior` field already states: *"Not one of
  the 3 variants (Create/Overwrite/Merge) in the live
  `ggen_config::manifest::types::GenerationMode` enum today."*
- **Line 1595** — a capability about a mutation-kill-rate/budget-threshold
  exit-code check. Its own `ggen:replacementOwner` field already states:
  *"UNKNOWN — this pass did not confirm whether the v5 unified `ggen sync`
  command still exposes an equivalent mutation-kill-rate/budget-threshold
  check under any exit code, or whether the capability was dropped
  entirely."*

Both are honest, pre-existing admissions of incomplete investigation from
whoever produced this evidence — not schema defects, and not something this
PRD (or any planning document) resolves. See the companion
[Completion ARD](16-foundry-completion-ard.md) for what closing them
actually requires.

## Requirement

Workstream C, and everything after it (D–K), admits only when:

1. Both capabilities above carry a real, verified disposition — determined
   by actually checking `~/ggen`'s current source (does
   `GenerationMode` have an `Append` variant today; does the v5 unified
   `ggen sync` command expose an equivalent threshold check), not by
   assigning a plausible-sounding value.
2. `admit_capabilities` is re-run for real and itself reports the real
   outcome — this document does not assert in advance that it will succeed.
3. The same discipline — read the real verifier binary, determine what real
   evidence or real decision it requires, obtain that evidence for real, run
   it, record the real result — repeats for D through K. This PRD does not
   pre-certify that D–K's real evidence exists; see the ARD for what is and
   isn't yet known about each.

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
