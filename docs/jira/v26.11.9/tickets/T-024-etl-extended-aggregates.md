# T024 — ETL: extend to the ~35 aggregates and backfill post-ETL fields

Standing: REGISTERED

Wave: W1 · Depends on: T-023, T-016
Owned paths: ~/srve/scripts/etl
Research lanes: L07

## Scope

Implement docs/plan/21 wave by wave (about 35 aggregates, 15 vocabulary maps) behind the DM
migration waves. Aggregates without target DDL are skipped with warning. Backfill what ETL cannot
write: srve_tenants.org_id, derived SP caches, overdue status, note authors.

## Acceptance

- Each aggregate ships with map, checksum and spot-check.
- Post-ETL fields non-NULL after the backfill step.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/scripts/etl && npx tsx etl.ts --dry-run --all
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t024-etl-extended-aggregates.md (under docs/jira/v26.11.9/)
Falsifier: An aggregate with no target DDL fails the run instead of skipping.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-024`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T1

Clauses:
- [T0/count] checksumOver flag implemented
  - paths:
    - `srve:scripts/etl/etl.ts`
  - pattern: `checksumOver`
  - n: `1`
- [T0/count] --all flag implemented
  - paths:
    - `srve:scripts/etl/etl.ts`
  - pattern: `--all`
  - n: `1`
- [T1/unverified] ~35 aggregates and 15 vocabulary maps of docs/plan/21 implemented
  - reason: `only the flag/engine is checkable from files; aggregate coverage needs a run`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
