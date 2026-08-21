# Authored-boundary overlap registry

Cross-ticket boundary-registry check, per `AUDIT-REPORT.md`'s recommendation
(auditing all 19 `GL-*.md` tickets found the dominant, recurring defect was
coordination hygiene — two tickets both staking an authored-boundary claim
on the same file with neither disclosing the other). Rather than hand-write
bespoke overlap prose in every affected ticket (error-prone, as the audit
itself demonstrated — several such notes were one-directional or missing),
this file is the single canonical registry. Each affected ticket's Authored
boundary section links here instead of repeating the reconciliation prose.

**Rule going forward**: before admitting a new ticket, grep every existing
`tickets/GL-*.md`'s Authored boundary for the file paths the new ticket is
about to claim. If any overlap, add a row here — don't rely on remembering
to write it in both files.

**This rule was itself violated twice already** — once when `GL-EXP-001`
through `012` landed (6 tickets missing rows, backfilled), and again when
`GL-EXP-013`/`015` (`appliance/bin/verify-standing-portfolio.py`) and
`GL-EXP-011`/`012` (`tools/v26.8.20/observe_contract.py`) landed without
rows either — the exact same failure mode recurring a second time, purely
because the rule is manual prose, not machine-enforced. `GL-EXP-020`
(`NOT_STARTED`) now proposes exactly the fix: a
`scripts/verify_ticket_overlaps.py` that parses every ticket's Authored
boundary and asserts any file claimed 2+ times has a disclosed row here.
Until that ticket executes, this registry will keep needing manual
backfills — treat that as expected, not a surprise, on every future
exploration pass.

## `tools/v26.8.1/legacy_archaeology.py`

- `GL-ARCH-003` (executed): owns `mine_structured()`, `draft_candidates()`,
  `main()` dispatch, `_catalog_covered_hashes()`.
- `GL-ERRC-008` (`NOT_STARTED`): adds `pre_filter_candidates()` downstream
  of `draft_candidates()` — additive, does not modify `GL-ARCH-003`'s
  functions.
- **Reconciled**: no conflict — different functions in the same file,
  `GL-ERRC-008` strictly downstream of `GL-ARCH-003`'s output shape.

## `tools/v26.8.1/src/coverage_projection.rs`

- `GL-ERRC-015` (executed): deleted the dead `read_coverage_csv_bytes()` fn.
- `GL-ERRC-019` (`NOT_STARTED`): modifies `exact_head()`'s return
  type/behavior (lines ~412-421 pre-`GL-ERRC-015`).
- `GL-VERIFY-006` (`NOT_STARTED`): adds a new `ParityGateReceipt`
  struct/fns, placed "after `check_provenance_receipt`, before
  `exact_head`" — immediately adjacent to what `GL-ERRC-019` changes.
- `GL-EXP-003` (`NOT_STARTED`): raises `project_coverage_rows()`'s
  undifferentiated `None`-branch fallback — a different function again.
- `GL-EXP-007` (`NOT_STARTED`): raises `resolve_root()`'s content-blind
  `AGENTS.md` check — a fourth distinct function in this file.
- **Reconciled**: five tickets, same file, non-overlapping functions today
  (`GL-ERRC-015`/`GL-ERRC-019` already executed and shifted line numbers —
  any ticket citing a pre-execution line range for this file should
  re-verify it against current HEAD before executing, not trust the cited
  range). Execution order matters where insertion points are defined
  relatively: land `GL-ERRC-019` before `GL-VERIFY-006` if both are picked
  up in the same session, since `GL-VERIFY-006`'s insertion point is
  defined relative to `exact_head`, which `GL-ERRC-019` changes.
  `GL-EXP-003`/`GL-EXP-007` touch `project_coverage_rows`/`resolve_root`
  respectively — no adjacency conflict with the other three today, but
  re-verify line ranges at execution time regardless (per the pattern
  above, this file accumulates tickets faster than any other).

## `tools/v26.8.1/src/bin/subsystem_verifier.rs`

- `GL-EXP-001` (`EXECUTED`): eliminated the private duplicate
  `resolve_root()` (formerly lines 375-391), importing the canonical copy
  from `coverage_projection.rs` instead — confirmed gone from the file as
  of this session (`grep -n "^fn resolve_root"` returns no match).
- `GL-EXP-005` (`EXECUTED`): eliminated the private duplicate
  `fresh_git_head()` (was lines 243-251 pre-execution, now confirmed gone
  via `grep -n "^fn fresh_git_head" tools/v26.8.1/src/bin/subsystem_verifier.rs`
  returning no match) by importing the canonical `exact_head` from
  `coverage_projection.rs`, mirroring `GL-EXP-001`'s already-executed
  pattern for `resolve_root()` in this same file. See
  `tickets/GL-EXP-005.md`'s `## Evidence`/`## Standing` sections for the
  full falsifier + `just ci-all` output.
- `GL-EXP-029` (`NOT_STARTED`): eliminates the dead `legacy_disposition_summary`
  field (lines 45-56, the `Manifest` struct near the top of the file) —
  deserialize-only, `#[allow(dead_code)]`-marked, zero read sites, superseded
  by `reverify_legacy_disposition()`'s independent re-derivation from primary
  sources.
- `GL-EXP-031` (`NOT_STARTED`): adds a real re-hash-and-compare check for
  the deserialize-only `VerifierIdentity.content_sha256` field (lines 58-63)
  against the real file at `verifier_identity.path`, wiring it into the
  `self_cert_ok` self-certification check (lines 430-441) and
  `VerifierReport.self_cert_check_passed` (lines 141/232/626) — a different
  field of the same `#[allow(dead_code)]`-unused shape as `GL-EXP-029`'s
  target, but on `VerifierIdentity`, not `Manifest`, and a different defect
  class from either `GL-EXP-001`'s or `GL-EXP-005`'s duplicate-function
  findings.
- **Reconciled**: no conflict — four tickets, four disjoint regions of the
  same file (`Manifest` struct near the top vs. `VerifierIdentity` struct +
  `self_cert_ok`/`self_cert_check_passed` vs. `fresh_git_head()` at
  lines 243-251 vs. the now-removed `resolve_root()` that formerly lived
  near the bottom). Each ticket touches only its own region; re-verify
  current line numbers at execution time regardless, per this file's own
  standing guidance for `coverage_projection.rs`.

## `scripts/verify_foundry_bootstrap.py`

- `GL-ERRC-011` (executed): added `EXPECTED_*_SOURCE` comments +
  `STALE_REFERENCE_UNVERIFIABLE` status wiring, split the bundled
  `coordinates != expected_coordinates` comparison.
- `GL-MANUFACTURE-005` (`NOT_STARTED`): pre-derived diff extends
  `EXPECTED_DISPOSITIONS` with 3 new routing-state enum values.
- **Reconciled**: no conflict — different fields (`EXPECTED_*` hash
  constants vs. `EXPECTED_DISPOSITIONS` list), but `GL-MANUFACTURE-005`'s
  diff was drafted against the pre-`GL-ERRC-011` file; re-verify the exact
  surrounding lines before applying, since `GL-ERRC-011`'s comment/status
  additions shifted line numbers in this file.

## `foundry/bootstrap.yaml`

- `GL-ERRC-020` (`NOT_STARTED`): scoped to `runtime_dependency_admitted` /
  `standing_transferred` only.
- `GL-EXP-037` (`NOT_STARTED`): deletes the dead `terminal_condition` block
  (lines 93-105) — an unread, drifted duplicate of
  `schemas/final-evidence.schema.json`'s `finalPredicates` constants that
  nothing in the repo reads or validates. Does not touch
  `runtime_dependency_admitted`, `standing_transferred`, or any other
  top-level field `GL-ERRC-020` claims.
- **Reconciled**: no conflict — disjoint fields (`terminal_condition` block
  vs. `runtime_dependency_admitted`/`standing_transferred`). Both tickets
  should re-verify current line numbers at execution time if either lands
  first, since deleting `terminal_condition` shifts nothing above it but
  removes lines 93-106 entirely.

## `AGENTS.md`

- `GL-PLAN-002` (executed, concurrent ticket): owns the "concurrent ticket
  admission stanza" — its own header line only.
- `GL-ERRC-013` (`EXECUTED` — this section's status was stale, corrected
  here; the field it added is live at `AGENTS.md:10-29`): added the
  `drafted tickets (see tickets/):` header field listing all
  drafted/executed tickets by slug+status.
- `GL-EXP-050` (`EXECUTED` — re-run performed for real this session; at
  drafting time the field enumerated only 19 of 71 real `tickets/GL-*.md`
  files (52 missing, 73%), and by execution time the corpus had grown
  further to 75 files with 56 missing before the fix): re-ran
  `GL-ERRC-013`'s own field, replacing its body with a freshly re-derived
  list of all 75 tickets present on disk at execution time, each with its
  own current `**Status:**` line (or the no-Status fallback), correcting
  both the missing-tickets drift and the stale `GL-AUTO-001` status entry
  (listed as "no Status: line" though the file has since gained one) in
  the same pass. Scoped to replacing that field's body content only — no
  new field added, `GL-PLAN-002`'s stanza untouched.
- **Reconciled**: no conflict — `GL-ERRC-013` created the field (additive,
  didn't touch `GL-PLAN-002`'s stanza); `GL-EXP-050` only replaces that
  same field's already-established body content with a freshly re-derived
  version, per `GL-ERRC-013`'s own Hard Law 4 ("re-run at execution time").
  Neither touches `GL-PLAN-002`'s `active`/`concurrent` lines.

## `justfile`

- `GL-PLAN-002` (executed, concurrent ticket): owns the `planning-max`
  target only.
- `GL-ERRC-022` (executed): owns the `propose-disposition` target only —
  optional, suggestion-only wiring for `tools/dsrust-disposition-proposer`.
- `GL-EXP-004` (`NOT_STARTED`): adds a new `planning-cli` (or similarly
  named) target — optional, suggestion-only pass-through wiring for
  `planning/v26.8.7/cli.py`'s 10 subcommands.
- `GL-EXP-006` (`NOT_STARTED`): corrects `justfile:4`'s stale
  `gl-lsp-001-runtime.yml` header-comment citation (a doc fix, no recipe
  added or renamed).
- `GL-EXP-008` (`NOT_STARTED`): wires
  `scripts/verify_ggen_v26_8_1_migration.py` in as a new, optional recipe.
- `GL-EXP-012` (`NOT_STARTED`): wires `tools/v26.8.20/observe_contract.py`
  in as a new, optional recipe.
- `GL-EXP-032` (`NOT_STARTED`): adds five new recipes
  (`dsrust-fmt`/`dsrust-check`/`dsrust-clippy`/`dsrust-test`/`dsrust-ci`)
  for `tools/dsrust-disposition-proposer`, mirroring the existing
  `v26-*`/`v26-ci` pattern, and extends `ci-all`'s dependency list to
  `ci v26-ci dsrust-ci`. Does not touch `propose-disposition`'s existing
  recipe body or header comment.
- `GL-EXP-036` (`NOT_STARTED`): adds one new recipe (proposed name
  `docs-book`) that runs `mdbook build` against `docs/book.toml` — a
  pure pass-through wiring the already-working `mdbook` binary in as a
  new, optional recipe, mirroring the same additive/suggestion-only shape
  as `GL-EXP-004`/`008`/`012`. Does not touch any other recipe's body.
- `GL-EXP-038` (`NOT_STARTED`): corrects `justfile:35`'s `ci-all` header
  comment ("Run the full ladder for both workspaces") to name `ci-all`'s
  real, current dependency scope (2 of this repo's 4 independent Cargo
  projects) instead of the undercounted "both" — a doc-comment fix, lines
  35-36 only. Does not touch line 3-5 (`GL-EXP-006`'s scope), any recipe
  body including `ci-all`'s own dependency list on line 37
  (`GL-EXP-032`'s scope), or `propose-disposition`.
- `GL-EXP-044` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): added the new
  `reference-e2e` recipe, a pure pass-through to `bash
  appliance/bin/run-reference-e2e.sh` -- wires the existing, already-passing
  Verifier Appliance reference regression harness in as a new, optional
  recipe, mirroring the same additive/suggestion-only shape as
  `GL-EXP-004`/`008`/`012`/`036`/`048`. Confirmed additive-only by
  comparing `git diff -- justfile` immediately before and after this edit:
  the only delta on top of pre-existing unrelated dirty state is a 7-line
  block appended after `verify-prd-ard`, zero lines removed or altered --
  mirrors the same byte-level-diff verification `GL-EXP-048`'s own row
  used. Does not touch any other recipe's body or
  `appliance/bin/run-reference-e2e.sh` itself. `just reference-e2e` run
  this session: exit `0`, final stdout line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`.
- `GL-EXP-048` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): added the new
  `verify-prd-ard` recipe that runs `python3
  verifiers/verify_ggen_v26_8_3.py` with hardcoded `--subject-root .`,
  `--expected-repository seanchatmangpt/ggen-legacy`, `--expected-role
  EXECUTABLE_ARCHITECTURE_CORPUS` flags — the exact `justfile`-wiring
  resolution `GL-EXP-035` deferred and `GL-EXP-040`'s Hard Law 3
  reaffirmed as out of scope, now picked up as its own follow-up now that
  `GL-EXP-040` fixed the underlying `BUILD_BROKEN` digest mismatch
  (verifier re-confirmed `"standing":"ALIVE"`/`"findings":[]` this
  session, both before and immediately before the edit). Confirmed
  additive-only via a byte-level pre/post diff of `justfile`: exactly 7
  new lines, zero removed or altered — mirrors the same
  additive/suggestion-only shape as `GL-EXP-004`/`008`/`012`/`036`/`044`,
  not added to `ci`/`ci-all`/`v26-ci`. Does not touch any other recipe's
  body or `verifiers/verify_ggen_v26_8_3.py` itself. `just ci-all` (both
  workspaces) re-run this session: exit `0`, 36/36 tests passing.
- **Reconciled**: no conflict — eleven tickets, eleven distinct concerns
  (five new recipe names or recipe groups still pending, two doc-comment
  fixes on disjoint header comments, three already-executed recipes
  — `GL-ERRC-022`'s `propose-disposition`, `GL-EXP-044`'s
  `reference-e2e`, and `GL-EXP-048`'s `verify-prd-ard` — and one
  dependency-list extension on `ci-all`) in the same file. Corrected
  2026-08-21 from the prior "ten tickets ... six ... still pending / two
  already-executed recipes" count, which had gone stale once
  `GL-EXP-044` reached `EXECUTED` above without this shared summary being
  updated to match. Each of `GL-EXP-004`/`008`/`012`/`032`/`036`/`038`
  (still `NOT_STARTED`) should re-verify `justfile`'s current recipe list
  before executing (`just --list`) rather than assume prior recipes are
  still exactly as quoted here — this file has now accumulated 11
  tickets total (including `GL-PLAN-002`/`GL-ERRC-022`) and is the
  second-most-contended file in the registry after
  `coverage_projection.rs`. `GL-EXP-032` additionally
  changes `ci-all`'s own dependency list (currently `ci v26-ci`); any
  other ticket that later also wants to extend `ci-all` should re-read its
  current dependency list rather than assume it still reads exactly `ci
  v26-ci`. `GL-EXP-038`'s own Hard Law 5 already accounts for executing
  after `GL-EXP-032` has changed that dependency list — it re-derives its
  replacement wording from whatever `ci-all` actually depends on at
  execution time rather than hardcoding today's `ci v26-ci`. `GL-EXP-044`
  and `GL-EXP-048` do not touch `ci-all`'s dependency list at all (each
  ticket's own Hard Law 3: local wiring only, not added to
  `ci`/`ci-all`/`v26-ci`), so neither has an ordering dependency on
  `GL-EXP-032`/`GL-EXP-038`.

## `appliance/bin/_shared.py`

- `GL-EXP-013` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): created the module, adding exactly
  `sha256_file()`/`read_json()` — confirmed via `ls appliance/bin/_shared.py` and
  `grep -n "^def " appliance/bin/_shared.py` showing exactly these two functions, nothing more
  (its own Hard Law 1/Falsifier 3).
- `GL-EXP-017` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): appended `write_json()` — `_shared.py`
  already existed (created by `GL-EXP-013` above), so this appended rather than created (its
  own Hard Law 3), leaving `sha256_file`/`read_json` byte-identical and untouched, confirmed
  via `grep -n "^def " appliance/bin/_shared.py` showing exactly three functions
  (`sha256_file`, `read_json`, `write_json`), nothing more.
- `GL-EXP-041` (`NOT_STARTED`): adds `tree_inventory()`, `tree_digest()`, `sha256_bytes()`,
  `canonical()` (the 5-file untyped variant only — explicitly excludes the differently-typed
  `canonical()` in `build-subsystem-evidence.py`/`verify-subsystem-evidence.py`) — appends to
  the now-existing module (its own Hard Law 5).
- `GL-EXP-045` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): appended `typed_canonical(value: Any)
  -> bytes` — the typed `canonical()` pair `GL-EXP-041` deliberately excluded above, named
  `typed_canonical()` to avoid colliding with `GL-EXP-041`'s still-unlanded untyped
  `canonical(obj)` — confirmed via `grep -n "^def " appliance/bin/_shared.py` showing exactly
  four functions (`sha256_file`, `read_json`, `write_json`, `typed_canonical`), the prior three
  untouched. Also added `from typing import Any` to `_shared.py`'s imports (needed to preserve
  the typed signature byte-for-byte, per this ticket's own Hard Law 1).
- `GL-EXP-049` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): appended `digest_sources()` and
  `check_map()` — the `build-subsystem-evidence.py`/`verify-subsystem-evidence.py` duplicate
  pair `GL-EXP-045` deliberately excluded from its own scope (`GL-EXP-045`'s Authored boundary
  states verbatim "No change to `sha256_file`, `exact_head`, `read_json`, `digest_sources`,
  `check_map`, or any other function in either file") — appended to the now-existing module
  under the helpers' existing names, byte-for-byte matching the bodies both files previously
  defined privately (md5 `7e5fd2e7826bec2300dcdfacbdac0f64` for `digest_sources()`,
  `e226b84faa099e4493cc8811fee3d5ca` for `check_map()`, both reconfirmed this session before and
  after the move). Confirmed via `grep -n "^def " appliance/bin/_shared.py` showing exactly six
  functions (`sha256_file`, `read_json`, `write_json`, `typed_canonical`, `digest_sources`,
  `check_map`), the prior four untouched and no collision with any name `GL-EXP-041` (still
  `NOT_STARTED`) plans to add.
- **Reconciled**: no conflict — five tickets, each adding disjoint, distinctly-named functions
  to the same new module, none modifying another's addition. All five explicitly forbid
  removing or truncating a sibling's contribution (`GL-EXP-013` Hard Law 2, `GL-EXP-017` Hard
  Law 3, `GL-EXP-041` Hard Law 5, `GL-EXP-045` Hard Law 5, `GL-EXP-049` Hard Law 5), so any
  execution order was/is safe as long as each ticket only adds its own functions. `GL-EXP-013`
  executed first and created `_shared.py` with exactly `sha256_file()`/`read_json()`;
  `GL-EXP-017` executed next, appending `write_json()` alone and leaving the prior two functions
  untouched; `GL-EXP-045` executed next, appending `typed_canonical()` alone and leaving the
  prior three functions untouched; `GL-EXP-049` executed next, appending `digest_sources()` and
  `check_map()` alone and leaving the prior four functions untouched. `GL-EXP-041` remains
  `NOT_STARTED` and should append to the now-existing module (which now carries six functions,
  not four), re-verifying its current contents at execution time rather than assuming it still
  holds only `sha256_file`/`read_json`/`write_json`/`typed_canonical`.

## `appliance/bin/verify-standing-portfolio.py`

- `GL-EXP-013` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): consolidated the private
  `sha256_file`/`read_json` (formerly lines 10-14) into an import from the new
  `appliance/bin/_shared.py` module — confirmed gone via
  `grep -n "^def sha256_file\|^def read_json" appliance/bin/verify-standing-portfolio.py`
  returning no match.
- `GL-EXP-015` (`NOT_STARTED`): raises the `challenge_files` loop's
  undifferentiated `except Exception: pass` (lines 44-50 pre-`GL-EXP-013`) — a different
  region of the same file.
- **Reconciled**: no conflict — disjoint line ranges, different concerns
  (helper consolidation vs. error-handling). `GL-EXP-013`'s edit shifted line numbers in this
  file (the two private `def` blocks collapsed to one `from _shared import` line); `GL-EXP-015`
  should re-verify the `challenge_files` loop's current line numbers at execution time rather
  than trust the pre-`GL-EXP-013` range above, per this file's own standing guidance for
  `coverage_projection.rs`.

## `tools/v26.8.20/observe_contract.py`

- `GL-EXP-011` (`NOT_STARTED`): raises `git_head()`'s undifferentiated
  `None` fallback.
- `GL-EXP-012` (`NOT_STARTED`): wires the script into `justfile` as an
  optional recipe.
- **Reconciled**: no conflict — one touches the script's internal logic,
  the other only adds an external `justfile` entry point.

## `appliance/bin` (`exact_head` vs. `sha256_file`/`read_json`)

- `GL-EXP-013` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): consolidated `sha256_file()`/
  `read_json()` into `appliance/bin/_shared.py` across 10 files, 4 of which
  (`build-document-evidence-index.py`, `build-subsystem-evidence.py`,
  `verify-subsystem-evidence.py`, `verify-crown.py`) are shared with the
  row below — did not touch `exact_head()` in any of them (confirmed via
  `git diff --stat`, which lists only the private `sha256_file`/`read_json` def lines and one
  new `from _shared import ...` line per file).
- `GL-EXP-023` (`NOT_STARTED`): raises the same four files' (plus a fifth,
  `observe-project.py`, not claimed by `GL-EXP-013`) duplicated
  `exact_head()` out of an undifferentiated `"UNKNOWN"` collapse.
- `GL-EXP-045` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): consolidated the typed `canonical()`
  (line 17 in both `build-subsystem-evidence.py` and `verify-subsystem-evidence.py` at execution
  time — shifted from the ticket's drafted line 15 by `GL-EXP-013`'s prior `from _shared import`
  insertion, re-verified before editing) into `appliance/bin/_shared.py` as `typed_canonical()` —
  a third, disjoint region of the same two files, touching only these two of the four/five files
  the rows above share; did not touch `exact_head()` or `sha256_file`/`read_json` call sites in
  either file (confirmed via `git diff --stat`, which lists only the removed `def canonical`
  block, one rewritten `from _shared import` line, and one rewritten call-site line per file).
- `GL-EXP-049` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): consolidated `digest_sources()` and
  `check_map()` (line 24 and line 40 respectively in both `build-subsystem-evidence.py` and
  `verify-subsystem-evidence.py` at execution time — unchanged from the ticket's drafted line
  numbers, since `GL-EXP-023` had not yet landed and shifted anything above them) into
  `appliance/bin/_shared.py` — a fourth, disjoint region of the same two files, sitting between
  `GL-EXP-023`'s (still `NOT_STARTED`) `exact_head()` claim (line 17) and each file's own
  build/verify-specific logic (`primary_result`/`main` in the build script,
  `expected_primary`/`main` in the verify script); did not touch `exact_head()`,
  `sha256_file`/`read_json`, or `canonical`/`typed_canonical` call sites in either file
  (confirmed via `git diff --stat`, which lists only the removed `def digest_sources`/`def
  check_map` blocks, one rewritten `from _shared import` line, and zero rewritten call-site
  lines per file — the 5 call sites in each file already called the bare names `digest_sources`/
  `check_map`, so importing those names from `_shared` under the same names left every call site
  textually unchanged). Regression proof: `bash appliance/bin/run-reference-e2e.sh` exits `0`
  ending `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`, both immediately before and immediately after
  this change (both runs captured this session).
- **Reconciled**: no conflict — in every shared file, `canonical()` preceded `sha256_file()`
  (now removed by `GL-EXP-013`, replaced by an import), which preceded `exact_head()`, which
  preceded `digest_sources()`/`check_map()` (now also removed by `GL-EXP-049`, replaced by an
  import) — four disjoint, non-overlapping function regions in file order pre-`GL-EXP-013`.
  `GL-EXP-045` re-verified current line numbers at execution time (line 17, not the ticket's
  drafted line 15) rather than trusting the pre-`GL-EXP-013` range, confirming the region was
  still disjoint from `GL-EXP-013`'s `sha256_file`/`read_json` import line and `GL-EXP-023`'s
  (still `NOT_STARTED`) `exact_head()` claim. `GL-EXP-049` likewise re-verified current line
  numbers at execution time (unchanged at line 24/line 40, since neither `GL-EXP-023` nor any
  other sibling had landed a line-shifting change above this region by execution time) before
  editing. `GL-EXP-023` remains `NOT_STARTED` and should likewise re-verify current line numbers
  at execution time rather than trust the pre-`GL-EXP-013` ranges above, per this file's own
  standing guidance for `coverage_projection.rs`.

## `.github/workflows/ci.yml`

- `GL-ERRC-009` (`EXECUTED`): owns exactly one existing step, `"Admit
  exact head and one-workflow topology"` — its `expected`/`actual`
  workflow-file-list comparison and the `workflow_count` it prints.
- `GL-EXP-032` (`NOT_STARTED`): adds new steps to the existing `verify`
  job, appended after the five existing Rust steps, running
  `tools/v26.8.1` and `tools/dsrust-disposition-proposer`'s
  fmt/check/clippy/test ladders via `--manifest-path` — does not touch
  the "Admit exact head and one-workflow topology" step, its
  expected/actual comparison, or the `workflow_count` it emits (stays
  `2`, since `GL-EXP-032` adds no new workflow file).
- **Reconciled**: no conflict — `GL-ERRC-009`'s claim is scoped to one
  named step; `GL-EXP-032`'s new steps are additive, appended later in
  the same job, and disjoint from that step's own logic.

## `.github/workflows/planning-v26-8-7.yml`

- `GL-PLAN-002` (`admitted concurrent executable ticket`): owns the whole
  file as part of its Authored boundary (the workflow this ticket's own
  Acceptance bar is meant to gate).
- `GL-EXP-024` (`NOT_STARTED`): adds one new step (`python3 -m unittest
  discover -s planning/v26.8.7/tests -v`) to the existing job, enforcing
  `GL-PLAN-002`'s own already-stated three-command Acceptance bar, of
  which the workflow currently runs only two.
- **Reconciled**: no conflict — `GL-EXP-024`'s change is additive (one new
  step appended to the existing job), does not alter `GL-PLAN-002`'s own
  scope, Hard Laws, or the workflow's two existing steps.

## `src/backend.rs`, `src/capabilities.rs`, `scripts/verify_lsp_contract.py`

- `GL-LSP-001` (standing: `ALIVE` source-contract rail): claims these three
  files as the basis for its own standing via `## Observable contract`
  point 4 ("Advertise every implemented capability truthfully"), `##
  Positive witnesses` ("every non-framework received method has a
  `LanguageServer` handler"), and `## Falsifiers` ("capability without
  handler") -- it has no formal `## Authored boundary` section (it
  predates that convention, using `## Identity` instead).
- `GL-EXP-027` (`NOT_STARTED`): finds that `verify_lsp_contract.py`'s sole
  content-level checks (`HANDLER_ABSENT`, `CAPABILITY_ABSENT`) are purely
  textual presence checks with no inspection of handler-body behavior, so
  14 advertised capabilities (`definitionProvider`, `referencesProvider`,
  `renameProvider`, `workspaceSymbolProvider`, `foldingRangeProvider`,
  `semanticTokensProvider`, `inlayHintProvider`, `codeLensProvider`,
  `callHierarchyProvider` x3, `typeHierarchyProvider` x3) are implemented
  as unconditional no-op stubs in `src/backend.rs` and pass the gate
  identically to a real implementation. `GL-EXP-027` proposes only a new
  finding class inside `verify_lsp_contract.py`'s existing report schema
  -- it does not modify `src/backend.rs`, `src/capabilities.rs`, or
  `GL-LSP-001.md` itself.
- **Reconciled**: no functional conflict -- `GL-EXP-027`'s scope is
  additive to `verify_lsp_contract.py` only, and its finding is a gap
  *within* the same standing claim `GL-LSP-001` already makes about these
  files, not a change that alters `GL-LSP-001`'s own scope, Hard Laws, or
  claimed files. `GL-LSP-001`'s `ALIVE` source-contract standing should be
  re-read as "the gate's own textual checks pass," not as "every
  advertised capability is behaviorally real," until `GL-EXP-027` (or a
  follow-on implementing real handler logic) lands.
- **`tickets/GL-LSP-001.md` itself — disclosure**: `GL-EXP-046`
  (`EXECUTED` 2026-08-21, was `NOT_STARTED`) is the first ticket to claim
  write access to `GL-LSP-001.md` (as opposed to citing it read-only,
  which 9 other tickets do per this session's `grep -l "GL-LSP-001.md"
  tickets/GL-*.md` check). Its scope was line 71's "not yet merged (draft PR
  `seanchatmangpt/lsp-max#22`)" bullet only — a live-`gh`-verified
  correction, disjoint from `GL-EXP-027`'s `verify_lsp_contract.py`-only
  scope above and from every other section of `GL-LSP-001.md`
  (`## Identity`, `## Admission`, `## Observable contract`, `## Positive
  witnesses`, `## Falsifiers`, `## Acceptance`, and the rest of
  `## Standing`). No conflict with `GL-EXP-027`.

## `authority/v26.8.3/release-authority.json`, `product/v26.8.3/PRD.md`, `architecture/v26.8.3/ARD.md`

- `GL-EXP-035` (`NOT_STARTED`): the pure finding that the live
  `verifiers/verify_ggen_v26_8_3.py --subject-root .` run reports
  `"standing":"BUILD_BROKEN"` with two `DOCUMENT_DIGEST_MISMATCH`
  findings against these two documents' digests as pinned in the
  authority JSON. Its own Hard Laws explicitly forbid it from changing
  either digest or editing either document — it names three candidate
  resolutions and defers the choice to a follow-up.
- `GL-EXP-040` (`EXECUTED`): that follow-up. Picks resolution (a) from
  `GL-EXP-035`'s Outcome — the pinned digests are wrong, not the
  documents — and is authorized, when executed, to change exactly
  `documents[0].sha256` and `documents[1].sha256` inside
  `authority/v26.8.3/release-authority.json`. It does not edit
  `product/v26.8.3/PRD.md` or `architecture/v26.8.3/ARD.md`, and does not
  wire the verifier into CI (`GL-EXP-035` resolution (c), left as its own
  separate follow-up).
- **Reconciled**: no conflict — `GL-EXP-035`'s Authored boundary is
  `tickets/GL-EXP-035.md` only (it never claims write access to the
  authority JSON or either document); `GL-EXP-040`'s Authored boundary
  adds exactly one file, `authority/v26.8.3/release-authority.json`,
  disjoint from `GL-EXP-035`'s own scope. Both tickets are `NOT_STARTED`;
  whichever executes first should re-run
  `verifiers/verify_ggen_v26_8_3.py` before acting, per each ticket's own
  Falsifiers, since the other may have already changed the live standing.

## `CLAUDE.md`

- `GL-EXP-038` (`NOT_STARTED`): corrects `CLAUDE.md:92`'s Verify-section
  line (`just ci-all # cargo fmt/check/clippy/test, both workspaces`) to
  name `ci-all`'s real, current dependency scope instead of the
  undercounted "both" — the same fix, and the same real-scope wording, as
  its paired `justfile:35-36` edit above. No other `CLAUDE.md` line
  changes. First entry in this section — no prior ticket's `##
  Authored boundary` claims any part of `CLAUDE.md` (checked this
  session: 6 tickets cite `CLAUDE.md` as supporting evidence for their own
  standing claims — `GL-CONTRACT-004`, `GL-ARCH-003`, `GL-ERRC-013`,
  `GL-MANUFACTURE-005`, `GL-RECEIPT-007`, `GL-VERIFY-006` — but none
  stakes an edit claim on the file itself).
- **Reconciled**: no conflict — one ticket, one line.

## `Cargo.toml` (root)

- `GL-EXP-025` (`EXECUTED`): deleted the unused direct `tracing = "0.1"`
  line, formerly line 27.
- `GL-EXP-046` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): corrected the
  `# PROVISIONAL PIN:` comment above the `lsp-max` dependency (was lines
  20-24, now 6 lines instead of 5 since the corrected prose grew by one
  line) — its stale "unmerged branch"/"not yet merged" framing,
  disproven via a real `gh pr view` re-verified fresh at execution time
  (PR #22 merged 2026-08-04, still `MERGED` with no discrepancy from
  drafting). Did not touch the `lsp-max = { git = ..., rev = ... }`
  dependency line itself (byte-identical, now sitting on line 26) or any
  other dependency declaration.
- **Reconciled**: no conflict — `GL-EXP-025`'s change was on line 27,
  already executed and gone; `GL-EXP-046`'s scope (the comment block,
  prose only) was a disjoint, adjacent region. Both now `EXECUTED`.

## `governance/production-gaps.md`

- `GL-EXP-006` (`EXECUTED`): corrected the stale `gl-lsp-001-runtime.yml`
  citation, scoped explicitly to line 31 only.
- `GL-EXP-046` (`EXECUTED` 2026-08-21, was `NOT_STARTED`): corrected the
  `lsp-max` dependency bullet's stale "pinned to an unmerged branch"
  framing (was lines 58-60) — the same live-`gh`-verified correction, fresh
  re-checked at execution time, as its paired `Cargo.toml` edit above.
- **Reconciled**: no conflict — disjoint line ranges (line 31 vs. the
  lsp-max bullet), different claims (a stale CI-workflow-filename citation
  vs. a stale PR-merge-status claim). Both now `EXECUTED`.

## `tools/v26.8.1/step_two.py`

- `GL-ERRC-014` (admitted, `NOT_STARTED`): Authored boundary claims the
  whole file (`tools/v26.8.1/step_two.py   # STALE_REFERENCE_UNVERIFIABLE
  status on unreachable-git-object path`), but its Outcome text targets one
  specific failure path — detecting and typing the downstream effect of
  dereferencing the unreachable git object
  `6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6` cited in
  `docs/v26.8.1/document-evidence-index.json`/`ontology/v26.8.1/document-
  evidence.ttl` (consumed indirectly via the `subsystem-evidence-manifest`
  command's downstream data). Its Outcome section never names `git()` or
  `run_command()`.
- `GL-EXP-051` (admitted, `NOT_STARTED`): Authored boundary is narrower and
  explicit — `git()` (lines 55-62) and `run_command()` (lines 65-103) only,
  the file's two generic subprocess wrapper functions, adding a `timeout=`
  bound and caught, distinguishable handling for a spawn failure at every
  call site. Independent of which command is being invoked or why any one
  command might fail.
- **Reconciled**: file-level overlap only (both tickets' Hard Law 3/4
  `git diff --stat` clauses claim `tools/v26.8.1/step_two.py`), no known
  function-level overlap — `GL-ERRC-014`'s likely landing point is
  somewhere in `execute()`'s command-result/gate handling (downstream of a
  `run_command()` call's returned `CommandEvidence`, not inside `git()`/
  `run_command()` themselves), while `GL-EXP-051` touches only the two
  wrapper function bodies. Re-verify both tickets' target line ranges
  against current HEAD before executing either, and prefer landing
  `GL-EXP-051` first if both are picked up in the same session — its
  change does not alter `run_command()`'s existing return type/signature
  on the happy path (Hard Law 1), so `GL-ERRC-014`'s downstream
  `CommandEvidence` consumption should remain unaffected regardless of
  execution order, but this has not been proven by executing both, only
  asserted from each ticket's own stated scope.

## See also

`tickets/AUDIT-REPORT.md` — the full 19-ticket audit that surfaced this
pattern, including the specific factual/citation errors (wrong line
numbers, a fabricated `ADR-002` citation, a miscounted grep result) fixed
directly in their respective ticket files rather than tracked here, since
those are per-ticket correctness issues, not cross-ticket coordination
issues.
