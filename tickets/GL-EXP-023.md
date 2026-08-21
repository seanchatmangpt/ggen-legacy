# GL-EXP-023 — Raise `appliance/bin`'s 5-file duplicated `exact_head()` out of an undifferentiated `"UNKNOWN"` collapse

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Note on this pass's own saturation check (per this session's explicit
## instruction to grep broadly before proposing another instance of this
## pattern)

This repo's ticket corpus already carries four instances of the
undifferentiated-git-failure-collapse anti-pattern: `GL-ERRC-019`
(`EXECUTED`, `tools/v26.8.1/src/coverage_projection.rs::exact_head`),
`GL-EXP-005` (`tools/v26.8.1/src/bin/subsystem_verifier.rs::fresh_git_head`),
`GL-EXP-011` (`tools/v26.8.20/observe_contract.py::git_head`), and
`GL-EXP-019` (`tools/v26.8.1/src/main.rs::git_provenance::run`).
`GL-EXP-015` is a **different** class (an `except Exception: pass` around a
loop body appending to an accumulator list in
`appliance/bin/verify-standing-portfolio.py`, not a single return-value
sentinel around a `git`/subprocess call) -- confirmed this session by
re-reading its own text, which explicitly names itself "a structurally
different manifestation ... not a single return value."

Before drafting this ticket, this session ran a repo-wide search
(`grep -h "^def " appliance/bin/*.py | sort | uniq -c | sort -rn`) rather
than assuming the pattern was exhausted, and found a real, previously
unticketed **fifth** instance -- not in `tools/v26.8.1` or
`tools/v26.8.20` (where all four prior instances live), but in
`appliance/bin`, and duplicated across five files simultaneously rather
than existing once. This is reported transparently as a real 5th/6th-order
recurrence, not silently piled on: it is included here specifically
because (a) it is a genuinely new subsystem (Python, `appliance/bin`, the
same subsystem `README.md`'s own standing table calls the `ALIVE`
"Verifier Appliance reference" rail) none of the four prior tickets'
Authored boundaries touch, and (b) it is simultaneously live evidence for
this repo's separate, also-real `appliance/bin` duplicated-helper pattern
(`GL-EXP-013`/`GL-EXP-017`), which did not catch this specific function.

## Outcome

Five files in `appliance/bin` each independently define `exact_head(root)`,
and all five collapse the two causally distinct failure modes of `git
rev-parse HEAD` (spawn failure and non-zero exit) into the identical
literal `"UNKNOWN"`, indistinguishable from each other or from any future
third failure cause. Confirmed this session by direct read of each
definition:

Four files (`build-document-evidence-index.py`,
`build-subsystem-evidence.py`, `verify-subsystem-evidence.py`,
`verify-crown.py`) share one byte-identical body (`md5` of each
`^def exact_head` block, 4 files: `cb52cbd91200512555e28e1637311e9d`):

```python
def exact_head(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True
    )
    return completed.stdout.strip() if completed.returncode == 0 else "UNKNOWN"
```

`observe-project.py` uses a differently-shaped but behaviorally identical
variant (`md5` of its block: `d5ca5ef24598619a6bb3601d82a7de6e`, a real
divergence, not a duplicate of the above):

```python
def exact_head(root: Path) -> str:
    code, out, _ = run(root, ["git", "rev-parse", "HEAD"])
    return out.strip() if code == 0 else "UNKNOWN"
```

Neither shape catches `FileNotFoundError` (or, for the `run()`-wrapper
variant, whatever exception its own internal `subprocess` call can raise)
if `git` is not on `PATH` -- `subprocess.run([...], capture_output=True,
text=True)` with no `check=True` does not raise on a non-zero exit, but it
*does* raise uncaught if the executable itself cannot be spawned, meaning
a missing `git` binary crashes these five scripts' `main()` outright
rather than degrading to `"UNKNOWN"`. And a real non-zero exit (e.g. `root`
not being inside a git working tree) collapses to the identical
`"UNKNOWN"` string a caller cannot distinguish from any other failure
cause -- the same anti-pattern `GL-ERRC-019`/`GL-EXP-005`/`GL-EXP-011`/
`GL-EXP-019` each treat as the defect worth fixing in their own target
files.

**This is not dead code -- confirmed this session it feeds real,
load-bearing compliance checks.** Every one of the five call sites
(`exact_head(` grepped in each file, this session) either writes the
result directly into an emitted report's `"exact_source_head"` field
(`build-document-evidence-index.py:57`, `build-subsystem-evidence.py:246`,
`observe-project.py:101`) or compares it against a manifest-recorded value
to gate a pass/fail check:

- `appliance/bin/verify-crown.py:90-99` -- `head = exact_head(root)`, then
  the `"exact-source-head"` check's `passed` field is
  `verifier_report.get("exact_source_head") == head and
  observed_coverage.get("exact_source_head") == head`. This is the exact
  check that feeds `run-reference-e2e.sh`'s crown-standing output, which
  `README.md:14`'s "Verifier Appliance reference: `ALIVE`" claim cites
  ("crown green") as its basis.
- `appliance/bin/verify-subsystem-evidence.py:147-151` -- the same
  shape: `head = exact_head(root)`, `"exact-source-head"` check's
  `passed` field is `manifest.get("exact_source_head") == head`.

If `exact_head()` collapses a real spawn/exit failure to `"UNKNOWN"` in one
of these two comparison call sites, and the compared-against manifest/
report value also happens to be (or was itself independently generated as)
`"UNKNOWN"` for an unrelated reason, the `"exact-source-head"` check would
report `passed: true` for the wrong reason -- a false positive
indistinguishable, from the check's own output, from a genuine matching
commit. This is the identical false-positive/false-negative ambiguity
class `GL-ERRC-019`'s own Outcome section names as its justification for
fixing the Rust-side `exact_head()`.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below. Four of
this ticket's five target files -- `build-document-evidence-index.py`,
`build-subsystem-evidence.py`, `verify-subsystem-evidence.py`,
`verify-crown.py` -- are also claimed by `GL-EXP-013` (`NOT_STARTED`) for
`sha256_file()`/`read_json()` consolidation into `appliance/bin/_shared.py`.
Confirmed this session via `grep -n "^def sha256_file\|^def read_json\|^def
exact_head"` on each of the four: in every file, `exact_head` is defined
at a line immediately *after* `sha256_file`/`read_json` -- a disjoint,
adjacent function region in the same file, not an overlapping one. This
overlap is disclosed in `tickets/OVERLAPS.md`'s new
`appliance/bin (exact_head vs. sha256_file/read_json)` section, added by
this ticket -- see Hard Law 5.)

```text
appliance/bin/build-document-evidence-index.py   # exact_head() body only
appliance/bin/build-subsystem-evidence.py        # exact_head() body only
appliance/bin/observe-project.py                 # exact_head() body only
appliance/bin/verify-subsystem-evidence.py       # exact_head() body only
appliance/bin/verify-crown.py                    # exact_head() body only
tickets/GL-EXP-023.md
tickets/OVERLAPS.md   # add appliance/bin exact_head vs. sha256_file/read_json section
```

No change to `sha256_file`, `read_json`, `write_json`, `tree_inventory`,
`tree_digest`, `canonical`, or any other function in any of the five
files -- this ticket's diff is scoped to `exact_head`'s body in each file
only. No change to `appliance/bin/verify-standing-portfolio.py`
(`GL-EXP-015`'s target, a different file and a different anti-pattern),
`appliance/bin/transparency-log.py` (`GL-ERRC-010`'s target),
`appliance/bin/build-standing-portfolio.py` (`GL-RECEIPT-007`'s target,
and not one of the five `exact_head`-carrying files -- confirmed via
`grep -l "^def exact_head" appliance/bin/*.py`), `tools/v26.8.1/src/
coverage_projection.rs` (`GL-ERRC-019`, `EXECUTED`), `tools/v26.8.1/src/
bin/subsystem_verifier.rs` (`GL-EXP-005`), `tools/v26.8.20/
observe_contract.py` (`GL-EXP-011`), or `tools/v26.8.1/src/main.rs`
(`GL-EXP-019`) -- five distinct, already-claimed files this ticket does
not touch.

## Hard laws

1. A real git repo where `git rev-parse HEAD` genuinely succeeds must
   return the identical trimmed SHA string as before this ticket, in all
   five files -- the happy path's observable value and type (`str`) do
   not change.
2. Spawn failure (missing `git` binary / `FileNotFoundError` or
   equivalent) and non-zero exit must each be distinguishable from one
   another and from the happy path in the returned value -- no two of the
   3 cases may collapse back into an identical string, in any of the five
   files.
3. A missing `git` executable must not crash any of the five scripts'
   `main()` with an uncaught traceback -- it must be caught and mapped to
   its own distinguishable value, matching the discipline
   `GL-EXP-011`'s Hard Law 3 already establishes for the Python side
   ("the `except Exception` catch-all is not simply deleted -- any
   exception type ... must still be caught and mapped to its own
   distinguishable value ... rather than propagating uncaught").
4. Every call site's current behavior for the happy path is preserved
   exactly: `"exact_source_head"` fields in emitted reports still receive
   the real SHA string on success; the `"exact-source-head"` checks in
   `verify-crown.py`/`verify-subsystem-evidence.py` still pass for a
   genuine match. Only the *value* on failure changes from the collapsed
   `"UNKNOWN"` to a cause-distinguishing string.
5. `tickets/OVERLAPS.md` gains a new section for this ticket's overlap
   with `GL-EXP-013` on the four shared files, naming both tickets and
   the disjoint function regions each claims -- per this ticket's own
   Authored-boundary note above.
6. `git diff --stat` after this ticket touches only the five named
   `appliance/bin/*.py` files, `tickets/GL-EXP-023.md`, and
   `tickets/OVERLAPS.md`.

## Falsifiers

- After the fix, a corrupted `PATH` (spawn failure) or a real non-git
  temp directory (non-zero exit) still produces the bare literal
  `"UNKNOWN"` indistinguishable from the other cause, in any of the five
  files.
- After the fix, a missing `git` binary crashes any of the five scripts'
  `main()` with an uncaught exception instead of a caught, distinguishable
  status.
- The happy-path SHA string returned for a real git repo's real `HEAD`
  changes value or trimming behavior in any of the five files as a side
  effect of this fix.
- `verify-crown.py`'s or `verify-subsystem-evidence.py`'s
  `"exact-source-head"` check's `passed` boolean for a genuine, real
  matching commit changes as a side effect of this fix.
- `git diff --stat` after this ticket touches any file outside the five
  named `appliance/bin/*.py` files, `tickets/GL-EXP-023.md`, and
  `tickets/OVERLAPS.md`.

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the fix lands, not yet-observed outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the collapse in all 5 files before touching anything:
for f in build-document-evidence-index build-subsystem-evidence observe-project \
         verify-subsystem-evidence verify-crown; do
  echo "--- $f.py ---"
  grep -A6 "^def exact_head" "appliance/bin/$f.py"
done

# After the fix, confirm the failure causes are distinguishable with a
# real subprocess invocation (no mocked subprocess return values, per
# this account's Chicago-style testing discipline) -- e.g. a real
# temporary non-git directory for the non-zero-exit case, and a real
# corrupted PATH for the spawn-failure case:
python3 -c "
import sys, tempfile
sys.path.insert(0, 'appliance/bin')
import importlib.util
spec = importlib.util.spec_from_file_location('verify_crown', 'appliance/bin/verify-crown.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from pathlib import Path
with tempfile.TemporaryDirectory() as d:
    print(m.exact_head(Path(d)))
"

# Regression proof, the pre-existing black-box e2e harness (already used
# by GL-EXP-013/GL-EXP-017 as this subsystem's own regression check):
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

git diff --stat   # only the 5 named files + tickets/GL-EXP-023.md + tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `grep -h "^def " appliance/bin/*.py | sort | uniq -c | sort -rn` this
  session: `5 def exact_head(root: Path) -> str:` alongside the
  already-ticketed `5 def sha256_file(...)`/`5 def sha256_file(path):`,
  `5 def read_json(path): ...`, `5 def write_json(path,obj):`, and two
  further-duplicated-but-out-of-scope helpers (`tree_inventory`,
  `tree_digest`, `canonical`) this ticket does not claim.
- `grep -l "^def exact_head" appliance/bin/*.py` this session: exactly
  `build-document-evidence-index.py`, `build-subsystem-evidence.py`,
  `observe-project.py`, `verify-subsystem-evidence.py`,
  `verify-crown.py` -- five files, confirmed not to include
  `build-standing-portfolio.py`, `transparency-log.py`, or
  `verify-standing-portfolio.py` (the three files claimed by
  `GL-ERRC-010`/`GL-RECEIPT-007`/`GL-EXP-015` respectively).
- Per-file `grep -A6 "^def exact_head" <file> | md5` this session:
  4 identical hashes (`cb52cbd91200512555e28e1637311e9d`) for
  `build-document-evidence-index.py`, `build-subsystem-evidence.py`,
  `verify-subsystem-evidence.py`, `verify-crown.py`; one distinct hash
  (`d5ca5ef24598619a6bb3601d82a7de6e`) for `observe-project.py`'s
  `run()`-wrapper variant -- confirming two behaviorally-identical but
  textually-distinct implementations, both collapsing to `"UNKNOWN"`.
- `grep -n "exact_head(" <file>` per file this session: 2 occurrences
  each (the `def` plus one call site), confirming live use, not dead
  code, in all five files.
- Direct `Read` of `appliance/bin/verify-crown.py:85-99` this session:
  confirms `head = exact_head(root)` at line 90 and the
  `"exact-source-head"` check's `passed` field comparing
  `verifier_report.get("exact_source_head")`/
  `observed_coverage.get("exact_source_head")` against `head`.
- Direct `Read` of `appliance/bin/verify-subsystem-evidence.py:142-151`
  this session: confirms the same shape --
  `manifest.get("exact_source_head") == head`.
- Direct `Read` of `README.md:14` this session: `Verifier Appliance
  reference | ALIVE | Ten assurance subsystems independently re-derived;
  crown green; replay matched; reference Release Admission true.` --
  confirming `verify-crown.py`'s check is the real basis for a real,
  currently-cited `ALIVE` claim.
- `grep -n "^def sha256_file\|^def read_json\|^def exact_head"` on each of
  the four `GL-EXP-013`-shared files this session: confirms `exact_head`'s
  definition line immediately follows `sha256_file`'s (and `read_json`'s,
  where present) in every case -- adjacent, disjoint regions, not
  overlapping ones.
- Direct `Read` of `tickets/GL-EXP-013.md`'s Authored boundary this
  session: confirms it claims `build-document-evidence-index.py`,
  `build-subsystem-evidence.py`, `verify-subsystem-evidence.py`,
  `verify-crown.py` (among six other files) for `sha256_file()`/
  `read_json()` consolidation, and never mentions `exact_head`.
- Direct `Read` of `tickets/GL-EXP-015.md`'s Outcome section this
  session: confirms its own explicit self-classification as "a
  structurally different manifestation" from the return-value-sentinel
  class, targeting a loop-body accumulator in
  `appliance/bin/verify-standing-portfolio.py` (not one of this ticket's
  five files).
- `grep -l "exact_head" tickets/GL-*.md` this session: `GL-ERRC-019.md`,
  `GL-EXP-005.md`, `GL-EXP-011.md` (mentions it only as a naming
  precedent, targets `observe_contract.py::git_head`, a different
  function), `GL-EXP-019.md` (mentions it as precedent, targets
  `main.rs::git_provenance::run`, a different function). None of the
  four targets any `appliance/bin/*.py` file.
- `grep -n "appliance/bin.*exact_head\|exact_head.*appliance" tickets/OVERLAPS.md`
  this session: zero matches -- no existing registry entry for this
  overlap.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
undifferentiated-collapse finding for `appliance/bin`'s five `exact_head()`
duplicates; the actual cause-distinguishing return shape (matching the
`STALE_REFERENCE_UNVERIFIABLE:<CAUSE>`-style convention `GL-ERRC-011`/`014`
established on the Python side) and its Chicago-style real-subprocess test
coverage have not been implemented, and the `tickets/OVERLAPS.md` edit
this ticket's own Hard Law 5 requires has not been made.
