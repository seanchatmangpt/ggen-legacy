# GL-ERRC-023 — Fix `GL-AUTO-001.md`'s fabricated CI-workflow claim and non-passing acceptance command

**Status:** `EXECUTED` — corrected `tickets/GL-AUTO-001.md` in place per Hard Laws 1-4
below; re-verified live 2026-08-21 against main checkout HEAD
`bce7f6386c4203784beaae426e40804636c4151a`. See `## Standing` and `## Acceptance` for
the real evidence.
**Base:** `seanchatmangpt/ggen-legacy@f9b283e` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

**Recovery note**: this ticket was the "eliminate" quadrant's real,
verified finding from an earlier exploration pass. Three parallel quadrant
agents raced on the filename `tickets/GL-ERRC-020.md` in that pass; this
finding's content was subsequently overwritten twice by unrelated
"reduce"-quadrant content about foundry-authority staleness (now the
canonical `tickets/GL-ERRC-020.md`). This file reconstructs the original
"eliminate" finding from the workflow's own returned evidence, given a
real unused id (`023`), so it isn't lost a third time.

## Outcome

`tickets/GL-AUTO-001.md` has two real defects, confirmed live this session:

1. **Fabricated CI-workflow claim.** The ticket's Purpose text asserts
   `.github/workflows/autonomic-crown.yml` executes its production command
   and uploads the evidence receipt. `test -f .github/workflows/autonomic-crown.yml`
   → does not exist. No workflow file by that name is present anywhere in
   `.github/workflows/`.
2. **Non-passing acceptance command.** The ticket's documented acceptance
   command, `python3 scripts/run_autonomic_crown.py`, is claimed to print
   `GL_AUTO_001_AUTONOMIC_CROWN_ALIVE`. Running it for real prints
   `REFUSED:FORBIDDEN_DIFF:...` (a long list of out-of-boundary changed
   files against the admitted base) instead — the claimed success string
   never appears.

Per `tickets/AUDIT-REPORT.md`'s audit, `GL-AUTO-001.md` also lacks nearly
every required section this corpus's other tickets use (no `Status` line,
no `Publication` line, no `Standing ceiling` heading, no `Outcome`
section, no `Hard laws` section, no `Falsifiers` section, no `Standing`
section — only `Subject`/`Purpose`/`Automated production command`/
`Authored boundary`/`Required behavior`/`Exclusions`/`Acceptance`),
ranking it the single worst ticket in the corpus. This ticket's scope is
narrower than a full rewrite: correct the two factual defects above and
add the missing `Status`/`Standing` framing so the file's claims match
this repo's own evidentiary discipline — not a redesign of what
`GL-AUTO-001` is trying to do.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
— check there before assuming sole ownership of a path below.)

```text
tickets/GL-AUTO-001.md   # correct the fabricated claim + add missing required sections
tickets/GL-ERRC-023.md
```

No change to `scripts/run_autonomic_crown.py`'s actual behavior or to
`.github/workflows/` — this ticket corrects what `GL-AUTO-001.md` *claims*
about reality, it does not change reality to match a false claim (e.g. it
must not create a fake `autonomic-crown.yml` workflow file just to make
the ticket's prose true).

**Execution confirmation:** neither `scripts/run_autonomic_crown.py` nor
any file under `.github/workflows/` was modified while executing this
ticket. Only `tickets/GL-AUTO-001.md` and `tickets/GL-ERRC-023.md` were
touched.

## Hard laws

1. The fabricated `.github/workflows/autonomic-crown.yml` claim is either
   removed or corrected to state the real current situation (no such
   workflow exists) — never left asserting something `test -f` disproves.
2. The acceptance command's documented expected output must match what
   the command *actually* prints today (`REFUSED:FORBIDDEN_DIFF:...`),
   or the ticket must explicitly mark the success-path claim as
   aspirational/`NOT_STARTED`, not asserted as current truth.
3. This ticket does not silently delete `GL-AUTO-001.md` — it corrects it
   in place, since the underlying `run_autonomic_crown.py`/`autonomic/`
   infrastructure is real (confirmed to exist) even though the ticket's
   claims about it were wrong.
4. Adding the missing `Status`/`Standing` sections must not retroactively
   claim `ALIVE`/`EXECUTED` for anything — the correct status, given the
   defects found, is `NOT_STARTED` or `BLOCKED`, decided by whichever this
   ticket's own re-verification at execution time actually supports.

**Compliance, re-verified 2026-08-21 (main checkout):**

1. Satisfied — `## Automated production command` in `GL-AUTO-001.md` now states
   plainly that `.github/workflows/autonomic-crown.yml` does not exist, with the
   `test -f` command that disproves the old claim quoted alongside it.
2. Satisfied — `GL-AUTO-001.md`'s `## Acceptance` section now quotes the real,
   freshly re-run `REFUSED:FORBIDDEN_DIFF:...` output verbatim (115 out-of-boundary
   files against main HEAD `bce7f6386c4203784beaae426e40804636c4151a`, exit code
   `1`), and labels the original `GL_AUTO_001_AUTONOMIC_CROWN_ALIVE` string as an
   explicitly unobserved "aspirational success path," not current truth.
3. Satisfied — `GL-AUTO-001.md` was corrected in place via targeted edits, not
   deleted. `scripts/run_autonomic_crown.py` and `.github/workflows/` were not
   touched.
4. Satisfied — `GL-AUTO-001.md`'s new `**Status:**` line and `## Standing` section
   both state `BLOCKED`, grounded in the real refusal observed this session; neither
   section claims `ALIVE` or `EXECUTED` for any part of `GL-AUTO-001`.

## Falsifiers

- `grep -c "autonomic-crown.yml"` on the corrected `GL-AUTO-001.md` still
  asserts the workflow file exists without qualification.
- The corrected ticket's stated acceptance-command output doesn't match a
  fresh `python3 scripts/run_autonomic_crown.py` run's real output.
- `GL-AUTO-001.md` still lacks a `Status:` line after this ticket executes.

**None of the above triggered, re-checked 2026-08-21 (main checkout):** every
`autonomic-crown.yml` mention in the corrected `GL-AUTO-001.md` is qualified as
non-existent (or is the pre-existing, unchanged `## Authored boundary` path listing,
which is an authorization-scope declaration, not an existence claim); the quoted
acceptance-command output matches a fresh run (`REFUSED:FORBIDDEN_DIFF:...`, 115
files, exit code `1`); and `grep -n "^\*\*Status:\*\*" tickets/GL-AUTO-001.md` matches
line 3.

## Acceptance (executed 2026-08-21 — real output below)

```bash
cd /Users/sac/ggen-legacy
test -f .github/workflows/autonomic-crown.yml && echo "UNEXPECTED: exists" || echo "confirmed missing"
python3 scripts/run_autonomic_crown.py   # re-run fresh, quote real output in the corrected ticket
grep -n "^\*\*Status:\*\*" tickets/GL-AUTO-001.md   # must exist after this ticket executes
```

Real output, this session, main checkout HEAD `bce7f6386c4203784beaae426e40804636c4151a`:

```text
$ test -f .github/workflows/autonomic-crown.yml && echo "UNEXPECTED: exists" || echo "confirmed missing"
confirmed missing

$ python3 scripts/run_autonomic_crown.py
REFUSED:FORBIDDEN_DIFF:.github/workflows/ci.yml,.github/workflows/planning-v26-8-7.yml,... (115 files total; full line quoted verbatim in tickets/GL-AUTO-001.md's Acceptance section)
[exit code 1]

$ grep -n "^\*\*Status:\*\*" tickets/GL-AUTO-001.md
3:**Status:** `BLOCKED` — corrected 2026-08-21 by `GL-ERRC-023`. A fresh run of the
```

All three falsifiers above were re-checked against these real outputs and none
triggered.

## Standing

`EXECUTED` — `tickets/GL-AUTO-001.md` was corrected in place this session
(2026-08-21) against main checkout HEAD `bce7f6386c4203784beaae426e40804636c4151a`:

1. The fabricated `.github/workflows/autonomic-crown.yml` claim in
   `## Automated production command` was replaced with a statement that the file
   does not exist, alongside the disproving `test -f` command — re-confirmed live
   (`confirmed missing`).
2. The `## Acceptance` section's claimed success output was relabeled as an
   explicitly unobserved "aspirational success path," and the section now also
   quotes the real, freshly re-run `REFUSED:FORBIDDEN_DIFF:...` output (115
   out-of-boundary files, exit code `1`) verbatim.
3. A `**Status:**` line (`BLOCKED`, with grounded reasoning) and a `## Standing`
   section were added to `GL-AUTO-001.md`, both re-verified live rather than
   copied from the un-executed draft; neither claims `ALIVE` or `EXECUTED` for any
   part of `GL-AUTO-001`, per Hard Law 4.

This ticket's own status is `EXECUTED`, not `ALIVE` — it corrected a documentation
defect and re-verified real command output; it did not, and does not claim to, make
`GL-AUTO-001`'s underlying automation reach `ALIVE`. `GL-AUTO-001` itself remains
`BLOCKED`, for the reasons now documented in its own `## Standing` section (its
admitted base is far behind current `HEAD`, and no CI workflow automates it).

**Note on this correction's provenance (2026-08-21):** this ticket's original draft
(and a sibling worktree's independent execution of it) cited worktree HEAD
`93d2ecd18147acaff659bf1d9cc2d4313628305b` and a 128-file `FORBIDDEN_DIFF` list. Main
checkout HEAD had since advanced to `bce7f6386c4203784beaae426e40804636c4151a`
(115 files), and `tickets/AUDIT-REPORT.md`/`tickets/OVERLAPS.md` — absent in that
worktree — are both present here. This file's evidence was independently re-run
against main's real state rather than copied from that worktree, per this ticket's
own Hard Law 2 (documented output must match what the command *actually* prints
today).
