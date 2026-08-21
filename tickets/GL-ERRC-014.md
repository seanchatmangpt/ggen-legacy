# GL-ERRC-014 — Undifferentiated BUILD_BROKEN on tools/v26.8.1/justfile's step-two recipe

**Status:** admitted, `NOT_STARTED` — drafted by ultracode ERRC pass 4
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/justfile`'s `step-two` recipe (`python3 step_two.py --root
../..`) fails today with an undifferentiated `exit 2` / `step_two_standing=
BUILD_BROKEN`. The failure traces to a git object,
`6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6`, that is unreachable in this
worktree's history but is cited as a `historical_source_commit` value inside
the v26.8.1 corpus data (`docs/v26.8.1/document-evidence-index.json` and
`ontology/v26.8.1/document-evidence.ttl`) that `step_two.py`'s evidence
pipeline consumes. This is the same failure class GL-ERRC-011 already
diagnoses and fixes for the 4 `verify_*.py` scripts' `EXPECTED_*` SHA
constants (stale cross-repo commit citations, not a real regression in this
worktree) — but `step_two.py` and `tools/v26.8.1/justfile` were out of
GL-ERRC-011's authored boundary, so this repeat of the same problem class in
a different file is still undifferentiated `BUILD_BROKEN` today. This ticket
mirrors GL-ERRC-011's established, already-precedented resolution instead of
inventing a new one: it does not silently pick a new "correct" commit to cite
(that would launder an unverified claim into a new hardcoded truth with the
same staleness failure mode) — it makes `step_two.py`'s handling of an
unreachable cited git object an explicit `STALE_REFERENCE_UNVERIFIABLE`
status, distinguishable in both the printed `step_two_standing=` line and the
written `report.json`, from a real build/verification failure. Resolving
which commit `6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6` was supposed to
reference (a real, reachable replacement, with documented provenance) is a
repo-owner decision and explicitly out of scope, per GL-ERRC-011's own Hard
Law 1 precedent.

## Authored boundary

```text
tools/v26.8.1/step_two.py   # STALE_REFERENCE_UNVERIFIABLE status on unreachable-git-object path
tickets/GL-ERRC-014.md
```

No change to `tools/v26.8.1/justfile`, `docs/v26.8.1/document-evidence-index.json`,
or `ontology/v26.8.1/document-evidence.ttl` — the cited commit hash's literal
value is not touched by this ticket. No other repo area (`.github/workflows/`,
covered separately by GL-ERRC-009; `scripts/verify_*.py`, covered by
GL-ERRC-011; `CATALOG`/`authority/`, covered by GL-ARCH-003) is touched.

## Hard laws

1. The cited commit hash `6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6` is not
   changed anywhere in this ticket's diff — this ticket makes the staleness
   visible and non-silent, it does not resolve which commit is correct.
2. Any command evidence step in `step_two.py` that currently passes (i.e.,
   does not depend on the unreachable object) must still pass identically
   after this ticket — only the specific failure path caused by dereferencing
   the unreachable object changes its status string and exit-code semantics
   from bare `BUILD_BROKEN`/exit 2 to a distinguishable
   `STALE_REFERENCE_UNVERIFIABLE`.
3. `git diff --stat` after this ticket touches only `tools/v26.8.1/step_two.py`
   and this ticket file.

## Falsifiers

- `6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6`'s literal value differs before
  vs. after this ticket anywhere in the repo.
- `git cat-file -e 6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6` newly succeeds
  (i.e., the object is in fact reachable and this ticket's staleness premise
  is false).
- After the fix, `just step-two` (or `python3 step_two.py --root ../..`
  directly) still prints an undifferentiated `BUILD_BROKEN`/exit 2 with no
  `STALE_REFERENCE_UNVERIFIABLE` marker distinguishing this cause from a real
  provenance mismatch.
- Any other command-evidence step's `passed`/`actual_exit` value in
  `.ggen/v26.8.1/step-two/report.json` changes as a side effect of this fix.

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the failure and its root cause before touching anything:
cd tools/v26.8.1 && just step-two; echo "exit=$?"
git cat-file -e 6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6 \
  && echo "REACHABLE (ticket premise falsified)" \
  || echo "unreachable (confirms staleness)"

# After the fix, confirm the new status is distinguishable:
python3 step_two.py --root ../.. 2>&1 | grep -i "stale\|BUILD_BROKEN"
cat .ggen/v26.8.1/step-two/report.json 2>/dev/null | grep -i "stale\|status"

git diff --stat   # must show only tools/v26.8.1/step_two.py + tickets/GL-ERRC-014.md
```

## Evidence this ticket is grounded in (verified this session)

- Reproduced live: `cd tools/v26.8.1 && just step-two` prints
  `step_two_standing=BUILD_BROKEN`, `step_two_admitted=false`,
  `ggen_release_admitted=false`, `report=.ggen/v26.8.1/step-two/report.json`,
  then `error: recipe step-two failed on line 12 with exit code 2` — exit
  code 2 confirmed via `echo $?`.
- `git cat-file -e 6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6` fails (nonzero
  exit) in this worktree, confirming the object is unreachable, as opposed
  to the repo's real current `HEAD`, `bce7f6386c4203784beaae426e40804636c4151a`.
- `grep -rl "6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6"` over the repo locates
  the citation in **at least three** files (**correction, per
  `tickets/AUDIT-REPORT.md`'s check-4 finding**: previously claimed "exactly
  two," a live re-run found a third): `docs/v26.8.1/document-evidence-index.json`,
  `ontology/v26.8.1/document-evidence.ttl`, and
  `docs/v26.8.1/document-evidence-index.md` — all v26.8.1 corpus-evidence
  data/doc files that `step_two.py`'s evidence pipeline reads, not a value
  hardcoded in `step_two.py` itself. Re-run the grep fresh at execution time
  rather than trusting this count, since it may drift further.
- `docs/v26.8.20/DECISIONS.md`'s "Just-recipe / CI-workflow drift (ultracode
  backlog item 23)" section documents this exact same finding: "the
  `step-two` recipe currently fails for real ... and `observe`/`crown`
  report `BUILD_BROKEN` standing due to git errors on an unreachable object
  `6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6` ... not present in this repo's
  history (consistent with this session's items 2/9 cross-repo-citation
  findings)" — and explicitly states it was "not fixed here ... outside
  GL-ARCH-003's boundary" and belongs "to no admitted ticket in this
  session." Item 23's other half (the `ci.yml` workflow-count check) is
  already covered by GL-ERRC-009; this ticket is the still-unticketed
  `step_two.py`/`justfile` half.
- `tickets/GL-ERRC-011.md` (admitted, `NOT_STARTED`) establishes the direct
  precedent this ticket mirrors: stale, unreachable cross-repo commit
  citations in this repo's verification tooling should surface as an
  explicit `STALE_REFERENCE_UNVERIFIABLE` status rather than an
  undifferentiated failure, with the correct replacement value left to the
  repo owner (Hard Law 1 there, mirrored as Hard Law 1 here).

## Standing

`UNKNOWN` — not started. This ticket only drafts the staleness-annotation
fix for the unreachable-git-object path in `step_two.py`; determining the
real, reachable commit `6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6` was meant
to cite (or whether that citation should instead be
`DISPOSITION_UNKNOWN`/removed) remains a repo-owner provenance decision
explicitly out of scope, per Hard Law 1.
