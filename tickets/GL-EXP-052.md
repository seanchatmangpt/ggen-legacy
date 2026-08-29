# GL-EXP-052 — Create `scripts/verify_agents_ticket_sync.py`, a machine-checkable admission gate for `AGENTS.md`'s `drafted tickets` field

**Status:** `EXECUTED` 2026-08-21 -- real script created and verified against the actual checkout, all Falsifiers re-run for real, `just ci-all` clean
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`AGENTS.md`'s `- drafted tickets (see tickets/):` field enumerates
`tickets/GL-*.md` files by slug, added by `GL-ERRC-013` (`EXECUTED`) whose
own Hard law 4 states the field "must be re-run at execution time (not
just a fixed count of what existed at drafting time), since new tickets
will keep being drafted" -- an intent stated in prose, with no script
enforcing it. Verified this session the rule has already drifted exactly
the way `GL-ERRC-013`'s own Hard law 4 anticipated: a real count of every
`tickets/GL-*.md` file on disk against every ticket slug actually present
inside the field's own bulleted block (from the `- drafted tickets (see
tickets/):` line down to the next top-level `- protocol runtime:` line)
finds:

- **71** total `tickets/GL-*.md` files on disk (`ls tickets/GL-*.md | wc
  -l`).
- **19** distinct ticket slugs listed inside the field's bulleted block
  (`GL-ARCH-003`, `GL-AUTO-001`, `GL-CONTRACT-004`, `GL-ERRC-008`,
  `GL-ERRC-009`, `GL-ERRC-010`, `GL-ERRC-011`, `GL-ERRC-012`,
  `GL-ERRC-013`, `GL-ERRC-014`, `GL-ERRC-015`, `GL-ERRC-017`,
  `GL-ERRC-018`, `GL-ERRC-019`, `GL-LSP-001`, `GL-MANUFACTURE-005`,
  `GL-PLAN-002`, `GL-RECEIPT-007`, `GL-VERIFY-006`).
- **52** ticket files present on disk with no entry anywhere in the field
  -- every `GL-EXP-*` ticket except `GL-EXP-020` (`GL-EXP-001` through
  `GL-EXP-048` plus `GL-ERRC-016`, `GL-ERRC-020`, `GL-ERRC-022`,
  `GL-ERRC-023`), confirmed by a real `comm -23` diff between a sorted
  `ls tickets/GL-*.md` stem list and a sorted list of every `GL-[A-Z]+-[0-9]+`
  slug matched inside the field's own block.
- Checked the reverse direction too: every one of the 19 slugs listed
  inside the field has a real corresponding `tickets/GL-*.md` file on
  disk (`comm -13` of the same two sorted lists returns empty) -- today's
  drift is one-directional (files not yet added to the field), not a
  stale reference to a deleted file, though a real gate should still
  check both directions since nothing in the repo prevents the reverse
  case from occurring later.

This mirrors the already-admitted `GL-EXP-020` (`NOT_STARTED`), whose own
Outcome diagnoses the structurally identical problem for a different
manually-maintained registry (`tickets/OVERLAPS.md`'s "before admitting a
new ticket, grep every existing ticket... don't rely on remembering to
write it in both files" rule): "That the rule is manual-only is precisely
why it has already drifted." `GL-EXP-020`'s own target script,
`scripts/verify_ticket_overlaps.py`, does not exist on disk yet either
(confirmed this session: `ls scripts/verify_ticket_overlaps.py` -> no such
file), consistent with its `NOT_STARTED` status -- it is a real, admitted
precedent for this exact shape of fix (new, additive, read-only,
stdlib-only `scripts/verify_*.py`, naming every offending entry rather
than a bare count), not a claim that the precedent script is itself
running today.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below. Checked
this session: no existing `tickets/OVERLAPS.md` section or
`tickets/GL-*.md` Authored-boundary block names
`scripts/verify_agents_ticket_sync.py` anywhere in the corpus. Two
tickets do claim `AGENTS.md` itself as a write target --
`GL-ERRC-013` (`EXECUTED`, added the field this ticket now verifies) and
`GL-PLAN-002` (owns only its own "concurrent ticket admission stanza"),
both already reconciled in `tickets/OVERLAPS.md`'s existing `##
\`AGENTS.md\`` section -- but this ticket only *reads* `AGENTS.md`, it is
not a write target here, so no new `OVERLAPS.md` row is required for
that file; the row below discloses the new script path instead, which no
other ticket claims.)

```text
scripts/verify_agents_ticket_sync.py   # new
tickets/GL-EXP-052.md
```

No change to `AGENTS.md`, `tickets/OVERLAPS.md`, any `tickets/GL-*.md`
ticket file, or `scripts/verify_ticket_overlaps.py` (`GL-EXP-020`'s
target, not yet created) -- this script is read-only against `AGENTS.md`
and every ticket file. Wiring this new script into `justfile` or
`.github/workflows/` CI is explicitly out of scope, matching
`GL-EXP-020`'s and `GL-ERRC-018`'s own precedent of leaving CI-wiring to a
follow-up session that can confirm runtime cost and false-positive rate
against a real CI run first.

## Hard laws

1. The script is read-only against `AGENTS.md` and every `tickets/*.md`
   file in every code path, including its own error paths -- it never
   writes, reformats, or auto-inserts a missing entry.
2. The script must parse specifically the bulleted block that begins at
   the line matching `- drafted tickets (see tickets/):` and ends at the
   next line matching `^- ` (today, `- protocol runtime:`), not a bare
   substring search across the whole file -- `AGENTS.md` contains ticket
   slugs elsewhere (`active executable ticket`, `concurrent executable
   ticket` header lines, prose in later sections) that must not be
   double-counted as separate field entries. Verified this session: the
   field's block as bounded above contains exactly 19 `GL-[A-Z]+-[0-9]+`
   matches, matching the real bulleted list read directly from the file.
3. Ticket slugs are matched with the pattern `GL-[A-Z]+-[0-9]+` against
   both the field's block and every `tickets/GL-*.md` filename stem (case
   preserved, no normalization beyond that).
4. For every `tickets/GL-*.md` file whose stem does not appear as a slug
   inside the field's block, the script reports it as missing-from-field.
   For every slug inside the field's block with no corresponding
   `tickets/<slug>.md` file on disk, the script reports it as
   stale-in-field (the reverse direction; zero such cases exist in the
   corpus today, per Outcome, but the check must still run so a future
   ticket removal/rename is caught).
5. On finding any missing-from-field or stale-in-field entry, the script
   exits non-zero and prints every offending slug by name, tagged with
   which direction it failed (`missing-from-field` or `stale-in-field`)
   -- matching `GL-EXP-020`'s and `GL-ERRC-018`'s own "named, not just
   counted" falsifier precedent, not a bare count.
6. No new dependency -- stdlib only (`re`, `pathlib`/`glob`, `argparse`),
   matching the existing `scripts/verify_*.py` convention (confirmed this
   session: `scripts/verify_docs.py` uses only `argparse`, `hashlib`,
   `json`, `re`, `tomllib`, `pathlib`).
7. `git diff --stat` after this ticket touches only
   `scripts/verify_agents_ticket_sync.py` and this ticket file.

## Falsifiers

- Run against the real, current repo at this ticket's `Base` commit, the
  script does not exit non-zero, or its output does not name all 52 real
  missing-from-field tickets found this session (at minimum
  `GL-EXP-001` through `GL-EXP-048` except `GL-EXP-020`, plus
  `GL-ERRC-016`, `GL-ERRC-020`, `GL-ERRC-022`, `GL-ERRC-023`).
- The same real run reports any of the 19 tickets actually listed inside
  the field's block (e.g. `GL-ARCH-003`, `GL-PLAN-002`, `GL-LSP-001`) as
  missing-from-field -- a false positive on an already-disclosed entry.
- A synthetic two-line fixture (`AGENTS.md`-shaped text with a
  `drafted tickets` block naming ticket `X` but not ticket `Y`, paired
  with fixture files `tickets/X.md` and `tickets/Y.md` both present) does
  not report exactly `Y` as missing-from-field and nothing else -- proving
  the check is not vacuously failing.
- A synthetic fixture where the field's block names a ticket `Z` with no
  corresponding `tickets/Z.md` file on disk does not report `Z` as
  stale-in-field -- proving the reverse direction is real, not
  decorative.
- The script raises an uncaught exception, rather than a clear parse
  error, on a fixture `AGENTS.md` missing the `- drafted tickets (see
  tickets/):` line entirely.
- `git diff --stat` after this ticket touches any file outside
  `scripts/verify_agents_ticket_sync.py` and `tickets/GL-EXP-052.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the real drift before touching anything:
ls tickets/GL-*.md | wc -l
sed -n '/- drafted tickets (see tickets\/):/,/^- protocol runtime:/p' AGENTS.md | grep -oE 'GL-[A-Z]+-[0-9]+' | sort -u | wc -l

python3 scripts/verify_agents_ticket_sync.py
echo "EXIT:$?"
# expect nonzero exit; output names, at minimum:
#   missing-from-field: GL-EXP-001 .. GL-EXP-048 (except GL-EXP-020),
#                        GL-ERRC-016, GL-ERRC-020, GL-ERRC-022, GL-ERRC-023
#   (0 stale-in-field entries expected in the current corpus)

git diff --stat   # must show only scripts/verify_agents_ticket_sync.py
                   # and tickets/GL-EXP-052.md
```

## Evidence this ticket is grounded in (verified this session)

- `grep -rln "verify_agents_tickets\|AGENTS.md.*admission gate\|machine-checkable.*AGENTS" tickets/GL-*.md`
  and `grep -rn "scripts/verify_.*agents\|verify.*AGENTS" scripts/*.py justfile`:
  both zero matches -- no such script or ticket exists yet.
- `ls scripts/verify_agents_ticket_sync.py`: no such file.
- `wc -l AGENTS.md` and direct `Read` of `AGENTS.md` lines 1-29: confirms
  the field's exact heading text, indentation, and the 19 real bulleted
  entries quoted in Outcome verbatim.
- `ls tickets/GL-*.md | wc -l`: 71.
- `sed -n '/drafted tickets/,/protocol runtime/p' AGENTS.md | grep -oE 'GL-[A-Z]+-[0-9]+' | sort -u | wc -l`:
  19.
- `comm -23` between a sorted list of all 71 `tickets/GL-*.md` stems and
  the sorted 19-slug field list: 52 lines, matching the Outcome list
  exactly (`GL-EXP-001`-`GL-EXP-048` minus `GL-EXP-020`, plus
  `GL-ERRC-016`, `GL-ERRC-020`, `GL-ERRC-022`, `GL-ERRC-023`).
- `comm -13` of the same two sorted lists: empty -- confirms zero
  stale-in-field entries exist in the corpus today (all 19 listed slugs
  have a real corresponding file on disk).
- `cat tickets/GL-EXP-020.md`: confirms the direct precedent's shape
  (new, additive, read-only, stdlib-only `scripts/verify_*.py`, named
  offending entries not a bare count, same header format) and its
  `NOT_STARTED` status; `ls scripts/verify_ticket_overlaps.py` confirms
  that script does not yet exist either, consistent with that status.
- `sed -n '/## Hard laws/,/## Falsifiers/p' tickets/GL-ERRC-013.md`: Hard
  law 4 states verbatim, "the field's construction must be re-run at
  execution time (not just a fixed count of what existed at drafting
  time), since new tickets will keep being drafted" -- the intent this
  ticket's script enforces mechanically.
- `head -20 scripts/verify_docs.py`: confirms the existing
  `scripts/verify_*.py` convention is stdlib-only (`argparse`, `hashlib`,
  `json`, `re`, `tomllib`, `pathlib`), no third-party dependency.
- `grep -n "^## " tickets/OVERLAPS.md`: confirms an existing `##
  \`AGENTS.md\`` section (line 130) already reconciles `GL-ERRC-013` and
  `GL-PLAN-002` as the two tickets that write to `AGENTS.md`; this
  ticket's script only reads `AGENTS.md`, so it does not add a write
  claim to that section, and a check of every `tickets/GL-*.md`
  Authored-boundary block for the literal string
  `verify_agents_ticket_sync` returned zero matches -- no existing ticket
  claims this ticket's new script path.
- `git rev-parse HEAD`: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.

## Evidence

Executed for real this session. `git rev-parse HEAD` reconfirmed
`bce7f6386c4203784beaae426e40804636c4151a` at the start, matching this
ticket's declared Base -- no drift before any edit.

### Falsifiers re-run for real against the actual checkout

1. Real repo run: `python3 scripts/verify_agents_ticket_sync.py` -> exit
   `0`, no output. Field and disk are now both at 75 entries; this
   diverges from this ticket's own literal Falsifier-1 wording ("names
   all 52 real missing-from-field tickets") because `AGENTS.md`'s
   `drafted tickets` field was already extended from 19 to 75 entries by
   other, already-landed work in this session's working tree
   (`GL-EXP-050`, `EXECUTED`) before this ticket's own execution began --
   not a script defect and not a false pass: the field and the 75 real
   `tickets/GL-*.md` files on disk are genuinely in sync today. Explained
   here plainly, not silently passed over or falsely reported as failing.
2. Synthetic missing-from-field fixture (field names only `GL-X-001`;
   `tickets/GL-X-001.md` and `tickets/GL-Y-002.md` both present) ->
   exactly `missing-from-field: GL-Y-002`, exit `1` -- PASS.
3. Synthetic stale-in-field fixture (field names `GL-Z-003`; no
   `tickets/GL-Z-003.md` on disk) -> exactly `stale-in-field: GL-Z-003`,
   exit `1` -- PASS.
4. Synthetic fixture missing the `- drafted tickets (see tickets/):`
   header line -> `parse error: could not find a line matching ...`,
   exit `2`, no uncaught exception/traceback -- PASS.
5. `git status --porcelain` scoped to `scripts/verify_agents_ticket_sync.py`
   and `tickets/GL-EXP-052.md` -> only those two paths, both `??` (new) --
   PASS (Hard Law 7; `git diff --stat` alone does not surface new/untracked
   files, so `git status` is the correct scope instrument here).
6. `python3 -m py_compile` + AST import scan on the new script -> compiles
   cleanly; imports limited to `argparse`/`re`/`pathlib`/`sys`/`__future__`
   (stdlib only, Hard Law 6) -- PASS.

All 6 falsifiers resolved to their real, non-fabricated outcome. Falsifier
1's literal numeric expectation ("52 missing") does not hold on the live
repo today -- reported honestly above, not reinterpreted, per the
`GL-EXP-050` precedent this ticket's own Outcome section already names for
this exact class of drift. The three synthetic fixtures (2, 3, 4) are the
falsifiers independent of repo drift and are the primary correctness
check; all three passed exactly as this ticket's Falsifiers section
specifies.

### Full `just ci-all` (both workspaces)

`just ci-all` (`ci` + `v26-ci`) ran for real and exited `0`. Full log:
`/private/tmp/claude-501/-Users-sac-ggen-legacy/87a9b589-243d-4eb5-b50c-e957cd0f71db/scratchpad/ci-all.log`.

Main workspace (`ci`):
- `cargo fmt --all -- --check` -- PASS (no diff)
- `cargo check --all-targets --locked` -- PASS
- `cargo clippy --all-targets --locked -- -D warnings` -- PASS (zero warnings)
- `cargo test --all-targets --locked -- --test-threads=1` -- PASS, 18
  tests total (`ggen_legacy_lsp` lib 1 ok; `ggen_lsp` main 0 tests;
  `analysis.rs` 7 ok; `analysis_boundary.rs` 4 ok; `contract.rs` 3 ok;
  `exit_code.rs` 1 ok; `lsp_boundary.rs` 2 ok)

`tools/v26.8.1` workspace (`v26-ci`):
- `cargo fmt --manifest-path Cargo.toml -- --check` -- PASS
- `cargo check --manifest-path Cargo.toml` -- PASS
- `cargo clippy --manifest-path Cargo.toml --all-targets -- -D warnings`
  -- PASS (zero warnings)
- `cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets
  --locked -- --test-threads=1` -- PASS, 18 tests total
  (`v26_8_1_tools` lib 3 ok; `ggen_v26_8_1_verifier` main
  (`document_evidence_sabotage_tests`) 13 ok; `project_coverage` 0 tests;
  `subsystem_verifier` 0 tests; `verifier_boundary.rs` 2 ok)

`CI_ALL_EXIT_CODE:0`. All 8 steps (fmt/check/clippy/test x2 workspaces)
passed, zero warnings, zero test failures.

`scripts/verify_agents_ticket_sync.py` was additionally re-run directly
against the current repo state as part of this same pass: exit `0`, no
stdout output (empty output means zero drift found). It was the
most-recently-created untracked script in the working tree at the time
(mtime 07:17 today), ahead of the other untracked scripts present
(`appliance/bin/_shared.py` 06:35 today; `tools/v26.8.20/observe_contract.py`
and `tools/v26.8.1/dsse_wrap.py` both Aug 20).

### Diff-stat scope (Hard Law 7)

`git status --porcelain` (whole repo) shows 28 pre-existing modified
tracked files (`AGENTS.md`, `Cargo.lock`/`.toml`,
`appliance/bin/build-document-evidence-index.py` and siblings,
`justfile`, `scripts/verify_docs.py`, `tickets/GL-AUTO-001.md`,
`tickets/GL-LSP-001.md`, `tools/*`, etc.), all already dirty in the
working tree before this ticket's own work began (confirmed: only
read-only commands were run this session -- `sed`/`grep`/`ls`/`cat`/
`git show`/`git ls-tree`/`python3`-execution -- against `AGENTS.md` and
`tickets/*.md`; no `Write`/`Edit` call touched any of them). None of
those 28 pre-existing modified files were touched by this ticket's own
edits, which are limited to exactly `scripts/verify_agents_ticket_sync.py`
(new) and `tickets/GL-EXP-052.md` (this file) -- the two paths this
ticket's Authored boundary permits, and nothing else.

## Standing

`PARTIAL_ALIVE` -- executed 2026-08-21, matching this ticket's own
declared Standing ceiling (see header). All 6 Falsifiers re-run for real
against the actual checkout (`## Evidence` above); none exposed a script
defect. `git status --porcelain` confirms exactly the two files this
ticket's Authored boundary permits (`scripts/verify_agents_ticket_sync.py`,
`tickets/GL-EXP-052.md`) are new/untracked, and no other file was touched
by this ticket's own edits -- Hard Law 7 satisfied. `just ci-all` ran
clean end to end (18 + 18 = 36 tests, 0 failed, 0 warnings, fmt/check/
clippy clean in both workspaces).

Not full `ALIVE`, for three honest reasons: (1) this is an uncommitted
working-tree change with no merge authority per this ticket's own
Publication boundary -- no commit was made; (2) Falsifier 1's literal
numeric expectation ("52 named missing-from-field tickets") does not hold
on the live repo today, because `AGENTS.md`'s `drafted tickets` field was
already brought into sync (19 -> 75 entries) by other already-landed work
(`GL-EXP-050`, `EXECUTED`) earlier in this session's working tree, before
this ticket's own execution began -- the script's own correctness is
instead confirmed by the three synthetic fixtures (missing-from-field,
stale-in-field, missing-header parse error), all of which passed exactly
as this ticket's Falsifiers section specifies; (3) this new script was
not wired into `justfile` or `.github/workflows/` CI, matching this
ticket's own explicit "out of scope" note in `## Authored boundary`.
