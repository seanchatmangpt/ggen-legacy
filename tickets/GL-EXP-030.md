# GL-EXP-030 — Reduce README.md's and claims-register.md's duplicate unbacked `foundry_runtime_candidate` ALIVE claim

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`README.md:16` (read directly this session, the project's top-of-file
"Project 001 standing" table) reads:

```text
| Foundry runtime candidate | `ALIVE` | Exact candidate `458f0f88…` passed
formatting, all targets including real-Git tests, and program validation.
It is not the stable dependency. |
```

`governance/claims-register.md:15` (read directly this session, row
`CLM-011`) reads:

```text
| CLM-011 | The exact foundry runtime candidate executes its declared
bounded contract. | `TESTED` | `ALIVE` | `458f0f88…`, all-target tests,
real-Git suite, program validation, clean source receipt | Candidate is
not admitted as the stable manufacturing dependency. |
```

Both rows assert the identical `ALIVE` standing for the identical
candidate revision `458f0f88aee0060cddce3ffdaa7e2172a4f40a25` that
`tickets/GL-ERRC-017.md` (read in full this session) and
`tickets/GL-EXP-026.md` (read in full this session) already target for
correction. `GL-ERRC-017`'s Outcome section establishes the underlying
fact this ticket relies on: `authority/project-001-promotion.json`'s
`bounded_rails.foundry_runtime_candidate.evidence` array names exactly one
file, `evidence/foundry-runtime-candidate.json`, and that file does not
exist -- "meaning that rail's `\"standing\": \"ALIVE\"` claim has, by this
file's own citation mechanism, no locatable backing whatsoever, not
partial backing." This session independently reconfirmed the file is
still missing: `test -e evidence/foundry-runtime-candidate.json` exits
non-zero. `GL-EXP-026` found the identical unbacked claim duplicated a
second time in `authority/verifier-appliance-profile.json` and drafted a
ticket to reduce that copy too, for the same reason.

Neither `GL-ERRC-017` nor `GL-EXP-026` touches `README.md` or
`governance/claims-register.md`. `GL-ERRC-017`'s Authored boundary (read
directly this session) names exactly `authority/project-001-promotion.json`
and `tickets/GL-ERRC-017.md`. `GL-EXP-026`'s Authored boundary (read
directly this session) names exactly
`authority/verifier-appliance-profile.json` and `tickets/GL-EXP-026.md`.
`grep -n "README.md" tickets/GL-ERRC-017.md tickets/GL-EXP-026.md` (run
this session): zero matches, exit 1. `grep -il "claims-register"
tickets/GL-*.md` (run this session, across the entire ticket corpus):
zero matches, exit 1 -- no ticket in the corpus, including these two,
names `governance/claims-register.md` at all.

If both currently-drafted tickets execute exactly as scoped, the result is
a corrected `authority/project-001-promotion.json` and a corrected
`authority/verifier-appliance-profile.json` (both `foundry_runtime_
candidate`/`verified_foundry_runtime_candidate` standing dropped to
`UNVERIFIED`) sitting next to an uncorrected `README.md` and an
uncorrected `governance/claims-register.md` -- specifically the repo's own
most-visible file (the top-of-README project-status table, the first
thing a reader sees) and its formal claims register -- both still
asserting the identical unbacked `ALIVE` claim for the identical
revision, undoing the two authority-file fixes' own purpose by leaving two
more uncorrected copies standing in the two places most likely to be read
by a human rather than parsed by tooling. This ticket closes that gap:
reduce both rows' standing from `ALIVE` to `UNVERIFIED`, mirroring
`GL-ERRC-017`'s Hard Law 1 disposition for the same underlying claim, so
all four copies of the claim (the two authority JSON files once their own
tickets execute, plus these two human-facing documents once this ticket
executes) read the same honest standing instead of two corrected and two
stale.

## Authored boundary

(No overlap with any existing ticket's Authored boundary was found:
`grep -iln "README.md" tickets/GL-*.md` (run this session) matches
`tickets/GL-AUTO-001.md`, `tickets/GL-EXP-013.md`, `tickets/GL-EXP-012.md`,
and `tickets/GL-EXP-023.md`, but none of the four claims the root
`README.md` as an Authored-boundary target: `GL-AUTO-001`'s own
`REFUSED:FORBIDDEN_DIFF:` list and Authored boundary name only nested
`README.md` files (`packs/cyberpunk-tv-platform-replay/README.md`,
`packs/nasa-dark-mode-replay/README.md`, `planning/v26.8.20/README.md`,
`planning/v26.8.7/README.md`) -- never the root file; `GL-EXP-013` and
`GL-EXP-023` each cite `README.md:14` (the *Verifier Appliance reference*
row, a different rail on a different line) purely as motivating evidence,
not as a file either claims to edit -- their own Authored boundary
sections are scoped to `appliance/bin/*.py`; `GL-EXP-012` cites
`planning/v26.8.20/README.md` and `planning/v26.8.7/README.md`, both
different nested files. `grep -iln "claims-register" tickets/GL-*.md
tickets/OVERLAPS.md` (run this session): zero matches anywhere in the
corpus or the registry. Since no ticket's Authored boundary claims either
target file, no `tickets/OVERLAPS.md` row is required under that
registry's own same-file-conflict scope -- this relationship is instead
recorded in prose above, mirroring how `GL-EXP-026` recorded its own
no-overlap finding.)

```text
README.md                       # "Foundry runtime candidate" row (line 16) only
governance/claims-register.md   # CLM-011 row (line 15), Standing column only
tickets/GL-EXP-030.md
```

No other row or line in either file is touched. No file is deleted,
moved, or regenerated. `evidence/foundry-runtime-candidate.json` is not
manufactured by this ticket (that would launder an unverified build
artifact into a checked-in claim, the same reasoning `GL-ERRC-017` and
`GL-EXP-026` already state for the sibling fields).

## Hard laws

1. `README.md:16`'s "State" column becomes `` `UNVERIFIED` ``, not
   `` `REFUSED` `` or silently left `` `ALIVE` `` -- matching `GL-ERRC-017`'s
   Hard Law 1 disposition for the identical claim in the sibling files
   (the claim itself -- "exact candidate verification only," "not the
   stable dependency" -- may still be true; only the *evidence for it* is
   confirmed not currently locatable).
2. `governance/claims-register.md:15`'s (`CLM-011`) "Standing" column
   becomes `` `UNVERIFIED` ``, not `` `REFUSED` `` or silently left
   `` `ALIVE` ``, for the same reason. The `Ceiling` column
   (`` `TESTED` ``) is left unchanged -- this ticket narrows the standing
   verdict only, matching `GL-EXP-026`'s Hard Law 2 discipline of not
   touching adjacent fields.
3. Both rows' remaining prose (README's basis text, claims-register's
   Claim/Evidence/Nonclaim columns) is left byte-identical except for the
   one standing token in each -- this ticket does not rewrite the
   candidate identity, the revision hash, or the "not the stable
   dependency" nonclaim, matching `GL-EXP-026`'s Hard Law 2.
4. No other row in either table (`README.md`'s eight other rail rows,
   `claims-register.md`'s twelve other `CLM-*` rows) is modified by this
   ticket.
5. No table structure (column count, header row, delimiter row) changes
   in either file -- only the two identified cell values change.
6. If `GL-ERRC-017` and/or `GL-EXP-026` execute before this ticket and
   their execution finds `foundry_runtime_candidate`/`verified_foundry_
   runtime_candidate` standing should for any reason land somewhere other
   than `UNVERIFIED` (per their own re-verification allowances), this
   ticket's execution re-checks that outcome and matches it rather than
   mechanically applying `UNVERIFIED` regardless of what the sibling
   tickets actually did -- matching `GL-EXP-026`'s Hard Law 4.

## Falsifiers

- `grep -n "Foundry runtime candidate" README.md` still shows `` `ALIVE` ``
  in that row after execution (must show `` `UNVERIFIED` ``).
- `grep -n "CLM-011" governance/claims-register.md` still shows `` `ALIVE` ``
  as the Standing column value after execution (must show
  `` `UNVERIFIED` ``).
- `git diff --stat` after this ticket shows any file other than
  `README.md`, `governance/claims-register.md`, and
  `tickets/GL-EXP-030.md`.
- `git diff README.md` after execution touches any line other than line
  16.
- `git diff governance/claims-register.md` after execution touches any
  line other than line 15.
- The revision hash `458f0f88…` or the "not the stable dependency" /
  "Candidate is not admitted as the stable manufacturing dependency"
  nonclaim text is altered or removed from either row.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
grep -n "Foundry runtime candidate" README.md
  # expect (pre-fix): | Foundry runtime candidate | `ALIVE` | ...
grep -n "CLM-011" governance/claims-register.md
  # expect (pre-fix): | CLM-011 | ... | `TESTED` | `ALIVE` | ...
test -e evidence/foundry-runtime-candidate.json && echo "UNEXPECTED: exists" || echo "confirmed missing"
  # expect: confirmed missing

# After the fix:
grep -n "Foundry runtime candidate" README.md
  # expect: | Foundry runtime candidate | `UNVERIFIED` | ...
grep -n "CLM-011" governance/claims-register.md
  # expect: | CLM-011 | ... | `TESTED` | `UNVERIFIED` | ...

git diff --stat   # must show only README.md, governance/claims-register.md, tickets/GL-EXP-030.md
```

## Evidence this ticket is grounded in (verified this session)

- `grep -n "foundry_runtime_candidate\|458f0f88\|ALIVE" README.md` and
  direct `Read` of `README.md` lines 1-25 (run this session): confirms
  line 16 verbatim as quoted in Outcome, confirms the table is the
  "Project 001 standing" section immediately below the file's title and
  one-line pitch -- the first substantive content a reader of the repo's
  root `README.md` encounters.
- `grep -n "458f0f88\|foundry runtime candidate\|CLM-011"
  governance/claims-register.md` and direct `Read` of the full 20-line
  file (run this session): confirms line 15 verbatim as quoted in
  Outcome, confirms it is row `CLM-011` of a 13-row claims table that is
  the file's entire content.
- `test -e evidence/foundry-runtime-candidate.json` (run this session):
  exits non-zero (missing) -- independently reconfirms the same gap
  `GL-ERRC-017` and `GL-EXP-026` already found.
- Direct `Read` of `tickets/GL-ERRC-017.md` in full (this session):
  confirms its Outcome section's "zero locatable evidence, full stop"
  finding, its Hard Law 1 (`UNVERIFIED` disposition), and its Authored
  boundary naming exactly `authority/project-001-promotion.json` and
  `tickets/GL-ERRC-017.md` -- no other file.
- Direct `Read` of `tickets/GL-EXP-026.md` in full (this session):
  confirms its Outcome section's identical finding for
  `authority/verifier-appliance-profile.json`, its Hard Law 1
  (`UNVERIFIED` disposition), and its Authored boundary naming exactly
  that file and `tickets/GL-EXP-026.md` -- no other file.
- `grep -n "README.md" tickets/GL-ERRC-017.md tickets/GL-EXP-026.md` (run
  this session): zero matches, exit 1 -- confirms neither ticket names
  `README.md` anywhere in its text.
- `grep -il "claims-register" tickets/GL-*.md` (run this session, across
  all 51 `tickets/GL-*.md` files): zero matches, exit 1 -- confirms no
  ticket in the corpus, including `GL-ERRC-017` and `GL-EXP-026`, names
  `governance/claims-register.md` anywhere.
- `grep -iln "README.md" tickets/GL-*.md` (run this session): matches
  `GL-AUTO-001.md`, `GL-EXP-013.md`, `GL-EXP-012.md`, `GL-EXP-023.md`.
  Each checked individually this session (quoted context above): none
  claims the root `README.md` as an Authored-boundary target -- three cite
  nested `README.md` files under `packs/`/`planning/`, two cite line 14
  (a different rail, "Verifier Appliance reference") purely as motivating
  evidence for `appliance/bin/*.py` changes.
- `grep -iln "claims-register" tickets/OVERLAPS.md` (run this session):
  zero matches -- confirms the overlap registry has no existing section
  for this file, consistent with no ticket claiming it.
- `git rev-parse HEAD` (run this session):
  `bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's
  declared Base and matching the Base both `GL-ERRC-017` and `GL-EXP-026`
  declare.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
duplicate-claim gap (the same unbacked `ALIVE` standing for the same
candidate revision, asserted in two human-facing files neither
`GL-ERRC-017` nor `GL-EXP-026` touches). The actual row edits have not
been made. Once `GL-ERRC-017` and `GL-EXP-026` execute, re-verify their
actual chosen standing value for the `foundry_runtime_candidate` rail (per
this ticket's Hard Law 6) before applying this ticket's own edits, so all
four copies land on the same honest value rather than diverging again
through independent execution order.
