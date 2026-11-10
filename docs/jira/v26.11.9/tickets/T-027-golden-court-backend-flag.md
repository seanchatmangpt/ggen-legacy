# T027 — bin/golden-court --backend URL

Standing: REGISTERED

Wave: W2 · Depends on: T-025, T-026
Owned paths: ~/srve/bin/golden-court
Research lanes: L13

## Scope

Add --backend: skip mix steps, run only the HTTP courts and two-probe identity. Restore
src/test/realServer.ts and setup.process.ts (referenced by real-backend.yml, not found) so FE
court 3 stops skipping loudly.

## Acceptance

- Dead port exits non-zero at the identity probe with no mix invoked.
- fe_golden_wire prints PASS, not SKIP.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && bin/golden-court --backend http://localhost:4000
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t027-golden-court-backend-flag.md (under docs/jira/v26.11.9/)
Falsifier: fe_golden_wire still prints SKIP.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-027`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/count] flag implemented
  - paths:
    - `srve:bin/golden-court`
  - pattern: `--backend`
  - n: `1`
- [T0/cmd] bash -n bin/golden-court
  - argv:
    - `bash`
    - `-n`
    - `@srve:bin/golden-court`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
