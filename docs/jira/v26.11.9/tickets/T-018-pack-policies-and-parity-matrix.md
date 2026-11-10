# T018 — Backend pack: policies with an allow/deny parity matrix

Standing: REGISTERED

Wave: W1 · Depends on: T-005, T-015
Owned paths: ~/srve/packs/srve-backend-pack
Research lanes: L01, L03

## Scope

71 serv_engine files use Ash.Policy.Authorizer. Generate policies from sv:Policy expressions
(T-005) and prove them with an actor x tenant x action allow/deny matrix captured from xaas and
replayed on the candidate.

## Acceptance

- Matrix identical on tenant isolation and role cases.
- Masked money fields null, never 0.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ./scripts/policy_matrix_diff.sh
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t018-pack-policies-and-parity-matrix.md (under docs/jira/v26.11.9/)
Falsifier: Any tenant-isolation or role case diverges.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-018`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T2

Clauses:
- [T0/exists] policy template
  - paths:
    - `srve:packs/srve-backend-pack/templates/policy.ex.tera`
- [T2/unverified] actor x tenant x action matrix vs recorded xaas
  - reason: `needs matrix capture from xaas`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
