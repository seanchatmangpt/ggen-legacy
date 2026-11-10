# T006 — Align one: and sv:; verify against introspection

Standing: REGISTERED

Wave: W0 · Depends on: T-005
Owned paths: ~/srve/ontology
Research lanes: L08, L05, L01

## Scope

Add the missing one:-to-sv: alignment (class, property, enum). Verify servengine-current.ttl
(regex-derived, UNVERIFIED) against Ash introspection of the pinned xaas SHA f0154ac1 so counts
(recorded as 311 vs 459 actions) agree; remove UNVERIFIED only on a receipt.

## Acceptance

- SPARQL reports zero unmapped one:CanonicalProperty and zero unmapped statuses.
- Introspection counts equal ontology counts for resources, actions, policies, enums.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ggen sync run --dry-run
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t006-ontology-align-one-sv-and-verify-current.md (under docs/jira/v26.11.9/)
Falsifier: A canonical property with no sv:Attribute counterpart, or any count mismatch against
introspection.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-006`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T2

Clauses:
- [T0/exists] alignment artifact
  - paths:
    - `srve:ontology/one-sv-alignment.ttl`
- [T2/unverified] counts vs Ash introspection of pinned xaas SHA
  - reason: `needs mix introspection of xaas`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
