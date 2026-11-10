# T036 — Update backend-law rule, memory and srve README after cutover

Standing: REGISTERED

Wave: W3 · Depends on: T-031
Owned paths: ~/.claude + ~/srve
Research lanes: L12, L14

## Scope

xaas-servengine-backend-law (xaas sole backend, :3002 forbidden) contradicts the operator's
2026-11-09 direction; rewrite it for the new backend identity. Update the srve memory file and
srve README boot order (xaas Postgres/mix/phx.server). Only after T-031 passes.

## Acceptance

- Rule, memory and README name the new backend; no rule requires xaas.

## Gates (verbatim, not yet run)

```bash
grep -rn 'xaas' ~/.claude/rules/xaas-servengine-backend-law.md
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t036-doctrine-and-memory-updates.md (under docs/jira/v26.11.9/)
Falsifier: A rule still requires :4000 xaas after cutover.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-036`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/absent] backend-law rule no longer mandates xaas
  - paths:
    - `home:.claude/rules/xaas-servengine-backend-law.md`
  - pattern: `ONLY runtime backend`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
