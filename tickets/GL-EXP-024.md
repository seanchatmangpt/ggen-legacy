# GL-EXP-024 — Create the missing CI step for `planning/v26.8.7`'s 27 real unit tests

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tickets/GL-PLAN-002.md`'s own `## Acceptance` section (read directly this
session) names exactly three commands as the standing's evidentiary bar:

```bash
python3 planning/v26.8.7/verify.py --strict
python3 -m unittest discover -s planning/v26.8.7/tests -v
planning/v26.8.7/skdecide_classical_engine.py --help
```

`.github/workflows/planning-v26-8-7.yml` -- the CI workflow whose own name
is "GL-PLAN-002 planning v26.8.7 replay" and whose `paths:` trigger
includes `planning/v26.8.7/**` and `tickets/GL-PLAN-002.md` -- runs only
two of these three commands (read in full this session, 21 lines):

```yaml
      - name: Verify combinatorial-max planning subsystem
        run: python3 planning/v26.8.7/verify.py --strict --output /tmp/gl-plan-002-report.json
      - name: Stable scikit-decide process witness
        run: planning/v26.8.7/skdecide_classical_engine.py --help | head -n 1 | grep '^skdecide-classical-engine/26.8.7$'
```

The `python3 -m unittest discover -s planning/v26.8.7/tests -v` command --
the ticket's own second, explicitly-named acceptance criterion -- is
absent. `grep -n "unittest\|test_planning"
.github/workflows/planning-v26-8-7.yml` (run this session) returns zero
matches. `justfile`'s own `planning-max` recipe (the one local command a
developer runs to reproduce what this workflow gates, per its own header
comment convention established for `ci-all`) likewise runs only `python3
planning/v26.8.7/verify.py --strict` -- confirmed by direct read this
session -- so neither CI nor the local one-command reproduction path
exercises the test suite.

**This is not a hypothetical or trivial gap.** `planning/v26.8.7/tests/`
contains a real, substantive suite -- confirmed this session by running it
directly:

```
$ python3 -m unittest discover -s planning/v26.8.7/tests -v
...
Ran 27 tests in 0.915s

OK
```

27 real tests, covering (per the real class/method names observed this
session) PDDL/plan-shape validation
(`PddlAndPlanTests.test_val_plan_shape`), MFW/POWL projection invariants
(`ProjectionTests.test_mfw_family_inventory_is_combinatorial`,
`test_mfw_projection_preserves_all_reachable_edges`,
`test_powl_projection_has_no_execution_authority`), and the recursive
parent/child controller's own hard laws
(`RecursiveControllerTests.test_blocked_spawn_child_manufacture_verify_admit_resume_parent`,
`test_manufacture_is_intent_only`, `test_receipt_subject_mismatch_refused`,
`test_replay_detects_tamper`,
`test_snapshot_matches_declared_orchestration_schema`, among others). Every
one of `GL-PLAN-002`'s ten Hard Laws (reference-solution exclusion,
planning-selects-doesn't-actuate, no self-promotion, tamper detection,
etc.) maps most directly onto one of these unit tests, not onto
`verify.py --strict`'s own report-shape checks alone. A PR that broke any
one of these 27 tests -- for example, silently reintroducing reference-
solution leakage into goal reconstruction, or letting a manufacture intent
actuate -- would merge cleanly through the real, current
`planning-v26-8-7.yml` workflow with a green check, because that workflow
never runs the suite that would catch it.

**No existing ticket covers this gap.** `grep -l "unittest discover\|test_planning"
tickets/GL-*.md` (run this session) returns `GL-AUTO-001.md` (one bare
filename, `planning/v26.8.7/tests/test_planning.py`, inside its 115-file
`REFUSED:FORBIDDEN_DIFF:...` dump -- the same non-substantive pattern
already established elsewhere in this corpus), `GL-EXP-004.md` (one
sentence noting `test_planning.py` exercises `lib.py`'s functions, in the
course of establishing that `cli.py` itself has zero test coverage -- a
different, narrower observation about a different file, not about CI
wiring), and `GL-PLAN-002.md` itself (the source of the three-command bar
this ticket's finding is measured against). None of the three names or
proposes fixing the workflow's own incomplete command coverage.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below.
`.github/workflows/planning-v26-8-7.yml` is claimed in full by
`GL-PLAN-002` (`admitted concurrent executable ticket`) in its own
Authored boundary -- a real, direct overlap this ticket discloses in
`tickets/OVERLAPS.md`'s new `.github/workflows/planning-v26-8-7.yml`
section, added by this ticket, rather than silently assuming sole
ownership. This ticket's change is additive -- one new step appended to
the existing job -- and enforces `GL-PLAN-002`'s own already-stated
Acceptance bar; it does not alter that ticket's own scope, Hard Laws, or
any other part of the workflow.)

```text
.github/workflows/planning-v26-8-7.yml   # one new step, additive, appended to the existing job
tickets/GL-EXP-024.md
tickets/OVERLAPS.md   # add .github/workflows/planning-v26-8-7.yml section
```

No change to `planning/v26.8.7/**` (any source, test, or fixture file
under `GL-PLAN-002`'s own boundary), `justfile`'s `planning-max` recipe (a
separate, already-established entry point this ticket does not alter --
though a future session may choose to add the same `unittest discover`
line there too; this ticket scopes itself to the CI workflow only, per
Hard Law 3), or any other workflow file (`.github/workflows/ci.yml`).

## Hard laws

1. The new CI step runs exactly `python3 -m unittest discover -s
   planning/v26.8.7/tests -v` -- the literal command `GL-PLAN-002.md`'s
   own Acceptance section already specifies, not a paraphrase or a
   `pytest`-based reimplementation.
2. The new step is additive to the existing `bounded-planning-replay` job
   -- it does not replace, reorder ahead of, or change the exit semantics
   of either existing step (`verify.py --strict`, the `skdecide` process
   witness).
3. This ticket does not also add the missing command to `justfile`'s
   `planning-max` recipe -- that is a natural, obvious follow-on this
   ticket deliberately leaves out to keep its own diff minimal and its
   overlap with `GL-PLAN-002`'s `justfile` claim (already tracked in
   `tickets/OVERLAPS.md`'s existing `justfile` section) unchanged.
4. If any of the 27 existing tests currently fails when run via CI's
   `ubuntu-latest` runner environment (as opposed to this session's local
   macOS run), that failure must be recorded honestly in this ticket's
   execution evidence, not silently worked around by skipping or altering
   a test -- this ticket adds enforcement of an existing, already-passing
   local suite; it does not get to also fix tests it discovers are
   platform-fragile as an incidental side quest.
5. `tickets/OVERLAPS.md` gains a new section for this ticket's overlap
   with `GL-PLAN-002` on `.github/workflows/planning-v26-8-7.yml`, per
   this ticket's own Authored-boundary note above.
6. `git diff --stat` after this ticket touches only
   `.github/workflows/planning-v26-8-7.yml`, `tickets/GL-EXP-024.md`, and
   `tickets/OVERLAPS.md`.

## Falsifiers

- After the fix, `grep -n "unittest discover" .github/workflows/planning-v26-8-7.yml`
  still returns no match.
- The new step is not additive -- it replaces or reorders either existing
  step, or changes the job's overall pass/fail semantics for a case that
  passed before this ticket.
- `planning-max`'s own recipe body in `justfile` is modified by this
  ticket (Hard Law 3).
- Any of the 27 tests is skipped, deleted, or altered to make it pass,
  rather than the CI step being added to run them as-is.
- `git diff --stat` after this ticket touches any file outside
  `.github/workflows/planning-v26-8-7.yml`, `tickets/GL-EXP-024.md`, and
  `tickets/OVERLAPS.md`.

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the fix lands, not yet-observed outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
grep -n "unittest\|test_planning" .github/workflows/planning-v26-8-7.yml
  # expect: no output (zero matches)
python3 -m unittest discover -s planning/v26.8.7/tests -v 2>&1 | tail -5
  # expect: Ran 27 tests ... OK  (confirms the suite the new step will run is real and green)

# After adding the step:
grep -n "unittest discover" .github/workflows/planning-v26-8-7.yml
  # expect: the new step's run: line

# Confirm the other two existing steps are unchanged:
grep -n "verify.py --strict\|skdecide_classical_engine" .github/workflows/planning-v26-8-7.yml

git diff --stat   # must show only .github/workflows/planning-v26-8-7.yml,
                   # tickets/GL-EXP-024.md, tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- Direct `Read` of `tickets/GL-PLAN-002.md:53-59` this session -- confirms
  the three-command `## Acceptance` block verbatim as quoted in Outcome.
- Direct `Read` of `.github/workflows/planning-v26-8-7.yml` in full (21
  lines) this session -- confirms the `on:`/`paths:` trigger
  (`planning/v26.8.7/**`, `tickets/GL-PLAN-002.md`,
  `.github/workflows/planning-v26-8-7.yml`, `AGENTS.md`, `justfile`), the
  job name `bounded-planning-replay`, and its exactly two `run:` steps,
  quoted verbatim in Outcome.
- `grep -n "unittest\|test_planning" .github/workflows/planning-v26-8-7.yml`
  this session: zero matches (exit 1, no output).
- `grep -A3 "^planning-max:" justfile` this session: confirms the recipe
  body is `python3 planning/v26.8.7/verify.py --strict` only, no
  `unittest` invocation.
- `python3 -m unittest discover -s planning/v26.8.7/tests -v` (run
  directly this session, real execution, not simulated): `Ran 27 tests in
  0.915s`, `OK` -- full real output captured, including individual test
  names, in Outcome above.
- `ls planning/v26.8.7/tests/` this session: confirms `test_planning.py`
  is the sole test file (plus `__pycache__`).
- `grep -l "unittest discover\|test_planning" tickets/GL-*.md` this
  session: `GL-AUTO-001.md`, `GL-EXP-004.md`, `GL-PLAN-002.md`. Per-file
  `grep -n` on each this session confirms: `GL-AUTO-001.md`'s hit is one
  filename inside its `REFUSED:FORBIDDEN_DIFF:...` dump; `GL-EXP-004.md`'s
  hit is a single sentence about `lib.py` function coverage, unrelated to
  CI-workflow wiring (confirmed by reading that ticket in full this
  session -- its entire scope is wiring `cli.py`'s 10 subcommands into
  `justfile`); `GL-PLAN-002.md`'s hit is the source three-command
  Acceptance block itself.
- `grep -n "planning-v26-8-7.yml" tickets/GL-PLAN-002.md` this session:
  confirms line 17, inside that ticket's own `## Authored boundary` fenced
  block -- the real, direct overlap this ticket discloses.
- `grep -n "planning-v26-8-7.yml" tickets/OVERLAPS.md` this session: zero
  matches -- no existing registry entry for this file.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
CI-coverage gap (the workflow's own missing step relative to
`GL-PLAN-002`'s own stated Acceptance bar, and the real 27-test suite that
bar names) and the `tickets/OVERLAPS.md` disclosure this ticket's own Hard
Law 5 requires. The actual workflow-file edit has not been made.
