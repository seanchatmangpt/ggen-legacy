# GL-EXP-009 — Eliminate the fully orphaned `scripts/ci_errc.py` CI-lane router

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`scripts/ci_errc.py` (350 lines) is a changed-file-to-CI-lane router and
"ERRC 80/20" fast-admission gate. It is invoked by nothing in the real,
current CI topology, and its routing table (`LANE_RULES`) encodes a
pre-consolidation, eight-workflow CI shape that no longer exists. This
ticket eliminates the script and its dedicated test file outright, rather
than rewiring the table to the current topology, because the current
topology (a single monolithic `ci.yml` that always runs everything) has no
per-lane routing problem left for this script to solve.

**Verified this session — not wired into anything real:**

- `grep -rn "ci_errc" .github/workflows/*.yml justfile
  tools/v26.8.1/justfile` — zero matches. No workflow step, no `just`
  recipe anywhere in the repo invokes `scripts/ci_errc.py`.
- `grep -rln "ci_errc" .` (repo-wide, excluding `.git/` and worktree
  checkouts) finds exactly four files: `scripts/ci_errc.py` itself,
  `scripts/tests/test_ci_errc.py` (its own dedicated test), and two
  ticket files (`tickets/GL-AUTO-001.md`, `tickets/GL-EXP-006.md`) — no
  workflow, no `justfile`, no other script references it.
- `grep -rn "pytest|test_ci_errc" .github/workflows/*.yml justfile
  tools/v26.8.1/justfile` — zero matches. `test_ci_errc.py` itself is
  never invoked by any wired CI step either; the entire subtree
  (`scripts/ci_errc.py` + `scripts/tests/test_ci_errc.py`, 416 lines
  total: `wc -l` this session) is dead weight, not merely unwired from one
  entry point.
- `grep -rln "errc-fast" .` (repo-wide, same exclusions) — the only hits
  are `scripts/ci_errc.py` itself (its own `--report` default path and
  self-describing `replay.command` string), `tickets/GL-EXP-006.md`
  (narrating this same finding), and `tools/v26.8.1/draft-candidates.json`
  (historical mining data describing a commit that deleted a workflow, not
  asserting the router runs today). No other script, workflow, or doc
  consumes `evidence/ci/errc-fast.json`, the report this router produces —
  confirming there is no downstream reader whose removal this ticket would
  break.

**Verified this session — its routing table encodes a retired topology:**

- `grep -n "LANE_RULES|\.yml" scripts/ci_errc.py` shows `LANE_RULES` cites
  five `.github/workflows/*.yml` files: `verify-docs.yml` (line 46),
  `gl-lsp-001-runtime.yml` (line 73), `autonomic-crown.yml` (line 86),
  `cyberpunk-tv-replay.yml` (line 94), `nasa-dark-mode-replay.yml`
  (line 102).
- `ls .github/workflows/` — real output this session: only `ci.yml` and
  `planning-v26-8-7.yml` exist. All five cited files are missing.
- `git log --oneline | grep 60d3826` — `60d3826 ci: rebuild CI around
  contract and real LSP execution`, the real commit
  `tickets/GL-EXP-006.md` already identified (and this ticket
  independently re-confirms via the same command) as the one that deleted
  the eight-workflow, per-lane topology `ci_errc.py`'s `LANE_RULES` still
  encodes, consolidating everything into the current single `ci.yml`.
- `cat .github/workflows/ci.yml` (read in full this session, 73 lines) —
  the real, current CI is one job (`verify`) that unconditionally runs
  exact-head admission, `verify_lsp_contract.py`, `cargo fmt`/`check`/
  `clippy`/`test` (all targets, every PR), and emits its own
  `evidence/ci/receipt.json`. It has no per-lane conditionality at all —
  every check listed in `ci_errc.py`'s `LANE_RULES` comment-table already
  runs on every PR regardless of which files changed. The fine-grained
  "only run the heavy lane if lane-owned files changed" problem
  `ci_errc.py` was built to solve does not exist in the current topology,
  because the current topology chose "run everything, always" instead of
  lane-conditional execution. There is nothing left for the router to
  route to.
- The individual verifier scripts `ci_errc.py` shells out to
  (`scripts/verify_docs.py`, `scripts/verify_lsp_contract.py`, and six
  others named in its `LANE_RULES`/`main()` body) all independently exist
  on disk (`for f in scripts/verify_docs.py
  scripts/verify_foundry_provenance.py scripts/verify_foundry_bootstrap.py
  scripts/verify_offline_transport.py
  scripts/verify_ggen_v26_8_1_migration.py scripts/verify_lsp_contract.py
  scripts/autonomic_finish.py scripts/verify_autonomic_finish.py
  scripts/run_autonomic_crown.py; do test -f "$f" && echo EXISTS || echo
  MISSING; done` — real output this session: all nine `EXISTS`) and
  `ci.yml` already calls `scripts/verify_lsp_contract.py` directly
  (`.github/workflows/ci.yml:41`) without going through `ci_errc.py`.
  Eliminating the router does not touch any verifier it used to call —
  those scripts are independent, already-referenced-elsewhere files, none
  of which are in this ticket's Authored boundary.

**This finding was already surfaced, and deliberately deferred, by
`tickets/GL-EXP-006.md`.** That ticket's Hard Law 4 and "Additional real
evidence found this session" section identify the same orphaned script and
the same five stale citations, and explicitly frame resolving them as
out of its own scope: `"a distinct, larger scope than a prose-citation
fix, and arguably an eliminate-quadrant question about the orphaned
script itself rather than a reduce-quadrant citation fix. Left as a named
follow-on, not silently dropped."` This ticket is that named follow-on,
re-verified fresh this session (every grep/ls/read above was re-run now,
not copied from `GL-EXP-006.md`'s prior output).

`grep -l "ci_errc" tickets/*.md` — real output this session:
`tickets/GL-AUTO-001.md`, `tickets/GL-EXP-006.md`. Direct inspection of
the `GL-AUTO-001.md` hit (`grep -n "ci_errc" tickets/GL-AUTO-001.md`,
line 110) shows it is one bare filename inside a giant single-line
`REFUSED:FORBIDDEN_DIFF:` comma-separated path dump from an unrelated
acceptance-command run — not a substantive Authored-boundary claim on the
file, the same pattern `GL-EXP-006.md` itself already documented for an
analogous tangential hit in the same ticket. No ticket in the corpus other
than `GL-EXP-006.md` (which defers) and this one owns
`scripts/ci_errc.py` or `scripts/tests/test_ci_errc.py`.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
check there before assuming sole ownership of a path below. `grep -n
"ci_errc" tickets/OVERLAPS.md` this session returns zero matches — neither
`scripts/ci_errc.py` nor `scripts/tests/test_ci_errc.py` has an existing
overlap registry entry, so this ticket has sole, undisputed ownership of
both paths.)

```text
scripts/ci_errc.py              # deleted in full
scripts/tests/test_ci_errc.py   # deleted in full
tickets/GL-EXP-009.md
```

No change to `.github/workflows/ci.yml`, `justfile`,
`governance/production-gaps.md`, or any of the nine verifier scripts
`ci_errc.py` used to shell out to — none of them reference `ci_errc.py` and
none of them are touched by removing it (see Hard Law 3). No change to
`tickets/GL-EXP-006.md`'s own text; this ticket supersedes only the
deferred follow-on it named, not the ticket file itself.

## Hard laws

1. Delete `scripts/ci_errc.py` and `scripts/tests/test_ci_errc.py` in full
   — this is an elimination, not a rewrite. Do not replace `LANE_RULES`
   with a topology-corrected version; the design judgment `GL-EXP-006.md`
   Hard Law 4 flagged (rewire vs. eliminate) is resolved here as
   eliminate, because `ci.yml`'s current always-run-everything shape has
   no lane-conditional execution problem left for a router to solve (see
   Outcome section, `ci.yml` re-read this session).
2. Before deleting, re-run `grep -rn "ci_errc" .github/workflows/*.yml
   justfile tools/v26.8.1/justfile scripts/ tools/` and confirm the only
   hits are inside `scripts/ci_errc.py`/`scripts/tests/test_ci_errc.py`
   themselves — if any real caller has appeared since this ticket was
   drafted, halt and re-scope instead of deleting a now-live script.
3. Do not modify any of the nine verifier scripts `ci_errc.py` shelled out
   to (`scripts/verify_docs.py`, `scripts/verify_lsp_contract.py`,
   `scripts/verify_foundry_provenance.py`,
   `scripts/verify_foundry_bootstrap.py`,
   `scripts/verify_offline_transport.py`,
   `scripts/verify_ggen_v26_8_1_migration.py`,
   `scripts/autonomic_finish.py`, `scripts/verify_autonomic_finish.py`,
   `scripts/run_autonomic_crown.py`) — all nine exist independently of
   this router and are out of scope.
4. Do not touch `tickets/GL-EXP-006.md`; its own justfile/
   production-gaps.md citation fix remains that ticket's separate scope
   and is unaffected by this deletion.
5. This ticket does not add a `tickets/OVERLAPS.md` entry — `scripts/
   ci_errc.py` and `scripts/tests/test_ci_errc.py` had zero prior
   registry entries and zero other active claimants (Authored boundary
   section above), so there is nothing to reconcile.

## Falsifiers

- `test -f scripts/ci_errc.py` or `test -f scripts/tests/test_ci_errc.py`
  still succeeds after this ticket executes (deletion did not happen).
- `grep -rn "ci_errc" .github/workflows/*.yml justfile
  tools/v26.8.1/justfile scripts/ tools/` finds a real caller that existed
  before this ticket ran but was not accounted for (Hard Law 2 skipped).
- `git diff --stat` after this ticket touches any file outside
  `scripts/ci_errc.py`, `scripts/tests/test_ci_errc.py`, and
  `tickets/GL-EXP-009.md`.
- Any of the nine verifier scripts named in Hard Law 3 shows a diff.
- `.github/workflows/ci.yml` fails after this deletion (it must not — it
  never invoked `ci_errc.py`; a failure here would mean this ticket's own
  "nothing depends on it" claim was wrong and must be re-investigated, not
  worked around).
- `just --list` fails to parse `justfile` after this deletion (it never
  referenced `ci_errc.py`, so this should be impossible; a failure here
  means an untracked dependency existed).

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the deletion lands, not yet-observed
outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the orphan status before touching anything:
grep -rn "ci_errc" .github/workflows/*.yml justfile tools/v26.8.1/justfile
grep -rln "ci_errc" . --exclude-dir=.git --exclude-dir=worktrees --exclude-dir=.worktrees
ls .github/workflows/

# After deletion, confirm both files are gone and nothing else changed:
test -f scripts/ci_errc.py && echo "UNEXPECTED: still exists" || echo "confirmed deleted"
test -f scripts/tests/test_ci_errc.py && echo "UNEXPECTED: still exists" || echo "confirmed deleted"
git diff --stat   # must show only the two deletions + tickets/GL-EXP-009.md

# Confirm nothing that depended on ci_errc.py broke:
just --list
grep -n "python3 scripts/verify_lsp_contract.py" .github/workflows/ci.yml

# Full local CI-equivalent proof the repo still builds/tests clean:
cargo fmt --all -- --check
cargo check --all-targets --locked
cargo clippy --all-targets --locked -- -D warnings
cargo test --all-targets --locked
```

## Evidence this ticket is grounded in (verified this session)

- `ls .github/workflows/` — real output: `ci.yml`, `planning-v26-8-7.yml`
  only.
- `grep -rn "ci_errc" .github/workflows/*.yml justfile
  tools/v26.8.1/justfile` — real output: zero matches (exit code 1).
- `grep -rln "ci_errc" .` (repo-wide, excluding `.git/` and worktree
  checkouts) — real output: exactly
  `tickets/GL-EXP-006.md`, `tickets/GL-AUTO-001.md`,
  `scripts/ci_errc.py`, `scripts/tests/test_ci_errc.py`.
- `grep -rn "pytest|test_ci_errc" .github/workflows/*.yml justfile
  tools/v26.8.1/justfile` — real output: zero matches (exit code 1).
- `grep -n "LANE_RULES|\.yml" scripts/ci_errc.py` — real output confirms
  the five stale `.github/workflows/*.yml` citations at lines 46, 73, 86,
  94, 102.
- Direct `Read` of `scripts/ci_errc.py` in full (351 lines) this session —
  confirms `LANE_RULES` (lines 18-106), the `ERRC` self-description dict
  (lines 108-125), `classify_path(s)` (lines 128-149),
  `git_changed_files` (152-169), `validate_structured_files` (172-198),
  `run_check` (201-224), `write_github_outputs`/`write_summary`
  (227-256), and `main()` (259-346) — the report's `replay.command` field
  (line 333-336) and `--report` default confirm its self-describing output
  path is `evidence/ci/errc-fast.json`.
- `grep -rln "errc-fast" .` (repo-wide, same exclusions) — real output:
  `tickets/GL-EXP-006.md`, `tools/v26.8.1/draft-candidates.json`,
  `scripts/ci_errc.py` only — no independent downstream consumer of its
  report.
- `wc -l scripts/ci_errc.py scripts/tests/test_ci_errc.py` — real output:
  350 + 66 = 416 total lines being eliminated.
- Direct `Read` of `scripts/tests/test_ci_errc.py` (first 60 of 66 lines)
  this session — confirms it is a dedicated `unittest` suite that only
  imports and exercises `scripts/ci_errc.py` via
  `importlib.util.spec_from_file_location`; it has no independent purpose
  once the module it tests is gone.
- `git log --oneline | grep 60d3826` — real output:
  `60d3826 ci: rebuild CI around contract and real LSP execution`.
- Direct `Read` of `.github/workflows/ci.yml` in full (73 lines) this
  session — confirms the single `verify` job, its unconditional
  fmt/check/clippy/test/verify_lsp_contract.py steps, its own
  `evidence/ci/receipt.json` emission independent of `ci_errc.py`'s
  `evidence/ci/errc-fast.json`, and that it calls
  `scripts/verify_lsp_contract.py` directly (line 41) rather than through
  the router.
- `for f in scripts/verify_docs.py scripts/verify_foundry_provenance.py
  scripts/verify_foundry_bootstrap.py scripts/verify_offline_transport.py
  scripts/verify_ggen_v26_8_1_migration.py scripts/verify_lsp_contract.py
  scripts/autonomic_finish.py scripts/verify_autonomic_finish.py
  scripts/run_autonomic_crown.py; do test -f "$f" && echo "EXISTS: $f" ||
  echo "MISSING: $f"; done` — real output: all nine report `EXISTS`,
  confirming none of `ci_errc.py`'s callees are themselves already dead
  (only the router calling them is dead).
- `grep -l "ci_errc" tickets/*.md` — real output:
  `tickets/GL-AUTO-001.md`, `tickets/GL-EXP-006.md`.
- `grep -n "ci_errc" tickets/GL-AUTO-001.md` — real output: line 110
  only, inside a single-line `REFUSED:FORBIDDEN_DIFF:` comma-separated
  path dump, confirmed by direct inspection to be incidental, not a
  substantive ownership claim.
- Direct `Read` of `tickets/GL-EXP-006.md` in full (254 lines) this
  session — confirms its Hard Law 4 and "Additional real evidence found
  this session" section already name this exact finding and explicitly
  defer it ("Left as a named follow-on, not silently dropped"), and that
  its own Authored boundary/Hard laws never touch `scripts/ci_errc.py`
  (Hard Law 4 there explicitly excludes it).
- `grep -n "ci_errc" tickets/OVERLAPS.md` — real output: zero matches, no
  prior overlap registry entry for either path this ticket claims.
- `git rev-parse HEAD` — `bce7f6386c4203784beaae426e40804636c4151a`, the
  real base commit this ticket is drafted against.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and re-verifies the
elimination case (every command above was re-run fresh this session, not
copied from `GL-EXP-006.md`'s prior output); the actual deletion has not
been made.
