# T010 — Cutover scope: actions and prefixes the frontend actually calls

Standing: REGISTERED

Wave: W0 · Depends on: none
Owned paths: ~/srve/servengine-frontend
Research lanes: L02, L16, L12

## Scope

From src/lib/xaas/__register__/call-register.json (rows split by kind; the 290-generated figure is
a summary field, the rows hold about 20 RPC entries) and the /api/* prefix census, produce the
authoritative cutover-scope file: domains, RPC actions, REST prefixes. Everything outside it is
non-scope (T-035). Prefix to controller mapping is traced, not inferred from names.

## Acceptance

- Scope file lists each called action and prefix with its owning domain.
- Every prefix in src/ appears in the file.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/servengine-frontend && jq '.rows | length' src/lib/xaas/__register__/call-register.json
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t010-fe-called-action-scope.md (under docs/jira/v26.11.9/)
Falsifier: A prefix or RPC action called by the FE is missing from the scope file.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-010`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/exists] cutover scope file
  - paths:
    - `ggen-legacy:docs/jira/v26.11.9/manifests/cutover-scope.json`
- [T0/fresh] manifest matches frontend HEAD
  - path: `ggen-legacy:docs/jira/v26.11.9/manifests/cutover-scope.json`
  - repos:
    - `srve/servengine-frontend`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
