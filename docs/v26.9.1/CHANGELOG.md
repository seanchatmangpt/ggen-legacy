# Changelog — v26.9.1 (in progress)

Entries below are limited to tickets with a real `EXECUTED` status and a
cited `## Standing` verification in their own `tickets/*.md` file, checked
directly against those files at base commit
`bce7f6386c4203784beaae426e40804636c4151a`. No entry here is inferred from
a commit message alone.

## Executed this pass

- **fix(coverage_projection.rs)**: Delete dead `read_coverage_csv_bytes()`
  from `tools/v26.8.1/src/coverage_projection.rs` (`GL-ERRC-015`).
  Standing: `ALIVE`. Verified in isolated worktree
  `.claude/worktrees/wf_d45a38a1-7b7-1` — pre-removal grep confirmed the
  function had exactly one match (its own definition, no callers);
  post-removal grep confirmed removal; `cargo build` and
  `cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets
  --locked` both ran clean afterward.

- **feat(archaeology)**: Add `mine_structured()` and `draft_candidates()`
  structured commit-mining bridge to legacy archaeology
  (`GL-ARCH-003`, `tools/v26.8.1/legacy_archaeology.py`).
  Standing: `PARTIAL_ALIVE`. `mine_structured()` walked all 420 reachable
  commits via `pygit2`, exactly matching `mine()`'s existing
  `git log --all --decorate --oneline` count (420 == 420).
  `draft_candidates()` emitted 20 draft candidates (of 420 commits, 22
  already short-hash-matched against `CATALOG`'s 65 published
  individuals) to `tools/v26.8.1/draft-candidates.json`;
  `ontology/v26.8.1/legacy-capabilities.ttl` confirmed byte-identical
  before/after. The 20 drafts are unreviewed by design; not `ALIVE`.

- **fix(verify scripts)**: Add `EXPECTED_*_SOURCE` provenance comments and
  a `STALE_REFERENCE_UNVERIFIABLE` status path to all four `verify_*.py`
  scripts (`scripts/verify_foundry_provenance.py`,
  `scripts/verify_foundry_bootstrap.py`, `scripts/verify_docs.py`,
  `scripts/verify_offline_transport.py`) (`GL-ERRC-011`).
  Standing: `PARTIAL_ALIVE`. All four scripts run clean; no `EXPECTED_*`
  literal value was changed (correct-value determination is an explicit
  repo-owner decision, out of scope). This makes existing staleness
  legible, does not resolve it.

- **fix(ci.yml)**: Fix hardcoded `workflow-count==1` self-check that
  blocks the next real CI run (`GL-ERRC-009`). Standing: `PARTIAL_ALIVE`
  — fix authored and verified against the real repository topology this
  session; **not yet landed** on the shared main checkout
  (`/Users/sac/ggen-legacy/.github/workflows/ci.yml`) due to this
  session's sandbox isolation. Outstanding.

## Not executed this pass (tracked, no code change)

The following tickets exist in `tickets/` as `admitted, NOT_STARTED` and
are explicitly not part of this changelog's code changes:
`GL-ERRC-008`, `GL-ERRC-010` (transparency-log security gap),
`GL-ERRC-012`, `GL-ERRC-013` (AGENTS.md header sync drift),
`GL-ERRC-014`, `GL-ERRC-017`, `GL-ERRC-018`, `GL-ERRC-019`,
`GL-CONTRACT-004`, `GL-MANUFACTURE-005`, `GL-RECEIPT-007`,
`GL-VERIFY-006`.

## See also

- `docs/v26.9.1/RELEASE-NOTES.md` — full standing summary and gap list
- `tickets/GL-ARCH-003.md`, `tickets/GL-ERRC-011.md`,
  `tickets/GL-ERRC-015.md`, `tickets/GL-ERRC-009.md` — source-of-truth
  standing sections for the entries above
- `README.md` — repository-wide Project 001 standing table

## Reconcile pass — 2026-08-20

- **fix(coverage_projection)**: Distinguish `exact_head()`'s 3 collapsed
  failure causes (`GL-ERRC-019`). Standing: `ALIVE`. Returns a distinct
  `STALE_REFERENCE_UNVERIFIABLE:<CAUSE>` string per cause
  (`SPAWN_FAILURE`, `NON_ZERO_EXIT`, `NON_UTF8_STDOUT`); `cargo build`
  and `cargo test exact_head -- --nocapture --test-threads=1` both green
  (3/3 real subprocess tests), full `cargo test --all-targets --locked`
  also green. `NON_UTF8_STDOUT` verified by code inspection only, not an
  executed non-UTF8 test case.

- **`AGENTS.md` header-sync drift (`GL-ERRC-013`)**: Standing remains
  `UNKNOWN` — not started this pass. No code or doc change applied;
  `AGENTS.md`'s header still names only `GL-LSP-001`/`GL-PLAN-002`,
  undercounting the real ticket set.

## Not executed this pass (tracked, no code change)

`GL-ERRC-013` (see above, still `NOT_STARTED`/`UNKNOWN`).

## See also

- `tickets/GL-ERRC-019.md`, `tickets/GL-ERRC-013.md` — source-of-truth
  standing sections for this pass's entries

## Reconcile pass — 2026-08-20, later (GL-ERRC-016, GL-ERRC-022, GL-ERRC-020)

- **fix(coverage_projection.rs)**: Add `--locked` to `run_subsystem_verifier()`'s
  internal `cargo build` invocation (`GL-ERRC-016`). Status: `EXECUTED`.
  Ticket's declared `Standing ceiling: PARTIAL_ALIVE`; its own final
  evidence section reports the falsifier grep clean (`--locked` alongside
  `--manifest-path`/`--bin`), `cargo build --manifest-path
  tools/v26.8.1/Cargo.toml --bin subsystem_verifier --locked` exiting 0
  (`Cargo.lock` not stale), and `cargo test --manifest-path
  tools/v26.8.1/Cargo.toml --all-targets --locked -- --test-threads=1`
  passing 18/18 across 5 suites — independently re-confirmed this pass by
  re-running the same grep and `git diff` against the live main checkout.
  Note: the ticket's own mid-file `## Standing` section still literally
  reads "`UNKNOWN` -- not started," left stale under this repo's
  append-don't-rewrite discipline and superseded by its later `##
  EXECUTED` section — flagged here rather than silently resolved.

- **feat(justfile)**: Add additive `propose-disposition` recipe wiring
  `dsrust-disposition-proposer`'s CLI into the admission workflow as an
  optional, suggestion-only pre-step (`GL-ERRC-022`). Status: `EXECUTED`,
  Standing: `PARTIAL_ALIVE` (ticket's own words). Independently
  re-confirmed this pass: `justfile` diff is exactly `9
  insertions(+)/0 deletions(-)`; a real compiled binary exists at
  `tools/dsrust-disposition-proposer/target/debug/propose-disposition`;
  `just propose-disposition --help` compiles the crate fresh and runs the
  real clap `--help` output, exit 0, no `GROQ_API_KEY` required for that
  path. **Not exercised**: a real disposition-proposal call with all five
  required arguments plus a live `GROQ_API_KEY` — only the
  argument-parsing/`--help` path ran. CLI wiring and compilation are real;
  end-to-end proposal invocation is not yet verified.

- **`authority/foundry-work-program.json` / `foundry/bootstrap.yaml` stale
  `OPEN_DRAFT`/`runtime_dependency_admitted:false` claim (`GL-ERRC-020`)**:
  Status: `admitted, NOT_STARTED`. Standing: `UNKNOWN` — not started, per
  the ticket's own words. No code or doc change applied this pass;
  independently re-confirmed the authority files are unchanged
  (`"status": "OPEN_DRAFT"` at both cited blocks,
  `runtime_dependency_admitted: false`, `standing_transferred: false`).
  No re-verification of sibling-repo PR #543/#544 was executed. This is
  the fourth time this stale claim has been documented without
  remediation.

## Not executed this pass (tracked, no code change)

`GL-ERRC-020` (see above, `admitted, NOT_STARTED`/`UNKNOWN` — foundry
authority stale-claim re-verification not yet run).

## See also

- `tickets/GL-ERRC-016.md`, `tickets/GL-ERRC-022.md`,
  `tickets/GL-ERRC-020.md` — source-of-truth standing sections for this
  pass's entries
- `docs/v26.9.1/RELEASE-NOTES.md` — full standing summary, including this
  pass's independent re-verification commands

## Post-pass correction

`tickets/GL-ERRC-020.md` was found to have been silently overwritten
between drafting and this pass's execution (a real filename race in an
earlier exploration pass). Deduplicated against `GL-ERRC-021.md` (deleted,
duplicate), recovered the lost `GL-AUTO-001` fabrication finding as
`tickets/GL-ERRC-023.md`, and fixed the exploration cron to use a separate
`GL-EXP-NNN` id namespace so this collision class can't recur. See
`docs/v26.9.1/RELEASE-NOTES.md`'s "Release-prep pass 3" section for the
full account.

## Reconcile pass — 2026-08-21 (GL-ERRC-023, GL-AUTO-001, GL-ERRC-012)

- **docs(tickets/GL-AUTO-001.md)**: Correct fabricated
  `.github/workflows/autonomic-crown.yml` claim and non-passing acceptance
  command in `GL-AUTO-001.md`; add missing `Status`/`Standing` sections
  (`GL-ERRC-023`). Status: `EXECUTED`. Standing ceiling:
  `PARTIAL_ALIVE`. Independently re-verified this pass: `test -f
  .github/workflows/autonomic-crown.yml` → `confirmed missing`; `python3
  scripts/run_autonomic_crown.py` → `REFUSED:FORBIDDEN_DIFF:...` (115
  out-of-boundary files), exit `1`, matching the output quoted verbatim in
  both tickets; `grep -n "^\*\*Status:\*\*" tickets/GL-AUTO-001.md` →
  line 3, `BLOCKED`. All three of the ticket's own Falsifiers re-checked,
  none triggered. Only `tickets/GL-AUTO-001.md` and `tickets/GL-ERRC-023.md`
  touched — `scripts/run_autonomic_crown.py` and `.github/workflows/`
  confirmed unmodified.

- **`GL-AUTO-001` itself — not landed work, a corrected claim**: Status
  `BLOCKED`, Standing `BLOCKED` — re-verified live 2026-08-21. The ticket
  now honestly documents that no CI workflow automates it and that the
  acceptance command refuses with `REFUSED:FORBIDDEN_DIFF:...` before
  reaching manufacture/replay/verification. Neither
  `GL_AUTO_001_AUTONOMIC_CROWN_ALIVE` nor `GL_AUTO_001_CROWN_ALIVE` has
  been observed printed by this command in this repository. This entry
  records a truthfulness fix to the ticket, not a change in what the
  underlying `autonomic/` machinery does — that machinery was never
  reached by this run and remains `UNKNOWN`.

- **docs(tickets)**: Split golden-trace corpus design out of
  `GL-VERIFY-006.md` into its own ticket (`GL-ERRC-012`). Status:
  `EXECUTED`. Standing: `PARTIAL_ALIVE` — the document split itself is
  done; the golden-trace corpus *implementation*
  (`equivalence_runner.py`'s `run_case` case-source branch, the example
  JSON file) remains `UNKNOWN`/`NOT_STARTED`, per the ticket's own words.
  Independently re-verified this pass: `grep -c "golden-trace"
  tickets/GL-VERIFY-006.md` → `1` (pointer only); `grep -c "golden-trace"
  tickets/GL-ERRC-012.md` → `25` (full section present). Flagged, not
  smoothed over: the ticket's own header evidence line states this second
  count as `23`; `25` is what this pass's independent grep actually
  measured — a minor stale self-citation in the ticket's own prose, not a
  defect in the relocation itself. `git status --porcelain` confirms only
  `tickets/GL-VERIFY-006.md` and `tickets/GL-ERRC-012.md` were touched by
  the split.

## Not executed this pass (tracked, no code change)

`GL-ERRC-020` (foundry-authority stale-claim re-verification, still
`NOT_STARTED`/`UNKNOWN` — untouched by this pass). The golden-trace corpus
*format implementation* split off by `GL-ERRC-012` remains `NOT_STARTED`
as well — only the design's location moved, not its build status.

## See also

- `tickets/GL-ERRC-023.md`, `tickets/GL-AUTO-001.md`,
  `tickets/GL-ERRC-012.md` — source-of-truth standing sections for this
  pass's entries
- `docs/v26.9.1/RELEASE-NOTES.md` — full standing summary, including this
  pass's independent re-verification commands

## Reconcile pass — 2026-08-21, later (GL-EXP-001, GL-EXP-002, GL-EXP-006) — code real, not an "Executed" entry

None of the three entries below are listed under "Executed this pass":
each ticket's own `**Status:**` line, re-read fresh this pass, still
reads `admitted, NOT_STARTED`, and none of the three files contains a
later `## EXECUTED` addendum. Listed here instead as verified,
uncommitted working-tree changes that satisfy each ticket's own
acceptance/falsifier commands, so the gap between code and ticket record
is visible rather than silently absorbed into either an "executed" or a
"no code change" bucket.

- **fix(subsystem_verifier.rs)**: Delete the byte-for-byte duplicate
  `resolve_root()` in `tools/v26.8.1/src/bin/subsystem_verifier.rs`;
  import the canonical `v26_8_1_tools::coverage_projection::resolve_root`
  instead (`GL-EXP-001`). Ticket `Status: admitted, NOT_STARTED`,
  `## Standing: UNKNOWN -- not started` (verbatim, unchanged). Code-level
  re-verification this pass: `grep -n "^fn resolve_root"
  tools/v26.8.1/src/bin/subsystem_verifier.rs` — no match; `cargo build
  --manifest-path tools/v26.8.1/Cargo.toml --locked` clean; `cargo test
  --manifest-path tools/v26.8.1/Cargo.toml --test verifier_boundary
  --locked` — `2 passed; 0 failed`. Uncommitted (`git status --porcelain`
  shows `M`).

- **fix(Cargo.toml)**: Repin `tools/ggen-verifier-cli-verify`'s
  `chicago-tdd-tools` dev-dependency from a dead
  `path = "/Users/sac/ggen/crates/chicago-tdd-tools"` to the published
  registry crate (`GL-EXP-002`). Ticket `Status: admitted, NOT_STARTED`;
  `## Standing: PARTIAL_ALIVE` for the ticket's *evidence*, with its own
  text stating the manifest edit/relock "have not been performed yet
  (`NOT_STARTED`)" — unchanged. Code-level re-verification this pass:
  `Cargo.lock` now resolves `chicago-tdd-tools` at `version = "26.8.9"`,
  `source = "registry+https://github.com/rust-lang/crates.io-index"`
  (a later published version than the ticket's `26.8.3` example,
  permitted by its own Hard Law 1); `cargo clippy --manifest-path
  tools/ggen-verifier-cli-verify/Cargo.toml --all-targets -- -D warnings`
  — exit `0`. Uncommitted (`M` on both `Cargo.toml` and `Cargo.lock`).

- **fix(justfile, governance/production-gaps.md)**: Correct the stale
  `.github/workflows/gl-lsp-001-runtime.yml` citation to
  `.github/workflows/ci.yml` in both files (`GL-EXP-006`). Ticket
  `Status: admitted, NOT_STARTED`, `## Standing: UNKNOWN -- not started`
  (verbatim, unchanged). Code-level re-verification this pass: `grep -n
  "gl-lsp-001-runtime" justfile governance/production-gaps.md` — no
  match; `grep -n "gl-lsp-001-runtime" scripts/ci_errc.py` — still
  matches at line 73, confirming the ticket's Hard Law 4 exclusion was
  honored (that file deliberately untouched); `just --list` parses
  cleanly. Uncommitted (`M` on both files).

**Why these are not counted as "Executed this pass":** this session's
task instruction was to report each entry from the ticket's own
post-execution `Status`/`Standing` section, not from independent
code-level re-verification alone. All three tickets' own files still say
`NOT_STARTED`. Real, passing code changes exist in the shared working
tree for all three — that is reported honestly above — but the tickets
that are supposed to be this repo's record of "is it done" were never
updated to say so, and this pass does not make that call on the tickets'
behalf.

## Not executed this pass (tracked, no ticket-status change)

`GL-EXP-001`, `GL-EXP-002`, `GL-EXP-006` — see above: real code exists,
but each ticket's own `Status`/`Standing` remains `admitted, NOT_STARTED`
/ `UNKNOWN`.

## See also

- `tickets/GL-EXP-001.md`, `tickets/GL-EXP-002.md`,
  `tickets/GL-EXP-006.md` — source-of-truth Status/Standing sections for
  this pass's entries (all three still read `NOT_STARTED`)
- `docs/v26.9.1/RELEASE-NOTES.md` — full account, including the
  independent re-verification commands and the code-vs-ticket-record gap
  this pass surfaced

## Reconcile pass — 2026-08-21, later (GL-EXP-029, GL-EXP-025)

Both tickets' own files already state `Status: EXECUTED` / `Standing:
ALIVE` (unlike the `GL-EXP-001`/`002`/`006` pass above, which found
`NOT_STARTED` tickets sitting on real code) — this pass independently
re-ran each ticket's own commands against the live main checkout
(`HEAD` = `bce7f6386c4203784beaae426e40804636c4151a`) rather than trusting
each ticket's own worktree-scoped verification.

## Executed this pass

- **fix(subsystem_verifier.rs)**: Delete the dead
  `#[allow(dead_code)] legacy_disposition_summary: serde_json::Value`
  field from `Manifest` in
  `tools/v26.8.1/src/bin/subsystem_verifier.rs` (`GL-EXP-029`). Standing:
  `ALIVE`. Independently re-verified this pass against the main checkout:
  `grep -c "legacy_disposition_summary"
  tools/v26.8.1/src/bin/subsystem_verifier.rs` → `0`; `cargo build
  --manifest-path tools/v26.8.1/Cargo.toml --locked` clean; `cargo test
  --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked` →
  `15 passed; 0 failed`, matching the ticket's own cited count exactly.
  Uncommitted (`M` on `subsystem_verifier.rs`).

- **fix(Cargo.toml)**: Remove the unused direct `tracing = "0.1"`
  dependency from root `Cargo.toml` (`tracing` stays resolvable
  transitively via `lsp-max`) (`GL-EXP-025`). Standing: `ALIVE`.
  Independently re-verified this pass against the main checkout:
  `grep -n '^tracing = ' Cargo.toml` → no match; `grep -n '^name =
  "tracing"$' Cargo.lock` → still present (pulled in via `lsp-max`);
  `cargo fmt --all -- --check`, `cargo check --all-targets`, `cargo
  clippy --all-targets -- -D warnings` all clean; `cargo test
  --all-targets` → `18 passed; 0 failed` (the ticket's own worktree run
  cited `13`; the +5 delta is unrelated tests independently added to
  `tests/analysis.rs`/`tests/analysis_boundary.rs` between the ticket's
  worktree base and the main checkout's `HEAD` — flagged honestly, not a
  regression). `src/main.rs`'s `tracing_subscriber::fmt()...init()` block
  re-confirmed byte-identical (Hard Law 5). Uncommitted (`M` on
  `Cargo.toml`, `Cargo.lock`).

`just ci-all`: clean (exit 0) against the main checkout after both
re-verifications.

## See also

- `tickets/GL-EXP-029.md`, `tickets/GL-EXP-025.md` — source-of-truth
  Status/Standing sections for this pass's entries (both `EXECUTED`/
  `ALIVE` in their own files, independently reconfirmed against the main
  checkout by this pass rather than assumed from worktree-scoped evidence)
- `docs/v26.9.1/RELEASE-NOTES.md` — full account, including the
  `EXECUTED`-count tally (15 → 17) and the re-measured uncommitted-file
  count (88, continuing the `GL-EXP-016` trend line)

## Executed this pass — 2026-08-21 (GL-EXP-005)

- **fix(subsystem_verifier.rs)**: Delete the regressed private duplicate
  `fn fresh_git_head(root: &Path) -> String` from
  `tools/v26.8.1/src/bin/subsystem_verifier.rs` and call the canonical
  `v26_8_1_tools::coverage_projection::exact_head` in its place, via a
  braced `use` import matching `main.rs`'s/`project_coverage.rs`'s
  existing style (`GL-EXP-005`). The deleted copy had regressed to the
  exact pre-`GL-ERRC-019` shape — all 3 distinct `git rev-parse HEAD`
  failure causes (spawn failure, non-zero exit, non-UTF8 stdout)
  collapsed into one undifferentiated `"UNKNOWN"` sentinel — while
  `exact_head()` already returns 3 distinct
  `STALE_REFERENCE_UNVERIFIABLE:<CAUSE>` values for the same 3 causes.
  Mirrors `GL-EXP-001`'s already-executed fix for this same file's
  `resolve_root()` duplicate.

  Standing: `PARTIAL_ALIVE`. All 5 of the ticket's own falsifiers
  resolved to their non-triggering outcome this session:
  `grep -n "^fn fresh_git_head" tools/v26.8.1/src/bin/subsystem_verifier.rs`
  → no match; `grep -n 'unwrap_or_else(|| "UNKNOWN"'
  tools/v26.8.1/src/bin/subsystem_verifier.rs` → no match; `cargo build
  --manifest-path tools/v26.8.1/Cargo.toml --locked` → clean; `cargo test
  --manifest-path tools/v26.8.1/Cargo.toml --test verifier_boundary
  --locked` → `2 passed; 0 failed; 0 ignored`; scoped `git diff --stat`
  review → edits confined to `subsystem_verifier.rs` and
  `tickets/GL-EXP-005.md`, all other diffed files pre-dating this
  session.

  `just ci-all` (both workspaces) additionally re-run this pass: exit
  code 0, **36 tests passed, 0 failed, 0 ignored** across root
  `ggen-legacy-lsp`/`ggen-lsp` (18) and `tools/v26.8.1` (18), fmt/check/
  clippy clean in both. `git status --porcelain -uall | wc -l` → **97**
  (current branch `agent/add-dsrust-groq-disposition-proposer`; 96 of
  those 97 paths pre-date this ticket's own two-file edit).
  `tickets/OVERLAPS.md`'s `subsystem_verifier.rs` row updated in place:
  `GL-EXP-005` marked `EXECUTED` (was `NOT_STARTED`).

## See also (GL-EXP-005 pass)

- `tickets/GL-EXP-005.md` — source-of-truth `## Evidence`/`## Standing`
  sections for this entry, including the full per-workspace `just
  ci-all` breakdown
- `docs/v26.9.1/RELEASE-NOTES.md` — matching narrative entry
  ("GL-EXP-005 executed — eliminate the regressed duplicate
  `fresh_git_head()`")

## Executed this pass — 2026-08-21 (GL-EXP-046)

- **fix(docs)**: Correct the stale "`lsp-max` PR #22 unmerged" claim in
  `Cargo.toml`'s `# PROVISIONAL PIN:` comment (above the `lsp-max`
  dependency), `governance/production-gaps.md`'s `lsp-max` bullet, and
  `tickets/GL-LSP-001.md`'s Standing-section pin bullet (`GL-EXP-046`).
  Fresh, execution-time re-verification (Hard Law 1, not reused from
  drafting) confirmed PR #22 is `MERGED` (`mergedAt:
  2026-08-04T15:18:48Z`, same `headRefOid` as drafting) with no release
  tag yet (`gh api repos/seanchatmangpt/lsp-max/tags` and `.../releases`
  both `[]`) — reproducing the drafting-session findings exactly, so
  Hard Law 2's correction path applied. All three files' "not yet
  merged"/"unmerged branch"/"draft PR" phrasing replaced with the
  corrected, present-tense fact (merged 2026-08-04; pin remains a
  commit-rev pin only because no tag exists yet). `Cargo.toml`'s
  `lsp-max = { git = ..., rev = ... }` dependency line itself is
  byte-identical before and after (only the comment above it grew by one
  line).

  Standing: `PARTIAL_ALIVE`. All 7 of the ticket's own falsifiers
  re-run this session, each resolved to its non-triggering outcome: the
  fresh `gh pr view`/`gh api tags`/`gh api releases` re-check above;
  `grep -n "not yet merged\|unmerged branch\|draft PR" Cargo.toml
  governance/production-gaps.md tickets/GL-LSP-001.md` → no matches; the
  `lsp-max = { git` dependency line confirmed unchanged via `git diff`;
  `git status --short` on the exact authored-boundary file set → exactly
  ` M Cargo.toml`, ` M governance/production-gaps.md`,
  ` M tickets/GL-LSP-001.md`, `?? tickets/GL-EXP-046.md`,
  `?? tickets/OVERLAPS.md`; `tickets/OVERLAPS.md` confirmed unaltered by
  construction; `Cargo.toml` confirmed still parses (`python3 -c "import
  tomllib; tomllib.load(open('Cargo.toml','rb'))"` and `cargo metadata
  --no-deps --manifest-path Cargo.toml` both succeeded); full Acceptance
  block re-run end to end.

  `just ci-all` (both workspaces) additionally re-run this pass, as an
  out-of-scope precaution given the edit is doc/comment-only: exit code
  0, root `ggen-legacy-lsp`/`ggen-lsp` workspace (6 test binaries, all
  `ok`, 0 failed; fmt/check/clippy clean) and `tools/v26.8.1` (`lib` 3/3
  ok, `main` bin 13/13 ok, `tests/verifier_boundary.rs` 2/2 ok;
  fmt/check/clippy clean) — **all 8 steps passed, no build/test
  failures.** `git status --porcelain -uall | wc -l` → **102**,
  unchanged before and after the `ci-all` run (pre-existing uncommitted
  work from other tickets, not artifacts of this run).
  `tickets/OVERLAPS.md`'s three `GL-EXP-046` references (the
  `GL-LSP-001.md`-disclosure row, the `Cargo.toml` (root) section, and
  the `governance/production-gaps.md` section) updated in place:
  `GL-EXP-046` marked `EXECUTED` (was `NOT_STARTED`), matching the
  pattern already established there for `GL-EXP-001`/`GL-EXP-005`.

## See also (GL-EXP-046 pass)

- `tickets/GL-EXP-046.md` — source-of-truth `## Evidence`/`## Standing`
  sections for this entry, including the full falsifier re-run and the
  complete per-workspace `just ci-all` breakdown
- `docs/v26.9.1/RELEASE-NOTES.md` — matching narrative entry
  ("GL-EXP-046 executed — reduce the stale \"lsp-max PR #22 unmerged\"
  claim")
- `tickets/OVERLAPS.md` — the three `GL-EXP-046` rows updated to
  `EXECUTED`

## Executed this pass — 2026-08-21 (GL-EXP-013)

- **fix(appliance/bin)**: Consolidate the independently-duplicated
  `sha256_file(path)` (10 files: 5 chunked-streaming, 5
  `read_bytes()`-based — same digest, different memory behavior) and
  `read_json(path)` (7 of those 10 files) into one new module,
  `appliance/bin/_shared.py`, containing exactly these two functions.
  All 10 files' private `sha256_file` definitions deleted and replaced
  with `from _shared import sha256_file` (7 also import `read_json`);
  the canonical implementation is the chunked-streaming variant
  (`GL-EXP-013`). `write_json` and the 3 files' inlined
  `json.loads(...read_text())` call sites are explicitly out of scope
  (Hard Laws 3–4) and were not touched.

  Standing: `PARTIAL_ALIVE`. All of the ticket's own falsifiers re-run
  this session, each resolved to its non-triggering outcome: `grep -n
  "^def sha256_file\|^def read_json" appliance/bin/*.py` → matches only
  `_shared.py`'s own two canonical definitions, zero matches in the 10
  former call-site files; `test -f appliance/bin/_shared.py && grep -n
  "^def " appliance/bin/_shared.py` → exactly `sha256_file`/`read_json`,
  no scope creep; digest equivalence on `AGENTS.md` — direct
  `hashlib.sha256(...).hexdigest()` and `_shared.sha256_file(...)` both
  returned `ada0ef86666c486d5a11120bd46557fbe688d9a1501b30409fc195d6688da2c5`;
  `bash appliance/bin/run-reference-e2e.sh`, run twice post-change, both
  exited `0` ending in `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`; `git diff
  --stat -- appliance/bin` → exactly the 10 Authored-boundary files (19
  insertions, 57 deletions), content-diff grep for `write_json`,
  `tree_inventory`, `tree_digest`, `canonical`, `sha256_bytes`,
  `argparse` → zero matches; `appliance/bin/cross-check-portfolio.py`
  and `appliance/bin/observe-project.py` confirmed unmodified; `python3
  -m py_compile` on `_shared.py` and all 10 edited files → clean.

  `just ci-all` (both workspaces) additionally re-run this pass: real
  exit code 0. Root workspace — fmt/check/clippy clean, `cargo test
  --all-targets --locked --test-threads=1` → 18 passed, 0 failed.
  `tools/v26.8.1` workspace — fmt/check/clippy clean, `cargo test
  --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked
  --test-threads=1` → 18 passed, 0 failed. **36 tests passed, 0 failed,
  0 ignored** total. `bash appliance/bin/run-reference-e2e.sh` was not
  part of the `ci-all` pass itself: `git diff --name-only main...HEAD`
  (this branch's real committed diff) touches 0 files under
  `appliance/bin/`, so the e2e script was correctly out of scope for
  that check under its own stated condition — the direct two-run e2e
  proof above (falsifier re-run) is the actual regression evidence for
  this ticket. `git status --porcelain -uall | wc -l` → **113** (28
  modified tracked, 85 untracked — pre-existing uncommitted work from
  other tickets and standing automation, not artifacts of this run;
  HEAD advanced from `f9b283e` to `bce7f63` during the run, consistent
  with other concurrent session activity in this repo).

  `tickets/OVERLAPS.md`'s three `appliance/bin`-related sections
  (`appliance/bin/_shared.py`, `appliance/bin/verify-standing-portfolio.py`,
  `appliance/bin` (`exact_head` vs. `sha256_file`/`read_json`)) updated
  in place: `GL-EXP-013` marked `EXECUTED` (was `NOT_STARTED`), and the
  still-`NOT_STARTED` siblings (`GL-EXP-015`, `GL-EXP-017`,
  `GL-EXP-023`, `GL-EXP-041`, `GL-EXP-045`) flagged to re-verify current
  line numbers / append to the now-existing `_shared.py` rather than
  assume pre-execution state.

## See also (GL-EXP-013 pass)

- `tickets/GL-EXP-013.md` — source-of-truth `## Outcome`/`## Standing`
  sections for this entry, including the full falsifier re-run and the
  complete per-workspace `just ci-all` breakdown
- `docs/v26.9.1/RELEASE-NOTES.md` — matching narrative entry
  ("GL-EXP-013 executed — consolidate the duplicated
  `sha256_file()`/`read_json()` helpers in `appliance/bin/`")
- `tickets/OVERLAPS.md` — the three `appliance/bin`-related sections
  updated to reflect `GL-EXP-013` `EXECUTED`

## Executed this pass — 2026-08-21 (GL-EXP-017)

- **fix(appliance/bin)**: Eliminate the byte-for-byte duplicated
  `write_json(path, obj)` across 5 files
  (`build-standing-portfolio.py`, `decision-engine.py`,
  `replay-standing-portfolio.py`, `transparency-log.py`,
  `verify-standing-portfolio.py`) — the follow-up `GL-EXP-013` explicitly
  named out of its own scope (Hard Law 4). `appliance/bin/_shared.py`
  already existed (created by `GL-EXP-013`), so this appended
  `write_json` to it (Hard Law 3's "append" branch) without touching the
  existing `sha256_file`/`read_json`. All 5 private definitions deleted;
  4 files now import `write_json` from `_shared`;
  `transparency-log.py`'s copy was genuinely dead code (0 call sites) and
  was deleted without adding an unused import (Hard Law 2).

  Standing: `PARTIAL_ALIVE`. All of the ticket's own falsifiers re-run
  this session, each resolved to its non-triggering outcome: `grep -n
  "^def write_json" appliance/bin/*.py` → matches only
  `_shared.py:28`, zero matches in the 5 former call-site files;
  `appliance/bin/_shared.py` confirmed to hold exactly three functions
  (`sha256_file`, `read_json`, `write_json`); `grep -c "from _shared
  import"` on all 5 files → 1 each (4 import all three names,
  `transparency-log.py` imports only `sha256_file, read_json`);
  `grep -n "write_json" appliance/bin/transparency-log.py` → zero matches
  of any kind post-edit; deterministic output-bytes equivalence
  (`_shared.write_json({'b':2,'a':1})` matched
  `json.dumps(obj, indent=2, sort_keys=True) + "\n"` byte-for-byte);
  `python3 -m py_compile` on `_shared.py` and all 5 edited files → clean;
  `bash appliance/bin/run-reference-e2e.sh`, run twice (pre- and
  post-change), both exited `0` ending in
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`; `git diff --stat` isolated to
  the 5 Authored-boundary files → 10 insertions(+), 45 deletions(-),
  content-diff grep for `sha256_file`, `read_json`, `tree_inventory`,
  `tree_digest`, `canonical`, `sha256_bytes`, `argparse` → zero matches;
  the other 7 `appliance/bin/*.py` files with no `write_json` duplicate
  confirmed unmodified by this ticket's own edits.

  `just ci-all` (both workspaces) additionally re-run this pass: real
  exit code 0. Root workspace — fmt/check/clippy clean, `cargo test
  --all-targets --locked --test-threads=1` → 20 passed, 0 failed
  (`lib.rs`, `main.rs`, `tests/analysis.rs` (7),
  `tests/analysis_boundary.rs` (4), `tests/contract.rs` (3),
  `tests/exit_code.rs` (1), `tests/lsp_boundary.rs` (2)).
  `tools/v26.8.1` workspace — fmt/check/clippy clean, `cargo test
  --all-targets --locked` → 18 passed, 0 failed (`lib.rs` (3),
  `main.rs`/`ggen_v26_8_1_verifier` (13
  `document_evidence_sabotage_tests`), `src/bin/project_coverage.rs` (0),
  `src/bin/subsystem_verifier.rs` (0), `tests/verifier_boundary.rs` (2)).
  **38 tests passed, 0 failed** total. `bash
  appliance/bin/run-reference-e2e.sh` was not part of the `ci-all` pass
  itself: `git log --oneline main..HEAD -- appliance/bin/` and `git diff
  --stat main...HEAD -- appliance/bin/` on this branch both returned
  empty (no committed change on this branch touches `appliance/bin/`) —
  the direct two-run e2e proof above (falsifier re-run) is the actual
  regression evidence for this ticket. `git status --porcelain -uall |
  wc -l` → **113** (pre-existing uncommitted work from other tickets and
  standing automation, not artifacts of this run).

  `tickets/OVERLAPS.md`'s `appliance/bin/_shared.py` section updated in
  place: `GL-EXP-017` marked `EXECUTED` (was `NOT_STARTED`), noting the
  "append" branch was taken (not "create" — `GL-EXP-013` had already
  created the module), and flagging the still-`NOT_STARTED` siblings
  (`GL-EXP-041`, `GL-EXP-045`) that `_shared.py` now carries three
  functions, not two.

## See also (GL-EXP-017 pass)

- `tickets/GL-EXP-017.md` — source-of-truth `## Outcome`/`## Standing`/
  `## CI verification` sections for this entry, including the full
  falsifier re-run and the complete per-workspace `just ci-all` breakdown
- `docs/v26.9.1/RELEASE-NOTES.md` — matching narrative entry
  ("GL-EXP-017 executed — eliminate the byte-for-byte duplicated
  `write_json()` helper in `appliance/bin/`")
- `tickets/OVERLAPS.md` — the `appliance/bin/_shared.py` section updated
  to reflect `GL-EXP-017` `EXECUTED`

## GL-EXP-045 executed — recovered from a stalled Workflow pass

`2026-08-21`. Consolidated the typed `canonical(value: Any) -> bytes`
duplicate in `appliance/bin/build-subsystem-evidence.py`/
`verify-subsystem-evidence.py` into `appliance/bin/_shared.py` as
`typed_canonical`. The executing Workflow pass (`w9e8dxd2r`) stalled
after landing the code edit but before finishing verification/
documentation — confirmed a genuine hang (zero live `cargo`/`just`
processes, journal stalled ~57 min), stopped it, then independently
re-ran every falsifier (`grep` for the deleted def, `run-reference-e2e.sh`
→ `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`/exit 0, full `just ci-all` →
clean both workspaces) before correcting the ticket's stale `Status`
header to `EXECUTED`. `git diff --stat` scoped to exactly the 2
Authored-boundary files, 6 insertions/30 deletions. Ticket count: 71
total, **21 executed**, 50 drafted.

## See also (GL-EXP-045 pass)

- `tickets/GL-EXP-045.md` — source-of-truth `## Evidence`/`## Standing`
  sections, including the recovery note
- `docs/v26.9.1/RELEASE-NOTES.md` — full narrative of the stall/recovery
- `tickets/OVERLAPS.md` — the two `GL-EXP-045` rows (already correct
  pre-stall)

## Executed this pass — 2026-08-21 (GL-EXP-049)

- **fix(appliance/bin)**: Consolidate the byte-identical
  `digest_sources(root, sources)`/`check_map(report)` duplicates in
  `appliance/bin/build-subsystem-evidence.py`/
  `appliance/bin/verify-subsystem-evidence.py` into
  `appliance/bin/_shared.py` — the last disjoint helper pair left in this
  file pair after `GL-EXP-013`/`017`/`045`'s prior consolidations
  (`sha256_file`/`read_json`/`write_json`/`typed_canonical`).
  `appliance/bin/_shared.py` now holds all six functions. Both files'
  private `def digest_sources`/`def check_map` blocks deleted outright,
  replaced with `from _shared import ..., digest_sources, check_map`; all
  10 call sites already used the bare names with no module qualification,
  so no call-site text changed (same pattern `GL-EXP-013`/`045`
  established for this file pair).

  Standing: `PARTIAL_ALIVE`. All of the ticket's own falsifiers re-run
  this session, each resolved to its non-triggering outcome: `grep -n
  "^def digest_sources\|^def check_map"` on both files → zero matches;
  `grep -n "^def " appliance/bin/_shared.py` → all six functions present,
  prior four untouched, no collision; `py_compile` on `_shared.py` and
  both edited files → clean; direct behavioral-equivalence check
  (reconstructed old bodies, md5-verified identical to what was deleted,
  vs. the `_shared`-imported versions) across 3 sample inputs for
  `digest_sources()` and 4 for `check_map()`, including a missing file, an
  empty source list, and non-dict/absent `checks` entries → identical in
  every case; `bash appliance/bin/run-reference-e2e.sh`, run pre- and
  post-change, both exited `0` ending in
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`; `git diff --stat` isolated to
  the 2 Authored-boundary files → 6 insertions(+), 78 deletions(-); the
  ticket's own Acceptance Python snippet run directly against
  `_shared.digest_sources`/`_shared.check_map` → "digest_sources() and
  check_map() behave as expected."

  `just ci-all` (both workspaces) additionally re-run this pass: real
  exit code 0. Root workspace — `cargo fmt --all -- --check` clean,
  `cargo check --all-targets --locked` clean, `cargo clippy --all-targets
  --locked -- -D warnings` clean, `cargo test --all-targets --locked
  --test-threads=1` → 18 passed, 0 failed. `tools/v26.8.1` workspace —
  fmt/check/clippy clean, `cargo test --all-targets --locked
  --test-threads=1` → 18 passed, 0 failed (including the 13
  `document_evidence_sabotage_tests`). Because `appliance/bin/` is
  modified in the working tree, `bash appliance/bin/run-reference-e2e.sh`
  was additionally re-run as part of this same pass: exit `0`, final line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` (the script's own
  sabotage-detection negative controls correctly reported
  `PARTIAL_ALIVE`/`passed:false` mid-run — the expected outcome of those
  fixtures, not a regression). `tools/v26.8.1/step_two.py` was not in the
  modified/untracked file set, so no `--help` smoke check applied.
  `git status --porcelain -uall | wc -l` → **117**, unchanged before and
  after both runs.

  `tickets/OVERLAPS.md`'s `appliance/bin/_shared.py` and
  `appliance/bin (exact_head vs. sha256_file/read_json)` sections updated
  in place: `GL-EXP-049` marked `EXECUTED` (was `NOT_STARTED`); only this
  ticket's own rows and the shared "Reconciled" text were edited —
  `GL-EXP-013`/`017`/`023`/`041`/`045`'s own rows confirmed byte-identical
  to their pre-edit text.

## See also (GL-EXP-049 pass)

- `tickets/GL-EXP-049.md` — source-of-truth `## Evidence`/`## Standing`
  sections for this entry, including the full falsifier re-run and the
  complete per-workspace `just ci-all` breakdown
- `docs/v26.9.1/RELEASE-NOTES.md` — matching narrative entry
  ("GL-EXP-049 executed — consolidate `digest_sources()`/`check_map()`
  into `_shared.py`")
- `tickets/OVERLAPS.md` — the two sections updated to reflect
  `GL-EXP-049` `EXECUTED`

## Executed this pass — 2026-08-21 (GL-EXP-050)

- **docs(AGENTS.md)**: Re-run `AGENTS.md`'s `drafted tickets (see
  tickets/):` field (`GL-ERRC-013`'s own field, never re-run since), fixing
  two staleness axes in one pass: 56 of 75 tickets (75%) silently omitted
  at execution time (up from 52 of 71 at drafting time), and one
  already-listed ticket's status text drifted stale (`GL-AUTO-001` shown
  as "no Status: line" though the file had since gained
  `**Status:** \`BLOCKED\``) (`GL-EXP-050`). Status: `EXECUTED`. Standing
  ceiling: `PARTIAL_ALIVE`. Field body replaced with a freshly re-derived
  75-line list (`AGENTS.md:11-85`), each ticket's status copied verbatim
  from its own current `**Status:**` line.

  3 of the ticket's own 4 falsifiers resolved to their non-triggering
  outcome this session: `for f in tickets/GL-*.md; do ...; done` (missing
  tickets) → no output; a from-scratch Python re-derivation comparing all
  75 field entries against each ticket's own Status line → 0 mismatches;
  `active`/`concurrent` executable-ticket lines (`GL-LSP-001`/
  `GL-PLAN-002`) → unchanged. The 4th falsifier (`git diff --stat` scoped
  to exactly `AGENTS.md`, `tickets/GL-EXP-050.md`, `tickets/OVERLAPS.md`)
  does **not** literally hold, because 27 other tracked files were already
  modified in the working tree before this execution touched anything —
  reported honestly as a non-pass, not reinterpreted; isolated
  `git status --porcelain` on the exact 3 named paths confirms this
  ticket's own footprint is correctly scoped (` M AGENTS.md`,
  `?? tickets/GL-EXP-050.md`, `?? tickets/OVERLAPS.md`), and an isolated
  `git diff -- AGENTS.md` confirms every changed line is a field
  header/bullet, nothing else.

  `just ci-all` (both workspaces) re-run this pass: real exit code `0`.
  Root workspace — fmt/check/clippy clean, `cargo test --all-targets
  --locked -- --test-threads=1` → 18 passed, 0 failed. `tools/v26.8.1`
  workspace — fmt/check/clippy clean, same test flags → 18 passed, 0
  failed (including the 13 `document_evidence_sabotage_tests`). **36
  tests passed, 0 failed** total. Because `appliance/bin/` is modified in
  the working tree, `bash appliance/bin/run-reference-e2e.sh` was
  additionally re-run: exit `0`, final line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` (its own negative-control
  checks correctly reported `PARTIAL_ALIVE`/`passed:false` mid-run by
  design, not a regression). `git status --porcelain -uall | wc -l` →
  **117**, unchanged before and after both runs.

  `tickets/OVERLAPS.md`'s existing `## \`AGENTS.md\`` section's
  `GL-EXP-050` row updated in place: status annotation changed from
  `(NOT_STARTED)` to `(EXECUTED)` with a real completion note; no other
  row touched.

## See also (GL-EXP-050 pass)

- `tickets/GL-EXP-050.md` — source-of-truth `## Execution evidence`/
  `## Standing`/`## CI verification` sections for this entry, including
  the full falsifier re-run (honestly reporting falsifier 4's literal
  non-pass) and the complete per-workspace `just ci-all` breakdown
- `docs/v26.9.1/RELEASE-NOTES.md` — matching narrative entry
  ("GL-EXP-050 executed — re-run `AGENTS.md`'s stale `drafted tickets`
  field")
- `tickets/OVERLAPS.md` — the `AGENTS.md` section's `GL-EXP-050` row,
  `EXECUTED`

## Executed this pass — 2026-08-21 (GL-EXP-052)

- **feat(scripts)**: Add `scripts/verify_agents_ticket_sync.py`, a new,
  read-only, stdlib-only admission gate that checks `AGENTS.md`'s
  `drafted tickets (see tickets/):` field stays in sync with
  `tickets/GL-*.md` on disk, in both directions (`missing-from-field`,
  `stale-in-field`) — enforcing mechanically the intent
  `GL-ERRC-013`'s own Hard Law 4 already stated in prose ("must be
  re-run at execution time... since new tickets will keep being
  drafted") (`GL-EXP-052`). Status: `EXECUTED`. Standing ceiling
  (ticket's own declared value): `PARTIAL_ALIVE`.

  All 6 of the ticket's own falsifiers re-run this session, each
  resolved to its real outcome: the real repo run (`python3
  scripts/verify_agents_ticket_sync.py`) exited `0` with no output —
  field and disk both now at 75 entries, in sync, because `AGENTS.md`'s
  field had already been brought current by other already-landed work
  (`GL-EXP-050`, `EXECUTED`) earlier in this session's working tree
  before this ticket began executing; this diverges from the ticket's
  own literal drafting-time expectation ("52 missing"), reported
  honestly rather than reinterpreted, mirroring the `GL-EXP-050`
  precedent named in the ticket's own Outcome section. The three
  synthetic two-fixture falsifiers — missing-from-field (`GL-Y-002`
  named exactly, exit `1`), stale-in-field (`GL-Z-003` named exactly,
  exit `1`), and the missing-header parse error (exit `2`, no uncaught
  exception) — are the primary correctness check independent of repo
  drift, and all three passed exactly as specified. `git status
  --porcelain` scoped to the two Authored-boundary paths confirmed only
  `scripts/verify_agents_ticket_sync.py` and `tickets/GL-EXP-052.md`,
  both `??` (new) — Hard Law 7 satisfied. `python3 -m py_compile` + an
  AST import scan confirmed the script compiles cleanly and imports only
  `argparse`/`re`/`pathlib`/`sys`/`__future__` (stdlib only, Hard Law 6).

  `just ci-all` (both workspaces) run this pass: real exit code `0`. Root
  workspace — `cargo fmt --all -- --check` clean, `cargo check
  --all-targets --locked` clean, `cargo clippy --all-targets --locked --
  -D warnings` clean (zero warnings), `cargo test --all-targets --locked
  -- --test-threads=1` → 18 passed, 0 failed (`ggen_legacy_lsp` lib 1,
  `analysis.rs` 7, `analysis_boundary.rs` 4, `contract.rs` 3,
  `exit_code.rs` 1, `lsp_boundary.rs` 2). `tools/v26.8.1` workspace —
  fmt/check/clippy clean (zero warnings), `cargo test --manifest-path
  tools/v26.8.1/Cargo.toml --all-targets --locked -- --test-threads=1` →
  18 passed, 0 failed (`v26_8_1_tools` lib 3,
  `document_evidence_sabotage_tests` 13, `verifier_boundary.rs` 2).
  **36 tests passed, 0 failed** total, all 8 fmt/check/clippy/test steps
  clean across both workspaces. Uncommitted (`git status --porcelain`:
  28 pre-existing modified tracked files, already dirty before this
  ticket began, none touched by this ticket's own edits, plus this
  ticket's own two new/untracked paths).

  No `tickets/OVERLAPS.md` update: checked this session, no existing
  ticket's Authored boundary or `OVERLAPS.md` section names
  `scripts/verify_agents_ticket_sync.py`, and this ticket only *reads*
  `AGENTS.md` (does not write it), so no new registry row is required —
  matching the ticket's own `## Authored boundary` reasoning verbatim.
  Wiring the new script into `justfile`/CI remains explicitly out of
  scope, per the ticket's own Authored boundary.

## Not executed this pass (tracked, no code change)

None new this pass — `GL-EXP-052` reached `EXECUTED` with real, re-run
verification. The pre-existing gaps named in prior passes above remain
unchanged.

## See also (GL-EXP-052 pass)

- `tickets/GL-EXP-052.md` — source-of-truth `## Evidence`/`## Standing`
  sections for this entry, including the full falsifier re-run and the
  complete per-workspace `just ci-all` breakdown
- `docs/v26.9.1/RELEASE-NOTES.md` — matching narrative entry
  ("GL-EXP-052 executed — machine-checkable admission gate for
  `AGENTS.md`'s `drafted tickets` field")

## Executed this pass — 2026-08-21 (GL-EXP-048)

- **feat(justfile)**: Add `verify-prd-ard`, a new, optional,
  suggestion-only recipe that pass-throughs to `python3
  verifiers/verify_ggen_v26_8_3.py --subject-root . --expected-repository
  seanchatmangpt/ggen-legacy --expected-role
  EXECUTABLE_ARCHITECTURE_CORPUS` (`GL-EXP-048`). Picks up the
  `justfile`-wiring half of the resolution `GL-EXP-035` deferred and
  `GL-EXP-040` reaffirmed out of scope, now that `GL-EXP-040` fixed the
  underlying `BUILD_BROKEN` digest mismatch. Status: `EXECUTED`. Standing
  ceiling (ticket's own declared value): `PARTIAL_ALIVE`.

  All 5 of the ticket's own falsifiers re-run this session, all passing:
  the verifier command re-run three times (before edit, via `just
  verify-prd-ard`, directly after edit) returned `"standing":"ALIVE"`,
  `"findings":[]`, exit `0` every time; `grep -rn
  "verify_ggen_v26_8_3|verifiers/" .github/workflows/*.yml
  tools/v26.8.1/justfile` after the edit found zero matches; `just
  --list | grep -i prd-ard` lists the new recipe and `just
  verify-prd-ard` reproduces the same JSON/exit code as the direct
  `python3` call; a byte-level pre/post diff of `justfile` confirmed
  exactly 7 additive lines, 0 removed, 0 altered — the raw whole-repo
  `git diff --stat` could not by itself isolate this (27 other
  pre-existing tracked-file changes plus ~85 pre-existing untracked
  paths, all confirmed unrelated via a `git status` snapshot taken
  before this session touched anything). `tickets/GL-EXP-048.md` and
  `tickets/OVERLAPS.md` are both untracked in git and were already
  present from an earlier drafting pass in this same session, with
  `OVERLAPS.md` already carrying an accurate disclosure row — this pass
  updated that row's status marker (`NOT_STARTED` → `EXECUTED`
  2026-08-21) rather than adding a second row, since exactly one
  disclosed row is the Acceptance criterion.

  `just ci-all` (both workspaces) run this pass: real exit code `0`.
  Root workspace — `cargo fmt --all -- --check` clean, `cargo check
  --all-targets --locked` clean, `cargo clippy --all-targets --locked --
  -D warnings` clean (zero warnings), `cargo test --all-targets --locked
  -- --test-threads=1` → 18 passed, 0 failed (lib 1, `analysis.rs` 7,
  `analysis_boundary.rs` 4, `contract.rs` 3, `exit_code.rs` 1,
  `lsp_boundary.rs` 2). `tools/v26.8.1` workspace — fmt/check/clippy
  clean (zero warnings), `cargo test --manifest-path
  tools/v26.8.1/Cargo.toml --all-targets --locked -- --test-threads=1` →
  18 passed, 0 failed (lib 3, `document_evidence_sabotage_tests` 13,
  `verifier_boundary.rs` 2). **36 tests passed, 0 failed** total, all 8
  fmt/check/clippy/test steps clean across both workspaces. Scope check:
  the branch diff vs `main` does not touch `appliance/bin/` or
  `tools/v26.8.1/step_two.py`, so the reference e2e script and
  `step_two.py` smoke check were correctly skipped this pass.

  `tickets/OVERLAPS.md`'s `GL-EXP-048` row updated `NOT_STARTED` →
  `EXECUTED` 2026-08-21; its ten-ticket reconciliation summary corrected
  from "one already-executed recipe" to "two already-executed recipes"
  (`GL-ERRC-022`, `GL-EXP-048`). The recipe stays CLI-only, not added to
  `ci`/`ci-all`/`v26-ci`, per the ticket's own Hard Law 3 — `GL-EXP-035`'s
  CI-gating question remains open.

## Not executed this pass (tracked, no code change)

None new this pass — `GL-EXP-048` reached `EXECUTED` with real, re-run
verification. The pre-existing gaps named in prior passes above remain
unchanged.

## See also (GL-EXP-048 pass)

- `tickets/GL-EXP-048.md` — source-of-truth `## Evidence`/`## Standing`
  sections for this entry, including the full falsifier re-run and the
  complete per-workspace `just ci-all` breakdown
- `docs/v26.9.1/RELEASE-NOTES.md` — matching narrative entry
  ("GL-EXP-048 executed — wire `verifiers/verify_ggen_v26_8_3.py` into
  `justfile` as `verify-prd-ard`")
- `tickets/OVERLAPS.md` — `GL-EXP-048` row updated `NOT_STARTED` →
  `EXECUTED` 2026-08-21

## Executed this pass — 2026-08-21 (GL-EXP-044)

- **feat(justfile)**: Add `reference-e2e`, a new, optional,
  suggestion-only recipe that pass-throughs to `bash
  appliance/bin/run-reference-e2e.sh` (`GL-EXP-044`) — the real,
  already-passing 12-script Verifier Appliance end-to-end regression
  harness that `README.md:14`'s `ALIVE` claim for the Verifier Appliance
  reference row already depends on, previously wired into no
  `justfile`/CI at all. Status: `EXECUTED`. Standing ceiling (ticket's
  own declared value): `PARTIAL_ALIVE`.

  All 7 Hard Laws and all 7 Falsifiers re-checked this session, all
  passing: `just reference-e2e` run directly returned exit `0`, final
  stdout line `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`, identical shape
  and exit behavior to the direct `bash
  appliance/bin/run-reference-e2e.sh` run; `just --list | grep -i
  "planning-max|propose-disposition|ci-all"` confirmed all three
  pre-existing recipes unchanged; a byte-level pre/post diff of
  `justfile` isolated the edit to exactly the 7-line `reference-e2e`
  block appended after `verify-prd-ard` (0 removed, 0 altered, on top of
  pre-existing unrelated dirty state already present on `justfile`);
  `git status --porcelain` line count was identical (113) before and
  after this ticket's edits, confirming only the 3 already-listed
  entries (`justfile`, `tickets/GL-EXP-044.md`, `tickets/OVERLAPS.md`)
  changed content, with no new/removed entries.
  `appliance/bin/run-reference-e2e.sh`, its 12 invoked scripts, and
  `.gitignore` all showed zero `git status --porcelain` output
  (confirmed untouched).

  `just ci-all` (both workspaces) also run this session as a general
  repository-health check: real exit code `0`. Root workspace — `cargo
  fmt --all -- --check` clean, `cargo check --all-targets --locked`
  clean, `cargo clippy --all-targets --locked -- -D warnings` clean
  (zero warnings), `cargo test --all-targets --locked` → 18 passed, 0
  failed (`ggen-legacy-lsp`: lib 1, main 0, `analysis.rs` 7,
  `analysis_boundary.rs` 4, `contract.rs` 3, `exit_code.rs` 1,
  `lsp_boundary.rs` 2). `tools/v26.8.1` workspace — fmt/check/clippy
  clean (zero warnings), `cargo test --all-targets --locked` → 18
  passed, 0 failed (lib 3, `document_evidence_sabotage_tests` 13,
  `project_coverage`/`subsystem_verifier` bins 0, `verifier_boundary.rs`
  2). **36 tests passed, 0 failed** total, no `error`/`FAILED`/`panic`
  lines in either log. Scope note: the currently committed diff
  (`main...HEAD`) touches `src/analysis.rs`, `tests/`,
  `tools/dsrust-disposition-proposer/`, `ontology`, and
  `planning/v26.8.20` — it does not touch `appliance/bin/` (`git diff
  --stat main...HEAD -- appliance/bin/`: empty), so this `ci-all` pass
  is a general health check, not a targeted re-verification of the new
  recipe; the recipe-specific check is the direct `just reference-e2e`
  run above.

  `tickets/OVERLAPS.md`'s `GL-EXP-044` row already read `EXECUTED`
  2026-08-21; its shared `justfile`-section `Reconciled` summary
  paragraph was found stale this pass (still counting "ten tickets ...
  six ... still pending / two already-executed recipes" and listing
  `GL-EXP-044` among "still NOT_STARTED" tickets, despite its own row
  already reading `EXECUTED`) and was corrected to "eleven tickets ...
  five ... still pending / three already-executed recipes"
  (`GL-ERRC-022`, `GL-EXP-044`, `GL-EXP-048`), with `GL-EXP-044` removed
  from the "still NOT_STARTED" enumeration. The recipe stays CLI-only,
  not added to `ci`/`ci-all`/`v26-ci`, per the ticket's own Hard Law 3.

## Not executed this pass (tracked, no code change)

None new this pass — `GL-EXP-044` reached `EXECUTED` with real, re-run
verification and a general `ci-all` health check. The pre-existing gaps
named in prior passes above remain unchanged.

## See also (GL-EXP-044 pass)

- `tickets/GL-EXP-044.md` — source-of-truth `## Evidence`/`## Execution
  evidence`/`## CI verification`/`## Standing` sections for this entry
- `docs/v26.9.1/RELEASE-NOTES.md` — matching narrative entry
  ("GL-EXP-044 executed — wire `appliance/bin/run-reference-e2e.sh` into
  `justfile` as `reference-e2e`")
- `tickets/OVERLAPS.md` — `GL-EXP-044` row confirmed `EXECUTED`; shared
  `justfile`-section `Reconciled` summary corrected to match 2026-08-21
