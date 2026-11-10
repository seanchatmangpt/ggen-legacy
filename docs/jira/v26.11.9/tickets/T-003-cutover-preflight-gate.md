# T003 — Preflight gate: refuse switch unless prerequisites hold

Standing: REGISTERED

Wave: W0 · Depends on: T-001
Owned paths: ~/ggen-create + ~/srve
Research lanes: L20, L14, L10

## Scope

cutover.plan runs a preflight and refuses (typed, with broken_term) unless: srve_* migrations
applied, auth bridge (T-020) configured, KP07 shared-table tripwire green, Release Admission
admitted:true, two-probe identity law passes on the candidate, and legacy write-freeze is
declared.

## Acceptance

- Each unmet prerequisite maps to one typed refusal code.
- With all prerequisites met preflight exits 0 and records its inputs in the plan.

## Gates (verbatim, not yet run)

```bash
cd ~/ggen-create && python3 -m unittest tests/test_cutover.py -k preflight
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t003-cutover-preflight-gate.md (under docs/jira/v26.11.9/)
Falsifier: Preflight passes with a missing migration or with release_admitted:false.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-003`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/count] cutover.py defines preflight refusals
  - paths:
    - `ggen-create:src/ggen_create/cutover.py`
  - pattern: `preflight`
  - n: `1`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
