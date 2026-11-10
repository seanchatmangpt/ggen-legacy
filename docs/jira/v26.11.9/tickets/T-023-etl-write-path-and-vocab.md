# T023 — ETL: verify the write path and reconcile status vocabularies

Standing: REGISTERED

Wave: W1 · Depends on: T-011
Owned paths: ~/srve/scripts/etl
Research lanes: L07, L20

## Scope

etl.ts (848 lines, 10 aggregates, PARTIAL_ALIVE) has only a verified dry run. Run the real write
into a scratch DB with per-aggregate src/dst count and checksum. Reconcile vocabularies in one
table (WO 23 mapped keys to 8 atoms; 25 DB rows vs 29 enum constants unreconciled; invoice 5 keys;
SP 3 keys): every legacy value mapped or rejected, no silent fallback to draft/onboarding. Add DDL
preflight gate and PRESERVATION_MAP (planned, not in etl.ts).

## Acceptance

- Second run changes neither row count nor checksum.
- unmapped* is empty on a real dump; fallbacks fail loudly.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/scripts/etl && npx tsx etl.ts --dry-run
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t023-etl-write-path-and-vocab.md (under docs/jira/v26.11.9/)
Falsifier: A second run changes counts, or any fallback is hit silently.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-023`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T1

Clauses:
- [T0/exists] etl.ts present
  - paths:
    - `srve:scripts/etl/etl.ts`
- [T0/count] PRESERVATION_MAP implemented
  - paths:
    - `srve:scripts/etl/etl.ts`
  - pattern: `PRESERVATION_MAP`
  - n: `1`
- [T1/unverified] real write into scratch DB; counts and checksums
  - reason: `needs scratch Postgres`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
