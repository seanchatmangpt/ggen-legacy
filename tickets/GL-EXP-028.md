# GL-EXP-028 — Add real Chicago-style test coverage for `scripts/verify_lsp_contract.py`, the sole `verify_*.py` script real CI actually gates on

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`scripts/verify_lsp_contract.py` (137 lines, read in full this session) is
the independent receiver verifier for the ggen-manufactured LSP contract. It
is the sole `verify_*.py` script actually invoked by real, current CI --
`.github/workflows/ci.yml:41`'s "Verify received generated contract" step
runs `python3 scripts/verify_lsp_contract.py` directly, gating every PR --
and it has zero dedicated test file. Its logic is non-trivial and directly
decides CI pass/fail: a `rust_constants()` regex extractor that parses
`pub const NAME: &[&str] = &[...]` arrays out of `src/generated_contract.rs`
(line 21), three list-equality drift checks between the received JSON
contract and those extracted Rust constants (`GENERATED_METHOD_DRIFT`/
`GENERATED_SURFACE_DRIFT`/`GENERATED_DIAGNOSTIC_DRIFT`, lines 56-61), a
`HANDLER_ABSENT` regex check confirming each contract method's
`legacy_handler` has a matching `async fn` in `src/backend.rs` (lines
63-68), `CAPABILITY_ABSENT`/`SURFACE_ABSENT`/`DIAGNOSTIC_ABSENT` substring
checks against `src/capabilities.rs`/`src/analysis.rs`, and an
`AMBIENT_ACTUATION` forbidden-marker scan (`std::process::Command`,
`reqwest::`, `TcpStream`, `UdpSocket`, lines 96-100). A regression to any of
these -- a loosened regex, a flipped equality, a typo'd forbidden-marker
list -- could silently let a broken contract sync pass CI on every future
PR, or silently start failing a correct one, with nothing in the repo's own
test suite to catch either direction today.

More broadly: of the 12 files in `scripts/*.py`, only the two already
targeted for outright elimination as fully orphaned dead code
(`scripts/ci_errc.py` -> `GL-EXP-009`, `scripts/ci_step_receipt.py` ->
`GL-EXP-021`, both `NOT_STARTED`) have a `scripts/tests/test_*.py`
counterpart. The 10 live, CI/admission-relevant scripts --
`verify_docs.py`, `verify_foundry_bootstrap.py`,
`verify_foundry_provenance.py`, `verify_offline_transport.py`,
`verify_lsp_contract.py`, `verify_ggen_v26_8_1_migration.py`,
`verify_ggen_create_bundle.py`, `autonomic_finish.py`,
`verify_autonomic_finish.py`, `run_autonomic_crown.py` -- have none. This
ticket scopes to `verify_lsp_contract.py` alone: it is the single instance
of this gap with a real, current, always-on CI consequence (every other
`verify_*.py` is either unwired from `ci.yml` entirely or invoked only from
a non-gating workflow), so it is the highest-leverage single file to fix
first; the other 9 remain an open gap this ticket does not close.

One correction against the candidate-item phrasing this ticket was drafted
from: the script computes a `sha256` digest per required source file into a
`source_manifest` dict (lines 102-105) that is included in the JSON report
output, but it does **not** compare that digest against any stored/expected
value anywhere in the script -- there is no `sha256 digest comparison`
logic to test, only a digest computation. This ticket's coverage targets
the digest computation reaching a stable, correct value for a known fixture
(a real assertion), not a comparison path that does not exist in the
source.

**Verified this session -- CI wiring and file inventory:**

- `git rev-parse HEAD` -- `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- `grep -n "verify_lsp_contract\|verify_docs\|verify_foundry\|verify_offline\|verify_ggen\|autonomic" .github/workflows/ci.yml`
  -- real output: exactly one hit, `41:        run: python3
  scripts/verify_lsp_contract.py`. `sed -n '1,60p' .github/workflows/ci.yml`
  confirms this is the "Verify received generated contract" step (the
  second step in the single `verify` job, right after exact-head admission
  and before the Rust toolchain install/fmt/check/clippy/test steps) -- the
  only `verify_*.py` script real CI invokes.
- `ls scripts/tests/` -- real output: `__pycache__`, `test_ci_errc.py`,
  `test_ci_step_receipt.py`. Exactly two test files.
- `for f in scripts/*.py; do base=$(basename "$f" .py); test -f
  "scripts/tests/test_${base}.py" || echo "NO TEST: $f"; done` -- real
  output lists all 10 remaining scripts, confirming zero test coverage for
  each: `autonomic_finish.py`, `run_autonomic_crown.py`,
  `verify_autonomic_finish.py`, `verify_docs.py`,
  `verify_foundry_bootstrap.py`, `verify_foundry_provenance.py`,
  `verify_ggen_create_bundle.py`, `verify_ggen_v26_8_1_migration.py`,
  `verify_lsp_contract.py`, `verify_offline_transport.py`.
- `find . -iname "*verify_lsp_contract*"` (repo-wide) -- real output: the
  script itself plus its identical copy inside 12 stale `.claude/worktrees/`
  checkouts (all pinned to the same branch state, not independent
  evidence) -- no test file anywhere under any path.
- Direct `Read` of `scripts/verify_lsp_contract.py` in full this session
  (137 lines) -- confirms the logic summarized in Outcome above: `sha256()`
  helper (lines 16-17), `rust_constants()` regex extractor (lines 20-24),
  `snake()` camel-to-snake helper (lines 27-28), the `verify()` function's
  required-file existence check / `MISSING:<path>` early exit (lines 37-40),
  three JSON-vs-Rust-constant list-equality checks (lines 56-61),
  `HANDLER_ABSENT` regex check (lines 63-68), capability/surface/diagnostic
  substring checks (lines 70-94), `AMBIENT_ACTUATION` forbidden-marker scan
  (lines 96-100), and the `source_manifest` sha256 computation with no
  downstream comparison (lines 102-105, 113).
- `grep -rn "sha256\|source_manifest" --include="*.py" --include="*.yml" --include="*.rs" .`
  (repo-wide, excluding the script's own file) -- no other file reads or
  compares `verify_lsp_contract.py`'s `source_manifest` output; it is
  reported, not checked, inside this script.

**Verified this session -- no existing ticket already covers adding tests
to this file or any of the other 9 live scripts:**

- `grep -iln "test coverage\|pytest\|unittest" tickets/GL-*.md` -- real
  output: `GL-ERRC-015`, `GL-EXP-004`, `GL-EXP-007`, `GL-ERRC-019`,
  `GL-EXP-015`, `GL-EXP-009`, `GL-EXP-020`, `GL-EXP-013`, `GL-EXP-024`,
  `GL-PLAN-002`, `GL-EXP-021`, `GL-VERIFY-006`. Cross-checked each hit
  against the 10 live script names
  (`grep -n "verify_lsp_contract\|verify_docs\.py\|verify_foundry\|verify_offline_transport\|verify_ggen_create_bundle\|verify_ggen_v26_8_1_migration\|autonomic_finish\.py\|run_autonomic_crown\|verify_autonomic_finish" <file>`
  for each): only `GL-EXP-020` (`NOT_STARTED`) mentions two of these names
  (`verify_docs.py`, `verify_foundry_bootstrap.py`), and only as *evidence*
  that a different, unrelated new script (`scripts/verify_ticket_overlaps.py`,
  a machine-checkable `tickets/OVERLAPS.md` admission gate) doesn't exist
  yet -- it does not propose adding tests to either script. `GL-EXP-009`
  hits only because it is the elimination ticket for `ci_errc.py`
  discussing the same `verify_*.py` family as context. No ticket proposes
  test coverage for `verify_lsp_contract.py` or any of the other 9 live
  scripts.
- `grep -n "verify_lsp_contract" tickets/GL-ERRC-011.md tickets/GL-EXP-009.md tickets/GL-LSP-001.md`
  (the only three tickets that mention the script's name at all) -- every
  hit is a citation/evidence reference (e.g. `GL-ERRC-011`'s own Authored
  boundary explicitly excludes it: "No other script ...
  `scripts/verify_lsp_contract.py` ... is touched"; `GL-EXP-009` cites it
  only as the CI step preceding the one it's eliminating; `GL-LSP-001` is
  the pre-consolidation runtime-admission ticket that cites running the
  script as one of its own acceptance commands). None claims the script or
  a test file for it as an Authored-boundary target.
- `grep -n "scripts/tests" tickets/GL-*.md tickets/OVERLAPS.md` -- every
  hit is inside `GL-EXP-009.md`/`GL-EXP-021.md` (their own
  `test_ci_errc.py`/`test_ci_step_receipt.py` deletions) or one incidental
  path-dump line inside `GL-AUTO-001.md`. No ticket claims
  `scripts/tests/test_verify_lsp_contract.py` (a file that does not yet
  exist) as an Authored-boundary path. Zero prior claimants -- no
  `tickets/OVERLAPS.md` entry is needed for this ticket's new file, matching
  `GL-EXP-021`'s own precedent for a zero-prior-claimant path.
- `python3 -m pytest scripts/tests/ -q` (run this session) -- real output:
  `9 passed in 0.49s`, confirming both existing test files are internally
  consistent and the repo's Python test tooling (`pytest`, already used by
  both existing `scripts/tests/test_*.py` files and by
  `planning/v26.8.7/tests/test_planning.py`) runs cleanly against
  `scripts/tests/` as a target today -- this ticket's new file slots into
  an already-working local test layout, it does not need to bootstrap one.
- `grep -n "pytest\|scripts/tests\|python3 -m unittest" justfile` -- zero
  matches; no `just` recipe runs `scripts/tests/` today (matching
  `GL-EXP-009`/`GL-EXP-021`'s own finding that their tests are likewise
  never CI-invoked) -- confirming this ticket's new test, once added, is
  runnable locally via `python3 -m pytest scripts/tests/test_verify_lsp_contract.py`
  but is not automatically added to CI by this ticket alone (see Hard Law
  4).

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
check there before assuming sole ownership of a path below. Confirmed this
session via `grep -n "scripts/tests" tickets/GL-*.md tickets/OVERLAPS.md`
and `grep -l "verify_lsp_contract" tickets/GL-*.md`: no existing entry, no
other ticket claims this path -- this ticket has sole, undisputed ownership
of the one new file below.)

```text
scripts/tests/test_verify_lsp_contract.py   # new file
tickets/GL-EXP-028.md
```

No change to `scripts/verify_lsp_contract.py` itself (this ticket adds
coverage of existing behavior; it does not alter that behavior), no change
to `.github/workflows/ci.yml`, `justfile`, or any other `scripts/*.py`
file (including `GL-EXP-009`/`GL-EXP-021`'s separate, already-admitted
`ci_errc.py`/`ci_step_receipt.py` targets).

## Hard laws

1. New test file only -- do not modify `scripts/verify_lsp_contract.py`'s
   own logic. If writing the tests surfaces a real bug in the script, name
   it in this ticket's own follow-up note and open a separate ticket for
   the fix; do not silently patch behavior inside a ticket scoped to
   coverage.
2. Chicago style, matching this repo's own two existing
   `scripts/tests/test_*.py` precedents (`test_ci_errc.py`,
   `test_ci_step_receipt.py`, both independently confirmed this session to
   be zero-mock via `grep -c "Mock\|mock\.\|monkeypatch\|patch("`): drive
   the real script as a real subprocess
   (`subprocess.run([sys.executable, str(SCRIPT), ...])`) against real
   fixture files written to a real temporary directory on disk (a fixture
   `authority/lsp-contract.json`, `src/generated_contract.rs`,
   `src/backend.rs`, `src/capabilities.rs`, `src/analysis.rs` tree, passed
   via the script's own `--root` argument), and assert on the real,
   returned JSON report's fields (`standing`, `findings`, `method_count`,
   etc.) -- no `unittest.mock`/`Mock`/`MagicMock`/`patch`/`monkeypatch`
   faking the script's file reads, `json.loads`, or regex matching.
3. Must cover at minimum, each as a real fixture tree driving a real run,
   not a description:
   - a fully-consistent fixture set reaching `"standing": "ALIVE"` with
     `"findings": []`;
   - a fixture where a contract method's `legacy_handler` has no matching
     `async fn NAME` in the fixture `backend.rs`, producing
     `HANDLER_ABSENT:<method>:<handler>` in `findings`;
   - a fixture where the JSON contract's `methods` (or `surfaces` or
     `diagnostics`) list differs from what `rust_constants()` extracts from
     the fixture `generated_contract.rs`, producing
     `GENERATED_METHOD_DRIFT` (or the corresponding `_SURFACE_DRIFT` /
     `_DIAGNOSTIC_DRIFT`) in `findings`;
   - a fixture tree missing one of the five required files, producing the
     `"standing": "BUILD_BROKEN"` early-exit path with a `MISSING:<path>`
     finding and no further checks attempted (lines 37-40).
4. Does not wire the new test file into `.github/workflows/ci.yml` or
   `justfile` -- adding local coverage and adding a CI/justfile invocation
   are separable concerns in this repo's own established precedent
   (`GL-EXP-009`/`GL-EXP-021` both found their existing test files real and
   passing but never CI-invoked, and neither ticket folds "wire it into
   CI" into its own scope). A follow-up wiring ticket, if wanted, is
   separate work.
5. `git diff --stat` after this ticket touches only
   `scripts/tests/test_verify_lsp_contract.py` and `tickets/GL-EXP-028.md`.

## Falsifiers

- `test -f scripts/tests/test_verify_lsp_contract.py` fails after this
  ticket executes (file was not created).
- `python3 -m pytest scripts/tests/test_verify_lsp_contract.py -v` does not
  pass cleanly.
- `grep -c "Mock\|mock\.\|monkeypatch\|patch(" scripts/tests/test_verify_lsp_contract.py`
  returns nonzero (a banned test double was used instead of a real
  subprocess + real fixture files).
- Any of the four Hard-Law-3 cases (ALIVE-pass, `HANDLER_ABSENT`, a
  `*_DRIFT` finding, `MISSING:<path>`/`BUILD_BROKEN`) is absent from the
  test file's actual assertions.
- `git diff --stat` after this ticket touches any file outside
  `scripts/tests/test_verify_lsp_contract.py` and `tickets/GL-EXP-028.md`
  (in particular, `scripts/verify_lsp_contract.py` itself, `.github/workflows/ci.yml`,
  or `justfile`).
- `python3 -m pytest scripts/tests/ -q` (the full directory, both old and
  new files) regresses below the pre-ticket `9 passed` baseline plus the
  new file's own tests.

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the test file lands, not yet-observed
outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
test -f scripts/tests/test_verify_lsp_contract.py && echo "UNEXPECTED: already exists"
grep -n "python3 scripts/verify_lsp_contract.py" .github/workflows/ci.yml

# After the new test file lands:
python3 -m pytest scripts/tests/test_verify_lsp_contract.py -v
python3 -m pytest scripts/tests/ -q   # full directory, confirm no regression
grep -c "Mock\|mock\.\|monkeypatch\|patch(" scripts/tests/test_verify_lsp_contract.py
git diff --stat   # must show only the new test file + tickets/GL-EXP-028.md

# Confirm the script itself was not altered:
git diff scripts/verify_lsp_contract.py   # must be empty

# Full local CI-equivalent proof the repo still builds/tests clean:
python3 scripts/verify_lsp_contract.py
cargo fmt --all -- --check
cargo check --all-targets --locked
cargo clippy --all-targets --locked -- -D warnings
cargo test --all-targets --locked
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` -- `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- `ls scripts/tests/` -- real output: `__pycache__`, `test_ci_errc.py`,
  `test_ci_step_receipt.py`.
- `ls scripts/*.py` -- real output: exactly 12 files (`autonomic_finish.py`,
  `ci_errc.py`, `ci_step_receipt.py`, `run_autonomic_crown.py`,
  `verify_autonomic_finish.py`, `verify_docs.py`,
  `verify_foundry_bootstrap.py`, `verify_foundry_provenance.py`,
  `verify_ggen_create_bundle.py`, `verify_ggen_v26_8_1_migration.py`,
  `verify_lsp_contract.py`, `verify_offline_transport.py`).
- `for f in scripts/*.py; do base=$(basename "$f" .py); test -f
  "scripts/tests/test_${base}.py" || echo "NO TEST: $f"; done` -- real
  output: all 10 non-`ci_errc`/non-`ci_step_receipt` scripts listed, zero
  test coverage confirmed for each.
- `sed -n '1,60p' .github/workflows/ci.yml` -- real output confirms line 41,
  `run: python3 scripts/verify_lsp_contract.py`, under the "Verify received
  generated contract" step name, the sole `verify_*.py` invocation in the
  file.
- Direct `Read` of `scripts/verify_lsp_contract.py` in full (137 lines) --
  confirmed every line reference cited in Outcome/Hard Law 3 above.
- `grep -rn "sha256\|source_manifest" --include="*.py" --include="*.yml" --include="*.rs" .`
  (excluding the script's own file) -- confirmed no downstream reader
  compares `source_manifest`; it is computed and reported only.
- `find . -iname "*verify_lsp_contract*"` -- real output: the script plus
  12 identical copies under stale `.claude/worktrees/` checkouts, no test
  file anywhere.
- `grep -iln "test coverage\|pytest\|unittest" tickets/GL-*.md` cross-
  checked against each hit's content this session -- no existing ticket
  proposes test coverage for `verify_lsp_contract.py` or the other 9 live
  `verify_*.py`/`autonomic_*.py` scripts; the one overlapping name-hit
  (`GL-EXP-020`) references two different script names only as evidence for
  an unrelated new-script ticket.
- `grep -n "verify_lsp_contract" tickets/GL-ERRC-011.md tickets/GL-EXP-009.md tickets/GL-LSP-001.md`
  -- all citation/evidence references, none an Authored-boundary claim on
  the script or a test file for it. `GL-ERRC-011`'s own text explicitly
  states `scripts/verify_lsp_contract.py` is not touched by that ticket.
- `grep -n "scripts/tests" tickets/GL-*.md tickets/OVERLAPS.md` -- confirmed
  zero prior claimants for `scripts/tests/test_verify_lsp_contract.py`;
  no `tickets/OVERLAPS.md` entry required (matching `GL-EXP-021`'s own
  precedent for a zero-prior-claimant new path).
- `python3 -m pytest scripts/tests/ -q` -- real output this session:
  `9 passed in 0.49s`, confirming the existing local pytest layout works
  cleanly today.
- `grep -n "pytest\|scripts/tests\|python3 -m unittest" justfile` -- zero
  matches, confirming neither existing test file is CI/justfile-invoked
  today (this ticket's new file inherits the same, unchanged status per
  Hard Law 4).

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the gap and
the coverage plan (every command above was re-run fresh this session); the
actual test file has not yet been written.
