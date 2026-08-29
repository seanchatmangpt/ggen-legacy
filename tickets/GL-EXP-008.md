# GL-EXP-008 — Wire `scripts/verify_ggen_v26_8_1_migration.py` into `justfile` as an optional, suggestion-only recipe

**Status:** admitted, NOT_STARTED — drafted by standing ultracode exploration cron

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`scripts/verify_ggen_v26_8_1_migration.py` is a real, working, already-executed
verifier (confirmed this session: `wc -l` reports 744 lines; `grep -n` confirms
real `blake3` per-file digest checks (`file_blake3`, `source_blake3`/
`destination_blake3` comparisons), real git-blob lineage checks
(`SOURCE_BLOB_DRIFT_REFUSED`, `observed_blob != record["source_git_blob"]`), a
real `negative_controls()` function (line 487, mutates a byte and asserts the
`blake3` comparison catches it), and a real deterministic-replay check
(`REPLAY_DRIFT_REFUSED`, line 663) — with the summary payload literally
labeling its own three guarantees `"per-file-git-blob-and-blake3-lineage"`,
`"negative-controls"`, and `"deterministic-replay"` at lines 685/695/696) — but
nothing wires it into this repo's admission workflow:
`grep -rn "verify_ggen_v26_8_1_migration" justfile tools/v26.8.1/justfile
.github/workflows/*.yml` (run this session) returns zero matches, and
`just --list | grep -i migrat` (run this session) confirms no recipe exposes
it. This is the same "real tool, zero wiring" shape already admitted and
executed for `tools/dsrust-disposition-proposer` (`GL-ERRC-022`, `EXECUTED`)
and already admitted (`NOT_STARTED`) for `planning/v26.8.7/cli.py`
(`GL-EXP-004`) — this ticket applies the identical, already-precedented
pattern (an additive, suggestion-only `justfile` pass-through recipe, no
change to the wrapped script's own logic, no CI gate) to the third sibling
candidate.

`grep -l "verify_ggen_v26_8_1_migration" tickets/*.md` (run this session)
returns exactly one match, `tickets/GL-ERRC-011.md`. Reading that ticket in
context (its "Authored boundary" section, run this session): it names
`verify_ggen_v26_8_1_migration.py` only as one of four scripts **confirmed to
have no `EXPECTED_*` constants** and explicitly states "No other script
(...`verify_ggen_v26_8_1_migration.py`, all already confirmed to have no
`EXPECTED_*` constants) is touched." `GL-ERRC-011` scopes itself away from
this script; it does not propose wiring it anywhere. No ticket in this corpus
owns that gap.

**Honest caveat, discovered live this session rather than glossed over:** the
script does not currently pass clean against the real sibling `~/ggen` repo.
Running it directly this session —

```console
$ python3 scripts/verify_ggen_v26_8_1_migration.py --source-root ~/ggen --destination-root .
REFUSED: SOURCE_HEAD_MISMATCH_REFUSED expected=8351af4c5bbbf60bd99ab8417752a1762c6ea4e3 observed=a6403d99c24f2372d2ec496f390536900bdefc74
```

— the manifest's recorded `source_head` (`8351af4c...`) no longer matches
`~/ggen`'s real, current `HEAD` (`a6403d99c...`, confirmed via
`git -C ~/ggen rev-parse HEAD` this session). The verifier's refusal behavior
is itself working correctly (it is refusing to certify a migration against a
source tree that has since moved), but it means the new recipe must **not**
be treated as a green gate. Per the same discipline `GL-ERRC-022` and
`GL-EXP-004` already apply to their own not-fully-green underlying tools, the
new recipe must stay additive/suggestion-only and must not be added to
`ci`/`ci-all`/`v26-ci`.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` —
check there before assuming sole ownership of a path below.)

```text
justfile                                   # new recipe only, additive
tickets/GL-EXP-008.md
```

No change to `scripts/verify_ggen_v26_8_1_migration.py` — this ticket wraps
the existing, already-working script; it does not modify its verification
logic, its `REFUSED` codes, or its report schema. No change to
`GL-ERRC-022`'s `propose-disposition` recipe or `GL-EXP-004`'s proposed
`planning-cli` recipe — this ticket adds a fourth, distinct `justfile` recipe
alongside `planning-max`, `propose-disposition`, and the (not yet executed)
`planning-cli`. This `justfile` overlap should be disclosed in
`tickets/OVERLAPS.md`'s existing `## \`justfile\`` section at execution time,
alongside the three entries already recorded there.

## Hard laws

1. The new recipe is a pure pass-through to `python3
   scripts/verify_ggen_v26_8_1_migration.py` — it must not reimplement,
   swallow, or reinterpret the script's `REFUSED`/exit-code behavior.
2. The new `justfile` recipe is additive; it does not change any existing
   recipe's behavior, including `planning-max`, `propose-disposition`, `ci`,
   `ci-all`, and `v26-ci`.
3. No new CI step is added by this ticket — CLI wiring only. The recipe must
   **not** be added to `ci`/`ci-all`/`v26-ci`, both because that mirrors
   `GL-ERRC-022`'s and `GL-EXP-004`'s existing discipline for not-fully-green
   tools, and because this script currently `REFUSED`s against the real
   `~/ggen` sibling repo's current state (see "Outcome" caveat above) — gating
   CI on it today would make every run fail for a reason unrelated to the
   change under review.
4. `--source-root` must remain a required, caller-supplied argument (mirrors
   the script's own `parse_args()`) — the new recipe must not hardcode a
   default source path that silently papers over the current
   `SOURCE_HEAD_MISMATCH_REFUSED` state.

## Falsifiers

- The new recipe does not exist / fails to invoke the real
  `scripts/verify_ggen_v26_8_1_migration.py`.
- `just --list` no longer shows `planning-max` or `propose-disposition`
  unchanged after this ticket's diff.
- The new recipe is reachable from `ci`, `ci-all`, or `v26-ci`.
- `git diff --stat` shows any file changed other than `justfile` and
  `tickets/GL-EXP-008.md`.
- `git diff --stat -- scripts/verify_ggen_v26_8_1_migration.py` shows any
  output (would mean this ticket strayed into the script's own logic).

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Confirm the gap before fixing:
grep -rn "verify_ggen_v26_8_1_migration" justfile tools/v26.8.1/justfile .github/workflows/*.yml
  # expect: no output (zero matches)
just --list | grep -i migrat   # expect no output (recipe doesn't exist yet)

# After adding the recipe (proposed name: verify-migration, mirroring
# GL-ERRC-022's `propose-disposition *ARGS:` pass-through shape):
just --list | grep -i verify-migration        # expect the new recipe listed
just verify-migration --help                  # expect the real script's usage line
just verify-migration --source-root ~/ggen    # expect the real REFUSED/ALIVE output, unmodified

# Confirm existing recipes untouched:
just planning-max               # expect unchanged verify.py --strict behavior
just --list | grep -i propose-disposition   # expect unchanged

git diff --stat   # must show only justfile and tickets/GL-EXP-008.md
git diff --stat -- scripts/verify_ggen_v26_8_1_migration.py   # must show no output
```

## Evidence this ticket is grounded in (verified this session)

- `wc -l scripts/verify_ggen_v26_8_1_migration.py` (run directly this
  session): `744 scripts/verify_ggen_v26_8_1_migration.py`.
- `grep -n "blake3\|git.blob\|negative.control\|deterministic.replay\|REFUSED"
  scripts/verify_ggen_v26_8_1_migration.py` (run directly this session)
  confirms real `file_blake3()` (line 144), a real `negative_controls()`
  function (line 487), a real `REPLAY_DRIFT_REFUSED` check (line 663), and
  the summary's own guarantee labels `"per-file-git-blob-and-blake3-lineage"`
  (line 685), `"negative-controls"` (line 695), `"deterministic-replay"`
  (line 696).
- `grep -rn "verify_ggen_v26_8_1_migration" justfile tools/v26.8.1/justfile
  .github/workflows/*.yml` (run directly this session): zero matches (exit
  code 1, no output).
- `just --list | grep -i migrat` (run directly this session): zero matches.
- `grep -l "verify_ggen_v26_8_1_migration" tickets/*.md` (run directly this
  session): exactly one match, `tickets/GL-ERRC-011.md`. Reading that file's
  "Authored boundary" section directly (this session) confirms it names
  `verify_ggen_v26_8_1_migration.py` only as one of 4 scripts confirmed to
  have no `EXPECTED_*` constants, and explicitly excludes it from that
  ticket's own touched-files list — `GL-ERRC-011` does not propose wiring
  this script anywhere.
- `python3 scripts/verify_ggen_v26_8_1_migration.py --source-root ~/ggen
  --destination-root .` (run directly this session, real command, real
  sibling repo, not simulated):
  ```text
  REFUSED: SOURCE_HEAD_MISMATCH_REFUSED expected=8351af4c5bbbf60bd99ab8417752a1762c6ea4e3 observed=a6403d99c24f2372d2ec496f390536900bdefc74
  ```
  cross-checked against `git -C ~/ggen rev-parse HEAD` (run directly this
  session): `a6403d99c24f2372d2ec496f390536900bdefc74` — matches the
  script's own `observed=` value exactly, confirming the refusal is real,
  not fabricated.
- `python3 scripts/verify_ggen_v26_8_1_migration.py --help` (run directly
  this session) confirms the real `argparse` interface:
  `--source-root SOURCE_ROOT` (required), `--destination-root
  DESTINATION_ROOT` (optional), `--report REPORT` (optional).
- `tickets/GL-ERRC-022.md` (read directly this session, `EXECUTED`) and
  `tickets/GL-EXP-004.md` (read directly this session, `NOT_STARTED`) are
  the two directly analogous, already-drafted/landed precedents for this
  exact "real tool, zero wiring" pattern — same additive, suggestion-only
  `justfile` recipe shape, same "no CI gate" discipline, same corpus.
- `tickets/OVERLAPS.md`'s `## \`justfile\`` section (read directly this
  session) already tracks three tickets sharing this file
  (`GL-PLAN-002`'s `planning-max`, `GL-ERRC-022`'s `propose-disposition`,
  `GL-EXP-004`'s proposed `planning-cli`) as non-conflicting, each owning a
  distinct recipe name — this ticket's `verify-migration` recipe follows
  the same non-overlapping-target convention.

## Standing

`PARTIAL_ALIVE` ceiling only — this ticket is drafted and admitted,
`NOT_STARTED`. No code has been written or run beyond the read-only
verification commands captured above (confirming the script's real internals,
its absence from `justfile`/CI, its exclusion from `GL-ERRC-011`'s scope, and
its current live `SOURCE_HEAD_MISMATCH_REFUSED` state against `~/ggen`).
Executing this ticket (adding the recipe, re-running the "Acceptance"
commands, and recording their real output) is required before any higher
standing can be claimed.
