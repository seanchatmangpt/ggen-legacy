# T005 — Ontology: executable action semantics on sv:Action

Standing: REGISTERED

Wave: W0 · Depends on: none
Owned paths: ~/srve/ontology
Research lanes: L08, L01

## Scope

servengine-current.ttl models 459 actions but carries no executable semantics (guard on 1 action;
sv:Policy has no expressions; no validations, changes, calculations, identities, invariants). Add
machine-readable predicates for guard, validation, change, policy expression, actor role, side
effect; extend servengine-current.shacl.ttl so an action missing them fails. Domain-data shapes,
not only ontology-shape checks.

## Acceptance

- SHACL fails on any sv:Action lacking guard/validation/change/policy predicates (or an explicit
  `none`).
- Counts re-derived by SPARQL, not recalled.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ggen sync run --dry-run
cd ~/srve && python3 scripts/check-cardinality.py
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t005-ontology-executable-action-semantics.md (under docs/jira/v26.11.9/)
Falsifier: An Ash action with a validate or change that the ontology lacks passes SHACL.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-005`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/count] sv:Action count == 459 (derivation)
  - paths:
    - `srve:ontology/servengine-current.ttl`
  - pattern: ` a sv:Action\b`
  - n: `459`
- [T0/count] every action carries a guard predicate
  - paths:
    - `srve:ontology/servengine-current.ttl`
  - pattern: `sv:guard`
  - n: `459`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
