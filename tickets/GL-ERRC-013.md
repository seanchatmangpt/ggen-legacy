# GL-ERRC-013 — AGENTS.md ticket-header sync drift (7 tickets missing from active/concurrent list)

**Status:** `EXECUTED` — fix applied and verified: `AGENTS.md` gained a
`drafted tickets (see tickets/):` field enumerating all `tickets/GL-*.md`
files present at execution time (slug + each file's own first
`**Status:**` line value, or `(no Status: line in ticket file)` for files
lacking one); `active executable ticket`/`concurrent executable ticket`
left unchanged at `GL-LSP-001`/`GL-PLAN-002`; verified by re-reading
`AGENTS.md` and confirming every `tickets/GL-*.md` slug appears in the new
field
**Base:** `seanchatmangpt/ggen-legacy@f9b283e`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`AGENTS.md:8-9` names exactly two tickets — `active executable ticket:
GL-LSP-001` and `concurrent executable ticket: GL-PLAN-002` — and
`CLAUDE.md`'s "Ticket-gated admission" section instructs sessions to
"check [`AGENTS.md`'s header] before starting executable work" to learn
"the active and concurrent executable tickets for the current session."
Since that header was last written, one further ticket has been executed
(`GL-ARCH-003`, code live in `tools/v26.8.1/legacy_archaeology.py`) and
seven more have been drafted/admitted-`NOT_STARTED`
(`GL-CONTRACT-004`, `GL-MANUFACTURE-005`, `GL-VERIFY-006`,
`GL-RECEIPT-007`, `GL-ERRC-008`, `GL-ERRC-009`, plus this pass's own new
tickets) — none of which appear in `AGENTS.md`'s header, so a session
following `CLAUDE.md`'s own instructed workflow ("check it before
starting executable work") reads a header that is silently 8 tickets
stale and would not learn `GL-ARCH-003` is already executed, or that 6+
other tickets exist in `tickets/` at all, without independently listing
the `tickets/` directory. This ticket adds a third header field,
`drafted tickets (see tickets/):`, enumerating every `tickets/GL-*.md`
file's slug and its own file-stated `Status:` line value (not
re-deriving standing, only mirroring what each ticket already
self-reports), so `AGENTS.md`'s header becomes a single source that
lists every ticket in the repo, not just the original two, while leaving
the existing `active`/`concurrent` semantics (which ticket a session
should treat as its primary/secondary scope) exactly as they were.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before assuming sole ownership of a path below.)

```text
AGENTS.md            # add one new header field listing all drafted/executed tickets by slug + status
tickets/GL-ERRC-013.md
```

`AGENTS.md`'s `active executable ticket`/`concurrent executable ticket`
fields, and every other section of the file (Mission, pipeline diagram,
everything below the header), are unchanged — this ticket adds one
enumerating field, it does not reassign which ticket is "active."

## Hard laws

1. `active executable ticket: GL-LSP-001` and
   `concurrent executable ticket: GL-PLAN-002` are not changed by this
   ticket — reassigning which ticket is active/concurrent is a scope
   decision for whoever admits the next executable ticket, not this
   sync-drift fix.
2. The new field's per-ticket status values are copied verbatim from each
   ticket file's own `**Status:**` line (first such line in the file) —
   this ticket does not independently assess or upgrade any ticket's
   standing.
3. Every `tickets/GL-*.md` file present at execution time appears in the
   new field — no ticket is silently omitted (this is the exact failure
   mode this ticket exists to fix, so partial coverage would defeat its
   own purpose).
4. This ticket is itself self-referential: once merged, `GL-ERRC-013`
   must appear in the field it adds, and the field's construction must be
   re-run at execution time (not just a fixed count of what existed at
   drafting time), since new tickets will keep being drafted (this ticket
   itself is 4 of that ongoing count) — the acceptance check below
   verifies the field's ticket count matches a live `ls tickets/GL-*.md`
   count at execution time, not a number hardcoded in this ticket.

## Falsifiers

- `AGENTS.md`'s new field omits any `tickets/GL-*.md` file present in the
  repository at execution time.
- Any status value in the new field doesn't match the corresponding
  ticket file's own `**Status:**` line.
- `active executable ticket`/`concurrent executable ticket` values differ
  from `GL-LSP-001`/`GL-PLAN-002` after this ticket.
- `git diff --stat` shows any file changed other than `AGENTS.md` and
  `tickets/GL-ERRC-013.md`.

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Confirm the drift before fixing:
grep -c "^- active executable ticket\|^- concurrent executable ticket" AGENTS.md   # expect 2
ls tickets/GL-*.md | wc -l   # expect > 2, confirming more tickets exist than the header names

# After the fix, confirm every real ticket file appears in the new field:
for f in tickets/GL-*.md; do
  slug=$(basename "$f" .md)
  grep -q "$slug" AGENTS.md || echo "MISSING FROM AGENTS.md: $slug"
done
# (expect no output)

# Confirm active/concurrent unchanged (correction, per tickets/AUDIT-REPORT.md's
# check-4 finding: the real AGENTS.md wraps these values in backticks --
# these greps previously used an unanchored-without-backticks pattern that
# fails against the real file even when untouched):
grep '^- active executable ticket: `GL-LSP-001`$' AGENTS.md
grep '^- concurrent executable ticket: `GL-PLAN-002`$' AGENTS.md

git diff --stat   # must show only AGENTS.md and tickets/GL-ERRC-013.md
```

## Evidence this ticket is grounded in (verified this session)

- `AGENTS.md:8-9` (read directly this session):
  ```text
  - active executable ticket: GL-LSP-001
  - concurrent executable ticket: GL-PLAN-002
  ```
  is the complete ticket-naming content of the header — no other ticket
  slug appears anywhere in `AGENTS.md`.
- `ls tickets/GL-*.md` (run directly this session) lists 10 files before
  this ticket's own creation: `GL-ARCH-003.md`, `GL-AUTO-001.md`,
  `GL-CONTRACT-004.md`, `GL-ERRC-008.md`, `GL-ERRC-009.md`,
  `GL-LSP-001.md`, `GL-MANUFACTURE-005.md`, `GL-PLAN-002.md`,
  `GL-RECEIPT-007.md`, `GL-VERIFY-006.md` — 8 of these 10 are absent from
  `AGENTS.md`'s header.
- `CLAUDE.md`'s "Ticket-gated admission" section (read directly this
  session): "`AGENTS.md`'s header names the active and concurrent
  executable tickets for the current session — check it before starting
  executable work." This is the repo's own stated reliance on the header
  being complete/current, which the drift directly undermines for any
  session that follows this instruction literally rather than also
  independently listing `tickets/`.
- `docs/v26.8.20/ultracode-loop-progress.md:60` (item 13, this repo's own
  prior audit, same session lineage): "Real gap: AGENTS.md:8-9 still only
  names GL-LSP-001/GL-PLAN-002 as active/concurrent tickets — GL-ARCH-003
  (executed this session, code live in legacy_archaeology.py) and the 4
  drafted tickets aren't reflected. Not fixed directly (AGENTS.md is
  outside GL-ARCH-003's declared authored boundary — editing it would be
  self-expanding scope outside ticket-gated admission); flagged as a
  recommendation for the repo owner or a follow-up ticket." This ticket is
  that follow-up, now covering 8 undocumented tickets (the 4 named in that
  finding, `GL-ERRC-008`, `GL-ERRC-009`, and this pass's own new tickets),
  not just the original 4.

## Standing

`ALIVE` — re-verified in the main checkout 2026-08-21 (this Standing
section previously contradicted the file's own `**Status:** EXECUTED`
header line, left stale from before the fix landed — corrected here per
`GL-EXP-014`'s finding of the same defect class):

```
$ grep -n "drafted tickets" AGENTS.md
10:- drafted tickets (see tickets/):
```

`AGENTS.md`'s header field is present and enumerates the real ticket set,
matching this ticket's own Status-line claim.
