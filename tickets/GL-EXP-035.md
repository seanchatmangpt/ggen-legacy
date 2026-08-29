# GL-EXP-035 — Raise `authority/v26.8.3/release-authority.json`'s silent, currently-real `BUILD_BROKEN` self-check out of an unrun, unrecorded state

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`verifiers/verify_ggen_v26_8_3.py` (113 lines, read in full this session)
is a real, independent verifier for this repo's own v26.8.3 PRD/ARD
authority bundle (`authority/v26.8.3/release-authority.json` +
`product/v26.8.3/PRD.md` + `architecture/v26.8.3/ARD.md`). It validates the
authority JSON against an embedded JSON Schema, checks every requirement
traces into the documents, checks document sha256 digests match the
authority file's pinned values, checks actuation/interface topology, and
scans for forbidden-overclaim phrases. Ran fresh this session, for real,
against the current, unmodified working tree:

```console
$ python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
    --expected-repository seanchatmangpt/ggen-legacy \
    --expected-role EXECUTABLE_ARCHITECTURE_CORPUS
{"...,"findings":["DOCUMENT_DIGEST_MISMATCH:architecture/v26.8.3/ARD.md",
"DOCUMENT_DIGEST_MISMATCH:product/v26.8.3/PRD.md"],...,
"standing":"BUILD_BROKEN",...}
```

Two real findings, `standing: "BUILD_BROKEN"`. Independently confirmed the
root cause this session by computing the real digests directly:

```console
$ python3 -c "..."
product/v26.8.3/PRD.md stored=7809715249d4f7ca actual=c8057a192b2c789a MISMATCH
architecture/v26.8.3/ARD.md stored=670fd6f5e759b675 actual=b5e2388104cd9e1e MISMATCH
```

**This is not later drift -- the pinned digests were wrong from the
moment they were committed.** `git status --porcelain -- authority/v26.8.3/
release-authority.json product/v26.8.3/PRD.md architecture/v26.8.3/ARD.md`
is empty (no uncommitted edits to any of the three files). All three
files' most recent commit is the identical single commit, `cf97fc5
docs(v26.8.3): rebase bounded PRD/ARD authority onto current main`
(confirmed via `git log --oneline -3 -- <each path>`). Re-computed the
digests against the exact committed git blobs (`git show
HEAD:<path>`, not the working-tree copy) this session -- the mismatch
reproduces identically against the committed blob content, confirming the
sha256 values baked into `release-authority.json` never matched the real
bytes of `PRD.md`/`ARD.md` as committed in that same `cf97fc5` commit.

**This real, currently-computable `BUILD_BROKEN` result is invisible --
nothing runs this verifier and nothing records its output for the
ggen-legacy side.** `grep -rn "verify_ggen_v26_8_3\|verifiers/"
.github/workflows/*.yml justfile tools/v26.8.1/justfile` (run this
session) returns zero matches. `grep -il "verify_ggen_v26_8_3\|verifiers/"
tickets/GL-*.md` (all 55 tickets, run this session) returns only
`tickets/GL-AUTO-001.md`, whose one hit is a bare filename inside its
115-file `REFUSED:FORBIDDEN_DIFF:` dump, not a substantive claim. By
contrast, the **peer** (`seanchatmangpt/ggen`) side of this same dual
verification *does* have a real, committed receipt --
`evidence/v26.8.3/peer-prd-ard-receipt.json` (read in full this session)
records a real `verifiers/verify_ggen_v26_8_3.py` run against the `~/ggen`
peer repo, `standing: "ALIVE"`, `findings: []`, a full 10-case mutation
suite all `killed: true`. The ggen-legacy repository's own,
self-referential half of this same verification scheme -- running this
exact script against its own `subject-root .` -- has no equivalent
committed receipt anywhere in the repo, and when actually run this session
does not pass.

`docs/src/SUMMARY.md`'s book chapters and `README.md`/
`governance/claims-register.md` were checked this session for any claim
resting on this authority bundle's consistency:
`grep -rn "release-authority.json\|verify_ggen_v26_8_3" README.md
governance/claims-register.md docs/v26.9.1/RELEASE-NOTES.md` returns zero
matches -- no top-level claim currently cites this specific file's
standing, so this finding is not (yet) contradicting an explicit `ALIVE`
claim elsewhere in the repo. But `authority/v26.8.3/release-authority.json`
itself declares `"standing_ceiling":"ALIVE"` and
`"launch_predicates":[...,"document_digests_match",...]` as one of its own
ten required launch predicates -- an implicit claim, baked into the file's
own schema-validated structure, that this session's real run directly
contradicts.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- checked this session, `grep -n "verify_ggen_v26_8_3\|release-authority"
tickets/OVERLAPS.md` returns zero matches, no existing entry.)

```text
tickets/GL-EXP-035.md
```

This ticket is a pure finding -- it does not modify
`authority/v26.8.3/release-authority.json`, `product/v26.8.3/PRD.md`,
`architecture/v26.8.3/ARD.md`, or `verifiers/verify_ggen_v26_8_3.py`. It
does not silently re-pin the two digests to whatever passes today (that
would launder an unverified claim into a new hardcoded truth with the same
staleness failure mode this repo's own `GL-ERRC-011`/`GL-ERRC-014`
precedent already rejects for stale hash constants) and it does not wire
the verifier into CI on its own authority. Whether the fix is (a)
recomputing and correcting the two digests to match the real, current
documents, (b) treating this repo's own PRD/ARD as having diverged from
what the authority bundle was meant to certify and revisiting the
documents instead, or (c) wiring `verifiers/verify_ggen_v26_8_3.py` into
`justfile`/CI as a real, visible admission gate so this class of drift is
caught immediately rather than staying silent indefinitely, is a decision
this ticket names but does not make -- a repo-owner or dedicated follow-up
ticket's call, per this repo's own established "flag, don't silently fix"
discipline (`GL-ERRC-011`, `GL-ERRC-014`, `GL-ERRC-019` precedent).

## Hard laws

1. This ticket does not change either digest value in
   `authority/v26.8.3/release-authority.json`, and does not edit
   `product/v26.8.3/PRD.md` or `architecture/v26.8.3/ARD.md`.
2. This ticket does not wire `verifiers/verify_ggen_v26_8_3.py` into
   `justfile` or `.github/workflows/`. If a future session chooses
   resolution (c) above, that wiring is its own, separately-scoped
   follow-up (mirroring this repo's own established
   `GL-ERRC-022`/`GL-EXP-004`/`GL-EXP-008`/`GL-EXP-012` pattern for
   "real tool, zero wiring" candidates) -- not bundled into this
   finding.
3. Re-running this ticket's own cited command at execution time must
   reproduce the same two `DOCUMENT_DIGEST_MISMATCH` findings (or, if the
   documents have since been edited for an unrelated reason, whatever the
   real, current mismatch state is) -- this ticket's evidence is not
   copied forward from drafting time without re-verification.
4. This ticket does not claim `evidence/v26.8.3/peer-prd-ard-receipt.json`
   (the peer/`~/ggen`-side receipt) is itself wrong or stale -- that file
   is independently real and unaffected; this finding is scoped to the
   ggen-legacy repository's own, self-referential half of the same
   verification scheme.

## Falsifiers

- Re-running `python3 verifiers/verify_ggen_v26_8_3.py --subject-root .
  --expected-repository seanchatmangpt/ggen-legacy --expected-role
  EXECUTABLE_ARCHITECTURE_CORPUS` at execution time reports
  `"standing":"ALIVE"` with no `DOCUMENT_DIGEST_MISMATCH` findings (would
  mean the drift was already fixed by an intervening change; re-verify and
  correct this ticket's evidence rather than assuming the finding still
  holds).
- A real, independent re-computation of `product/v26.8.3/PRD.md`'s or
  `architecture/v26.8.3/ARD.md`'s sha256 (via `git show HEAD:<path> |
  sha256sum`, or equivalent) matches the value pinned in
  `authority/v26.8.3/release-authority.json` (would falsify this ticket's
  core claim).
- `grep -rn "verify_ggen_v26_8_3\|verifiers/" .github/workflows/*.yml
  justfile` finds a real invocation at execution time (would mean the
  verifier is already wired in, contradicting this ticket's "invisible"
  claim).
- `git diff --stat` after this ticket touches any file outside
  `tickets/GL-EXP-035.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the live BUILD_BROKEN finding before touching anything:
python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
  --expected-repository seanchatmangpt/ggen-legacy \
  --expected-role EXECUTABLE_ARCHITECTURE_CORPUS
  # expect: "standing":"BUILD_BROKEN", two DOCUMENT_DIGEST_MISMATCH findings

# Independently reconfirm the root cause:
python3 -c "
import json, hashlib, pathlib
d = json.load(open('authority/v26.8.3/release-authority.json'))
for doc in d['documents']:
    p = pathlib.Path(doc['path'])
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    print(doc['path'], 'MATCH' if actual == doc['sha256'] else 'MISMATCH')
"
  # expect: MISMATCH for both product/v26.8.3/PRD.md and architecture/v26.8.3/ARD.md

# Confirm nothing runs this check today:
grep -rn "verify_ggen_v26_8_3\|verifiers/" .github/workflows/*.yml justfile
  # expect: no output

git diff --stat   # must show only tickets/GL-EXP-035.md
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- Direct `Read` of `verifiers/verify_ggen_v26_8_3.py` in full (113 lines)
  this session: confirms `findings()`'s per-document `digest(p)!=
  d.get('sha256')` check, the embedded JSON Schema, the
  `REQUIRED_INVARIANTS`/`REQUIRED_LAUNCH` sets, and `main()`'s real
  `argparse` interface (`--subject-root`, `--expected-repository`,
  `--expected-role`, `--self-test`).
- Real command run this session, output redirected to a file and the
  shell `$?` captured directly (not read from a piped `head`, which can
  mask the real exit code): `python3 verifiers/verify_ggen_v26_8_3.py
  --subject-root . --expected-repository seanchatmangpt/ggen-legacy
  --expected-role EXECUTABLE_ARCHITECTURE_CORPUS` -- real exit code `2`,
  matching the script's own documented convention (`main()`: `return 0 if
  report['standing']=='ALIVE' else 2`). Real JSON output:
  `"findings":["DOCUMENT_DIGEST_MISMATCH:architecture/v26.8.3/ARD.md",
  "DOCUMENT_DIGEST_MISMATCH:product/v26.8.3/PRD.md"]`,
  `"standing":"BUILD_BROKEN"`.
- Real, independent digest recomputation this session (`python3 -c`
  script, direct `hashlib.sha256` over `pathlib.Path.read_bytes()`):
  `product/v26.8.3/PRD.md` stored `7809715249d4f7ca...` vs. actual
  `c8057a192b2c789a...` (MISMATCH); `architecture/v26.8.3/ARD.md` stored
  `670fd6f5e759b675...` vs. actual `b5e2388104cd9e1e...` (MISMATCH).
- `git status --porcelain -- authority/v26.8.3/release-authority.json
  product/v26.8.3/PRD.md architecture/v26.8.3/ARD.md` this session: empty
  -- confirms no uncommitted edit is the cause.
- `git log --oneline -3 -- authority/v26.8.3/release-authority.json`,
  `... -- product/v26.8.3/PRD.md`, `... -- architecture/v26.8.3/ARD.md`
  this session: all three report the identical single commit, `cf97fc5
  docs(v26.8.3): rebase bounded PRD/ARD authority onto current main`, as
  their most recent (and, per each `git log`'s single-line output, only
  listed within the 3-commit window) touch.
- Real re-verification against the exact committed git blob (not the
  working-tree copy) this session, via `subprocess.run(['git','show',
  f'HEAD:{path}'])` piped into `hashlib.sha256`: reproduces the identical
  two mismatches, confirming the wrong digest was baked in at commit time,
  not introduced by later drift.
- `grep -rn "verify_ggen_v26_8_3\|verifiers/" .github/workflows/*.yml
  justfile tools/v26.8.1/justfile` this session: zero matches.
- `grep -il "verify_ggen_v26_8_3\|verifiers/" tickets/GL-*.md` this
  session (55 tickets): only `tickets/GL-AUTO-001.md`, confirmed by direct
  inspection to be one bare filename inside its `REFUSED:FORBIDDEN_DIFF:`
  path dump, not a substantive claim.
- Direct `Read` of `evidence/v26.8.3/peer-prd-ard-receipt.json` in full
  this session: confirms a real, committed receipt for the peer
  (`seanchatmangpt/ggen`) side of this same verification scheme --
  `"standing":"ALIVE"`, `"findings":[]`, a 10-case mutation suite with
  `"killed":10,"total":10` -- and `"subject_repository":"seanchatmangpt/
  ggen"`, confirming it is not evidence for the ggen-legacy self-check
  this ticket names as missing.
- `grep -rn "release-authority.json\|verify_ggen_v26_8_3" README.md
  governance/claims-register.md docs/v26.9.1/RELEASE-NOTES.md` this
  session: zero matches -- no top-level claim currently cites this file's
  standing.
- `grep -n "verify_ggen_v26_8_3\|release-authority" tickets/OVERLAPS.md`
  this session: zero matches, no existing registry entry.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
currently-real, currently-silent `BUILD_BROKEN` finding for this
repository's own v26.8.3 authority self-check (a real command run this
session, not inferred), and names three candidate resolutions without
choosing between them. No digest correction, document edit, or CI/justfile
wiring has been made.
