# Cleanup and Merge Plan: ggen-legacy

## Current State (as observed 2026-09-17)

Evidence gathered via `git`, `git worktree list`, `git log`, `git status`, `git cherry`, `du -sh` run directly against each path below. No destructive commands were run.

Canonical repo: `/Users/sac/ggen-legacy` — `origin` = `https://github.com/seanchatmangpt/ggen-legacy`, `main` @ `16a5c4f1` (2026-08-28, "integrate: origin/agent/after-code-reading-pivot-v26.8.1"), working tree clean.

`git worktree list` on the canonical repo shows 16 entries total (1 main + 15 linked worktrees):

| Path | Type | Branch | Status | Last commit (worktree HEAD) | Size |
|---|---|---|---|---|---|
| `/Users/sac/ggen-legacy` | canonical repo | `main` | clean | 16a5c4f · 2026-08-28 | 1.9G (whole tree incl. worktrees) |
| `/private/tmp/integrate6-eafexec` | worktree (registered, **directory missing from disk**) | `integrate6/eafexec` | git itself reports `prunable`; branch tip `16a5c4f` = identical to `main` (0 commits ahead/behind) | 16a5c4f · 2026-08-28 | n/a (gone) |
| `.claude/worktrees/wf_14d41261-3fe-1` | worktree | `worktree-wf_14d41261-3fe-1` | dirty (2 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_14d41261-3fe-2` | worktree | `worktree-wf_14d41261-3fe-2` | dirty (2 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_14d41261-3fe-3` | worktree | `worktree-wf_14d41261-3fe-3` | dirty (1 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_2d1bd891-8f3-1` | worktree | `worktree-wf_2d1bd891-8f3-1` | dirty (1 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_2d1bd891-8f3-2` | worktree | `worktree-wf_2d1bd891-8f3-2` | dirty (2 untracked tickets) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_c50257bb-165-1` | worktree | `worktree-wf_c50257bb-165-1` | dirty (1 modified, 16 untracked tickets) | 93d2ecd · 2026-08-17 | 3.3M |
| `.claude/worktrees/wf_c50257bb-165-2` | worktree | `worktree-wf_c50257bb-165-2` | dirty (1 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_d45a38a1-7b7-1` | worktree | `worktree-wf_d45a38a1-7b7-1` | dirty (1 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_d45a38a1-7b7-2` | worktree | `worktree-wf_d45a38a1-7b7-2` | dirty (1 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_d45a38a1-7b7-3` | worktree | `worktree-wf_d45a38a1-7b7-3` | dirty (4 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_d4a5bdab-bb5-1` | worktree | `worktree-wf_d4a5bdab-bb5-1` | dirty (1 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_d4a5bdab-bb5-2` | worktree | `worktree-wf_d4a5bdab-bb5-2` | **clean**, 2 commits ahead of `main` (1 real + 1 merge commit) | 8fc54c1 · 2026-08-20 | 3.2M |
| `.claude/worktrees/wf_dbca2a9c-5eb-1` | worktree | `worktree-wf_dbca2a9c-5eb-1` | dirty (1 staged modified, 1 staged added) | 93d2ecd · 2026-08-17 | 3.2M |
| `.claude/worktrees/wf_dbca2a9c-5eb-2` | worktree | `worktree-wf_dbca2a9c-5eb-2` | dirty (2 modified, 1 untracked ticket) | 93d2ecd · 2026-08-17 | 3.2M |

`.claude/worktrees/` subtotal: 45M across all 14 present worktrees.

All 14 present worktrees except `wf_d4a5bdab-bb5-2` are **0 commits ahead of `main`, 148 commits behind** — they were branched from an old point in history (93d2ecd, 2026-08-17) and never advanced. Their only local content is uncommitted scratch: mostly a single untracked `tickets/GL-*.md` file per worktree (workflow-run scratch output) plus, in a few, small modified files (`justfile`, `Cargo.lock/.toml`, `coverage_projection.rs`, `AGENTS.md`, CI workflow, verify scripts). None of these modifications are staged/committed anywhere.

`wf_d4a5bdab-bb5-2` is the one exception: clean working tree, branch `worktree-wf_d4a5bdab-bb5-2` @ `8fc54c1` is 2 commits ahead of `main` (a merge commit plus `feat(justfile): wire dsrust-disposition-proposer's propose-disposition CLI (GL-ERRC-022)`). `git cherry main worktree-wf_d4a5bdab-bb5-2` returned `+ 8fc54c1...` (a `+`, not `-`), confirming this commit's content is genuinely **not** already present in `main` — it is real unique work.

### Other paths checked and ruled out of this family

The computed task's related-path list was empty; the following were checked because they surfaced during the `~/`-wide worktree/temp/scratch sweep the user asked for, but git evidence shows none of them are part of the `ggen-legacy` git-worktree family (no `.git` pointer back to `ggen-legacy`, or a different `origin` remote entirely):

- `/private/tmp/B4PM-*-worktree`, `/private/tmp/GI-0*-worktree`, `/private/tmp/ggen-ci06-worktree`, `/private/tmp/ggen-gmparity-worktree`, `/private/tmp/ggen-marketplace-ci05-worktree`, `/private/tmp/ggen-self-test`, `/private/tmp/ggen-fix-autonomics`, `/private/tmp/ggen_igniter-gi08-worktree`, `/private/tmp/ggen_backup_step4`, `/private/tmp/eds-ggen-fix`, `/private/tmp/brce-full-chain-test-worktree` — checked for a `.git` file/dir; **none exist**. `du -sh` on every one of these returned `0B`. These are empty leftover directories from past workflow runs, unrelated to `ggen-legacy`'s actual git worktree mechanism. Not part of this repo's merge plan.
- `/private/tmp/ggen-ecosystem-check` — has a `.git` directory but `git -C` reports "fatal: not a git repository" against it (corrupted/incomplete `.git`), and is also `0B` by `du`. Dead artifact, not a worktree of anything.
- `/Users/sac/ggen`, `/Users/sac/ggen-marketplace`, `/Users/sac/ggen_igniter`, `/Users/sac/ggen-ecosystem`, `/Users/sac/ggen-create`, `/Users/sac/ggen-spec-kit` — each has its **own distinct `origin` remote** (`ggen.git`, `ggen-marketplace`, `ggen_igniter.git`, `ggen-ecosystem`, `ggen-create`, `ggen-spec-kit.git` respectively) and independent commit history. These are separate repositories in the same GitHub org, not duplicates or worktrees of `ggen-legacy`. Out of scope for this plan.
- `/Users/sac/scratch-ggen` (7.9G), `/Users/sac/scratch-ggen-verify2` (5.4G), `/Users/sac/ggen-marketplace-worktrees` (5.5G), `/Users/sac/ggen-marketplace-bridged-packs` (660K), `/Users/sac/ggen-marketplace-wip-staging` (60K) — no `.git` at all; plain scratch/output directories, largest disk consumers found in the sweep. Not `ggen-legacy` worktrees. See **Open Questions**.
- `/Users/sac/ggen-core-v2`, `/Users/sac/ggen-broker`, `/Users/sac/ggen-irregularity-probe`, `/Users/sac/ggen-smoke-test` — no `.git`; small (112K–468K); appear to be scratch/probe directories for those other repos, not `ggen-legacy`.

## What "merged" should look like

**Canonical path going forward: `/Users/sac/ggen-legacy` (the main working copy, not any worktree).** Evidence: it is the only path with an `origin` remote (`https://github.com/seanchatmangpt/ggen-legacy`), it is the git-worktree "main" entry (all 15 others are linked worktrees of it), its `main` branch is at the newest commit in the whole family (`16a5c4f1`, 2026-08-28 — every worktree's `93d2ecd` base is 148 commits older), and it has a fully clean working tree. No other path in this family is a competing candidate; the 15 worktrees exist solely to give past workflow runs (`.claude/worktrees/wf_*`) or an ad hoc integration branch (`/private/tmp/integrate6-eafexec`) an isolated checkout of this same repo — they were never meant to become canonical.

For every other path in the family:

1. **`/private/tmp/integrate6-eafexec`** — directory already deleted from disk (this matches the user's "deleted gemma manually" note; this entry is simply stale git metadata left behind). Its branch tip (`16a5c4f`) is byte-identical to `main`'s current tip — zero unique commits, zero content to lose. `git worktree list` already flags it `prunable`. **Safe to prune directly**, no merge needed.

2. **13 of the 14 present `.claude/worktrees/wf_*` worktrees** (all except `wf_d4a5bdab-bb5-2`) — each is 0 commits ahead of `main` (148 behind) and its only local content is uncommitted scratch: an untracked `tickets/GL-*.md` file (a workflow run's scratch ticket draft) plus, in some, a handful of modified-but-uncommitted files. None of this is committed anywhere, so there is nothing to cherry-pick or merge. **MANUAL REVIEW REQUIRED before deletion** — a human should skim each worktree's single untracked ticket file to confirm it's disposable scratch and not a ticket draft someone still wants, then `git worktree remove --force` each one (force is required only because they carry uncommitted changes, not because they carry unique commits).

3. **`wf_d4a5bdab-bb5-2`** — clean working tree, 2 commits ahead of `main`, and `git cherry` confirms the tip commit (`8fc54c1`, "feat(justfile): wire dsrust-disposition-proposer's propose-disposition CLI (GL-ERRC-022)") is genuinely unique, real work not yet in `main`. **This one commit should be merged into `main` before this worktree is removed** — either merge the `worktree-wf_d4a5bdab-bb5-2` branch or cherry-pick `8fc54c1` onto `main`, then remove the worktree (which will then be clean, no force needed).

## Commands to run (in order), once approved

```bash
cd /Users/sac/ggen-legacy

# 1. Prune the stale, already-deleted worktree entry (0 unique commits, dir already gone).
git worktree remove /private/tmp/integrate6-eafexec --force   # or: git worktree prune
git branch -d integrate6/eafexec   # safe: identical to main, 0 commits ahead

# 2. Merge the one worktree with real unique work (wf_d4a5bdab-bb5-2) BEFORE removing it.
git merge worktree-wf_d4a5bdab-bb5-2   # or: git cherry-pick 8fc54c1
git worktree remove .claude/worktrees/wf_d4a5bdab-bb5-2
git branch -d worktree-wf_d4a5bdab-bb5-2

# 3. The remaining 13 worktrees below carry ONLY uncommitted scratch (no unique commits).
#    MANUAL REVIEW REQUIRED first (open each ticket .md / diff and confirm disposable),
#    per branch, before running the corresponding lines:
# git worktree remove .claude/worktrees/wf_14d41261-3fe-1 --force
# git branch -D worktree-wf_14d41261-3fe-1
# git worktree remove .claude/worktrees/wf_14d41261-3fe-2 --force
# git branch -D worktree-wf_14d41261-3fe-2
# git worktree remove .claude/worktrees/wf_14d41261-3fe-3 --force
# git branch -D worktree-wf_14d41261-3fe-3
# git worktree remove .claude/worktrees/wf_2d1bd891-8f3-1 --force
# git branch -D worktree-wf_2d1bd891-8f3-1
# git worktree remove .claude/worktrees/wf_2d1bd891-8f3-2 --force
# git branch -D worktree-wf_2d1bd891-8f3-2
# git worktree remove .claude/worktrees/wf_c50257bb-165-1 --force
# git branch -D worktree-wf_c50257bb-165-1
# git worktree remove .claude/worktrees/wf_c50257bb-165-2 --force
# git branch -D worktree-wf_c50257bb-165-2
# git worktree remove .claude/worktrees/wf_d45a38a1-7b7-1 --force
# git branch -D worktree-wf_d45a38a1-7b7-1
# git worktree remove .claude/worktrees/wf_d45a38a1-7b7-2 --force
# git branch -D worktree-wf_d45a38a1-7b7-2
# git worktree remove .claude/worktrees/wf_d45a38a1-7b7-3 --force
# git branch -D worktree-wf_d45a38a1-7b7-3
# git worktree remove .claude/worktrees/wf_d4a5bdab-bb5-1 --force
# git branch -D worktree-wf_d4a5bdab-bb5-1
# git worktree remove .claude/worktrees/wf_dbca2a9c-5eb-1 --force
# git branch -D worktree-wf_dbca2a9c-5eb-1
# git worktree remove .claude/worktrees/wf_dbca2a9c-5eb-2 --force
# git branch -D worktree-wf_dbca2a9c-5eb-2

# 4. Empty /private/tmp scratch directories with no .git and 0B content (see table above) —
#    safe to remove directly, they hold nothing:
rmdir /private/tmp/B4PM-1702-worktree /private/tmp/B4PM-1703-worktree /private/tmp/B4PM-1704-worktree \
      /private/tmp/B4PM-1705-worktree /private/tmp/B4PM-1706-worktree /private/tmp/B4PM-1707-worktree \
      /private/tmp/B4PM-1708-worktree /private/tmp/B4PM-1709-worktree /private/tmp/brce-full-chain-test-worktree \
      /private/tmp/eds-ggen-fix /private/tmp/ggen_backup_step4 /private/tmp/ggen_igniter_test_out \
      /private/tmp/ggen_igniter_verify_scratch /private/tmp/ggen_igniter-gi08-worktree /private/tmp/ggen_verify_scratch \
      /private/tmp/ggen-ci06-worktree /private/tmp/ggen-ecosystem /private/tmp/ggen-ecosystem-check \
      /private/tmp/ggen-fix-autonomics /private/tmp/ggen-gmparity-worktree /private/tmp/ggen-marketplace-ci05-worktree \
      /private/tmp/ggen-self-test /private/tmp/ggen-v26.9.9-assets /private/tmp/GI-02-worktree \
      /private/tmp/GI-03-worktree /private/tmp/GI-04-worktree /private/tmp/GI-07-worktree 2>&1
# (rmdir is used deliberately instead of rm -rf: it only succeeds on genuinely empty dirs,
#  so it cannot silently delete anything with unexpected content that appeared since this scan.)
```

## Open Questions

- **`/private/tmp/B4PM-*-worktree` and `/private/tmp/GI-0*-worktree`, `ggen-ci06-worktree`, etc. all show `0B` and no `.git`** — `du` and a `.git` check cannot tell whether these are truly empty (safe) or whether `du` rounded a tiny non-empty dir down; recommend a plain `ls -la` on each immediately before the `rmdir` step, since `rmdir` will simply fail (harmlessly) if anything is still inside.
- **`/private/tmp/integrate6-eafexec`'s directory is already gone but its git worktree registration still exists** — git alone can't say whether the directory was removed by the "deleted gemma manually" cleanup mentioned by the user, by a workflow, or by something else; worth a quick "does this ring a bell" check with the user, though since content-wise it's byte-identical to `main` there is no data-loss risk either way.
- **The 13 stale worktrees' single untracked `tickets/GL-*.md` file each** — git can prove these are *uncommitted* and the branch has *no commits* main lacks, but git cannot tell whether a given draft ticket file is intentional WIP someone still wants to finish versus disposable scratch from an abandoned workflow run. That distinction needs a human skim of each file's content (~14 short markdown files total), not a git command.
- **Large non-`ggen-legacy` scratch directories surfaced by the broader `~/` sweep** (`/Users/sac/scratch-ggen` 7.9G, `/Users/sac/scratch-ggen-verify2` 5.4G, `/Users/sac/ggen-marketplace-worktrees` 5.5G) — these are real disk consumers but belong conceptually to other repos (`ggen`, `ggen-marketplace`) or are standalone scratch trees with no `.git` at all, so this document's git-evidence method doesn't apply to them. If the intent behind "the `~/` worktrees temps scratch etc" was to also clean these up, they need their own separate plan/doc (likely one per owning repo) rather than being folded into `ggen-legacy`'s plan — confirm with the user whether that's wanted as a follow-up.
- **`/Users/sac/ggen-core-v2`, `/Users/sac/ggen-broker`, `/Users/sac/ggen-irregularity-probe`, `/Users/sac/ggen-smoke-test`** — no `.git`, small, unclear which (if any) repo they were scratch space for; not investigated further since they carry no git history to compare against `ggen-legacy` and are out of this plan's stated scope.

## Merge Execution Log (2026-09-17)

Content-level evaluation/merge pass, no deletions performed (deletion is a separate,
later pass owned by the user). Every command below was run against the canonical repo
(`/Users/sac/ggen-legacy`) or a worktree registered to it; `git status`/`git log` was
re-checked after each mutating command. No `rm`, `rmdir`, `git worktree remove`,
`git branch -d/-D`, `git clean`, `git checkout -- <path>`, or `git reset --hard` was run.

### Re-verification of current state (before acting)

Re-ran the doc's own investigation commands. Findings matched the doc almost exactly,
with two corrections:

- `git rev-list --left-right --count main...worktree-wf_d4a5bdab-bb5-2` → main is 142
  commits ahead (not 148 as the doc estimated), branch is 2 ahead — same conclusion,
  slightly different count.
- `git cherry main worktree-wf_d4a5bdab-bb5-2` still returns `+ 8fc54c1...` (unique by
  patch-id), confirming the doc's finding — but a real merge attempt (below) surfaced
  that "unique by patch-id" is not the same as "safe to merge": main has *independently*
  evolved equivalent content since the worktree branched.

### Item 3 — `wf_d4a5bdab-bb5-2` (the one worktree with real unique commits)

Attempted the doc's own recommended action: `git merge --no-commit --no-ff
worktree-wf_d4a5bdab-bb5-2` on `main`. Result: **real conflicts**, not a clean additive
merge —

```
Auto-merging justfile
CONFLICT (content): Merge conflict in justfile
Auto-merging tickets/GL-ERRC-022.md
CONFLICT (add/add): Merge conflict in tickets/GL-ERRC-022.md
```

Root cause found by inspection: `main`'s commit `d0a4010` ("v26.9.1 release-prep
session — 26 executed tickets...") already independently added an equivalent
`propose-disposition` `justfile` recipe and an equivalent `tickets/GL-ERRC-022.md`
ticket, in a later/more-evolved form (main's ticket references a workflow-file rename
and slightly different verified command output than the worktree's version). Separately,
`git merge-base --is-ancestor` confirmed the worktree branch's *other* merged content
(the `tools/dsrust-disposition-proposer` crate + `src/analysis.rs`/tests changes, via
merge commit `0571c74` from `origin/agent/add-dsrust-groq-disposition-proposer`, tip
`26ff775`) **is already an ancestor of `main`** through a separate integration path — so
the only genuinely non-ancestor content on this branch is the top commit `8fc54c1`
itself (a `justfile` recipe + a `GL-ERRC-022.md` draft), and that content's *subject
matter* already exists in `main` in superseding form, just not that literal diff.

Per this task's hard constraint ("if you are not fully confident an action is safe and
purely additive, do NOT do it"), **the merge was not forced**. `git merge --abort` was
run immediately (aborts only the in-progress merge attempt just started in this session;
discards nothing that existed before it — verified `main` returned to clean, `HEAD`
unchanged at `16a5c4f1`).

**Preservation action taken instead:** pushed `worktree-wf_d4a5bdab-bb5-2` to `origin`
as-is (new branch, no rewrite): `git push origin worktree-wf_d4a5bdab-bb5-2` →
`* [new branch] worktree-wf_d4a5bdab-bb5-2 -> worktree-wf_d4a5bdab-bb5-2`, remote tip
confirmed via `git ls-remote origin` = `8fc54c1707d7365a6e9401670888940fb5a68a6c`. The
commit is now durably captured in the canonical repo's remote, independent of the local
worktree/branch surviving any later deletion pass.

**Still open (human judgment needed):** whether `tickets/GL-ERRC-022.md`'s two divergent
narratives (main's `d0a4010` version vs. this branch's `8fc54c1` version) should be
reconciled by hand into one ticket file, or whether main's later version is simply
accepted as the superseding one and this branch's version treated as historical-only
(now safely on `origin` either way). No code-level content appears to be at risk of loss
either way, since the `tools/dsrust-disposition-proposer` crate itself is already fully
present in `main`'s history.

### Items 2 — the 13 stale `.claude/worktrees/wf_*` worktrees (all except `wf_d4a5bdab-bb5-2`)

Re-checked each: all 13 confirmed still 0 commits ahead of `main`, still carrying only
uncommitted content (modified tracked files and/or untracked `tickets/GL-*.md` drafts) —
matches the doc.

Cross-checked every distinct ticket ID appearing across these 13 worktrees
(`GL-EXP-001/002/006`, `GL-ERRC-008/009/010/011/012/013/014/015/016/017/018/019/023`,
`GL-VERIFY-006`, `GL-ARCH-003`, `GL-CONTRACT-004`, `GL-MANUFACTURE-005`,
`GL-RECEIPT-007`, `GL-AUTO-001`, `GL-EXP-025/029`) against `main`'s `tickets/` tree:
**every single one already exists, tracked, in `main`.** Spot-diffing a sample (
`GL-EXP-006`, `GL-AUTO-001`, `GL-ERRC-012`) showed a mix — some worktree drafts are
byte-identical to `main`'s version (nothing to capture), others (`GL-EXP-006`,
`GL-AUTO-001`) are genuinely different draft narratives from `main`'s current text (a
different execution session's evidence, or an earlier pre-correction version). Given
the volume (13 worktrees, ~35 total modified/untracked paths) and that this is exactly
the "does a human still want this draft" judgment call the doc already flagged as
**MANUAL REVIEW REQUIRED**, no attempt was made to decide relevance file-by-file.

**Preservation action taken (per "commit the current state as-is" in the hard
constraints):** for each of the 13 worktrees, ran `git add -A && git commit` (message:
"chore: preserve pre-existing uncommitted worktree scratch (no discard)") directly on
that worktree's own branch — purely additive, touches only that one local branch, never
`main`. Re-verified `git status --short` empty in every worktree afterward. Commit SHAs:

| Worktree | Branch | Preservation commit |
|---|---|---|
| `wf_14d41261-3fe-1` | `worktree-wf_14d41261-3fe-1` | `ab22f1d` |
| `wf_14d41261-3fe-2` | `worktree-wf_14d41261-3fe-2` | `1af4aaf` |
| `wf_14d41261-3fe-3` | `worktree-wf_14d41261-3fe-3` | `2b95711` |
| `wf_2d1bd891-8f3-1` | `worktree-wf_2d1bd891-8f3-1` | `471b7b5` |
| `wf_2d1bd891-8f3-2` | `worktree-wf_2d1bd891-8f3-2` | `a5f1ca1` |
| `wf_c50257bb-165-1` | `worktree-wf_c50257bb-165-1` | `f7bdecb` |
| `wf_c50257bb-165-2` | `worktree-wf_c50257bb-165-2` | `359fc8d` |
| `wf_d45a38a1-7b7-1` | `worktree-wf_d45a38a1-7b7-1` | `5c63891` |
| `wf_d45a38a1-7b7-2` | `worktree-wf_d45a38a1-7b7-2` | `ff71147` |
| `wf_d45a38a1-7b7-3` | `worktree-wf_d45a38a1-7b7-3` | `2c9c056` |
| `wf_d4a5bdab-bb5-1` | `worktree-wf_d4a5bdab-bb5-1` | `8ac948a` |
| `wf_dbca2a9c-5eb-1` | `worktree-wf_dbca2a9c-5eb-1` | `ad451dc` |
| `wf_dbca2a9c-5eb-2` | `worktree-wf_dbca2a9c-5eb-2` | `7accb1a` |

Then pushed all 13 branches to `origin` in the same call as `wf_d4a5bdab-bb5-2`'s branch
(14 total `[new branch]` results, no rejections, no force). All 14 branch tips confirmed
present on `origin` via `git ls-remote`. This means every worktree's scratch content now
survives even if the worktree directory and local branch are later removed in the
separate deletion pass — nothing is only-uncommitted or only-local anymore.

**Not merged into `main`:** none of these 13 branches were merged/cherry-picked into
`main`. Every ticket ID they touch already exists in `main`; deciding whether any
individual draft supersedes or should overwrite `main`'s current ticket text is the
exact human-judgment call the doc already scoped as manual review, and none of it looked
like an unambiguous, conflict-free addition to `main` (several are same-path edits to
files `main` has since moved on from, e.g. `AGENTS.md`, `.github/workflows/ci.yml`,
`scripts/verify_*.py`, `tools/v26.8.1/src/coverage_projection.rs`).

### Item 1 — `/private/tmp/integrate6-eafexec`

Re-verified: `git rev-parse integrate6/eafexec origin/main main` all return the same
SHA (`16a5c4f1...`). Zero unique content, already fully represented on `origin`. No
action needed or taken (this item is disposal-only, i.e. next pass's job, not a merge
item).

### Item 4 — empty `/private/tmp` scratch directories

Not touched. Deletion-only item, explicitly out of scope for this pass.

### Summary of git mutations this session

- 0 commits added to `main`. `main` is unchanged at `16a5c4f1`, working tree clean
  (only the pre-existing untracked `docs/jira/` from this doc itself).
- 13 new preservation commits, one per stale worktree, each on that worktree's own
  local branch (SHAs in the table above).
- 14 branches pushed to `origin` (the 13 preservation commits' branches, plus
  `worktree-wf_d4a5bdab-bb5-2` as-is) — all new branches on the existing `origin`
  remote, no force, no rewrite of any existing ref.
- 1 merge attempted and cleanly aborted (`worktree-wf_d4a5bdab-bb5-2` → `main`), because
  it produced real conflicts rather than the doc's assumed clean fast-forward-able merge.

### Still open (for the human / for the separate deletion pass)

- Reconcile or consciously supersede `tickets/GL-ERRC-022.md`'s two narratives (`main`
  commit `d0a4010` vs. branch `worktree-wf_d4a5bdab-bb5-2` commit `8fc54c1`, now safely
  on `origin`) — no code is at risk either way.
- Human skim of the 13 preserved worktree branches' `tickets/GL-*.md` drafts (now
  permanent commits on `origin`, not uncommitted scratch) to decide, per the doc's
  original open question, whether any draft's *text* should replace `main`'s current
  version of that ticket. This is now a zero-risk, whenever-convenient review — nothing
  is only-uncommitted anymore.
- Once a human has done that review (or decided it's unnecessary), all of: the 13 stale
  worktrees + their local branches, `wf_d4a5bdab-bb5-2`'s worktree + local branch (after
  the `GL-ERRC-022.md` question above is resolved one way or the other), and
  `/private/tmp/integrate6-eafexec`'s stale git-worktree registration are safe to remove
  in the separate deletion pass — every one of them now has its content durably on
  `origin` first.
- The large non-`ggen-legacy` scratch directories and empty `/private/tmp` dirs from the
  Open Questions above remain untouched and out of this pass's scope, as previously
  documented.
