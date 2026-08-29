# GL-EXP-038 — Correct `justfile:35` and `CLAUDE.md:92`'s "both workspaces" undercount: `ci-all` covers 2 of this repo's 4 independent Cargo projects, not 2 of 2

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`find . -maxdepth 3 -name Cargo.toml -not -path "./.git/*" -not -path
"./.claude/*"` (run this session) lists exactly 4 real Cargo manifests:
`./Cargo.toml` (root), `./tools/v26.8.1/Cargo.toml`,
`./tools/dsrust-disposition-proposer/Cargo.toml`, and
`./tools/ggen-verifier-cli-verify/Cargo.toml`. Each is independently
buildable (`cargo build --manifest-path <path>`); none is a member of
another. Direct `Read` of each this session shows the root manifest is a
bare `[package]` (`ggen-legacy-lsp`, no `[workspace]` table — `grep -c
"\[workspace\]" Cargo.toml` returns `0`, already independently confirmed
by `GL-EXP-032`'s own `cargo metadata --no-deps --format-version 1`
finding of exactly one workspace member, `["ggen-legacy-lsp"]`), while the
three `tools/*` manifests each open with an explicit empty `[workspace]`
table followed by their own `[package]` — i.e. 4 real, independent Cargo
projects total, 3 with an explicit `[workspace]` root and 1 (root) with an
implicit one (Cargo's own default for any package outside another
workspace). This ticket says "4 independent Cargo projects," not "4
workspace tables," to stay accurate about the root manifest's real shape.

`justfile` (read in full this session) defines `ci: fmt check clippy
test` (line 18, bare `cargo fmt/check/clippy/test` from the repo root —
targets only the root `ggen-legacy-lsp` package) and `v26-ci: v26-fmt
v26-check v26-clippy v26-test` (line 33, delegates to
`tools/v26.8.1/justfile`). `ci-all: ci v26-ci` (line 37) is the union of
exactly these two — 2 of the 4 real Cargo projects. `grep -n
"ggen-verifier-cli-verify\|dsrust-disposition-proposer" justfile` (run
this session) shows `dsrust-disposition-proposer` appears only in the
separate, explicitly-opt-out `propose-disposition` recipe (lines 46-52,
whose own header comment states verbatim: "Not part of
`ci`/`ci-all`/`v26-ci` and not invoked from any workflow"), and
`ggen-verifier-cli-verify` does not appear in `justfile` at all — zero
matches, confirming it has no recipe, wired or unwired.

Despite this, `justfile:35`'s header comment for `ci-all` reads "Run the
full ladder for both workspaces" and `CLAUDE.md:92`'s Verify-section line
reads `just ci-all # cargo fmt/check/clippy/test, both workspaces` (both
confirmed byte-for-byte this session via `sed -n` / `grep -n "both
workspaces" justfile CLAUDE.md`, which returns exactly these two lines,
one per file). Both assert the same "both" (i.e. exactly 2) framing for a
repo whose real, independently-buildable Cargo-project count is 4 — an
undercount of 2, duplicated across two files rather than a single typo.

**This is not a case where the repo's authors were unaware of the third
and fourth projects.** `justfile`'s own `propose-disposition` header
comment, 11 lines below the "both workspaces" comment it never updates
in light of, already names `tools/dsrust-disposition-proposer` as a real
crate explicitly outside `ci`/`ci-all`/`v26-ci`. The file documents the
gap it doesn't count.

`grep -l "CLAUDE.md" tickets/GL-*.md` (run this session) finds 6 tickets
that cite `CLAUDE.md` (`GL-CONTRACT-004`, `GL-ARCH-003`, `GL-ERRC-013`,
`GL-MANUFACTURE-005`, `GL-RECEIPT-007`, `GL-VERIFY-006`); direct `grep -n
"CLAUDE.md"` on each this session shows every citation refers to a named
prose section elsewhere in the file (a "Gall's Law checkpoint", the
"Ticket-gated admission" section) as supporting evidence for that
ticket's own standing claim — none stakes an `## Authored boundary` edit
claim on `CLAUDE.md` itself, let alone its Verify section or line 92
specifically. `CLAUDE.md` has no existing section in `tickets/OVERLAPS.md`
(`grep -n "^## " tickets/OVERLAPS.md`, run this session, lists 14
section headers, none naming `CLAUDE.md`) — this file is genuinely
unclaimed by the current 59-ticket corpus.

**Two existing tickets touch `justfile` near this exact text without
fixing it.** `GL-EXP-006` (`NOT_STARTED`, read in full this session)
fixes a different, adjacent citation — `justfile:4`'s stale
`.github/workflows/gl-lsp-001-runtime.yml` reference inside the *root* `ci`
ladder's header comment (lines 3-5) — and its own Hard Law 3 states "No
other prose in either file changes. This ticket is a citation correction,
not an editorial pass," so it will not touch `justfile:35` or
`CLAUDE.md:92`. `GL-EXP-032` (`NOT_STARTED`, read in full this session)
plans to extend `ci-all`'s dependency list to `ci v26-ci dsrust-ci`
(Hard Law 5) — narrowing the undercount from 2-of-4 to 3-of-4, still
short of `ggen-verifier-cli-verify` (its own Hard Law 2 explicitly leaves
that fourth project out of CI) — while its `## Authored boundary` lists
only new recipes and `ci-all`'s dependency list, never `justfile:35-36`'s
header comment or `CLAUDE.md:92`. If `GL-EXP-032` lands first, "both
workspaces" would describe 3-of-4 instead of 2-of-4 — still wrong, just
less wrong — and this ticket's Hard Laws below are written to be
re-verified against whichever of `ci: fmt check clippy test`/`v26-ci`/
`dsrust-ci` `ci-all` actually depends on at execution time, not to
hardcode today's `ci v26-ci` as permanent.

`governance/production-gaps.md:31` (checked this session via `grep -n
"both workspaces" governance/production-gaps.md`) carries the identical
phrase in retrospective, past-tense prose ("added a root `justfile`
... mirroring [file]'s ladder exactly for both workspaces"). `GL-EXP-006`
already claims edit ownership of that exact sentence (for the filename
half) and its Hard Law 3 explicitly declines to touch anything else in
it, including this phrase. This ticket does not touch
`governance/production-gaps.md` either — it is retrospective narrative
describing a past PR, not a standing instruction like `justfile:35` or
`CLAUDE.md:92`'s Verify section, and fixing it would require reopening
scope `GL-EXP-006` already closed. Left as a named, undropped gap, not
silently expanded into.

## Authored boundary

(Cross-ticket file overlaps checked against every ticket's own `##
Authored boundary` and against `tickets/OVERLAPS.md` this session before
writing this section. `tickets/OVERLAPS.md`'s existing `## \`justfile\``
section lists 7 tickets, none claiming lines 35-36 — `GL-EXP-006` claims
lines 3-5 only; `GL-EXP-032` claims new recipes plus `ci-all`'s
*dependency list* on line 37, not its header comment on lines 35-36. No
line-range conflict. `CLAUDE.md` has no existing `tickets/OVERLAPS.md`
section; this ticket adds the first one. Both disclosures added by this
same write.)

```text
justfile              # header comment only, lines 35-36 (ci-all's comment)
CLAUDE.md              # Verify-section line only, line 92
tickets/GL-EXP-038.md
tickets/OVERLAPS.md   # add a row to the existing `justfile` section; add a new `## CLAUDE.md` section
```

No change to `justfile:3-5` (`GL-EXP-006`'s scope), any recipe body
including `ci-all`'s own dependency list (`GL-EXP-032`'s scope, line 37),
`propose-disposition`'s recipe or header comment (lines 46-52), or any
other `justfile` line. No change to `governance/production-gaps.md` (see
Outcome above for why). No change to any other `CLAUDE.md` section.

## Hard laws

1. `justfile:35`'s "Run the full ladder for both workspaces" is replaced
   with wording that names the real scope of `ci-all`'s *current*
   dependency list at execution time (today: `ci v26-ci`, i.e. the root
   `ggen-legacy-lsp` package and the `tools/v26.8.1` workspace) rather
   than a bare count word like "both"/"three"/"four" that silently goes
   stale the next time `ci-all`'s dependencies change. Re-run `grep -n
   "^ci-all" justfile` immediately before editing to confirm the current
   dependency list matches what the new comment names.
2. `CLAUDE.md:92`'s `# cargo fmt/check/clippy/test, both workspaces` is
   corrected the same way, naming the same real scope as Hard Law 1's
   `justfile` edit rather than asserting a bare count independently (the
   two files must not drift back out of sync with each other the way
   they were found).
3. Line 36 of `justfile` ("engineer can run to reproduce what CI gates
   before opening a PR") is left unmodified — its accuracy (whether
   `ci-all` actually reproduces what `.github/workflows/ci.yml` gates) is
   `GL-EXP-032`'s scope, not this ticket's.
4. No change to `justfile:3-5`, any recipe body (`ci`, `v26-ci`,
   `ci-all`'s dependency list, `propose-disposition`, or any recipe a
   currently-`NOT_STARTED` ticket, e.g. `GL-EXP-004`/`008`/`012`/`032`/
   `036`, might add), or `governance/production-gaps.md`.
5. If this ticket executes after `GL-EXP-032` has already landed and
   changed `ci-all`'s dependency list, re-derive the replacement text from
   the real, current dependency list rather than reusing this ticket's
   drafted-against-Base wording verbatim.

## Falsifiers

- `grep -n "both workspaces" justfile CLAUDE.md` still matches after this
  ticket executes.
- The replacement text in either file names a Cargo project `ci-all` does
  not actually depend on at execution time (re-verify against `grep -n
  "^ci-all" justfile` immediately before editing, per Hard Law 5).
- `git diff --stat` after this ticket touches any file outside `justfile`,
  `CLAUDE.md`, and `tickets/GL-EXP-038.md` (plus `tickets/OVERLAPS.md` for
  the disclosure).
- `just --list` fails to parse `justfile` after the edit.
- `tickets/OVERLAPS.md`'s existing `justfile` section rows, or any of its
  other existing sections, are altered rather than only appended to.

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these
are the exact commands to run once the fix lands, not yet-observed
outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the undercount before touching anything:
grep -n "both workspaces" justfile CLAUDE.md
find . -maxdepth 3 -name Cargo.toml -not -path "./.git/*" -not -path "./.claude/*" | sort
grep -n "^ci-all" justfile

# After the fix, confirm the phrase is gone from both files:
grep -n "both workspaces" justfile CLAUDE.md && echo "UNEXPECTED: still present"

# Confirm justfile still parses and recipe bodies are unchanged:
just --list
grep -n "^ci-all\|^ci:\|^v26-ci:" justfile

git diff --stat   # must show only justfile, CLAUDE.md, tickets/GL-EXP-038.md,
                   # tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `find . -maxdepth 3 -name Cargo.toml -not -path "./.git/*" -not -path
  "./.claude/*"` — real output this session: exactly 4 manifests (root,
  `tools/v26.8.1`, `tools/dsrust-disposition-proposer`,
  `tools/ggen-verifier-cli-verify`).
- `grep -c "\[workspace\]" Cargo.toml` (root) — real output this session:
  `0` (bare `[package]`, no explicit workspace table).
- Direct `Read`/`sed -n` of the first ~15 lines of all 4 `Cargo.toml`
  files this session — root is `[package]` only; each `tools/*` manifest
  opens with an explicit empty `[workspace]` table followed by `[package]`.
- Direct `Read` of `justfile` in full this session — `ci: fmt check
  clippy test` (line 18), `v26-ci: v26-fmt v26-check v26-clippy v26-test`
  (line 33), `ci-all: ci v26-ci` (line 37), `propose-disposition`'s header
  comment (lines 46-52, stating verbatim "Not part of
  `ci`/`ci-all`/`v26-ci` and not invoked from any workflow").
- `grep -n "ggen-verifier-cli-verify\|dsrust-disposition-proposer"
  justfile` — real output this session: `dsrust-disposition-proposer`
  appears only in the `propose-disposition` recipe block;
  `ggen-verifier-cli-verify` has zero matches anywhere in the file.
- `sed -n '35,37p' justfile` and `sed -n '92p' CLAUDE.md` — real output
  this session, byte-for-byte matching the quoted "both workspaces" text
  in Outcome above.
- `grep -n "both workspaces" justfile CLAUDE.md` — real output this
  session: exactly `justfile:35` and `CLAUDE.md:92`, one hit per file.
- `grep -n "both workspaces" governance/production-gaps.md` — real output
  this session: one additional hit at line 31, in past-tense retrospective
  prose already claimed (for its filename half) by `GL-EXP-006`.
- Direct `Read` of `tickets/GL-EXP-006.md` in full this session — confirms
  its real scope is `justfile:4` (a different header comment) and
  `governance/production-gaps.md:31`, and its Hard Law 3 explicitly
  declines to touch any other prose in either file.
- Direct `Read` of `tickets/GL-EXP-032.md` in full this session — confirms
  its `cargo metadata --no-deps --format-version 1` finding of exactly one
  workspace member (`["ggen-legacy-lsp"]`) at the repo root, its Hard Law 5
  plan to extend `ci-all` to `ci v26-ci dsrust-ci`, and that its own `##
  Authored boundary` never names `justfile:35-36` or `CLAUDE.md:92`.
- `grep -l "CLAUDE.md" tickets/GL-*.md` — real output this session: 6
  tickets (`GL-CONTRACT-004`, `GL-ARCH-003`, `GL-ERRC-013`,
  `GL-MANUFACTURE-005`, `GL-RECEIPT-007`, `GL-VERIFY-006`); per-file
  `grep -n "CLAUDE.md"` on each this session confirms every citation
  refers to a named prose section as supporting evidence, none an
  Authored-boundary edit claim on `CLAUDE.md` itself.
- `grep -n "^## " tickets/OVERLAPS.md` — real output this session: 14
  section headers, none naming `CLAUDE.md`.
- `sed -n '134,173p' tickets/OVERLAPS.md` — real output this session,
  confirms the current `justfile` section's 7 listed tickets and that
  none claims lines 35-36.
- `ls tickets/GL-*.md | wc -l` — real output this session: `59`.
- `ls tickets/GL-EXP-038.md` before this write — real output this
  session: file did not exist (`No such file or directory`).
- `git rev-parse HEAD` — `bce7f6386c4203784beaae426e40804636c4151a`, the
  real base commit this ticket is drafted against.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
undercount (confirmed live, this session, by directly reading both cited
lines and all 4 real `Cargo.toml` files) and the two `tickets/OVERLAPS.md`
disclosures its own Authored boundary requires. No edit to `justfile` or
`CLAUDE.md` has been made.
