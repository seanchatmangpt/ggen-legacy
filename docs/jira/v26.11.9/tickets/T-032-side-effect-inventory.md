# T032 — Side-effect inventory with cutover behavior

Standing: REGISTERED

Wave: W3 · Depends on: T-010
Owned paths: ~/srve/docs
Research lanes: L20

## Scope

Name an owner and cutover behavior (pause, drain, dual-send) for S3 presign (B13 unported),
email/notifications, Oban poll jobs, Reactor sagas (RFC-0042), Sentry, DynamoDB sessions, in-
flight work orders. DynamoDB/Sentry/tenant_id-drop risks were not confirmed in any read doc: mark
UNVERIFIED until grepped.

## Acceptance

- Every side effect has an owner and behavior; unverified items marked UNVERIFIED.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && grep -rln 'dynamodb\|sentry' docs servengine-frontend/src | head
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t032-side-effect-inventory.md (under docs/jira/v26.11.9/)
Falsifier: Duplicate emails sent or in-flight jobs lost on a rehearsal.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-032`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/exists] side-effect table
  - paths:
    - `ggen-legacy:docs/jira/v26.11.9/manifests/side-effects.md`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
