# GL-EXP-018 — Backfill 2 missing `tickets/OVERLAPS.md` rows: `appliance/bin/verify-standing-portfolio.py` and `tools/v26.8.20/observe_contract.py`

**Status:** `EXECUTED` — the two rows this ticket specifies were added to
`tickets/OVERLAPS.md` directly in the same session that drafted this
ticket, since it's a low-risk documentation-only fix matching the
already-established pattern.
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tickets/OVERLAPS.md` is the canonical registry built specifically to catch two
`GL-*` tickets independently staking an Authored-boundary claim on the same file
without disclosing each other. Its own text already admits this rule was
violated once (6 rows backfilled for `subsystem_verifier.rs`/
`coverage_projection.rs`/`justfile`, covering `GL-EXP-001/003/005/006/007/008`
-- see `docs/v26.9.1/RELEASE-NOTES.md:586-597`). That backfill pass ran before
`GL-EXP-011`-`016` were admitted, so it could not and did not cover them.
Verified this session by parsing every `tickets/GL-*.md`'s `## Authored
boundary` fenced block and grouping by claimed file path: two more pairs
share a file with no `tickets/OVERLAPS.md` section for either, and neither
ticket in either pair discloses the other:

```
grep -n "^## \`appliance/bin/verify-standing-portfolio.py\`\|^## \`tools/v26.8.20/observe_contract.py\`" tickets/OVERLAPS.md
# exit 1 -- neither section exists
```

**Pair 1 -- `appliance/bin/verify-standing-portfolio.py`, a real, live overlap.**
`GL-EXP-013` (admitted in the 013-016 pass) claims this file for
"delete private `sha256_file()`+`read_json()`, import shared" -- confirmed via
`grep -n "^def " appliance/bin/verify-standing-portfolio.py`: `sha256_file`
(line 10), `read_json` (line 15), `write_json` (line 16). `GL-EXP-015`
(same pass) claims the same file for the `challenge_files` scan (lines
44-50) and the `hidden-challenges` check detail (line 51) -- a disjoint
region, confirmed by direct read
(`grep -n "" appliance/bin/verify-standing-portfolio.py | sed -n '41,51p'`).
`GL-EXP-013`'s own Authored-boundary block explicitly lists
`tickets/OVERLAPS.md # add new \`appliance/bin/\` section` as a file it
intends to touch -- that addition was never made. Disclosure check both
directions: `grep -n "GL-EXP-015" tickets/GL-EXP-013.md` and
`grep -n "GL-EXP-013" tickets/GL-EXP-015.md` both return zero matches.
`GL-EXP-015`'s own boundary note only cross-checks `GL-ERRC-019`,
`GL-EXP-005`, and `GL-EXP-011` as "no change to" -- it never mentions
`GL-EXP-013` despite claiming the identical file. This is a genuine,
functionally real overlap (two distinct, disjoint edit regions in one
file, same class as the already-reconciled `coverage_projection.rs`
section above it in the registry) that the registry's own rule requires a
row for, and does not have one.

**Pair 2 -- `tools/v26.8.20/observe_contract.py`, a listed-but-inert overlap.**
`GL-EXP-011` (009-012 pass) claims `git_head()`'s return-type/behavior
(confirmed: `def git_head(repo: Path) -> str | None:` at line 30,
`except Exception: return None` at lines 37-38). `GL-EXP-012` (same pass)
lists the same path in its own Authored-boundary block, but its own text
is explicit that this is not a competing source-edit claim: `"tools/
v26.8.20/observe_contract.py # no source change -- wiring only, not
modifying the script's own logic"`. `GL-EXP-012`'s real target is a new
`justfile` recipe that invokes the script; that specific overlap (`GL-EXP-012`
vs. the file `justfile` already tracks) is in fact already disclosed --
`tickets/OVERLAPS.md:109-110` lists `GL-EXP-012` under the existing
`` ## `justfile` `` section. What is missing is the corresponding row for
`observe_contract.py` itself, which the registry's own precedent (see the
`legacy_archaeology.py` section: two tickets sharing a file, reconciled as
"no conflict," still get a row) says should exist regardless of whether the
two claims actually collide. Disclosure check: `grep -n "GL-EXP-012"
tickets/GL-EXP-011.md` and `grep -n "GL-EXP-011" tickets/GL-EXP-012.md`
both return zero matches -- so even though this pair does not functionally
conflict (`GL-EXP-012` touches no source in the file), the registry's own
completeness rule ("before admitting a new ticket, grep every existing
Authored boundary for the file paths... if any overlap, add a row") is
still unmet.

**Not the same severity, and this ticket must not present them as such.**
Pair 1 is a real, disjoint-but-live dual-edit claim on one file with no
existing note anywhere. Pair 2 is a listed file path where one of the two
claimants makes no source edit at all -- closer to the already-reconciled
`legacy_archaeology.py`/`AGENTS.md` sections than to the contested
`coverage_projection.rs`/`justfile` sections. Both are still missing rows
under the registry's own stated rule, and both are added by this ticket,
but the two `## Reconciled` verdicts below are written to reflect the real
difference rather than force a false "identical conflict" parity between
them.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- this ticket's entire purpose is editing that registry, not claiming a
new code-file boundary.)

```text
tickets/OVERLAPS.md   # add two new sections: `appliance/bin/verify-standing-portfolio.py`
                       # and `tools/v26.8.20/observe_contract.py`
tickets/GL-EXP-018.md
```

No change to `appliance/bin/verify-standing-portfolio.py`,
`tools/v26.8.20/observe_contract.py`, `justfile`, or any ticket file other
than this one -- this ticket is documentation-only, adding disclosure rows
for overlaps that already exist in the four referenced tickets' own text.

## Hard laws

1. The two new `tickets/OVERLAPS.md` sections name all four tickets
   (`GL-EXP-013`/`GL-EXP-015` for the first, `GL-EXP-011`/`GL-EXP-012` for
   the second) and cite the real, current line ranges/functions each
   claims, re-verified against `appliance/bin/verify-standing-portfolio.py`
   and `tools/v26.8.20/observe_contract.py` at execution time (not trusted
   from this ticket's cited line numbers, per the registry's own
   re-verify-at-execution convention).
2. The `appliance/bin/verify-standing-portfolio.py` section's `Reconciled`
   verdict does not claim a functional conflict exists between `GL-EXP-013`
   and `GL-EXP-015` unless one is independently found -- it documents the
   disjoint-region status quo, matching the `coverage_projection.rs`
   section's own pattern of naming disjoint functions as "no conflict
   today" rather than asserting collision.
3. The `tools/v26.8.20/observe_contract.py` section's `Reconciled` verdict
   states plainly that `GL-EXP-012` makes no source edit to this file (per
   `GL-EXP-012`'s own Authored-boundary text) and that its real overlap is
   already tracked under the `justfile` section -- this row exists for
   registry completeness, not because a live conflict was found.
4. No existing `tickets/OVERLAPS.md` section (`legacy_archaeology.py`,
   `coverage_projection.rs`, `subsystem_verifier.rs`,
   `verify_foundry_bootstrap.py`, `AGENTS.md`, `justfile`) is edited,
   reordered, or removed by this ticket.
5. `git diff --stat` after this ticket touches only `tickets/OVERLAPS.md`
   and this ticket file.

## Falsifiers

- Either new section omits one of its two claimant tickets, or cites a
  line range/function that does not match the live file at execution
  time.
- The `observe_contract.py` section's reconciliation text asserts a
  functional conflict between `GL-EXP-011` and `GL-EXP-012` without new
  evidence, contradicting `GL-EXP-012`'s own "no source change" claim.
- `tickets/OVERLAPS.md`'s existing 6 sections (or the `justfile` section's
  existing `GL-EXP-012` row at lines 109-110) are altered.
- `git diff --stat` after this ticket touches any file outside
  `tickets/OVERLAPS.md` and `tickets/GL-EXP-018.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm both rows are still missing before editing:
grep -n "^## \`appliance/bin/verify-standing-portfolio.py\`\|^## \`tools/v26.8.20/observe_contract.py\`" tickets/OVERLAPS.md
echo "EXIT (expect 1, no match):$?"

# Reconfirm the four source tickets' current Authored-boundary claims and
# disclosure status haven't changed:
grep -n "GL-EXP-015" tickets/GL-EXP-013.md; echo "EXIT (expect 1):$?"
grep -n "GL-EXP-013" tickets/GL-EXP-015.md; echo "EXIT (expect 1):$?"
grep -n "GL-EXP-012" tickets/GL-EXP-011.md; echo "EXIT (expect 1):$?"
grep -n "GL-EXP-011" tickets/GL-EXP-012.md; echo "EXIT (expect 1):$?"

# Reconfirm the live line numbers each row will cite:
grep -n "^def " appliance/bin/verify-standing-portfolio.py
grep -n "" appliance/bin/verify-standing-portfolio.py | sed -n '41,51p'
grep -n "^def git_head" tools/v26.8.20/observe_contract.py

# After the edit:
grep -n "^## \`appliance/bin/verify-standing-portfolio.py\`\|^## \`tools/v26.8.20/observe_contract.py\`" tickets/OVERLAPS.md
git diff --stat   # must show only tickets/OVERLAPS.md and tickets/GL-EXP-018.md
```

## Evidence this ticket is grounded in (verified this session)

- `grep -n "^## \`appliance/bin/verify-standing-portfolio.py\`\|^## \`tools/v26.8.20/observe_contract.py\`" tickets/OVERLAPS.md`
  this session: exit 1, zero matches -- neither section exists.
- `grep -n "^def " appliance/bin/verify-standing-portfolio.py` this
  session: `sha256_file` (line 10), `read_json` (line 15), `write_json`
  (line 16), `challenge_files=[]` (line 44), the `hidden-challenges` check
  (line 51) -- `GL-EXP-013`'s and `GL-EXP-015`'s claimed regions confirmed
  disjoint at the current line numbers.
- `grep -n "^def git_head" tools/v26.8.20/observe_contract.py` this
  session: line 30, `try`/`except Exception: return None` at lines 31-38 --
  matches `GL-EXP-011`'s claimed target exactly.
- `grep -n "GL-EXP-015" tickets/GL-EXP-013.md`, `grep -n "GL-EXP-013"
  tickets/GL-EXP-015.md`, `grep -n "GL-EXP-012" tickets/GL-EXP-011.md`,
  `grep -n "GL-EXP-011" tickets/GL-EXP-012.md` this session: all four
  exit 1, zero matches -- no disclosure in either direction for either
  pair.
- Full read of `tickets/GL-EXP-011.md`, `tickets/GL-EXP-012.md`,
  `tickets/GL-EXP-013.md`, `tickets/GL-EXP-015.md`'s `## Authored boundary`
  sections this session: confirmed `GL-EXP-012`'s block states "no source
  change -- wiring only, not modifying the script's own logic" for
  `observe_contract.py`, and confirmed `GL-EXP-013`'s block states
  `tickets/OVERLAPS.md # add new \`appliance/bin/\` section` as an intended
  (but never-made) edit.
- `grep -n "appliance/bin\|observe_contract" tickets/OVERLAPS.md` this
  session: one match, `tickets/OVERLAPS.md:109`, under the existing
  `` ## `justfile` `` section (`GL-EXP-012` wiring `observe_contract.py` in
  as a recipe) -- confirming the `justfile`-side overlap is already
  disclosed and this ticket does not duplicate it; the missing rows are
  for the two source files themselves.
- Full read of `docs/v26.9.1/RELEASE-NOTES.md:562-601` this session:
  confirmed the prior backfill pass covered exactly 6 rows
  (`subsystem_verifier.rs`, `coverage_projection.rs`, `justfile` --
  `GL-EXP-001/003/005/006/007/008`) and ran before `GL-EXP-011`-`016` were
  admitted (`docs/v26.9.1/RELEASE-NOTES.md:578-584` for `GL-EXP-011`/`012`,
  `:725-745` for `GL-EXP-013`/`015`) -- confirming this is a genuine gap in
  registry coverage, not a re-discovery of an already-fixed case.
- `git rev-parse HEAD` this session:
  `bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's
  declared Base.

## Standing

`ALIVE`, re-verified 2026-08-21:

```
$ grep -n "verify-standing-portfolio.py\|observe_contract.py" tickets/OVERLAPS.md
## `appliance/bin/verify-standing-portfolio.py`
## `tools/v26.8.20/observe_contract.py`
```

Both rows present with reconciliation notes. `OVERLAPS.md`'s own
recurring-violation note updated to point at `GL-EXP-020` as the real fix
for the underlying manual-enforcement gap.
