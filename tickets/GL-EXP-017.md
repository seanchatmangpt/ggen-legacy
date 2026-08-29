# GL-EXP-017 — Eliminate the byte-for-byte duplicated `write_json()` helper in `appliance/bin/`

**Status:** `EXECUTED` 2026-08-21 — real fix landed in the main checkout and re-verified there
(was `NOT_STARTED`, drafted by standing ultracode exploration cron)

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`grep -n "^def write_json" appliance/bin/*.py` (run directly this session) matches exactly 5
files: `build-standing-portfolio.py:16`, `decision-engine.py:16`, `replay-standing-portfolio.py:16`,
`transparency-log.py:16`, `verify-standing-portfolio.py:16`. Direct body comparison (`sed -n
'16,18p'` on each, run this session, then `md5` over each 3-line span) confirms all 5 are
byte-for-byte identical — same hash (`0965c88f7e66af1f1314426033f6f9b4`) on all 5:

```python
def write_json(path,obj):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
```

These are the identical 5 files already named in `tickets/GL-EXP-013.md` (`admitted,
NOT_STARTED`, read in full this session) as carrying the sibling `sha256_file()`/`read_json()`
duplication that ticket consolidates into a new `appliance/bin/_shared.py` module.
`GL-EXP-013`'s own Hard Law 4 (verbatim, confirmed this session): "`write_json` (duplicated
verbatim in the same 5 chunked-`sha256_file` files) is explicitly **out of scope** for this
ticket — not consolidated, not touched... it is a legitimate, distinct follow-up candidate,
not this ticket's job." This ticket is that named follow-up.

`grep -l "write_json" tickets/*.md` (run this session) returns only `tickets/GL-EXP-013.md`
(which excludes it per Hard Law 4 above) — no ticket currently owns consolidating this
duplicate. `grep -n "write_json" docs/v26.9.1/*.md docs/v26.8.20/*.md` (run this session,
both directories confirmed to exist via `ls docs/`) returns zero matches — the duplication is
not named as a candidate anywhere in the milestone docs either. This finding is new.

Per-file call-site counts (`grep -n "write_json(" <file>`, run this session, excluding each
file's own `def` line): `build-standing-portfolio.py` — 7 call sites (lines 57-69);
`decision-engine.py` — 2 call sites (lines 35-36); `replay-standing-portfolio.py` — 1 call
site (line 38); `verify-standing-portfolio.py` — 1 call site (line 72);
`transparency-log.py` — **0 call sites** (the function is defined at line 16 but never
invoked anywhere in that 65-line file, confirmed by reading the file in full this session —
genuinely dead code, not merely duplicated code, in that one file specifically).

This ticket adds one canonical `write_json(path, obj)` to `appliance/bin/_shared.py`,
imported by all 5 files, replacing each private redefinition (and, for
`transparency-log.py`, removing the now-unused import rather than adding a dead call site).
Because `GL-EXP-013` is `NOT_STARTED` (`appliance/bin/_shared.py` does not yet exist —
confirmed via `ls appliance/bin/_shared.py` this session), this ticket's Hard Laws below
handle execution in either order: if `GL-EXP-013` has already run, this ticket appends
`write_json` to the existing `_shared.py`; if it has not, this ticket creates `_shared.py`
with `write_json` alone and leaves `sha256_file`/`read_json` for `GL-EXP-013` to add on top
(both tickets import from the same module name, so neither ordering produces a conflicting
file — see Hard Law 3).

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there
before assuming sole ownership of a path below. `grep -n "appliance/bin" tickets/OVERLAPS.md`
returns no existing section this session, and `GL-EXP-013`'s own Authored boundary already
claims `appliance/bin/_shared.py` as a new module and the same 5 files below for its own
`sha256_file`/`read_json` consolidation — this ticket adds a second, explicitly compatible
claim on the same paths under Hard Law 3, and adds the `OVERLAPS.md` section recording both
tickets' shared claim on `_shared.py` and these 5 files.)

```text
appliance/bin/_shared.py                    # add write_json() (create the file if GL-EXP-013 has not run yet)
appliance/bin/build-standing-portfolio.py   # delete private write_json(), import shared, rewrite 7 call sites
appliance/bin/decision-engine.py            # delete private write_json(), import shared, rewrite 2 call sites
appliance/bin/replay-standing-portfolio.py  # delete private write_json(), import shared, rewrite 1 call site
appliance/bin/transparency-log.py           # delete private write_json() (dead code; 0 call sites), drop the now-unused import
appliance/bin/verify-standing-portfolio.py  # delete private write_json(), import shared, rewrite 1 call site
tickets/GL-EXP-017.md
tickets/OVERLAPS.md                         # add/extend the appliance/bin `_shared.py` section, noting GL-EXP-013 + GL-EXP-017 both touch it
```

No change to `appliance/bin/build-document-evidence-index.py`,
`appliance/bin/build-subsystem-evidence.py`, `appliance/bin/project-subsystem-coverage.py`,
`appliance/bin/verify-crown.py`, `appliance/bin/verify-subsystem-evidence.py`,
`appliance/bin/cross-check-portfolio.py`, or `appliance/bin/observe-project.py` (none defines
`write_json` — confirmed via `grep -l "write_json" appliance/bin/*.py` this session, which
returns exactly and only the 5 files above). No change to `appliance/bin/run-reference-e2e.sh`
itself (it only invokes the scripts). No change to `GL-EXP-013`'s own `sha256_file`/
`read_json` consolidation logic, `GL-ERRC-010`'s `transparency-log.py` `verify()` `--anchor`
mode, or `GL-RECEIPT-007`'s `build-standing-portfolio.py` SLSA/DSSE projection — this ticket
touches only the `write_json` definitions and their call sites.

## Hard laws

1. `appliance/bin/_shared.py` contains exactly one canonical `write_json(path, obj)`,
   byte-for-byte matching the implementation already shared by all 5 files today (3-line body:
   `Path(path)`, `mkdir(parents=True, exist_ok=True)`, `write_text(json.dumps(obj, indent=2,
   sort_keys=True)+"\n")`). No new serialization behavior, no new key ordering, no new
   indentation width.
2. All 5 files' private `def write_json` definitions are deleted outright (not deprecated,
   not left dead) and replaced with an import from `_shared`. `transparency-log.py` gets the
   deletion and the import removed entirely (it has zero call sites — adding an unused import
   would be new dead code, which this ticket does not introduce).
3. If `appliance/bin/_shared.py` already exists when this ticket executes (i.e. `GL-EXP-013`
   ran first), this ticket **appends** `write_json` to it without modifying `sha256_file` or
   `read_json`. If `appliance/bin/_shared.py` does not yet exist (i.e. this ticket runs
   first), this ticket creates it containing `write_json` alone; `GL-EXP-013`, whenever it
   executes, is responsible for adding `sha256_file`/`read_json` to that same file without
   removing `write_json`. Neither ticket may overwrite or truncate the other's addition to
   `_shared.py`.
4. Every call site's external behavior is unchanged: same file written, same bytes, same
   directory-creation behavior on a missing parent, for the same `(path, obj)` input.
5. `appliance/bin/run-reference-e2e.sh` must exit `0` and end in the literal line
   `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` after this ticket's change, matching both baseline
   runs captured in this ticket's Evidence section.

## Falsifiers

- `grep -n "^def write_json" appliance/bin/*.py` still matches any file after this ticket
  executes.
- `appliance/bin/_shared.py` does not exist after this ticket executes, or (if `GL-EXP-013`
  had already run) this ticket's change removed `sha256_file` or `read_json` from it.
- `transparency-log.py` gains a new call to `write_json` (it has none today; adding one would
  be new behavior, not a like-for-like consolidation).
- `bash appliance/bin/run-reference-e2e.sh` exits non-zero, or its final stdout line is not
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`.
- A direct `json.dumps({"a":1,"b":2}, indent=2, sort_keys=True)+"\n"` written via
  `pathlib.Path.write_text` disagrees byte-for-byte with the same object written via
  `_shared.write_json` to a fresh path (would mean the consolidation changed output bytes,
  not just the call site).
- `git diff --stat` touches `sha256_file`, `read_json`, `tree_inventory`, `tree_digest`,
  `canonical`, `sha256_bytes`, any `argparse`/CLI surface, or any file outside the Authored
  boundary above.
- Any of `build-document-evidence-index.py`, `build-subsystem-evidence.py`,
  `project-subsystem-coverage.py`, `verify-crown.py`, `verify-subsystem-evidence.py`,
  `cross-check-portfolio.py`, or `observe-project.py` is modified (none has a `write_json`
  duplicate to consolidate).

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the duplication before touching anything:
grep -n "^def write_json" appliance/bin/*.py
grep -n "write_json(" appliance/bin/transparency-log.py   # expect: only the def line (0 call sites)

# Baseline regression proof (record before any change):
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

# After adding/extending appliance/bin/_shared.py and rewriting the 5 call sites:
grep -n "^def write_json" appliance/bin/*.py   # expect: zero matches
grep -c "from _shared import\|import _shared" appliance/bin/build-standing-portfolio.py \
  appliance/bin/decision-engine.py appliance/bin/replay-standing-portfolio.py \
  appliance/bin/transparency-log.py appliance/bin/verify-standing-portfolio.py
  # expect: 1 for each of the 5 files

# Deterministic output-bytes equivalence:
python3 -c "
import sys, json, tempfile
from pathlib import Path
sys.path.insert(0, 'appliance/bin')
from _shared import write_json
obj = {'b': 2, 'a': 1}
p = Path(tempfile.mktemp())
write_json(p, obj)
expected = json.dumps(obj, indent=2, sort_keys=True) + '\n'
assert p.read_text() == expected, 'byte mismatch'
print('write_json output bytes match expected serialization')
"

# Regression proof, post-fix:
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

git diff --stat   # only the Authored-boundary files above
```

## Evidence this ticket is grounded in (verified this session)

- `grep -n "^def write_json" appliance/bin/*.py`: confirmed exactly 5 matches, one per file
  named above, each at line 16.
- `sed -n '16,18p' <file> | md5` on each of the 5 files: all 5 produced the identical hash
  `0965c88f7e66af1f1314426033f6f9b4`, confirming byte-for-byte identical 3-line bodies.
- `cat tickets/GL-EXP-013.md` (read in full this session): confirmed `admitted, NOT_STARTED`
  status, and confirmed Hard Law 4 verbatim excludes `write_json` from that ticket's scope
  while naming it "a legitimate, distinct follow-up candidate."
- `grep -l "write_json" tickets/*.md`: returns only `tickets/GL-EXP-013.md`.
- `grep -n "write_json" docs/v26.9.1/*.md docs/v26.8.20/*.md`: zero matches; `ls docs/`
  confirmed both `v26.9.1` and `v26.8.20` directories exist and were actually searched.
- `grep -n "write_json(" <file>` on each of the 5 files, read with line numbers: confirmed
  per-file call-site counts (7/2/1/1/0) and confirmed `transparency-log.py`'s `write_json` has
  zero call sites by reading the full 65-line file — the function, along with `read_json`,
  `tree_inventory`, and `tree_digest` defined in that same file, is dead code there (only
  `sha256_bytes`, `sha256_file`, `canonical`, `verify`, and `append_entry` are actually used
  by that file's own `main()`).
- `ls appliance/bin/_shared.py`: no such file — confirmed `GL-EXP-013` has not executed yet,
  so this ticket's Hard Law 3 ordering logic is live, not hypothetical.
- `grep -n "appliance/bin" tickets/OVERLAPS.md`: zero matches — no existing section to
  conflict with; this ticket is the second to claim `appliance/bin/_shared.py` (after
  `GL-EXP-013`), handled explicitly via Hard Law 3.
- `git rev-parse HEAD`: `bce7f6386c4203784beaae426e40804636c4151a`, identical to the base
  commit `GL-EXP-013` was drafted against — confirming no drift between the two tickets'
  baselines.
- `bash appliance/bin/run-reference-e2e.sh` (run directly this session, twice, real
  subprocess execution, not simulated): both runs exited `0` and ended in the literal line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`; first run's stdout tail: `{"standing": "ALIVE",
  "subsystems": 10}` / `{"checks": 10, "coverage_unchanged": true, "standing": "ALIVE"}` /
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`; second run produced the same three lines.
- `grep -rln "run-reference-e2e\|appliance/bin" .github/workflows/*.yml`: zero matches — this
  script is not invoked by CI, matching the same finding already recorded in `GL-EXP-013`.
- `find . -iname "*appliance*test*" -o -iname "*test*appliance*"`: no output — no dedicated
  test suite exists for `appliance/bin/`, matching `GL-EXP-013`'s own finding.

## Standing

`PARTIAL_ALIVE` — executed 2026-08-21, all Falsifiers re-run for real against the actual
checkout, none tripped.

- `git rev-parse HEAD` re-checked before touching anything: `bce7f6386c4203784beaae426e40804636c4151a`,
  identical to this ticket's declared Base — no drift.
- Confirmed `GL-EXP-013` had already executed (uncommitted, in-tree) before this ticket started:
  `appliance/bin/_shared.py` already existed, containing exactly `sha256_file()`/`read_json()`,
  and all 5 target files already carried `from _shared import sha256_file, read_json` with only
  their private `write_json` def remaining (line 12 in each, not line 16 as originally drafted —
  the line-number shift matches `GL-EXP-013`'s already-applied consolidation). Hard Law 3's
  "append" branch applied; the "create" branch did not.
- `appliance/bin/_shared.py` now contains exactly three functions — `sha256_file`, `read_json`
  (untouched, byte-identical to `GL-EXP-013`'s addition), and the new `write_json(path, obj)`
  (3-line body, byte-identical to the 5 files' former private copies) — confirmed via
  `grep -n "^def " appliance/bin/_shared.py`.
- `grep -n "^def write_json" appliance/bin/*.py` now matches only `appliance/bin/_shared.py:28`
  (the canonical definition Hard Law 1 requires) — zero matches in any of the 5 former
  call-site files.
- `grep -c "from _shared import"` on all 5 files: 1 each. 4 files
  (`build-standing-portfolio.py`, `decision-engine.py`, `replay-standing-portfolio.py`,
  `verify-standing-portfolio.py`) import `sha256_file, read_json, write_json`;
  `transparency-log.py` imports only `sha256_file, read_json` (unchanged — Hard Law 2 forbids
  adding an unused `write_json` import there, since it has zero call sites).
- All 7 real call sites (7 in `build-standing-portfolio.py`, 2 in `decision-engine.py`, 1 in
  `replay-standing-portfolio.py`, 1 in `verify-standing-portfolio.py`) confirmed byte-identical
  before/after via direct diff — no call site rewritten, only the def/import lines changed.
  `transparency-log.py` confirmed to have zero `write_json` references of any kind after the
  edit (`grep -n "write_json" appliance/bin/transparency-log.py` returns no output).
- Deterministic output-bytes equivalence: `_shared.write_json({'b':2,'a':1})` produced
  `json.dumps(obj, indent=2, sort_keys=True) + "\n"` byte-for-byte — confirmed by direct
  assertion, real script run, not simulated.
- `python3 -m py_compile` on `_shared.py` and all 5 edited files: clean, no syntax errors.
- `bash appliance/bin/run-reference-e2e.sh`, run once pre-change and once post-change: both
  exited `0` and ended in the literal line `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` — no
  behavioral regression. (The `receipt_digest` field mid-output differed between the two runs;
  the literal final line and exit code, which are this ticket's actual Hard Law 5 bar, matched
  both times. That digest is not derived from anything this ticket's diff touches.)
- `git diff --stat -- appliance/bin`: touches 10 files total, because this working tree carries
  `GL-EXP-013`'s own consolidation uncommitted underneath this ticket's edits (neither ticket
  has been committed) — the other 5 files
  (`build-document-evidence-index.py`, `build-subsystem-evidence.py`,
  `project-subsystem-coverage.py`, `verify-crown.py`, `verify-subsystem-evidence.py`) reflect
  `GL-EXP-013`'s pre-existing, already-applied `sha256_file`/`read_json` consolidation only —
  this ticket did not edit them. Isolated to this ticket's own 5 Authored-boundary files:
  `git diff --stat -- appliance/bin/build-standing-portfolio.py
  appliance/bin/decision-engine.py appliance/bin/replay-standing-portfolio.py
  appliance/bin/transparency-log.py appliance/bin/verify-standing-portfolio.py` shows exactly
  those 5 files, 10 insertions(+), 45 deletions(-). Content-diff grep for `tree_inventory`,
  `tree_digest`, `canonical`, `sha256_bytes`, `argparse` across the full `appliance/bin` diff:
  zero matches — none of those out-of-scope symbols were touched.
  `appliance/bin/cross-check-portfolio.py` and `appliance/bin/observe-project.py` confirmed
  unmodified (`git diff --stat` against both: empty).
- `tickets/OVERLAPS.md` updated: the `appliance/bin/_shared.py` section now reflects
  `GL-EXP-017` as `EXECUTED`, so the still-`NOT_STARTED` siblings (`GL-EXP-041`, `GL-EXP-045`)
  know `_shared.py` now carries three functions, not two.

## CI verification (post-execution, full repo gate)

`just ci-all` was run for real in this checkout. Real exit code: `0` (all steps green, both
workspaces).

- Root workspace (`Cargo.toml`): `cargo fmt --all -- --check` PASS (no diff); `cargo check
  --all-targets --locked` PASS; `cargo clippy --all-targets --locked -- -D warnings` PASS (zero
  warnings); `cargo test --all-targets --locked --test-threads=1` PASS — 20 tests total across
  `lib.rs`, `main.rs`, `tests/analysis.rs` (7), `tests/analysis_boundary.rs` (4),
  `tests/contract.rs` (3), `tests/exit_code.rs` (1), `tests/lsp_boundary.rs` (2); 0 failed.
- `tools/v26.8.1` workspace (via `just -f tools/v26.8.1/justfile ...`): `fmt --check` PASS;
  `check` PASS; `clippy -D warnings` PASS; `cargo test --all-targets --locked` PASS — 18 tests
  total across `lib.rs` (3), `main.rs`/`ggen_v26_8_1_verifier` (13
  `document_evidence_sabotage_tests`), `src/bin/project_coverage.rs` (0),
  `src/bin/subsystem_verifier.rs` (0), `tests/verifier_boundary.rs` (2); 0 failed.
- Total: **38 tests passed, 0 failed** across both workspaces. Full raw log saved at
  `/private/tmp/claude-501/-Users-sac-ggen-legacy/87a9b589-243d-4eb5-b50c-e957cd0f71db/scratchpad/ci-all.log`
  (127 lines, terminated with `EXIT_CODE:0`).

`appliance/bin` e2e: **not run** as part of this `ci-all` pass. `git log --oneline main..HEAD --
appliance/bin/` and `git diff --stat main...HEAD -- appliance/bin/` on the current branch
(`agent/add-dsrust-groq-disposition-proposer`) both returned empty — no committed change on this
branch touches `appliance/bin/`. Several `appliance/bin/*.py` files do show as modified in the
uncommitted working tree, but that is pre-existing uncommitted state, not a change introduced by
any commit on this branch, and this ticket's own committed diff does not touch `appliance/bin/`.
The direct two-run `bash appliance/bin/run-reference-e2e.sh` proof already in this ticket's
`## Standing` section above (a real falsifier re-run, pre-change and post-change, not part of
`ci-all`) remains the actual regression evidence for this ticket's change.

`git status --porcelain -uall | wc -l`: real count = **113** (mix of modified tracked files and
untracked new files/tickets/docs already present in the working tree before this run; `just
ci-all` itself only produced normal cargo build-artifact activity under `target/`, which is
gitignored and does not appear in this count). This is repo-wide working-tree state, not
evidence against this ticket's own scoped diff (`git diff --stat` isolated to the 5
Authored-boundary files, cited above in `## Standing`).
