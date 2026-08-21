# GL-EXP-016 — Create a real git commit checkpoint for the entire uncommitted ticket corpus and every EXECUTED/ALIVE code change

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

Verified live this session via `git status --porcelain -uall`: the working tree on branch
`agent/add-dsrust-groq-disposition-proposer` has **14 tracked files modified** (`M`) and
**48 files untracked** (`??`) — 62 paths total (`git status --porcelain -uall | wc -l` → `62`).
`git log -1` shows the branch's real, current `HEAD` is `bce7f6386c4203784beaae426e40804636c4151a`,
dated `2026-08-20 20:44:18`, an unrelated planning-tooling commit
("`planning: extend real prototype with construct_replacement/retire_predecessor`") — not a
checkpoint of any of this session's ticket-admission work.

`ls tickets/GL-*.md | wc -l` → `35`; `git status --porcelain -uall -- tickets/ | wc -l` → `35`
— every single ticket file in the corpus, with no exception, is untracked. This includes
`tickets/AUDIT-REPORT.md` and `tickets/OVERLAPS.md`, the corpus's own audit and cross-ticket
overlap ledger. Every file any ticket in this corpus claims to have fixed under `EXECUTED`
standing is either modified-but-uncommitted or entirely new-and-untracked:
`.github/workflows/ci.yml` (`GL-ERRC-009`), `AGENTS.md` (`GL-ERRC-013`),
`justfile`/`governance/production-gaps.md` (`GL-EXP-006`, `EXECUTED` per its own later
correction section in `docs/v26.9.1/RELEASE-NOTES.md`),
`scripts/verify_foundry_bootstrap.py`/`verify_foundry_provenance.py`/`verify_docs.py`/
`verify_offline_transport.py` (`GL-ERRC-011`),
`tools/v26.8.1/src/coverage_projection.rs` (`GL-ERRC-015`/`016`/`019`),
`tools/v26.8.1/src/bin/subsystem_verifier.rs` (`GL-EXP-001`, `EXECUTED` per the same
correction), `tools/ggen-verifier-cli-verify/Cargo.toml`/`Cargo.lock` (`GL-EXP-002`,
`EXECUTED` per the same correction), `tickets/GL-AUTO-001.md` (`GL-ERRC-023`), and new
untracked content backing `GL-ARCH-003`/`GL-RECEIPT-007`
(`tools/v26.8.1/draft-candidates.json`, `dsse_wrap.py`, `requirements.txt`).

`grep -n "^[a-z-]*:" justfile` (run live this session) lists only `fmt`, `check`, `clippy`,
`test`, `ci`, `ci-all`, `planning-max` — no commit-related recipe. `grep -n "git commit\|git add"
justfile tools/v26.8.1/justfile .github/workflows/*.yml` (run live this session) returns zero
matches anywhere in the repo's own tooling — nothing in CI or `just` ever runs `git commit`.

`grep -n -i "uncommitted" docs/v26.9.1/RELEASE-NOTES.md` (run live this session) matches only
two lines (631, 700), both inside one narrow correction section about three specific `GL-EXP-*`
tickets' ticket-record-vs-code gap (`GL-EXP-001`, `GL-EXP-002`, `GL-EXP-006`) — that section's
own "honest conclusion" documents the code/ticket-status mismatch and resolves it by editing
those three tickets' `Status` text, but it never runs `git commit`, and it never names the
repo-wide risk that **the entire admitted ticket corpus and every claimed `EXECUTED`/`ALIVE`
fix across this whole session's work has zero git history**. `grep -l "git commit\|commit
checkpoint\|entire ticket corpus" tickets/*.md AGENTS.md docs/v26.9.1/*.md` (run live this
session) returns nothing — no ticket in the corpus has this repo-wide checkpoint as its
Authored boundary. Any `git clean -fdx`, hard reset, or lost/corrupted working directory on
this branch right now would silently destroy all 62 paths — including every ticket file this
corpus's own admission discipline depends on as its system of record.

## Authored boundary

This ticket's own drafting changes no source file — it is a pure finding. Its **execution**
(not performed by this ticket) would be a `git add` + `git commit` checkpoint of the exact
working-tree state enumerated above, plus (only if Hard Law 2 below identifies a genuine
exclusion) a `.gitignore` addition — no content of any existing file would be altered by
executing this ticket; `git add`/`git commit` stage and record bytes already on disk verbatim.

```text
tickets/GL-EXP-016.md                # this ticket only, at drafting time
.gitignore                           # only if execution identifies a genuine exclusion (Hard Law 2)
(execution stages/commits, but does not edit the content of, the 62 paths listed above)
```

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before
assuming sole ownership of a path below; this ticket's execution would touch the same paths
every `EXECUTED` ticket above already claims to have fixed, but only at the git-plumbing layer
— staging and committing bytes those tickets already put on disk, never re-editing them.)

## Hard laws

1. Pure additive git operations only — `git add` and `git commit`. No `git reset --hard`, no
   `git clean -fdx`, no history rewrite, no `git commit --amend`, no rebase — per this
   session's own global git-workflow instruction ("fix forward only... commits are immutable").
2. Before committing, each of the 62 currently-modified/untracked paths must be reviewed
   against `.gitignore` for a genuine exclusion — build caches, machine-local settings
   (`.claude/settings.json`), or clearly-ephemeral regenerated artifacts (e.g.
   `tools/v26.8.20/observed/*.json`, a fresh contract JSON regenerated on every
   `observe_contract.py` invocation — already characterized as "not a stable gate" by
   `GL-EXP-012`'s own Hard Law 3). Any exclusion must be justified per-path in the commit
   message or a `.gitignore` comment, never a blanket `git add -A` performed without review.
3. The commit message must not claim any ticket as `EXECUTED`/`ALIVE` beyond what that
   ticket's own `Status`/`Standing` text already states — this ticket only creates a git
   history boundary for existing claims; it does not upgrade any ticket's standing.
4. The new commit's parent must be the real current `HEAD`
   (`bce7f6386c4203784beaae426e40804636c4151a`) — appended on top, never replacing it.
5. Must not alter the byte content of any file being committed — `git add`/`git commit` of
   exactly what is already on disk, verified by an empty `git diff` between the pre-commit
   working tree and the post-commit `HEAD` for every path committed.

## Falsifiers

- `git status --porcelain -uall` still shows any of the 62 paths present at drafting time
  (minus a Hard-Law-2-justified exclusion) after execution.
- `git log -1 --format=%H` does not return a new commit hash distinct from
  `bce7f6386c4203784beaae426e40804636c4151a`.
- `git log -1 --format=%P` does not return `bce7f6386c4203784beaae426e40804636c4151a` as the
  new commit's sole parent.
- Any of `git reflog | grep -i "reset --hard\|clean -fdx"` shows a destructive operation
  attributed to this ticket's execution.
- The commit message asserts any ticket is `EXECUTED`/`ALIVE` beyond what that ticket's own
  file states as of the commit.
- `git diff bce7f6386c4203784beaae426e40804636c4151a..HEAD -- <any committed path>` differs
  from that path's pre-commit working-tree bytes (would mean content was altered while
  checkpointing, not preserved as-is).

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Confirm the gap before fixing:
git status --porcelain -uall | wc -l        # expect 62 at drafting time
git log -1 --format=%H                       # expect bce7f6386c4203784beaae426e40804636c4151a
ls tickets/GL-*.md | wc -l                   # expect 35
git status --porcelain -uall -- tickets/ | wc -l  # expect 35 (all untracked)
grep -n "git commit\|git add" justfile tools/v26.8.1/justfile .github/workflows/*.yml
  # expect: no output (zero matches)

# After committing (execution, not performed by this ticket):
git status --porcelain -uall                 # expect empty (or only Hard-Law-2-justified exclusions)
git log -1 --format=%H                       # expect a new commit hash
git log -1 --format=%P                       # expect bce7f6386c4203784beaae426e40804636c4151a
git status --porcelain -uall -- tickets/ | wc -l  # expect 0 (all 35 ticket files now tracked)
```

## Evidence this ticket is grounded in (verified this session)

- `git status --porcelain -uall` (run directly this session): 14 `M` + 48 `??` = 62 paths,
  reproduced exactly (`git status --porcelain -uall | wc -l` → `62`).
- `git log -1` (run directly this session): `bce7f6386c4203784beaae426e40804636c4151a`,
  `2026-08-20 20:44:18`, an unrelated planning-tooling commit — not a checkpoint of this
  session's ticket-admission work. `git branch --show-current` →
  `agent/add-dsrust-groq-disposition-proposer`.
- `ls tickets/GL-*.md | wc -l` → `35`; `git status --porcelain -uall -- tickets/ | wc -l` → `35`
  (run directly this session) — every ticket file in the corpus is untracked, no exception.
- `grep -n "^[a-z-]*:" justfile` (run directly this session): only `fmt`, `check`, `clippy`,
  `test`, `ci`, `ci-all`, `planning-max` — no commit recipe exists.
- `grep -n "git commit\|git add" justfile tools/v26.8.1/justfile .github/workflows/*.yml` (run
  directly this session): zero matches — no CI or `just` step ever commits.
- `grep -n -i "uncommitted" docs/v26.9.1/RELEASE-NOTES.md` (run directly this session): two
  matches, both inside one narrow correction section scoped to three `GL-EXP-*` tickets'
  record-vs-code gap — read in full this session (lines 610-710); it never states or addresses
  the repo-wide risk this ticket documents, and it never runs `git commit`.
- `grep -l "git commit\|commit checkpoint\|entire ticket corpus" tickets/*.md AGENTS.md
  docs/v26.9.1/*.md` (run directly this session): no matches — no existing ticket claims this
  finding or this file boundary.
- `cat .gitignore` (read directly this session, 24 lines): confirms build caches and generated
  evidence directories are already excluded (`target/`, `evidence/appliance/`, `.venv*/`, etc.)
  but the 62 live paths above are not among them — they are genuinely untracked/modified
  working content, not gitignore oversights.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the finding that the entire
working tree — including all 35 ticket files, the corpus's own `AUDIT-REPORT.md` and
`OVERLAPS.md`, and every file any `EXECUTED`/`ALIVE` ticket in this corpus claims to have
fixed — sits uncommitted with no commit boundary and no tooling that ever runs `git commit`.
The actual `git add`/`git commit` checkpoint has not been performed; no higher standing can be
claimed until it is, and its real post-commit `git log -1`/`git status --porcelain -uall`
output is recorded here.
