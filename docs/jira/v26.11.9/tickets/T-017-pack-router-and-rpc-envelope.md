# T017 — Backend pack: router and RPC envelope parity

Standing: REGISTERED

Wave: W1 · Depends on: T-010, T-015
Owned paths: ~/srve/packs/srve-backend-pack
Research lanes: L02

## Scope

Generate POST /internal-api/rpc/run and /rpc/validate for every RPC action in the cutover scope
manifest with {success,data|errors} kept on 400/401; rpc routes declared before any catch-all
forward; typed 400 on malformed fields spec (validate_rpc_fields); interpolated error handler
parity; bearer plus X-Tenant-Id and acting-entity-id handling; CORS OPTIONS 204.

## Acceptance

- Every in-scope RPC action returns the envelope shape; 400/401 keep it.
- Malformed fields returns typed 400, never 500.
- rpc/run never returns no_route_found.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/servengine-frontend \
  && XAAS_TEST_URL=$CANDIDATE npx vitest run --config vitest.process.config.ts
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t017-pack-router-and-rpc-envelope.md (under docs/jira/v26.11.9/)
Falsifier: Any action returns non-JSON or a bare error body.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-017`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T2

Clauses:
- [T0/exists] router template
  - paths:
    - `srve:packs/srve-backend-pack/templates/router.ex.tera`
- [T2/unverified] 290 actions return envelope; fields spec typed 400
  - reason: `needs candidate running`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
