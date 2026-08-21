# GL-EXP-039 — Raise `cross-check-portfolio.py`'s hidden-challenge scan out of an uncaught crash on malformed `evidence/raw/challenges/*.json`

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`appliance/bin/cross-check-portfolio.py:20` has zero exception handling
around the `json.loads` call in its hidden-challenge scan. Direct read
(`grep -n "HIDDEN_CHALLENGE_MISSING\|json.loads(p.read_text())"
appliance/bin/cross-check-portfolio.py`) confirms the construct at the
exact line number, byte-for-byte:

```python
hidden=list((root/"evidence/raw/challenges").glob("*.json")) if (root/"evidence/raw/challenges").exists() else []
if not any(json.loads(p.read_text()).get("visibility")=="customer-hidden" for p in hidden): failures.append("HIDDEN_CHALLENGE_MISSING")
```

**Reproduced this session, not inferred from reading source.** Built a
real scratch portfolio directory with a real `claim-manifest.json` and one
malformed file at `evidence/raw/challenges/bad.json` containing the
literal bytes `{not valid json`, then ran the real script against it:

```
python3 appliance/bin/cross-check-portfolio.py --portfolio <dir> \
  --public-key /nonexistent.pem --signature /nonexistent.sig \
  --report <dir>/report.json
```

Real output: exit code `1`, an uncaught `json.decoder.JSONDecodeError:
Expecting property name enclosed in double quotes: line 1 column 2 (char
1)` traceback dumped to stderr, and no `report.json` written at all
(`ls <dir>/report.json` after the run: "No such file or directory"). This
is a genexpr inside `any(...)`, so *any* single malformed file among
`evidence/raw/challenges/*.json` aborts the whole scan before the `for
item in m.get("evidence_inventory",[])` digest loop, the `openssl
dgst -sign -verify` signature check, or the report write ever run —
one bad file destroys every other check this script performs, with no
`HIDDEN_CHALLENGE_PARSE_ERROR`-style finding, no written report, no
controlled `PARTIAL_ALIVE`/`REFUSED` outcome, just a bare Python crash.

**This is the opposite-failure-mode sibling of `GL-EXP-015`**, which
targets the identical `evidence/raw/challenges/*.json` glob-and-parse
pattern one file over, in `appliance/bin/verify-standing-portfolio.py`.
Direct read of `tickets/GL-EXP-015.md` this session confirms its target
construct:

```python
try:
    item=read_json(path)
    if item.get("visibility")=="customer-hidden": challenge_files.append(path.name)
except Exception:
    pass
```

`verify-standing-portfolio.py` over-forgives (silently drops a parse
failure into the same bucket as "not a hidden-challenge file", per
`GL-EXP-015`'s Outcome); `cross-check-portfolio.py` under-forgives (zero
`try`/`except`, an uncaught crash). Both are undifferentiated-failure-mode
defects on the exact same source pattern, in the exact same portfolio
subtree, in two independently-invoked scripts that both run against the
same portfolio directory in the same `run-reference-e2e.sh` pipeline —
but they are opposite failure directions, not duplicates: `GL-EXP-015`'s
fix (catch, but record the cause) and this ticket's fix (catch to avoid
a crash, and record the cause) converge on the same target shape from
opposite starting points.

**Downstream blast radius confirmed.** `grep -n "cross.check\|cross_check"
appliance/bin/decision-engine.py` this session shows `decision-engine.py`
takes `--cross-check-report` as a required argument and calls
`read_json(a.cross_check_report)` on it (line 31) to compute
`release-admission.json`'s `basis.cross_check` field (line 35). A crash
in `cross-check-portfolio.py` that leaves no `report.json` on disk means
`decision-engine.py`, if invoked next in a pipeline (as it is in
`run-reference-e2e.sh`), itself crashes on a missing file with its own
uncaught traceback — the malformed-file defect propagates into a second
script's failure, not just this one's.

**No existing ticket already scopes this crash.** Verified this session:

- `grep -l cross-check-portfolio tickets/GL-*.md`: `GL-EXP-013.md`,
  `GL-EXP-015.md`, `GL-EXP-017.md`, `GL-RECEIPT-007.md`. Direct
  inspection of every match's context and Authored-boundary section this
  session:
  - `GL-EXP-013.md:121,170` and `GL-EXP-017.md:80,131`: both explicitly
    state "No change to `appliance/bin/cross-check-portfolio.py`" and
    list it as a Falsifier if modified (neither defines the
    `sha256_file`/`read_json`/`write_json` helpers those tickets
    consolidate) — the file is named only to be excluded.
  - `GL-EXP-015.md:88` and `GL-RECEIPT-007.md:84`: each has exactly one
    incidental prose mention of `cross-check-portfolio.py` (a
    parenthetical aside and a correction about where an `openssl dgst
    -sign` step lives), never inside an `## Authored boundary` fence,
    never discussing the hidden-challenge scan or this crash.
  - `awk` scan of every `tickets/GL-*.md`'s `## Authored boundary`
    fenced code block this session: zero files list
    `appliance/bin/cross-check-portfolio.py` as a path any ticket claims
    to edit.
- `grep -n "cross-check-portfolio\|cross_check" tickets/OVERLAPS.md`:
  zero matches — no existing cross-ticket entry for this file.
- `find . -path ./.claude -prune -o -iname "*test*cross-check*" -print`
  and `ls appliance/bin/ | grep -i test`: zero matches — no dedicated
  test coverage exists for this script today.

**This is a live, exercised code path, not dead weight.** Verified this
session:

- `grep -rn cross-check-portfolio appliance/bin/*.sh justfile`:
  `appliance/bin/build-offline-bundle.sh:76` — `python3
  appliance/bin/cross-check-portfolio.py --help >/dev/null`, an
  existence/smoke check only, does not exercise the hidden-challenge
  scan.
  `appliance/bin/run-reference-e2e.sh:16` — one real, fully-argumented
  invocation (`--portfolio/--public-key/--signature/--report`), not a
  smoke test.
- Direct read of `run-reference-e2e.sh`: the reference e2e script writes
  a real customer-hidden challenge file into the evidence tree before
  building the portfolio (`printf
  '{"id":"runtime-hidden","visibility":"customer-hidden","nonce":"%s"}\n'
  "$(openssl rand -hex 32)" >
  "$TMP/evidence/challenges/runtime-hidden.json"`), which
  `build-standing-portfolio.py` copies into the portfolio's
  `evidence/raw/challenges/` directory, confirming the exact scan this
  ticket targets is genuinely exercised, with a real matching file, on
  every reference e2e run.
- `wc -l appliance/bin/cross-check-portfolio.py`: 29 lines total — a
  small, fully-reviewed file, not a fragment excerpted out of a larger
  unreviewed context.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below. Confirmed
this session via `grep -n "cross-check-portfolio" tickets/OVERLAPS.md`:
no existing entry for this file, and via `awk`-scanning every
`tickets/GL-*.md`'s `## Authored boundary` fence: no other ticket claims
this path as a path it edits — `GL-EXP-013`/`GL-EXP-017` explicitly
exclude it, `GL-EXP-015`/`GL-RECEIPT-007` only mention it in passing
outside any Authored-boundary fence. No disclosed overlap to record.)

```text
appliance/bin/cross-check-portfolio.py   # HIDDEN_CHALLENGE_MISSING scan (line 20) only
tickets/GL-EXP-039.md
```

No change to `digest`, the `VERIFIER_NOT_INDEPENDENT` identity check, the
`evidence_inventory` digest loop, the `SIGNATURE_INVALID` `openssl`
subprocess check, or `main()`'s argument parsing beyond what is strictly
required to make the hidden-challenge scan's parse failure distinguishable
and non-crashing. No change to `appliance/bin/verify-standing-
portfolio.py` (`GL-EXP-015`'s own separate target), `appliance/bin/
build-standing-portfolio.py`, `appliance/bin/decision-engine.py`,
`appliance/bin/run-reference-e2e.sh`, or `appliance/bin/
build-offline-bundle.sh`.

## Hard laws

1. A portfolio whose `evidence/raw/challenges/*.json` files all parse
   successfully must produce the identical `failures` list and identical
   exit code as before this ticket -- the happy path's observable
   behavior does not change.
2. A file matched by the `*.json` glob that cannot be parsed or read
   (malformed JSON, non-UTF8 bytes, unreadable/permission-denied, or
   valid JSON that is not an object) must be caught and its cause
   recorded as a distinct entry in the emitted report's `failures` list
   (e.g. `HIDDEN_CHALLENGE_PARSE_ERROR:<filename>`), distinguishable from
   both `HIDDEN_CHALLENGE_MISSING` (the genuine zero-hidden-file case)
   and a clean pass.
3. The crash is not simply wrapped in a blanket `except: pass` that
   discards the cause (that would just re-import `GL-EXP-015`'s opposite
   defect into this file) -- a read/parse failure must still be caught,
   but recorded, and `main()` must still write a `report.json` and exit
   non-zero (matching the existing `failures`-list / `SystemExit`
   contract), not crash with an uncaught traceback and no report at all.
4. The `HIDDEN_CHALLENGE_MISSING` check's pass/fail semantics for the
   genuine "zero customer-hidden files present, all files parse cleanly"
   case do not change from current behavior.
5. `git diff --stat` after this ticket touches only
   `appliance/bin/cross-check-portfolio.py` and this ticket file.

## Falsifiers

- After the fix, a real malformed file under `evidence/raw/challenges/`
  (e.g. the literal bytes `{not valid json`) still crashes
  `cross-check-portfolio.py` with an uncaught exception, non-zero exit,
  and no `report.json` written.
- The happy-path `failures` list or exit code for a portfolio with only
  well-formed challenge files changes as a side effect of this fix.
- `appliance/bin/run-reference-e2e.sh` fails, or its cross-check-report-
  dependent assertions regress, for the reference fixtures that
  currently pass end to end.
- A single corrupted challenge file still causes `decision-engine.py` (or
  any downstream consumer of `--cross-check-report`) to crash on a
  missing `report.json`, instead of receiving a written report with the
  parse failure recorded and a controlled non-zero standing.
- `git diff --stat` after this ticket touches any file outside
  `appliance/bin/cross-check-portfolio.py` and
  `tickets/GL-EXP-039.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the crash before touching anything:
grep -n "" appliance/bin/cross-check-portfolio.py | sed -n '15,22p'

# Confirm the real e2e path that exercises this scan still passes
# end-to-end after the fix (it already writes a real customer-hidden
# challenge file at evidence/challenges/runtime-hidden.json -- see
# run-reference-e2e.sh):
bash appliance/bin/run-reference-e2e.sh
echo "EXIT:$?"

# After the fix, confirm a real malformed challenge file's parse failure
# is caught and recorded instead of crashing: write a real malformed-
# JSON file to a real tmp evidence/raw/challenges/ directory (as
# reproduced in this ticket's Outcome), run the real script against it,
# and assert on the real report dict's content and the real (non-crash)
# exit code -- no mocked file I/O or json.loads, per this account's
# Chicago-style testing discipline.

git diff --stat   # must show only appliance/bin/cross-check-portfolio.py
                   # and tickets/GL-EXP-039.md
```

## Evidence this ticket is grounded in (verified this session)

- Direct read (`grep -n "HIDDEN_CHALLENGE_MISSING\|json.loads(p.read_text())"
  appliance/bin/cross-check-portfolio.py`) this session: confirmed the
  zero-try/except construct byte-for-byte at line 20 exactly as quoted in
  Outcome.
- Real reproduction this session: built a real scratch portfolio
  directory (`claim-manifest.json` with `implementer_identity`/
  `verifier_identity`/`evidence_inventory` keys, plus one malformed file
  at `evidence/raw/challenges/bad.json` containing `{not valid json`) and
  ran `python3 appliance/bin/cross-check-portfolio.py --portfolio <dir>
  --public-key /nonexistent.pem --signature /nonexistent.sig --report
  <dir>/report.json` against it. Real captured output: exit code `1`,
  full Python traceback ending in `json.decoder.JSONDecodeError:
  Expecting property name enclosed in double quotes: line 1 column 2
  (char 1)`, and `ls <dir>/report.json` afterward reporting "No such file
  or directory" -- confirming no report is written on this crash path.
- `wc -l appliance/bin/cross-check-portfolio.py` this session: 29 lines
  total -- a small, fully-reviewed file.
- `grep -rn cross-check-portfolio appliance/bin/*.sh justfile` and
  targeted follow-up reads this session: confirmed
  `build-offline-bundle.sh:76` (a `--help` smoke check only) and
  `run-reference-e2e.sh:16` (one real, fully-argumented invocation) both
  call this script, ruling out dead-code concerns.
- Direct read of `run-reference-e2e.sh` this session: confirmed the
  reference e2e script writes a real `customer-hidden`-visibility
  challenge file (`runtime-hidden.json`, with a real `openssl rand -hex
  32` nonce) into the evidence tree that `build-standing-portfolio.py`
  copies into the portfolio, then calls `cross-check-portfolio.py`
  against that exact portfolio -- confirming the hidden-challenge scan is
  genuinely exercised by a real file on every reference e2e run.
- `grep -n "cross.check\|cross_check" appliance/bin/decision-engine.py`
  this session: confirmed `decision-engine.py` requires
  `--cross-check-report` and calls `read_json(a.cross_check_report)`
  (line 31) to populate `release-admission.json`'s `basis.cross_check`
  field (line 35), confirming a missing `report.json` from this crash
  propagates into a second script's own failure downstream.
- `grep -l cross-check-portfolio tickets/GL-*.md` this session:
  `GL-EXP-013.md`, `GL-EXP-015.md`, `GL-EXP-017.md`,
  `GL-RECEIPT-007.md`. Direct read of every match's surrounding context
  and each ticket's `## Authored boundary` fence this session: none
  claims `appliance/bin/cross-check-portfolio.py` as a path it edits --
  `GL-EXP-013`/`GL-EXP-017` explicitly exclude it as a Falsifier if
  modified; `GL-EXP-015`/`GL-RECEIPT-007` mention it only in incidental
  prose outside any Authored-boundary fence. Confirmed via an `awk` scan
  of every `tickets/GL-*.md`'s `## Authored boundary` block for
  `cross-check-portfolio`: zero matches.
- `grep -n "cross-check-portfolio\|cross_check" tickets/OVERLAPS.md` this
  session: zero matches (exit 1) -- no existing cross-ticket entry, so no
  overlap disclosure is required by this ticket's own Authored-boundary
  claim.
- `find . -path ./.claude -prune -o -iname "*test*cross-check*" -print`
  and `ls appliance/bin/ | grep -i test` this session: zero matches -- no
  dedicated test coverage exists for this file today.
- Direct read of `tickets/GL-EXP-015.md` this session (Outcome and
  Authored-boundary sections): confirmed its target construct
  (`verify-standing-portfolio.py`'s `try: ... except Exception: pass`
  around the identical `evidence/raw/challenges/*.json` glob-and-parse
  pattern) and confirmed its Authored boundary is scoped to
  `verify-standing-portfolio.py` only, not this file -- establishing the
  two tickets as disjoint, sibling fixes on the opposite failure-mode
  ends of the same source pattern in two different files.
