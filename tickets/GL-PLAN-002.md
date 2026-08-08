# GL-PLAN-002 — combinatorial-max benchmark planning and recursive admission

**Status:** admitted concurrent executable ticket  
**Base:** `seanchatmangpt/ggen-legacy@982fea0a476ae7c74d2c31ab876650bdae1bd6d4`  
**Standing ceiling:** `PARTIAL_ALIVE`  
**Publication:** draft pull request; no merge authority

## Outcome

Manufacture an independent bounded planning/search/verification layer that can reconstruct benchmark goal-state constraints without reference-solution leakage, preserve the maximal finite reversible capability graph, project to multiple planner/process representations, recursively decompose blocked parent goals, admit independently verified children, resume the parent, and replay the evidence chain.

## Authored boundary

```text
AGENTS.md                            # concurrent ticket admission stanza only
justfile                             # planning-max target only
.github/workflows/planning-v26-8-7.yml
planning/v26.8.7/**
tickets/GL-PLAN-002.md
```

GL-LSP-001 and all existing generated contract surfaces remain outside this ticket.

## Required transitions

```text
parse benchmark
→ admit/refuse goal constraints
→ construct finite reversible state graph
→ preserve every lawful child edge
→ select one consequential child (WIP=1)
→ manufacture construct-only intent
→ independent verifier receipt
→ admit exact child subject
→ replan/resume parent
→ project candidate representations
→ receipt/replay
```

## Hard laws

1. Reference/gold solutions are excluded from goal reconstruction.
2. Planning selects; it does not actuate.
3. Hooks/projections manufacture intents only; they have no direct actuation authority.
4. A planner success cannot self-promote subsystem, repository, release, or production standing.
5. Unsupported planner/dialect features are preserved as topology and never silently simplified.
6. An engine registry entry, process help witness, or source inspection is not solver execution.
7. Child admission requires a verified receipt bound to the exact capability subject.
8. One failed planner edge does not imply graph failure.
9. External MFW/scikit-decide standing requires observed exact-subject execution; missing trees/runtimes are typed `BLOCKED`.
10. Event-chain tampering is `BUILD_BROKEN`.

## Acceptance

```bash
python3 planning/v26.8.7/verify.py --strict
python3 -m unittest discover -s planning/v26.8.7/tests -v
planning/v26.8.7/skdecide_classical_engine.py --help
```

The verifier must demonstrate the full finite career-capability parent/child cycle and emit a machine-readable report with distinct observed/admitted/executed/changed/verified/inferred/refused/blocked/unsupported evidence.

## Falsifiers

- a reference solution is admitted;
- unsupported PDDL is rewritten or dropped;
- scikit-decide is claimed successful without observed scikit-decide execution;
- a manufacture intent actuates or admits itself;
- a mismatched receipt admits a child;
- the parent fails to resume after verified child admission;
- replay accepts a modified chain;
- missing MFW/planner runtime is relabeled as success;
- any ticket edit changes GL-LSP-001 authority or generated LSP contract surfaces.
