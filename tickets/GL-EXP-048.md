# GL-EXP-048 — Wire `verifiers/verify_ggen_v26_8_3.py` into `justfile` as an optional, suggestion-only recipe, now that `GL-EXP-040` has fixed the digest mismatch that blocked it

**Status:** `EXECUTED` 2026-08-21 -- justfile recipe landed and re-verified this
session, `just ci-all` (both workspaces) clean, 36/36 tests passing
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`verifiers/verify_ggen_v26_8_3.py` (113 lines, confirmed via `wc -l` this
session) is a real, independent verifier for this repo's own v26.8.3
PRD/ARD authority bundle. `GL-EXP-035` (read in full this session) found it
`BUILD_BROKEN` (two `DOCUMENT_DIGEST_MISMATCH` findings) and named three
candidate resolutions without choosing between them, explicitly deferring
resolution (c) ("wire `verifiers/verify_ggen_v26_8_3.py` into
`justfile`/CI") to "its own, separately scoped follow-up" (`GL-EXP-035`
Hard Law 2, Authored-boundary text). `GL-EXP-040` (read in full this
session, `Status: EXECUTED`) picked resolution (a) instead -- corrected the
two `sha256` fields in `authority/v26.8.3/release-authority.json` -- and
its own Hard Law 3 reaffirms "This ticket does not wire
`verifiers/verify_ggen_v26_8_3.py` into `justfile` or
`.github/workflows/`." Neither ticket proposes the wiring itself; both
leave it open.

Re-ran the verifier fresh this session, independently of both tickets'
cited output:

```console
$ python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
    --expected-repository seanchatmangpt/ggen-legacy \
    --expected-role EXECUTABLE_ARCHITECTURE_CORPUS
{"claim_ceiling":"PRD_ARD_AUTHORITY_BUNDLE_ONLY","components":17,
"content_root_sha256":"a7611d6624a2b1329ba530ab1050a912c593e16fbf8f41a06c57df91eaa257e1",
"direct_actuation":false,"findings":[],"interfaces":2,"requirements":24,
"schema_version":"chatman.v26.8.3.prd-ard-verifier/1","self_certification":false,
"standing":"ALIVE","subject_base_sha":"70e599a599fedb7c62c965377cc2f80df1fa01ec",
"subject_repository":"seanchatmangpt/ggen-legacy",
"subject_role":"EXECUTABLE_ARCHITECTURE_CORPUS"}
$ echo $?
0
```

`standing: "ALIVE"`, `findings: []`, exit `0` -- confirms `GL-EXP-040`'s fix
is live and holding against the current checkout (`git rev-parse HEAD` this
session: `bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's
declared Base and both `GL-EXP-035`'s and `GL-EXP-040`'s declared Base).
The exact concern that made `GL-EXP-035` decline to wire this in on its own
authority -- "gating CI on a currently-`BUILD_BROKEN` check" -- no longer
applies to the CLI-wiring half of that decision (this ticket is scoped to
`justfile` only, not `.github/workflows/`; see Hard Law 3).

**Confirmed still unwired.** `grep -rn "verify_ggen_v26_8_3\|verifiers/"
.github/workflows/*.yml justfile tools/v26.8.1/justfile` (run fresh this
session) returns zero matches. `grep -il "verify_ggen_v26_8_3"
tickets/GL-*.md` (67 tickets total, `ls tickets/GL-*.md | wc -l`) returns
exactly `tickets/GL-AUTO-001.md`, `tickets/GL-EXP-035.md`, and
`tickets/GL-EXP-040.md`. Direct inspection of `GL-AUTO-001.md`'s one hit
(line 110 this session) confirms it is a bare filename inside a single-line,
115-path `REFUSED:FORBIDDEN_DIFF:` dump -- not a substantive claim over the
file, and not a proposal to wire it anywhere. No ticket in the corpus
currently proposes this wiring.

This follows the same additive, suggestion-only `justfile` pattern already
established six times in this repo: `GL-ERRC-022` (`propose-disposition`,
executed), `GL-EXP-004` (`planning-cli`, proposed), `GL-EXP-008`
(wraps `scripts/verify_ggen_v26_8_1_migration.py`, proposed), `GL-EXP-012`
(wraps `tools/v26.8.20/observe_contract.py`, proposed), `GL-EXP-036`
(`docs-book`, proposed), and `GL-EXP-044` (`reference-e2e`, proposed) --
confirmed by reading each ticket's `justfile`-touching lines this session
(`grep -n "justfile" tickets/GL-ERRC-022.md tickets/GL-EXP-004.md
tickets/GL-EXP-008.md tickets/GL-EXP-012.md tickets/GL-EXP-036.md
tickets/GL-EXP-044.md`). Unlike `GL-EXP-008`'s wrapped script (which
`REFUSED`s against the real `~/ggen` sibling today, per that ticket's own
"Honest caveat" section) or `GL-EXP-012`/`GL-EXP-036`/`GL-EXP-044`'s
not-yet-verified-in-this-session state, this ticket's wrapped verifier is
confirmed `ALIVE`/`findings: []` in the exact command re-run above -- the
new recipe would report success on first use, not a pre-existing failure.
This ticket still keeps the recipe out of `ci`/`ci-all`/`v26-ci` (Hard Law
3) -- not because the check currently fails, but because `GL-EXP-035`
explicitly reserved the CI-gating decision itself (as opposed to a bare CLI
entry point) for a dedicated follow-up, and a future document edit could
re-introduce a digest mismatch without that necessarily meaning the
release itself is broken (the same asymmetry `GL-ERRC-022`/`GL-EXP-004`
already apply to their own optional recipes).

## Authored boundary

(Cross-ticket file overlaps are tracked in `tickets/OVERLAPS.md` -- this
ticket adds a disclosed row to the existing `## \`justfile\`` section
there, in the same write, alongside the nine tickets already recorded.)

```text
justfile                          # new recipe only, additive
tickets/GL-EXP-048.md
tickets/OVERLAPS.md               # new disclosed row in the existing `justfile` section
```

No change to `verifiers/verify_ggen_v26_8_3.py` -- this ticket wraps the
existing, already-working, already-`ALIVE` script; it does not modify its
verification logic, its `standing` values, or its report schema. No change
to `authority/v26.8.3/release-authority.json`, `product/v26.8.3/PRD.md`,
or `architecture/v26.8.3/ARD.md` -- those are `GL-EXP-035`'s/`GL-EXP-040`'s
scope, not this ticket's. No change to any existing `justfile` recipe body
(`fmt`, `check`, `clippy`, `test`, `ci`, `v26-fmt`, `v26-check`,
`v26-clippy`, `v26-test`, `v26-ci`, `ci-all`, `planning-max`,
`propose-disposition`) -- this ticket adds one new, tenth recipe-adding
entry to `justfile`'s already-contended history per `OVERLAPS.md`.

## Hard laws

1. The new recipe is a pure pass-through to `python3
   verifiers/verify_ggen_v26_8_3.py --subject-root . --expected-repository
   seanchatmangpt/ggen-legacy --expected-role
   EXECUTABLE_ARCHITECTURE_CORPUS` -- it must not reimplement, swallow, or
   reinterpret the script's `standing`/`findings`/exit-code behavior.
2. `--subject-root`, `--expected-repository`, and `--expected-role` are
   hardcoded in the recipe body to the values above -- this is a
   self-check of this repo against its own fixed identity
   (`seanchatmangpt/ggen-legacy` / `EXECUTABLE_ARCHITECTURE_CORPUS`), not a
   general-purpose cross-repo comparison tool needing caller-supplied
   arguments (unlike `GL-EXP-008`'s `--source-root`, which stays
   caller-supplied because that script compares two different repos).
3. The new recipe is **not** added to `ci`, `ci-all`, or `v26-ci` -- CLI
   wiring only, mirroring `GL-ERRC-022`/`GL-EXP-004`/`GL-EXP-008`/
   `GL-EXP-012`/`GL-EXP-036`/`GL-EXP-044`'s identical discipline. Whether
   this check should ever become a CI gate is `GL-EXP-035`'s named,
   still-open resolution-(c) decision -- this ticket satisfies only the
   "CLI-invocable" half of it, not the "CI-gating" half.
4. This ticket does not touch any existing `justfile` recipe's body,
   including `planning-max` and `propose-disposition`.
5. Before landing, re-run the exact Outcome command and confirm
   `"standing":"ALIVE"` with `"findings":[]` still holds -- if an
   intervening change has re-broken the digests, this ticket's premise
   ("now safe to wire in") no longer holds and execution must stop and
   re-verify against `GL-EXP-035`/`GL-EXP-040` rather than silently wiring
   in a recipe that reports failure on first use.

## Falsifiers

- Re-running `python3 verifiers/verify_ggen_v26_8_3.py --subject-root .
  --expected-repository seanchatmangpt/ggen-legacy --expected-role
  EXECUTABLE_ARCHITECTURE_CORPUS` at execution time reports anything other
  than `"standing":"ALIVE"` / `"findings":[]` (would mean `GL-EXP-040`'s
  fix has regressed; re-verify against `GL-EXP-035`/`GL-EXP-040` before
  proceeding, per Hard Law 5).
- `grep -rn "verify_ggen_v26_8_3\|verifiers/" .github/workflows/*.yml
  justfile tools/v26.8.1/justfile` at execution time already finds a real
  match (would mean this wiring already exists, contradicting this
  ticket's "unwired" claim).
- `just --list` after the edit does not list the new recipe, or `just
  <new-recipe-name>` does not reproduce the same `ALIVE`/`findings: []`
  JSON as the direct `python3` invocation.
- `git diff --stat` after execution shows any file changed other than
  `justfile`, `tickets/GL-EXP-048.md`, and `tickets/OVERLAPS.md`.
- `git diff justfile` shows any changed line outside the new recipe's own
  added lines (would mean an existing recipe was altered, violating Hard
  Law 4).

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the verifier is live-ALIVE before wiring anything:
python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
  --expected-repository seanchatmangpt/ggen-legacy \
  --expected-role EXECUTABLE_ARCHITECTURE_CORPUS
  # expect: "standing":"ALIVE", "findings":[], exit 0

# Confirm nothing wires it in yet:
grep -rn "verify_ggen_v26_8_3\|verifiers/" .github/workflows/*.yml justfile tools/v26.8.1/justfile
  # expect: no output

# Add a new, additive recipe to justfile, e.g.:
#   # GL-EXP-048: optional, suggestion-only self-check of this repo's own
#   # v26.8.3 PRD/ARD authority bundle. Not part of ci/ci-all/v26-ci.
#   verify-prd-ard:
#       python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
#         --expected-repository seanchatmangpt/ggen-legacy \
#         --expected-role EXECUTABLE_ARCHITECTURE_CORPUS

just --list | grep -i prd-ard
  # expect: verify-prd-ard listed

just verify-prd-ard
  # expect: same "standing":"ALIVE" / "findings":[] JSON, exit 0

# Confirm the blast radius:
git diff --stat
  # expect: only justfile, tickets/GL-EXP-048.md, tickets/OVERLAPS.md
git diff justfile
  # expect: only the new recipe's added lines; no existing recipe altered
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base and both `GL-EXP-035`'s and
  `GL-EXP-040`'s declared Base.
- Direct `Read` of `tickets/GL-EXP-035.md` in full this session: confirms
  it names resolution (c) ("wire `verifiers/verify_ggen_v26_8_3.py` into
  `justfile`/CI") and explicitly defers it ("a repo-owner or dedicated
  follow-up ticket's call"), and confirms its Hard Law 2 ("This ticket does
  not wire `verifiers/verify_ggen_v26_8_3.py` into `justfile` or
  `.github/workflows/`").
- Direct `Read` of `tickets/GL-EXP-040.md` in full this session: confirms
  `Status: EXECUTED`, confirms it picked resolution (a) (digest
  correction), confirms its Hard Law 3 ("This ticket does not wire
  `verifiers/verify_ggen_v26_8_3.py` into `justfile` or
  `.github/workflows/`"), and confirms its `## Standing` section's real,
  committed command output: `"findings":[],"standing":"ALIVE"`, exit `0`.
- Real command re-run this session, independent of both tickets' cited
  output: `python3 verifiers/verify_ggen_v26_8_3.py --subject-root .
  --expected-repository seanchatmangpt/ggen-legacy --expected-role
  EXECUTABLE_ARCHITECTURE_CORPUS` -- exit code `0`, real JSON output
  `"standing":"ALIVE"`, `"findings":[]`.
- `grep -rn "verify_ggen_v26_8_3\|verifiers/" .github/workflows/*.yml
  justfile tools/v26.8.1/justfile` this session: zero matches.
- `ls tickets/GL-*.md | wc -l` this session: `67`. `grep -il
  "verify_ggen_v26_8_3" tickets/GL-*.md` this session: exactly
  `tickets/GL-AUTO-001.md`, `tickets/GL-EXP-035.md`,
  `tickets/GL-EXP-040.md` -- no other ticket. Direct inspection of
  `GL-AUTO-001.md` line 110 this session confirms its hit is one bare
  filename inside a single-line, 115-path `REFUSED:FORBIDDEN_DIFF:` dump
  (`.github/workflows/ci.yml,...,verifiers/verify_ggen_v26_8_3.py`), not a
  substantive claim or a wiring proposal.
- Direct `Read` of `justfile` in full this session (51 lines): confirms
  the current 13 recipes (`fmt`, `check`, `clippy`, `test`, `ci`,
  `v26-fmt`, `v26-check`, `v26-clippy`, `v26-test`, `v26-ci`, `ci-all`,
  `planning-max`, `propose-disposition`) and confirms no existing recipe
  references `verifiers/` or `verify_ggen_v26_8_3`.
- `just --list` this session: confirms the same 13 recipes are the live,
  currently-registered set (no `docs-book` or `reference-e2e` recipe from
  `GL-EXP-036`/`GL-EXP-044` yet -- both still `NOT_STARTED`, consistent
  with those tickets' own declared status).
- `grep -n "justfile" tickets/GL-ERRC-022.md tickets/GL-EXP-004.md
  tickets/GL-EXP-008.md tickets/GL-EXP-012.md tickets/GL-EXP-036.md
  tickets/GL-EXP-044.md` this session: confirms each of the six precedent
  tickets independently states the same additive, suggestion-only,
  not-added-to-`ci`/`ci-all`/`v26-ci` pattern this ticket follows.
- Direct `Read` of `tickets/OVERLAPS.md`'s existing `## \`justfile\``
  section in full this session: confirms nine prior tickets are already
  recorded there (`GL-PLAN-002`, `GL-ERRC-022`, `GL-EXP-004`, `GL-EXP-006`,
  `GL-EXP-008`, `GL-EXP-012`, `GL-EXP-032`, `GL-EXP-036`, `GL-EXP-038`,
  `GL-EXP-044` -- ten names, `GL-EXP-006`/`GL-EXP-038` being doc-comment
  fixes rather than new recipes) and confirms none of them claims
  `verifiers/verify_ggen_v26_8_3.py` or proposes a `verify-prd-ard`-shaped
  recipe -- no existing overlap to reconcile beyond disclosing this
  ticket's own addition, which this ticket does in the same write.
- `python3 verifiers/verify_ggen_v26_8_3.py --help` this session: confirms
  the real `argparse` interface (`--subject-root`, `--expected-repository`,
  `--expected-role`, `--output`, `--self-test`), matching the three
  required flags this ticket's proposed recipe hardcodes.
- `just ci-all` run for real this session (background, waited for
  completion), full log at
  `/private/tmp/claude-501/-Users-sac-ggen-legacy/87a9b589-243d-4eb5-b50c-e957cd0f71db/scratchpad/ci-all.log`,
  exit code `0`. Root workspace (`ci`: fmt check clippy test) --
  `cargo fmt --all -- --check` PASS, `cargo check --all-targets --locked`
  PASS, `cargo clippy --all-targets --locked -- -D warnings` PASS (zero
  warnings), `cargo test --all-targets --locked -- --test-threads=1` PASS
  -- 18 tests across 7 binaries/suites, all `ok` (lib unittests 1
  `generated_contract`; main unittests 0; `tests/analysis.rs` 7;
  `tests/analysis_boundary.rs` 4; `tests/contract.rs` 3;
  `tests/exit_code.rs` 1; `tests/lsp_boundary.rs` 2). `tools/v26.8.1`
  workspace (`v26-ci`: v26-fmt v26-check v26-clippy v26-test) --
  fmt/check/clippy all PASS (zero warnings), `cargo test --manifest-path
  tools/v26.8.1/Cargo.toml --all-targets --locked -- --test-threads=1`
  PASS -- 18 tests across 5 binaries/suites, all `ok` (lib unittests 3
  `coverage_projection`; main unittests 13
  `document_evidence_sabotage_tests`; `project_coverage`/
  `subsystem_verifier` bins 0; `tests/verifier_boundary.rs` 2). **Total:
  36/36 tests passed, 0 failed, 0 ignored, across both workspaces.**
  Scope check: current branch
  (`agent/add-dsrust-groq-disposition-proposer`) diff vs `main` does not
  touch `appliance/bin/` or `tools/v26.8.1/step_two.py`, so the reference
  e2e script and `step_two.py` smoke check were correctly not run for
  this pass, per the same discipline `AGENTS.md` already documents.

## Standing

`ALIVE` -- executed this session. `git rev-parse HEAD` at execution start
matched this ticket's declared Base
(`bce7f6386c4203784beaae426e40804636c4151a`) exactly, so no re-verification
against `GL-EXP-035`/`GL-EXP-040` was triggered by Hard Law 5.

Before touching `justfile`, the exact Outcome command was re-run fresh and
confirmed still `ALIVE`/`findings: []`/exit `0`:

```console
$ python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
    --expected-repository seanchatmangpt/ggen-legacy \
    --expected-role EXECUTABLE_ARCHITECTURE_CORPUS
{"claim_ceiling":"PRD_ARD_AUTHORITY_BUNDLE_ONLY","components":17,
"direct_actuation":false,"findings":[],"interfaces":2,"requirements":24,
"schema_version":"chatman.v26.8.3.prd-ard-verifier/1","self_certification":false,
"standing":"ALIVE","subject_base_sha":"70e599a599fedb7c62c965377cc2f80df1fa01ec",
"subject_repository":"seanchatmangpt/ggen-legacy",
"subject_role":"EXECUTABLE_ARCHITECTURE_CORPUS"}
$ echo $?
0
```

The new `verify-prd-ard` recipe was then appended to `justfile` as a pure,
7-line additive block after the existing `propose-disposition` recipe --
zero existing lines altered (confirmed by diffing a pre-edit snapshot of
`justfile` against the post-edit file: the diff shows only the 7 new added
lines, no removed or changed lines). `just --list | grep -i prd-ard` lists
`verify-prd-ard`. `just verify-prd-ard` reproduces the same
`"standing":"ALIVE"` / `"findings":[]` result, exit `0`.

**`tickets/OVERLAPS.md` note**: this ticket's disclosed row in the existing
`## \`justfile\`` section was already present, byte-for-byte, before this
execution session touched anything -- both `tickets/GL-EXP-048.md` and
`tickets/OVERLAPS.md` are untracked in git (`git ls-files` returns nothing
for either path, confirmed this session) and were evidently written
together by the same drafting pass that authored this ticket. The row's
content was verified accurate (correct recipe name `verify-prd-ard`,
correct hardcoded flags) and left untouched rather than duplicated, since
the Acceptance criterion is "exactly one new disclosed row," not two.
`tickets/OVERLAPS.md` is confirmed byte-identical before and after this
execution session (`diff` against a pre-edit snapshot: no output).

**Blast radius.** The working tree had substantial pre-existing dirty state
unrelated to this ticket at execution start (`git status --porcelain`
showed ~28 modified tracked files plus dozens of untracked files/dirs,
including `justfile` itself already carrying an uncommitted `GL-ERRC-022`
`propose-disposition` recipe and an uncommitted header-comment fix). Raw
`git diff --stat` / `git status --porcelain` therefore cannot, by
themselves, isolate this ticket's edit from that pre-existing noise, and
`tickets/GL-EXP-048.md`/`tickets/OVERLAPS.md` being untracked means they
never appear in plain `git diff --stat` regardless of whether they're
touched. The precise check actually run this session: a byte-level diff of
each of the three Authored-boundary files against a snapshot taken
immediately before this execution began. Result: `justfile` gained exactly
7 additive lines (the new recipe) and nothing else; `tickets/OVERLAPS.md`
is unchanged; `tickets/GL-EXP-048.md` is this file's own Status/Standing
update. No file outside the three-file Authored boundary was written by
this execution.

**CI verification.** `just ci-all` was run for real this session (both
workspaces): exit code `0`, `36/36` tests passing, `fmt`/`check`/`clippy`
clean with zero warnings on both the root workspace and `tools/v26.8.1`.
See the "CI verification" bullet in `## Evidence` above for the full
per-workspace breakdown and the log path. This confirms the working tree
is in a real, currently-testing-clean state at the moment this ticket's
`justfile` edit landed, on top of (not a substitute for) the ticket's own
five re-run falsifiers above. `git status --porcelain` (whole repo) shows
113 entries as of this Standing section's last confirmation -- the large
majority pre-existing, unrelated dirty state already present before this
ticket's own work began (see "Blast radius" above for the precise
byte-level isolation of this ticket's own three-file edit from that
pre-existing noise); this remains an uncommitted working-tree change with
no merge authority per this ticket's own Publication boundary -- no
commit was made.
