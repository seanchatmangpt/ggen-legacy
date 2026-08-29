# GL-EXP-045 — Consolidate the typed `canonical(value: Any) -> bytes` duplicate in `appliance/bin/build-subsystem-evidence.py`/`verify-subsystem-evidence.py` into `_shared.py`

**Status:** `EXECUTED` 2026-08-21 -- real fix landed in the main checkout and re-verified
there (was `admitted, NOT_STARTED`, drafted by standing ultracode exploration cron).
**Recovery note**: the Workflow pass that executed this ticket stalled mid-run after
the code edit and this file's own Evidence/Standing sections had already landed
(confirmed no live `cargo`/`just` process and no stale git lock — a genuine hang, not
a slow build); the stalled task was stopped and I completed the remaining
verification (falsifiers, `just ci-all`) and this header correction directly, rather
than losing or re-doing already-verified work.

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`appliance/bin/build-subsystem-evidence.py:15` and `appliance/bin/verify-subsystem-evidence.py:15`
each define the identical typed helper:

```python
def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
```

Confirmed byte-identical this session: `sed -n '/^def canonical/,/^$/p' <file> | md5` on both
files → `02693b06fcb4cdf04afc331ab93686d1`. `grep -n "^def " appliance/bin/build-subsystem-evidence.py
appliance/bin/verify-subsystem-evidence.py` (this session) confirms `canonical()` sits at line
15 in both files, immediately before `sha256_file()` (line 21) and `exact_head()` (line 25) —
disjoint from both, not overlapping either.

Both are live, not dead code: `grep -n "canonical(manifest)\|canonical(unsigned)" appliance/bin/build-subsystem-evidence.py
appliance/bin/verify-subsystem-evidence.py` (this session) shows one real call site each --
`build-subsystem-evidence.py:254`: `manifest["receipt_digest"] = hashlib.sha256(canonical(manifest)).hexdigest()`;
`verify-subsystem-evidence.py:167`: `receipt_observed = hashlib.sha256(canonical(unsigned)).hexdigest()`.

This is the exact pair `GL-EXP-041` (`NOT_STARTED`, same corpus, same base commit) already
found and deliberately excluded from its own `_shared.py` consolidation of the 5-file untyped
`canonical(obj)` variant. `GL-EXP-041`'s Hard Law 4 states verbatim: "`appliance/bin/build-subsystem-evidence.py`'s
and `appliance/bin/verify-subsystem-evidence.py`'s own typed `canonical(value: Any) -> bytes`
is explicitly **out of scope** -- not touched, not consolidated, not re-pointed to `_shared.py`.
It is behaviorally equivalent to the 5-file version (verified this session) but not the same
source, and unifying differently-typed call signatures across files with a different
type-hinting convention (`from typing import Any` present vs. absent) is a legitimate,
distinct follow-up candidate, not this ticket's job." (`tickets/GL-EXP-041.md:146-151`, read
in full this session.) `GL-EXP-041`'s own Evidence section already established the two
implementations behaviorally equivalent -- identical output bytes for identical input, since
Python's `.encode()` already defaults to UTF-8 -- so re-pointing these two call sites at a
`_shared.canonical()` changes zero external behavior.

`grep -ln "canonical(value: Any)" tickets/GL-*.md` (this session): exactly one match,
`tickets/GL-EXP-041.md` -- the file that names and defers this exact pair. No other ticket in
the corpus claims it. `grep -n "canonical" tickets/OVERLAPS.md` (this session) finds the
existing `appliance/bin/_shared.py` section (added by `GL-EXP-041`), which lists `GL-EXP-013`,
`GL-EXP-017`, and `GL-EXP-041` as the module's three current contributors and explicitly notes
`GL-EXP-041`'s `canonical()` addition is "the 5-file untyped variant only -- explicitly
excludes the differently-typed `canonical()` in `build-subsystem-evidence.py`/
`verify-subsystem-evidence.py`" -- confirming, from the registry's own text, that this typed
pair is a disclosed gap, not an oversight this ticket is inventing.

`ls appliance/bin/_shared.py` (this session): no such file yet -- none of `GL-EXP-013`,
`GL-EXP-017`, or `GL-EXP-041` has executed. This ticket is a fourth, independent contributor to
the same not-yet-created module, adding exactly one function (`canonical`, the typed variant,
under a distinguishing name so it cannot collide with the untyped `canonical(obj)` the other
three tickets add -- see Hard Law 1).

`ls tickets/GL-EXP-045.md` (run before writing this file): confirmed no such file existed --
this pre-assigned id was free.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` -- checked there and
against every existing `GL-EXP-*.md`'s Authored boundary before writing this section.
`appliance/bin/build-subsystem-evidence.py` and `appliance/bin/verify-subsystem-evidence.py`
are already claimed by `GL-EXP-013` (`sha256_file`/`read_json`, lines 21/32) and `GL-EXP-023`
(`exact_head`, line 25) in the existing `appliance/bin (exact_head vs. sha256_file/read_json)`
section of `tickets/OVERLAPS.md` -- this ticket's own claim is `canonical()` at line 15 in both
files, a disjoint, earlier-in-file region than either sibling's, so this write adds a new
disclosure to that same registry rather than a new section. `appliance/bin/_shared.py` is
already claimed by `GL-EXP-013`/`GL-EXP-017`/`GL-EXP-041` in the registry's existing
`appliance/bin/_shared.py` section -- this ticket appends its disclosure there too.)

```text
appliance/bin/_shared.py                    # add typed_canonical(value: Any) -> bytes (create the file if none of GL-EXP-013/017/041 has run yet; append otherwise)
appliance/bin/build-subsystem-evidence.py   # delete private canonical() (line 15), import shared, rewrite the one call site (line 254)
appliance/bin/verify-subsystem-evidence.py  # delete private canonical() (line 15), import shared, rewrite the one call site (line 167)
tickets/GL-EXP-045.md
tickets/OVERLAPS.md                         # append disclosure to the existing `appliance/bin/_shared.py` and `appliance/bin (exact_head vs. sha256_file/read_json)` sections
```

No change to `sha256_file`, `exact_head`, `read_json`, `digest_sources`, `check_map`, or any
other function in either file. No change to the 5-file untyped `canonical(obj)` `GL-EXP-041`
already owns, or to `GL-EXP-013`'s `sha256_file`/`read_json` logic, or to `GL-EXP-023`'s
`exact_head` logic. No change to `appliance/bin/run-reference-e2e.sh` itself.

## Hard laws

1. `appliance/bin/_shared.py` gains exactly one new helper for this ticket, byte-for-byte
   matching the typed body already shared by both files (md5 cited in Outcome). To avoid
   colliding with the untyped `canonical(obj)` name `GL-EXP-041` independently adds to the same
   module, this ticket names its addition `typed_canonical(value: Any) -> bytes` (or, if
   `GL-EXP-041` has already landed by execution time and its `canonical(obj)` is confirmed to
   still coexist safely under a different name, this ticket may instead re-derive a
   non-colliding name at execution time -- either way, no ticket among the four may cause a
   `_shared.py` name collision).
2. Both files' private `def canonical` (line 15 in each, confirmed this session) are deleted
   outright and replaced with an import from `_shared`.
3. The one call site in each file (`build-subsystem-evidence.py:254`,
   `verify-subsystem-evidence.py:167`) is rewritten to call the imported name; external
   behavior is unchanged -- same `receipt_digest`/`receipt_observed` bytes for the same input,
   confirmed by `GL-EXP-041`'s own behavioral-equivalence check (Outcome, above) plus this
   ticket's own Acceptance re-check below.
4. The 5-file untyped `canonical(obj)` `GL-EXP-041` owns is explicitly out of scope -- not
   touched, not merged with, not renamed by this ticket.
5. If `appliance/bin/_shared.py` already exists when this ticket executes (any of
   `GL-EXP-013`/`GL-EXP-017`/`GL-EXP-041` ran first), this ticket appends its one helper
   without modifying any sibling's addition. If `_shared.py` does not yet exist, this ticket
   creates it containing exactly this one helper; whichever sibling executes later is
   responsible for appending without removing this ticket's addition. No ticket among the four
   may overwrite or truncate another's contribution to `_shared.py`.
6. `appliance/bin/run-reference-e2e.sh` must exit `0` and end in the literal line
   `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` after this ticket's change, matching the real run
   captured in this ticket's Evidence section.
7. `tickets/OVERLAPS.md` gains a disclosure of this ticket in both the existing
   `appliance/bin/_shared.py` section and the existing
   `appliance/bin (exact_head vs. sha256_file/read_json)` section -- not a new section for
   either, since both already exist and this ticket's claim is additive to each.

## Falsifiers

- `grep -n "^def canonical" appliance/bin/build-subsystem-evidence.py
  appliance/bin/verify-subsystem-evidence.py` still matches either file after this ticket
  executes.
- `appliance/bin/_shared.py` does not exist after this ticket executes, or (if any of
  `GL-EXP-013`/`GL-EXP-017`/`GL-EXP-041` had already run) this ticket's change removed
  `sha256_file`, `read_json`, `write_json`, `tree_inventory`, `tree_digest`, `sha256_bytes`, or
  the untyped `canonical` from it.
- `_shared.py` ends up with two definitions of the same name (a collision between this
  ticket's typed helper and `GL-EXP-041`'s untyped `canonical`).
- `sha256_file`, `exact_head`, `read_json`, or any function other than `canonical` is modified
  in either `build-subsystem-evidence.py` or `verify-subsystem-evidence.py`.
- The 5-file untyped `canonical(obj)` `GL-EXP-041` owns is modified, renamed, or merged with
  this ticket's helper.
- `hashlib.sha256(canonical({"b": 2, "a": 1})).hexdigest()` (old, in-file implementation)
  disagrees with the same call against the `_shared`-imported implementation, for any sample
  input including a non-ASCII string.
- `bash appliance/bin/run-reference-e2e.sh` exits non-zero, or its final stdout line is not
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`.
- `git diff --stat` touches any file outside the Authored boundary above.
- `tickets/OVERLAPS.md`'s existing `appliance/bin/_shared.py` or
  `appliance/bin (exact_head vs. sha256_file/read_json)` section rows for `GL-EXP-013`,
  `GL-EXP-017`, `GL-EXP-023`, or `GL-EXP-041` are altered rather than only appended to.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the duplication before touching anything:
sed -n '/^def canonical/,/^$/p' appliance/bin/build-subsystem-evidence.py | md5
sed -n '/^def canonical/,/^$/p' appliance/bin/verify-subsystem-evidence.py | md5
  # expect: both 02693b06fcb4cdf04afc331ab93686d1

# Reconfirm the two call sites:
grep -n "canonical(manifest)\|canonical(unsigned)" appliance/bin/build-subsystem-evidence.py \
  appliance/bin/verify-subsystem-evidence.py
  # expect: build-subsystem-evidence.py:254, verify-subsystem-evidence.py:167

# Baseline regression proof (record before any change):
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

# After adding/extending appliance/bin/_shared.py and rewriting both files' call sites:
grep -n "^def canonical" appliance/bin/build-subsystem-evidence.py \
  appliance/bin/verify-subsystem-evidence.py
  # expect: zero matches
grep -n "^def canonical\|^def typed_canonical" appliance/bin/_shared.py
  # expect: this ticket's helper present, plus (if landed) GL-EXP-041's untyped canonical(obj), no collision

# Deterministic behavior equivalence:
python3 -c "
import sys, hashlib
sys.path.insert(0, 'appliance/bin')
import _shared as shared
fn = getattr(shared, 'typed_canonical', None) or getattr(shared, 'canonical')
sample = {'b': 2, 'a': 1, 'c': 'non-ascii: \u00e9'}
out = fn(sample)
assert out == b'{\"a\":1,\"b\":2,\"c\":\"non-ascii: \\u00e9\"}'.replace(b'\\\\u00e9', 'é'.encode('utf-8'))
print('typed canonical() behaves as expected:', out)
"

# Regression proof, post-fix:
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

git diff --stat   # only the Authored-boundary files above
```

## Evidence this ticket is grounded in (verified this session)

- `sed -n '/^def canonical/,/^$/p' appliance/bin/build-subsystem-evidence.py | md5` and the
  same on `appliance/bin/verify-subsystem-evidence.py` (run directly this session): both
  produce `02693b06fcb4cdf04afc331ab93686d1` -- byte-identical bodies.
- Direct `Read` of both files' first 30 lines this session: confirmed identical
  `def canonical(value: Any) -> bytes: return json.dumps(value, sort_keys=True,
  separators=(",", ":"), ensure_ascii=False).encode("utf-8")` at line 15 in each.
- `grep -n "^def " appliance/bin/build-subsystem-evidence.py
  appliance/bin/verify-subsystem-evidence.py` (this session): confirms `canonical` at line 15,
  `sha256_file` at line 21, `exact_head` at line 25, `read_json` at line 32 in both files --
  `canonical()`'s region is disjoint from and precedes the regions `GL-EXP-013` (`sha256_file`/
  `read_json`) and `GL-EXP-023` (`exact_head`) already claim.
- `grep -n "canonical(manifest)\|canonical(unsigned)\|hashlib.sha256(canonical"
  appliance/bin/build-subsystem-evidence.py appliance/bin/verify-subsystem-evidence.py` (this
  session): exactly one call site each, at `build-subsystem-evidence.py:254` and
  `verify-subsystem-evidence.py:167`, confirmed live (not dead) by direct `Read` of the
  surrounding context in both files.
- `grep -ln "canonical(value: Any)" tickets/GL-*.md` (this session): exactly one match,
  `tickets/GL-EXP-041.md`.
- Direct `Read` of `tickets/GL-EXP-041.md` lines 138-151 this session: confirmed Hard Law 4
  states verbatim that this typed pair is "explicitly **out of scope**" for that ticket and
  names it "a legitimate, distinct follow-up candidate, not this ticket's job."
- Direct `Read` of `tickets/GL-EXP-041.md`'s Evidence section (lines ~245-255) this session:
  confirmed the prior session's direct Python check (`.encode()` vs. `.encode("utf-8")` on a
  non-ASCII sample) established the typed and untyped implementations are behaviorally
  equivalent -- identical output bytes for identical input.
- `ls appliance/bin/_shared.py` (this session): no such file -- confirmed none of
  `GL-EXP-013`/`GL-EXP-017`/`GL-EXP-041` has executed yet.
- Direct `Read` of `tickets/OVERLAPS.md`'s existing `appliance/bin/_shared.py` section (this
  session): lists `GL-EXP-013`, `GL-EXP-017`, `GL-EXP-041` as the module's three current
  contributors and explicitly states `GL-EXP-041`'s `canonical()` addition excludes this typed
  pair -- confirming the gap is disclosed, not newly discovered by this ticket.
- Direct `Read` of `tickets/OVERLAPS.md`'s existing
  `appliance/bin (exact_head vs. sha256_file/read_json)` section (this session): confirms
  `GL-EXP-013` and `GL-EXP-023` both already claim regions of these same two files
  (`sha256_file`/`read_json` and `exact_head` respectively) -- this ticket's `canonical()`
  claim is a third, disjoint region, requiring its own disclosure in that section.
- `git rev-parse HEAD` (this session): `bce7f6386c4203784beaae426e40804636c4151a`, identical to
  the base commit `GL-EXP-013`/`GL-EXP-017`/`GL-EXP-041` were drafted against.
- `bash appliance/bin/run-reference-e2e.sh` (run directly this session, real subprocess
  execution, not simulated): exit `0`, final stdout line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`, `1.35s user 0.44s system 95% cpu 1.870 total`. This
  harness exercises `appliance/bin/build-subsystem-evidence.py` and
  `appliance/bin/verify-subsystem-evidence.py` directly (both named in `GL-EXP-044`'s own
  12-script enumeration of the harness), so it is the correct regression proof for this
  ticket's change.
- `ls tickets/GL-EXP-045.md` (run before writing this file): confirmed no such file existed.

## Standing

`PARTIAL_ALIVE` — executed 2026-08-21, all Falsifiers re-run for real against the actual
checkout, none tripped.

- `git rev-parse HEAD` re-confirmed `bce7f6386c4203784beaae426e40804636c4151a` before any edit
  — matches this ticket's declared Base, no drift.
- Pre-edit state re-confirmed real, not stale: `appliance/bin/_shared.py` already existed (three
  functions — `sha256_file`, `read_json`, `write_json`; no `canonical`/`typed_canonical`), and
  both target files' `def canonical` sat at line 17 (shifted from the ticket's drafted line 15
  by `GL-EXP-013`'s prior, uncommitted `from _shared import sha256_file, read_json` insertion),
  with call sites at `build-subsystem-evidence.py:248` and `verify-subsystem-evidence.py:161` —
  both re-confirmed live via direct `grep -n`/`Read` this session, exactly as this ticket's own
  drift note predicted. Duplication re-confirmed byte-identical:
  `sed -n '/^def canonical/,/^$/p' <file> | md5` on both files → `02693b06fcb4cdf04afc331ab93686d1`.
- `appliance/bin/_shared.py`: appended `typed_canonical(value: Any) -> bytes`, byte-for-byte the
  same body as the deleted `canonical()`, under the ticket-mandated distinguishing name (Hard
  Law 1). Also added `from typing import Any` to `_shared.py`'s imports — required to preserve
  the typed signature verbatim, since `_shared.py` had no prior `Any` import.
  `grep -n "^def " appliance/bin/_shared.py` shows exactly four functions (`sha256_file`,
  `read_json`, `write_json`, `typed_canonical`), the prior three untouched.
- Both files' private `def canonical` (line 17) deleted outright; both now
  `from _shared import sha256_file, read_json, typed_canonical` (Hard Law 2). Both call sites
  rewritten to call `typed_canonical(...)` by name, not aliased (Hard Law 3):
  `build-subsystem-evidence.py:242` `hashlib.sha256(typed_canonical(manifest)).hexdigest()`;
  `verify-subsystem-evidence.py:155` `hashlib.sha256(typed_canonical(unsigned)).hexdigest()`.
  `grep -n "^def canonical" appliance/bin/build-subsystem-evidence.py
  appliance/bin/verify-subsystem-evidence.py`: zero matches, as required.
- Behavioral equivalence re-checked directly, old in-file body vs. the `_shared`-imported
  `typed_canonical`, across three sample inputs including a non-ASCII string (`{'b':2,'a':1}`,
  `{'b':2,'a':1,'c':'non-ascii: é'}`, a nested dict/list/None sample): identical SHA-256 digests
  in every case. The ticket's own Acceptance Python snippet (dict with a non-ASCII value) was
  also run directly and produced the expected byte string.
  `python3 -m py_compile` on all three edited files: clean.
- `sha256_file`, `exact_head`, `read_json`, `digest_sources`, `check_map`, and the untyped
  5-file `canonical(obj)` `GL-EXP-041` owns: confirmed untouched — content-diff of the two edited
  files shows only the deleted `def canonical` block, one rewritten `from _shared import` line,
  and one rewritten call-site line each; `GL-EXP-041`'s own file was not opened for writing.
- `bash appliance/bin/run-reference-e2e.sh`, run once as a pre-change baseline and once
  post-change: both exited `0` and ended in the literal line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` — no behavioral regression (Hard Law 6).
- `git diff --stat -- appliance/bin/build-subsystem-evidence.py
  appliance/bin/verify-subsystem-evidence.py`: exactly these two Authored-boundary files, 6
  insertions(+), 30 deletions(-) total (the removal of the 4-line `def canonical` block plus the
  one-word import/call-site rewrites in each file), no other file under `appliance/bin/`
  touched by this ticket's own edits. `appliance/bin/_shared.py` and `tickets/OVERLAPS.md` are
  untracked working-tree files (not yet committed by any of `GL-EXP-013`/`017`/`041`/`045`), so
  their changes show in `git status`, not in tracked-file `git diff` — consistent with
  `GL-EXP-013`'s own precedent for this same not-yet-committed module.
  Repo-wide `git status --porcelain -uall | wc -l` = 113 at execution time, matching the ambient
  multi-ticket uncommitted working-tree state `GL-EXP-013`'s Standing section already
  documented (not evidence against this ticket's own scoped diff).
- `tickets/OVERLAPS.md` updated: the `appliance/bin/_shared.py` and `appliance/bin` (`exact_head`
  vs. `sha256_file`/`read_json`) sections' existing `GL-EXP-045` rows (pre-drafted at ticket-write
  time) updated from `NOT_STARTED` to `EXECUTED` with real per-function evidence; only this
  ticket's own rows and the shared "Reconciled" summary text were edited — `GL-EXP-013`'s,
  `GL-EXP-017`'s, `GL-EXP-023`'s, and `GL-EXP-041`'s own bullet rows were left byte-for-byte
  untouched (Hard Law 7 / final Falsifier).

Executing this ticket end-to-end (adding `typed_canonical` to `appliance/bin/_shared.py`,
rewriting both files' one call site each, re-running the "Acceptance" commands with real output,
and disclosing in `tickets/OVERLAPS.md`) is complete. `PARTIAL_ALIVE` (not full `ALIVE`) because,
as with `GL-EXP-013`, this remains an uncommitted working-tree change — no merge authority per
this ticket's Publication boundary, and `just ci-all` was not re-run as part of this ticket
(out of scope; not named in this ticket's Hard Laws or Falsifiers).
