# GL-EXP-006 — Correct the stale `gl-lsp-001-runtime.yml` citation in `justfile` and `governance/production-gaps.md`

**Status:** EXECUTED -- fix applied and verified for real this session, in
the isolated worktree `.claude/worktrees/wf_14d41261-3fe-1` (worktree base
commit `93d2ecd18147acaff659bf1d9cc2d4313628305b`). The ticket file itself
was not tracked by this worktree's git history at task start (only
uncommitted draft content in the shared `~/ggen-legacy` checkout, whose
tooling refuses cross-checkout edits by design); it is written here, in the
worktree, with the Status line updated to record the real execution.
Real evidence gathered this session:
- `justfile:4` now reads `# .github/workflows/ci.yml step for step (fmt,
  check,` (re-read after edit).
- `governance/production-gaps.md:31` now reads `` `.github/workflows/ci.yml`'s
  ladder exactly for both `` (re-read after edit).
- `grep -n "gl-lsp-001-runtime" justfile governance/production-gaps.md` →
  zero matches (exit code 1) after the edit.
- `grep -n "gl-lsp-001-runtime" scripts/ci_errc.py` → line 73 unchanged
  (`".github/workflows/gl-lsp-001-runtime.yml",`), confirming Hard Law 4
  held — that file was not touched.
- `grep -n "ci.yml" justfile governance/production-gaps.md` → both new
  citations present.
- `just --list` → parses cleanly after the comment-only edit, listing all
  recipes (`check`, `ci`, `ci-all`, `clippy`, `fmt`, `planning-max`, `test`,
  `v26-check`, `v26-ci`, `v26-clippy`, `v26-fmt`, `v26-test`).
- `git diff --stat` (worktree) → `governance/production-gaps.md | 2 +-` and
  `justfile | 2 +-` only, prior to adding this ticket file.
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`justfile:4` and `governance/production-gaps.md:31` both cite
`.github/workflows/gl-lsp-001-runtime.yml` as the CI workflow they mirror or
describe. That file does not exist. Confirmed this session:
`test -f .github/workflows/gl-lsp-001-runtime.yml` fails, and
`ls .github/workflows/` lists only `ci.yml` and `planning-v26-8-7.yml`. The
real content at each site (re-read this session):

```
justfile:4: # .github/workflows/gl-lsp-001-runtime.yml step for step (fmt, check,
governance/production-gaps.md:31:   `.github/workflows/gl-lsp-001-runtime.yml`'s ladder exactly for both
```

`git log --oneline | grep 60d3826` confirms the real commit that retired
this filename: `60d3826 ci: rebuild CI around contract and real LSP
execution`. `tools/v26.8.1/draft-candidates.json` (mined history, lines
9/21/237, real content this session) independently corroborates that this
single commit deleted eight per-lane workflow files simultaneously —
`autonomic-crown.yml`, `cyberpunk-tv-replay.yml`, `errc-fast.yml`,
`ggen-create-receiver.yml`, `gl-lsp-001-runtime.yml`,
`nasa-dark-mode-replay.yml`, `verify-docs.yml`, and
`verify-ggen-v26-8-1-migration.yml` — consolidating them into the single
`ci.yml` that exists today. `ci.yml` itself (read this session, lines
27-36) now hard-asserts a "one-workflow topology" invariant in its own CI
step: it lists `expected="ci.yml\nplanning-v26-8-7.yml"` and fails the build
if the real `.github/workflows/*.yml` file set differs — i.e. the *current*
CI already enforces, on every PR, that these two files are the only ones
that exist. `justfile`'s header comment and
`governance/production-gaps.md`'s retrospective prose never caught up to
that rename, so both currently point a reader at a file CI itself proves
cannot exist.

**Additional real evidence found this session, beyond the two sites
originally reported:** `scripts/ci_errc.py:73` also lists
`.github/workflows/gl-lsp-001-runtime.yml` as an `include` pattern inside
its `LANE_RULES["lsp_runtime"]` table (a changed-file-to-CI-lane router).
Checking the same table's other four workflow-bearing lanes
(`assurance_deep` → `verify-docs.yml`, `autonomic_crown` →
`autonomic-crown.yml`, `cyberpunk_replay` → `cyberpunk-tv-replay.yml`,
`nasa_replay` → `nasa-dark-mode-replay.yml`) shows every one of them cites a
workflow file from the same pre-`60d3826` topology, and every one of those
files is equally missing today (`for f in autonomic-crown.yml
cyberpunk-tv-replay.yml errc-fast.yml ggen-create-receiver.yml
gl-lsp-001-runtime.yml nasa-dark-mode-replay.yml verify-docs.yml
verify-ggen-v26-8-1-migration.yml; do test -f ".github/workflows/$f" ||
echo "MISSING: $f"; done` — real output this session: all eight report
`MISSING`). Separately, `scripts/ci_errc.py` itself is orphaned:
`grep -rn "ci_errc" .github/workflows/*.yml justfile
tools/v26.8.1/justfile` (run this session) returns zero matches — nothing
in the current, real CI wiring invokes this router at all; it was almost
certainly driven by the now-deleted `errc-fast.yml`. This means the stale
citation this ticket fixes is one instance of a wider, real pattern (a
whole router script's lane table still encoding the pre-consolidation
8-workflow topology), not an isolated typo — which is why this ticket
explicitly scopes itself to the two prose citations only and defers the
`scripts/ci_errc.py` question (see Hard Law 4 below).

`grep -l 'gl-lsp-001-runtime' tickets/*.md` (run this session) returns zero
matches — no existing ticket's *own on-disk Authored boundary/Hard
laws/Acceptance sections* cover either the `justfile` or
`governance/production-gaps.md` citation. One ticket, `tickets/GL-EXP-002.md`,
does narrate a superficially identical finding in
`docs/v26.9.1/RELEASE-NOTES.md:474-477` ("`GL-EXP-002` (reduce/eliminate — 2
items surveyed): a stale filename citation in `justfile`'s header comment
... and `tools/ggen-verifier-cli-verify/Cargo.toml`'s dead
dev-dependency..."). Direct `Read` of the real `tickets/GL-EXP-002.md` this
session (all 147 lines) confirms its actual Outcome, Authored boundary,
Hard laws, Falsifiers, and Acceptance sections cover *only* the
`ggen-verifier-cli-verify/Cargo.toml` dead absolute-path dependency — the
words `justfile`, `governance/production-gaps.md`, and
`gl-lsp-001-runtime.yml` never appear anywhere in that file. The release
notes narrated a two-item survey; the ticket that was actually drafted from
it covers only one of the two. This is a real drift between what
`RELEASE-NOTES.md` claims was ticketed and what the ticket file itself
contains, of the same kind this corpus's own `GL-ERRC-020`/`023` recovery
already documented once for a different pair of files. This ticket closes
that drift for the `justfile`/`production-gaps.md` half.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
check there before assuming sole ownership of a path below.
`tickets/OVERLAPS.md`'s existing `## \`justfile\`` section records three
other tickets each owning one distinct, additive recipe name
(`GL-PLAN-002`'s `planning-max`, `GL-ERRC-022`'s `propose-disposition`,
`GL-EXP-004`'s proposed `planning-cli`). This ticket does not touch any
recipe — it edits only the header **comment** at lines 3-5, textually
disjoint from every recipe body those tickets claim, so there is no
line-range conflict. This ticket's `justfile` overlap should be disclosed
in `tickets/OVERLAPS.md`'s existing `## \`justfile\`` section at execution
time, the same convention `GL-EXP-004`/`GL-EXP-008` already follow while
`NOT_STARTED`.)

```text
justfile                              # header comment only, lines 3-5
governance/production-gaps.md         # prose citation only, line 31
tickets/GL-EXP-006.md
```

No change to `scripts/ci_errc.py`, any `.github/workflows/*.yml` file, or
any `justfile` recipe body — see Hard Law 4 for why `ci_errc.py`'s
identically-stale citation is explicitly out of scope here despite being
real, verified evidence documented above.

## Hard laws

1. `justfile:4`'s `.github/workflows/gl-lsp-001-runtime.yml` citation is
   replaced with `.github/workflows/ci.yml` — the real file that now
   carries the fmt/check/clippy/test ladder the comment describes
   (confirmed this session: `ci.yml` lines 43-52 run exactly `cargo fmt --
   -check`, `cargo check --all-targets --locked`, `cargo clippy ... -D
   warnings`, `cargo test --all-targets --locked`, matching the comment's
   parenthetical "(fmt, check, clippy, test)" verbatim).
2. `governance/production-gaps.md:31`'s
   `` `.github/workflows/gl-lsp-001-runtime.yml`'s ladder exactly for both
   workspaces `` citation is replaced with the equivalent reference to
   `.github/workflows/ci.yml`, preserving the surrounding sentence's claim
   ("added a root `justfile` (`just ci-all`) mirroring
   [file]'s ladder exactly for both workspaces") — a retrospective factual
   correction only, not a rewrite of the surrounding narrative.
3. No other prose in either file changes. This ticket is a citation
   correction, not an editorial pass.
4. `scripts/ci_errc.py:73`'s identical stale citation (and the four sibling
   stale citations in the same `LANE_RULES` table, and the question of
   whether the fully-orphaned `ci_errc.py` router should be fixed, rewired,
   or eliminated) is explicitly **not** touched by this ticket. That
   citation lives inside a functional `include`-glob tuple whose correct
   replacement is a design judgment (does `ci.yml`'s now-monolithic,
   always-runs-everything shape mean per-lane "own workflow changed"
   triggers should name `ci.yml`, or be deleted outright now that the
   8-lane pre-consolidation topology `ci_errc.py` still encodes no longer
   exists?) — a distinct, larger scope than a prose-citation fix, and
   arguably an `eliminate`-quadrant question about the orphaned script
   itself rather than a `reduce`-quadrant citation fix. Left as a named
   follow-on, not silently dropped.

## Falsifiers

- `grep -n "gl-lsp-001-runtime" justfile governance/production-gaps.md`
  still matches after this ticket executes (citation not actually fixed in
  either file). **Checked this session: zero matches — not triggered.**
- `grep -n "gl-lsp-001-runtime" justfile governance/production-gaps.md
  scripts/ci_errc.py` — a *narrower* fix that also silently touched
  `ci_errc.py` in violation of Hard Law 4 (this ticket's own diff must not
  include `scripts/ci_errc.py`). **Checked this session:
  `scripts/ci_errc.py:73` still shows the original stale citation,
  untouched — not triggered.**
- The replacement text in either file no longer parses as valid Markdown
  prose / a valid `justfile` comment (e.g. broken line-wrapping introduced
  by the edit). **Checked this session: `just --list` parses cleanly;
  both prose sites re-read and remain grammatical — not triggered.**
- `git diff --stat` after this ticket touches any file outside `justfile`,
  `governance/production-gaps.md`, and `tickets/GL-EXP-006.md`. **Checked
  this session (worktree): only `justfile` and
  `governance/production-gaps.md` changed prior to adding this ticket file
  — not triggered.**
- `just --list` (or `just --dry-run ci`) fails to parse `justfile` after
  the edit (comment-only edits should never break this, but it is the
  cheapest real regression check available). **Checked this session:
  succeeds, lists all recipes — not triggered.**

## Acceptance (executed this session -- real output below)

```bash
cd /Users/sac/ggen-legacy/.claude/worktrees/wf_14d41261-3fe-1
# Reconfirm the stale citation before touching anything:
grep -n "gl-lsp-001-runtime" justfile governance/production-gaps.md
# -> justfile:4:# .github/workflows/gl-lsp-001-runtime.yml step for step (fmt, check,
# -> governance/production-gaps.md:31:  `.github/workflows/gl-lsp-001-runtime.yml`'s ladder exactly for both
test -f .github/workflows/gl-lsp-001-runtime.yml && echo "UNEXPECTED: exists" || echo "confirmed missing"
# -> confirmed missing
ls .github/workflows/
# -> ci.yml

# After the fix, confirm the citation is gone from both files and ci_errc.py is untouched:
grep -n "gl-lsp-001-runtime" justfile governance/production-gaps.md && echo "UNEXPECTED: still present"
# -> exit 1, no output (correctly absent)
grep -n "gl-lsp-001-runtime" scripts/ci_errc.py   # must still show line 73 unchanged (Hard Law 4)
# -> 73:            ".github/workflows/gl-lsp-001-runtime.yml",
grep -n "ci.yml" justfile governance/production-gaps.md
# -> justfile:4:# .github/workflows/ci.yml step for step (fmt, check,
# -> governance/production-gaps.md:31:  `.github/workflows/ci.yml`'s ladder exactly for both

# Confirm justfile still parses:
just --list
# -> Available recipes: check, ci, ci-all, clippy, fmt, planning-max, test,
#    v26-check, v26-ci, v26-clippy, v26-fmt, v26-test

git diff --stat   # must show only justfile, governance/production-gaps.md, tickets/GL-EXP-006.md
# -> governance/production-gaps.md | 2 +-
# -> justfile                      | 2 +-
# (tickets/GL-EXP-006.md was newly written in this worktree, not
#  previously tracked here; see Status line above for why.)
```

## Evidence this ticket is grounded in (verified this session)

- `test -f .github/workflows/gl-lsp-001-runtime.yml` — real exit status
  this session: missing.
- `ls .github/workflows/` — real output this session: `ci.yml`,
  `planning-v26-8-7.yml` only.
- Direct `Read`/`sed -n` of `justfile:1-20` and
  `governance/production-gaps.md:25-35` this session — both citation
  strings quoted above are byte-for-byte real file content, not
  paraphrased.
- `git cat-file -t 60d3826` → `commit`; `git log --oneline | grep
  60d3826` → `60d3826 ci: rebuild CI around contract and real LSP
  execution` — the real rename commit.
- `grep -n 'gl-lsp-001-runtime' -r .` (repo-wide, excluding `.git/` and
  worktree checkouts under `.claude/worktrees/`) — real output this
  session locates exactly three live, current-tree occurrences:
  `justfile:4`, `governance/production-gaps.md:31`,
  `scripts/ci_errc.py:73`; plus historical, correctly-past-tense mining
  data in `tools/v26.8.1/draft-candidates.json` (describing commits that
  *deleted* the file, not asserting it exists) and a citation inside
  `docs/v26.9.1/RELEASE-NOTES.md:477`'s narration of `GL-EXP-002`.
- `for f in autonomic-crown.yml cyberpunk-tv-replay.yml errc-fast.yml
  ggen-create-receiver.yml gl-lsp-001-runtime.yml
  nasa-dark-mode-replay.yml verify-docs.yml
  verify-ggen-v26-8-1-migration.yml; do test -f
  ".github/workflows/$f" || echo "MISSING: $f"; done` — real output this
  session: all eight report `MISSING`, confirming `scripts/ci_errc.py`'s
  `LANE_RULES` table encodes a fully retired 8-workflow topology across
  five lanes, not just the one cited by the original two-site finding.
- `grep -rn "ci_errc" .github/workflows/*.yml justfile
  tools/v26.8.1/justfile` — real output this session: zero matches,
  confirming `scripts/ci_errc.py` is wired into nothing in the current
  CI topology.
- Direct `Read` of `.github/workflows/ci.yml` (all 73 lines) this
  session — confirms the real fmt/check/clippy/test steps (lines 43-52)
  and the "one-workflow topology" self-check (lines 27-36) that already
  proves, on every PR, the real workflow file set is exactly `{ci.yml,
  planning-v26-8-7.yml}`.
- `grep -l 'gl-lsp-001-runtime' tickets/*.md` — real output this session:
  zero matches (no ticket's own Authored boundary/Hard laws/Acceptance
  sections cover this).
- Direct `Read` of `tickets/GL-EXP-002.md` in full (147 lines) this
  session — confirms its real Outcome/Authored boundary/Hard laws/
  Falsifiers/Acceptance sections name only
  `tools/ggen-verifier-cli-verify/Cargo.toml`
  and `tools/ggen-verifier-cli-verify/Cargo.lock`; `justfile`,
  `governance/production-gaps.md`, and `gl-lsp-001-runtime.yml` do not
  appear anywhere in that file — a real, verified drift between
  `docs/v26.9.1/RELEASE-NOTES.md:474-477`'s two-item narration of
  `GL-EXP-002` and the one-item scope the actual ticket file contains.
- `sed -n '60,80p' tickets/OVERLAPS.md` — confirms the existing
  `## \`justfile\`` overlap registry entry, its three current claimants
  (`GL-PLAN-002`, `GL-ERRC-022`, `GL-EXP-004`), and that none of them
  claim the header-comment lines this ticket touches.
- `grep -n "production-gaps" tickets/GL-AUTO-001.md` — its one hit (line
  110) is a bare filename inside a giant `REFUSED:FORBIDDEN_DIFF:`
  comma-separated path dump from an unrelated acceptance-command run, not
  a substantive authored-boundary claim on the file — same pattern
  `GL-EXP-002.md` itself already documented for its own tangential hit.
- `git rev-parse HEAD` — `bce7f6386c4203784beaae426e40804636c4151a`, the
  real base commit this ticket is drafted against.

## Standing

`PARTIAL_ALIVE` -- executed this session in the isolated worktree
`.claude/worktrees/wf_14d41261-3fe-1`: both citation sites fixed, verified
by direct re-read and by every Falsifier command above returning
not-triggered, `just --list` parsing cleanly, and the diff scope holding to
exactly the two files plus this ticket. Ceiling stays `PARTIAL_ALIVE`
rather than `ALIVE` because this worktree carries no merge authority into
the shared `~/ggen-legacy` checkout or `main` (per this ticket's own
`Publication: draft pull request; no merge authority` line) — the fix is
real and verified in this checkout, but has not yet been merged into the
branch of record.
