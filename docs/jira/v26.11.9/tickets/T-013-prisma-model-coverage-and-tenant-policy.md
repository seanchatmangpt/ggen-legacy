# T013 — Prisma model coverage manifest and tenant-key policy

Standing: REGISTERED

Wave: W0 · Depends on: T-006
Owned paths: ~/srve/ontology + docs
Research lanes: L05

## Scope

Classify all 237 models (re-derive; count recorded in the manifest) as canonical, tenant-only,
legacy or unmapped against canonical.ttl (45 classes carry an aggregate) and the four aggregates
in docs/plan/12. State tenant-keyed vs global per class (suppliers are global after migration
20260715173000; canonical.ttl:208 keeps per-tenant WO numbers). Generated code enforces the
policy.

## Acceptance

- No model unclassified; every one: class has a backing model.
- Per-class tenant policy table matches generated DDL.

## Gates (verbatim, not yet run)

```bash
cd ~/srve/onengine-backend && grep -c '^model ' prisma/schema.prisma
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t013-prisma-model-coverage-and-tenant-policy.md (under docs/jira/v26.11.9/)
Falsifier: Generated code tenant-scopes a global supplier or leaves a tenant-keyed class unscoped.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-013`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/exists] coverage manifest
  - paths:
    - `ggen-legacy:docs/jira/v26.11.9/manifests/prisma-coverage.json`
- [T0/fresh] manifest matches srve and onengine-backend HEAD
  - path: `ggen-legacy:docs/jira/v26.11.9/manifests/prisma-coverage.json`
  - repos:
    - `srve/onengine-backend`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
