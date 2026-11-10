# T021 — Two-probe identity law and CORS on the candidate

Standing: REGISTERED

Wave: W1 · Depends on: T-017
Owned paths: ~/srve/packs/srve-backend-pack
Research lanes: L02, L13

## Scope

GET /health returns 200 unauthenticated with no DB access; unauthenticated GET /api/health returns
401 'missing or invalid Bearer token'; /internal-api/health token-gated; OPTIONS preflight 204.
The probe must reject wrong servers (ForeignBackendError class).

## Acceptance

- Probe passes on the candidate and refuses a stub that serves /api/health 200.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/servengine-frontend \
  && XAAS_TEST_URL=$CANDIDATE npx playwright test --project=chromium-desktop \
  playwright/globalSetup-tony.ts
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t021-health-two-probe-and-cors.md (under docs/jira/v26.11.9/)
Falsifier: /api/health returns 200 with no token, or OPTIONS /health returns 404.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-021`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T2

Clauses:
- [T0/exists] identity globalSetup present
  - paths:
    - `srve:servengine-frontend/playwright/globalSetup-xaas-identity.ts`
- [T0/cmd] bash -n scripts/dryrun/two_probe.sh
  - argv:
    - `bash`
    - `-n`
    - `@srve:scripts/dryrun/two_probe.sh`
- [T2/unverified] live probe vs candidate; stub serving /api/health 200 refused
  - reason: `needs candidate`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
