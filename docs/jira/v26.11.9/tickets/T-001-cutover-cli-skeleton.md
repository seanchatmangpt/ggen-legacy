# T001 — cutover CLI skeleton: plan, power, verify, rollback

Standing: REGISTERED

Wave: W0 · Depends on: none
Owned paths: ~/ggen-create
Research lanes: L11, L18

## Scope

Add four skills to ggen-create SKILLS: cutover.plan (CONSTRUCT), cutover.power (DO_INTENT,
confirm, no session), cutover.verify (SELECT), cutover.rollback (DO_INTENT, confirm). Dispatch
branches lazy-import a new cutover.py. Add argparse `cutover` subcommands and an elif in run().
Base is ggen-create's Broker (digest-sealed intent, hash-chained ReceiptStore), not a new Rust
CLI; osx-clnr is the structural reference only. `just cutover` in srve is a one-line alias.

## Acceptance

- `ggen-create skills list` shows the four cutover.* skills with the stated authority and confirm
  flags.
- `cutover power` without --confirm exits with ACTUATION_CONFIRMATION_REQUIRED_REFUSED.
- plan run twice on the same subject yields byte-identical JSON and touches no file outside
  output_root.

## Gates (verbatim, not yet run)

```bash
cd ~/ggen-create && python3 -m unittest tests/test_cutover.py
cd ~/ggen-create && ggen-create --json skills list | grep -c cutover
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t001-cutover-cli-skeleton.md (under docs/jira/v26.11.9/)
Falsifier: power runs with the confirm gate removed, or plan output differs between two runs.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-001`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/skills] four cutover skills registered with stated authority/confirm
- [T0/exists] cutover.py present
  - paths:
    - `ggen-create:src/ggen_create/cutover.py`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
