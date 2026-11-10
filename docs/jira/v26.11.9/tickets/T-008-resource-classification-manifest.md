# T008 — Manifest: every Ash resource and action tagged generated vs residue

Standing: REGISTERED

Wave: W0 · Depends on: T-006
Owned paths: ~/srve/ontology + docs
Research lanes: L01

## Scope

Produce a derived manifest of every AshPostgres resource (67 at xaas d7e38a37; the working tree
carries more uncommitted ones) and every action, tagged generated or custom-handler, with the grep
derivation commands recorded in the file head (CONTRACT.md pattern). Tag totals must equal the
totals recorded in the manifest derivation (74 create, 97 update, 87 read, 19 destroy, 12 generic
at xaas d7e38a37).

## Acceptance

- Every resource and action has exactly one tag.
- Tag totals equal derivation-command totals.

## Gates (verbatim, not yet run)

```bash
cd ~/xaas && grep -rl 'data_layer: AshPostgres' lib/xaas/serv_engine | wc -l
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t008-resource-classification-manifest.md (under docs/jira/v26.11.9/)
Falsifier: A resource or action found in xaas with no tag.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-008`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/exists] classification manifest
  - paths:
    - `ggen-legacy:docs/jira/v26.11.9/manifests/resource-classification.json`
- [T0/fresh] manifest matches xaas HEAD
  - path: `ggen-legacy:docs/jira/v26.11.9/manifests/resource-classification.json`
  - repos:
    - `xaas`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
