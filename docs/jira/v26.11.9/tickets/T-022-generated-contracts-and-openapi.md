# T022 — Contracts and OpenAPI generated from the backend schema

Standing: REGISTERED

Wave: W1 · Depends on: T-009, T-015
Owned paths: ~/srve/servengine-frontend/packages/contracts
Research lanes: L12, L06, L09

## Scope

Hand-written packages/contracts (schemas.ts, woStatus.ts, woTransitions.ts) is deleted in favor of
generated output; regenerate src/contracts/xaas-generated/{ash_rpc,ash_types,ash_zod}.ts from the
candidate. Emit OpenAPI covering 100% of the T-009 inventory (legacy covers ~21%).
ash_typescript/ash_surface are unverified candidates; confirm the emitting mix task on a fixture
first.

## Acceptance

- Backend schema change changes contracts output.
- OpenAPI diff versus inventory is empty.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ggen sync run && git status --short servengine-frontend/packages/contracts
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t022-generated-contracts-and-openapi.md (under docs/jira/v26.11.9/)
Falsifier: A backend schema change does not change the contracts output.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-022`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T1

Clauses:
- [T0/not_exists] hand-written contracts removed
  - paths:
    - `srve:servengine-frontend/packages/contracts/src/schemas.ts`
- [T1/unverified] regenerate contracts in scratch and diff
  - reason: `needs ggen sync in scratch`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
