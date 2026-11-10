# T015 — Backend pack: generate resources from the srve ontology

Standing: REGISTERED

Wave: W1 · Depends on: T-005, T-006, T-008
Owned paths: ~/srve/packs/srve-backend-pack (new)
Research lanes: L09, L01, L08

## Scope

Pack modeled on ggen-docs-reconstitution-pack and reusing xaas-ash-core-pack + canonical-ash-
projection-generator from ggen-marketplace. Existing packs emit shell commands and semantic-map
TTL, not resource source, so add templates that render attributes, relationships, identities and
code interfaces. Decision D1 (CHARTER): generated Ash on the BEAM is the only existing pack path;
a TypeScript target needs new packs.

## Acceptance

- `ggen sync run` emits one resource per srve entity; command count equals entity count.
- Second sync is byte-stable.
- Output compiles with no hand edit.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ggen sync run --dry-run && ggen sync run && ggen sync run \
  && git status --short packs generated
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t015-pack-resources-from-ontology.md (under docs/jira/v26.11.9/)
Falsifier: Emitted source needs a hand edit to compile, or the second sync differs.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-015`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T1

Clauses:
- [T0/exists] pack manifest and resource template
  - paths:
    - `srve:packs/srve-backend-pack/pack.toml`
    - `srve:packs/srve-backend-pack/templates/resource.ex.tera`
- [T1/unverified] ggen sync run --dry-run twice, byte-stable
  - reason: `needs ggen over the pack in scratch`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
