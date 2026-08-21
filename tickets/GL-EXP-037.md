# GL-EXP-037 — Delete `foundry/bootstrap.yaml`'s dead, self-contradicting `terminal_condition` block (lines 93-105)

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`foundry/bootstrap.yaml` (read in full this session) carries two things at
once: an honest, actively-checked top-level state (`"standing":
"PARTIAL_ALIVE"`, `"runtime_dependency_admitted": false`, and an 11-entry
`"workstreams"` array where every one of `A`-`K` reads `"status":
"NOT_STARTED"`), and a `"terminal_condition"` block at lines 93-105 that
flatly contradicts it — `"standing": "ALIVE"`,
`"fortune_scale_reference_manufactured": true`,
`"solution_admission": true`, asserted verbatim inside the same document.

This session confirmed, by direct read and grep, that nothing in the repo
reads that block. `grep -rln "terminal_condition"` across the entire repo
(excluding `.git` and `.claude/worktrees`) returns exactly one hit —
`foundry/bootstrap.yaml` itself, the field's own definition. No `.py`,
`.rs`, `.md`, or other `.json`/`.yaml` file anywhere in the repo names this
key. `scripts/verify_foundry_bootstrap.py` (read in full, lines 144-165)
is the script that actually enforces the finalized-standing predicates this
block appears to duplicate — but it does so by loading
`schemas/final-evidence.schema.json`'s `$defs.finalPredicates.properties[*]`
`const` values into a hardcoded `expected_constants` dict and comparing
those against nothing from `bootstrap.yaml`; `bootstrap.yaml["terminal_condition"]`
is never referenced by that script, or by `scripts/ci_errc.py` (which only
JSON-parses `foundry/bootstrap.yaml` for structural validity) or
`scripts/verify_docs.py` (which only reads `schema_version` and
`runtime_dependency_admitted` from it). The block is dead data.

It is also drifted from the schema it appears to restate. Direct
Python comparison this session
(`json.load` both files, diff key sets) shows `bootstrap.yaml`'s
`terminal_condition` carries exactly 11 keys, all of which match
`schemas/final-evidence.schema.json`'s `$defs.finalPredicates.properties`
`const` values verbatim (`unknown_capabilities`/`unknown_dispositions`/
`unknown_standings`/`unassigned_verifiers`/`missing_equivalence_cases`/
`equivalence_failures`/`replay_differences` all `0`,
`cross_repository_receipts_valid`/`fortune_scale_reference_manufactured`/
`solution_admission` all `true`, `standing` `"ALIVE"`) — but the schema's
`finalPredicates` has 13 required properties, and `terminal_condition` is
missing 2 of them entirely: `ggen_kernel_admitted` and
`ggen_legacy_corpus_admitted` (both `const: true` in the schema). A field
that duplicates 11 of 13 keys of a schema and silently omits the other 2
is not a reliable restatement of anything — it is stale copy-paste that
has already drifted once and has no mechanism preventing further drift,
because nothing checks it.

The combination is the actual defect: a reader who parses
`bootstrap.yaml["terminal_condition"]["standing"]` naively gets `"ALIVE"`
from a document whose real, checked top-level `standing` is
`"PARTIAL_ALIVE"` with all 11 workstreams `NOT_STARTED` — a false-positive
green reading sitting inside an otherwise honestly-`PARTIAL_ALIVE` file,
reachable by nothing except a human or tool that trusts the wrong key.

This ticket eliminates the block outright rather than repairing it into a
"live check." A live check would require `foundry/bootstrap.yaml` — a
static data file — to compute a derived value at read time, which is not
what this file is for; the actual live check for these predicates already
exists, correctly, in `scripts/verify_foundry_bootstrap.py:144-165`,
sourced from the schema, not duplicated into the bootstrap document.
Deleting the dead, drifted, self-contradicting duplicate is the smaller,
safer, and more honest fix: it removes a false-positive reading without
adding any new logic, and nothing downstream breaks, because nothing
downstream reads the field being removed.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- checked this session: `grep -rln "bootstrap.yaml" tickets/GL-*.md`
found `GL-ERRC-020` (scoped to `runtime_dependency_admitted` /
`standing_transferred` only), `GL-EXP-010` (scoped to a different file,
`migrations/ggen-v26.8.1/migration-manifest.json`), `GL-EXP-034` (scoped
to a different file, `authority/ggen-create-receiving-contract.json`), and
`GL-MANUFACTURE-005` (scoped to `scripts/verify_foundry_bootstrap.py`'s
`EXPECTED_DISPOSITIONS` constant, not `foundry/bootstrap.yaml` itself, and
not the `finalPredicates`/`terminal_condition` comparison at lines
144-165). None claims the `terminal_condition` field. A disclosed row has
been added to `tickets/OVERLAPS.md`'s `foundry/bootstrap.yaml` section by
this same write.)

```text
foundry/bootstrap.yaml   # terminal_condition block only (lines 93-105) — deletion
tickets/GL-EXP-037.md
tickets/OVERLAPS.md      # new `foundry/bootstrap.yaml` section, disclosing this ticket vs. GL-ERRC-020
```

No change to `foundry/bootstrap.yaml`'s `standing`, `runtime_dependency_admitted`,
`workstreams`, `coordinates`, `receiving_evidence`, `provenance`,
`refusal_conditions`, or any other top-level field — this ticket touches
only the `terminal_condition` object and its enclosing braces/comma. No
change to `scripts/verify_foundry_bootstrap.py`, `scripts/ci_errc.py`,
`scripts/verify_docs.py`, or `schemas/final-evidence.schema.json` — none of
them reads `terminal_condition`, so none needs to change for this deletion
to be safe. No change to `tickets/GL-ERRC-020.md`'s own scope or its
`runtime_dependency_admitted`/`standing_transferred` claim.

## Hard laws

1. This ticket deletes the `terminal_condition` key and its entire object
   value (lines 93-105 as of this ticket's declared Base) from
   `foundry/bootstrap.yaml` — it does not repair, rename, or relocate the
   block, and it does not add a new "live check" mechanism anywhere. The
   real, already-existing live check for these predicates
   (`scripts/verify_foundry_bootstrap.py:144-165`, sourced from
   `schemas/final-evidence.schema.json`) is left untouched.
2. `foundry/bootstrap.yaml` must remain valid JSON after the edit (this
   file's JSON body is loaded as JSON by `scripts/ci_errc.py`,
   `scripts/verify_docs.py`, and `scripts/verify_foundry_bootstrap.py`) —
   the preceding key's trailing comma (currently after
   `"refusal_conditions"`'s closing `]`) must be removed along with the
   `terminal_condition` block so the object's last member has no trailing
   comma.
3. No other top-level key in `foundry/bootstrap.yaml` changes value,
   ordering, or presence.
4. `scripts/verify_foundry_bootstrap.py`'s exit code and printed report
   must be unchanged by this edit (it does not reference
   `terminal_condition` today, confirmed by grep this session, so removing
   the field must not introduce a new error code).

## Falsifiers

- `foundry/bootstrap.yaml` fails to parse as JSON after the edit.
- `grep -n "terminal_condition" foundry/bootstrap.yaml` still matches
  after the edit.
- Any top-level key other than `terminal_condition` changes value.
- `python3 scripts/verify_foundry_bootstrap.py` exits non-zero, or its
  printed `errors` list is non-empty, after the edit (would mean the
  script secretly depended on `terminal_condition` after all, contradicting
  this ticket's own grep-based finding — re-verify rather than land).
- `python3 scripts/ci_errc.py` (or its structured-file-parse path) reports
  `STRUCTURED_FILE_INVALID` for `foundry/bootstrap.yaml` after the edit.
- `git diff --stat` shows any file changed other than
  `foundry/bootstrap.yaml`, `tickets/GL-EXP-037.md`, and
  `tickets/OVERLAPS.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Confirm the dead, drifted block before fixing:
grep -n "terminal_condition" foundry/bootstrap.yaml
  # expect: line 93, "terminal_condition": {
grep -rln "terminal_condition" . --exclude-dir=.git --exclude-dir=.claude
  # expect: only foundry/bootstrap.yaml
python3 -c "
import json
b = json.load(open('foundry/bootstrap.yaml'))
s = json.load(open('schemas/final-evidence.schema.json'))
tc = set(b['terminal_condition'].keys())
fp = set(s['\$defs']['finalPredicates']['properties'].keys())
print('missing from terminal_condition:', sorted(fp - tc))
"
  # expect: ['ggen_kernel_admitted', 'ggen_legacy_corpus_admitted']

# After deleting the terminal_condition block:
python3 -c "json.load(open('foundry/bootstrap.yaml'))" 2>&1 || python3 -c "
import json
json.load(open('foundry/bootstrap.yaml'))
print('OK: still valid JSON')
"
grep -n "terminal_condition" foundry/bootstrap.yaml
  # expect: no output (zero matches)
python3 scripts/verify_foundry_bootstrap.py
  # expect: exit 0, "errors": [] in the printed report
python3 scripts/ci_errc.py --help >/dev/null 2>&1 || true
  # (structural-parse path exercised indirectly via ci_errc.py's own test/CI invocation)

git diff --stat   # must show only foundry/bootstrap.yaml,
                   # tickets/GL-EXP-037.md, tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` / `git log -1` this session:
  `bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's
  declared Base.
- Direct `Read` of `foundry/bootstrap.yaml` in full this session: confirms
  top-level `"standing": "PARTIAL_ALIVE"`, `"runtime_dependency_admitted":
  false`, `"workstreams"` array with all 11 `A`-`K` entries `"status":
  "NOT_STARTED"`, and the `"terminal_condition"` object at lines 93-105
  asserting `"standing": "ALIVE"`,
  `"fortune_scale_reference_manufactured": true`,
  `"solution_admission": true` verbatim.
- `grep -rn "terminal_condition" . --include="*.yaml" --include="*.yml"`
  this session (excluding `.claude/worktrees`): exactly one hit,
  `foundry/bootstrap.yaml:93`.
- `grep -rln "terminal_condition" /Users/sac/ggen-legacy --exclude-dir=.git
  --exclude-dir=.claude` this session (no extension filter, whole repo):
  exactly one file, `foundry/bootstrap.yaml` — confirms no `.py`, `.rs`,
  `.md`, `.json`, or other file anywhere in the repo references this key.
- Direct `Read` of `scripts/verify_foundry_bootstrap.py` in full this
  session: confirms lines 144-165 build `expected_constants` from
  `schemas/final-evidence.schema.json`'s `$defs.finalPredicates.properties[*]`
  `const` values and compare against `observed_constants` derived from that
  same schema file — `bootstrap.yaml` is never indexed for
  `"terminal_condition"` anywhere in the script (confirmed by the
  whole-repo grep above, which would have caught it).
- Direct `Read` of `schemas/final-evidence.schema.json` in full this
  session: confirms `$defs.finalPredicates.required`/`.properties` lists
  13 keys with `const` values, 11 of which are also verbatim in
  `bootstrap.yaml`'s `terminal_condition`, and 2 of which
  (`ggen_kernel_admitted`, `ggen_legacy_corpus_admitted`, both
  `const: true`) are absent from `terminal_condition` entirely.
- Real Python comparison run this session:
  ```
  terminal_condition keys: [11 keys, listed]
  schema finalPredicates keys: [13 keys, listed]
  missing from terminal_condition: ['ggen_kernel_admitted', 'ggen_legacy_corpus_admitted']
  extra in terminal_condition not in schema: []
  value mismatches on shared keys: []
  ```
  confirming the drift is exactly a 2-key omission, not a broader
  divergence, and that all 11 shared keys' values already agree.
- `grep -rln "bootstrap.yaml\|foundry/bootstrap" .` this session (whole
  repo): found `scripts/ci_errc.py`, `scripts/verify_docs.py`,
  `scripts/verify_foundry_bootstrap.py`, and several doc/ticket files; direct
  `Read` of the relevant ranges in `scripts/ci_errc.py` (lines 170-198) and
  `scripts/verify_docs.py` (lines 185-200) confirms neither references
  `terminal_condition` — `ci_errc.py` only JSON-parses the file for
  structural validity, `verify_docs.py` only reads `schema_version` and
  `runtime_dependency_admitted`.
- `grep -l "bootstrap.yaml" tickets/GL-*.md` this session: `GL-ERRC-020`,
  `GL-EXP-010`, `GL-EXP-034`, `GL-MANUFACTURE-005`. Direct `Read` of each
  one's `## Authored boundary` section this session confirms: `GL-ERRC-020`
  claims `foundry/bootstrap.yaml`'s `runtime_dependency_admitted` /
  `standing_transferred` fields only; `GL-EXP-010` and `GL-EXP-034` claim
  entirely different files (`migrations/ggen-v26.8.1/migration-manifest.json`,
  `authority/ggen-create-receiving-contract.json`), not
  `foundry/bootstrap.yaml`; `GL-MANUFACTURE-005` claims
  `scripts/verify_foundry_bootstrap.py`'s `EXPECTED_DISPOSITIONS` constant,
  not `foundry/bootstrap.yaml` and not the `finalPredicates` comparison at
  lines 144-165. None overlaps the `terminal_condition` field this ticket
  targets.
- `sed`/`Read` of `tickets/OVERLAPS.md` in full this session: confirmed no
  existing `foundry/bootstrap.yaml` section prior to this ticket's own
  write (the existing `scripts/verify_foundry_bootstrap.py` section covers
  a different file). A new `foundry/bootstrap.yaml` section was added by
  this same write, disclosing this ticket against `GL-ERRC-020`.

## Standing

`PARTIAL_ALIVE` ceiling only -- this ticket is drafted and admitted,
`NOT_STARTED`. No code or data file has been changed by this ticket beyond
the read-only verification commands and the `tickets/OVERLAPS.md`
disclosure row captured above. Executing this ticket (deleting the
`terminal_condition` block, re-running the "Acceptance" commands, and
recording their real output) is required before any higher standing can be
claimed.
