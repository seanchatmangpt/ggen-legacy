# GL-EXP-014 — Fix self-contradicting terminal `## Standing` sections in `GL-ERRC-009.md` and `GL-ERRC-013.md`

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `UNKNOWN`
**Publication:** draft pull request; no merge authority

## Outcome

`tickets/GL-ERRC-009.md` and `tickets/GL-ERRC-013.md` each carry a
terminal `## Standing` section (the last section in the file, the
section a reader lands on for the "is this actually done" answer) that
contradicts the file's own `**Status:**` line at the top and, for
GL-ERRC-009, its own mid-file `## Post-execution update` section too:

- `GL-ERRC-013.md:3-10` states `**Status:** \`EXECUTED\` — fix applied
  and verified: AGENTS.md gained a drafted tickets (see tickets/): field
  enumerating all tickets/GL-*.md files present at execution time...`.
  Its terminal `## Standing` section (lines 148-152, the file's only
  `## Standing` heading) still reads: `` `UNKNOWN` — not started. This
  ticket only drafts the header-sync fix and its acceptance commands;
  editing AGENTS.md remains out of scope until a session/human
  explicitly starts this ticket. `` The Status line and the Standing
  section directly disagree about whether the AGENTS.md edit happened.
- `GL-ERRC-009.md:3-4` states `**Status:** \`EXECUTED\` — fix applied
  and verified this session against the real .github/workflows/
  directory contents (2026-08-20)`. Its `## Post-execution update`
  section (lines 118-129) goes further: "it has since been **applied to
  and verified against the real main checkout**
  (/Users/sac/ggen-legacy/.github/workflows/ci.yml) directly... The
  'Outstanding' limitation noted below no longer applies." Yet its
  terminal `## Standing` section (lines 180-186, the file's last
  section) still reads `` `PARTIAL_ALIVE` — fix authored and verified
  for real against the actual repository topology this session; landing
  it on the shared main checkout... was blocked by this session's
  sandbox isolation and remains outstanding ``. This is a three-way
  disagreement inside one file: Status says done, Post-execution update
  says done and says the outstanding note no longer applies, Standing
  says still outstanding.

Both underlying fixes are real and independently re-verified this pass,
not just asserted by the tickets:

- `grep -n "drafted tickets" AGENTS.md` shows the field at line 10, and
  it enumerates ticket slugs including GL-ERRC-013's own Status text
  verbatim at line 19 — the AGENTS.md edit GL-ERRC-013 claims did
  happen.
- `.github/workflows/ci.yml` (read directly this pass, lines 27-39)
  contains the allowlist-based `Admit exact head and one-workflow
  topology` step (`expected="ci.yml\nplanning-v26-8-7.yml"`,
  `test "$actual" = "$(echo "$expected" | sort)"`) — the fix GL-ERRC-009
  claims landed on the main checkout did land there.
- `git status --porcelain` in the main checkout (run this pass) shows
  both `.github/workflows/ci.yml` and `AGENTS.md` as modified,
  uncommitted files — consistent with real, in-tree, not-yet-committed
  fixes rather than fabricated claims.

So the code-level claims in both Status lines are true and verified;
the defect is narrowly that each file's own terminal `## Standing`
section — the section this repo's own convention treats as the
authoritative "current state" answer — was never edited to match, and
is the literal last thing a reader sees when reading either file start
to finish.

Correcting the evidence this ticket was drafted from: the sourcing
material for this exploration claimed GL-ERRC-009 and GL-ERRC-013 "have
never been named for this specific defect anywhere in the ticket corpus
or RELEASE-NOTES.md." That claim does not hold up under direct
re-checking and is not repeated here as fact. `docs/v26.9.1/RELEASE-NOTES.md`
discusses both tickets' Standing at length in multiple passes (e.g.
lines 49-56, 91, 101, 114, 120-135, 163-172, 204-205, 295-296, 435-436,
695-696) and its "Correction and consolidation pass" section (lines
161-172) explicitly asserts both fixes now-landed and "Verified" — but
that pass, like the ones before it, never actually edited
`GL-ERRC-009.md`'s or `GL-ERRC-013.md`'s own `## Standing` text, so its
"Verified" claim about the ticket record is itself now stale relative
to the two files' real, current, on-disk content (re-read fresh this
pass). The one place this exact defect class — a ticket's own mid-file
`## Standing` text left stale under this repo's append-don't-rewrite
discipline, never itself edited to state an explicit post-execution
value — was named in writing is `docs/v26.9.1/RELEASE-NOTES.md:229-238`,
and only for a third ticket, `GL-ERRC-016`, not for GL-ERRC-009 or
GL-ERRC-013. This repo has independent precedent for the correct fix,
though: `docs/v26.9.1/RELEASE-NOTES.md`'s final section (lines 706-712)
records that `GL-EXP-001.md`, `GL-EXP-002.md`, and `GL-EXP-006.md` had
this identical class of gap (real landed fix, stale ticket-file Status/
Standing text) and had their `Status`/`## Standing` sections "updated in
place" with fresh command output — independently confirmed this pass by
reading each file's current `**Status:**` line (all three now read
`` `EXECUTED` — real fix landed in the main checkout and re-verified
there ``, with no unresolved contradiction between Status and Standing
in any of the three). This ticket applies that same already-proven
remediation pattern to GL-ERRC-009 and GL-ERRC-013.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before assuming sole ownership of a path below.)

```text
tickets/GL-ERRC-009.md   # terminal ## Standing section only, edited in place
tickets/GL-ERRC-013.md   # terminal ## Standing section only, edited in place
tickets/GL-EXP-014.md
```

No other section of either ticket file is touched (`## Outcome`,
`## Fix applied`, `## Authored boundary`, `## Hard laws`, `## Falsifiers`,
`## Acceptance`, `## Post-execution update`, `## Execution notes`,
`## Evidence this ticket is grounded in` are all left exactly as
written). No file outside `tickets/` is touched — this ticket is a
record-keeping correction, not a re-verification or re-landing of either
underlying code fix (both were already independently re-verified real
this pass, per the Outcome section above, before this ticket was
drafted).

## Hard laws

1. The edited `## Standing` text in each file must be consistent with
   that same file's own `**Status:**` line and (for GL-ERRC-009) its own
   `## Post-execution update` section — no new contradiction introduced,
   and the old one removed.
2. The edited `## Standing` text must not claim anything beyond what is
   independently, freshly re-verifiable at execution time (re-run the
   `AGENTS.md` grep and the `.github/workflows/ci.yml` content check
   below; do not copy forward a prior pass's citation without
   re-running it).
3. No section other than `## Standing` is rewritten in either file — per
   this repo's append-don't-rewrite discipline for everything except the
   one section whose entire purpose is to state current standing, this
   ticket corrects only that section, not the historical record above
   it.
4. `git diff --stat` after execution shows only
   `tickets/GL-ERRC-009.md`, `tickets/GL-ERRC-013.md`, and
   `tickets/GL-EXP-014.md` changed.

## Falsifiers

- After the fix, `tickets/GL-ERRC-009.md`'s `## Standing` section still
  contains the word "outstanding" or otherwise states the main-checkout
  landing is not done.
- After the fix, `tickets/GL-ERRC-013.md`'s `## Standing` section still
  contains "not started" or otherwise states the `AGENTS.md` edit is not
  done.
- The corrected Standing text in either file asserts something that a
  fresh re-run of its own file's Acceptance commands, or the direct
  content checks in this ticket's own Acceptance section below, does not
  confirm.
- `git diff --stat` shows any file changed other than the three listed
  in Hard Law 4.

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Confirm the contradiction before fixing:
grep -n "^\*\*Status:\*\*" tickets/GL-ERRC-009.md tickets/GL-ERRC-013.md
sed -n '/^## Standing/,$p' tickets/GL-ERRC-009.md
sed -n '/^## Standing/,$p' tickets/GL-ERRC-013.md
# expect: both Status lines say EXECUTED; both Standing sections still
# say the underlying edit/landing has not happened.

# Independently re-confirm both underlying fixes are real before
# rewriting either Standing section (do not trust the prior claim
# without re-running this):
grep -n "drafted tickets" AGENTS.md
for f in tickets/GL-*.md; do
  slug=$(basename "$f" .md)
  grep -q "$slug" AGENTS.md || echo "MISSING FROM AGENTS.md: $slug"
done
# expect: no output from the loop

sed -n '/Admit exact head and one-workflow topology/,/workflow_count/p' .github/workflows/ci.yml
# expect: the allowlist-based check (expected="ci.yml\nplanning-v26-8-7.yml"),
# not the old `test "$count" -eq 1` form

# After editing both Standing sections in place:
grep -n "outstanding" tickets/GL-ERRC-009.md   # expect no match in the Standing section
grep -n "not started" tickets/GL-ERRC-013.md   # expect no match in the Standing section
git diff --stat
# must show only tickets/GL-ERRC-009.md, tickets/GL-ERRC-013.md,
# tickets/GL-EXP-014.md
```

## Standing

`UNKNOWN` — not started. This ticket only documents the contradiction
and drafts its correction and acceptance commands; the two ticket
files' `## Standing` sections have not themselves been edited yet. That
edit remains out of scope until a session/human explicitly starts this
ticket.
