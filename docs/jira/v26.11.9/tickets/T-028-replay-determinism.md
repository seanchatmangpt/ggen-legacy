# T028 — Deterministic replay: byte-stable second sync

Standing: REGISTERED

Wave: W2 · Depends on: T-015, T-016, T-017
Owned paths: ~/ggen-legacy + ~/srve
Research lanes: L10

## Scope

Release Admission requires clean deterministic replay. Two full generate runs at the same subject
produce identical output digests and identical receipt-chain head.

## Acceptance

- Two replays: identical digest set and chain head.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ggen sync run && sha256sum -r generated/* > /tmp/a && ggen sync run \
  && sha256sum -r generated/* > /tmp/b && diff /tmp/a /tmp/b
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t028-replay-determinism.md (under docs/jira/v26.11.9/)
Falsifier: Digests differ or replay is not clean.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-028`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T1

Clauses:
- [T1/unverified] two scratch generate runs; digest sets and chain head equal
  - reason: `needs ggen sync twice in scratch`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
