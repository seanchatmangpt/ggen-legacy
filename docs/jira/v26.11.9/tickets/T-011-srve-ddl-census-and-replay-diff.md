# T011 — srve_* DDL census and replay-diff harness

Standing: REGISTERED

Wave: W0 · Depends on: none
Owned paths: ~/srve
Research lanes: L04

## Scope

Census final-state DDL of every srve_* table (66 at xaas d7e38a37 from 162 committed migrations;
the working tree adds uncommitted migrations) plus resource_snapshots (56 srve entries; not sole
source). Build a harness comparing pg_dump --schema-only of generated SQL against the xaas-
migrated DB: columns, types, defaults, NOT NULL, FKs, Ash-named indexes, raw execute() alterations
(srve_notes.work_order_id nullability).

## Acceptance

- Census lists every table with columns; count reconciles with migrations grep.
- Harness diff is empty on the xaas DB compared with itself and non-empty on a mutated fixture.

## Gates (verbatim, not yet run)

```bash
cd ~/xaas && grep -rhoE 'create table\(:srve_[a-z_0-9]+' priv/repo/migrations | sort -u | wc -l
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t011-srve-ddl-census-and-replay-diff.md (under docs/jira/v26.11.9/)
Falsifier: A table in migrations missing from the census, or an injected column change not
flagged.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-011`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T1

Clauses:
- [T0/distinct] distinct srve_* tables in migrations
  - paths:
    - `xaas:priv/repo/migrations`
  - pattern: `create table\(:srve_[a-z_0-9]+`
  - n: `73`
- [T0/exists] ddl census
  - paths:
    - `ggen-legacy:docs/jira/v26.11.9/manifests/ddl-census.json`
- [T1/unverified] pg_dump replay diff
  - reason: `needs scratch Postgres replay of 166 migrations`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
