# T030 — Parametrize kind scripts, align Postgres, replace asset-hash smoke

Standing: REGISTERED

Wave: W3 · Depends on: T-017
Owned paths: ~/srve/scripts + justfile
Research lanes: L14

## Scope

kind-bootstrap.sh, kind_doctor.sh, kind-smoke-test.sh hardcode cluster kind-xaas, deployment xaas,
image xaas:local. Accept BACKEND=ggen. Postgres: KinD uses postgres:16-alpine while compose uses
pgvector/pgvector:pg15 and migrations may need the vector extension (verify). Smoke test checks
hashed assets (index-DHFaKXPx.js); replace with one API route plus a DB query, assets discovered
not hardcoded. `just cutover backend=<xaas|ggen>` recipe.

## Acceptance

- grep for xaas:local and deployment/xaas in scripts/kind* returns nothing.
- Smoke fails against a dead backend and passes after an FE rebuild.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && grep -n 'xaas:local\|deployment/xaas' scripts/kind*
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t030-kind-scripts-parametrize-backend.md (under docs/jira/v26.11.9/)
Falsifier: A frontend rebuild breaks the smoke test.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-030`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/absent] no xaas:local / deployment/xaas in kind scripts
  - paths:
    - `srve:scripts/kind-*.sh`
    - `srve:scripts/kind_doctor.sh`
  - pattern: `xaas:local|deployment/xaas`
- [T0/absent] no hashed asset names in smoke test
  - paths:
    - `srve:scripts/kind-smoke-test.sh`
  - pattern: `index-[A-Za-z0-9_-]{8}\.(js|css)`
- [T0/cmd] bash -n scripts/kind-bootstrap.sh
  - argv:
    - `bash`
    - `-n`
    - `@srve:scripts/kind-bootstrap.sh`
- [T0/cmd] bash -n scripts/kind-smoke-test.sh
  - argv:
    - `bash`
    - `-n`
    - `@srve:scripts/kind-smoke-test.sh`
- [T0/cmd] bash -n scripts/kind_doctor.sh
  - argv:
    - `bash`
    - `-n`
    - `@srve:scripts/kind_doctor.sh`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
