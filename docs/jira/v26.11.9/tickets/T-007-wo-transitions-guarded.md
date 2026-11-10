# T007 — Work-order state machine: 48 transitions as guarded, queryable facts

Standing: REGISTERED

Wave: W0 · Depends on: T-005
Owned paths: ~/srve/ontology + queries
Research lanes: L08, L01, L07

## Scope

work-order-lifecycle.ttl holds 48 one:transition triples with free-text evidence; sv: holds 11.
Reify each with machine-readable guard, actor role and side effect; extend queries/wo-
transitions.rq. Visit and proposal guards (visit_status_transition_guard, proposal_status_guard,
client_update_status_guard) are modeled the same way or listed as residue (T-008).

## Acceptance

- 48/48/48 agreement across legacy FSM, ontology and Ash transition list.
- No guard exists only inside rdfs:comment text.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ggen sync run --dry-run
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t007-wo-transitions-guarded.md (under docs/jira/v26.11.9/)
Falsifier: A transition with its guard only in comment text, or a legal/illegal edge
accepted/rejected differently.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-007`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/count] ontology transitions == 48
  - paths:
    - `srve:ontology/work-order-lifecycle.ttl`
  - pattern: `^one:\S+ one:transition one:\S+ \.`
  - n: `48`
- [T0/count] Ash transition() entries == 48
  - paths:
    - `xaas:lib/xaas/serv_engine/operations/work_order.ex`
  - pattern: `transition\(`
  - n: `48`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
