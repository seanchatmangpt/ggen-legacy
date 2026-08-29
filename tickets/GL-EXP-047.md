# GL-EXP-047 — Raise `execute()`'s total absence of exception handling in `scripts/verify_ggen_v26_8_1_migration.py`, the crash surface behind all 16 subprocess call sites, explicitly outside GL-EXP-043's scope

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`scripts/verify_ggen_v26_8_1_migration.py`'s `execute()` function (`Read`,
this session, lines 88-118) wraps a bare
`subprocess.run(argv, cwd=cwd, env=command_env, text=True,
capture_output=True, check=False, timeout=timeout)` (line 97-105) with
**zero** `try`/`except` anywhere in the function body. Confirmed directly
this session:

```python
def execute(argv: list[str], *, cwd: Path, timeout: int = 900) -> tuple[CommandReceipt, str, str]:
    command_env = os.environ.copy()
    ...
    result = subprocess.run(
        argv, cwd=cwd, env=command_env, text=True,
        capture_output=True, check=False, timeout=timeout,
    )
    receipt_stdout, receipt_stderr = canonical_receipt_output(...)
    receipt = CommandReceipt(...)
    return receipt, result.stdout, result.stderr
```

`require_success()` (lines 121-128) is a thin wrapper over `execute()` that
only inspects `receipt.exit_status` after the call returns -- it adds no
exception handling of its own.

**16 real call sites** into `execute()`/`require_success()`, confirmed this
session by `grep -n "require_success(\|execute(" scripts/verify_ggen_v26_8_1_migration.py`
excluding the two `def` lines: lines 122, 132, 138, 178, 296, 329, 353, 359,
365, 379, 391, 402, 419, 425, 431, 608. These span `git rev-parse HEAD`
(`git_head()`, line 132), `git merge-base --is-ancestor` (`is_ancestor()`,
line 138), `git diff --quiet` (the local-corpus checkpoint drift check,
line 608), `git clone` (compose step, line 178/329), `cargo fmt`/`fetch`/
`clean`/`test` against both the destination root and the composed root
(lines 353-431), and `python3 planning/v26.8.1/verify_planning.py` /
`python3 tools/v26.8.1/validate_shacl.py` (behavioral checks, line
353/359/419/425) -- not a single narrow function, the entire subprocess
surface of this verifier.

**`main()`'s own top-level exception handler does not cover this.**
`Read`, this session, line 731:

```python
    except (VerificationRefusal, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
```

`grep -n "except" scripts/verify_ggen_v26_8_1_migration.py` this session:
exactly 4 matches in the whole 744-line file (lines 165, 506, 635, 731) --
none is `FileNotFoundError`, `OSError`, `subprocess.TimeoutExpired`, or a
bare `except`. A missing `git`/`cargo`/`python3` binary, or any of the 16
call sites' commands hanging past its `timeout`, raises an exception type
`main()`'s `try`/`except` (lines 586-740) does not match -- the exception
propagates all the way out of `main()` uncaught, so line 738's
`write_json(report_path, refusal)` never executes. Every other failure mode
this script handles (`VerificationRefusal`, malformed JSON/TOML) produces a
`BUILD_BROKEN` `report.json` with a `refusal` field; this failure mode
produces neither -- no report file at all, just a raw Python traceback and
whatever exit code the interpreter assigns on an uncaught exception,
bypassing the script's own carefully-designed refusal contract entirely.

**Both failure modes reproduced live this session, no mocking** (per this
account's Chicago-style testing discipline -- real module, real corrupted
`PATH`/real slow subprocess, no `unittest.mock`/monkeypatch anywhere):

```console
$ python3 -c "
import sys, os
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location(
    'verify_ggen_v26_8_1_migration', 'scripts/verify_ggen_v26_8_1_migration.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['verify_ggen_v26_8_1_migration'] = mod
spec.loader.exec_module(mod)
os.environ['PATH'] = '/nonexistent-bin-dir-xyz'
try:
    print('RETURNED:', mod.git_head(Path('.')))
except FileNotFoundError as e:
    print('CRASHED with FileNotFoundError:', e)
"
CRASHED with FileNotFoundError: [Errno 2] No such file or directory: 'git'

$ python3 -c "
import sys, os, subprocess
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location(
    'verify_ggen_v26_8_1_migration', 'scripts/verify_ggen_v26_8_1_migration.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['verify_ggen_v26_8_1_migration'] = mod
spec.loader.exec_module(mod)
try:
    mod.execute(['sleep', '5'], cwd=Path('.'), timeout=1)
except subprocess.TimeoutExpired as e:
    print('CRASHED with TimeoutExpired:', e)
"
CRASHED with TimeoutExpired: Command '['sleep', '5']' timed out after 1 seconds
```

Both crashes are the real, direct behavior of the real functions in the
real file at this session's `HEAD` -- not inferred from reading the code,
independently reproduced.

**This finding is explicitly broader than, and outside the scope of,
`GL-EXP-043` (`admitted, NOT_STARTED`).** `sed -n '203-213p'
tickets/GL-EXP-011.md` this session (GL-EXP-043's own cited source) and
direct `Read` of `tickets/GL-EXP-043.md`'s "Authored boundary" section this
session both confirm `GL-EXP-043` names
`scripts/verify_ggen_v26_8_1_migration.py:131` (this file's own
`git_head()`, which just calls `require_success(["git", "rev-parse",
"HEAD"], cwd=root)`) as a "4th sibling" in an undifferentiated-`git_head()`
anti-pattern family, then explicitly marks it "not in this ticket's scope"
and restricts its own Authored boundary to 3 *other* files
(`tools/v26.8.1/document_evidence_index.py`,
`tools/v26.8.1/subsystem_evidence_manifest.py`,
`planning/v26.8.1/verify_planning.py`) -- `GL-EXP-043`'s own Authored
boundary section states verbatim it makes "No change to ...
`scripts/verify_ggen_v26_8_1_migration.py`." Even if `GL-EXP-043` executes
exactly as scoped, this file's crash surface is untouched: `GL-EXP-043`
would fix 3 other files' single-purpose `git_head()` functions, while this
file's `execute()` -- which backs `git_head()`, `is_ancestor()`, and 14
other call sites across `git` and `cargo` -- would remain fully exposed.
This ticket is the first in the corpus to target `execute()` itself in this
file.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
checked there and against every ticket's Authored boundary before writing
this section. `grep -n "verify_ggen_v26_8_1_migration"
tickets/OVERLAPS.md` this session: exactly one match, line 152, in the
`justfile` section -- `GL-EXP-008` ("wires
`scripts/verify_ggen_v26_8_1_migration.py` in as a new, optional recipe")
-- that entry is about a `justfile` recipe wrapping this script's
invocation, not about anything inside the script's own body, so it is not
an overlap with this ticket's target (`execute()`'s exception handling).
No new `OVERLAPS.md` row is added by this ticket because no other ticket's
Authored boundary claims `execute()`, `require_success()`, or any of their
16 call sites' bodies in this file. Confirmed directly this session:
`grep -l "verify_ggen_v26_8_1_migration" tickets/GL-*.md` returns 10
matches (`GL-ERRC-011`, `GL-EXP-008`, `GL-EXP-009`, `GL-EXP-010`,
`GL-EXP-011`, `GL-EXP-012`, `GL-EXP-028`, `GL-EXP-034`, `GL-EXP-043`,
`GL-EXP-044`); per-file `grep -n -B1 -A2` of each hit, read in context this
session: `GL-ERRC-011`/`GL-EXP-009`/`GL-EXP-028` cite it only as one of a
list of scripts confirmed to lack `EXPECTED_*` constants; `GL-EXP-008`,
`GL-EXP-010`, `GL-EXP-012` each state verbatim "No change to
`scripts/verify_ggen_v26_8_1_migration.py`" as their own Authored-boundary
exclusion (their scope is `justfile` recipe wiring or the migration
manifest's `source_head` pin, never this script's logic); `GL-EXP-034`
cites the script only as an analogy for a staleness pattern in a different
file; `GL-EXP-043` explicitly excludes this file, as detailed in Outcome
above; `GL-EXP-044` cites it only as one of 6 prior `justfile`-wiring
precedents. None of the 10 touches `execute()`, `require_success()`, or any
exception-handling behavior in this file.)

```text
scripts/verify_ggen_v26_8_1_migration.py   # execute()'s body only
tickets/GL-EXP-047.md
```

No change to any of the 16 call sites' arguments (`argv`, `cwd`, `timeout`
values), `require_success()`'s existing non-zero-exit-status handling
(already raises `VerificationRefusal` cleanly and is unaffected by this
ticket), `canonical_receipt_output()`, `CommandReceipt`'s fields, `main()`'s
control flow beyond what is strictly required to let the existing
`except (VerificationRefusal, json.JSONDecodeError,
tomllib.TOMLDecodeError)` clause (or an equivalent, widened clause) catch
the newly-wrapped exceptions, or the `BUILD_BROKEN` report schema written
at line 738. No change to `justfile`, `GL-EXP-008`/`GL-EXP-010`/
`GL-EXP-012`'s own recipe-wiring or manifest-staleness scopes, or
`GL-EXP-043`'s 3 target files (`document_evidence_index.py`,
`subsystem_evidence_manifest.py`, `verify_planning.py`).

## Hard laws

1. `execute()`'s signature (`argv`, `cwd`, `timeout`) and return type
   (`tuple[CommandReceipt, str, str]`) do not change for any call that
   completes normally -- the happy-path return value and type are
   unaffected by this ticket.
2. A missing binary (`FileNotFoundError`/`OSError` raised by
   `subprocess.run` inside `execute()`) must no longer propagate uncaught
   past `main()`'s `try`/`except` -- it must be caught (inside `execute()`,
   `require_success()`, or `main()`'s own handler, whichever keeps the
   smallest diff) and mapped into a `VerificationRefusal` (or an exception
   type already covered by `main()`'s existing `except` clause), so the
   existing `BUILD_BROKEN` report -- `write_json(report_path, refusal)` at
   line 738 -- fires for this failure mode exactly as it already does for
   every `VerificationRefusal`-raised failure.
3. A hang past `timeout` (`subprocess.TimeoutExpired` raised by
   `subprocess.run` inside `execute()`) must likewise be caught and mapped
   into a `VerificationRefusal` (or an already-covered type), not propagate
   uncaught.
4. All 16 existing call sites (line numbers in Outcome above) continue to
   receive either the same `CommandReceipt`/`str`/`str`-shaped return on
   success, or a `VerificationRefusal` they can already handle (several
   call sites are already inside `main()`'s `try` block and several already
   call `require_success()`, which already raises `VerificationRefusal` on
   non-zero exit) -- no call site starts receiving a raw
   `FileNotFoundError`/`subprocess.TimeoutExpired` it did not receive
   (i.e. did not previously crash on) before this ticket.
5. The existing `BUILD_BROKEN` report's shape (`schema`, `standing`,
   `refusal`, `failed_checks` fields, written at line 738) stays
   byte-identical in structure for the failure modes it already handles
   (`VerificationRefusal`-raised paths, malformed JSON/TOML) -- this ticket
   only extends which raw OS/subprocess exceptions get wrapped into that
   same existing contract; it does not redesign the report schema itself.
6. No change to `canonical_receipt_output()`, `CommandReceipt`'s field set,
   or `require_success()`'s existing non-zero-exit-status
   `VerificationRefusal` raise (lines 123-127) -- that path is already
   correct and untouched by this ticket.
7. `git diff --stat` after this ticket touches only
   `scripts/verify_ggen_v26_8_1_migration.py` and
   `tickets/GL-EXP-047.md`.

## Falsifiers

- After the fix, either of this ticket's two live repros (broken `PATH`
  against `git_head(Path('.'))`; `execute(['sleep', '5'], cwd=Path('.'),
  timeout=1)`) still raises `FileNotFoundError`/`subprocess.TimeoutExpired`
  (or any other exception) uncaught out of `main()`, instead of producing a
  `BUILD_BROKEN` `report.json`.
- The happy-path return value or type of `execute()`/`require_success()`
  changes for any of the 16 call sites under normal operation (a real,
  successful `git`/`cargo`/`python3` invocation).
- The existing `VerificationRefusal`-driven `BUILD_BROKEN` report's field
  set or `schema` value changes as a side effect of this fix.
- `python3 scripts/verify_ggen_v26_8_1_migration.py --help` stops working,
  or a real run against a real sibling checkout (`--source-root ~/ggen
  --destination-root .`) starts failing differently than its pre-fix
  `SOURCE_HEAD_MISMATCH_REFUSED` behavior for reasons unrelated to this
  ticket's exception-handling change.
- `git diff --stat` after this ticket touches any file other than
  `scripts/verify_ggen_v26_8_1_migration.py` and `tickets/GL-EXP-047.md`.
- Any of `GL-EXP-008`/`GL-EXP-010`/`GL-EXP-012`/`GL-EXP-043`'s own "No
  change to `scripts/verify_ggen_v26_8_1_migration.py`" (or equivalent)
  claims are falsified because this ticket's edit reaches into logic those
  tickets depend on (their own recipe wiring, `REFUSED` codes, or the
  3-file `git_head()` targets `GL-EXP-043` claims instead).

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the total absence of exception handling before touching
# anything:
sed -n '88,118p' scripts/verify_ggen_v26_8_1_migration.py
grep -n "except" scripts/verify_ggen_v26_8_1_migration.py
  # expect exactly 4 matches (lines 165, 506, 635, 731), none matching
  # FileNotFoundError/OSError/TimeoutExpired/bare except

# Reconfirm both real, unmocked crash repros:
python3 -c "
import sys, os, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location(
    'verify_ggen_v26_8_1_migration', 'scripts/verify_ggen_v26_8_1_migration.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['verify_ggen_v26_8_1_migration'] = mod
spec.loader.exec_module(mod)
os.environ['PATH'] = '/nonexistent-bin-dir-xyz'
try:
    print('RETURNED:', mod.git_head(Path('.')))
except FileNotFoundError as e:
    print('CRASHED:', e)
"
python3 -c "
import sys, subprocess, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location(
    'verify_ggen_v26_8_1_migration', 'scripts/verify_ggen_v26_8_1_migration.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['verify_ggen_v26_8_1_migration'] = mod
spec.loader.exec_module(mod)
try:
    mod.execute(['sleep', '5'], cwd=Path('.'), timeout=1)
except subprocess.TimeoutExpired as e:
    print('CRASHED:', e)
"

# After the fix, confirm both repros now degrade into the existing
# BUILD_BROKEN report contract instead of crashing uncaught, e.g. a real
# unit test per exception type exercising a real corrupted-PATH
# FileNotFoundError and a real short-timeout TimeoutExpired against a real
# subprocess.run call -- no mocked subprocess return values, per this
# account's Chicago-style testing discipline.

# Confirm ordinary operation still works:
python3 scripts/verify_ggen_v26_8_1_migration.py --help
python3 scripts/verify_ggen_v26_8_1_migration.py --source-root ~/ggen --destination-root .
  # expect the same SOURCE_HEAD_MISMATCH_REFUSED (or whatever the current
  # real manifest pin produces) via the normal VerificationRefusal path,
  # unchanged by this ticket

git diff --stat   # must show only scripts/verify_ggen_v26_8_1_migration.py
                   # and tickets/GL-EXP-047.md
```

## Evidence this ticket is grounded in (verified this session)

- Direct `Read` of `scripts/verify_ggen_v26_8_1_migration.py:88-118`
  (`execute()`) this session: byte-for-byte the shape quoted in Outcome --
  a bare `subprocess.run(..., timeout=timeout)` at lines 97-105, zero
  `try`/`except` in the function body.
- `grep -n "require_success(\|execute(" scripts/verify_ggen_v26_8_1_migration.py`
  this session, excluding the two `def` lines: 16 real call sites at lines
  122, 132, 138, 178, 296, 329, 353, 359, 365, 379, 391, 402, 419, 425, 431,
  608 -- matching the candidate item's cited count exactly.
- Direct `Read` of `scripts/verify_ggen_v26_8_1_migration.py:578-745`
  (`main()`) this session: confirms the `try` block spans lines 586-730 and
  the sole `except` clause (line 731) is
  `except (VerificationRefusal, json.JSONDecodeError,
  tomllib.TOMLDecodeError) as exc:` -- no `FileNotFoundError`, `OSError`,
  or `subprocess.TimeoutExpired` anywhere in it; `write_json(report_path,
  refusal)` (line 738) only executes inside that `except` body, so any
  exception not matching the tuple never reaches it.
- `grep -n "except" scripts/verify_ggen_v26_8_1_migration.py` this session:
  exactly 4 matches total in the 744-line file (lines 165, 506, 635, 731) --
  confirming nothing else in the file would catch an escaping
  `FileNotFoundError`/`TimeoutExpired` either.
- Live, real, unmocked crash repro run directly this session (module
  loaded via `importlib.util` from the real file on disk, registered in
  `sys.modules` so its own `@dataclass` forward-reference resolution
  works, then called with a real corrupted `PATH` so the real OS `execvp`
  lookup for `git` genuinely fails -- no `unittest.mock`/monkeypatch
  anywhere in this verification, per this account's Chicago-style testing
  discipline): `mod.git_head(Path('.'))` -->
  `CRASHED with FileNotFoundError: [Errno 2] No such file or directory:
  'git'`.
- Live, real, unmocked crash repro for the timeout path, run directly this
  session: `mod.execute(['sleep', '5'], cwd=Path('.'), timeout=1)` -->
  `CRASHED with TimeoutExpired: Command '['sleep', '5']' timed out after 1
  seconds`. This is strictly stronger evidence than the candidate item this
  ticket is drafted from, which asserted the timeout-crash behavior from
  code inspection ("a hang crashes the whole verifier uncaught") without a
  live repro for that specific path; both failure modes are now
  independently reproduced live in this ticket.
- Direct `Read` of `tickets/GL-EXP-043.md`'s Outcome and Authored-boundary
  sections this session: confirms it names
  `scripts/verify_ggen_v26_8_1_migration.py:131` as a "4th sibling" in the
  undifferentiated-`git_head()`-collapse family, explicitly states this
  file is "not in this ticket's scope," and its own Authored boundary
  restricts to 3 other files with the line "No change to ... [this
  script]" -- confirming `GL-EXP-043`, even if executed exactly as
  written, leaves this file's `execute()` (and all 15 non-`git_head()`
  call sites) completely untouched.
- `sed -n '203-213p' tickets/GL-EXP-011.md` this session (the source
  `GL-EXP-043` itself cites): lists this file's `git_head()` (line 131)
  among 4 siblings "out of scope for this ticket's Authored boundary" --
  confirming the exclusion originates two tickets back and neither
  picked this file up.
- `grep -n "verify_ggen_v26_8_1_migration" tickets/OVERLAPS.md` this
  session: exactly 1 match, line 152, inside the existing `justfile`
  section (`GL-EXP-008`'s recipe-wiring row) -- confirmed by direct `Read`
  of that section (lines 139-169) to be entirely about a `justfile` recipe
  wrapping this script's CLI invocation, not about anything inside
  `execute()`/`require_success()`'s bodies -- no overlap with this
  ticket's target.
- `grep -l "verify_ggen_v26_8_1_migration" tickets/GL-*.md` this session:
  10 matches (`GL-ERRC-011`, `GL-EXP-008`, `GL-EXP-009`, `GL-EXP-010`,
  `GL-EXP-011`, `GL-EXP-012`, `GL-EXP-028`, `GL-EXP-034`, `GL-EXP-043`,
  `GL-EXP-044`). Per-file `grep -n -B1 -A2` of every hit, read in real
  surrounding context this session: `GL-EXP-008`/`GL-EXP-010`/`GL-EXP-012`
  each state verbatim "No change to
  `scripts/verify_ggen_v26_8_1_migration.py`"; `GL-ERRC-011`/`GL-EXP-009`/
  `GL-EXP-028` cite it only in a list of scripts lacking `EXPECTED_*`
  constants; `GL-EXP-034` cites it only as a staleness-pattern analogy for
  a different file; `GL-EXP-044` cites it only as a prior `justfile`-wiring
  precedent. None of the 10 references `execute()`, `require_success()`,
  or any exception-handling logic in this file.
- `test -d ~/ggen` this session: `EXISTS` -- confirming the sibling
  checkout the Acceptance section's real end-to-end invocation depends on
  (the same checkout `GL-EXP-008`/`GL-EXP-010` already used) is genuinely
  available in this environment, not assumed.
- `python3 scripts/verify_ggen_v26_8_1_migration.py --help` run directly
  this session: real `argparse` usage output (`--source-root`,
  `--destination-root`, `--report`), confirming the script's CLI entry
  point is currently reachable and unbroken, as a pre-change baseline.
- `git rev-parse HEAD` this session:
  `bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's
  declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
total-absence-of-exception-handling finding for `execute()` (the shared
crash surface behind all 16 subprocess call sites in this file, strictly
broader than and explicitly outside `GL-EXP-043`'s 3-file,
`git_head()`-only scope), with two independent, real, live, unmocked crash
repros (missing-binary and timeout). No fix has been implemented. The
actual fix -- catching `FileNotFoundError`/`OSError` and
`subprocess.TimeoutExpired` inside `execute()` (or an equivalent point) and
mapping them into the existing `VerificationRefusal`/`BUILD_BROKEN` report
contract, plus real Chicago-style test coverage exercising a genuinely
corrupted `PATH` and a genuinely short timeout against real subprocess
calls -- has not been implemented.
