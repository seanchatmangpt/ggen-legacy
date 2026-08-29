# GL-EXP-040 — Fix (not just document) `GL-EXP-035`'s live `BUILD_BROKEN` finding: correct `authority/v26.8.3/release-authority.json`'s two pinned SHA-256 digests

**Status:** `EXECUTED` — both digests corrected in the main checkout and
re-verified there 2026-08-21. See "## Standing" for real command output.
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`GL-EXP-035` (read in full this session) is a pure finding: its own Hard
Laws forbid it from changing either digest in
`authority/v26.8.3/release-authority.json`, editing
`product/v26.8.3/PRD.md` or `architecture/v26.8.3/ARD.md`, or wiring
`verifiers/verify_ggen_v26_8_3.py` into CI. It names three candidate
resolutions ((a) correct the digests, (b) revisit the documents instead,
(c) wire the verifier into CI) and explicitly declines to choose between
them, deferring the decision to "a repo-owner or dedicated follow-up
ticket."

This ticket is that follow-up, and picks resolution (a): the pinned
digests are wrong, not the documents. Re-verified live this session,
independently of both `GL-EXP-035`'s and this ticket's own prior claims:

```console
$ python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
    --expected-repository seanchatmangpt/ggen-legacy \
    --expected-role EXECUTABLE_ARCHITECTURE_CORPUS
{...,"findings":["DOCUMENT_DIGEST_MISMATCH:architecture/v26.8.3/ARD.md",
"DOCUMENT_DIGEST_MISMATCH:product/v26.8.3/PRD.md"],...,
"standing":"BUILD_BROKEN",...}
```

exit code `2`, reproducing byte-identically. Independently recomputed the
real digests this session, direct `hashlib.sha256` over
`pathlib.Path.read_bytes()`, no piping through the verifier's own code:

```console
product/v26.8.3/PRD.md      stored=7809715249d4f7ca... actual=c8057a192b2c789a... MISMATCH
architecture/v26.8.3/ARD.md stored=670fd6f5e759b675... actual=b5e2388104cd9e1e... MISMATCH
```

`git status --porcelain -- authority/v26.8.3/release-authority.json
product/v26.8.3/PRD.md architecture/v26.8.3/ARD.md` is empty this
session -- no uncommitted edit to any of the three files is masking or
causing the mismatch; the committed bytes are the ones being compared.
`git log --oneline -3` for each of the three files independently
confirms the identical single commit, `cf97fc5 docs(v26.8.3): rebase
bounded PRD/ARD authority onto current main`, as each file's only listed
recent touch -- the wrong digests were baked in at that commit, not
introduced by later drift.

Choosing resolution (a) over (b)/(c): `product/v26.8.3/PRD.md` and
`architecture/v26.8.3/ARD.md` are otherwise-unremarked, already-real
documents (both pass every other check the verifier runs -- required-
section presence, requirement traceability, actuation/interface
topology, forbidden-overclaim phrase scan; the *only* two findings in
the whole run are the two digest mismatches). Nothing in `GL-EXP-035`'s
evidence, or re-checked independently this session, suggests the
documents' own content is wrong or that the authority bundle's intent
has changed since `cf97fc5` -- the simplest, most targeted explanation is
that the digests were computed against a pre-rebase draft of the two
files and never recomputed against the post-rebase committed bytes
before being pinned. Resolution (c) (CI wiring) is a real, separate,
higher-blast-radius change (touches `.github/workflows/*.yml` or
`justfile`, a file no ticket in this corpus currently owns for that
purpose per `tickets/OVERLAPS.md`) that does not by itself make the
verifier's current run pass -- wiring a currently-`BUILD_BROKEN` check
into CI before fixing the underlying mismatch would only turn a silent
break into a blocking one, not a fix. This ticket is scoped to the
minimal, targeted correction: two string fields in one JSON file.

## Authored boundary

(Cross-ticket file overlaps are tracked in `tickets/OVERLAPS.md` -- this
ticket adds a disclosed entry there, in the same write, per the overlap
with `GL-EXP-035`'s evidence scope over the same three files.)

```text
tickets/GL-EXP-040.md
authority/v26.8.3/release-authority.json
```

This ticket is authorized, when executed, to modify exactly two fields
inside `authority/v26.8.3/release-authority.json`:
`documents[0].sha256` (the `product/v26.8.3/PRD.md` entry, currently
`kind: "PRD"`) and `documents[1].sha256` (the
`architecture/v26.8.3/ARD.md` entry, currently `kind: "ARD"`) -- replacing
each stored value with the real, current sha256 of the committed file at
`HEAD`. It does not touch any other field in that JSON file (`base_sha`,
`components`, `requirements`, `interfaces`, `claim_ceiling`,
`self_certification`, `standing_ceiling`, `launch_predicates`, or either
document's `required_sections` list). It does not edit
`product/v26.8.3/PRD.md` or `architecture/v26.8.3/ARD.md` themselves --
per this ticket's own Outcome reasoning, the documents are the correct
artifact and the pinned digests are what was wrong. It does not wire
`verifiers/verify_ggen_v26_8_3.py` into `justfile` or
`.github/workflows/` -- that remains resolution (c)'s own, separately
scoped follow-up, per `GL-EXP-035` Hard Law 2's precedent.

## Hard laws

1. This ticket changes only `documents[0].sha256` and
   `documents[1].sha256` inside `authority/v26.8.3/release-authority.json`
   -- no other key in that file, and no other file, is touched by the
   fix itself.
2. This ticket does not edit `product/v26.8.3/PRD.md` or
   `architecture/v26.8.3/ARD.md`. If a future session determines the
   documents themselves (not the digests) are what's wrong (`GL-EXP-035`
   resolution (b)), that is a distinct, separately-scoped follow-up that
   must explicitly supersede this ticket's resolution-(a) choice, not
   silently coexist with it.
3. This ticket does not wire `verifiers/verify_ggen_v26_8_3.py` into
   `justfile` or `.github/workflows/` (`GL-EXP-035` resolution (c)
   remains its own follow-up).
4. The replacement digests must be computed directly from the real,
   current committed bytes of each file (e.g. `git show HEAD:<path> |
   sha256sum`, or equivalent direct read+hash) at execution time --
   never copied forward from this drafting session's cited values without
   re-computation, since the working tree may have moved by execution
   time.
5. After the fix is applied, re-running
   `python3 verifiers/verify_ggen_v26_8_3.py --subject-root . --expected-repository seanchatmangpt/ggen-legacy --expected-role EXECUTABLE_ARCHITECTURE_CORPUS`
   must report `"standing":"ALIVE"` with `"findings":[]` before this
   ticket's Standing can move past `NOT_STARTED` -- a partial fix (one
   digest corrected, not both) does not satisfy Acceptance.
6. This ticket does not silently re-pin the digests to whatever content
   happens to be on disk at some *later*, further-drifted commit -- the
   fix is scoped to reconciling the two files as they stood at this
   ticket's declared `Base` commit, the same commit `GL-EXP-035` audited.
   If `HEAD` has moved by execution time, the executing session must
   re-run the mismatch check first (Falsifier 1 below) and re-derive
   fresh digests from whatever `HEAD` actually is then, not from this
   drafting session's cached hex values.

## Falsifiers

- Re-running `python3 verifiers/verify_ggen_v26_8_3.py --subject-root .
  --expected-repository seanchatmangpt/ggen-legacy --expected-role
  EXECUTABLE_ARCHITECTURE_CORPUS` at execution time already reports
  `"standing":"ALIVE"` with no `DOCUMENT_DIGEST_MISMATCH` findings
  (would mean an intervening change already fixed this; re-verify before
  assuming this ticket's fix is still needed).
- After applying the fix, the same command still reports any
  `DOCUMENT_DIGEST_MISMATCH` finding (would mean the fix was applied
  incorrectly -- wrong field, stale hash, or a `HEAD` mismatch between
  when the hash was computed and when it was written).
- `git diff --stat` after execution shows any file changed other than
  `tickets/GL-EXP-040.md`, `tickets/OVERLAPS.md`, and
  `authority/v26.8.3/release-authority.json`.
- `git diff authority/v26.8.3/release-authority.json` after execution
  shows any changed line outside the two `sha256` value fields (would
  mean Hard Law 1 was violated).

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the live BUILD_BROKEN finding before touching anything:
python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
  --expected-repository seanchatmangpt/ggen-legacy \
  --expected-role EXECUTABLE_ARCHITECTURE_CORPUS
  # expect: "standing":"BUILD_BROKEN", two DOCUMENT_DIGEST_MISMATCH findings

# Compute the real, current digests directly from the committed HEAD blobs:
python3 -c "
import subprocess, hashlib
for path in ['product/v26.8.3/PRD.md', 'architecture/v26.8.3/ARD.md']:
    blob = subprocess.run(['git', 'show', f'HEAD:{path}'], capture_output=True).stdout
    print(path, hashlib.sha256(blob).hexdigest())
"

# Write exactly those two values into documents[0].sha256 (PRD) and
# documents[1].sha256 (ARD) in authority/v26.8.3/release-authority.json,
# and no other field.

# Reconfirm the fix:
python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
  --expected-repository seanchatmangpt/ggen-legacy \
  --expected-role EXECUTABLE_ARCHITECTURE_CORPUS
  # expect: "standing":"ALIVE", "findings":[]

# Confirm the blast radius:
git diff --stat
  # expect: only tickets/GL-EXP-040.md, tickets/OVERLAPS.md,
  # authority/v26.8.3/release-authority.json
git diff authority/v26.8.3/release-authority.json
  # expect: exactly two changed lines, both "sha256" value fields
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- Direct `Read` of `tickets/GL-EXP-035.md` in full this session:
  confirms its Hard Laws forbid it from touching
  `authority/v26.8.3/release-authority.json`,
  `product/v26.8.3/PRD.md`, or `architecture/v26.8.3/ARD.md`, confirms
  its Standing section reads `UNKNOWN -- not started... No digest
  correction, document edit, or CI/justfile wiring has been made.`, and
  confirms it names three candidate resolutions without choosing one.
- Real command re-run this session (independent of `GL-EXP-035`'s cited
  output): `python3 verifiers/verify_ggen_v26_8_3.py --subject-root .
  --expected-repository seanchatmangpt/ggen-legacy --expected-role
  EXECUTABLE_ARCHITECTURE_CORPUS` -- exit code `2`, real JSON output
  `"findings":["DOCUMENT_DIGEST_MISMATCH:architecture/v26.8.3/ARD.md",
  "DOCUMENT_DIGEST_MISMATCH:product/v26.8.3/PRD.md"]`,
  `"standing":"BUILD_BROKEN"` -- reproduces byte-identically.
- Real, independent digest recomputation this session (direct
  `hashlib.sha256` over `pathlib.Path.read_bytes()`, no dependency on
  the verifier's own code path): `product/v26.8.3/PRD.md` stored
  `7809715249d4f7ca...` vs. actual `c8057a192b2c789a...` (MISMATCH);
  `architecture/v26.8.3/ARD.md` stored `670fd6f5e759b675...` vs. actual
  `b5e2388104cd9e1e...` (MISMATCH).
- `git status --porcelain -- authority/v26.8.3/release-authority.json
  product/v26.8.3/PRD.md architecture/v26.8.3/ARD.md` this session:
  empty -- confirms no uncommitted edit is the cause.
- `git log --oneline -3` for each of the three files independently this
  session: all three report the identical single commit, `cf97fc5
  docs(v26.8.3): rebase bounded PRD/ARD authority onto current main`, as
  their most recent touch -- confirming the wrong digests were baked in
  at commit time, not introduced by later drift.
- Direct `Read` (`python3 -m json.tool`) of
  `authority/v26.8.3/release-authority.json`'s `documents` array this
  session: confirms the exact field structure --
  `documents[0] = {"kind":"PRD","path":"product/v26.8.3/PRD.md",
  "required_sections":[...8 items...],"sha256":"7809715249d4f7ca..."}`,
  `documents[1] = {"kind":"ARD","path":"architecture/v26.8.3/ARD.md",
  "required_sections":[...8 items...],"sha256":"670fd6f5e759b675..."}`
  -- confirming this ticket's Authored-boundary claim of exactly two
  scalar fields to change.
- `grep -l "architecture/v26.8.3/ARD.md\|product/v26.8.3/PRD.md\|authority/v26.8.3/release-authority.json"
  tickets/GL-*.md` this session (59 tickets total, `ls tickets/GL-*.md |
  wc -l`): hits only `tickets/GL-AUTO-001.md` (one bare filename inside
  its 115-file `REFUSED:FORBIDDEN_DIFF:` dump, confirmed by direct
  inspection to be a non-substantive path list, not a claim over the
  file) and `tickets/GL-EXP-035.md` itself -- no other ticket in the
  corpus claims or fixes these three files.
- `grep -rln "release-authority.json" --include="*.rs" --include="*.py"
  --include="*.yml" .` this session (excluding stale worktree copies
  under `.claude/worktrees/`): only `verifiers/verify_ggen_v26_8_3.py`
  itself reads this file -- no other script, test, or CI workflow
  depends on its current (wrong) digest values, so correcting them has
  no other blast radius to reconcile.
- `grep -rn "verify_ggen_v26_8_3\|verifiers/" .github/workflows/*.yml
  justfile tools/v26.8.1/justfile` this session: zero matches --
  confirms `GL-EXP-035`'s "invisible, nothing runs this" finding still
  holds, and confirms resolution (c) (CI wiring) is untouched by this
  ticket.
- `grep -n "verify_ggen_v26_8_3\|release-authority\|GL-EXP-035\|GL-EXP-040"
  tickets/OVERLAPS.md` this session, before this ticket's own write:
  zero matches -- no existing registry entry; this ticket adds one in
  the same write (see `tickets/OVERLAPS.md`).
- `docs/v26.9.1/RELEASE-NOTES.md` this session: confirms the corpus's own
  "self-generated recommendation to stop exploring and start executing"
  (`## Exploration pass -- 5 more GL-EXP tickets (029-032, one
  recovered)` section) and confirms the immediately following pass (`##
  Exploration pass -- 4 more GL-EXP tickets (033-036)`) grew the corpus
  from the 55 tickets recorded at that recommendation to 59, rather than
  executing/reducing it -- named here as the reason this ticket is
  scoped as a real, executable fix rather than another finding-only
  ticket.
- `git status --porcelain -uall | wc -l` this session: `88` -- matches
  the trend (`66 -> 78 -> 82 -> 86 -> 88`) `GL-EXP-016` and
  `docs/v26.9.1/RELEASE-NOTES.md` both already track as this corpus's
  most severe, still-open risk; not this ticket's Authored boundary and
  not resolved by this ticket, but the context motivating why this
  ticket picks a concrete fix over a fourth candidate-resolution list.

## Standing

`ALIVE`, executed and verified in the main checkout 2026-08-21:

```
$ python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
    --expected-repository seanchatmangpt/ggen-legacy \
    --expected-role EXECUTABLE_ARCHITECTURE_CORPUS
{...,"findings":[],"standing":"ALIVE",...}
exit 0
```

Both digests corrected to real, freshly-computed `sha256` of the committed
`HEAD` bytes (`c8057a19...` for `PRD.md`, `b5e23881...` for `ARD.md`),
computed via `git show HEAD:<path> | sha256sum`-equivalent, not copied
from this ticket's drafting-time citation. `git diff --stat
authority/v26.8.3/release-authority.json` shows exactly `1 file changed,
1 insertion(+), 1 deletion(-)` (the file is single-line JSON; both
`sha256` value substitutions land as one line-level diff) — confirmed via
direct string-level inspection that only the two `sha256` field values
changed, no other key. All 6 Hard Laws and both Falsifiers hold: `git
diff --stat` (repo-wide) touches `authority/v26.8.3/release-authority.json`
plus this ticket file plus `tickets/OVERLAPS.md`'s new disclosure entry —
no other file. `GL-EXP-035`'s own live finding is now resolved, not just
documented.
