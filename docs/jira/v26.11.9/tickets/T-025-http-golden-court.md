# T025 — HTTP golden court ported from the Elixir courts

Standing: REGISTERED

Wave: W2 · Depends on: T-017, T-018
Owned paths: ~/srve/servengine-frontend/playwright + vitest
Research lanes: L13

## Scope

Restate golden_lifecycle_court_test.exs (ingest to invoice, NTE refusal, 7 OCEL events, cross-
tenant invoice masking) and golden_saga_replay_court over HTTP only, driven by XAAS_TEST_URL.
Extract the HTTP contract from the route census and ConnCase wire courts (json_api_route_census,
entity_surface_rpc, cors, correlation_id, clients_tenant_scope).

## Acceptance

- Passes against ~/xaas :4000 and the candidate; fails against a stub backend.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/servengine-frontend && XAAS_TEST_URL=http://localhost:4000 npx vitest run golden
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t025-http-golden-court.md (under docs/jira/v26.11.9/)
Falsifier: The court passes against a stub backend.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-025`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T2

Clauses:
- [T0/exists] http golden spec
  - paths:
    - `srve:servengine-frontend/playwright/e2e/golden-http-court.spec.ts`
- [T2/unverified] passes on xaas, fails on stub
  - reason: `needs xaas and stub running`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
