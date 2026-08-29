# GL-ERRC-020 — Reduce the thrice-flagged stale `runtime_dependency_admitted:false` / `OPEN_DRAFT` claim in the foundry authority files to a real re-verification decision

**Status:** admitted, `NOT_STARTED` — drafted by standing ultracode exploration cron
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE` (decision/doc-level only — no runtime admission)
**Publication:** draft pull request; no merge authority

**Dedup note**: a duplicate of this exact finding was independently
drafted as `tickets/GL-ERRC-021.md` by this session's manual recovery of a
lost "reduce" quadrant write from an earlier collision, then this file was
independently overwritten with the same subject by a later exploration
pass. `021` was deleted as the less-complete duplicate (80 lines vs. this
file's 138, missing this file's execution-time-re-verification Hard Law).
This file is canonical for this finding.

## Outcome

`authority/foundry-work-program.json` and `foundry/bootstrap.yaml` both
assert that the sibling-repo runtime PRs `seanchatmangpt/ggen#543` and
`#544` are unmerged and their runtime is not admitted:

- `authority/foundry-work-program.json:9` — `"status": "OPEN_DRAFT"`
  (provenance block, PR #543)
- `authority/foundry-work-program.json:19` — `"status": "OPEN_DRAFT"`
  (runtime_provenance block, PR #544)
- `authority/foundry-work-program.json:20` —
  `"runtime_dependency_admitted": false`
- `foundry/bootstrap.yaml:8` — `runtime_dependency_admitted: false`

I re-checked both PRs against the real `seanchatmangpt/ggen` sibling repo
this session with `gh pr view 543 --json state,mergedAt` and
`gh pr view 544 --json state,mergedAt`: both report
`"state":"MERGED"`, `"mergedAt":"2026-08-01T03:07:44Z"` (#543) and
`"mergedAt":"2026-08-01T03:08:14Z"` (#544) — i.e. both PRs have been merged
for three weeks as of today (2026-08-20), directly contradicting the
authority files' `OPEN_DRAFT` / not-admitted claims.

This exact contradiction has now been flagged three separate times with
zero remediation:

1. `docs/v26.8.20/DECISIONS.md:76-83`, "Stale foundry authority finding
   (ultracode backlog item 16)" — records the same PR-merged-vs-claimed-open
   contradiction and explicitly declines to act: "Not acted on here... This
   is the repo owner's decision to make, not this session's."
2. `docs/v26.8.20/ultracode-loop-progress.md` item 16 — restates the same
   finding (not re-quoted here to avoid duplicating unverified line
   numbers; confirmed present via `docs/v26.8.20/DECISIONS.md`'s own
   cross-reference to it).
3. `tickets/GL-MANUFACTURE-005.md:29-50`, "⚠ Stale premise found (ultracode
   backlog item 16 — flagged, not acted on)" — the most detailed of the
   three, stating verbatim: "flipping `runtime_dependency_admitted`... is
   exactly the kind of admission decision this repo's ticket-gating exists
   to prevent from happening incidentally inside an audit pass. It is named
   so the repo owner (or a dedicated follow-up ticket) can decide."

I ran `grep -rln "runtime_dependency_admitted\|foundry-work-program\|bootstrap.yaml" tickets/GL-*.md`
this session: only two tickets reference these files —
`tickets/GL-ERRC-011.md:123` (a single unrelated mention of
`authority/foundry-work-program.json` in a different context — that
ticket's `ggen_source_revision` discussion, not this stale-claim finding)
and `tickets/GL-MANUFACTURE-005.md` (the flag-only note quoted above, whose
own text explicitly defers the decision to "a dedicated follow-up ticket").
No ticket in the repo actually performs that follow-up. This ticket is that
follow-up: it does not flip the flag itself (that remains the repo owner's
call, per all three prior flags), but it makes the re-verification and
decision an actual trackable unit of work instead of a claim re-flagged a
fourth time with no owner and no acceptance criteria.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before assuming sole ownership of a path below.)

```text
authority/foundry-work-program.json   # provenance/runtime_provenance status fields only
foundry/bootstrap.yaml                # runtime_dependency_admitted / standing_transferred only
tickets/GL-ERRC-020.md
```

No change to `tickets/GL-MANUFACTURE-005.md`'s own exclusion boundary — that
ticket's explicit exclusion of runtime admission stands independently of
whatever this ticket decides; if this ticket does result in admission,
`GL-MANUFACTURE-005` is a separate, later decision about whether its own
exclusion should be revisited.

## Hard laws

1. This ticket may re-verify PR #543/#544 state against the real sibling
   repo (`gh pr view`, or equivalent) and update
   `authority/foundry-work-program.json`'s `status` fields and
   `foundry/bootstrap.yaml`'s `runtime_dependency_admitted` /
   `standing_transferred` fields to match **only if** that re-verification
   is re-run at execution time and its real output is quoted in this
   ticket's evidence — never carry forward this drafting session's
   `gh pr view` output as sufficient at execution time, since PR/branch
   state can change between drafting and execution.
2. If re-verification at execution time shows the sibling PRs still merged
   with no new disqualifying evidence (e.g. a revert, a force-push
   invalidating the recorded `head` SHA), the authority files' `status` /
   `runtime_dependency_admitted` fields may be updated to reflect reality —
   this is the deliberate, dedicated-ticket decision all three prior flags
   asked for, not an incidental flip inside an unrelated audit.
3. If re-verification shows any discrepancy from this ticket's drafting-time
   findings (different head SHA, PR reopened, etc.), this ticket must not
   silently proceed — it must record the discrepancy and stop short of
   flipping the authority fields until a human confirms.
4. `git diff --stat` after this ticket touches only
   `authority/foundry-work-program.json`, `foundry/bootstrap.yaml`, and
   `tickets/GL-ERRC-020.md`.

## Falsifiers

- The authority files are changed without a fresh, quoted `gh pr view`
  (or equivalent) re-verification run at execution time.
- The `head`/`base_head` SHAs recorded in `authority/foundry-work-program.json`
  are left unreconciled against the sibling repo's actual merged-commit SHAs
  after the status fields are flipped.
- Any file outside the authored boundary above is modified.
- A fourth "flagged, not acted on" note is added anywhere in the repo
  instead of this ticket being executed or explicitly rejected by the repo
  owner.

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the stale claim before touching anything:
grep -n '"status"\|runtime_dependency_admitted' authority/foundry-work-program.json
grep -n 'runtime_dependency_admitted\|standing_transferred' foundry/bootstrap.yaml

# Re-verify sibling-repo PR state at execution time (not drafting time):
cd /Users/sac/ggen && gh pr view 543 --json state,mergedAt,headRefOid
gh pr view 544 --json state,mergedAt,headRefOid

# If merged and SHAs reconcile, update the authority files' status fields
# accordingly; otherwise record the discrepancy and stop.

cd /Users/sac/ggen-legacy
git diff --stat   # must show only the two authority files and this ticket
```

## Standing

`UNKNOWN` — not started. This ticket only establishes the re-verification
and decision as a real trackable unit of work; whether the authority files
should ultimately be flipped to admitted/merged is left to execution-time
re-verification and the repo owner, not decided here.
