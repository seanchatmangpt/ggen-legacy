# T033 — Downstream parity: receipts, OCEL ndjson, pins

Standing: REGISTERED

Wave: W3 · Depends on: T-028
Owned paths: ~/srve + ~/zoela + ~/chatman-ecosystem
Research lanes: L15

## Scope

No other repo calls :4000 at runtime. Contract surfaces: ggen_igniter receipt_from_xaas must parse
candidate receipts; gymact castle_feed (parse_xaas_ndjson) must pass test_castle_feed.py on
candidate OCEL ndjson; zoela target-architecture.md pin xaas/main@42fd0ce and chatman-ecosystem
release.ttl must be refreshed post-cutover; cmms census packs xaas-ash-core / xaas-castle-bridge
inventoried; confirm xaas path deps on ggen_igniter/ash_a2a unchanged.

## Acceptance

- Candidate receipts parse; gymact test passes; stale pins named in the plan.

## Gates (verbatim, not yet run)

```bash
cd ~/gymact && python3 -m pytest tests/test_castle_feed.py
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t033-downstream-parity.md (under docs/jira/v26.11.9/)
Falsifier: A receipt or ndjson line from the candidate fails its downstream parser.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-033`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T1

Clauses:
- [T0/exists] gymact castle feed test present
  - paths:
    - `gymact:tests/test_castle_feed.py`
- [T1/unverified] candidate-shaped fixtures through igniter and gymact parsers
  - reason: `needs fixtures`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
