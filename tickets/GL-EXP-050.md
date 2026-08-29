# GL-EXP-050 — Re-run `AGENTS.md`'s `drafted tickets (see tickets/):` field: 52 of 71 tickets (73%) are currently silently omitted

**Status:** `EXECUTED` — re-run performed for real this session against the real
`AGENTS.md`; see "Execution evidence" below.
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`GL-ERRC-013` (read in full this session, `Status: EXECUTED`) added
`AGENTS.md`'s `drafted tickets (see tickets/):` field specifically so that
"a session following `CLAUDE.md`'s own instructed workflow ('check it
before starting executable work')" would learn the full ticket set
without independently listing `tickets/`. Its own Hard Law 4 named the
exact failure mode this ticket now fixes, in its own words: "the field's
construction must be re-run at execution time (not just a fixed count of
what existed at drafting time), since new tickets will keep being
drafted... the acceptance check below verifies the field's ticket count
matches a live `ls tickets/GL-*.md` count at execution time, not a number
hardcoded in this ticket." That re-run has not happened since the field
was first populated (it enumerates exactly 19 tickets, `AGENTS.md:11-29`).

Re-verified fresh this session, independent of `GL-ERRC-013`'s own cited
counts:

```console
$ ls tickets/GL-*.md | wc -l
71
$ for f in tickets/GL-*.md; do
    slug=$(basename "$f" .md)
    grep -q "$slug" AGENTS.md || echo "MISSING: $slug"
  done | wc -l
52
$ grep -oE "GL-[A-Z]+-[0-9]+" AGENTS.md | sort -u
GL-ARCH-003 GL-AUTO-001 GL-CONTRACT-004 GL-ERRC-008 GL-ERRC-009
GL-ERRC-010 GL-ERRC-011 GL-ERRC-012 GL-ERRC-013 GL-ERRC-014 GL-ERRC-015
GL-ERRC-017 GL-ERRC-018 GL-ERRC-019 GL-LSP-001 GL-MANUFACTURE-005
GL-PLAN-002 GL-RECEIPT-007 GL-VERIFY-006
```

Exactly 19 tickets are present; 52 are absent, including all four of
`GL-ERRC-016`/`GL-ERRC-020`/`GL-ERRC-022`/`GL-ERRC-023` and all 48 of
`GL-EXP-001` through `GL-EXP-048` (verified present on disk via `ls
tickets/GL-ERRC-016.md tickets/GL-ERRC-020.md tickets/GL-ERRC-022.md
tickets/GL-ERRC-023.md tickets/GL-EXP-0*.md` -- all exist). 73% omission
is worse than the drift `GL-ERRC-013` was admitted to fix: at drafting
time, `GL-ERRC-013`'s own Evidence section found "8 of these 10 [tickets]
are absent" from the pre-fix header (80% present, 20% missing); the
field it built to solve that now has the coverage inverted (27% present,
73% missing), because the field is a snapshot that nothing re-runs, and
the ticket corpus has more than sextupled (10 to 71 files) since.

A second, independent staleness axis, found and re-verified this session
(not part of `GL-ERRC-013`'s original scope, but the same field): of the
19 tickets the field *does* list, at least one entry's status text is
itself now stale. `AGENTS.md:12` reads `` `GL-AUTO-001`: (no Status: line
in ticket file) ``, but `tickets/GL-AUTO-001.md:3` (read directly this
session) now reads `` **Status:** `BLOCKED` — corrected 2026-08-21 by
`GL-ERRC-023`. ``, i.e. the ticket gained a `Status:` line since the field
was populated and the field was never updated to reflect it. This ticket's
fix (re-deriving every listed ticket's status text fresh at execution
time, per `GL-ERRC-013`'s own Hard Law 2: "copied verbatim from each
ticket file's own `**Status:**` line... at execution time") corrects both
axes in the same pass -- it is not two separate fixes.

This ticket does not invent a new mechanism. `GL-ERRC-013` already built
the field, named the re-run discipline in its own Hard Law 4, and its own
Acceptance script already includes the exact `for f in tickets/GL-*.md; do
... done` loop this ticket's evidence reuses to detect the drift. This
ticket is that named, not-yet-executed re-run, now covering 71 tickets
instead of the 10 (soon to be 11, with `GL-ERRC-013` itself) present when
the field was first built.

No other ticket in the corpus targets this specific field. `tickets/GL-EXP-014.md`
(read in full this session) targets `GL-ERRC-009.md`'s and
`GL-ERRC-013.md`'s own terminal `## Standing` *sections* (a self-contradiction
between each file's `**Status:**` line and its own `## Standing` text) --
a different section of a different pair of files, not `AGENTS.md`'s
enumeration field. `tickets/GL-EXP-030.md` (read in full this session)
targets `README.md`'s and `governance/claims-register.md`'s duplicated
`foundry_runtime_candidate` claim -- unrelated file, unrelated claim.
`grep -rln "verify_agents\|AGENTS.md.*admission gate" tickets/GL-*.md`
and `grep -rn "verify.*AGENTS" scripts/*.py justfile` (both re-run this
session) return zero matches -- no ticket proposes a mechanical verifier
for this field's completeness, and no script in the repo checks it
automatically today (this ticket does not add one either; it is scoped
to re-running the field's content by hand, per `GL-ERRC-013`'s own
established, hand-run acceptance-script pattern, not to building new
tooling -- a mechanical `scripts/verify_agents_ticket_field.py` would be
its own, separately scoped follow-up).

## Authored boundary

(Cross-ticket file overlaps are tracked in `tickets/OVERLAPS.md` -- this
ticket adds a disclosed row to the existing `## \`AGENTS.md\`` section
there, in the same write, alongside `GL-PLAN-002` and `GL-ERRC-013`
already recorded.)

```text
AGENTS.md                # `drafted tickets (see tickets/):` field only (lines 10-29 at drafting time) -- re-run to enumerate all 71 current tickets.md files, correcting both missing entries and stale status text for already-listed entries
tickets/GL-EXP-050.md
tickets/OVERLAPS.md      # new disclosed row in the existing `AGENTS.md` section
```

`AGENTS.md`'s `active executable ticket: GL-LSP-001` /
`concurrent executable ticket: GL-PLAN-002` lines (`GL-PLAN-002`'s own
Authored-boundary scope, per `OVERLAPS.md`'s existing `AGENTS.md` section)
are not touched. No other section of `AGENTS.md` (`Mission`, the pipeline
diagram, everything below the header) is touched. No `tickets/GL-*.md`
file other than `GL-EXP-050.md` itself is edited by this ticket -- the
per-ticket status text copied into the field is read-only, verbatim from
each file's own existing `**Status:**` line, never written back.

## Hard laws

1. `active executable ticket: GL-LSP-001` and
   `concurrent executable ticket: GL-PLAN-002` are unchanged -- this
   ticket only re-runs the enumeration field `GL-ERRC-013` already built,
   it does not reassign scope.
2. Every `tickets/GL-*.md` file present at execution time appears in the
   field -- re-derive the list live (`ls tickets/GL-*.md`), do not copy
   forward this ticket's drafting-time count of 71 (or its 52-missing
   finding) as a fixed number, since more tickets may be drafted between
   now and execution (the exact discipline `GL-ERRC-013`'s own Hard Law 4
   already states, restated here because this ticket is the first
   execution of it).
3. Each listed ticket's status text is copied verbatim from that ticket
   file's own first `**Status:**` line at execution time, or `(no
   Status: line in ticket file)` if it has none -- this ticket does not
   independently assess or upgrade any ticket's standing, and does not
   edit any `tickets/GL-*.md` file's own content (only reads it).
4. `git diff --stat` after execution shows only `AGENTS.md`,
   `tickets/GL-EXP-050.md`, and `tickets/OVERLAPS.md` changed.

## Falsifiers

- After execution, `for f in tickets/GL-*.md; do slug=$(basename "$f"
  .md); grep -q "$slug" AGENTS.md || echo "MISSING: $slug"; done`
  produces any output (would mean a ticket is still silently omitted).
- After execution, any listed ticket's status text in `AGENTS.md` does
  not match that ticket file's own current first `**Status:**` line (or
  `(no Status: line in ticket file)` for `GL-LSP-001`, its one ticket
  with no such line, re-confirmed this session).
- `AGENTS.md`'s `active executable ticket`/`concurrent executable ticket`
  values differ from `GL-LSP-001`/`GL-PLAN-002` after this ticket.
- `git diff --stat` shows any file changed other than the three named in
  Hard Law 4.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the drift before fixing:
ls tickets/GL-*.md | wc -l                        # expect 71 or more (re-derive, don't assume 71)
for f in tickets/GL-*.md; do
  slug=$(basename "$f" .md)
  grep -q "$slug" AGENTS.md || echo "MISSING: $slug"
done | wc -l                                       # expect 52 or a number consistent with new tickets since drafting

# Re-derive the field's full content fresh (slug + own Status: line, or the
# no-Status fallback), matching GL-ERRC-013's original construction:
for f in tickets/GL-*.md; do
  slug=$(basename "$f" .md)
  status=$(grep -m1 "^\*\*Status:\*\*" "$f" | sed 's/^\*\*Status:\*\* //')
  if [ -z "$status" ]; then status="(no Status: line in ticket file)"; fi
  echo "  - \`$slug\`: $status"
done | sort > /tmp/new-agents-field.txt

# Replace AGENTS.md's existing field body (lines between
# "drafted tickets (see tickets/):" and the next top-level "- " header
# field, i.e. "protocol runtime:") with the regenerated content above.

# After the edit, confirm completeness and correctness:
for f in tickets/GL-*.md; do
  slug=$(basename "$f" .md)
  grep -q "$slug" AGENTS.md || echo "STILL MISSING: $slug"
done
# expect: no output

grep -A2 "GL-AUTO-001" AGENTS.md | head -1
# expect: BLOCKED (matching tickets/GL-AUTO-001.md's own current Status
# line), not "(no Status: line in ticket file)"

grep '^- active executable ticket: `GL-LSP-001`$' AGENTS.md
grep '^- concurrent executable ticket: `GL-PLAN-002`$' AGENTS.md
# expect: both still present, unchanged

git diff --stat   # expect only AGENTS.md, tickets/GL-EXP-050.md, tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `ls tickets/GL-*.md | wc -l` this session: `71`.
- `for f in tickets/GL-*.md; do slug=$(basename "$f" .md); grep -q
  "$slug" AGENTS.md || echo "MISSING: $slug"; done | wc -l` this session:
  `52`.
- `grep -oE "GL-[A-Z]+-[0-9]+" AGENTS.md | sort -u` this session: exactly
  19 slugs, matching `AGENTS.md:11-29`'s field verbatim (`GL-ARCH-003`,
  `GL-AUTO-001`, `GL-CONTRACT-004`, `GL-ERRC-008` through `GL-ERRC-015`
  and `GL-ERRC-017` through `GL-ERRC-019`, `GL-LSP-001`,
  `GL-MANUFACTURE-005`, `GL-PLAN-002`, `GL-RECEIPT-007`, `GL-VERIFY-006`).
- `ls tickets/GL-ERRC-016.md tickets/GL-ERRC-020.md
  tickets/GL-ERRC-022.md tickets/GL-ERRC-023.md` this session: all four
  exist on disk; none appears in the `grep -oE` output above.
- `ls tickets/GL-EXP-*.md | wc -l` this session: `48` -- none of
  `GL-EXP-001` through `GL-EXP-048` appears in the `grep -oE` output
  above.
- Direct `Read` of `tickets/GL-ERRC-013.md` in full this session: confirms
  `**Status:** EXECUTED`, confirms its Outcome text about the field's
  purpose, and confirms its Hard Law 4's exact wording about re-running
  the field's construction at execution time (quoted verbatim in this
  ticket's Outcome section above).
- Direct `Read` of `tickets/GL-AUTO-001.md` line 3 this session: `**Status:**
  \`BLOCKED\` — corrected 2026-08-21 by \`GL-ERRC-023\`.` -- confirms
  `AGENTS.md:12`'s `` `GL-AUTO-001`: (no Status: line in ticket file) ``
  entry is now stale on a second axis (a ticket already listed, whose
  status text has since diverged from its own file), independent of the
  52-missing-tickets finding.
- Direct `Read` of `tickets/GL-EXP-014.md` in full this session: confirms
  its scope is `GL-ERRC-009.md`'s and `GL-ERRC-013.md`'s own terminal
  `## Standing` sections, not `AGENTS.md`'s enumeration field -- no
  overlap with this ticket's scope.
- Direct `Read` of `tickets/GL-EXP-030.md` in full this session: confirms
  its scope is `README.md`'s/`governance/claims-register.md`'s
  `foundry_runtime_candidate` claim -- unrelated to this ticket.
- `grep -rln "verify_agents\|AGENTS.md.*admission gate" tickets/GL-*.md`
  this session: zero matches, exit 1.
- `grep -rn "verify.*AGENTS" scripts/*.py justfile` this session: zero
  matches, exit 1.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- Direct `Read` of `tickets/OVERLAPS.md`'s existing `## \`AGENTS.md\``
  section this session: confirms `GL-PLAN-002` (the `active`/`concurrent`
  stanza) and `GL-ERRC-013` (the `drafted tickets` field) are already
  recorded there, and confirms no existing row covers a *re-run* of the
  field -- this ticket adds one, disclosing that it edits the same
  `drafted tickets` field `GL-ERRC-013` created (no line-range conflict:
  this ticket only replaces that field's body content, which
  `GL-ERRC-013`'s own row already scopes to).

## Execution evidence (this session)

Re-verified live before editing (base `bce7f6386c4203784beaae426e40804636c4151a`,
confirmed matching `git rev-parse HEAD` at execution start):

```console
$ ls tickets/GL-*.md | wc -l
75
$ for f in tickets/GL-*.md; do
    slug=$(basename "$f" .md)
    grep -q "$slug" AGENTS.md || echo "MISSING: $slug"
  done | wc -l
56
```

The corpus had grown from 71 to 75 tickets since this ticket was drafted
(56 missing at execution time vs. 52 at drafting time), confirming the
drift was still live, not stale, and confirming Hard Law 2's instruction
not to copy forward the drafting-time count.

`AGENTS.md`'s `drafted tickets (see tickets/):` field body (previously
`AGENTS.md:11-29`, 19 entries) was replaced with the output of the exact
command specified in this ticket's own Acceptance section, run for real:

```console
$ for f in tickets/GL-*.md; do
    slug=$(basename "$f" .md)
    status=$(grep -m1 '^\*\*Status:\*\*' "$f" | sed 's/^\*\*Status:\*\* //')
    [ -z "$status" ] && status="(no Status: line in ticket file)"
    echo "  - \`$slug\`: $status"
  done | sort
```

producing 75 lines (`AGENTS.md:11-85` after the edit), one per ticket
file present on disk at execution time.

Post-edit falsifier re-runs, for real:

```console
$ for f in tickets/GL-*.md; do
    slug=$(basename "$f" .md)
    grep -q "$slug" AGENTS.md || echo "STILL MISSING: $slug"
  done
(no output)

$ grep -A2 "GL-AUTO-001" AGENTS.md | head -1
  - `GL-AUTO-001`: `BLOCKED` — corrected 2026-08-21 by `GL-ERRC-023`. A fresh run of the

$ grep '^- active executable ticket: `GL-LSP-001`$' AGENTS.md
- active executable ticket: `GL-LSP-001`
$ grep '^- concurrent executable ticket: `GL-PLAN-002`$' AGENTS.md
- concurrent executable ticket: `GL-PLAN-002`
```

`GL-AUTO-001`'s stale `(no Status: line in ticket file)` entry (the second
staleness axis this ticket's Outcome section named) is corrected to its
real current `` `BLOCKED` `` status. `GL-LSP-001` retains the no-Status
fallback, confirmed correct: `grep -m1 '^\*\*Status:\*\*'
tickets/GL-LSP-001.md` matches nothing (exit 1).

Also updated: `tickets/OVERLAPS.md`'s existing `## \`AGENTS.md\`` section's
`GL-EXP-050` row, status annotation changed from `(NOT_STARTED)` to
`(EXECUTED)` with a real completion note (same file, same section
`GL-ERRC-013` and `GL-PLAN-002` are already recorded in; no new section
added, no other row touched).

`git diff --stat` after execution: only `AGENTS.md` appears (76 lines
changed) among tracked files. `tickets/GL-EXP-050.md` and
`tickets/OVERLAPS.md` are both untracked in this checkout (`git status`
shows `??` for both, unrelated to this ticket's execution — they were
already untracked before this session touched them) so neither appears in
plain `git diff --stat` output regardless of content; their edits are
real and present on disk, confirmed via direct `Read`/diff-against-working-copy,
not via `git diff --stat` (which by construction only reports tracked-file
changes). The working tree also carries pre-existing modifications to
~24 unrelated tracked files (e.g. `Cargo.lock`, `.github/workflows/ci.yml`,
`justfile`) and ~90 unrelated untracked files, present before this
session began and not touched by this execution -- confirmed by this
session's edits touching only `AGENTS.md`, `tickets/GL-EXP-050.md`, and
`tickets/OVERLAPS.md`.

## Standing

`PARTIAL_ALIVE` -- matching this ticket's own declared standing ceiling.
Executed and re-verified this session: `AGENTS.md`'s `drafted tickets`
field now enumerates all 75 `tickets/GL-*.md` files present on disk at
execution time (0 missing, re-confirmed by the falsifier loop above), and
the previously-stale `GL-AUTO-001` entry now matches that ticket's own
current `**Status:**` line. `GL-PLAN-002`'s `active`/`concurrent` stanza
is unchanged. Reported as `PARTIAL_ALIVE`, not `ALIVE`, because the field
is a hand-run snapshot, not a mechanically-enforced invariant: nothing in
the repo re-runs this regeneration automatically (confirmed at drafting
time by this ticket's own Outcome section: zero matches for
`scripts/verify_agents_ticket_field.py`-style tooling), so the same drift
this ticket fixed can recur the next time a ticket is drafted or a
ticket's own `**Status:**` line changes, exactly as it did between
`GL-ERRC-013`'s execution and this ticket's.

## CI verification (post-execution, full repo gate)

`just ci-all` was run for real in this checkout (background, warm target
dirs, finished in seconds). Full raw log saved at
`/private/tmp/claude-501/-Users-sac-ggen-legacy/87a9b589-243d-4eb5-b50c-e957cd0f71db/scratchpad/ci-all.log`.
Real overall exit code: `0` (all steps green, both workspaces).

- Root workspace (`ci: fmt check clippy test`): `cargo fmt --all --
  --check` PASS (no diff); `cargo check --all-targets --locked` PASS
  (`Finished dev profile` in 0.19s); `cargo clippy --all-targets --locked
  -- -D warnings` PASS (0 warnings); `cargo test --all-targets --locked
  -- --test-threads=1` PASS — 18/18 tests ok across 6 binaries
  (`ggen_legacy_lsp` lib: 1 ok; `ggen_lsp` main: 0 tests;
  `tests/analysis.rs`: 7 ok; `tests/analysis_boundary.rs`: 4 ok;
  `tests/contract.rs`: 3 ok; `tests/exit_code.rs`: 1 ok;
  `tests/lsp_boundary.rs`: 2 ok). 0 failed.
- `tools/v26.8.1` workspace (`v26-ci: v26-fmt v26-check v26-clippy
  v26-test`, its own justfile): `fmt --check` PASS; `check` PASS
  (`Finished dev profile` in 0.03s); `clippy -- -D warnings` PASS (0
  warnings); `test --all-targets --locked -- --test-threads=1` PASS —
  18/18 tests ok across 5 binaries (`v26_8_1_tools` lib: 3 ok incl.
  `exact_head_tests`; `ggen_v26_8_1_verifier` main: 13 ok incl.
  `document_evidence_sabotage_tests`; `project_coverage`: 0 tests;
  `subsystem_verifier`: 0 tests; `tests/verifier_boundary.rs`: 2 ok). 0
  failed.
- Total: **36 tests passed, 0 failed** across both workspaces.

One transient operational note, not a code failure: an earlier attempt to
launch `ci-all` with a redundant trailing `&` inside a background-run call
detached the subprocess from the harness's tracking and it was killed
mid-`clippy` when the wrapper shell exited (log stopped after 5 lines, no
`cargo`/`just` process left running per `ps aux`). Re-ran it correctly (no
nested `&`) and it completed for real with the full green log summarized
above.

`appliance/bin/` is modified in the working tree on this branch (10 files
vs. `main`, plus a new `appliance/bin/_shared.py`), so per this repo's own
instructions `bash appliance/bin/run-reference-e2e.sh` was additionally
run for real: exit code `0`, final stdout line
`GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`. Full log saved at
`/private/tmp/claude-501/-Users-sac-ggen-legacy/87a9b589-243d-4eb5-b50c-e957cd0f71db/scratchpad/e2e.log`
— it includes several intermediate suite reports with standing
`PARTIAL_ALIVE`/`passed:false` entries by design (the script's own
hidden-challenge/negative-control checks, e.g. "identities must be
distinct": `passed=false` at one deliberate step), but the script's own
overall exit code was `0` and its final marker line confirms `ALIVE`.

No new standalone `verify_*`-style script (e.g. a hypothetical
`verify_agents_ticket_sync.py`) exists in this branch's diff or working
tree: checked via `git status --porcelain -uall` for new `.py` files —
only `appliance/bin/_shared.py` (a shared helper module, no
`__main__`/CLI, not independently runnable), `tools/v26.8.1/dsse_wrap.py`,
and `tools/v26.8.20/observe_contract.py` are new, none matches the
described verify-script pattern, so none was run separately.
`tools/dsrust-disposition-proposer` (tied to this branch's own name) is
**not** part of `ci-all` by design — confirmed via the justfile's own
comment ("Not part of ci/ci-all/v26-ci and not invoked from any workflow
-- a human runs this by hand ... Requires GROQ_API_KEY") — it has its own
separate `just propose-disposition` recipe, untouched by this run.

`git status --porcelain -uall | wc -l` = **117**, unchanged before and
after this verification pass (27 modified-vs-HEAD/untracked entries plus
many untracked planning/ticket files already present at session start —
e.g. `tickets/GL-EXP-001..052`, `docs/v26.9.1/*`, `planning/v26.9.1/*`,
`.claude/settings.json`, `CLAUDE.md`). This CI run made no working-tree
changes of its own.
