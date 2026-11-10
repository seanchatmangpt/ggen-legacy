# T016 — Backend pack: migrations that replay to byte-equivalent DDL

Standing: REGISTERED

Wave: W1 · Depends on: T-011, T-015
Owned paths: ~/srve/packs/srve-backend-pack
Research lanes: L04, L09

## Scope

Generate the migration chain (including execute() alterations and updated_at backfill order) so
the pack owns the srve_* chain instead of xaas. Both backends must never run migrations against
the same DB (schema_migrations conflict): the cutover hands ownership over once.

## Acceptance

- T-011 harness diff is empty against the xaas-migrated DB.
- schema_migrations ownership recorded in the cutover plan.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ./scripts/ddl_replay_diff.sh
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t016-pack-migrations-ddl.md (under docs/jira/v26.11.9/)
Falsifier: Two backends run migrations on one DB, or any column default/index name differs.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-016`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T1

Clauses:
- [T0/exists] migration template
  - paths:
    - `srve:packs/srve-backend-pack/templates/migration.exs.tera`
- [T1/unverified] generated DDL equals xaas-migrated DB
  - reason: `needs scratch Postgres`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
