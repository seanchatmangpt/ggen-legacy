# GL-EXP-051 — Raise `step_two.py`'s `git()`/`run_command()` out of a simultaneous zero-timeout, zero-exception-handling crash/hang risk in this repo's own admitted release-verification pipeline

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/step_two.py`'s two subprocess wrappers, `git()` (line 55) and
`run_command()` (line 65), back this repo's own admitted `just step-two`
release-verification recipe (`tools/v26.8.1/justfile:11-12`:
`python3 step_two.py --root {{root}}`). Neither passes a `timeout=` kwarg to
its `subprocess.run()` call, and neither is itself called from inside a
`try`/`except` anywhere in the file:

```python
def git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=root, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


def run_command(
    root: Path, command_id: str, argv: Sequence[str], *,
    expected_exit: int = 0, expected_exits: Sequence[int] | None = None,
    require_text: str | None = None, cwd: Path | None = None,
) -> CommandEvidence:
    started = time.monotonic_ns()
    completed = subprocess.run(
        list(argv), cwd=cwd if cwd is not None else root,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        env={**os.environ, "CARGO_TERM_COLOR": "never"},
    )
    ...
```

`grep -n "timeout=\|TimeoutExpired" tools/v26.8.1/step_two.py` returns zero
matches in the whole 637-line file. Both wrapper call sites use `check=False`
and manually inspect `.returncode`, so a normal nonzero exit is already
handled cleanly (`run_command`'s `passed` computation, `git()`'s callers
`clean_paths`/`exact_head` both branch on `result.returncode != 0`) -- the
gap is specifically the two failure modes `check=False` and a returncode
check do **not** cover: (1) the subprocess never starts (missing binary --
`FileNotFoundError`/`OSError` at the `subprocess.run()` call itself, before
there is any `CompletedProcess` to inspect), and (2) the subprocess starts
but never exits (an unbounded hang -- no `timeout=` means `subprocess.run`
blocks indefinitely).

Live, unmocked repro this session (no `unittest.mock`/monkeypatch, per this
account's Chicago-style testing discipline -- a real corrupted `PATH` so the
real OS `execvp` lookup for `git` genuinely fails):

```
$ python3 -c "
import sys, os
sys.path.insert(0, 'tools/v26.8.1')
import step_two
from pathlib import Path
os.environ['PATH'] = '/nonexistent-bin-dir-xyz'
try:
    step_two.git(Path('.'), 'rev-parse', 'HEAD')
except FileNotFoundError as e:
    print('CRASHED with FileNotFoundError:', e)
try:
    step_two.run_command(Path('.'), 'test-cmd', ['git', 'rev-parse', 'HEAD'])
except FileNotFoundError as e:
    print('CRASHED with FileNotFoundError:', e)
"
CRASHED with FileNotFoundError: [Errno 2] No such file or directory: 'git'
CRASHED with FileNotFoundError: [Errno 2] No such file or directory: 'git'
```

Both functions crash uncaught. `main()` (line 627) calls `execute(root)`
with no `try`/`except` either, so any exception from any of the file's real
call sites propagates all the way to the interpreter as a raw traceback and
a nonzero process exit -- bypassing the deliberate `report.json`/
`receipt.json` evidence-writing (`write_json` at lines 609/618) that this
file's own module docstring exists to guarantee ("Step Two is ALIVE when the
autonomous control system can observe, plan, verify, falsify, replay, and
fail closed without human steering"). A crash here is not a fail-closed
report -- it is an unreported process death, the opposite of the module's
stated contract.

`git()` has 2 real call sites (`clean_paths` at line 239, `exact_head` at
line 251); `run_command()` has 10 real call sites (lines 273, 280, 287, 301,
310, 362, 387, 435, 482, 517), of which 7 invoke `cargo test`/`cargo run`
(`pddl-parser-boundary`, `cli-default-verb-law`, `project-coverage`,
`crown-observe-first`, `crown-observe-replay`,
`crown-sabotage-negative-control`, `crown-real-state-observation`) and 3
invoke a Python script (`planning-structural`, `subsystem-evidence-
manifest`, `coverage-matrix-sabotage-portfolio`) -- 12 combined call sites
across the two wrapper functions, all exposed to the same unbounded-hang and
uncaught-spawn-failure risk. (**Correction to the candidate item this ticket
is drafted from**: it claimed "11 real call sites" for `run_command()` and
"8 `cargo test`/`cargo run` invocations" -- a live re-count this session via
`grep -n "run_command("` found exactly 10 call sites, of which 7, not 8, are
`cargo`. The 11th line the candidate item's count likely included is
`run_command`'s own `def` at line 65, not a call. This correction does not
change the finding's substance -- the missing-timeout/missing-exception-
handling gap is identical whether the count is 10 or 11 call sites.)

One of the 10 `run_command()` calls (`crown-sabotage-negative-control`, line
435) sits inside a `try:`/`finally:` block (lines 431-466) -- but that block
has no `except` clause; it exists solely to guarantee
`shutil.rmtree(sabotage_dir, ...)` cleanup (line 466), not to catch or
degrade a subprocess failure. An exception raised inside that block (from
`build_crown_input_copy`, `sabotage_coverage_matrix`, or the wrapped
`run_command` call itself) still propagates uncaught after the `finally`
cleanup runs -- Python's `try`/`finally` re-raises by design. So this one
call site is no better protected than the other 9.

## Comparison to this repo's own `git_head()`/`exact_head()` collapse family
(context, not an overlap claim -- see "Authored boundary" for the real
overlap, which is with `GL-ERRC-014`, not this family)

- `GL-ERRC-019` (Rust, `coverage_projection.rs::exact_head()`, `EXECUTED`)
  fixed a 3-way undifferentiated-`"UNKNOWN"` *cause* collapse, but Rust's
  `Command::output()` returns a `Result` regardless of fix status -- even
  its pre-fix code could not crash uncaught on a missing `git` binary.
- `GL-EXP-011` (Python, `observe_contract.py::git_head()`, `NOT_STARTED`)
  and the 3 targets of `GL-EXP-043` (Python, `document_evidence_index.py`/
  `subsystem_evidence_manifest.py`/`verify_planning.py`'s `git_head()`,
  `NOT_STARTED`) are the closer Python siblings. `GL-EXP-043`'s Outcome
  section documents that its 3 targets have **zero** exception handling and
  crash uncaught on a missing `git` binary -- the identical defect class
  this ticket's 2 targets share.
- **Correction to the candidate item this ticket is drafted from**: it
  described `GL-EXP-005/011/019/023/043/047` as "all `NOT_STARTED`" -- a
  live re-check this session (`head -8` of each) found `GL-EXP-005` is
  actually `EXECUTED`, not `NOT_STARTED`. Of the 6 named siblings, 2
  (`GL-ERRC-019`, `GL-EXP-005`) are `EXECUTED`; 4 (`GL-EXP-011/019/023/047`)
  are `NOT_STARTED`. This correction does not change this ticket's own
  finding -- none of those 6 tickets targets `step_two.py`'s `git()`/
  `run_command()` (confirmed by direct inspection of each ticket's Authored
  boundary this session; see "Authored boundary" below).
- This ticket's targets differ from every sibling above in one respect: they
  are the file's **generic subprocess-invocation primitives**, called by
  every command this pipeline runs (10+2 call sites), not a single-purpose
  helper called from 1-3 sites each. A hang or crash in `git()`/
  `run_command()` takes down the entire `step-two` release-verification pass
  in one shot, not one subsystem's status field.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
checked there and against every ticket's Authored boundary before writing
this section. `grep -rln "step_two" tickets/*.md` this session returns 4
matches: `GL-ERRC-019.md`, `GL-EXP-011.md`, `GL-EXP-043.md`, and
`GL-ERRC-014.md`. Direct inspection of each this session:
`GL-ERRC-019`/`GL-EXP-011`/`GL-EXP-043` only *mention* `step_two.py` in
passing (as the pipeline that calls their real Rust/Python targets, or as an
explicit exclusion -- `GL-EXP-043`'s Authored boundary states verbatim "No
change to `tools/v26.8.1/step_two.py`"); none claims it in an Authored
boundary. **`GL-ERRC-014` (admitted, `NOT_STARTED`) does** claim
`tools/v26.8.1/step_two.py` in its own Authored boundary -- a real,
disclosed overlap, added to `tickets/OVERLAPS.md` by this ticket (new
section below) rather than left implicit. `GL-ERRC-014`'s target is
functionally disjoint from this ticket's: it adds a
`STALE_REFERENCE_UNVERIFIABLE` status specifically for the one
already-diagnosed failure path caused by dereferencing the unreachable git
object `6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6` cited in
`docs/v26.8.1/document-evidence-index.json`/`ontology/v26.8.1/document-
evidence.ttl` (consumed indirectly via the `subsystem-evidence-manifest`
command's downstream data, not via `git()`/`run_command()` themselves) --
its own Outcome text never names `git()` or `run_command()`. This ticket's
target is the two generic subprocess wrapper functions' own
timeout/exception-safety, independent of which command they are invoked
for. See the new `tools/v26.8.1/step_two.py` section in
`tickets/OVERLAPS.md`, added by this ticket, for the full reconciliation.)

```text
tools/v26.8.1/step_two.py   # git() and run_command() bodies only (lines 55-103)
tickets/GL-EXP-051.md
tickets/OVERLAPS.md         # new tools/v26.8.1/step_two.py section
```

No change to any of the 12 call sites' arguments beyond what is strictly
required to let `git()`/`run_command()` continue returning their existing
`CompletedProcess`/`CommandEvidence` types on every currently-passing path --
no change to `clean_paths()`, `exact_head()`, `execute()`'s gate list, the
`commands`/`gates` construction, `write_json()`, `main()`'s argument
parsing, or any Gate's pass/fail logic beyond what is strictly required to
give a newly-caught spawn-failure/timeout its own distinguishable
`CommandEvidence`/gate outcome instead of an uncaught crash. No change to
`tools/v26.8.1/coverage_sabotage_tests.py`, `tools/v26.8.1/justfile`, or any
`docs/v26.8.1/document-evidence-index.*`/`ontology/v26.8.1/document-
evidence.ttl` content (`GL-ERRC-014`'s eventual target, once it lands). No
change to `tools/v26.8.1/document_evidence_index.py`,
`tools/v26.8.1/subsystem_evidence_manifest.py`, or
`planning/v26.8.1/verify_planning.py` (`GL-EXP-043`'s 3 targets) or
`tools/v26.8.20/observe_contract.py` (`GL-EXP-011`'s target) -- this ticket
does not touch any `git_head()`/`exact_head()` sibling outside
`step_two.py` itself.

## Hard laws

1. A real, healthy invocation of every one of the 12 call sites (with `git`
   and `cargo` present on `PATH`, no injected hang) must return the
   identical `CompletedProcess`/`CommandEvidence` value as before this
   ticket -- the happy path's observable behavior, including
   `elapsed_ms`/`stdout_sha256`/`stderr_sha256`/`passed` fields on
   `CommandEvidence`, does not change.
2. A missing binary (`FileNotFoundError`/`OSError` at the `subprocess.run()`
   call) in either `git()` or `run_command()` must no longer propagate
   uncaught to `main()` -- it must be caught and mapped to a
   distinguishable, non-crashing outcome (e.g. a `CommandEvidence`/`Gate`
   entry with `passed=False` and the exception text recorded, or an
   equivalent typed report field), so `execute()` still reaches
   `write_json()` and produces a real `report.json`/`receipt.json` instead
   of dying with a raw traceback.
3. Both `subprocess.run()` calls (inside `git()` and inside `run_command()`)
   must gain a `timeout=` bound; a subprocess that exceeds it must raise (or
   be caught and mapped to a distinguishable timeout outcome per Hard Law
   2's shape) rather than blocking `execute()` indefinitely. The specific
   bound's value is an implementation choice for whoever executes this
   ticket, not fixed by this ticket -- but it must be a finite, real number,
   not `None`/absent.
4. `git diff --stat` after this ticket touches only
   `tools/v26.8.1/step_two.py`, `tickets/GL-EXP-051.md`, and
   `tickets/OVERLAPS.md`.

## Falsifiers

- After the fix, the live repro used in "Outcome" above (a real corrupted
  `PATH`, no mocking) still raises `FileNotFoundError` uncaught out of
  `git()` or `run_command()` instead of returning a value.
- After the fix, a `run_command()`/`git()` call against a command that never
  exits (e.g. `["sleep", "9999"]` as `argv`) still blocks `execute()`
  indefinitely instead of returning/raising within the configured
  `timeout=` bound.
- Any of the 12 call sites' `passed`/`actual_exit`/`stdout_sha256` value in
  `.ggen/v26.8.1/step-two/report.json` changes for a normal, non-hanging,
  non-crashing run against this real repository with `git`/`cargo` present
  on `PATH` (regression on ordinary operation).
- `git diff --stat` after this ticket touches any file outside
  `tools/v26.8.1/step_two.py`, `tickets/GL-EXP-051.md`, and
  `tickets/OVERLAPS.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the zero-timeout, zero-exception-handling gap before touching
# anything:
sed -n '55,103p' tools/v26.8.1/step_two.py
grep -n "timeout=\|TimeoutExpired" tools/v26.8.1/step_two.py   # expect: no matches

# Reconfirm the real crash repro (no mocking -- a real broken PATH against
# the real subprocess call):
python3 -c "
import sys, os
sys.path.insert(0, 'tools/v26.8.1')
import step_two
from pathlib import Path
os.environ['PATH'] = '/nonexistent-bin-dir-xyz'
try:
    step_two.git(Path('.'), 'rev-parse', 'HEAD')
    print('did not crash (unexpected pre-fix)')
except FileNotFoundError as e:
    print('CRASHED (confirms pre-fix state):', e)
"

# After the fix, confirm the identical repro degrades to a typed,
# non-crashing outcome instead of raising, and confirm a real hanging
# command (e.g. ['sleep', '9999']) is bounded by the new timeout= instead
# of blocking forever -- both via real subprocess calls, no mocked
# subprocess.run return values, per this account's Chicago-style testing
# discipline.

# Confirm ordinary operation still works end to end:
cd tools/v26.8.1 && just step-two; echo "EXIT:$?"
cd /Users/sac/ggen-legacy

git diff --stat   # must show only tools/v26.8.1/step_two.py,
                   # tickets/GL-EXP-051.md, tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- Direct `Read` of `tools/v26.8.1/step_two.py:1-103` this session: confirms
  `git()` (line 55) and `run_command()` (line 65) byte-for-byte as quoted in
  Outcome, neither passing `timeout=` to `subprocess.run()`.
- `wc -l tools/v26.8.1/step_two.py` this session: `637`, matching the
  candidate item's cited total.
- `grep -n "timeout=\|TimeoutExpired" tools/v26.8.1/step_two.py` this
  session: zero matches, exit code 1.
- `grep -n "git(root" tools/v26.8.1/step_two.py` this session: confirms
  exactly 2 real call sites beyond the `def` -- line 239 (`clean_paths`),
  line 251 (`exact_head`).
- `grep -n "run_command(" tools/v26.8.1/step_two.py` this session: 11 total
  matches, 1 of which is the `def run_command(` at line 65 -- 10 real call
  sites at lines 273, 280, 287, 301, 310, 362, 387, 435, 482, 517. Read each
  call's `argv` directly: 7 are `cargo test`/`cargo run`, 3 are
  `sys.executable`-invoked Python scripts.
- `grep -n "except\b" tools/v26.8.1/step_two.py` this session: exactly 1
  match, line 353 (`except (json.JSONDecodeError, OSError) as exc:`),
  inside the `manufacturing-synchronized-state` block -- guards a
  `json.loads`/`.read_bytes()` pair, not any `subprocess.run()` call.
  `grep -n "^\s*try:" tools/v26.8.1/step_two.py` this session: 2 matches,
  lines 337 and 431. Line 337's `try` is the block containing line 353's
  `except` (unrelated to subprocess calls, as above). Line 431's `try` has
  no matching `except` in its `try:`/`finally:` block (lines 431-466) --
  confirmed by direct `Read` of lines 428-466 -- so even the one
  `run_command()` call site textually inside a `try` block (line 435, the
  `crown-sabotage-negative-control` command) is not exception-guarded; the
  block exists only to guarantee `shutil.rmtree` cleanup via `finally`, and
  re-raises any exception after that cleanup runs.
- Live, real, unmocked crash repro this session (no
  `unittest.mock`/monkeypatch anywhere, per this account's Chicago-style
  testing discipline): imported the real `step_two` module, called the real
  `git()` and `run_command()` functions with `os.environ['PATH']` pointed at
  a real nonexistent directory (so the real OS `execvp` lookup for `git`
  genuinely fails) -- both raised `FileNotFoundError: [Errno 2] No such file
  or directory: 'git'` uncaught. See "Outcome" above for the full transcript.
  This is strictly stronger evidence than the candidate item this ticket is
  drafted from, which asserted the crash/hang behavior from code inspection
  ("would either crash ... or block it forever") rather than a live repro.
- `sed -n '1,20p' tools/v26.8.1/justfile` this session: confirms lines 11-12
  are the real, wired `step-two` recipe (`python3 step_two.py --root
  {{root}}`), matching the candidate item's citation.
- `grep -rln "step_two" tickets/*.md` this session: 4 matches
  (`GL-ERRC-019.md`, `GL-EXP-011.md`, `GL-EXP-043.md`, `GL-ERRC-014.md`).
  Direct `awk '/## Authored boundary/,/## Hard laws/'` on each this session:
  only `GL-ERRC-014.md` names `tools/v26.8.1/step_two.py` in its own
  Authored boundary (`tools/v26.8.1/step_two.py   # STALE_REFERENCE_
  UNVERIFIABLE status on unreachable-git-object path`); the other 3 mention
  the file only in passing or as an explicit exclusion. `GL-ERRC-014`'s
  Outcome section (re-read in full this session) never names `git()` or
  `run_command()` -- its target is the `execute()`-level handling of one
  specific dereferenced-stale-object failure, not the generic subprocess
  wrappers. This grounds the "Authored boundary" section's overlap
  disclosure and the new `tickets/OVERLAPS.md` section above.
- `head -8 tickets/GL-EXP-005.md tickets/GL-EXP-011.md tickets/GL-EXP-019.md
  tickets/GL-EXP-023.md tickets/GL-EXP-047.md tickets/GL-ERRC-019.md` this
  session: confirms Status lines -- `GL-ERRC-019` and `GL-EXP-005` are
  `EXECUTED`; `GL-EXP-011`, `GL-EXP-019`, `GL-EXP-023`, `GL-EXP-047` are
  `admitted, NOT_STARTED`. Corrects the candidate item's claim that all 6
  named siblings were `NOT_STARTED` (see "Comparison" section above).
- `grep -n "timeout=" scripts/verify_ggen_v26_8_1_migration.py` this
  session: 5 matches (lines 104, 122, 332, 388, 399) -- confirms
  `GL-EXP-047`'s target file already has `timeout=` bound on its
  subprocess calls, consistent with the candidate item's characterization
  of it as the closest analog missing only the exception-handling half.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies, with a real
live unmocked crash repro, the simultaneous zero-timeout/zero-exception-
handling finding for `step_two.py`'s `git()`/`run_command()` -- the actual
fix (a `timeout=` bound on both `subprocess.run()` calls, and a caught,
distinguishable outcome for a spawn failure or timeout at every one of the
12 call sites, plus Chicago-style real-subprocess test coverage) has not
been implemented.
