# GL-EXP-004 — Wire `planning/v26.8.7/cli.py`'s 10 subcommands into the admission/workflow surface

**Status:** admitted, NOT_STARTED — drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`planning/v26.8.7/cli.py` is a real, working `argparse` dispatcher exposing
10 subcommands (`reconstruct-goal`, `solve-capabilities`, `classify-pddl`,
`project-mfw`, `project-powl`, `orchestrate`, `replay`, `verify-plan`,
`probe-engine`, `run-engine`) — confirmed this session by running
`python3 planning/v26.8.7/cli.py --help`, which lists all 10, and
`python3 planning/v26.8.7/cli.py reconstruct-goal --help`, which resolves a
real per-subcommand parser (`usage: ggen-legacy-planning-max reconstruct-goal
[-h] benchmark`, exit 0). `justfile`'s only touch point for
`planning/v26.8.7` is the `planning-max` recipe
(`python3 planning/v26.8.7/verify.py --strict`, `justfile:41-42`) — `cli.py`
is never invoked from `justfile`, `tools/v26.8.1/justfile`, or any
`.github/workflows/*.yml` (re-confirmed this session:
`grep -n 'planning-max\|planning/v26.8.7' justfile` returns only the
`verify.py` line). `grep -rln 'cli\.py' planning/v26.8.7/tests/` returns no
matches — zero test coverage of the CLI dispatcher itself (as opposed to the
`lib.py` functions it wraps, which `planning/v26.8.7/tests/test_planning.py`
does exercise). This ticket wires the existing, working CLI in as an
optional, suggestion-only pass-through recipe — mirroring the pattern
already executed for the sibling candidate in `GL-ERRC-022` (which wired
`tools/dsrust-disposition-proposer`'s `propose-disposition` binary into
`justfile` the same way) — it does not change what `planning-max` verifies
or admits.

This re-verifies (with real commands run this session, not re-cited)
`docs/v26.9.1/innovation-candidates.md`'s #2-ranked, score-10 candidate
("`planning/v26.8.7` CLI subcommands not exposed via any top-level verb"),
which that document explicitly states still needs "its own `GL-*` ticket
with real, independently-re-verified evidence" before being actionable.

**Correction to the candidate's own evidence, made during this ticket's
drafting**: the candidate write-up that proposed this ticket claimed
`grep -l 'cli\.py' tickets/GL-*.md` "returns nothing — no ticket
references it." Re-run this session, that grep in fact returns
`tickets/GL-AUTO-001.md` (line 110). Reading that match in context: it is
one path among 115 inside a `REFUSED:FORBIDDEN_DIFF:...` file list —
`GL-AUTO-001`'s acceptance command mechanically enumerating every file that
differs from its own admitted base, `planning/v26.8.7/cli.py` included only
because it happens to be one of many files touched elsewhere in this
working tree. `GL-AUTO-001` does not describe, own, or propose wiring
`cli.py`'s subcommands anywhere in its own prose. The substantive claim
("no ticket concerns itself with exposing `cli.py`'s subcommands via a
top-level verb") still holds; the literal "grep returns nothing" framing in
the source candidate does not, and is corrected here rather than repeated.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` —
check there before assuming sole ownership of a path below.)

```text
justfile                              # new recipe only, additive
tickets/GL-EXP-004.md
```

No change to `planning/v26.8.7/**` — this ticket wraps the existing,
already-working `cli.py` dispatcher; it does not modify `cli.py`, `lib.py`,
or any other file under `GL-PLAN-002`'s `planning/v26.8.7/**` authored
boundary. No change to `GL-PLAN-002`'s `planning-max` recipe or
`GL-ERRC-022`'s `propose-disposition` recipe — this ticket adds a third,
distinct `justfile` recipe alongside them. `justfile`'s overlap with
`GL-PLAN-002` (which owns the `planning-max` target only) and `GL-ERRC-022`
(which owns the `propose-disposition` target only) is disclosed in
`tickets/OVERLAPS.md`.

## Hard laws

1. The new recipe is a pure pass-through to `python3
   planning/v26.8.7/cli.py` — it must not reimplement, wrap with retries,
   or alter any subcommand's arguments or output.
2. The new `justfile` recipe is additive; it does not change any existing
   recipe's behavior, including `planning-max` and `propose-disposition`.
3. No new CI step is added by this ticket — CLI wiring only (a future
   ticket may separately propose making any subcommand a CI/admission
   gate; out of scope here).
4. This ticket does not change what `planning-max`/`verify.py --strict`
   admits, verifies, or reports — `cli.py`'s subcommands remain
   independent, human-invoked operations, not an admission-workflow input.
5. `planning/v26.8.7/cli.py`, `lib.py`, and every other file under
   `GL-PLAN-002`'s `planning/v26.8.7/**` boundary are read-only from this
   ticket's perspective.

## Falsifiers

- The new recipe does not exist / fails to invoke the real
  `planning/v26.8.7/cli.py` dispatcher.
- `just --list` no longer shows `planning-max` or `propose-disposition`
  unchanged after this ticket's diff.
- Any existing `justfile` recipe's behavior changes as a side effect.
- `git diff --stat` shows any file changed other than `justfile` and
  `tickets/GL-EXP-004.md`.
- `planning/v26.8.7/**` shows any diff at all (would mean this ticket
  strayed into `GL-PLAN-002`'s exclusive boundary).

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Confirm the gap before fixing:
grep -n 'planning-max\|planning/v26.8.7' justfile   # expect only the planning-max line
just --list | grep -i planning-cli                  # expect no output (recipe doesn't exist yet)

# After adding the recipe (proposed name: planning-cli, mirroring
# GL-ERRC-022's `propose-disposition *ARGS:` pass-through shape):
just --list | grep -i planning-cli                  # expect the new recipe listed
just planning-cli --help                             # expect the real 10-subcommand usage line
just planning-cli reconstruct-goal --help             # expect the real per-subcommand usage line

# Confirm existing recipes untouched:
just planning-max            # expect unchanged verify.py --strict behavior
just --list | grep -i propose-disposition            # expect unchanged

git diff --stat   # must show only justfile and tickets/GL-EXP-004.md
git diff --stat -- planning/v26.8.7   # must show no output
```

## Evidence this ticket is grounded in (verified this session)

- `python3 planning/v26.8.7/cli.py --help` (run directly this session):
  ```text
  usage: ggen-legacy-planning-max [-h]
                                  {reconstruct-goal,solve-capabilities,classify-pddl,project-mfw,project-powl,orchestrate,replay,verify-plan,probe-engine,run-engine} ...
  ```
  exit code 0 — a real, working `argparse` dispatcher with all 10
  subcommands.
- `grep -n 'add_parser' planning/v26.8.7/cli.py` (run directly this
  session) confirms each of the 10 subcommand names is a real
  `sub.add_parser(...)` call at lines 45, 48, 51, 54, 57, 62, 66, 69, 72,
  76 — not a stub list.
- `python3 planning/v26.8.7/cli.py reconstruct-goal --help` (run directly
  this session) resolves a real per-subcommand parser: `usage:
  ggen-legacy-planning-max reconstruct-goal [-h] benchmark`, exit 0.
- `grep -n 'planning-max\|planning/v26.8.7' justfile` (run directly this
  session) returns exactly one match, `justfile:41-42`:
  ```text
  planning-max:
      python3 planning/v26.8.7/verify.py --strict
  ```
  — `cli.py` does not appear anywhere in `justfile`.
- `grep -rln 'cli\.py' planning/v26.8.7/tests/` (run directly this
  session) returns no output — zero test files reference `cli.py`.
- `docs/v26.9.1/innovation-candidates.md:22-26` (read directly this
  session) states this exact candidate at score 10, and its closing
  section (`## What this means for v26.9.1`) requires "its own `GL-*`
  ticket with real, independently-re-verified evidence" before promotion —
  this ticket is that re-verification.
- `tickets/GL-ERRC-022.md` (read directly this session, `EXECUTED`) is the
  directly analogous, already-landed precedent for the sibling candidate
  (`tools/dsrust-disposition-proposer`): same pattern (optional,
  suggestion-only `justfile` pass-through recipe, no source-file change to
  the wrapped tool, no CI wiring), same corpus.
- `tickets/GL-PLAN-002.md:16` (read directly this session) claims
  `justfile # planning-max target only` in its authored boundary — the
  overlap this ticket's new recipe creates on the same file is disclosed
  in `tickets/OVERLAPS.md` rather than left implicit, per
  `tickets/AUDIT-REPORT.md`'s finding that undisclosed same-file overlaps
  were this corpus's dominant recurring defect.
- Corrected evidence claim: `grep -l 'cli\.py' tickets/GL-*.md` (run
  directly this session) returns `tickets/GL-AUTO-001.md`, not "nothing"
  as the source candidate asserted — see the "Correction" paragraph under
  `## Outcome` above for the full re-check.

## Standing

`PARTIAL_ALIVE` ceiling only — this ticket is drafted and admitted,
`NOT_STARTED`. No code has been written or run beyond the read-only
verification commands captured above (confirming `cli.py` works standalone
and is absent from `justfile`/CI/tests). Executing this ticket (adding the
recipe, re-running the "Acceptance" commands, and recording their real
output) is required before any higher standing can be claimed.
