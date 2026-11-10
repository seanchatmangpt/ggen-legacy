# T012 — Extend shared-table tripwire from 13 to all srve_* tables

Standing: REGISTERED

Wave: W0 · Depends on: T-011
Owned paths: ~/srve/onengine-backend (test only)
Research lanes: L04, L06

## Scope

src/xaas-contract EXPECTED_SHARED_TABLES covers the original 13; 60 srve_* tables are unguarded.
Extend the contract test to every table with its owning resource. Prisma stays unmodeled for
srve_*.

## Acceptance

- Contract test names every census table.
- Adding a table without an entry fails the test.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/onengine-backend && npx jest __tests__/sharedTables.contract.test.ts
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t012-shared-table-tripwire-extension.md (under docs/jira/v26.11.9/)
Falsifier: A table added in xaas with no test entry still passes.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-012`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/distinct] tripwire names every census table (distinct)
  - paths:
    - `srve:onengine-backend/src/xaas-contract`
  - pattern: `srve_[a-z_0-9]+`
  - n: `73`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
