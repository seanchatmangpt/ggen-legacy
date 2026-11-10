# T026 — Backend-neutral seed fixture

Standing: REGISTERED

Wave: W2 · Depends on: T-017
Owned paths: ~/srve/scripts
Research lanes: L13

## Scope

Replace `mix run priv/repo/seeds/golden_amc_work_order.exs` with an HTTP/JSON fixture loader (wo-
cycle/00-seed-xaas.client.ts is the seed idiom; dev_seed_controller exists in xaas).

## Acceptance

- Same fixture seeds two backends to identical readbacks.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ./scripts/seed_fixture.sh $URL
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t026-backend-neutral-seed.md (under docs/jira/v26.11.9/)
Falsifier: Omitting a fixture field is not detected by the readback diff.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-026`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T2

Clauses:
- [T0/exists] seed loader
  - paths:
    - `srve:scripts/seed_fixture.sh`
- [T0/cmd] bash -n scripts/seed_fixture.sh
  - argv:
    - `bash`
    - `-n`
    - `@srve:scripts/seed_fixture.sh`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
