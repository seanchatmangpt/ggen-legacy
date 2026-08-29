# GL-EXP-020 — Create `scripts/verify_ticket_overlaps.py`, a machine-checkable admission gate for `tickets/OVERLAPS.md`

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tickets/OVERLAPS.md` states its own coordination rule as prose only, with no
machine enforcement: "before admitting a new ticket, grep every existing
`tickets/GL-*.md`'s Authored boundary for the file paths the new ticket is
about to claim. If any overlap, add a row here -- don't rely on remembering
to write it in both files." Verified this session
(`grep -rln "OVERLAPS.md\|overlap" scripts/*.py tools/v26.8.1/*.py`): no
script anywhere in the repo implements this check. The one incidental hit,
`tools/v26.8.1/legacy_archaeology.py:661`, is unrelated -- it is the word
"overlaps" inside a `notes=` string about ggen-graph's hashing machinery,
and does not reference `tickets/OVERLAPS.md` at all (confirmed:
`grep -q "tickets/OVERLAPS.md" tools/v26.8.1/legacy_archaeology.py` exits 1).

That the rule is manual-only is precisely why it has already drifted. A
real, working parser prototype run this session (Python stdlib `re`, no new
dependency -- see Evidence) against every `tickets/GL-*.md`'s actual
`## Authored boundary` fenced block found **4** non-`tickets/`-prefixed
files each claimed by 2 distinct tickets with **no corresponding disclosed
row** in `tickets/OVERLAPS.md`:

- `appliance/bin/verify-standing-portfolio.py` -- claimed by `GL-EXP-013`
  (deletes its private `sha256_file()`/`read_json()`, imports shared) and
  `GL-EXP-015` (raises its `challenge_files` scan out of a bare
  `except Exception: pass`). No `## appliance/bin/verify-standing-portfolio.py`
  section exists in `tickets/OVERLAPS.md` (confirmed:
  `grep -n "^## " tickets/OVERLAPS.md` lists only 6 sections, none for this
  path).
- `tools/v26.8.20/observe_contract.py` -- claimed by `GL-EXP-011` (changes
  `git_head()`'s return behavior) and `GL-EXP-012` (wires the script into
  `justfile` as a new recipe; states "no source change" to the script
  itself). `tools/v26.8.20/observe_contract.py` appears exactly once in
  `tickets/OVERLAPS.md` (confirmed: `grep -n observe_contract
  tickets/OVERLAPS.md` → one hit, line 109), but that hit is inside the
  `## \`justfile\`` section's prose describing `GL-EXP-012`'s recipe
  addition -- it does not disclose that `GL-EXP-011` also claims this same
  file in its own Authored boundary, and `GL-EXP-011` is not named anywhere
  in `tickets/OVERLAPS.md` (confirmed:
  `grep -c "GL-EXP-011" tickets/OVERLAPS.md` → 0).
- `appliance/bin/build-standing-portfolio.py` -- claimed by `GL-EXP-013`
  (deletes its private helpers, imports shared) and `GL-RECEIPT-007`
  (SLSA/DSSE provenance projection addition). Zero mentions of
  `build-standing-portfolio` anywhere in `tickets/OVERLAPS.md` (confirmed
  this session), even though `GL-EXP-013`'s own prose acknowledges
  `GL-RECEIPT-007` by name -- the reconciliation exists in ticket prose but
  was never promoted to the registry the project's own rule requires.
- `appliance/bin/transparency-log.py` -- claimed by `GL-ERRC-010` (owns
  `verify()`'s `--anchor` mode) and `GL-EXP-013` (deletes its private
  helpers, imports shared). Same gap: zero mentions of `transparency-log`
  anywhere in `tickets/OVERLAPS.md` this session, despite `GL-EXP-013`'s
  own prose naming `GL-ERRC-010` directly.

The first two of these four are exactly what the originating candidate item
for this ticket cited; the second two were found independently this session
by actually running the parser prototype end-to-end rather than
hand-checking two paths, which is itself the argument for this ticket --
manual grepping missed 2 of the 4 real gaps that existed in the corpus at
the moment the candidate item was drafted.

This mirrors the already-admitted `GL-ERRC-018` (`NOT_STARTED`), which
built the identical shape of fix -- a new, additive, read-only, stdlib-only
`scripts/verify_*.py` admission gate -- for a different invariant (CATALOG
disposition-confidence in `legacy-capabilities.ttl`). `GL-ERRC-018`'s own
script (`scripts/verify_catalog_disposition_confidence.py`) does not yet
exist on disk (confirmed this session: `ls
scripts/verify_catalog_disposition_confidence.py` → no such file),
consistent with its ticket's own `NOT_STARTED` status -- it is a real,
admitted precedent for this ticket's shape of fix, not a claim that the
precedent script itself is executed.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below. Confirmed
this session via `grep -n verify_ticket_overlaps tickets/OVERLAPS.md`: no
existing entry for this file or script name.)

```text
scripts/verify_ticket_overlaps.py   # new
tickets/GL-EXP-020.md
```

No change to `tickets/OVERLAPS.md`, any `tickets/GL-*.md` ticket file, or
any file named as a target inside any ticket's Authored boundary -- this
script is read-only against all of them. No change to
`scripts/verify_catalog_disposition_confidence.py` (`GL-ERRC-018`'s
target, not yet created) or any other existing `scripts/verify_*.py` file.
Wiring this new script into `justfile` or `.github/workflows/` CI is
explicitly out of scope, matching `GL-ERRC-018`'s own precedent of leaving
CI-wiring to a follow-up session that can confirm runtime cost and
false-positive rate against a real CI run first.

## Hard laws

1. The script is read-only against every `tickets/*.md` file (including
   `tickets/OVERLAPS.md`) in every code path, including its own error
   paths -- it never writes, reformats, or auto-inserts a missing row.
2. The script must parse specifically the fenced code block immediately
   following each ticket's `## Authored boundary` heading (up to the next
   `## ` heading), not a bare substring search across the whole ticket
   file. Verified this session: the literal string `tickets/OVERLAPS.md`
   appears somewhere in 24 of the 39 `tickets/GL-*.md` files (boilerplate
   prose: "Cross-ticket file overlaps... are tracked in
   `tickets/OVERLAPS.md`"), but a real parse of only the fenced blocks
   found it as an actual claimed edit target in exactly 1 of those 24
   (`GL-EXP-013.md`) -- a bare substring search would manufacture 23 false
   collisions on this one path alone.
3. Ticket files with no `## Authored boundary` heading, or no fenced code
   block immediately beneath it, must be skipped with a named warning
   (the ticket's filename) printed to stderr, not treated as a fatal
   parse error and not silently dropped with no trace. Verified this
   session: `tickets/GL-LSP-001.md` is a real, current instance of this
   shape -- an older ticket template using `## Identity` / `## Admission`
   / `## Observable contract` instead of `## Outcome` / `## Authored
   boundary`, with no `## Authored boundary` heading anywhere in the file.
4. Paths beginning with `tickets/` that appear inside a fenced
   Authored-boundary block (a ticket referencing its own file, or one
   ticket naming another ticket file as an edit target) are excluded from
   the disclosure check entirely -- they are a structurally different,
   self-disclosing class. Verified this session: 4 such cross-ticket-file
   collisions exist today under the real parse (`tickets/GL-AUTO-001.md`
   claimed by `GL-AUTO-001` and `GL-ERRC-023`; `tickets/GL-ERRC-009.md` and
   `tickets/GL-ERRC-013.md` both claimed by `GL-ERRC-013`/`GL-ERRC-009`
   respectively and `GL-EXP-014`; `tickets/GL-VERIFY-006.md` claimed by
   `GL-VERIFY-006` and `GL-ERRC-012`) -- in every case the referencing
   ticket's own title names the referenced ticket directly (e.g.
   `GL-ERRC-023`: "Fix `GL-AUTO-001.md`'s fabricated CI-workflow claim..."),
   so these are not the silent-collision failure mode this registry
   exists to catch, and must not be flagged.
5. For every remaining (non-`tickets/`-prefixed) path claimed inside 2 or
   more distinct tickets' fenced Authored-boundary blocks, the script must
   find that exact path named under its own `## <path>` heading in
   `tickets/OVERLAPS.md`, with every contributing ticket ID named in that
   section's body. A path mentioned only incidentally under a *different*
   file's heading (verified this session:
   `tools/v26.8.20/observe_contract.py` appears once in `tickets/OVERLAPS.md`,
   inside the `## \`justfile\`` section, not its own) does not count as
   disclosure.
6. On finding an undisclosed overlap, the script exits non-zero and prints
   every offending path together with every contributing ticket ID on its
   own line -- matching `GL-ERRC-018`'s own "named, not just counted"
   falsifier precedent, not a bare count.
7. No new dependency -- stdlib only (`re`, `pathlib`/`glob`, `argparse`),
   matching the existing `scripts/verify_*.py` convention (confirmed this
   session: `scripts/verify_docs.py` uses only `argparse`, `hashlib`,
   `json`, `re`, `tomllib`, `pathlib`).
8. `git diff --stat` after this ticket touches only
   `scripts/verify_ticket_overlaps.py` and this ticket file.

## Falsifiers

- Run against the real, current repo at this ticket's `Base` commit, the
  script does not exit non-zero, or its output does not name
  `appliance/bin/verify-standing-portfolio.py` alongside both `GL-EXP-013`
  and `GL-EXP-015` and `tools/v26.8.20/observe_contract.py` alongside both
  `GL-EXP-011` and `GL-EXP-012` -- the two gaps the originating candidate
  item cited.
- The same real run does not also name `appliance/bin/build-standing-portfolio.py`
  alongside `GL-EXP-013`/`GL-RECEIPT-007`, and
  `appliance/bin/transparency-log.py` alongside `GL-ERRC-010`/`GL-EXP-013`
  -- the two further gaps this session's own prototype parse found.
- A synthetic two-ticket fixture claiming the same non-`tickets/`-prefixed
  path, paired with an `OVERLAPS.md` fixture carrying a disclosed row
  under that path's own heading naming both ticket IDs, does not produce a
  clean exit-0 run -- proving the check is not vacuously failing.
- The script raises an uncaught exception (rather than a per-file skip
  warning) on a fixture shaped like `tickets/GL-LSP-001.md` (no `##
  Authored boundary` heading at all).
- The script flags any of the 4 real `tickets/*.md`-to-`tickets/*.md`
  collisions named in Hard law 4 as an `OVERLAPS.md`-disclosure violation
  -- these are explicitly excluded and must never produce a false
  positive.
- `git diff --stat` after this ticket touches any file outside
  `scripts/verify_ticket_overlaps.py` and `tickets/GL-EXP-020.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the 4 known gaps before touching anything:
grep -n "^## " tickets/OVERLAPS.md
grep -n "observe_contract\|verify-standing-portfolio\|build-standing-portfolio\|transparency-log" tickets/OVERLAPS.md

python3 scripts/verify_ticket_overlaps.py
echo "EXIT:$?"
# expect nonzero exit; output names, at minimum:
#   appliance/bin/verify-standing-portfolio.py   (GL-EXP-013, GL-EXP-015)
#   tools/v26.8.20/observe_contract.py           (GL-EXP-011, GL-EXP-012)
#   appliance/bin/build-standing-portfolio.py    (GL-EXP-013, GL-RECEIPT-007)
#   appliance/bin/transparency-log.py            (GL-ERRC-010, GL-EXP-013)

git diff --stat   # must show only scripts/verify_ticket_overlaps.py and
                   # tickets/GL-EXP-020.md
```

## Evidence this ticket is grounded in (verified this session)

- `grep -rln "OVERLAPS.md\|overlap" scripts/*.py tools/v26.8.1/*.py`: one
  hit, `tools/v26.8.1/legacy_archaeology.py`. Direct inspection
  (`grep -n "OVERLAPS\|overlap" tools/v26.8.1/legacy_archaeology.py`) shows
  it is line 661, a `notes="Notably overlaps in spirit with ggen-graph's
  current deterministic-hashing/receipt machinery..."` string, unrelated
  to `tickets/OVERLAPS.md`; `grep -q "tickets/OVERLAPS.md"
  tools/v26.8.1/legacy_archaeology.py` exits 1, confirming no reference.
- `find . -iname "*verify_ticket_overlap*"`: no output -- the proposed
  script does not already exist anywhere in the repo.
- Direct `Read` of `tickets/OVERLAPS.md`: the "Rule going forward" prose
  quoted in Outcome, confirmed verbatim.
- `grep -n "^## " tickets/OVERLAPS.md`: exactly 6 sections
  (`tools/v26.8.1/legacy_archaeology.py`, `tools/v26.8.1/src/coverage_projection.rs`,
  `tools/v26.8.1/src/bin/subsystem_verifier.rs`,
  `scripts/verify_foundry_bootstrap.py`, `AGENTS.md`, `justfile`), none for
  `appliance/bin/verify-standing-portfolio.py`,
  `tools/v26.8.20/observe_contract.py`,
  `appliance/bin/build-standing-portfolio.py`, or
  `appliance/bin/transparency-log.py`.
- Real Python prototype run this session (stdlib `re`/`glob` only, no
  mocking) that parses every `tickets/GL-*.md`'s `## Authored boundary`
  fenced block and builds a real path -> ticket-ID map from the real files
  on disk: found exactly 1 ticket (`tickets/GL-LSP-001.md`) with no
  parsable Authored-boundary section, and found the following
  non-`tickets/`-prefixed paths claimed by 2+ tickets:
  `AGENTS.md`, `appliance/bin/build-standing-portfolio.py`,
  `appliance/bin/transparency-log.py`,
  `appliance/bin/verify-standing-portfolio.py`, `justfile`,
  `scripts/verify_foundry_bootstrap.py`,
  `tools/v26.8.1/legacy_archaeology.py`,
  `tools/v26.8.1/src/bin/subsystem_verifier.rs`,
  `tools/v26.8.1/src/coverage_projection.rs`,
  `tools/v26.8.20/observe_contract.py` -- cross-checked each against
  `tickets/OVERLAPS.md`'s 6 real headings: the first 6 are disclosed, the
  last 4 (`build-standing-portfolio.py`, `transparency-log.py`,
  `verify-standing-portfolio.py`, `observe_contract.py`) are not.
- The same prototype run also surfaced 4 `tickets/*.md`-to-`tickets/*.md`
  collisions (`GL-AUTO-001.md`, `GL-ERRC-009.md`, `GL-ERRC-013.md`,
  `GL-VERIFY-006.md`, each claimed by 2 tickets); direct `Read` of
  `tickets/GL-ERRC-023.md:1` and `tickets/GL-EXP-014.md:1` confirms both
  are self-disclosing "fix ticket X" tickets naming their target ticket in
  their own title, not silent collisions.
- Confirmed the fenced-block-vs-prose distinction (Hard law 2) directly:
  a second prototype pass isolated only the fenced block after `##
  Authored boundary` in each of the 24 files containing the substring
  `tickets/OVERLAPS.md`, and found it inside the fenced block in exactly 1
  of them (`GL-EXP-013.md`), confirming a bare substring search would
  produce 23 false collisions on this single path.
- `cat tickets/GL-ERRC-018.md`: confirms the precedent ticket's shape
  (new, additive, read-only, stdlib-only `scripts/verify_*.py`, named
  offending entries not a bare count, same header format) and its
  `NOT_STARTED` status; `ls scripts/verify_catalog_disposition_confidence.py`
  confirms that script does not yet exist, consistent with that status.
- `head -30 scripts/verify_docs.py`: confirms the existing
  `scripts/verify_*.py` convention is stdlib-only (`argparse`, `hashlib`,
  `json`, `re`, `tomllib`, `pathlib`), no third-party dependency.
- `git rev-parse HEAD`: `bce7f6386c4203784beaae426e40804636c4151a`, matching
  this ticket's declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
undisclosed-overlap finding (4 real gaps in `tickets/OVERLAPS.md`, 2 more
than the originating candidate item cited) and a real, tested-live parsing
prototype for the eventual script; the actual committed
`scripts/verify_ticket_overlaps.py` and its own test coverage have not
been implemented.
