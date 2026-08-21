# GL-EXP-044 — Wire `appliance/bin/run-reference-e2e.sh` into `justfile` as a new, optional, suggestion-only recipe

**Status:** admitted, EXECUTED 2026-08-21, was NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`appliance/bin/run-reference-e2e.sh` is a real, already-working, fast
black-box end-to-end regression harness for the Verifier Appliance
subsystem. Run directly this session, real (not simulated):

```console
$ time bash appliance/bin/run-reference-e2e.sh
... (portfolio build, sign, transparency-log append, verify, cross-check,
     replay, tamper-refusal check, revoke/verify, crown/observe/coverage
     pipeline -- full real stdout captured this session) ...
GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
bash appliance/bin/run-reference-e2e.sh  1.45s user 0.40s system 96% cpu 1.913 total
# exit code: 0
```

Exit `0`, ends in the literal line `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`.
`wc -l appliance/bin/run-reference-e2e.sh` (this session): 80 lines.
`grep -o "appliance/bin/[a-zA-Z_.-]*\.py" appliance/bin/run-reference-e2e.sh
| sort -u` (this session) shows it exercises 12 distinct scripts:
`build-document-evidence-index.py`, `build-standing-portfolio.py`,
`build-subsystem-evidence.py`, `cross-check-portfolio.py`,
`decision-engine.py`, `observe-project.py`, `project-subsystem-coverage.py`,
`replay-standing-portfolio.py`, `transparency-log.py`, `verify-crown.py`,
`verify-standing-portfolio.py`, `verify-subsystem-evidence.py`. This is the
same script `README.md:14`'s table row (`| Verifier Appliance reference |
`ALIVE` | Ten assurance subsystems independently re-derived; crown green;
replay matched; reference Release Admission true. |`) cites as its basis,
and the same script `GL-EXP-023`'s Outcome (line 97) names explicitly as
what feeds that claim ("the exact check that feeds
`run-reference-e2e.sh`'s crown-standing output, which `README.md:14`'s
... claim cites").

**Confirmed zero current wiring.** `grep -rn "run-reference-e2e" justfile
tools/v26.8.1/justfile .github/workflows/*.yml` (this session): zero
matches. `just --list` (this session) confirms the current recipe set has
no reference-e2e-named entry: `check`, `ci`, `ci-all`, `clippy`, `fmt`,
`planning-max`, `propose-disposition`, `test`, `v26-check`, `v26-ci`,
`v26-clippy`, `v26-fmt`, `v26-test`.

**Confirmed the script writes real evidence files, but into a gitignored
directory -- no git-status side effect.** The script's tail (`Read`, this
session) writes 6 JSON files to `$ROOT/evidence/appliance/` (e.g.
`reference-verifier-report.json`, `reference-crown-report.json`) plus
regenerates a `crown-report.json` it asserts against. `git check-ignore -v
evidence/appliance/reference-verifier-report.json` (this session):
`.gitignore:15:evidence/appliance/` -- matches. `git status --porcelain --
evidence/appliance/` after the real run above (this session): empty output
-- confirms the write is real but does not dirty git status, the same
generated-artifact pattern `GL-EXP-036`'s `docs/book/` finding already
established for this repo's `.gitignore` block.

**Confirmed no ticket in the 63-file corpus proposes this wiring.**
`grep -l "run-reference-e2e" tickets/GL-*.md` (this session): exactly 6
matches -- `GL-EXP-013`, `GL-EXP-015`, `GL-EXP-017`, `GL-EXP-023`,
`GL-EXP-039`, `GL-RECEIPT-007`. Reading each citation's real surrounding
context this session (not just the grep hit):

- `GL-EXP-013.md:123` and `GL-EXP-017.md:82`: both state verbatim "No
  change to `appliance/bin/run-reference-e2e.sh` itself" as their own
  Authored-boundary exclusion -- the script is explicitly off-limits to
  *those* tickets' own edits, not proposed as a `justfile` target.
- `GL-EXP-015`, `GL-EXP-023`, `GL-EXP-039`: each cites
  `run-reference-e2e.sh` only as re-run evidence (`bash
  appliance/bin/run-reference-e2e.sh` quoted as a verification command) or
  as the pipeline that feeds a check under discussion (`GL-EXP-023:97`,
  quoted above) -- none proposes a `justfile` recipe for it.
- `GL-RECEIPT-007.md:82-88`: corrects its own prior premise about *where*
  an RSA-PSS signing step lives (inside this script, not
  `build-standing-portfolio.py`) -- again citing the script as existing
  behavior to build on, not proposing to wire it anywhere.

None of the 6 mentions `justfile` in relation to this script (`grep -n
"justfile" tickets/GL-EXP-013.md tickets/GL-EXP-015.md
tickets/GL-EXP-017.md tickets/GL-EXP-023.md tickets/GL-EXP-039.md
tickets/GL-RECEIPT-007.md`, this session: zero matches in any of the six).
`grep -n "run-reference-e2e" tickets/OVERLAPS.md` (this session): zero
matches -- the existing `justfile` section of that registry (9 rows:
`GL-PLAN-002`, `GL-ERRC-022`, `GL-EXP-004`, `GL-EXP-006`, `GL-EXP-008`,
`GL-EXP-012`, `GL-EXP-032`, `GL-EXP-036`, `GL-EXP-038`, read in full this
session) has no row for this recipe name, confirming no collision.

**This mirrors an already-established, repeated pattern in this same
registry.** `GL-ERRC-022` (executed) wired `propose-disposition` as a bare,
optional, suggestion-only recipe not part of `ci`/`ci-all`/`v26-ci`.
`GL-EXP-004`/`008`/`012`/`032`/`036`/`038` (all `NOT_STARTED`) extend the
same additive shape to `planning/v26.8.7/cli.py`,
`scripts/verify_ggen_v26_8_1_migration.py`,
`tools/v26.8.20/observe_contract.py`, `tools/dsrust-disposition-proposer`'s
fmt/check/clippy/test ladder, and `mdbook build` respectively. This ticket
adds `appliance/bin/run-reference-e2e.sh` as a tenth entry in the same
`justfile` overlap section, with the same shape: a real, already-passing,
already-verified tool, zero source modification, additive-only recipe.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- checked there and against every ticket's Authored boundary before
writing this section, per the process above. `justfile` already has an
existing section listing 9 prior recipe-adding/recipe-fixing tickets; this
ticket adds a tenth row rather than a new section, disclosed by this same
write.)

```text
justfile                # new recipe only, additive
tickets/GL-EXP-044.md
tickets/OVERLAPS.md     # add a row to the existing `justfile` section
```

No change to `appliance/bin/run-reference-e2e.sh` itself, or to any of the
12 scripts it invokes -- this ticket wires the existing, already-working
script in as a new recipe; it does not modify the harness's own logic,
fixtures, or evidence-output paths. No change to `.gitignore`'s existing
`evidence/appliance/` exclusion. No change to `GL-EXP-013`/`GL-EXP-015`/
`GL-EXP-017`/`GL-EXP-023`/`GL-EXP-039`/`GL-RECEIPT-007`'s own scopes or
findings.

## Hard laws

1. The new recipe is a pure pass-through to `bash
   appliance/bin/run-reference-e2e.sh` -- it must not reimplement, wrap, or
   alter any of the script's own logic.
2. The new `justfile` recipe is additive; it does not change any existing
   recipe's behavior, including `ci`, `ci-all`, `v26-ci`, `planning-max`,
   or `propose-disposition`.
3. No new CI step is added by this ticket -- local wiring only, mirroring
   this repo's own established "real tool, zero wiring" discipline
   (`GL-ERRC-022`, `GL-EXP-004`, `GL-EXP-008`, `GL-EXP-012`, `GL-EXP-032`,
   `GL-EXP-036`). A future ticket may separately propose making a clean
   `run-reference-e2e.sh` exit `0` a CI/admission gate; that is out of
   scope here.
4. This ticket does not change what the script writes or where --
   `evidence/appliance/*.json` stays exactly as today (gitignored,
   regenerated on every invocation); no new `.gitignore` edit.
5. This ticket does not modify `appliance/bin/run-reference-e2e.sh` itself,
   honoring the same boundary `GL-EXP-013`/`GL-EXP-017` already declared
   for that file.
6. `tickets/OVERLAPS.md` gains exactly one new row in the existing
   `justfile` section (not a new section), added by this same write.
7. `git diff --stat` after this ticket touches only `justfile`,
   `tickets/GL-EXP-044.md`, and `tickets/OVERLAPS.md`.

## Falsifiers

- The new recipe does not exist, or fails to invoke the real
  `appliance/bin/run-reference-e2e.sh` script.
- `bash appliance/bin/run-reference-e2e.sh` (run via the new recipe) exits
  non-zero or its final stdout line is not
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` against the current, real repo
  tree (would mean this ticket's own "already-passing" claim was wrong --
  re-verify and correct rather than landing a recipe wrapping a broken
  script).
- Any existing `justfile` recipe's behavior changes as a side effect.
- `appliance/bin/run-reference-e2e.sh` itself, or any of the 12 scripts it
  invokes, is modified by this ticket.
- `.gitignore`'s `evidence/appliance/` exclusion is changed.
- `git diff --stat` shows any file changed other than `justfile`,
  `tickets/GL-EXP-044.md`, and `tickets/OVERLAPS.md`.
- `tickets/OVERLAPS.md`'s existing `justfile` section rows (for
  `GL-PLAN-002`, `GL-ERRC-022`, `GL-EXP-004`, `GL-EXP-006`, `GL-EXP-008`,
  `GL-EXP-012`, `GL-EXP-032`, `GL-EXP-036`, `GL-EXP-038`) are altered
  rather than only appended to.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
grep -rn "run-reference-e2e" justfile tools/v26.8.1/justfile .github/workflows/*.yml
  # expect: no output (zero matches)
just --list | grep -i reference-e2e
  # expect: no output (recipe doesn't exist yet)

# Reconfirm the script is still green in isolation (the exact command the
# new recipe will run, unmodified):
time bash appliance/bin/run-reference-e2e.sh
  # expect: exit 0, final stdout line GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE

# After adding the recipe (proposed name: reference-e2e, mirroring the
# existing single-purpose recipe naming convention used by docs-book):
just --list | grep -i reference-e2e
  # expect: the new recipe listed
just reference-e2e
  # expect: real script output, exit 0, ends in
  # GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE

# Confirm existing recipes untouched:
just --list | grep -i "planning-max\|propose-disposition\|ci-all"

git diff --stat   # must show only justfile, tickets/GL-EXP-044.md,
                   # tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session:
  `bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's
  declared Base and the Base most other `GL-EXP` tickets in this corpus
  were drafted against.
- Real, direct execution this session (not simulated) of `time bash
  appliance/bin/run-reference-e2e.sh`: exit code `0`, full real stdout
  captured (portfolio build/sign/transparency-log/verify/cross-
  check/replay/tamper-refusal/revoke/crown pipeline), final line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`, timing `1.45s user 0.40s system
  96% cpu 1.913 total`.
- `wc -l appliance/bin/run-reference-e2e.sh` this session: 80 lines.
- `grep -o "appliance/bin/[a-zA-Z_.-]*\.py"
  appliance/bin/run-reference-e2e.sh | sort -u` this session: 12 distinct
  script paths (listed in Outcome above).
- Direct `Read` of `README.md` lines 1-20 this session: line 14 is the
  literal table row `| Verifier Appliance reference | \`ALIVE\` | Ten
  assurance subsystems independently re-derived; crown green; replay
  matched; reference Release Admission true. |`.
- `grep -rn "run-reference-e2e" justfile tools/v26.8.1/justfile
  .github/workflows/*.yml` this session: zero matches.
- `just --list` this session: 13 recipes total, none named
  `reference-e2e` or similar.
- Direct `Read` of the tail of `appliance/bin/run-reference-e2e.sh` this
  session: confirms it writes 6 JSON files under
  `$ROOT/evidence/appliance/`.
- `git check-ignore -v evidence/appliance/reference-verifier-report.json`
  this session: `.gitignore:15:evidence/appliance/`.
- `git status --porcelain -- evidence/appliance/` this session,
  immediately after the real run above: empty output (no git-status side
  effect from the script's real writes).
- `grep -l "run-reference-e2e" tickets/GL-*.md` this session: exactly 6
  matches (`GL-EXP-013`, `GL-EXP-015`, `GL-EXP-017`, `GL-EXP-023`,
  `GL-EXP-039`, `GL-RECEIPT-007`).
- Per-file `grep -n "run-reference-e2e"` on each of the 6 this session,
  read in real surrounding context (not just the grep hit): confirms
  `GL-EXP-013.md:123` and `GL-EXP-017.md:82` each state "No change to
  `appliance/bin/run-reference-e2e.sh` itself" as their own boundary;
  `GL-EXP-015`/`GL-EXP-023`/`GL-EXP-039` cite the script only as
  evidence/pipeline context; `GL-RECEIPT-007:82-88` corrects a premise
  about where a signing step lives, also citing the script as existing
  behavior, not a wiring target.
- `grep -n "justfile" tickets/GL-EXP-013.md tickets/GL-EXP-015.md
  tickets/GL-EXP-017.md tickets/GL-EXP-023.md tickets/GL-EXP-039.md
  tickets/GL-RECEIPT-007.md` this session: zero matches in any of the six.
- `grep -n "run-reference-e2e" tickets/OVERLAPS.md` this session: zero
  matches.
- Direct `Read` of `tickets/OVERLAPS.md`'s `justfile` section this
  session: 9 existing rows (`GL-PLAN-002`, `GL-ERRC-022`, `GL-EXP-004`,
  `GL-EXP-006`, `GL-EXP-008`, `GL-EXP-012`, `GL-EXP-032`, `GL-EXP-036`,
  `GL-EXP-038`), none claiming a `reference-e2e`-named recipe.
- Direct `Read` of `justfile` in full this session: confirms the existing
  `propose-disposition` recipe's header comment pattern ("optional,
  suggestion-only wiring ... Not part of `ci`/`ci-all`/`v26-ci` and not
  invoked from any workflow") this ticket's own new recipe will match.
- Direct `Read` of `tickets/GL-ERRC-022.md` (`EXECUTED`) and
  `tickets/GL-EXP-036.md` (`NOT_STARTED`) in full this session: both
  confirm the identical additive/suggestion-only `justfile`-recipe shape
  this ticket follows.

## Execution evidence (this session, 2026-08-21)

Before touching anything, `git rev-parse HEAD` reconfirmed
`bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's declared
Base -- no discrepancy.

Reconfirmed the gap immediately before editing:
`grep -rn "run-reference-e2e" justfile tools/v26.8.1/justfile
.github/workflows/*.yml` -- zero matches. `just --list | grep -i
reference-e2e` -- zero matches (recipe did not yet exist).

Added exactly one new recipe to `justfile` (proposed name `reference-e2e`,
used as-is), a pure pass-through with no reimplementation of the script's
own logic:

```just
# GL-EXP-044: optional, suggestion-only wiring for the real, already-passing
# Verifier Appliance reference regression harness. Not part of ci/ci-all/v26-ci
# and not invoked from any workflow -- a pure pass-through, no reimplementation
# of the script's own logic, and it does not change any existing recipe.
reference-e2e:
    bash appliance/bin/run-reference-e2e.sh
```

Confirmed additive-only by comparing `git diff -- justfile` immediately
before and immediately after this edit: the working tree already carried
unrelated pre-existing dirty state on `justfile` (a header-comment fix and
the already-executed `propose-disposition`/`verify-prd-ard` recipes, none
of it this ticket's own edit); the only delta this ticket's edit introduced
on top of that pre-existing state is the 7-line block quoted above, appended
after `verify-prd-ard`, mirroring the same byte-level-diff verification
`GL-EXP-048`'s own row used. Zero existing lines removed or altered.

Ran `just --list | grep -i reference-e2e` after the edit: the new recipe is
listed (`reference-e2e             # of the script's own logic, and it does
not change any existing recipe.`).

Ran `time just reference-e2e`: real stdout from the full portfolio
build/sign/transparency-log/verify/cross-check/replay/tamper-refusal/revoke/
crown/observe/coverage pipeline, final line
`GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`, `just reference-e2e  1.34s user
0.41s system 91% cpu 1.919 total`, exit code `0` -- identical shape and exit
behavior to the direct `bash appliance/bin/run-reference-e2e.sh` run quoted
in this ticket's Outcome section above, confirming the recipe is a real
pass-through and not a reimplementation.

Ran `just --list | grep -i "planning-max\|propose-disposition\|ci-all"`
after the edit: all three still listed, unchanged. Full `just --list` after
the edit shows 14 recipes total (13 pre-existing plus `reference-e2e`);
every pre-existing recipe name and its own header comment is byte-identical
to before this edit.

No edit made to `appliance/bin/run-reference-e2e.sh` or any of the 12
scripts it invokes. No edit made to `.gitignore`.

## CI verification (this session, 2026-08-21)

`just ci-all` run to confirm the working tree remains healthy after this
ticket's edit: exit `0` (verified directly via synchronous re-run plus
`$?`, cross-checked with a matching backgrounded run). `ci-all` = `ci`
(main workspace) + `v26-ci` (`tools/v26.8.1` workspace). All 8 steps
passed: `cargo fmt --check` (both workspaces) clean, `cargo check` (both)
clean, `cargo clippy -D warnings` (both) zero warnings, `cargo test
--all-targets` (both) all green -- 18/18 tests passed in the main
workspace (`ggen-legacy-lsp`: 1+0+7+4+3+1+2), 18/18 tests passed in the
`tools/v26.8.1` workspace (3+13+0+0+2). No `error`/`FAILED`/`panic` line
in either log.

Scope note: the currently committed diff (`main...HEAD`) touches
`src/analysis.rs`, `tests/`, `tools/dsrust-disposition-proposer/`,
`ontology`, and `planning/v26.8.20` -- it does **not** touch
`appliance/bin/` (`git diff --stat main...HEAD -- appliance/bin/`:
empty), so this `ci-all` pass is a general repository-health check, not a
recipe-targeted re-verification of this ticket's own `reference-e2e`
recipe; the recipe-specific re-verification (`just reference-e2e`, exit
`0`, final line `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`) is already
covered above in Execution evidence. This ticket's own `justfile`/ticket
edits remain uncommitted working-tree changes (per this ticket's
Publication boundary -- no merge authority, no commit made this
session); at the time of this CI pass `git status --porcelain` reported
118 lines (pre-existing dirty state from other tickets' work, not
introduced by this ticket -- see Execution evidence above for the
ticket-scoped before/after diff that isolates this ticket's own 7-line
delta).

## Standing

`PARTIAL_ALIVE` -- executed. The real, already-passing
`appliance/bin/run-reference-e2e.sh` reference regression harness is now
wired into `justfile` as an additive, suggestion-only `reference-e2e`
recipe, verified this session to be a pure pass-through (exit `0`, final
line `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`, identical to the direct-script
run). `just ci-all` (general repository health, both workspaces) also
confirmed clean this session: exit `0`, 36/36 tests passing, zero
fmt/clippy warnings across both workspaces -- see CI verification above
(a general health check, not a targeted re-run of this ticket's own
recipe, which is separately confirmed above in Execution evidence). Not
promoted further because CI wiring remains explicitly out of scope (Hard
Law 3), matching the standing pattern `GL-EXP-036`/`GL-EXP-048` (its
closest structural analogs) declare for the same reason.
