# T035 — Sunset admission is a separate authorized actuation

Standing: REGISTERED

Wave: W3 · Depends on: T-002, T-028, T-029
Owned paths: ~/ggen-legacy
Research lanes: L10, L19

## Scope

Switch-over is not retirement. cutover never deletes, archives or decommissions ~/xaas or
onengine-backend. Sunset needs its own exact predecessor receipt (ggen.legacy.receipt.v1 with
ALIVE standing for xaas at an exact SHA, covering every endpoint srve calls), Release Admission
admitted:true, independent verification (T-029), and a separate receipted authorization.
Retirement emits a TOMBSTONES file in the gym-ecosystem gitgym-removal-20260903.md shape (old SHA,
claimed vs observed role, evidence commands with captured output that were actually run);
foundry/bootstrap.yaml shows the nonclaims pattern (standing_transferred:false).

## Acceptance

- cutover source contains no delete/archive path for xaas.
- Sunset refuses while release_admitted:false.

## Gates (verbatim, not yet run)

```bash
cd ~/ggen-create && grep -rn 'rmtree\|unlink' src/ggen_create/cutover.py
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t035-sunset-admission-separate-actuation.md (under docs/jira/v26.11.9/)
Falsifier: The switchover command touches or deletes ~/xaas, or sunset admits with
release_admitted:false.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-035`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/absent] cutover code has no delete/archive path
  - paths:
    - `ggen-create:src/ggen_create/cutover.py`
  - pattern: `rmtree|os\.remove|shutil\.move|\.rmdir|shutil\.make_archive`
- [T0/count] only deletion is the single temp-file cleanup in _atomic_write
  - paths:
    - `ggen-create:src/ggen_create/cutover.py`
  - pattern: `unlink`
  - n: `1`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
