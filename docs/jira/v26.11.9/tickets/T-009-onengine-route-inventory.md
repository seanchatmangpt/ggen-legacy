# T009 — Route inventory extractor and OpenAPI reconciliation for onengine-backend

Standing: REGISTERED

Wave: W0 · Depends on: none
Owned paths: ~/srve/onengine-backend (read-only) + scripts
Research lanes: L06

## Scope

Emit a machine-readable inventory (method, path, module, auth middleware, controller) for every
route registration (840 at onengine-backend e78330aa, router.<verb>, public and app variants).
Reconcile against swagger/output/openapi.yaml (148 paths, 185 verbs, about a fifth of the routes)
and apiDefinition/. The inventory is the legacy half of parity; onengine-backend is not edited.

## Acceptance

- Inventory count equals the derivation grep count exactly.
- A diff lists every undocumented route.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/onengine-backend \
  && grep -rEc 'router\.(get|post|put|patch|delete)\(' src/modules | awk -F: '{s+=$2} END{print s}'
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t009-onengine-route-inventory.md (under docs/jira/v26.11.9/)
Falsifier: A route registered in the Express app but absent from the inventory.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-009`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/exists] route inventory
  - paths:
    - `ggen-legacy:docs/jira/v26.11.9/manifests/route-inventory.json`
- [T0/fresh] manifest matches onengine-backend HEAD
  - path: `ggen-legacy:docs/jira/v26.11.9/manifests/route-inventory.json`
  - repos:
    - `srve/onengine-backend`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
