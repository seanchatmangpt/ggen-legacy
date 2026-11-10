# T004 — Frontend: one backend-origin variable feeds every call site

Standing: REGISTERED

Wave: W0 · Depends on: none
Owned paths: ~/srve/servengine-frontend
Research lanes: L12

## Scope

Introduce one resolver (VITE_BACKEND_ORIGIN) replacing the chain VITE_XAAS_AUTH_URL / API_URL /
RPC_URL / RPC_BASE_URL / VITE_BASE_URL. Remove the 8 non-test hardcoded http://localhost:4000
fallbacks (jsonApiClient.ts:29, ashRpcClient.ts:46, queries/core.ts:28, backendHealth.ts:12,
dispatch-queue.queries.ts:10, XaasDemo/SurveyCaptureGrid.tsx:129, three *.court.test.ts,
vite.config.ts ashAdminProxy). Courts read the origin variable. VITE_LOCAL_API_PROXY and
VITE_XAAS_PROXY_URL derive from it.

## Acceptance

- `grep -rn localhost:4000 src vite.config.ts` returns no non-test hits.
- Setting only the origin variable sends every request to that host (network-tab check in a
  court).
- The *.court.test.ts files run against a second port.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/servengine-frontend && grep -rn 'localhost:4000' src vite.config.ts
cd ~/srve/servengine-frontend && npx tsc --noEmit
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t004-fe-single-backend-origin.md (under docs/jira/v26.11.9/)
Falsifier: A request still reaches another host after only the origin variable changes.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-004`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/absent] no localhost:4000 in non-test FE source
  - paths:
    - `srve:servengine-frontend/src`
    - `srve:servengine-frontend/vite.config.ts`
  - pattern: `localhost:4000`
- [T0/count] resolver variable referenced
  - paths:
    - `srve:servengine-frontend/src`
  - pattern: `VITE_BACKEND_ORIGIN`
  - n: `1`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
