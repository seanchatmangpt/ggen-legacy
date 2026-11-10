# T002 — Cutover receipt chain and sunset-admission schema

Standing: REGISTERED

Wave: W0 · Depends on: T-001
Owned paths: ~/ggen-legacy schemas/ + ~/ggen-create
Research lanes: L10, L11, L19 (receipt lane; re-read at fill)

## Scope

Extend schemas/sunset-admission.schema.json (today only schema/admitted/state) with predecessor
SHA, release-admission ref, replay digest and authorization-receipt ref. Two receipt shapes exist
and are not interchangeable: the cutover receipt follows ~/.claude/dfcm/receipt.schema.json v2
(identity.subject_sha, subject_before/after sha256, replay.commands with output_sha256, standing
with broken_term on REFUSED/BLOCKED/UNSUPPORTED, plus a provider_ext block holding the
lock_content_root root, the ggen portable_receipt digest and the old backend's last SHA); the xaas
predecessor receipt used for sunset follows ggen.legacy.receipt.v1. Cutover receipts chain through
ReceiptStore; failures write BLOCKED receipts. Byte-replay: regenerate from clean state, recompute
lock_content_root (ggen-ecosystem scripts/lock_content_root.py --check) and pack_digest, require
equality, else REFUSED(code). Rollback emits a mirror receipt linked via
predecessor_work_order_ids. See T-035 for the retirement gate.

## Acceptance

- A sunset payload missing any of the four new fields fails schema validation.
- Flipping one byte in a generated file makes the replay verifier report REFUSED, not ALIVE.
- `ggen-create receipt chain` passes after plan, power, verify, rollback; a failed phase leaves a
  BLOCKED receipt.
- Receipts carry the five fields identity/authority/consequence/replay/standing.

## Gates (verbatim, not yet run)

```bash
cd ~/ggen-legacy && python3 -c "import json,jsonschema"  # schema loads
cd ~/ggen-create && ggen-create --json receipt chain
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t002-cutover-receipt-and-sunset-schema.md (under docs/jira/v26.11.9/)
Falsifier: A payload without a replay digest validates, or a failed phase writes no receipt.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-002`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/json_required] sunset schema requires the four new fields
  - path: `ggen-legacy:schemas/sunset-admission.schema.json`
  - fields:
    - `predecessor_sha`
    - `release_admission_ref`
    - `replay_digest`
    - `authorization_receipt_ref`
- [T0/exists] dfcm receipt schema present
  - paths:
    - `home:.claude/dfcm/receipt.schema.json`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
