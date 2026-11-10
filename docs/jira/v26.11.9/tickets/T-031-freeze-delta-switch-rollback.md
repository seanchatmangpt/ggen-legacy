# T031 — Write freeze, delta sync, atomic switch, rollback

Standing: REGISTERED

Wave: W3 · Depends on: T-003, T-023, T-032
Owned paths: ~/ggen-create + ~/srve
Research lanes: L20, L11

## Scope

cutover.power sequence: legacy write-freeze, final delta ETL to zero diff, flip origin (T-004) and
per-family VITE_XAAS_FAMILY_* flags, verify, sign-off gate. cutover.rollback restores xaas as
active in one command. Irreversible: writes accepted on srve_* (needs reverse ETL or freeze),
session format switch (users re-login), legacy table drops and decommission (deferred entirely),
notification/email sends. Rollback must leave no rows written only to the new store.

## Acceptance

- Rollback restores a working :4000 xaas and zero rows exist only in the new store.
- Power refuses when freeze not declared.

## Gates (verbatim, not yet run)

```bash
cd ~/ggen-create && ggen-create cutover plan --dry-run
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t031-freeze-delta-switch-rollback.md (under docs/jira/v26.11.9/)
Falsifier: Rollback leaves rows written only to the new backend.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-031`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/count] cutover.py defines rollback
  - paths:
    - `ggen-create:src/ggen_create/cutover.py`
  - pattern: `rollback`
  - n: `1`
- [T0/count] round-trip, drift and all-or-nothing tests exist (not executed by the dry-run)
  - paths:
    - `ggen-create:tests/test_cutover.py`
  - pattern: `byte_exact|TARGET_DRIFT_REFUSED|all-or-nothing`
  - n: `3`
- [T0/count] receipt-chain test exists
  - paths:
    - `ggen-create:tests/test_cutover.py`
  - pattern: `receipt\.chain\.verify`
  - n: `1`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
