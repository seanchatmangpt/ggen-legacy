# GL-EXP-021 — Eliminate the fully orphaned `scripts/ci_step_receipt.py` receipt recorder

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`scripts/ci_step_receipt.py` (118 lines) is a `argparse`-driven "durable JSON
receipt" recorder for CI command execution -- three subcommands (`init`,
`run`, `finalize`) meant to be called once per CI step, accumulating a
`checks`/`failures` list into a receipt file, per its own module docstring
("Record exact-head CI command execution into a durable JSON receipt.").
It is invoked by nothing in the real, current CI topology, and has its own
dedicated test file that is likewise never run by CI -- this is the exact
same "orphaned pre-consolidation CI tooling" defect class `GL-EXP-009`
already found and fixed for `scripts/ci_errc.py`, but in a second,
independent script pair `GL-EXP-009`'s own authored boundary explicitly
does not cover.

**Verified this session -- not wired into anything real:**

- `grep -rn "ci_step_receipt" .github/workflows/*.yml justfile
  tools/v26.8.1/justfile` -- zero matches. No workflow step, no `just`
  recipe anywhere in the repo invokes `scripts/ci_step_receipt.py`.
- `grep -rln "ci_step_receipt" .` (repo-wide, excluding `.git/` and
  worktree checkouts under `.claude/worktrees/`) finds exactly three
  files: `scripts/ci_step_receipt.py` itself, its own dedicated test
  (`scripts/tests/test_ci_step_receipt.py`), and one incidental hit inside
  `tickets/GL-AUTO-001.md` -- confirmed by direct inspection to be one bare
  filename among 115 comma-separated paths inside a single-line
  `REFUSED:FORBIDDEN_DIFF:...` dump from an unrelated acceptance-command
  run, not a substantive reference (the same pattern `GL-EXP-006`/
  `GL-EXP-009` already documented for analogous incidental hits in the same
  ticket).
- `.github/workflows/ci.yml`'s own "Emit verification receipt" step
  (lines 57-71, read directly this session) writes `evidence/ci/receipt.json`
  via an inline bash heredoc, independently of `ci_step_receipt.py` --
  confirming the real CI receipt mechanism in production today does not
  route through this script at all; it duplicates the script's stated
  purpose with a different, self-contained implementation.
- `python3 -m pytest scripts/tests/test_ci_step_receipt.py -q` (run
  directly this session, real subprocess execution against the real
  script via `subprocess.run([sys.executable, str(SCRIPT), *args], ...)`,
  no mocking -- confirmed via `grep -c "Mock\|mock\.\|monkeypatch\|patch("
  scripts/tests/test_ci_step_receipt.py` returning `0`) passes: `3 passed
  in 0.48s`. The script and its test are both real and internally
  consistent -- this is dead-weight orphaning, not a broken/unfinished
  tool.

**Same historical origin as `GL-EXP-009`'s finding, confirmed this
session:** `git log --oneline --all -- scripts/ci_step_receipt.py` shows it
was introduced by `1b33a4e add reusable CI step receipts` (2026-08-05,
branching directly off `9118fe4 refactor CI to 80/20 ERRC (#20)` --
`GL-EXP-009`'s own `ci_errc.py` origin commit, same day, same
pre-consolidation CI generation) and last touched by `70ff5fc make CI
receipt-complete and exact-head ALIVE (#21)` (2026-08-07) -- the same
pre-consolidation CI generation `GL-EXP-009`'s `ci_errc.py` finding traces
to (`git log --oneline | grep 60d3826` -> `60d3826 ci: rebuild CI around
contract and real LSP execution`, 2026-08-08, the commit that replaced the
whole per-lane topology with the current monolithic `ci.yml`, which built
its own inline receipt step rather than continuing to shell out to this
script).

**No existing ticket already covers this file pair.** Verified this
session: `grep -l "ci_step_receipt" tickets/GL-*.md` returns only
`tickets/GL-AUTO-001.md` (the incidental hit above). `tickets/GL-EXP-009.md`
(read in full this session) is scoped exclusively to
`scripts/ci_errc.py`/`scripts/tests/test_ci_errc.py` -- its own Authored
boundary and Hard Law 3 (naming the nine `verify_*.py`/`autonomic_*.py`
scripts it must not touch) never mention `ci_step_receipt.py`, and its own
Falsifiers/Acceptance sections re-verify only `ci_errc.py`'s orphan status.
`grep -n "ci_step_receipt" tickets/OVERLAPS.md` returns zero matches -- no
existing overlap-registry entry for this path either.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
check there before assuming sole ownership of a path below. Confirmed this
session via `grep -n "ci_step_receipt" tickets/OVERLAPS.md`: no existing
entry, and `grep -l "ci_step_receipt" tickets/GL-*.md` confirms only the
incidental `GL-AUTO-001.md` hit -- this ticket has sole, undisputed
ownership of both paths below.)

```text
scripts/ci_step_receipt.py              # deleted in full
scripts/tests/test_ci_step_receipt.py   # deleted in full
tickets/GL-EXP-021.md
```

No change to `.github/workflows/ci.yml`'s own inline "Emit verification
receipt" step (it never called `ci_step_receipt.py` and continues writing
`evidence/ci/receipt.json` exactly as it does today), `justfile`, or any of
the scripts `ci_step_receipt.py` never called (it has no callees of its
own beyond stdlib `json`/`subprocess`/`argparse` -- confirmed by direct
read: no `import` of any other repo module). No change to
`scripts/ci_errc.py`/`scripts/tests/test_ci_errc.py` (`GL-EXP-009`'s
separate, already-admitted target).

## Hard laws

1. Delete `scripts/ci_step_receipt.py` and
   `scripts/tests/test_ci_step_receipt.py` in full -- this is an
   elimination, not a rewrite or a "wire it in instead" fix. The script's
   stated purpose (a durable per-step CI receipt) is already served by
   `.github/workflows/ci.yml`'s own independent inline heredoc step; there
   is no live gap for this script to fill.
2. Before deleting, re-run `grep -rn "ci_step_receipt"
   .github/workflows/*.yml justfile tools/v26.8.1/justfile scripts/
   tools/` and confirm the only hits are inside
   `scripts/ci_step_receipt.py`/`scripts/tests/test_ci_step_receipt.py`
   themselves -- if any real caller has appeared since this ticket was
   drafted, halt and re-scope instead of deleting a now-live script.
3. `.github/workflows/ci.yml`'s "Emit verification receipt" step (its
   `run:` block, its `evidence/ci/receipt.json` schema, and its
   `upload-artifact` step) is not touched -- it already works
   independently of the script this ticket removes.
4. This ticket does not add a `tickets/OVERLAPS.md` entry -- both paths
   had zero prior registry entries and zero other active claimants
   (Authored boundary section above), so there is nothing to reconcile.

## Falsifiers

- `test -f scripts/ci_step_receipt.py` or
  `test -f scripts/tests/test_ci_step_receipt.py` still succeeds after
  this ticket executes (deletion did not happen).
- `grep -rn "ci_step_receipt" .github/workflows/*.yml justfile
  tools/v26.8.1/justfile scripts/ tools/` finds a real caller that existed
  before this ticket ran but was not accounted for (Hard Law 2 skipped).
- `git diff --stat` after this ticket touches any file outside
  `scripts/ci_step_receipt.py`, `scripts/tests/test_ci_step_receipt.py`,
  and `tickets/GL-EXP-021.md`.
- `.github/workflows/ci.yml` fails after this deletion (it must not -- it
  never invoked `ci_step_receipt.py`; a failure here would mean this
  ticket's own "nothing depends on it" claim was wrong and must be
  re-investigated, not worked around).
- `just --list` fails to parse `justfile` after this deletion (it never
  referenced `ci_step_receipt.py`, so this should be impossible).

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the deletion lands, not yet-observed
outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the orphan status before touching anything:
grep -rn "ci_step_receipt" .github/workflows/*.yml justfile tools/v26.8.1/justfile
grep -rln "ci_step_receipt" . --exclude-dir=.git --exclude-dir=worktrees --exclude-dir=.worktrees

# After deletion, confirm both files are gone and nothing else changed:
test -f scripts/ci_step_receipt.py && echo "UNEXPECTED: still exists" || echo "confirmed deleted"
test -f scripts/tests/test_ci_step_receipt.py && echo "UNEXPECTED: still exists" || echo "confirmed deleted"
git diff --stat   # must show only the two deletions + tickets/GL-EXP-021.md

# Confirm nothing that depended on ci_step_receipt.py broke:
just --list
grep -n "Emit verification receipt" .github/workflows/ci.yml

# Full local CI-equivalent proof the repo still builds/tests clean:
cargo fmt --all -- --check
cargo check --all-targets --locked
cargo clippy --all-targets --locked -- -D warnings
cargo test --all-targets --locked
```

## Evidence this ticket is grounded in (verified this session)

- `wc -l scripts/ci_step_receipt.py scripts/tests/test_ci_step_receipt.py`
  -- real output: `118 scripts/ci_step_receipt.py`,
  `83 scripts/tests/test_ci_step_receipt.py`, `201 total`.
- `grep -rn "ci_step_receipt" .github/workflows/*.yml justfile
  tools/v26.8.1/justfile` -- real output: zero matches (exit 1, no
  output).
- `grep -rln "ci_step_receipt" .` (repo-wide, excluding `.git/` and
  `.claude/worktrees/`) -- real output: `scripts/ci_step_receipt.py`,
  `scripts/tests/test_ci_step_receipt.py`, `tickets/GL-AUTO-001.md`.
  `grep -n "ci_step_receipt" tickets/GL-AUTO-001.md` shows the one hit is
  inside the single-line `REFUSED:FORBIDDEN_DIFF:...` path dump.
- Direct `Read` of `.github/workflows/ci.yml:55-71` this session --
  confirms the real, independent "Emit verification receipt" step: a bash
  heredoc writing `evidence/ci/receipt.json` with fields `repository`,
  `subject_sha`, `workflow`, `run_id`, `standing`, `workflow_count`,
  `boundaries`, then `actions/upload-artifact@v4` -- no reference to
  `ci_step_receipt.py` anywhere in this step or the rest of the file.
- Direct `Read` of `scripts/ci_step_receipt.py` in full this session --
  confirms `init`/`run`/`finalize` subcommands (`argparse`, `sub.add_parser`
  at each), `load()`/`store()` JSON read/write helpers, and `TAIL_LIMIT`
  stdout-truncation constant; no import of any other repo module beyond
  Python stdlib.
- `python3 -m pytest scripts/tests/test_ci_step_receipt.py -q` -- real
  output this session: `3 passed in 0.48s`. `grep -c
  "Mock\|mock\.\|monkeypatch\|patch(" scripts/tests/test_ci_step_receipt.py`
  -- `0`, confirming the test exercises the real script via a real
  `subprocess.run` call (`ROOT = Path(__file__).resolve().parents[2]`,
  `SCRIPT = ROOT / "scripts" / "ci_step_receipt.py"`), not a mock.
- `git log --oneline --all -- scripts/ci_step_receipt.py` -- real output:
  `70ff5fc make CI receipt-complete and exact-head ALIVE (#21)`,
  `1b33a4e add reusable CI step receipts` (the actual introducing commit;
  it branches directly off `9118fe4 refactor CI to 80/20 ERRC (#20)` --
  confirmed via `git log --oneline --graph --all -- scripts/ci_step_receipt.py
  scripts/ci_errc.py` and `git show --stat --format="" 9118fe4`, which shows
  `9118fe4` itself introduced `scripts/ci_errc.py`, not this file; both
  commits land the same day, 2026-08-05). `git log --oneline | grep
  60d3826` -- `60d3826 ci: rebuild CI around contract and real LSP
  execution` (2026-08-08), the same commit `tickets/GL-EXP-006.md`/
  `GL-EXP-009.md` already identify as the one that retired the
  pre-consolidation, per-lane CI topology this script's sibling
  `ci_errc.py` was built for.
- `grep -l "ci_step_receipt" tickets/GL-*.md` -- real output: only
  `tickets/GL-AUTO-001.md` (the incidental hit above). Read
  `tickets/GL-EXP-009.md` in full this session -- confirms its own
  Authored boundary and Hard Law 3 name only `scripts/ci_errc.py`,
  `scripts/tests/test_ci_errc.py`, and the nine `verify_*.py`/
  `autonomic_*.py` scripts `ci_errc.py` shelled out to; `ci_step_receipt.py`
  is not named anywhere in that ticket.
- `grep -n "ci_step_receipt" tickets/OVERLAPS.md` -- real output: zero
  matches, no existing overlap-registry entry for either path this ticket
  claims.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
elimination case (every command above was re-run fresh this session); the
actual deletion has not been made.
