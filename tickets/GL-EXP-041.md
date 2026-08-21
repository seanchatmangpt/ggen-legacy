# GL-EXP-041 — Consolidate the duplicated `tree_inventory()`/`tree_digest()`/`sha256_bytes()`/`canonical()` helpers in `appliance/bin/`

**Status:** admitted, `NOT_STARTED` — drafted by standing ultracode exploration cron

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`grep -n "^def tree_inventory\|^def tree_digest\|^def canonical" appliance/bin/*.py` (run
directly this session) shows `tree_inventory`/`tree_digest` each defined in exactly 5 files —
`build-standing-portfolio.py`, `decision-engine.py`, `replay-standing-portfolio.py`,
`transparency-log.py`, `verify-standing-portfolio.py` — the identical 5-file set
`GL-EXP-013`/`GL-EXP-017` already consolidate `sha256_file`/`read_json`/`write_json` for.
Direct body extraction + `md5` (`sed -n '/^def NAME/,/^$/p' <file> | md5`, run this session)
confirms byte-identical bodies across all 5 files for `tree_inventory`
(`2717417bed0624eaa9db6fdc0115bc7b`) and `tree_digest` (`92df102403d2ce858f15517b3f94e34c`).
`grep -n "^def sha256_bytes" appliance/bin/*.py` confirms the same 5-file set for
`sha256_bytes`, all reading the identical one-liner
`def sha256_bytes(data): return hashlib.sha256(data).hexdigest()` (confirmed via
`grep -h "^def sha256_bytes" appliance/bin/*.py | sort -u` returning exactly one distinct
line). All three helpers are live in every one of the 5 files: `tree_inventory` is called at
least once in each (line 25, sometimes also 35); `sha256_bytes` is called in each (inside
`tree_digest`'s own body at minimum, plus `build-standing-portfolio.py` lines 41/44/45/66 and
`transparency-log.py` lines 37/46).

**Correction to the originating exploration candidate's evidence, made this session**: the
candidate claimed `canonical()` "each return exactly 5 matches" identically to the other three
helpers. Re-running the cited grep directly this session shows `canonical` actually appears in
**7** files, not 5, with **two distinct, non-identical implementations**:

- The same 5-file set above (`build-standing-portfolio.py`, `decision-engine.py`,
  `replay-standing-portfolio.py`, `transparency-log.py`, `verify-standing-portfolio.py`) all
  define the untyped one-liner
  `def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(",", ":"),
  ensure_ascii=False).encode()` — confirmed byte-identical across all 5 via
  `sed -n '/^def canonical/,/^$/p' <file> | md5` → `63fabc6505931c141f8441ad427f82fd` on all 5.
- `build-subsystem-evidence.py:15` and `verify-subsystem-evidence.py:15` instead define a
  **different**, typed implementation —
  `def canonical(value: Any) -> bytes: return json.dumps(value, sort_keys=True,
  separators=(",", ":"), ensure_ascii=False).encode("utf-8")` — confirmed identical to each
  other (`md5` → `02693b06fcb4cdf04afc331ab93686d1` on both) but **not** identical source to
  the 5-file version (explicit `Any`/`-> bytes` typing, explicit `"utf-8"` argument to
  `.encode()` vs. the 5-file version's bare `.encode()`). A direct Python check this session
  (`json.dumps(sample, sort_keys=True, separators=(",", ":"),
  ensure_ascii=False).encode()` vs. `...encode("utf-8")` on the same non-ASCII sample object)
  confirms the two implementations are **behaviorally equivalent** — identical output bytes
  for identical input, since `.encode()` already defaults to UTF-8 — but they are not the
  literal byte-for-byte duplicate the candidate's evidence claimed, and the 2 extra files are
  not part of the 5-file set this ticket (and its two siblings) target. This ticket therefore
  scopes `canonical()` consolidation to the same 5 files as the other three helpers, and
  explicitly excludes `build-subsystem-evidence.py`/`verify-subsystem-evidence.py`'s own typed
  `canonical()` — see Hard Law 4 and Falsifiers below. Treating a behaviorally-equivalent,
  differently-typed function as a literal duplicate would have been scope creep past what a
  like-for-like consolidation can safely claim.

Per-file `canonical()` call-site counts (`grep -n "canonical(" <file>`, run this session,
excluding each file's own `def` line): `build-standing-portfolio.py` — 2 call sites (lines
45, 66, e.g. `receipt["receipt_hash"]=sha256_bytes(canonical(receipt))` at line 66);
`transparency-log.py` — 2 call sites (lines 37, 46, e.g.
`entry["entry_hash"]=sha256_bytes(canonical(entry))` at line 46); `decision-engine.py`,
`replay-standing-portfolio.py`, `verify-standing-portfolio.py` — **0 call sites each**
(`canonical` is defined in all three but never invoked, confirmed by reading each file in
full this session — genuinely dead code in 3 of the 5 files, the same class of finding
`GL-EXP-017` already made for `write_json` in `transparency-log.py`). `tree_digest` is
similarly unevenly called: live in `build-standing-portfolio.py:70` (embedded in a
`print(json.dumps({...,"tree_digest":tree_digest(out),...}))` call),
`replay-standing-portfolio.py:36` (`d1=tree_digest(p1); d2=tree_digest(p2)`), and
`verify-standing-portfolio.py:71`, but **never called** in `decision-engine.py` or
`transparency-log.py` — dead code in those 2 for `tree_digest` specifically, even though
`tree_inventory` (which `tree_digest` itself calls) is live in both via its own line-25 call
site.

`grep -l "tree_inventory\|tree_digest\|canonical\|sha256_bytes" tickets/*.md` was not needed
to establish scope: `GL-EXP-013.md`'s and `GL-EXP-017.md`'s own `## Falsifiers` sections
(`grep -n "tree_inventory\|tree_digest\|canonical\|sha256_bytes"` on each, run this session)
both list all four names verbatim as paths their own `git diff --stat` must **not** touch —
confirming both siblings deliberately left these four helpers out, not merely omitted them by
oversight. `grep -n "tree_inventory\|tree_digest\|canonical\|sha256_bytes"
tickets/OVERLAPS.md` (run this session) returns zero matches for the functions themselves (the
one substring hit, "canonical registry"/"canonical copy", is the unrelated English word, not
this function) — no existing registry row. `ls tickets/GL-EXP-041.md` (run before this file was
written) confirmed the id was free.

This ticket consolidates `tree_inventory()`, `tree_digest()`, `sha256_bytes()`, and
`canonical()` (the 5-file untyped variant only) into `appliance/bin/_shared.py` — the same
module `GL-EXP-013` (`sha256_file`/`read_json`) and `GL-EXP-017` (`write_json`) already target,
both still `NOT_STARTED` (`ls appliance/bin/_shared.py` this session: no such file — neither
sibling has executed yet). Because three tickets now independently claim the same new module,
this ticket follows the same append-only ordering discipline `GL-EXP-017`'s Hard Law 3 already
established for itself and `GL-EXP-013`, extended to a third ticket — see Hard Law 5 and the
new `tickets/OVERLAPS.md` section this ticket adds.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before
assuming sole ownership of a path below. `grep -n "_shared.py" tickets/OVERLAPS.md` returns no
existing section as of this session, even though `GL-EXP-013`'s and `GL-EXP-017`'s own
Authored-boundary text each say they will add one — neither has executed, so neither actually
did. This ticket adds the first real `_shared.py` section, disclosing all three tickets'
claims.)

```text
appliance/bin/_shared.py                    # add tree_inventory(), tree_digest(), sha256_bytes(), canonical() (create the file if neither GL-EXP-013 nor GL-EXP-017 has run yet; append otherwise)
appliance/bin/build-standing-portfolio.py   # delete private tree_inventory/tree_digest/sha256_bytes/canonical, import shared, rewrite call sites
appliance/bin/decision-engine.py            # delete private tree_inventory/tree_digest/sha256_bytes/canonical (canonical + tree_digest: dead, no call sites to rewrite), import shared
appliance/bin/replay-standing-portfolio.py  # delete private tree_inventory/tree_digest/sha256_bytes/canonical (canonical: dead, no call sites to rewrite), import shared, rewrite tree_digest call sites
appliance/bin/transparency-log.py           # delete private tree_inventory/tree_digest/sha256_bytes/canonical (tree_digest: dead, no call sites to rewrite), import shared, rewrite canonical/sha256_bytes call sites
appliance/bin/verify-standing-portfolio.py  # delete private tree_inventory/tree_digest/sha256_bytes/canonical (canonical: dead, no call sites to rewrite), import shared, rewrite tree_digest call sites
tickets/GL-EXP-041.md
tickets/OVERLAPS.md                         # add new `appliance/bin/_shared.py` section disclosing GL-EXP-013 + GL-EXP-017 + GL-EXP-041's shared claim on the module
```

No change to `appliance/bin/build-subsystem-evidence.py` or
`appliance/bin/verify-subsystem-evidence.py` — both define a differently-typed, non-identical
`canonical()` (see Outcome's correction above); this ticket does not touch, consolidate, or
re-point either to `_shared.py`. No change to `appliance/bin/build-document-evidence-index.py`,
`appliance/bin/project-subsystem-coverage.py`, `appliance/bin/verify-crown.py`,
`appliance/bin/cross-check-portfolio.py`, or `appliance/bin/observe-project.py` (none defines
any of `tree_inventory`/`tree_digest`/`sha256_bytes`/`canonical` — confirmed via the grep
above, which returns matches only in the 5+2 files already named). No change to
`GL-EXP-013`'s own `sha256_file`/`read_json` logic, `GL-EXP-017`'s own `write_json` logic,
`GL-ERRC-010`'s `transparency-log.py` `verify()` `--anchor` mode, or `GL-RECEIPT-007`'s
`build-standing-portfolio.py` SLSA/DSSE projection — this ticket touches only the four named
helper definitions and their call sites. No change to `appliance/bin/run-reference-e2e.sh`
itself (it only invokes the scripts).

## Hard laws

1. `appliance/bin/_shared.py` gains exactly four new canonical helpers —
   `tree_inventory(root)`, `tree_digest(root)`, `sha256_bytes(data)`, and `canonical(obj)` —
   byte-for-byte matching the bodies already shared by the 5 files today (md5s cited in
   Outcome). No new hashing algorithm, no new tree-walking behavior, no new serialization
   behavior.
2. All 5 files' private `def tree_inventory`, `def tree_digest`, `def sha256_bytes`, and
   `def canonical` are deleted outright (not deprecated, not left dead) and replaced with an
   import from `_shared`. Where a helper has zero call sites in a given file today
   (`canonical` in `decision-engine.py`/`replay-standing-portfolio.py`/
   `verify-standing-portfolio.py`; `tree_digest` in `decision-engine.py`/
   `transparency-log.py`), the import is added for consistency (matching `GL-EXP-013`'s
   pattern of importing all consolidated names uniformly) but no new call site is introduced.
3. Every call site's external behavior is unchanged: same digest for the same tree contents,
   same bytes for the same input, same exceptions on missing/malformed input.
4. `appliance/bin/build-subsystem-evidence.py`'s and
   `appliance/bin/verify-subsystem-evidence.py`'s own typed `canonical(value: Any) -> bytes`
   is explicitly **out of scope** — not touched, not consolidated, not re-pointed to
   `_shared.py`. It is behaviorally equivalent to the 5-file version (verified this session)
   but not the same source, and unifying differently-typed call signatures across files with a
   different type-hinting convention (`from typing import Any` present vs. absent) is a
   legitimate, distinct follow-up candidate, not this ticket's job.
5. If `appliance/bin/_shared.py` already exists when this ticket executes (`GL-EXP-013` and/or
   `GL-EXP-017` ran first), this ticket **appends** its four helpers without modifying
   `sha256_file`, `read_json`, or `write_json`. If `_shared.py` does not yet exist, this ticket
   creates it containing exactly these four helpers; whichever of `GL-EXP-013`/`GL-EXP-017`
   executes later is responsible for appending its own helpers without removing this ticket's.
   No ticket among the three may overwrite or truncate another's addition to `_shared.py`.
6. `appliance/bin/run-reference-e2e.sh` must exit `0` and end in the literal line
   `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE` after this ticket's change, matching both baseline
   runs captured in this ticket's Evidence section.

## Falsifiers

- `grep -n "^def tree_inventory\|^def tree_digest\|^def sha256_bytes\|^def canonical"
  appliance/bin/build-standing-portfolio.py appliance/bin/decision-engine.py
  appliance/bin/replay-standing-portfolio.py appliance/bin/transparency-log.py
  appliance/bin/verify-standing-portfolio.py` still matches any of these 5 files after this
  ticket executes.
- `appliance/bin/_shared.py` does not exist after this ticket executes, or (if `GL-EXP-013`
  and/or `GL-EXP-017` had already run) this ticket's change removed `sha256_file`,
  `read_json`, or `write_json` from it.
- `appliance/bin/build-subsystem-evidence.py` or `appliance/bin/verify-subsystem-evidence.py`
  is modified in any way (neither has a duplicate this ticket may touch — their `canonical()`
  is a distinct, out-of-scope implementation).
- `decision-engine.py` or `transparency-log.py` gains a new call to `tree_digest` (zero today).
- `decision-engine.py`, `replay-standing-portfolio.py`, or `verify-standing-portfolio.py`
  gains a new call to `canonical` (zero today in each).
- `bash appliance/bin/run-reference-e2e.sh` exits non-zero, or its final stdout line is not
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`.
- A direct `hashlib.sha256(b"probe").hexdigest()` disagrees with `_shared.sha256_bytes(b"probe")`,
  or a direct tree walk of a fixed fixture directory disagrees with `_shared.tree_digest()` on
  that same directory before vs. after this ticket's change.
- `git diff --stat` touches `sha256_file`, `read_json`, `write_json`, any `argparse`/CLI
  surface, or any file outside the Authored boundary above.
- Any of `build-document-evidence-index.py`, `project-subsystem-coverage.py`, `verify-crown.py`,
  `cross-check-portfolio.py`, or `observe-project.py` is modified (none has a duplicate of
  these four helpers to consolidate).

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the duplication before touching anything:
grep -n "^def tree_inventory\|^def tree_digest\|^def sha256_bytes\|^def canonical" appliance/bin/*.py
# Reconfirm the 2-file typed exception is untouched by this reconfirmation step:
grep -n "^def canonical" appliance/bin/build-subsystem-evidence.py appliance/bin/verify-subsystem-evidence.py

# Baseline regression proof (record before any change):
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

# After adding/extending appliance/bin/_shared.py and rewriting the 5 files' call sites:
grep -n "^def tree_inventory\|^def tree_digest\|^def sha256_bytes\|^def canonical" \
  appliance/bin/build-standing-portfolio.py appliance/bin/decision-engine.py \
  appliance/bin/replay-standing-portfolio.py appliance/bin/transparency-log.py \
  appliance/bin/verify-standing-portfolio.py
  # expect: zero matches
grep -n "^def canonical" appliance/bin/build-subsystem-evidence.py \
  appliance/bin/verify-subsystem-evidence.py
  # expect: unchanged, still present (out of scope)

# Deterministic behavior equivalence (does not depend on the e2e script's own embedded randomness):
python3 -c "
import sys, hashlib
sys.path.insert(0, 'appliance/bin')
from _shared import sha256_bytes, tree_inventory, tree_digest, canonical
assert sha256_bytes(b'probe') == hashlib.sha256(b'probe').hexdigest()
assert canonical({'b':2,'a':1}) == b'{\"a\":1,\"b\":2}'
inv = tree_inventory('appliance/bin')
assert isinstance(inv, list) and len(inv) > 0
print('sha256_bytes/canonical/tree_inventory/tree_digest behave as expected')
"

# Regression proof, post-fix:
bash appliance/bin/run-reference-e2e.sh 2>&1 | tail -1
  # expect: GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE
echo $?   # expect: 0

git diff --stat   # only the Authored-boundary files above
```

## Evidence this ticket is grounded in (verified this session)

- `grep -n "^def tree_inventory\|^def tree_digest\|^def canonical" appliance/bin/*.py` (run
  directly this session): confirmed `tree_inventory`/`tree_digest` in exactly the 5 files
  named above; `canonical` in those same 5 files **plus** `build-subsystem-evidence.py` and
  `verify-subsystem-evidence.py` (7 total) — the correction documented in Outcome.
- `grep -n "^def sha256_bytes" appliance/bin/*.py` and `grep -h "^def sha256_bytes"
  appliance/bin/*.py | sort -u` (run this session): confirmed exactly 5 matches, one distinct
  body.
- `sed -n '/^def NAME/,/^$/p' <file> | md5` on each of `tree_inventory`, `tree_digest`,
  `canonical` across all 5 (and, for `canonical`, the 2 extra) files (run this session):
  `tree_inventory` → `2717417bed0624eaa9db6fdc0115bc7b` (all 5 identical); `tree_digest` →
  `92df102403d2ce858f15517b3f94e34c` (all 5 identical); `canonical` → `63fabc6505931c141f8441ad427f82fd`
  (all 5 identical) vs. `02693b06fcb4cdf04afc331ab93686d1` (the 2 typed-signature files,
  identical to each other, different from the 5).
- Direct read of `appliance/bin/build-subsystem-evidence.py:15-18` and
  `appliance/bin/verify-subsystem-evidence.py:15-18` (this session): confirmed the typed
  `def canonical(value: Any) -> bytes: ... .encode("utf-8")` signature, distinct from the
  5-file `def canonical(obj): ... .encode()`.
- A direct Python check this session (`json.dumps(sample, sort_keys=True,
  separators=(",",":"), ensure_ascii=False).encode()` vs. `...encode("utf-8")` on a non-ASCII
  sample) confirmed identical output bytes — the two `canonical()` implementations are
  behaviorally equivalent despite non-identical source.
- `grep -n "canonical(\|tree_inventory(\|tree_digest(\|sha256_bytes(" <file>` on each of the 5
  files, excluding `def` lines (run this session): confirmed per-file call-site presence/
  absence, including the three files with zero `canonical()` call sites
  (`decision-engine.py`, `replay-standing-portfolio.py`, `verify-standing-portfolio.py`) and
  the two files with zero `tree_digest()` call sites (`decision-engine.py`,
  `transparency-log.py`) — read each file in full this session to confirm, not inferred from
  the grep alone.
- `grep -n "tree_inventory\|tree_digest\|canonical\|sha256_bytes" tickets/GL-EXP-013.md
  tickets/GL-EXP-017.md` (run this session): both tickets' `## Falsifiers` sections list all
  four names verbatim as paths their own diff must not touch, confirming deliberate exclusion.
- `grep -n "tree_inventory\|tree_digest\|canonical\|sha256_bytes" tickets/OVERLAPS.md` (run
  this session): zero matches against the functions (the file's only "canonical" hits are the
  unrelated English word "canonical registry"/"canonical copy") — no existing registry row for
  these four helpers.
- `ls appliance/bin/_shared.py` (run this session): no such file — confirmed neither
  `GL-EXP-013` nor `GL-EXP-017` has executed yet, so this ticket's Hard Law 5 ordering logic is
  live, not hypothetical.
- `grep -n "_shared.py" tickets/OVERLAPS.md` (run this session): zero matches — despite both
  `GL-EXP-013`'s and `GL-EXP-017`'s own Authored-boundary text stating they would add a
  `_shared.py` section, neither has (both are `NOT_STARTED`); this ticket adds the first one,
  disclosing all three tickets' claims.
- `git rev-parse HEAD`: `bce7f6386c4203784beaae426e40804636c4151a`, identical to the base
  commit `GL-EXP-013`/`GL-EXP-017` were drafted against — confirming no drift between the three
  tickets' baselines.
- `bash appliance/bin/run-reference-e2e.sh` (run directly this session, twice, real subprocess
  execution, not simulated): both runs exited `0` and ended in the literal line
  `GGEN_LEGACY_ASSURANCE_REFERENCE_ALIVE`.
- `grep -n "run-reference-e2e" scripts/verify_docs.py` and `grep -rln
  "run-reference-e2e\|appliance/bin" .github/workflows/*.yml` (run this session): the script
  is referenced only as a path-existence check in `scripts/verify_docs.py:51`, never invoked
  by CI (zero workflow matches) — matching the same finding already recorded in `GL-EXP-013`
  and `GL-EXP-017`.
- `find . -iname "*appliance*test*" -o -iname "*test*appliance*"` (run this session): no
  output — no dedicated test suite exists for `appliance/bin/`, matching both siblings' own
  finding.
- `ls tickets/GL-EXP-041.md` (run before writing this file): confirmed no such file existed —
  this id was genuinely free, not reused.

## Standing

`PARTIAL_ALIVE` ceiling only — this ticket is drafted and admitted, `NOT_STARTED`. No code has
been written or run beyond the read-only verification commands captured above (confirming the
real duplication across the 5 files, correcting the originating candidate's overclaim that
`canonical()` was byte-identical across 5 files when it is actually present in 7 with two
distinct implementations, documenting the three helpers' uneven call-site liveness across the
5 files, its absence from every other ticket's claimed boundary and from `tickets/OVERLAPS.md`,
and two real passing runs of the one pre-existing black-box regression harness that covers all
5 affected files). Executing this ticket (adding/extending `appliance/bin/_shared.py`,
rewriting the 5 files' call sites, and re-running the "Acceptance" commands with their real
output) is required before any higher standing can be claimed.
