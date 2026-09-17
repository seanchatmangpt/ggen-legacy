# GL-ERRC-010 — External anchor for transparency-log.py's verify() (silent-unrevoke gap)

**Status:** admitted, `NOT_STARTED` — drafted by ultracode ERRC pass 3
**Base:** `seanchatmangpt/ggen-legacy@f9b283e`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`appliance/bin/transparency-log.py`'s `verify()` (lines 29-39) checks
per-entry `index`/`previous_hash` sequencing and recomputes `entry_hash`
from `canonical(entry)`, but has no anchor outside the log file itself —
an attacker with write access to the log can truncate the tail, drop a
revocation entry (silently un-revoking a previously-revoked entry), or
rebuild the whole chain dropping a middle entry, and `verify()` reports
`(True, entries, None)` in all three cases because every check `verify()`
performs is *internal consistency*, not *append-only-ness against a prior
observed state*. This ticket adds a `--anchor <path>` mode to `verify()`:
before the file-only check, if a sidecar anchor file
(`<log>.anchor.json`, containing `{"entry_count": N, "head_entry_hash":
"<sha256>"}`, written by `append_entry()` after every successful append)
exists, `verify()` additionally asserts the *current* file's
`len(entries)` and final `entry_hash` are `>=`/`==` what the last observed
anchor recorded — a log that has *shrunk* or whose recorded head no
longer matches a previously-anchored head fails closed
(`TRANSPARENCY_ANCHOR_REGRESSION`), even though the file's own internal
hash chain still validates. This does not implement a full external
transparency-log service (e.g. Sigstore Rekor) — it is the smallest
change that closes the specific silent-unrevoke/truncate class this
session reproduced live, named explicitly as a stopgap, not a claim of
full tamper-evidence.

## Authored boundary

```text
appliance/bin/transparency-log.py   # verify() gains --anchor mode; append_entry() writes/updates the sidecar anchor
tickets/GL-ERRC-010.md
```

No other file in `appliance/bin/` is touched. `scripts/verify_docs.py`'s
existing reference to `appliance/bin/transparency-log.py` (line 48, an
existence check only) is unaffected — this ticket doesn't change the
script's interface, only adds a new opt-in flag and a new sidecar file
`append_entry()` writes.

## Hard laws

1. `verify()` without `--anchor` (the current default call signature) is
   byte-for-byte unchanged in behavior — this ticket adds an opt-in mode,
   it does not change the meaning of a bare `verify(log)` call any
   existing caller (`scripts/verify_docs.py`, `append_entry()`'s own
   pre-append check) makes today.
2. The anchor file is written only by `append_entry()`, only after a
   successful append (i.e., only observed-good states get anchored) —
   never by `verify()` itself, so running `verify()` cannot forge a new
   anchor that launders a tampered file into "previously observed."
3. A missing anchor file is `UNKNOWN`/pass-through (first run before any
   append has happened), never a hard failure — this ticket must not
   break the existing zero-anchor bootstrap case.
4. This ticket does not claim to defend against an attacker who can write
   *both* the log and its anchor file in the same operation (e.g., a
   single `cp -r` of a forged directory) — the anchor must eventually be
   written to storage the log-writer doesn't fully control (e.g. this
   session's own `transparency-log.py` being invoked from a CI step whose
   anchor artifact is uploaded separately) for real security value; this
   ticket only builds the mechanism, real deployment of an independent
   anchor store is out of scope and named as a follow-up.

## Falsifiers

- Truncating the tail of a real log file (dropping the last N entries)
  after an anchor has been written still reports `valid: True` under
  `--anchor`.
- Dropping a `revocation` entry from the middle of a real log, leaving
  every other entry's `index`/`previous_hash` fields unpatched (this
  session's reproduced attack requires renumbering `index` and rewriting
  `previous_hash` for every entry after the drop, which itself changes
  every downstream `entry_hash` — confirm the anchor's recorded
  `head_entry_hash` catches this rewritten-tail case where per-entry
  internal consistency alone does not) reports `valid: True` under
  `--anchor`.
- `verify()` without `--anchor` behaves differently than before this
  ticket for any of the 3 existing return tuples
  (`TRANSPARENCY_LOG_MISSING` / `TRANSPARENCY_CHAIN_BROKEN` /
  `TRANSPARENCY_ENTRY_HASH_MISMATCH`).
- First-run bootstrap (no anchor file yet, `--anchor` passed) raises
  instead of falling through to file-only verification.

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy
python3 -c "
import sys, json, tempfile, os
sys.path.insert(0, 'appliance/bin')
import importlib.util
spec = importlib.util.spec_from_file_location('tlog', 'appliance/bin/transparency-log.py')
tlog = importlib.util.module_from_spec(spec); spec.loader.exec_module(tlog)

d = tempfile.mkdtemp()
log = os.path.join(d, 'log.jsonl')
tlog.append_entry(log, {'entry_type':'note','payload':'a'})
tlog.append_entry(log, {'entry_type':'revocation','target_entry_hash':'x'})
tlog.append_entry(log, {'entry_type':'note','payload':'c'})

# Attack: truncate the tail after anchoring.
lines = open(log).read().splitlines()
open(log, 'w').write('\n'.join(lines[:2]) + '\n')

ok, entries, err = tlog.verify(log)  # file-only: still internally consistent
assert ok, 'sanity: file-only verify should still pass on a consistent truncation'

ok2, entries2, err2 = tlog.verify(log, anchor=os.path.join(d, 'log.jsonl.anchor.json'))
assert not ok2, 'anchor mode must catch the truncation the file-only check misses'
assert err2 == 'TRANSPARENCY_ANCHOR_REGRESSION', err2
print('OK: truncation caught under --anchor, silent under file-only (confirms the gap and the fix)')
"
```

## Evidence this ticket is grounded in (verified this session)

- `appliance/bin/transparency-log.py:29-39` (`verify()`, read directly this
  session) performs exactly three checks per entry —
  `e.get("index")!=index or e.get("previous_hash")!=previous`,
  `claimed!=actual` (recomputed `entry_hash`) — and returns
  `(bool(entries), entries, None if entries else "TRANSPARENCY_LOG_EMPTY")`
  once the loop completes; there is no reference anywhere in the function
  to any state outside the single file passed in as `log`.
- `docs/v26.8.20/ultracode-loop-progress.md:59` (item 10, this repo's own
  prior audit, same session lineage): "verify() has no external anchor —
  reproduced 3 live attacks (truncate tail, un-revoke by dropping the
  revocation entry, full chain rebuild dropping a middle entry) that all
  report `{valid:true, error:null}`. Concretely: a revoked entry can be
  silently un-revoked by an attacker with file write access. Not fixed
  (outside GL-ARCH-003 boundary) — worth a dedicated ticket given
  severity." This ticket is that dedicated ticket.
- `docs/v26.8.20/DECISIONS.md`'s "Just-recipe / CI-workflow drift" and
  "Stale foundry authority finding" sections show this repo's established
  pattern of flagging-not-fixing security/staleness findings until a real
  ticket exists — this ticket follows that same discipline for the one
  finding explicitly marked "worth a dedicated ticket given severity" and
  still, as of this session, has none.
- `tickets/GL-RECEIPT-007.md` line 26-28 explicitly states
  `transparency-log.py`'s existing hash-chain "remain[s] unchanged" under
  that ticket's boundary — confirming no other admitted or drafted ticket
  currently claims this file, so this ticket does not duplicate or
  conflict with GL-RECEIPT-007's scope.
- `scripts/verify_docs.py:48` references
  `"appliance/bin/transparency-log.py"` only as a path-existence check in
  a list of expected files (confirmed by direct read) — it does not call
  `verify()` at all, so this ticket's new opt-in `--anchor` parameter has
  no existing caller to keep compatible beyond `transparency-log.py`'s own
  `append_entry()` pre-append call, which this ticket's Hard Law 1 already
  pins to unchanged behavior.

## Standing

`UNKNOWN` — not started. This ticket only drafts the anchor mechanism and
its acceptance reproduction; implementing `verify()`'s `--anchor` branch
and `append_entry()`'s sidecar-write, and wiring a real independent anchor
store for production use (Hard Law 4's named follow-up), remain out of
scope until a session/human explicitly starts this ticket.
