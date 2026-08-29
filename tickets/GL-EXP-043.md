# GL-EXP-043 — Raise 3 `git_head()` siblings out of a total-absence-of-exception-handling crash, worse than every already-fixed/ticketed collapse in this family

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

Three independently-defined `git_head()` functions --
`tools/v26.8.1/document_evidence_index.py:184`,
`tools/v26.8.1/subsystem_evidence_manifest.py:82`, and
`planning/v26.8.1/verify_planning.py:72` -- share the identical shape:

```python
def git_head(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True
    )
    if completed.returncode != 0:
        return "UNKNOWN"
    return completed.stdout.strip()
```

(`verify_planning.py:72-76` is the ternary equivalent of the same shape, with
no functional difference.)

None of the three wraps the `subprocess.run` call in any `try`/`except` at
all. This makes them **strictly worse** than every other sibling already
fixed or already ticketed in this exact undifferentiated-git-head-collapse
anti-pattern family:

- GL-ERRC-019 (Rust, `coverage_projection.rs::exact_head()`, `EXECUTED`)
  fixed a 3-way *cause* collapse (spawn failure / non-zero exit / non-UTF8
  stdout all became `"UNKNOWN"`) but its pre-fix code, like its Python
  cousins below, still ran the equivalent of a real subprocess call and
  degraded on failure rather than crashing uncaught -- Rust's
  `Command::output()` returns a `Result`, so a spawn failure was always at
  least an `Err` value the caller could match on, never an unhandled panic.
- GL-EXP-005 (Rust, `subsystem_verifier.rs::fresh_git_head()`, `NOT_STARTED`)
  and GL-EXP-019 (Rust, `git_provenance::run()`, `NOT_STARTED`) target the
  same class of Rust `Result`-returning collapse -- degrade-on-failure, not
  crash-on-failure.
- GL-EXP-023 (bash, `appliance/bin`'s 5-file `exact_head()`, `NOT_STARTED`)
  targets a Python `subprocess.run(...).returncode`-checking shape closest
  to this ticket's targets, but every one of those 5 already checks
  `returncode` cleanly with no unguarded call that can raise -- the same gap
  this ticket's 3 targets have, but GL-EXP-023 does not claim or fix the
  "raises uncaught" failure mode; it is scoped to the `"UNKNOWN"`-collapse
  question only.
- GL-EXP-011 (Python, `observe_contract.py::git_head()`, `NOT_STARTED`) is
  the closest sibling and the one that makes the severity gap explicit: its
  target function **does** wrap `subprocess.run` in `try: ... except
  Exception: return None`, so a missing `git` binary there still degrades to
  `None` -- ugly (3 distinct causes collapse into 1), but the tool keeps
  running and writes its output contract. This ticket's 3 targets have *no*
  handler at all, so the identical missing-`git`-binary condition does not
  degrade to any sentinel value -- it raises `FileNotFoundError` uncaught
  and crashes the calling script's `main()` with a non-zero exit and a raw
  Python traceback.

This is not a theoretical difference. Verified directly this session with a
real, unmocked repro (no `unittest.mock`/monkeypatch anywhere in this
verification, per this account's Chicago-style testing discipline): each of
the 3 target functions was imported directly from its real module and
called with `os.environ['PATH']` pointed at a real nonexistent directory (so
the real OS `execvp` lookup for `git` genuinely fails), and each one raised
an uncaught `FileNotFoundError` rather than returning `"UNKNOWN"`:

```
$ python3 -c "
import sys, os
sys.path.insert(0, 'tools/v26.8.1')
import document_evidence_index as dei
from pathlib import Path
os.environ['PATH'] = '/nonexistent-bin-dir-xyz'
try:
    print('RETURNED:', dei.git_head(Path('.')))
except FileNotFoundError as e:
    print('CRASHED with FileNotFoundError:', e)
"
CRASHED with FileNotFoundError: [Errno 2] No such file or directory: 'git'
```

Identical crash reproduced for `subsystem_evidence_manifest.git_head` and
`verify_planning.git_head` (see Evidence). All three modules were also
confirmed to have **zero** top-level `except Exception`/`except OSError`/
bare `except:` anywhere else in the file (`grep -n "except" <file>` -- no
matches in any of the 3), so nothing further up the call stack would catch
this either -- the crash genuinely propagates to the Python interpreter and
a non-zero process exit, not merely a documented internal return-value
degradation.

All three are live, not dead code:

- `document_evidence_index.py:296` -- `head = git_head(root)` inside
  `build_index()`, which is called from this file's own `main()`
  (`if __name__ == "__main__":` at line 530). Not currently shelled out to
  by `step_two.py`, `justfile`, or any other file in this repo (verified:
  `grep -rl "document_evidence_index" --include=*.py --include=justfile
  --include=*.sh .` outside `tickets/` and `.claude/worktrees/` returns only
  the file itself) -- live via direct CLI invocation
  (`python3 tools/v26.8.1/document_evidence_index.py`), not via an
  automated pipeline today.
- `subsystem_evidence_manifest.py:429` -- `head = git_head(root)`, and this
  file **is** wired into the automated pipeline:
  `tools/v26.8.1/step_two.py:304` shells out to it as
  `[sys.executable, "tools/v26.8.1/subsystem_evidence_manifest.py"]`.
- `verify_planning.py:140` -- `"source_head": git_head()`, and this file has
  3 real call sites: `tools/v26.8.1/step_two.py:276` (subprocess shell-out),
  `planning/v26.8.1/justfile:4` and `:8` (`python3 verify_planning.py`), and
  `scripts/verify_ggen_v26_8_1_migration.py:354` and `:420` (subprocess
  shell-out with `cwd=destination_root`/`cwd=composed_root`).

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
check there before assuming sole ownership of a path below. `grep -n
"document_evidence_index\.py\|subsystem_evidence_manifest\.py\|
verify_planning\.py" tickets/OVERLAPS.md` returns zero matches this session
-- no overlap entry existed, and none is added by this ticket because no
other ticket's Authored boundary claims the `git_head()` function in any of
these 3 files. 4 other tickets reference one or more of these 3 filenames for
unrelated reasons, confirmed by direct inspection this session:
`GL-EXP-003.md` (the file's `SUBSYSTEMS` dict, unrelated to `git_head`),
`GL-EXP-031.md` and `GL-EXP-033.md` (the file's own `content_sha256`/
generator-provenance identity, unrelated to `git_head`; GL-EXP-031 line 289
explicitly notes `fresh_git_head` as an "unrelated function" it is not
targeting), and `GL-EXP-011.md` (which names these same 3 files' `git_head()`
functions by identical path and line number in its own Evidence section,
lines 207-213, then explicitly marks them "out of scope for this ticket's
Authored boundary" -- this ticket is the pickup of that explicitly-deferred
thread, not a new discovery competing with it.)

```text
tools/v26.8.1/document_evidence_index.py     # git_head() body only
tools/v26.8.1/subsystem_evidence_manifest.py # git_head() body only
planning/v26.8.1/verify_planning.py          # git_head() body only
tickets/GL-EXP-043.md
```

No change to any of the 3 files' call sites (`document_evidence_index.py:296`,
`subsystem_evidence_manifest.py:429`, `verify_planning.py:140`) beyond what
is strictly required to keep assigning `git_head(...)`'s return value into
its existing field/variable. No change to `build_index()`'s other logic,
`SUBSYSTEMS`/`REQUIRED` dicts, `balanced()`, `main()`'s argument parsing, or
any hashing/digest scheme in any of the 3 files. No change to
`tools/v26.8.1/step_two.py`, `planning/v26.8.1/justfile`,
`scripts/verify_ggen_v26_8_1_migration.py`, `tools/v26.8.20/observe_contract.py`
(GL-EXP-011's target), any `appliance/bin/*.py` (GL-EXP-023's target), or any
`.rs` file (GL-ERRC-019/GL-EXP-005/GL-EXP-019's targets).

## Hard laws

1. A real, healthy git repo whose `git rev-parse HEAD` genuinely succeeds
   must return the identical trimmed SHA string as before this ticket, in
   all 3 files -- the happy path's observable value and type (`str`) do not
   change.
2. In all 3 files, a missing `git` binary (`FileNotFoundError`) must no
   longer propagate uncaught -- it must be caught and mapped to a
   distinguishable value (e.g. `"UNKNOWN"` at minimum, or a
   cause-tagged string consistent with GL-EXP-011's eventual convention if
   that ticket lands first) rather than crashing the calling script's
   `main()` with a non-zero exit and a raw traceback.
3. The existing non-zero-exit branch (`git rev-parse` runs but fails,
   e.g. not a git working tree) keeps returning `"UNKNOWN"` (or the same
   cause-tagged convention as law 2) -- this ticket does not regress the
   one failure mode these 3 functions already handle.
4. Each of the 3 functions' call sites (`build_index()`,
   the `subsystem_evidence_manifest.py:429` caller, and
   `verify_planning.py:140`'s `"source_head"` field) keeps receiving a
   `str` return value on every path -- no call site starts receiving an
   exception it did not receive before.
5. `git diff --stat` after this ticket touches only the 3 named `.py`
   files' `git_head()` bodies and this ticket file.

## Falsifiers

- After the fix, running any of the 3 functions with `PATH` pointed at a
  real nonexistent directory (the same repro used in Outcome/Evidence)
  still raises `FileNotFoundError` (or any other exception) uncaught,
  instead of returning a string.
- The happy-path SHA string returned for a real git repo's real `HEAD`
  changes value or trimming behavior as a side effect of this fix, in any
  of the 3 files.
- The existing non-zero-exit-return-`"UNKNOWN"` behavior (git runs, exits
  non-zero) stops working after this fix, in any of the 3 files.
- `python3 tools/v26.8.1/subsystem_evidence_manifest.py` (or the other 2
  files' real invocations named in Outcome) exits non-zero or fails to
  produce its expected output, for a normal run against this real git repo
  with `git` present on `PATH` (regression on ordinary operation).
- `git diff --stat` after this ticket touches any file outside the 3 named
  `.py` files and `tickets/GL-EXP-043.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the 3 collapses and the total absence of exception handling
# before touching anything:
sed -n '184,192p' tools/v26.8.1/document_evidence_index.py
sed -n '82,90p' tools/v26.8.1/subsystem_evidence_manifest.py
sed -n '72,77p' planning/v26.8.1/verify_planning.py
grep -n "except" tools/v26.8.1/document_evidence_index.py \
  tools/v26.8.1/subsystem_evidence_manifest.py \
  planning/v26.8.1/verify_planning.py   # expect: zero matches, all 3 files

# Reconfirm the real crash repro for all 3 (no mocking -- a real broken
# PATH against the real subprocess call):
python3 -c "
import sys, os
sys.path.insert(0, 'tools/v26.8.1')
import document_evidence_index as dei
from pathlib import Path
os.environ['PATH'] = '/nonexistent-bin-dir-xyz'
try:
    print('RETURNED:', dei.git_head(Path('.')))
except FileNotFoundError as e:
    print('CRASHED:', e)
"

# After the fix, confirm each of the 3 functions degrades instead of
# crashing under the identical repro, e.g. a unit test per file exercising
# a real corrupted-PATH `FileNotFoundError` against a real subprocess call
# -- no mocked subprocess return values, per this account's Chicago-style
# testing discipline.

# Confirm ordinary operation still works end to end for the pipeline-wired
# file:
python3 tools/v26.8.1/subsystem_evidence_manifest.py
echo "EXIT:$?"

git diff --stat   # must show only the 3 named .py files and
                   # tickets/GL-EXP-043.md
```

## Evidence this ticket is grounded in (verified this session)

- Direct `Read`/`sed -n` of all 3 functions this session:
  `tools/v26.8.1/document_evidence_index.py:184-190`,
  `tools/v26.8.1/subsystem_evidence_manifest.py:82-88`,
  `planning/v26.8.1/verify_planning.py:72-76` -- byte-for-byte the shape
  quoted in Outcome, confirmed by real line-numbered `grep -n "def
  git_head"` output: `planning/v26.8.1/verify_planning.py:72`,
  `tools/v26.8.1/document_evidence_index.py:184`,
  `tools/v26.8.1/subsystem_evidence_manifest.py:82` -- matching the
  candidate item's cited line numbers exactly.
- `grep -n "git_head(" <each file>` this session: confirms the real call
  sites cited above -- `document_evidence_index.py:296`
  (`head = git_head(root)`), `subsystem_evidence_manifest.py:429`
  (`head = git_head(root)`), `verify_planning.py:140`
  (`"source_head": git_head()`).
- `grep -n "subsystem_evidence_manifest" tools/v26.8.1/step_two.py` this
  session: line 304, `[sys.executable,
  "tools/v26.8.1/subsystem_evidence_manifest.py"]` -- a real pipeline
  shell-out, not a hypothetical caller.
- `grep -n "verify_planning\.py" planning/v26.8.1/justfile
  scripts/verify_ggen_v26_8_1_migration.py tools/v26.8.1/step_two.py` this
  session: 5 real matches across 3 files -- `justfile:4` and `:8`
  (`python3 verify_planning.py`), `verify_ggen_v26_8_1_migration.py:354` and
  `:420` (subprocess shell-outs with distinct `cwd=`), and
  `step_two.py:276` (subprocess shell-out) -- confirming this file has the
  most call sites of the 3 and is genuinely pipeline-wired from multiple
  independent callers.
- `grep -rl "document_evidence_index" --include=*.py --include=justfile
  --include=*.sh .` this session, outside `tickets/` and
  `.claude/worktrees/`: only the file itself -- confirming
  `document_evidence_index.py` is real, runnable
  (`if __name__ == "__main__":` at line 530, `def main` at line 499), and
  reachable via direct CLI invocation, but not currently wired into
  `step_two.py`/`justfile`/CI the way the other 2 are. Stated honestly
  rather than overclaiming "wired into CI" for this one file.
- Live, real, unmocked crash repro this session for all 3 functions
  (imported the real module, called the real function, with a real
  corrupted `PATH` env var so the real OS `execvp` lookup for `git`
  genuinely fails -- no `unittest.mock`/monkeypatch anywhere in this
  verification, per this account's Chicago-style testing discipline):
  - `document_evidence_index.git_head(Path('.'))` -->
    `CRASHED with FileNotFoundError: [Errno 2] No such file or directory:
    'git'`
  - `subsystem_evidence_manifest.git_head(Path('.'))` --> identical crash,
    identical `FileNotFoundError`
  - `verify_planning.git_head()` --> identical crash, identical
    `FileNotFoundError`
  All 3 confirmed via direct `python3 -c` execution this session, not by
  code-reading inference alone -- this is strictly stronger evidence than
  the candidate item this ticket is drafted from, which asserted the crash
  behavior from code inspection ("would crash") rather than a live repro.
- `grep -n "except" tools/v26.8.1/document_evidence_index.py
  tools/v26.8.1/subsystem_evidence_manifest.py
  planning/v26.8.1/verify_planning.py` this session: zero matches in any of
  the 3 files -- confirming nothing further up each call stack would catch
  the `FileNotFoundError` either; the crash genuinely reaches the
  interpreter and produces a non-zero process exit with a raw traceback,
  not merely an internal-function-level degradation.
- `grep -n "document_evidence_index\.py\|subsystem_evidence_manifest\.py\|
  verify_planning\.py" tickets/OVERLAPS.md` this session: zero matches,
  exit code 1 -- no pre-existing overlap entry for these files, and none is
  needed since no other ticket's Authored boundary claims their
  `git_head()` functions (see next 2 findings).
- `grep -l "document_evidence_index\.py\|subsystem_evidence_manifest\.py\|
  verify_planning\.py" tickets/GL-*.md` this session: 4 matches --
  `GL-EXP-003.md`, `GL-EXP-011.md`, `GL-EXP-031.md`, `GL-EXP-033.md`. Direct
  `grep -n` of the matched lines in `GL-EXP-003.md`, `GL-EXP-031.md`, and
  `GL-EXP-033.md` this session confirms all references are to unrelated
  content (`SUBSYSTEMS` dict at `subsystem_evidence_manifest.py:226`, the
  file's own `content_sha256`/generator-identity hash, generator-fixture
  provenance) -- none discusses or targets the `git_head()` function itself;
  `GL-EXP-031.md:289` explicitly calls out `fresh_git_head` (the Rust
  sibling, not these 3) as an "unrelated function," confirming that
  ticket's authors already did this same disambiguation.
- `sed -n '203-213p' tickets/GL-EXP-011.md` this session (re-read, already
  quoted verbatim in that ticket's own Evidence section): lists exactly
  these 3 files/line numbers (plus a 4th, `scripts/
  verify_ggen_v26_8_1_migration.py:131`, not in this ticket's scope) as
  "separate, independently-defined functions in separate files, out of
  scope for this ticket's Authored boundary, and not evidence against this
  finding" -- confirming GL-EXP-011 itself surfaced these 3 and explicitly
  declined to fix them, making this ticket their first real pickup rather
  than a competing discovery.
- `head -8 tickets/GL-EXP-005.md tickets/GL-EXP-011.md tickets/GL-EXP-019.md
  tickets/GL-EXP-023.md tickets/GL-ERRC-019.md` this session: confirms
  Status lines -- `GL-ERRC-019` is `EXECUTED`; `GL-EXP-005`, `GL-EXP-011`,
  `GL-EXP-019`, `GL-EXP-023` are all `admitted, NOT_STARTED` -- exactly 1 of
  the 5 named siblings in this anti-pattern family is actually fixed, 4 are
  ticketed but not yet started, matching the candidate item's count.
- `sed -n '146-196p' tickets/GL-ERRC-019.md` (Execution evidence) this
  session: confirms GL-ERRC-019's real fix target is
  `tools/v26.8.1/src/coverage_projection.rs::exact_head()` (Rust, call
  sites `tools/v26.8.1/src/main.rs:145` and
  `tools/v26.8.1/src/bin/project_coverage.rs:76`), not any Python file --
  correcting an initial assumption that its "already-fixed sibling" might
  be a Python file; the Rust `Command::output()` API returns `Result`
  regardless of fix status, so even GL-ERRC-019's *pre-fix* code could not
  crash uncaught on a missing `git` binary the way these 3 Python functions
  do -- the "strictly worse" framing in Outcome is stated precisely against
  this fact, not loosely.
- `sed -n '15-30p' tickets/GL-EXP-011.md` this session (re-read): confirms
  `observe_contract.py::git_head()`, GL-EXP-011's real target, wraps its
  `subprocess.run(..., check=True)` call in `try: ... except Exception:
  return None` -- i.e. it already catches a missing-`git`-binary
  `FileNotFoundError` and degrades to `None`, unlike this ticket's 3
  targets which have no such wrapper and crash instead. Grounds the
  "strictly worse than GL-EXP-011's target" claim directly against that
  ticket's own quoted source, not by paraphrase.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
total-absence-of-exception-handling finding (strictly worse than every
other sibling in the `git_head()`/`exact_head()` collapse family) for these
3 files' `git_head()` functions, with a real, live, unmocked crash repro
for each; the actual fix (catching `FileNotFoundError` and any other
exception, mapping it to a distinguishable value, and adding Chicago-style
real-subprocess test coverage per function) has not been implemented.
