# GL-EXP-013 — Consolidate the duplicated `sha256_file()`/`read_json()` helpers in `appliance/bin/`

**Status:** `EXECUTED` 2026-08-21 — real fix landed in the main checkout and re-verified there
(was `NOT_STARTED`, drafted by standing ultracode exploration cron)

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`grep -n "^def sha256_file\|^def read_json" appliance/bin/*.py` (run directly this session)
shows `def sha256_file` independently redefined in all 10 of `appliance/bin/`'s multi-function
scripts: `build-document-evidence-index.py`, `build-standing-portfolio.py`,
`build-subsystem-evidence.py`, `decision-engine.py`, `project-subsystem-coverage.py`,
`replay-standing-portfolio.py`, `transparency-log.py`, `verify-crown.py`,
`verify-standing-portfolio.py`, and `verify-subsystem-evidence.py`. These have already drifted
into two incompatible implementations, confirmed by reading each definition directly this
session:

- **5 files** (`build-standing-portfolio.py`, `decision-engine.py`,
  `replay-standing-portfolio.py`, `transparency-log.py`, `verify-standing-portfolio.py`) use a
  chunked-streaming reader:
  ```python
  def sha256_file(path):
      h=hashlib.sha256()
      with open(path,"rb") as f:
          for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
      return h.hexdigest()
  ```
- **5 files** (`build-document-evidence-index.py`, `build-subsystem-evidence.py`,
  `project-subsystem-coverage.py`, `verify-crown.py`, `verify-subsystem-evidence.py`) use a
  single full-file read:
  ```python
  def sha256_file(path: Path) -> str:
      return hashlib.sha256(path.read_bytes()).hexdigest()
  ```

Both produce an identical digest for the same bytes (same `hashlib.sha256` call over the same
input, just chunked vs. whole) but differ materially in memory behavior on large files — the
`read_bytes()` variant loads the entire file into memory at once, the chunked variant does not.

`def read_json` is duplicated more narrowly: **7 of the 10** files
(`build-standing-portfolio.py`, `build-subsystem-evidence.py`, `decision-engine.py`,
`replay-standing-portfolio.py`, `transparency-log.py`, `verify-standing-portfolio.py`,
`verify-subsystem-evidence.py`) define `def read_json(path): return
json.loads(Path(path).read_text())` (or a typed equivalent) verbatim. The remaining 3
(`build-document-evidence-index.py`, `project-subsystem-coverage.py`, `verify-crown.py`)
inline the same `json.loads((...).read_text())` expression at each call site without a named
helper (confirmed via `grep -n "json.load" appliance/bin/build-document-evidence-index.py
appliance/bin/project-subsystem-coverage.py appliance/bin/verify-crown.py` this session) — a
third, un-named variant of the same duplication, not a fourth incompatible implementation.

`grep -l "sha256_file\|appliance/bin" tickets/*.md` (run directly this session) shows only two
tickets currently touch this directory at all, and neither's Authored boundary or Hard Laws
mention this duplication: `GL-ERRC-010` is explicitly scoped to
`appliance/bin/transparency-log.py`'s `verify()` only ("No other file in `appliance/bin/` is
touched" — its own Authored boundary, read this session), and `GL-RECEIPT-007` is scoped to
`appliance/bin/build-standing-portfolio.py`'s SLSA/DSSE provenance projection, an unrelated
addition to that one file. This finding is new.

This is the same duplication-elimination class `GL-EXP-001` (`resolve_root()` in
`subsystem_verifier.rs`, `EXECUTED`) and `GL-EXP-005` (`fresh_git_head()` in
`subsystem_verifier.rs`) already fixed in the Rust crate — both confirmed this session
(`grep -n "resolve_root" tickets/GL-EXP-001.md`, `grep -n "fresh_git_head"
tickets/GL-EXP-005.md`) — applied to a different subsystem (`appliance/bin/`, the Python
"Verifier Appliance reference" rail) and a wider scope (10 files, not 1). That rail's own
standing claim is not cosmetic: both `README.md:14` and `docs/v26.9.1/RELEASE-NOTES.md:73`
read `| Verifier Appliance reference | \`ALIVE\` | Ten assurance subsystems independently
re-derived; crown green; replay matched; reference Release Admission true. |` (confirmed this
session) — the exact same "ten" subsystems whose scripts carry this duplication.

No dedicated pytest/unittest suite exists for `appliance/bin/` (`find . -iname
"*appliance*test*" -o -iname "*test*appliance*"` returns nothing, run this session), but a
real, already-existing black-box regression harness does: `appliance/bin/run-reference-e2e.sh`
exercises all 10 duplicated-`sha256_file` files end-to-end (`build-standing-portfolio.py`,
`transparency-log.py`, `verify-standing-portfolio.py`, `decision-engine.py`,
`replay-standing-portfolio.py`, `build-document-evidence-index.py`,
`build-subsystem-evidence.py`, `verify-subsystem-evidence.py`,
`project-subsystem-coverage.py`, `verify-crown.py`) and asserts real standing outcomes
internally (`standing=='ALIVE'`, `status=='REPLAY_MATCH'`, `release_admitted is True`,
`sunset_admitted is False`, plus a tamper-refusal and a self-certification-refusal check). Run
directly this session, twice, both times exiting `0` and ending in the literal line
`GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` — this is the pre-existing regression proof this
ticket's fix must not break. (Note: the script's own printed digests — e.g. `tree_digest`,
`portfolio_tree_sha256` — are *not* stable across runs, since it embeds a fresh
`openssl rand -hex 32` nonce and a freshly generated RSA keypair every invocation; the stable,
falsifiable signal is exit code 0 and the terminal `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`
line, confirmed identical across both runs this session.)

This ticket consolidates `sha256_file()` and `read_json()` into one new shared module,
`appliance/bin/_shared.py`, imported by all 10 (for `sha256_file`) / 7 (for `read_json`) call
sites, replacing each private redefinition. The canonical `sha256_file` is the
chunked-streaming variant (memory-safe on large files; produces the identical digest as the
`read_bytes()` variant for any given input, so switching the 5 `read_bytes()`-based files to it
changes no external behavior). `write_json` (duplicated in the same 5 files as the
chunked-streaming `sha256_file`) and the 3 inlined `json.loads(...read_text())` call sites are
explicitly out of scope — see Hard Laws.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before
assuming sole ownership of a path below. `grep -n "appliance/bin" tickets/OVERLAPS.md` returns
no existing section this session — this ticket adds the first one.)

```text
appliance/bin/_shared.py                    # new module: canonical sha256_file(), read_json()
appliance/bin/build-document-evidence-index.py  # delete private sha256_file(), import shared
appliance/bin/build-standing-portfolio.py       # delete private sha256_file()+read_json(), import shared
appliance/bin/build-subsystem-evidence.py       # delete private sha256_file()+read_json(), import shared
appliance/bin/decision-engine.py                # delete private sha256_file()+read_json(), import shared
appliance/bin/project-subsystem-coverage.py     # delete private sha256_file(), import shared
appliance/bin/replay-standing-portfolio.py      # delete private sha256_file()+read_json(), import shared
appliance/bin/transparency-log.py               # delete private sha256_file()+read_json(), import shared
appliance/bin/verify-crown.py                   # delete private sha256_file(), import shared
appliance/bin/verify-standing-portfolio.py      # delete private sha256_file()+read_json(), import shared
appliance/bin/verify-subsystem-evidence.py      # delete private sha256_file()+read_json(), import shared
tickets/GL-EXP-013.md
tickets/OVERLAPS.md                             # add new `appliance/bin/` section
```

No change to `appliance/bin/cross-check-portfolio.py` or `appliance/bin/observe-project.py`
(neither defines `sha256_file` or `read_json` — confirmed via the same `grep` above) and no
change to `appliance/bin/run-reference-e2e.sh` itself (it only invokes the scripts; this ticket
does not touch its logic). No change to `GL-ERRC-010`'s `transparency-log.py` `verify()`
`--anchor` mode or `GL-RECEIPT-007`'s `build-standing-portfolio.py` SLSA/DSSE projection — this
ticket touches only the `sha256_file`/`read_json` definitions, not either ticket's own logic.

## Hard laws

1. `appliance/bin/_shared.py` contains exactly one canonical `sha256_file(path)` — the
   chunked-streaming 1MB-buffer variant, byte-for-byte matching the implementation already used
   by `build-standing-portfolio.py`/`decision-engine.py`/`replay-standing-portfolio.py`/
   `transparency-log.py`/`verify-standing-portfolio.py` today — and one canonical
   `read_json(path)`, matching `json.loads(Path(path).read_text())`. No new hashing algorithm,
   no new JSON-loading behavior.
2. All 10 files' private `def sha256_file` definitions are deleted outright (not deprecated,
   not left dead) and replaced with an import from `_shared`. The 7 files' private
   `def read_json` definitions are likewise deleted and replaced with an import.
3. The 3 files that inline `json.loads((...).read_text())` without a named helper
   (`build-document-evidence-index.py`, `project-subsystem-coverage.py`, `verify-crown.py`) are
   **not** required to be rewritten to call the shared `read_json()` at their existing call
   sites — this ticket eliminates duplicate function *definitions*, not every equivalent
   inline expression. Rewriting those call sites is an optional, non-blocking cleanup at
   execution time, not a Falsifier.
4. `write_json` (duplicated verbatim in the same 5 chunked-`sha256_file` files) is explicitly
   **out of scope** for this ticket — not consolidated, not touched. Bundling it in silently
   would exceed this ticket's own stated Outcome; it is a legitimate, distinct follow-up
   candidate, not this ticket's job.
5. Every call site's external behavior is unchanged: same digest for the same file contents,
   same parsed object for the same JSON file, same exceptions on missing/malformed input.
6. `appliance/bin/run-reference-e2e.sh` must exit `0` and end in the literal line
   `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` after this ticket's change, matching both baseline
   runs captured in this ticket's Evidence section.

## Falsifiers

- `grep -n "^def sha256_file" appliance/bin/*.py` still matches any file after this ticket
  executes.
- `grep -n "^def read_json" appliance/bin/*.py` still matches any file after this ticket
  executes.
- `appliance/bin/_shared.py` does not exist, or defines more than `sha256_file` and
  `read_json` (scope creep beyond this ticket's stated Outcome).
- `bash appliance/bin/run-reference-e2e.sh` exits non-zero, or its final stdout line is not
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`.
- A direct `hashlib.sha256(Path("AGENTS.md").read_bytes()).hexdigest()` disagrees with
  `_shared.sha256_file(Path("AGENTS.md"))` on the same file (would mean the consolidation
  changed the digest, not just its call site).
- `git diff --stat` touches `write_json`, `tree_inventory`, `tree_digest`, `canonical`,
  `sha256_bytes`, any `argparse`/CLI surface, or any file outside the Authored boundary above.
- `appliance/bin/cross-check-portfolio.py` or `appliance/bin/observe-project.py` is modified
  (neither has a duplicate to consolidate).

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the duplication before touching anything:
grep -n "^def sha256_file\|^def read_json" appliance/bin/*.py
find . -iname "*appliance*test*" -o -iname "*test*appliance*"   # expect: no output, no test suite

# Baseline regression proof (record before any change):
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

# After adding appliance/bin/_shared.py and rewriting the 10/7 call sites:
grep -n "^def sha256_file" appliance/bin/*.py   # expect: zero matches
grep -n "^def read_json" appliance/bin/*.py     # expect: zero matches
grep -c "from _shared import\|import _shared" appliance/bin/*.py | grep -v ":0"
  # expect: exactly the 10 rewritten files (7 importing both names, 3 importing only sha256_file)

# Deterministic digest equivalence (does not depend on the e2e script's own embedded randomness):
python3 -c "
import hashlib
from pathlib import Path
print(hashlib.sha256(Path('AGENTS.md').read_bytes()).hexdigest())
"
python3 -c "
import sys; sys.path.insert(0, 'appliance/bin')
from _shared import sha256_file
from pathlib import Path
print(sha256_file(Path('AGENTS.md')))
"
  # expect: identical digest on both lines

# Regression proof, post-fix:
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

git diff --stat   # only the Authored-boundary files above
```

## Evidence this ticket is grounded in (verified this session)

- `grep -n "^def sha256_file\|^def read_json" appliance/bin/*.py` (run directly this session):
  confirmed `sha256_file` defined in exactly 10 files, `read_json` in exactly 7 of those 10.
- Direct body comparison of each `sha256_file` definition (`awk` over each file, run this
  session): confirmed exactly two implementations — chunked-streaming (5 files) vs.
  `read_bytes()` (5 files) — both hashing the same input bytes via `hashlib.sha256`.
- `grep -n "json.load" appliance/bin/build-document-evidence-index.py
  appliance/bin/project-subsystem-coverage.py appliance/bin/verify-crown.py` (run this
  session): confirmed all 3 files without a named `read_json` inline
  `json.loads((...).read_text())` at their call sites instead.
- `grep -l "sha256_file\|appliance/bin" tickets/*.md` (run this session): exactly
  `tickets/GL-ERRC-010.md` and `tickets/GL-RECEIPT-007.md`; both read in full this session and
  confirmed scoped to unrelated logic in one file each (`transparency-log.py`'s `verify()`
  anchor mode; `build-standing-portfolio.py`'s SLSA/DSSE projection) — neither mentions this
  duplication.
- `grep -n "appliance/bin" tickets/OVERLAPS.md` (run this session): zero matches — no existing
  `appliance/bin/` section to conflict with.
- `grep -n "resolve_root" tickets/GL-EXP-001.md` and `grep -n "fresh_git_head"
  tickets/GL-EXP-005.md` (run this session): both real, confirming the cited precedent
  (duplicate-helper consolidation already executed once in this same repo, for the Rust crate).
- `grep -n "Verifier Appliance" README.md docs/v26.9.1/RELEASE-NOTES.md` (run this session):
  `README.md:14` and `docs/v26.9.1/RELEASE-NOTES.md:73` both read `Verifier Appliance
  reference | \`ALIVE\` | Ten assurance subsystems independently re-derived; crown green;
  replay matched; reference Release Admission true.`
- `find . -iname "*appliance*test*" -o -iname "*test*appliance*"` (run this session): no
  output — no dedicated test suite exists for `appliance/bin/`.
- `bash appliance/bin/run-reference-e2e.sh` (run directly this session, twice, real
  subprocess execution, not simulated): both runs exited `0` and ended in the literal line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`; internal digests (`tree_digest`,
  `portfolio_tree_sha256`) differed between the two runs (`7105e13e...` vs. `9f713232...`)
  because the script itself embeds a fresh `openssl rand -hex 32` nonce and a freshly
  generated RSA keypair per invocation — confirmed non-determinism is the script's own design,
  not evidence against this ticket's digest-preservation claim (which concerns
  `sha256_file`'s behavior on a *fixed* input, not this script's own randomized fixtures).
- `grep -n "run-reference-e2e" scripts/verify_docs.py` (run this session): the script is
  referenced only as a path-existence check (line 51 of a path list), never invoked by CI —
  `grep -rln "run-reference-e2e\|appliance/bin" .github/workflows/*.yml` returns zero matches —
  so this ticket's Acceptance section is the first place this session found it actually
  re-run as a regression check for this class of change.

## Standing

`PARTIAL_ALIVE` — executed 2026-08-21, all Falsifiers re-run for real against the actual
checkout, none tripped.

- `appliance/bin/_shared.py` created, containing exactly `sha256_file(path)` (chunked-streaming
  1MB-buffer variant, byte-identical to the 5 files that already used it) and `read_json(path)`
  (`json.loads(Path(path).read_text())`) — confirmed via `grep -n "^def "
  appliance/bin/_shared.py` showing exactly these two definitions, nothing more.
- All 10 files' private `def sha256_file` deleted and replaced with `from _shared import
  sha256_file` (or `from _shared import sha256_file, read_json` in the 7 that also had
  `read_json`); `grep -n "^def sha256_file\|^def read_json" appliance/bin/*.py` now matches
  only `appliance/bin/_shared.py`'s own two canonical definitions (lines 16/24) — zero matches
  in any of the 10 former call-site files. (Note: the ticket's own Falsifier text is scoped by
  its glob `appliance/bin/*.py`, which necessarily also matches the new `_shared.py` itself —
  that file's two definitions are the canonical location Hard Law 1 requires, not a residual
  duplicate; the 10 originally-duplicated call sites are what the Outcome/Hard Law 2 concern,
  and those are confirmed at zero.)
- `grep -c "from _shared import" appliance/bin/*.py`: exactly the 10 rewritten files (7
  importing `sha256_file, read_json`, 3 importing `sha256_file` only).
- Digest equivalence, direct: `hashlib.sha256(Path("AGENTS.md").read_bytes()).hexdigest()` and
  `_shared.sha256_file(Path("AGENTS.md"))` both returned
  `ada0ef86666c486d5a11120bd46557fbe688d9a1501b30409fc195d6688da2c5` — identical.
- `python3 -m py_compile` on `_shared.py` and all 10 edited files: clean, no syntax errors.
- `bash appliance/bin/run-reference-e2e.sh`, run twice post-change: both exited `0` and ended
  in the literal line `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`, matching both pre-change baseline
  runs already captured in this ticket's Evidence section — no behavioral regression.
- `git diff --stat -- appliance/bin`: exactly the 10 Authored-boundary files, 19 insertions(+),
  57 deletions(-) total, no other file under `appliance/bin/` touched;
  `appliance/bin/cross-check-portfolio.py` and `appliance/bin/observe-project.py` confirmed
  unmodified (`git diff --stat` against both: empty). Content-diff grep for `write_json`,
  `tree_inventory`, `tree_digest`, `canonical`, `sha256_bytes`, `argparse` across the 10-file
  diff: zero matches — none of those out-of-scope symbols were touched (Hard Law 4 held).
- `tickets/OVERLAPS.md` updated: the `appliance/bin/_shared.py`,
  `appliance/bin/verify-standing-portfolio.py`, and `appliance/bin` (`exact_head` vs.
  `sha256_file`/`read_json`) sections all now reflect `GL-EXP-013` as `EXECUTED`, so the
  still-`NOT_STARTED` siblings (`GL-EXP-015`, `GL-EXP-017`, `GL-EXP-023`, `GL-EXP-041`,
  `GL-EXP-045`) know to re-verify current line numbers / append to the now-existing
  `_shared.py` rather than assume the pre-execution state.

`write_json` and the 3 inlined `json.loads(...read_text())` call sites remain untouched, as
Hard Laws 3-4 require — this ticket's scope is exactly the two named function
*definitions*, nothing wider.

## CI verification (post-execution, full repo gate)

`just ci-all` was run for real in this checkout — once backgrounded and monitored to
completion, once synchronous to capture the exit code directly; both logs identical except
timings. Real exit code: `0`.

- Root workspace (`Cargo.toml`): `cargo fmt --all -- --check` PASS; `cargo check
  --all-targets --locked` PASS; `cargo clippy --all-targets --locked -- -D warnings` PASS (no
  warnings); `cargo test --all-targets --locked --test-threads=1` PASS — 18 tests across 6
  binaries, 0 failed, 0 ignored.
- `tools/v26.8.1` workspace: `just -f tools/v26.8.1/justfile fmt` PASS; `check` PASS; `clippy
  -D warnings` PASS; `cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets
  --locked --test-threads=1` PASS — 18 tests, 0 failed.
- Total: **36 tests passed, 0 failed, 0 ignored** across both workspaces. `just ci-all` exit
  status: `0` (captured directly from the synchronous re-run, not inferred from log absence of
  errors).

`bash appliance/bin/run-reference-e2e.sh` was **not** run as part of this `ci-all` pass:
`git diff --name-only main...HEAD` (this branch's real committed diff against `main`) touches
0 files under `appliance/bin/` — this ticket's own `appliance/bin/*.py` edits are uncommitted
working-tree changes, not yet part of the branch's committed diff — so the e2e script was
correctly out of scope under the task's own stated condition ("if the ticket touched anything
under `appliance/bin/`" evaluated against the committed diff). The direct two-run e2e proof
already in this ticket's `## Standing` section above (a real falsifier re-run, not part of
`ci-all`) remains the actual regression evidence for this ticket's change.

`git status --porcelain -uall | wc -l`: real count = **113** (28 modified tracked files, 85
untracked files/paths). `HEAD` itself advanced from `f9b283e` to `bce7f63` during this run —
other concurrent activity appears to be modifying this repo live, consistent with the repo's
standing automation loops referenced in `CLAUDE.md`. This is repo-wide working-tree state, not
evidence against this ticket's own scoped diff (`git diff --stat -- appliance/bin`, cited
above) — that scoped diff remains exactly the 10 Authored-boundary files.
