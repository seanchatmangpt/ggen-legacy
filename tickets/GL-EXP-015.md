# GL-EXP-015 — Raise `verify-standing-portfolio.py`'s hidden-challenge scan out of an undifferentiated `except Exception: pass`

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`appliance/bin/verify-standing-portfolio.py:44-50` collapses every possible
failure to read or parse a hidden-challenge evidence file into the
identical, silent outcome: the file is dropped from `challenge_files` with
no distinguishable signal. Verified this session by direct read
(`grep -n "" appliance/bin/verify-standing-portfolio.py | sed -n
'41,51p'`), byte-for-byte:

```python
challenge_files=[]
for path in sorted((root/"evidence/raw/challenges").glob("*.json")) if (root/"evidence/raw/challenges").exists() else []:
    try:
        item=read_json(path)
        if item.get("visibility")=="customer-hidden": challenge_files.append(path.name)
    except Exception:
        pass
c("hidden-challenges",m.get("hidden_challenge_count",0)>0 and bool(challenge_files),{"declared":m.get("hidden_challenge_count",0),"observed":challenge_files})
```

`read_json` (`json.loads(Path(path).read_text())`, line 15) can raise for
at least 3 causally distinct reasons on a file already matched by the
`*.json` glob: `UnicodeDecodeError`/`OSError` reading a non-UTF8 or
permission-denied file, `json.JSONDecodeError` on malformed/truncated
JSON, and `AttributeError`/`TypeError` inside `item.get(...)` if the
parsed JSON is valid but not an object (e.g. a bare JSON array or
scalar). All 3 are caught by the bare `except Exception: pass` and
produce the identical outcome: the file is simply missing from
`challenge_files`, indistinguishable from "this file's `visibility` is
not `customer-hidden`" (the normal, non-error skip case one line above).

This feeds directly into the `hidden-challenges` compliance check at line
51, which cross-checks a *declared* count (`m.get("hidden_challenge_count",
0)`, sourced from the engagement config's `challenges` list at
`build-standing-portfolio.py:36,53` -- a separate mechanism) against the
*observed* file list this loop builds from scanning
`evidence/raw/challenges/*.json` on disk. A single corrupted, truncated,
or non-UTF8 hidden-challenge evidence file is silently dropped from the
observed side of that cross-check with no record of *why* -- it reads back
identically to "there was never a hidden-challenge file here," which can
flip `hidden-challenges` from pass to fail (if the corrupted file was the
only customer-hidden one) with zero diagnostic trail in the emitted
report's `{"declared":...,"observed":[...]}` detail.

**This is a live, exercised code path, not dead weight.** Verified this
session:

- `grep -rln "verify-standing-portfolio" appliance/bin/*.sh` (repo root,
  excluding `.claude/worktrees/`): matches `build-offline-bundle.sh` and
  `run-reference-e2e.sh`.
- `grep -n "verify-standing-portfolio" appliance/bin/build-offline-bundle.sh`:
  line 75, `python3 appliance/bin/verify-standing-portfolio.py --help
  >/dev/null` -- an existence/smoke check only, does not exercise the
  hidden-challenges scan.
- `grep -n "verify-standing-portfolio" appliance/bin/run-reference-e2e.sh`:
  3 real invocations (lines 15, 40, 55), each with a full
  `--portfolio/--public-key/--signature/--transparency-log/--report`
  argument set -- genuine end-to-end verification, not a smoke test.
- Direct read of `run-reference-e2e.sh:9`: the reference e2e script itself
  writes a real customer-hidden challenge file into the evidence tree
  before building the portfolio --
  `printf '{"id":"runtime-hidden","visibility":"customer-hidden",
  "nonce":"%s"}\n' "$(openssl rand -hex 32)" >
  "$TMP/evidence/challenges/runtime-hidden.json"` -- which
  `build-standing-portfolio.py` copies into the portfolio's
  `evidence/raw/challenges/` directory, confirming this exact loop
  (line 44-50) is genuinely exercised, with a real matching file, on
  every reference e2e run, not merely reachable in theory.
- `ls tests/fixtures/customer-evidence/` and `ls
  tests/fixtures/engagement.reference.json` this session: both exist on
  disk, confirming the e2e script's fixture inputs are real, not
  hypothetical.

**No existing ticket already scopes this except-swallow.** Verified this
session:

- `grep -l "verify-standing-portfolio" tickets/*.md`: only
  `tickets/GL-RECEIPT-007.md`. `grep -n "verify-standing-portfolio"
  tickets/GL-RECEIPT-007.md`: one match, line 83, an incidental mention
  ("signing step, verified by
  `appliance/bin/verify-standing-portfolio.py`/`cross-check-portfolio.py`")
  inside a correction about where an RSA-PSS signing step actually lives
  -- not an authored-boundary target, and it never discusses the
  hidden-challenges scan or this except-swallow.
- `grep -rln "hidden-challenges\|hidden_challenge_count\|challenge_files"
  tickets/*.md`: zero matches -- no ticket names this check or this
  specific collapse.
- `grep -n "verify-standing-portfolio\|verify_standing_portfolio"
  tickets/OVERLAPS.md`: zero matches (exit 1) -- no cross-ticket claim on
  this file.

**Same anti-pattern class as 3 prior tickets, a 4th independent
instance.** This is the identical undifferentiated-failure-collapse class
GL-ERRC-019 already fixed (`EXECUTED`) for
`tools/v26.8.1/src/coverage_projection.rs::exact_head()` (3 causes
collapsed into `"UNKNOWN"`), that GL-EXP-005 (`NOT_STARTED`) found
unfixed a second time in `tools/v26.8.1/src/bin/subsystem_verifier.rs
::fresh_git_head()`, and that GL-EXP-011 (`NOT_STARTED`) found a third
time in `tools/v26.8.20/observe_contract.py::git_head()` (3 causes
collapsed into Python `None`). All 3 prior tickets scope a single
function's *return-value* sentinel. This is a structurally different
manifestation of the same class -- a `try`/`except: pass` around a
**loop body appending to an accumulator list**, not a single return
value -- in a 4th distinct file (`appliance/bin/verify-standing-
portfolio.py`), confirmed via `head -8`/Authored-boundary reads of
GL-ERRC-019, GL-EXP-005, and GL-EXP-011 this session: none names
`appliance/bin/verify-standing-portfolio.py` or the `evidence/raw/
challenges` scan.

**No dedicated test coverage exists for this file.** `find . -path
./.claude -prune -o -iname "*test*standing-portfolio*" -print` (repo-wide,
excluding worktrees): zero matches. `ls appliance/bin/`: no
`tests/`/`test_*.py` sibling for `verify-standing-portfolio.py`.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below. Confirmed
this session via `grep -n "verify-standing-portfolio"
tickets/OVERLAPS.md`: no existing entry for this file.)

```text
appliance/bin/verify-standing-portfolio.py   # challenge_files scan (lines 44-50) and the
                                              # "hidden-challenges" check detail (line 51) only
tickets/GL-EXP-015.md
```

No change to `check_signature`, `verify_log`, `tree_inventory`,
`tree_digest`, the `evidence-digests`/`coordinate-bindings`/`signature`/
`bounded-claim`/`customer-control`/`independent-verifier` checks, or
`main()`'s argument parsing or report-writing control flow beyond what is
strictly required to make the `challenge_files` scan's failure modes
distinguishable. No change to `appliance/bin/build-standing-portfolio.py`
(the separate `hidden_challenge_count` declaration mechanism),
`appliance/bin/run-reference-e2e.sh`, or `appliance/bin/build-offline-
bundle.sh`. No change to `tools/v26.8.1/src/coverage_projection.rs`
(GL-ERRC-019, `EXECUTED`), `tools/v26.8.1/src/bin/subsystem_verifier.rs`
(GL-EXP-005, `NOT_STARTED`), or `tools/v26.8.20/observe_contract.py`
(GL-EXP-011, `NOT_STARTED`).

## Hard laws

1. A portfolio directory whose `evidence/raw/challenges/*.json` files all
   parse successfully must produce the identical `challenge_files` list
   and identical `hidden-challenges` check outcome as before this ticket
   -- the happy path's observable behavior does not change.
2. A file matched by the `*.json` glob whose contents cannot be parsed or
   read (malformed JSON, non-UTF8 bytes, unreadable/permission-denied, or
   valid JSON that is not an object) must be distinguishable, in the
   emitted report, from a file that parses successfully but whose
   `visibility` is not `customer-hidden`. The two cases must not collapse
   into the same silent omission from `challenge_files`.
3. The `except Exception` catch-all is not simply deleted -- a read/parse
   failure on one challenge file must not crash `verify-standing-
   portfolio.py`'s `main()` with an uncaught traceback and a non-zero
   exit; it must still be caught, but its cause recorded (e.g. a
   `challenge_parse_errors` list in the `hidden-challenges` check detail)
   rather than silently discarded.
4. The `hidden-challenges` check's boolean pass/fail semantics for the
   genuine "zero customer-hidden files present, all files parsed cleanly"
   case do not change from current behavior.
5. `git diff --stat` after this ticket touches only
   `appliance/bin/verify-standing-portfolio.py` and this ticket file.

## Falsifiers

- After the fix, a real corrupted file under `evidence/raw/challenges/`
  (e.g. truncated JSON, or non-UTF8 bytes) still produces a
  `hidden-challenges` report identical to a portfolio with zero
  hidden-challenge files -- no distinguishable trace of the parse
  failure anywhere in the report.
- The happy-path `challenge_files` list or `hidden-challenges` check
  outcome for a portfolio with only well-formed challenge files changes
  as a side effect of this fix.
- `appliance/bin/run-reference-e2e.sh` fails or its `hidden-challenges`-
  dependent assertions regress after this fix, for the reference
  fixtures that currently pass end to end.
- A single corrupted challenge file causes `verify-standing-portfolio.py`
  to crash with an uncaught exception and non-zero exit, instead of
  completing and writing a report with the failure recorded.
- `git diff --stat` after this ticket touches any file outside
  `appliance/bin/verify-standing-portfolio.py` and
  `tickets/GL-EXP-015.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the collapse before touching anything:
grep -n "" appliance/bin/verify-standing-portfolio.py | sed -n '41,51p'

# Confirm the real e2e path that exercises this loop still passes
# end-to-end after the fix (it already writes a real customer-hidden
# challenge file at evidence/challenges/runtime-hidden.json -- see
# run-reference-e2e.sh:9):
bash appliance/bin/run-reference-e2e.sh
echo "EXIT:$?"

# After the fix, confirm a real corrupted challenge file's parse failure
# is distinguishable from a genuine zero-hidden-challenges case, e.g. a
# unit test writing a real malformed-JSON file to a real tmp
# evidence/raw/challenges/ directory and asserting on the real report
# dict's content -- no mocked file I/O or json.loads, per this account's
# Chicago-style testing discipline.

git diff --stat   # must show only appliance/bin/verify-standing-portfolio.py
                   # and tickets/GL-EXP-015.md
```

## Evidence this ticket is grounded in (verified this session)

- Direct read (`grep -n "" appliance/bin/verify-standing-portfolio.py |
  sed -n '41,51p'`) this session: `challenge_files` scan and
  `except Exception: pass` byte-for-byte as quoted in Outcome, with the
  bare catch on line 49 confirmed at that exact line number.
- `wc -l appliance/bin/verify-standing-portfolio.py` this session: 73
  lines total -- a small, fully-reviewed file, not a fragment excerpted
  out of a larger unreviewed context.
- `grep -rln "verify-standing-portfolio" appliance/bin/*.sh` and
  targeted `grep -n` on each match this session: confirmed
  `build-offline-bundle.sh:75` (a `--help` smoke check only) and
  `run-reference-e2e.sh:15,40,55` (3 real, fully-argumented invocations)
  both call this script, ruling out dead-code concerns.
- Direct read of `run-reference-e2e.sh:1-25` this session: confirmed the
  reference e2e script writes a real `customer-hidden`-visibility
  challenge file (`runtime-hidden.json`, with a real `openssl rand -hex
  32` nonce) into the evidence tree that `build-standing-portfolio.py`
  copies into the portfolio, then calls `verify-standing-portfolio.py`
  against that exact portfolio -- confirming the `challenge_files` loop
  (lines 44-50) is genuinely exercised by a real file on every reference
  e2e run, not merely reachable in theory.
- `ls tests/fixtures/customer-evidence/` and `ls
  tests/fixtures/engagement.reference.json` this session: both exist on
  disk (exit 0), confirming `run-reference-e2e.sh`'s fixture inputs are
  real.
- `grep -n "hidden_challenge_count\|customer-hidden\|challenges"
  appliance/bin/build-standing-portfolio.py` this session: confirmed
  `hidden_challenge_count` (lines 36, 53) is sourced from the engagement
  config's `challenges` list -- a mechanism entirely separate from
  `verify-standing-portfolio.py`'s own `evidence/raw/challenges/*.json`
  directory scan, confirming line 51's check is a genuine cross-check
  between two independently-derived values, not a tautology.
- `grep -l "verify-standing-portfolio" tickets/*.md` and `grep -n
  "verify-standing-portfolio" tickets/GL-RECEIPT-007.md` this session:
  exactly one ticket, one match (line 83), an incidental mention of a
  signing step, not an authored-boundary target and not a discussion of
  this except-swallow.
- `grep -rln "hidden-challenges\|hidden_challenge_count\|challenge_files"
  tickets/*.md` this session: zero matches -- no other ticket names this
  check.
- `grep -n "verify-standing-portfolio\|verify_standing_portfolio"
  tickets/OVERLAPS.md` this session: zero matches (exit 1) -- no
  cross-ticket claim on this file.
- `head -8 tickets/GL-ERRC-019.md`, `cat tickets/GL-EXP-005.md`, and the
  `git_head()`-scoped Authored boundary in `tickets/GL-EXP-011.md` this
  session: confirmed all 3 prior undifferentiated-collapse tickets scope
  a single Rust or Python file's return-value sentinel, none of them
  `appliance/bin/verify-standing-portfolio.py`, and none discussing a
  loop-body accumulator collapse -- ruling out duplication with this
  ticket's target and construct.
- `find . -path ./.claude -prune -o -iname
  "*test*standing-portfolio*" -print` this session: zero matches --
  confirmed no dedicated test file currently exercises this script's
  failure modes.
- `git rev-parse HEAD` this session:
  `bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's
  declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
undifferentiated-collapse finding for `verify-standing-portfolio.py`'s
`challenge_files` scan; the actual cause-distinguishing report shape
(e.g. a `challenge_parse_errors` list threaded into the `hidden-
challenges` check detail) and its Chicago-style real-file test coverage
have not been implemented.
