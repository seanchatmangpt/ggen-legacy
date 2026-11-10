# T034 — Retirement manifest for xaas non-core domains

Standing: REGISTERED

Wave: W3 · Depends on: T-010
Owned paths: ~/srve/docs
Research lanes: L16, L15

## Scope

Assign each lib/xaas directory an owner (repo, new repo, drop): ultracode (44k LOC), governance
(7.2k), semantics, sjira, sa2a/a2a, zoe, gall, witness/ocel/receipt group, marketplace,
conference, research dirs. Keep list: serv_engine, procurement, billing, accounts, platform,
security, ledger (into billing); operations and library need a check. Cross-domain scan: any alias
from keep-list modules into non-core modules.

## Acceptance

- Every directory has an owner.
- Scan lists keep-list to non-core aliases with disposition.

## Gates (verbatim, not yet run)

```bash
cd ~/xaas && ls lib/xaas | wc -l
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t034-non-core-domain-retirement-manifest.md (under docs/jira/v26.11.9/)
Falsifier: A lib/xaas directory has no owner, or a keep-list module aliases a dropped domain.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-034`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/exists] retirement manifest
  - paths:
    - `ggen-legacy:docs/jira/v26.11.9/manifests/retirement-manifest.md`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
