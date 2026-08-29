# GL-ARCH-003 — structured commit mining bridge for legacy archaeology (Gall checkpoint 1)

**Status:** admitted executable ticket
**Base:** `seanchatmangpt/ggen-legacy@f9b283e` (branch `agent/add-dsrust-groq-disposition-proposer`)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

Add a structured, library-backed alternative to `mine()`'s raw `git log`/`git
tag` shell-out, and a `draft-candidates` mode that surfaces commits not yet
represented in the hand-curated `CATALOG` — without automating away the
human evidence-verification step `CATALOG`'s own docstring requires
(`tools/v26.8.1/legacy_archaeology.py:27-37`). This is Gall's Law checkpoint
1 from `CLAUDE.md`'s "evolve from prior art" table: borrow a real
commit-object-model library (`pygit2`) instead of hand-parsing `git log`
stdout, per the deep-research finding that MSR tooling (GraphRepo, PyDriller,
RepoDriller) already solves this.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before assuming sole ownership of a path below.)

```text
tools/v26.8.1/legacy_archaeology.py   # additive: mine_structured(), draft_candidates(), main() dispatch only
tools/v26.8.1/requirements.txt        # new
tickets/GL-ARCH-003.md
```

`CATALOG`, `EXT_CATALOG`, `EXT_CATALOG2`, `to_turtle()`, `emit()`, and
`ontology/v26.8.1/legacy-capabilities.ttl` remain outside this ticket —
unmodified.

## Required transitions

```text
walk full --all git history via pygit2 (structured Commit objects)
→ diff each commit against its first parent, classify deleted paths
→ cross-reference deleted-path commits against CATALOG's already-published
  historical_source_commit hashes (short-hash match)
→ emit UNKNOWN-disposition drafts for uncovered commits to a side file
→ (out of scope) human/session reviews drafts, re-verifies each commit
  independently, promotes verified ones into CATALOG by hand
```

## Hard laws

1. `mine_structured()`/`draft_candidates()` are additive; they do not replace
   or remove `mine()`, `CATALOG`, or `emit()`'s existing behavior.
2. `draft-candidates.json` is never auto-merged into `CATALOG` — every draft
   carries `disposition: UNKNOWN` and an explicit "not yet human-verified" note.
3. `ontology/v26.8.1/legacy-capabilities.ttl` must be byte-identical before
   and after running `draft-candidates` (verified this session via checksum).
4. A missing `pygit2` install fails closed with operator install instructions
   (`SystemExit`), never a bare traceback or a silent fallback to guessing.
5. `mine_structured()`'s commit count for full `--all` history must match
   `mine()`'s raw `git log --all --decorate --oneline` line count exactly —
   any divergence is a bug in the structured walker, not evidence to paper over.

## Falsifiers

- `mine_structured()`'s commit count diverges from raw
  `git log --all --decorate --oneline`'s line count (Hard Law 5).
- `draft-candidates` mode writes to `ontology/v26.8.1/legacy-capabilities.ttl`
  or otherwise mutates `CATALOG`/`EXT_CATALOG`/`EXT_CATALOG2` (Hard Law 2).
- A missing `pygit2` install produces a bare traceback instead of the
  documented install instructions (Hard Law 4).
- Any draft candidate omits the `disposition: UNKNOWN` /
  not-yet-human-verified marker (Hard Law 2).

(This ticket's ultracode-audit ticket sweep — see `tickets/AUDIT-REPORT.md`
— flagged that this section was previously missing/folded into the
"Real finding" section below; restored as its own heading per the corpus
convention 17 of 19 sibling tickets already use.)

## Real finding this session: CATALOG's cited commits predate this worktree's history

Falsifying against the two commits `CLAUDE.md`'s Gall checkpoint 1 description
named as a cross-check (`9cef6e40f`, `bde78f7d5`) found neither is a valid
git object in this worktree (`git cat-file -t` fails closed on both — not a
tool bug). This worktree's full `--all` history is exactly 420 commits, and
`CATALOG`'s own prose (`tools/v26.8.1/legacy_archaeology.py:122`, `:143`) cites
these hashes as belonging to a different producing repository's history
(`seanchatmangpt/ggen`, referenced via `docs/jira/v26.7.16/...`), not this
repo's own commits — a pre-existing condition, not something introduced or
fixable by this ticket. Recorded as `standing: UNKNOWN` for that specific
cross-repo linkage, not silently assumed resolved.

## Acceptance

```bash
python3 -m venv tools/v26.8.1/.venv-archaeology
tools/v26.8.1/.venv-archaeology/bin/pip install -r tools/v26.8.1/requirements.txt
tools/v26.8.1/.venv-archaeology/bin/python3 tools/v26.8.1/legacy_archaeology.py mine-structured | wc -l   # must equal: git log --all --decorate --oneline | wc -l (a live count, not a fixed number -- see Hard Law 5)
tools/v26.8.1/.venv-archaeology/bin/python3 tools/v26.8.1/legacy_archaeology.py draft-candidates
git diff --stat ontology/v26.8.1/legacy-capabilities.ttl   # must be empty
```

## Amendment: ultracode audit (25-prompt backlog item 1) found and fixed 3 real bugs

An adversarial audit-then-verify workflow (2026-08-20/21) found 5 candidate
issues in `mine_structured()`/`draft_candidates()`, adversarially re-verified
each against real command output (not just re-reading the diff), and
confirmed 4 as real, refuting 1 as a false positive. Fixed the 3 with actual
observable-consequence impact (all within this ticket's already-admitted
authored boundary — bugfixes to code this ticket owns, not new admission):

1. **Merge commits only diffed against `parents[0]`** — silently hid
   deletions visible only relative to a merge's other parent(s). Confirmed
   against a real merge commit in this repo
   (`ef2502522a01ef413c588f9ee135139b097efb7b`): 8 workflow-file deletions
   only visible relative to `parents[1]` were invisible before the fix.
   Fixed: diff against every parent, union deletions, deletion wins over
   modification for a path touched both ways across parents.
2. **Rename detection never enabled** (`diff.find_similar()` never called) —
   every plain rename surfaced as a false-positive DELETE+ADD pair. Fixed:
   call `find_similar()` per parent-diff and skip `GIT_DELTA_RENAMED`/
   `GIT_DELTA_COPIED` deltas.
3. **`_catalog_covered_hashes()` only captured the first hash in compound
   `historical_source_commit` fields** (e.g. `"9cef6e40f (delete) /
   cbf173f82 (...) / d0b9ff1c6.. (...)"` only registered `9cef6e40f`) —
   silently under-counted already-curated commits, re-surfacing them as
   fresh `UNKNOWN` drafts. Fixed: extract every hex-hash-shaped token from
   the field via regex, not just a fixed-offset prefix of the whole string.
   Re-verified: `draft-candidates` now recognizes 33 covered hashes (was 22
   before the fix) and emits 22 drafts (was 20).

A 5th finding (low severity, re-walking already-seen commits through
multiple refs before the seen-set dedup) was confirmed real but is a
performance characteristic, not a correctness bug — no diff work is wasted
on already-seen commits (the `seen` check precedes the diff loop), so left
unfixed as out of proportion to this ticket's scope.

Re-verified post-fix: `mine-structured`'s commit count still exactly matches
raw `git log --all --decorate --oneline`'s count (both drift upward together
as the repo gains commits — 420 at initial verification, 422 at the
ultracode backlog item 25 adversarial re-check; the invariant Hard Law 5
requires is equality between the two live counts, never a fixed number),
`draft-candidates` still leaves `legacy-capabilities.ttl` byte-identical,
`just ci-all` still passes clean.

## Adversarial self-review (ultracode backlog item 25)

Independently re-run from scratch, not trusting this ticket's own prose:
all 4 claims (commit-count invariant, TTL byte-identity via sha256sum,
`just ci-all` exit 0, all 3 amendment fixes present at their cited line
ranges) verified PASS. One flag: this ticket's acceptance-block comment
originally hardcoded `# == 420` instead of stating the live invariant —
fixed above.

## Standing

`PARTIAL_ALIVE`, verified this session:

- `mine_structured()` walks all 420 reachable commits in this worktree via
  `pygit2`, matching `mine()`'s raw `git log --all --decorate --oneline`
  line count exactly (420 == 420).
- `draft_candidates()` ran clean: 20 draft candidates emitted (of 420 commits
  walked, 22 already short-hash-matched against `CATALOG`'s 65 published
  individuals) to `tools/v26.8.1/draft-candidates.json`.
  `ontology/v26.8.1/legacy-capabilities.ttl` confirmed byte-identical
  before/after (checksum diff empty).
- Not `ALIVE`: the 20 drafts are unreviewed by design (Hard Law 2) — this
  ticket's standing ceiling is `PARTIAL_ALIVE` until a human/session promotes
  a first verified draft into `CATALOG`, which is explicitly out of this
  ticket's authored boundary.
- The cross-repo commit-hash finding above is `UNKNOWN`, named rather than
  silently resolved — a future ticket (or a note to the repo owner) is
  needed to decide whether `CATALOG`'s historical commits should be
  re-anchored to a different producing repository's history, or left as
  cross-repo citations by design.
