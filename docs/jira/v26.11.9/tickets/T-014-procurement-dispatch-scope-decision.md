# T014 — Decision: procurement, dispatch, forms, W9 scope

Standing: REGISTERED

Wave: W0 · Depends on: T-010, T-013
Owned paths: ~/srve/docs
Research lanes: L05, L06, L16

## Scope

Procurement (40k lines, 160 routes, 17.6k-line service.ts, external flight/part/email/quotation
integrations), dispatcher/sweep/ranking tables and form builder have no one: class. Record per
area: in-scope with ontology classes added, ported behind ports, or out-of-scope with explicit
UNSUPPORTED row. Cutover refuses to route a table with no owner.

## Acceptance

- Every area has a recorded disposition and owner.
- Integration helpers are isolated behind ports for any in-scope area.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && grep -c 'procurement' ontology/procurement.ttl
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t014-procurement-dispatch-scope-decision.md (under docs/jira/v26.11.9/)
Falsifier: A procurement route routed by the cutover with no recorded owner.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-014`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/exists] scope decision record
  - paths:
    - `ggen-legacy:docs/jira/v26.11.9/manifests/scope-decisions.md`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
