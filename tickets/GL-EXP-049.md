# GL-EXP-049 — Consolidate the byte-identical `digest_sources()`/`check_map()` duplicates in `appliance/bin/build-subsystem-evidence.py`/`verify-subsystem-evidence.py` into `_shared.py`

**Status:** `EXECUTED` 2026-08-21 -- real fix landed in the main checkout and re-verified
there (was `admitted, NOT_STARTED`, drafted by standing ultracode exploration cron).

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`appliance/bin/build-subsystem-evidence.py` and `appliance/bin/verify-subsystem-evidence.py`
each define two identical helpers, `digest_sources()` and `check_map()`, at the same line
numbers in both files (confirmed this session):

```text
appliance/bin/build-subsystem-evidence.py:24:def digest_sources(root: Path, sources: list[str]) -> tuple[str, list[str]]:
appliance/bin/build-subsystem-evidence.py:40:def check_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
appliance/bin/verify-subsystem-evidence.py:24:def digest_sources(root: Path, sources: list[str]) -> tuple[str, list[str]]:
appliance/bin/verify-subsystem-evidence.py:40:def check_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
```

```python
def digest_sources(root: Path, sources: list[str]) -> tuple[str, list[str]]:
    digest = hashlib.sha256()
    missing: list[str] = []
    for rel in sorted(sources):
        path = root / rel
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        if path.is_file():
            digest.update(path.read_bytes())
        else:
            missing.append(rel)
            digest.update(b"MISSING")
        digest.update(b"\0")
    return digest.hexdigest(), missing


def check_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in report.get("checks", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
```

Confirmed byte-identical this session: `sed -n '/^def digest_sources/,/^$/p' <file> | md5` on
both files -> identical hash `7e5fd2e7826bec2300dcdfacbdac0f64`. Same check for `check_map` ->
identical hash `e226b84faa099e4493cc8811fee3d5ca`.

Both are live, not dead code. `digest_sources()` has 2 call sites in each file:
`build-subsystem-evidence.py:186,189` and `verify-subsystem-evidence.py:192,195`. `check_map()`
has 3 call sites in each file: `build-subsystem-evidence.py:121,132,182` and
`verify-subsystem-evidence.py:90,96,132` — confirmed via `grep -n "digest_sources\|check_map"`
on both files this session, all inside live control flow (`primary_result()`/`main()` in the
build script, `expected_primary()`/`main()` in the verify script), not commented out or
unreachable.

This is the same file pair, and the same `_shared.py` module, that `GL-EXP-013` (`EXECUTED`
2026-08-21) and `GL-EXP-017` (`EXECUTED` 2026-08-21) already consolidated `sha256_file()` /
`read_json()` / `write_json()` into, and that `GL-EXP-045` (`EXECUTED` 2026-08-21) most recently
extended with `typed_canonical()` — this ticket's `digest_sources()`/`check_map()` pair is the
one remaining disjoint, unconsolidated duplication left in this same pair of files.
`digest_sources()`/`check_map()` are explicitly named, and explicitly excluded from that
ticket's own scope, in `GL-EXP-045`'s Authored boundary text: "No change to `sha256_file`,
`exact_head`, `read_json`, `digest_sources`, `check_map`, or any other function in either file."
(`tickets/GL-EXP-045.md:93-94`, read in full this session.) `grep -n "digest_sources\|check_map"
tickets/GL-EXP-041.md` (this session) also returns no match — `GL-EXP-041` (`NOT_STARTED`),
which adds `tree_inventory()`/`tree_digest()`/`sha256_bytes()`/`canonical()` to the same module,
does not touch this pair either.

`grep -iln "digest_sources\|check_map" tickets/GL-*.md` (this session): exactly one match,
`tickets/GL-EXP-045.md` — read in full, its text only disclaims scope over these two names, it
does not claim them. `grep -n "digest_sources\|check_map" tickets/OVERLAPS.md` (this session):
zero matches — no existing registry row for either name.

`ls appliance/bin/_shared.py` (this session): the file exists (created by `GL-EXP-013`,
extended by `GL-EXP-017` and `GL-EXP-045`) and currently holds exactly four functions —
`sha256_file`, `read_json`, `write_json`, `typed_canonical` (`grep -n "^def "
appliance/bin/_shared.py`, this session). This ticket is a fifth, independent contributor,
adding exactly two functions (`digest_sources`, `check_map`, verbatim names — neither collides
with any function already in the module or with any name `GL-EXP-041`, still `NOT_STARTED`,
plans to add).

`ls tickets/GL-EXP-049.md` (run before writing this file): confirmed no such file existed —
this pre-assigned id was free.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — checked there and
against every existing `GL-EXP-*.md`'s Authored boundary before writing this section.
`appliance/bin/_shared.py` is already claimed by `GL-EXP-013`/`GL-EXP-017`/`GL-EXP-041`/
`GL-EXP-045` in the registry's existing `appliance/bin/_shared.py` section — this ticket appends
its disclosure there. `appliance/bin/build-subsystem-evidence.py` and
`appliance/bin/verify-subsystem-evidence.py` are already claimed by `GL-EXP-013`
(`sha256_file`/`read_json`), `GL-EXP-023` (`exact_head`, still `NOT_STARTED`), and `GL-EXP-045`
(`typed_canonical`/`canonical`) in the registry's existing `appliance/bin (exact_head vs.
sha256_file/read_json)` section — this ticket's own claim, `digest_sources()`/`check_map()` at
lines 24/40 in both files, is a fourth, disjoint region (it follows `exact_head()` at line 17
and precedes `primary_result()`/`expected_primary()` at line 48 in both files), so this write
adds a new disclosure to that same section rather than a new one.)

```text
appliance/bin/_shared.py                    # append digest_sources() and check_map() (module already exists per GL-EXP-013/017/045)
appliance/bin/build-subsystem-evidence.py   # delete private digest_sources() (line 24) and check_map() (line 40), import shared, rewrite the 5 call sites (lines 121,132,182,186,189)
appliance/bin/verify-subsystem-evidence.py  # delete private digest_sources() (line 24) and check_map() (line 40), import shared, rewrite the 5 call sites (lines 90,96,132,192,195)
tickets/GL-EXP-049.md
tickets/OVERLAPS.md                         # append disclosure to the existing `appliance/bin/_shared.py` and `appliance/bin (exact_head vs. sha256_file/read_json)` sections
```

No change to `sha256_file`, `exact_head`, `read_json`, `write_json`, `typed_canonical`, or any
other function in either file. No change to the 5-file untyped `canonical(obj)` `GL-EXP-041`
still owns (`NOT_STARTED`), or to `GL-EXP-023`'s (`NOT_STARTED`) `exact_head()` claim. No change
to `appliance/bin/run-reference-e2e.sh` itself.

## Hard laws

1. `appliance/bin/_shared.py` gains exactly two new helpers for this ticket, byte-for-byte
   matching the bodies already shared by both files (md5 hashes cited in Outcome), under their
   existing names `digest_sources(root: Path, sources: list[str]) -> tuple[str, list[str]]` and
   `check_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]` — neither name collides with
   any function already in `_shared.py` (`sha256_file`, `read_json`, `write_json`,
   `typed_canonical`) or with any name `GL-EXP-041` (still `NOT_STARTED`) plans to add
   (`tree_inventory`, `tree_digest`, `sha256_bytes`, `canonical`).
2. Both files' private `def digest_sources` (line 24) and `def check_map` (line 40) are deleted
   outright and replaced with an import from `_shared`.
3. Every call site in each file (`build-subsystem-evidence.py:121,132,182,186,189`;
   `verify-subsystem-evidence.py:90,96,132,192,195`) is rewritten to call the imported name;
   external behavior is unchanged — same digest hex string / missing-file list for
   `digest_sources()`, same id-keyed dict for `check_map()`, for identical input.
4. The 5-file untyped `canonical(obj)` `GL-EXP-041` owns, and the `typed_canonical()`/
   `sha256_file`/`read_json`/`write_json` helpers already in `_shared.py`, are explicitly out of
   scope — not touched, not merged with, not renamed by this ticket.
5. If `appliance/bin/_shared.py`'s current four functions have changed by execution time (e.g.
   `GL-EXP-041` has landed), this ticket appends its two helpers without modifying any sibling's
   addition. No ticket may overwrite or truncate another's contribution to `_shared.py`.
6. `appliance/bin/run-reference-e2e.sh` must exit `0` and end in the literal line
   `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` after this ticket's change, matching the real baseline
   run captured in this ticket's Evidence section.
7. `tickets/OVERLAPS.md` gains a disclosure of this ticket in both the existing
   `appliance/bin/_shared.py` section and the existing `appliance/bin (exact_head vs.
   sha256_file/read_json)` section — not a new section for either, since both already exist and
   this ticket's claim is additive to each.

## Falsifiers

- `grep -n "^def digest_sources\|^def check_map" appliance/bin/build-subsystem-evidence.py
  appliance/bin/verify-subsystem-evidence.py` still matches either file after this ticket
  executes.
- `appliance/bin/_shared.py` does not exist after this ticket executes, or this ticket's change
  removed `sha256_file`, `read_json`, `write_json`, `typed_canonical`, or any other pre-existing
  function from it.
- `_shared.py` ends up with two definitions of the same name (a collision between this ticket's
  helpers and any sibling ticket's addition).
- `sha256_file`, `exact_head`, `read_json`, `write_json`, `typed_canonical`, or any function
  other than `digest_sources`/`check_map` is modified in either
  `build-subsystem-evidence.py` or `verify-subsystem-evidence.py`.
- The 5-file untyped `canonical(obj)` `GL-EXP-041` owns is modified, renamed, or merged with
  this ticket's helpers.
- `digest_sources()` or `check_map()`, called against a representative sample input, returns a
  different result (digest hex string, missing-file list, or id-keyed dict) from the old,
  in-file implementation vs. the `_shared`-imported implementation.
- `bash appliance/bin/run-reference-e2e.sh` exits non-zero, or its final stdout line is not
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`.
- `git diff --stat` touches any file outside the Authored boundary above.
- `tickets/OVERLAPS.md`'s existing `appliance/bin/_shared.py` or `appliance/bin (exact_head vs.
  sha256_file/read_json)` section rows for `GL-EXP-013`, `GL-EXP-017`, `GL-EXP-023`,
  `GL-EXP-041`, or `GL-EXP-045` are altered rather than only appended to.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the duplication before touching anything:
sed -n '/^def digest_sources/,/^$/p' appliance/bin/build-subsystem-evidence.py | md5
sed -n '/^def digest_sources/,/^$/p' appliance/bin/verify-subsystem-evidence.py | md5
  # expect: both 7e5fd2e7826bec2300dcdfacbdac0f64
sed -n '/^def check_map/,/^$/p' appliance/bin/build-subsystem-evidence.py | md5
sed -n '/^def check_map/,/^$/p' appliance/bin/verify-subsystem-evidence.py | md5
  # expect: both e226b84faa099e4493cc8811fee3d5ca

# Reconfirm all call sites:
grep -n "digest_sources\|check_map" appliance/bin/build-subsystem-evidence.py \
  appliance/bin/verify-subsystem-evidence.py
  # expect: 8 lines total per file (2 def lines + 5/6 call-site lines each, per Outcome)

# Baseline regression proof (record before any change):
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

# After extending appliance/bin/_shared.py and rewriting both files' call sites:
grep -n "^def digest_sources\|^def check_map" appliance/bin/build-subsystem-evidence.py \
  appliance/bin/verify-subsystem-evidence.py
  # expect: zero matches
grep -n "^def " appliance/bin/_shared.py
  # expect: prior functions untouched, plus digest_sources and check_map, no collision

# Deterministic behavior equivalence (sample input, run against both old and new implementation
# before deleting the old one):
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'appliance/bin')
import _shared as shared
digest, missing = shared.digest_sources(Path('.'), ['README.md', 'CLAUDE.md', 'does-not-exist.xyz'])
assert isinstance(digest, str) and len(digest) == 64
assert missing == ['does-not-exist.xyz']
cm = shared.check_map({'checks': [{'id': 'a', 'passed': True}, {'id': 'b', 'passed': False}]})
assert cm == {'a': {'id': 'a', 'passed': True}, 'b': {'id': 'b', 'passed': False}}
print('digest_sources() and check_map() behave as expected')
"

# Regression proof, post-fix:
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

git diff --stat   # only the Authored-boundary files above
```

## Evidence this ticket is grounded in (verified this session)

- `grep -n "^def digest_sources\|^def check_map" appliance/bin/*.py` (run directly this
  session): returns exactly these 2 files for each name, both at line 24 (`digest_sources`) and
  line 40 (`check_map`).
- `sed -n '/^def digest_sources/,/^$/p' <file> | md5` on both files (run directly this session):
  both produce `7e5fd2e7826bec2300dcdfacbdac0f64` — byte-identical bodies. Same check for
  `check_map` produces `e226b84faa099e4493cc8811fee3d5ca` on both files.
- `grep -n "digest_sources\|check_map" appliance/bin/build-subsystem-evidence.py
  appliance/bin/verify-subsystem-evidence.py` (this session): confirms `digest_sources()` has 2
  live call sites in each file (`build-subsystem-evidence.py:186,189`;
  `verify-subsystem-evidence.py:192,195`) and `check_map()` has 3 live call sites in each
  (`build-subsystem-evidence.py:121,132,182`; `verify-subsystem-evidence.py:90,96,132`).
- `grep -n "^def \|^from _shared" appliance/bin/build-subsystem-evidence.py
  appliance/bin/verify-subsystem-evidence.py` (this session): confirms current function layout
  in both files — `from _shared import sha256_file, read_json, typed_canonical` (line 11),
  `exact_head` (line 17), `digest_sources` (line 24), `check_map` (line 40), then the
  build/verify-specific logic (`primary_result`/`negative_result`/`main` in the build script,
  `expected_primary`/`expected_negative`/`main` in the verify script) — this ticket's claim is
  disjoint from and between `GL-EXP-023`'s (`exact_head`) and `GL-EXP-013`'s
  (`sha256_file`/`read_json`, now an import) claimed regions.
- `grep -iln "digest_sources\|check_map" tickets/GL-*.md` (this session): exactly one match,
  `tickets/GL-EXP-045.md`.
- Direct `Read` of `tickets/GL-EXP-045.md` (this session): confirmed its Authored boundary text
  states verbatim "No change to `sha256_file`, `exact_head`, `read_json`, `digest_sources`,
  `check_map`, or any other function in either file" (`tickets/GL-EXP-045.md:93-94`) — disclaims
  scope over these two names, does not claim them.
- `grep -n "digest_sources\|check_map" tickets/GL-EXP-041.md` (this session): zero matches —
  `GL-EXP-041` (still `NOT_STARTED`) does not touch this pair either.
- `grep -n "digest_sources\|check_map" tickets/OVERLAPS.md` (this session): zero matches — no
  existing registry row for either name.
- `head -5 tickets/GL-EXP-013.md tickets/GL-EXP-017.md tickets/GL-EXP-023.md
  tickets/GL-EXP-041.md tickets/GL-EXP-045.md` (this session): confirmed real current statuses —
  `GL-EXP-013` `EXECUTED` 2026-08-21, `GL-EXP-017` `EXECUTED` 2026-08-21, `GL-EXP-023`
  `NOT_STARTED`, `GL-EXP-041` `NOT_STARTED`, `GL-EXP-045` `EXECUTED` 2026-08-21.
- `ls appliance/bin/_shared.py` + `Read` of its full contents (this session): file exists,
  holds exactly four functions (`sha256_file`, `read_json`, `write_json`, `typed_canonical`),
  confirming `GL-EXP-013`/`GL-EXP-017`/`GL-EXP-045`'s executed state and that `GL-EXP-041`'s
  additions have not yet landed.
- Direct `Read` of `tickets/OVERLAPS.md`'s existing `appliance/bin/_shared.py` and
  `appliance/bin (exact_head vs. sha256_file/read_json)` sections (this session): confirmed the
  current registry rows for `GL-EXP-013`/`GL-EXP-017`/`GL-EXP-023`/`GL-EXP-041`/`GL-EXP-045`,
  none of which claims `digest_sources`/`check_map` — this ticket's claim is a genuine,
  previously-undisclosed gap, not a duplicate of an existing row.
- `git rev-parse HEAD` (this session): `bce7f6386c4203784beaae426e40804636c4151a`.
- `bash appliance/bin/run-reference-e2e.sh` (run directly this session, real subprocess
  execution, not simulated): exit `0`, stdout ending
  `{"standing": "ALIVE", "subsystems": 10}` / `{"checks": 10, "coverage_unchanged": true,
  "standing": "ALIVE"}` / `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`. This harness exercises
  `appliance/bin/build-subsystem-evidence.py` and `appliance/bin/verify-subsystem-evidence.py`
  directly, so it is the correct regression proof for this ticket's change.
- `ls tickets/GL-EXP-049.md` (run before writing this file): confirmed no such file existed.

## Standing

`PARTIAL_ALIVE` — executed 2026-08-21, all Falsifiers re-run for real against the actual
checkout, none tripped.

- `git rev-parse HEAD` re-confirmed `bce7f6386c4203784beaae426e40804636c4151a` before any edit
  — matches this ticket's declared Base, no drift.
- Pre-edit state re-confirmed real, not stale: both target files' `def digest_sources` (line 24)
  and `def check_map` (line 40) re-confirmed byte-identical —
  `sed -n '/^def digest_sources/,/^$/p' <file> | md5` → `7e5fd2e7826bec2300dcdfacbdac0f64` on
  both files; same check for `check_map` → `e226b84faa099e4493cc8811fee3d5ca` on both files. All
  10 call sites re-confirmed live via direct `grep -n` this session at the exact lines this
  ticket's Outcome section names.
- `bash appliance/bin/run-reference-e2e.sh` run as a pre-change baseline: exit `0`, final line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`.
- `appliance/bin/_shared.py`: appended `digest_sources(root: Path, sources: list[str]) ->
  tuple[str, list[str]]` and `check_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]`,
  byte-for-byte the same bodies as the deleted private definitions, under their existing names
  (Hard Law 1). `grep -n "^def " appliance/bin/_shared.py` shows exactly six functions
  (`sha256_file`, `read_json`, `write_json`, `typed_canonical`, `digest_sources`, `check_map`),
  the prior four untouched, no collision.
- Both files' private `def digest_sources` (line 24) and `def check_map` (line 40) deleted
  outright; both now `from _shared import sha256_file, read_json, typed_canonical,
  digest_sources, check_map` (Hard Law 2). `grep -n "^def digest_sources\|^def check_map"
  appliance/bin/build-subsystem-evidence.py appliance/bin/verify-subsystem-evidence.py`: zero
  matches, as required.
- Every call site (`build-subsystem-evidence.py:121,132,182,186,189` (now at 97,108,158,162,165
  post-deletion); `verify-subsystem-evidence.py:90,96,132,192,195` (now at 66,72,108,168,171
  post-deletion)) already called the bare names `digest_sources(...)`/`check_map(...)` with no
  module-qualification, so importing those exact names from `_shared` left every call site
  textually identical — confirmed via `grep -n "digest_sources\|check_map"` on both post-edit
  files, showing the same 5 call-site lines each, unchanged in form, now resolving through the
  import (Hard Law 3, "external behavior is unchanged").
- Behavioral equivalence checked directly, the reconstructed old in-file bodies (md5-verified
  identical to what was deleted) vs. the `_shared`-imported implementations, across 3 sample
  inputs for `digest_sources()` (including a missing file and an empty source list) and 4 sample
  inputs for `check_map()` (including an empty/absent `checks` list and non-dict entries):
  identical results in every case. The ticket's own Acceptance Python snippet was also run
  directly against `_shared.digest_sources`/`_shared.check_map` and produced the expected
  digest length, missing-file list, and id-keyed dict.
- `sha256_file`, `exact_head`, `read_json`, `write_json`, `typed_canonical`, and the untyped
  5-file `canonical(obj)` `GL-EXP-041` owns: confirmed untouched — `git diff --stat` on the two
  edited files shows only the deleted `def digest_sources`/`def check_map` blocks and one
  rewritten `from _shared import` line each, no call-site line rewrites (none were needed);
  `GL-EXP-041`'s own file was not opened for writing.
- `bash appliance/bin/run-reference-e2e.sh`, run once as a pre-change baseline and once
  post-change: both exited `0` and ended in the literal line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` — no behavioral regression (Hard Law 6).
- `git diff --stat -- appliance/bin/build-subsystem-evidence.py
  appliance/bin/verify-subsystem-evidence.py`: exactly these two Authored-boundary files, 6
  insertions(+), 78 deletions(-) total (the removal of the two def blocks plus the
  import-line rewrite in each file), no other file under `appliance/bin/` touched by this
  ticket's own edits. `appliance/bin/_shared.py`, `tickets/OVERLAPS.md`, and this ticket file
  itself are untracked working-tree files (not yet committed by any of
  `GL-EXP-013`/`017`/`041`/`045`), so their changes show in `git status`, not in tracked-file
  `git diff` — consistent with `GL-EXP-013`'s own precedent for this same not-yet-committed
  module. Repo-wide `git status --porcelain -uall | wc -l` = 117 at execution time, matching the
  ambient multi-ticket uncommitted working-tree state `GL-EXP-013`'s Standing section already
  documented (not evidence against this ticket's own scoped diff).
- `tickets/OVERLAPS.md` updated: the `appliance/bin/_shared.py` and `appliance/bin` (`exact_head`
  vs. `sha256_file`/`read_json`) sections' existing `GL-EXP-049` rows (pre-drafted at ticket-write
  time) updated from `NOT_STARTED` to `EXECUTED` with real per-function evidence; only this
  ticket's own rows and the shared "Reconciled" summary text were edited — `GL-EXP-013`'s,
  `GL-EXP-017`'s, `GL-EXP-023`'s, and `GL-EXP-041`'s own bullet rows were left byte-for-byte
  untouched (Hard Law 7 / final Falsifier).

Executing this ticket end-to-end (adding `digest_sources`/`check_map` to
`appliance/bin/_shared.py`, rewriting both files' imports (call sites required no textual
change), re-running the "Acceptance" commands with real output, and disclosing in
`tickets/OVERLAPS.md`) is complete. `PARTIAL_ALIVE` (not full `ALIVE`) because, as with
`GL-EXP-013`/`GL-EXP-045`, this remains an uncommitted working-tree change — no merge authority
per this ticket's Publication boundary, and `just ci-all` was not re-run as part of this ticket
(out of scope; not named in this ticket's Hard Laws or Falsifiers).
