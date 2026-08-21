# GL-EXP-046 — Reduce the stale "lsp-max PR #22 unmerged" claim in `Cargo.toml`, `governance/production-gaps.md`, and `tickets/GL-LSP-001.md` to a real re-verification decision

**Status:** `EXECUTED` -- real fix landed in the main checkout and re-verified
there 2026-08-21 (fresh `gh pr view`/`gh api tags`/`gh api releases` calls at
execution time, per Hard Law 1, reproduced the same `state: MERGED`,
`mergedAt: 2026-08-04T15:18:48Z`, empty `tags`/`releases` this ticket's
drafting-session findings reported -- no discrepancy, so Hard Law 2 applies,
not Hard Law 3).
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE` (doc/comment correction only -- no dependency-pin
change, no toolchain/build re-verification)
**Publication:** draft pull request; no merge authority

## Outcome

Three files in this repository currently assert that
`seanchatmangpt/lsp-max` PR #22 (the branch `Cargo.toml`'s `lsp-max`
dependency is pinned to) is **not yet merged**:

- `Cargo.toml:20-24` (the `# PROVISIONAL PIN:` comment directly above the
  `lsp-max = { git = ..., rev = "c1cab89..." }` line): "this rev lives on
  the unmerged branch ... unblock by merging that branch upstream (or
  pinning to a released tag once one exists)".
- `governance/production-gaps.md:58-60`: "`lsp-max` dependency is pinned to
  an unmerged branch of `seanchatmangpt/lsp-max` ... unblocked by merging
  that branch upstream or cutting a release tag".
- `tickets/GL-LSP-001.md:71`: "`lsp-max` is pinned to
  `c1cab89bf54fcc9100b3ce75580b3cc3aa8eb852` on branch
  `fix/wasm4pm-lsp-example-crates-io-dep`, **not yet merged** (draft PR
  `seanchatmangpt/lsp-max#22`) ... This pin is provisional pending PR #22
  review/merge".

I re-checked PR #22 against the real `seanchatmangpt/lsp-max` sibling repo
this session with a live GitHub API call (not memory):

```console
$ gh pr view 22 --repo seanchatmangpt/lsp-max --json state,mergedAt,headRefOid,baseRefName
{"baseRefName":"master","headRefOid":"13c118a9eb9036c35fb6d311a6033c4ba2e5b8b8","mergedAt":"2026-08-04T15:18:48Z","state":"MERGED"}
```

`state: MERGED`, `mergedAt: 2026-08-04T15:18:48Z` -- 16 days before today
(2026-08-21), directly contradicting all three files' "not yet
merged"/"unmerged branch" framing. This is a live measurement taken this
session, not a durable fact to re-quote at execution time (see Hard Law 1).

I independently confirmed the exact pinned revision itself is a real
ancestor of `lsp-max`'s current `master`, not just that *some* PR merged:

```console
$ gh api repos/seanchatmangpt/lsp-max/compare/master...c1cab89bf54fcc9100b3ce75580b3cc3aa8eb852
... "status":"behind","ahead_by":0,"behind_by":128,"total_commits":0,"files":[] ...
```

`ahead_by: 0`, `status: "behind"` means the pinned rev
`c1cab89bf54fcc9100b3ce75580b3cc3aa8eb852` (the exact SHA `Cargo.toml:25`
pins) is fully contained in `lsp-max`'s current `master` history, which is
128 commits further ahead (the `merge_base_commit` returned by this exact
compare call *is* `c1cab89...`, confirming it is a genuine ancestor, not a
coincidentally-equal SHA). `master`'s tip at compare time was itself a merge
of PR #23 ("receipt-bound 80/20 Rust LSP intelligence"), one commit further
than PR #22's merge -- consistent with PR #22 having landed first and #23
building on top of it.

I also confirmed the comment's second-named unblock path (a released tag)
is **not yet available**, so only the first-named path (merge) has actually
resolved:

```console
$ gh api repos/seanchatmangpt/lsp-max/tags
[]
$ gh api repos/seanchatmangpt/lsp-max/releases
[]
```

Both empty. This ticket's Outcome is therefore narrower than "the pin is
fully resolved" -- it is "the specific 'not yet merged'/'unmerged branch'
claim in all three files is stale and disprovable today; whether to also
move the pin itself to a tag (once one exists) or leave it pinned to a
now-merged commit rev is a separate, later decision, deliberately deferred
by this ticket (see Hard Laws)."

**Confirmed no ticket in the corpus proposes this re-verification.**
`grep -il "lsp-max" tickets/GL-*.md` this session: exactly 3 matches --
`GL-EXP-025.md` (touches root `Cargo.toml:27`'s unrelated, now-deleted
`tracing = "0.1"` line; cites `lsp-max = { git` only as unrelated
surrounding context, explicitly not its own scope), `GL-EXP-032.md` (cites
the `Cargo.toml` PROVISIONAL PIN note only as supporting evidence for an
unrelated `tracing`-dependency-graph finding, explicitly stating that
topic is "not this repo's CI topology"), and `GL-LSP-001.md` itself (the
source of the stale claim, not a correction of it). No ticket proposes
correcting the merge-status framing in any of the three files.

This mirrors the already-established `GL-ERRC-020` pattern in this same
registry: a stale "PR unmerged"/`OPEN_DRAFT` claim (there: sibling repo
`ggen`'s PR #543/#544, three weeks stale) independently disproven via a
real `gh pr view` call and turned into a dedicated re-verification ticket
rather than a fourth silent re-flag. That ticket's own Hard Law 1 --
re-verify fresh at execution time, never carry forward the drafting-time
`gh` output as sufficient -- applies identically here (Hard Law 1 below).

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
checked there and against every existing ticket's Authored boundary before
writing this section. Two new sections and one existing-file disclosure are
added to that registry by this same write: a new `Cargo.toml` (root)
section disclosing this ticket sits in a disjoint, adjacent line range from
the already-executed `GL-EXP-025`; a new `governance/production-gaps.md`
section disclosing this ticket's lines 58-60 are disjoint from
`GL-EXP-006`'s already-claimed line 31; and a new
`tickets/GL-LSP-001.md` section disclosing this is the first ticket to
claim write (not read-only-citation) access to that file, alongside the
existing `src/backend.rs`/`src/capabilities.rs`/`verify_lsp_contract.py`
section's unrelated `GL-EXP-027` claim on the same ticket file.)

```text
Cargo.toml                    # PROVISIONAL PIN comment, lines 20-24, only
governance/production-gaps.md # lsp-max bullet, lines 58-60, only
tickets/GL-LSP-001.md         # Standing section's lsp-max-pin bullet only
tickets/GL-EXP-046.md
tickets/OVERLAPS.md           # add two new sections + one disclosure row
```

No change to `Cargo.toml`'s `lsp-max = { git = ..., rev = ... }` dependency
line itself, `Cargo.lock`, `rust-toolchain.toml`, or any other dependency
declaration -- this ticket corrects the merge-status *prose* around the
pin, it does not move the pin to a different rev or tag (no tag exists to
move to, per the empty `tags`/`releases` check above). No change to
`GL-LSP-001.md`'s `## Identity`, `## Admission`, `## Observable contract`,
`## Positive witnesses`, `## Falsifiers`, or `## Acceptance` sections, or to
any other prose in its `## Standing` section besides the single
now-contradicted bullet named above. No change to `GL-EXP-025.md`,
`GL-EXP-027.md`, `GL-EXP-032.md`, or `GL-ERRC-020.md`'s own scopes,
findings, or files.

## Hard laws

1. Re-verify PR #22's state against the real `seanchatmangpt/lsp-max`
   sibling repo (`gh pr view 22 --repo seanchatmangpt/lsp-max --json
   state,mergedAt,headRefOid`, or equivalent) **at execution time**, and
   likewise re-check `gh api repos/seanchatmangpt/lsp-max/tags` /
   `.../releases` -- never carry forward this drafting session's quoted
   output as sufficient, since PR/branch/tag state can change between
   drafting and execution (mirrors `GL-ERRC-020` Hard Law 1 verbatim for a
   different sibling repo).
2. If re-verification confirms PR #22 is still `MERGED` with the same
   `headRefOid` (or a fast-forward of it) and no release tag yet exists,
   update all three files' prose to state the corrected, present-tense
   fact: the branch has been merged upstream (name the real merge date
   re-derived at execution time), but no released tag exists yet, so the
   pin itself remains a commit-rev pin, provisional in that narrower sense
   only -- not in the "review/merge pending" sense the current text
   states.
3. If re-verification instead shows a discrepancy from this ticket's
   drafting-time findings (PR reopened, force-pushed to a different head,
   or a tag now exists), this ticket must not silently proceed on stale
   drafting-time facts -- it must record the discrepancy and adjust the
   correction to match what execution-time re-verification actually shows,
   including moving the pin to a release tag if Hard Law 2's precondition
   ("no tag exists yet") no longer holds by execution time (that move
   itself, if taken, is this ticket's own decision to make once triggered
   by a real re-check, not deferred to a further ticket).
4. This ticket does not itself decide whether the `lsp-max` dependency pin
   should move off a bare commit rev (e.g. to a tag, once one exists, or
   pinned differently) -- only that the "not yet merged"/"unmerged branch"
   framing is corrected to match reality. A pin-strategy change is a
   separate, later decision.
5. `tickets/OVERLAPS.md` gains exactly two new sections (`Cargo.toml`
   (root), `governance/production-gaps.md`) and one new disclosure row
   under the existing `GL-LSP-001.md`-adjacent section, added by this same
   write -- no existing row or section in that file is altered.
6. `git diff --stat` after this ticket touches only `Cargo.toml`,
   `governance/production-gaps.md`, `tickets/GL-LSP-001.md`,
   `tickets/GL-EXP-046.md`, and `tickets/OVERLAPS.md`.

## Falsifiers

- The three files are changed without a fresh, quoted `gh pr view` (or
  equivalent) re-verification run at execution time.
- The corrected prose still says "not yet merged," "unmerged branch," or
  "draft PR" for PR #22 after execution-time re-verification confirms it
  is merged.
- `Cargo.toml`'s `lsp-max = { git = ..., rev = ... }` dependency line
  itself is changed by this ticket (in-scope is the comment above it only).
- Any file outside the authored boundary above is modified.
- `tickets/OVERLAPS.md`'s existing sections/rows (for any ticket other than
  this one) are altered rather than only appended to.
- A re-verification at execution time that actually contradicts this
  ticket's drafting-time findings is silently ignored rather than recorded
  per Hard Law 3.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the stale claim before touching anything:
sed -n '20,25p' Cargo.toml
grep -n "lsp-max" governance/production-gaps.md
grep -n "not yet merged" tickets/GL-LSP-001.md

# Re-verify sibling-repo PR/tag state at execution time (not drafting time):
gh pr view 22 --repo seanchatmangpt/lsp-max --json state,mergedAt,headRefOid,baseRefName
gh api repos/seanchatmangpt/lsp-max/tags
gh api repos/seanchatmangpt/lsp-max/releases

# If still MERGED and no tag exists, correct all three files' prose per
# Hard Law 2; otherwise record the discrepancy and adjust per Hard Law 3.

git diff --stat   # must show only Cargo.toml, governance/production-gaps.md,
                   # tickets/GL-LSP-001.md, tickets/GL-EXP-046.md,
                   # tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- `gh pr view 22 --repo seanchatmangpt/lsp-max --json
  state,mergedAt,headRefOid,baseRefName` this session (real, live GitHub
  API call): `{"baseRefName":"master","headRefOid":"13c118a9eb9036c35fb6d311a6033c4ba2e5b8b8","mergedAt":"2026-08-04T15:18:48Z","state":"MERGED"}`.
- `gh api repos/seanchatmangpt/lsp-max/compare/master...c1cab89bf54fcc9100b3ce75580b3cc3aa8eb852`
  this session: `"status":"behind","ahead_by":0,"behind_by":128`, with
  `merge_base_commit.sha == c1cab89bf54fcc9100b3ce75580b3cc3aa8eb852` --
  confirms the exact pinned rev is a real ancestor of current `master`.
- `gh api repos/seanchatmangpt/lsp-max/tags` this session: `[]` (empty).
- `gh api repos/seanchatmangpt/lsp-max/releases` this session: `[]` (empty).
- Direct `Read` of `Cargo.toml:1-35` this session: confirms the
  `# PROVISIONAL PIN:` comment (lines 20-24) and the `lsp-max = { git =
  "https://github.com/seanchatmangpt/lsp-max", rev =
  "c1cab89bf54fcc9100b3ce75580b3cc3aa8eb852" }` line (line 25) verbatim.
- `grep -n "lsp-max" governance/production-gaps.md` this session: lines
  58-59, matching the quoted bullet above.
- Direct `Read` of `tickets/GL-LSP-001.md` in full this session: line 71 is
  the literal "not yet merged (draft PR `seanchatmangpt/lsp-max#22`)"
  sentence quoted above.
- `grep -il "lsp-max" tickets/GL-*.md` this session: exactly 3 matches
  (`GL-EXP-025.md`, `GL-EXP-032.md`, `GL-LSP-001.md`); per-file context
  read for each confirms none proposes this correction (`GL-EXP-025`
  targets `Cargo.toml:27`'s unrelated, now-deleted `tracing` line;
  `GL-EXP-032` cites the PROVISIONAL PIN note only as unrelated supporting
  evidence for a `tracing`-dependency-graph finding).
- `grep -il "Cargo\.toml" tickets/GL-*.md` and manual review of each hit's
  claimed line range this session: no existing ticket claims lines 20-24
  (only `GL-EXP-025`, executed, on the disjoint, now-deleted line 27).
- `grep -il "production-gaps" tickets/GL-*.md` this session: 7 matches;
  per-file review confirms only `GL-EXP-006` (`EXECUTED`) claims write
  access, scoped explicitly to line 31 (`gl-lsp-001-runtime.yml` citation),
  disjoint from this ticket's lines 58-60.
- `grep -l "GL-LSP-001.md" tickets/GL-*.md` this session: 9 matches besides
  `GL-LSP-001.md` itself; per-file review confirms every one cites it as
  read-only evidence (`grep`/`Read` quoting its content) -- none claims an
  Authored-boundary edit right on the file itself. This ticket is the
  first to do so.
- Direct `Read` of `tickets/OVERLAPS.md` in full this session: no existing
  section for root `Cargo.toml` or `governance/production-gaps.md`; the
  one existing `GL-LSP-001.md`-adjacent section covers
  `src/backend.rs`/`src/capabilities.rs`/`verify_lsp_contract.py`
  (`GL-EXP-027`'s capability-stub finding), an unrelated concern to this
  ticket's merge-status correction.
- `date "+%Y-%m-%d"` this session: `2026-08-21` -- PR #22 merged
  `2026-08-04`, 16 days prior (matches this ticket's "for over two weeks"
  characterization loosely; stated precisely as 16 days in this ticket's
  own text above rather than re-asserting "over two weeks" as a durable
  fact that will drift further stale with time).

## Standing

`PARTIAL_ALIVE`, re-verified in the main checkout 2026-08-21:

```console
$ gh pr view 22 --repo seanchatmangpt/lsp-max --json state,mergedAt,headRefOid,baseRefName
{"baseRefName":"master","headRefOid":"13c118a9eb9036c35fb6d311a6033c4ba2e5b8b8","mergedAt":"2026-08-04T15:18:48Z","state":"MERGED"}
$ gh api repos/seanchatmangpt/lsp-max/tags
[]
$ gh api repos/seanchatmangpt/lsp-max/releases
[]
```

Execution-time re-verification (Hard Law 1) reproduced the drafting-time
findings exactly -- same `state: MERGED`, same `mergedAt`, same
`headRefOid`, empty `tags`/`releases` -- so Hard Law 2's correction path
applies (no discrepancy to record under Hard Law 3).

All three files corrected; the stale phrases are gone:

```console
$ grep -n "not yet merged\|unmerged branch\|draft PR" Cargo.toml governance/production-gaps.md tickets/GL-LSP-001.md
(no matches)
```

`Cargo.toml`'s `lsp-max = { git = ..., rev = "c1cab89..." }` dependency line
itself is byte-identical before and after (confirmed via `git diff` showing
only comment-line changes and `grep -n 'lsp-max = { git'` still resolving to
the same rev). `Cargo.toml` still parses (`python3 -c "import tomllib;
tomllib.load(open('Cargo.toml','rb'))"` and `cargo metadata --no-deps` both
succeed).

`tickets/OVERLAPS.md` already carried this ticket's two new sections
(`` ## `Cargo.toml` (root)` ``, `` ## `governance/production-gaps.md`` ``)
and its one disclosure row under the `GL-LSP-001.md`-adjacent section from
this ticket's own drafting write -- `git diff --stat -- tickets/OVERLAPS.md`
this session shows no further change was needed or made (Hard Law 5: no
existing row/section altered).

```console
$ git diff --stat -- Cargo.toml governance/production-gaps.md tickets/GL-LSP-001.md
 Cargo.toml                    | 12 ++++++------
 governance/production-gaps.md | 11 ++++++-----
 tickets/GL-LSP-001.md         |  2 +-
 3 files changed, 13 insertions(+), 12 deletions(-)
```

Plus the two untracked authored-boundary files: `tickets/GL-EXP-046.md`
(this file -- Status/`## Evidence`/`## Standing` updated to
`EXECUTED`/`PARTIAL_ALIVE` with real re-verification evidence) and
`tickets/OVERLAPS.md` (left byte-unaltered this pass -- it already
carried this ticket's two new sections plus one disclosure row from its
own drafting-time write). A repo-wide `git diff --stat` (no path filter)
additionally lists roughly 18 files with pre-existing, unrelated
uncommitted changes from other tickets already present in this working
tree before this session started (spot-checked via targeted `git diff`
on `Cargo.toml`/`governance/production-gaps.md` confirming the
already-landed `GL-EXP-025` `tracing` removal and `GL-EXP-006`
`gl-lsp-001-runtime.yml` fix were already there) -- none of those were
touched by this session's edits.

Matches Hard Law 6: only `Cargo.toml`, `governance/production-gaps.md`,
`tickets/GL-LSP-001.md`, and `tickets/GL-EXP-046.md` (this write);
`tickets/OVERLAPS.md` needed no additional change. `PARTIAL_ALIVE` ceiling
per this ticket's own header: doc/comment-level correction only, no
dependency-pin re-target (no tag exists to move to). This pass
additionally re-ran the repo-wide `just ci-all` gate as an out-of-scope
precaution against the doc-only edit having broken TOML parsing or the
build -- see "Full falsifier re-run and CI verification" below. That
extra confirmation does not raise this ticket's own standing ceiling
above `PARTIAL_ALIVE`: the fix itself remains a comment/prose correction,
matching `GL-ERRC-020`'s standing pattern for the same reason.

## Full falsifier re-run and CI verification (this pass, 2026-08-21)

All 7 of this ticket's falsifiers were re-run in full this pass and every
one resolved to its non-triggering (pass) outcome:

1. Hard Law 1 fresh re-verification at execution time --
   `gh pr view 22 --repo seanchatmangpt/lsp-max --json
   state,mergedAt,headRefOid,baseRefName` ->
   `{"baseRefName":"master","headRefOid":"13c118a9eb9036c35fb6d311a6033c4ba2e5b8b8","mergedAt":"2026-08-04T15:18:48Z","state":"MERGED"}`;
   `gh api repos/seanchatmangpt/lsp-max/tags` -> `[]`;
   `gh api repos/seanchatmangpt/lsp-max/releases` -> `[]` (all match
   drafting-session findings exactly -- no discrepancy, Hard Law 2 path
   taken, Hard Law 3 not triggered).
2. Stale phrases gone -- `grep -n "not yet merged\|unmerged
   branch\|draft PR" Cargo.toml governance/production-gaps.md
   tickets/GL-LSP-001.md` -> no matches (exit 1).
3. `Cargo.toml`'s `lsp-max = { git = ..., rev = ... }` dependency line
   itself unchanged -- `grep -n 'lsp-max = { git' Cargo.toml` -> line
   moved from 25 to 26 (comment grew by one line) but content is
   byte-identical to the original, confirmed via `git diff` showing only
   comment-line changes.
4. No file outside the authored boundary modified --
   `git status --short -- Cargo.toml governance/production-gaps.md
   tickets/GL-LSP-001.md tickets/GL-EXP-046.md tickets/OVERLAPS.md` ->
   exactly ` M Cargo.toml`, ` M governance/production-gaps.md`,
   ` M tickets/GL-LSP-001.md`, `?? tickets/GL-EXP-046.md`,
   `?? tickets/OVERLAPS.md` (`OVERLAPS.md` untracked and left
   byte-unaltered by this session -- no `Edit`/`Write` call touched it).
5. `OVERLAPS.md` existing rows/sections not altered -- confirmed by
   construction (no `Edit`/`Write` call issued against it this session);
   it already carried this ticket's two new sections plus one disclosure
   row from its own drafting-time write, satisfying Hard Law 5 without
   further change.
6. Cheap regression check -- `Cargo.toml` still parses:
   `python3 -c "import tomllib; tomllib.load(open('Cargo.toml','rb'))"`
   -> TOML syntax OK; `cargo metadata --no-deps --manifest-path
   Cargo.toml` -> succeeded.
7. The full Acceptance block (reconfirm-before, `gh` re-verify,
   reconfirm-after, `git diff --stat`) was re-run end to end, all real
   output captured in the transcript.

**Falsifiers passed:** `true` -- all 7 resolved to their non-triggering
outcome, none fired.

As an additional, out-of-scope precaution (this ticket's own Authored
boundary does not require a build/test gate for a comment-only change),
the full repo-wide `just ci-all` was also run for real this pass, in the
background with a real process-liveness wait (PID `11461`, exited
cleanly), log at
`/private/tmp/claude-501/-Users-sac-ggen-legacy/87a9b589-243d-4eb5-b50c-e957cd0f71db/scratchpad/ci-all-output.log`:

- Main workspace (`ci` recipe: fmt check clippy test):
  `cargo fmt --all -- --check` -> no diff, PASS;
  `cargo check --all-targets --locked` -> `Finished dev profile`, PASS;
  `cargo clippy --all-targets --locked -- -D warnings` -> `Finished dev
  profile`, zero warnings, PASS;
  `cargo test --all-targets --locked -- --test-threads=1` -> 6 test
  binaries, all suites `ok`, 0 failed (`generated_contract`, `lsp` bin,
  `tests/analysis.rs` 7/7, `tests/analysis_boundary.rs` 4/4,
  `tests/contract.rs` 3/3, `tests/exit_code.rs` 1/1,
  `tests/lsp_boundary.rs` 2/2), PASS.
- `tools/v26.8.1` workspace (`v26-ci` recipe: fmt check clippy test):
  `cargo fmt --manifest-path Cargo.toml -- --check` -> no diff, PASS;
  `cargo check --manifest-path Cargo.toml` -> `Finished dev profile`,
  PASS; `cargo clippy --manifest-path Cargo.toml --all-targets --
  -D warnings` -> `Finished dev profile`, zero warnings, PASS;
  `cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets
  --locked -- --test-threads=1` -> `lib` (3/3 ok), `main` bin (13/13 ok,
  includes `document_evidence_sabotage_tests`), `project_coverage` bin
  (0 tests), `subsystem_verifier` bin (0 tests),
  `tests/verifier_boundary.rs` (2/2 ok), PASS.
- `grep -E "error|FAILED|panic|warning" over the full log matched
  nothing but benign "0 failed" test-summary substrings -- no real
  errors/warnings anywhere. Since `just` aborts a recipe chain on the
  first non-zero step and the log runs cleanly through the final
  `v26-test` step, every prior step in the `ci-all` chain necessarily
  returned 0.

**CI result: all 8 steps passed (`ci_passed: true`), no build/test
failures.**

`git status --porcelain -uall | wc -l` = **102**, both immediately before
and immediately after this `ci-all` run (unchanged) -- these are
pre-existing modified/untracked files from other tickets' work already
present in this working tree before this session started (e.g.
`.github/workflows/ci.yml`, `AGENTS.md`, `Cargo.lock`/`Cargo.toml`,
several other `tickets/*.md`, `docs/v26.9.1/*`, `tools/v26.8.1/*`
changes, plus many untracked `GL-ERRC-*`/`GL-EXP-*` ticket files and
`.claude/settings.json`, `CLAUDE.md`), not artifacts produced by the
`ci-all` run itself. This count is a superset of, and consistent with,
this ticket's own scoped `git status --short` output in falsifier 4
above.

No falsifier fired, and CI confirms the doc/comment-only edit did not
regress the build in either workspace. Standing remains `PARTIAL_ALIVE`
per this ticket's own declared ceiling -- CI passing is confirmatory
evidence the fix is safe, not a claim that this ticket's scope grew to
include a dependency-pin change or toolchain work it explicitly excluded
(Hard Law 4).
