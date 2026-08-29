# GL-EXP-042 — Reduce product-profile.json's duplicate unbacked `foundry_runtime_candidate_standing` ALIVE claim

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`authority/product-profile.json:14` and `:22` (read directly this session,
`cat -n authority/product-profile.json`, file is 33 lines total) read:

```json
"foundry_runtime_candidate_standing": "ALIVE",
```

and, eight lines later:

```json
"verified_runtime_candidate": "458f0f88aee0060cddce3ffdaa7e2172a4f40a25",
```

`grep -rl "458f0f88" --include="*.json" --include="*.md" .` (run this
session, worktrees excluded) returns exactly seven files: the five real
source files carrying this candidate revision plus its unqualified `ALIVE`
claim (`README.md`, `authority/project-001-promotion.json`,
`authority/verifier-appliance-profile.json`,
`governance/claims-register.md`, and `authority/product-profile.json`) and
the two ticket files that already document the first four
(`tickets/GL-EXP-030.md`, `tickets/GL-EXP-026.md`). Three separate,
already-admitted tickets each reduce one of the first four files' copy of
this same claim, for the same reason: `GL-ERRC-017` ->
`authority/project-001-promotion.json`'s
`bounded_rails.foundry_runtime_candidate.standing`; `GL-EXP-026` ->
`authority/verifier-appliance-profile.json`'s
`verified_foundry_runtime_candidate.standing`; `GL-EXP-030` ->
`README.md`'s "Foundry runtime candidate" row and
`governance/claims-register.md`'s CLM-011 Standing column. None of the
three touches `authority/product-profile.json` -- its
`foundry_runtime_candidate_standing` field is a fifth, currently-uncorrected
copy of the identical unbacked claim for the identical revision.

The claim's sole possible evidence, per `project-001-promotion.json`'s own
`bounded_rails.foundry_runtime_candidate.evidence` array (the only place in
the repository that names an evidence path for this candidate revision at
all), is `evidence/foundry-runtime-candidate.json`. `test -e
evidence/foundry-runtime-candidate.json` (run this session): exits
non-zero. `ls evidence/` (run this session) confirms the directory exists
(`appliance/`, `autonomic/`, `foundry-bootstrap-verifier.json`,
`foundry-provenance-verifier.json`, `local-docs-verifier.json`,
`lsp-contract/`, `offline-transport-provenance.json`, `v26.8.3/`) but
contains no file by that name. `product-profile.json` itself has no
`evidence` key of its own anywhere in the file (`grep -n "\"evidence\""
authority/product-profile.json`, run this session: zero matches, exit 1) --
so, exactly as `GL-EXP-026` found for `verifier-appliance-profile.json`,
this field has, if anything, less locatable citation machinery than the
sibling field `GL-ERRC-017` is already fixing, not more. `product-profile.
json`'s own `promotion_authority` field (line 23) reads
`"authority/project-001-promotion.json"` -- it names that file as its
authorizing source, the same cross-reference relationship `GL-EXP-026`
already documented for `verifier-appliance-profile.json`.

If `GL-ERRC-017`, `GL-EXP-026`, and `GL-EXP-030` all execute exactly as
currently scoped, the result is four corrected files sitting next to one
uncorrected fifth copy (`product-profile.json`) still asserting
`foundry_runtime_candidate_standing: "ALIVE"` for the same revision, the
same missing evidence, and the same underlying gap -- undoing four-fifths
of the fix's own purpose by leaving the last uncorrected copy standing
right next to the corrected ones.

## Authored boundary

(No overlap with any existing ticket's Authored boundary was found:
`grep -l "product-profile.json" tickets/GL-*.md` (run this session)
matches only `tickets/GL-ERRC-011.md` and `tickets/GL-EXP-026.md`.
`GL-ERRC-011`'s own Authored boundary (read in full this session) claims
only `scripts/verify_foundry_provenance.py`,
`scripts/verify_foundry_bootstrap.py`, `scripts/verify_docs.py`, and
`scripts/verify_offline_transport.py` -- never
`authority/product-profile.json` itself; its prose mentions
`product-profile.json`'s *different* field, `ggen_source_revision`, purely
as motivating context for an `EXPECTED_STABLE_GGEN` staleness comparison
in those scripts, not as an edit target. `GL-EXP-026`'s own Authored
boundary claims only `authority/verifier-appliance-profile.json`; its
prose mentions `product-profile.json` only once, in a `grep -n
"authority/"` evidence listing of which tickets touch which
`authority/*.json` files, again never as an edit target of its own. `grep
-n "product-profile" tickets/OVERLAPS.md` (run this session): zero
matches, exit 1. Since no ticket's Authored boundary claims
`authority/product-profile.json`'s `foundry_runtime_candidate_standing`
field, no `tickets/OVERLAPS.md` row is required under that registry's own
same-file-conflict scope -- this relationship is instead recorded in
prose here, mirroring how `GL-EXP-026` and `GL-EXP-030` each recorded
their own no-overlap findings.)

```text
authority/product-profile.json   # foundry_runtime_candidate_standing field only
tickets/GL-EXP-042.md
```

No other field in `product-profile.json` (`documentation_standing`,
`implementation_standing`, `verifier_appliance_standing`,
`offline_transport_standing`, `complete_foundry_standing`,
`external_production_standing`, `ggen_source_revision`,
`verified_runtime_candidate`, `promotion_authority`, `nonclaims`, etc.) is
touched -- this ticket is scoped to the one duplicate-and-unbacked field
identified above. `ggen_source_revision` in particular is explicitly left
alone: it is `GL-ERRC-011`'s field, not this ticket's, and the two fields
carry unrelated claims (a staleness-comparison coordinate vs. a
runtime-candidate verification standing) that happen to sit in the same
file. No file is deleted, moved, or regenerated.
`evidence/foundry-runtime-candidate.json` is not manufactured by this
ticket (that would launder an unverified build artifact into a checked-in
claim, the same reasoning `GL-ERRC-017`, `GL-EXP-026`, and `GL-EXP-030`
already state for the sibling fields).

## Hard laws

1. `foundry_runtime_candidate_standing` becomes `"UNVERIFIED"`, not
   `"REFUSED"` or silently left `"ALIVE"` -- matching `GL-ERRC-017`'s and
   `GL-EXP-026`'s Hard Law 1 disposition for the identical claim in the
   sibling files, for the identical reason (the claim itself may still be
   true; only the *evidence for it* is confirmed not currently locatable).
2. `verified_runtime_candidate` (the hash, line 22) is left
   byte-identical -- this ticket narrows the standing verdict only, it
   does not touch or reinterpret the candidate identity.
3. No other top-level standing field in `product-profile.json`
   (`documentation_standing`, `implementation_standing`,
   `verifier_appliance_standing`, `offline_transport_standing`,
   `complete_foundry_standing`, `external_production_standing`) is
   modified by this ticket, including where a broader field's own
   composition logic might arguably be affected by this one sub-claim's
   downgrade -- any such dependency is flagged as a follow-up, not
   silently resolved here.
4. If `GL-ERRC-017` executes before this ticket and its execution finds
   `bounded_rails.foundry_runtime_candidate.standing` should for any
   reason land somewhere other than `UNVERIFIED` (per its own Hard Law 3's
   re-verification allowance), this ticket's execution re-checks that
   outcome and matches it rather than mechanically applying `UNVERIFIED`
   regardless of what the sibling tickets actually did.

## Falsifiers

- `python3 -c "import json; d=json.load(open('authority/product-profile.json')); print(d['foundry_runtime_candidate_standing'])"`
  prints `UNVERIFIED`, not `ALIVE`.
- `python3 -c "import json; d=json.load(open('authority/product-profile.json')); print(d['verified_runtime_candidate'])"`
  still prints `458f0f88aee0060cddce3ffdaa7e2172a4f40a25` unchanged.
- `python3 -m json.tool authority/product-profile.json` still parses as
  valid JSON after the edit (schema/structure preserved, only the one
  field value changes).
- `git diff --stat` after this ticket touches only
  `authority/product-profile.json` and `tickets/GL-EXP-042.md`.
- `documentation_standing`, `implementation_standing`,
  `verifier_appliance_standing`, `offline_transport_standing`,
  `complete_foundry_standing`, and `external_production_standing` are all
  unchanged by this ticket (Hard Law 3) -- a diff touching any of those
  lines without a separate, explicitly-scoped ticket justifying it is out
  of bounds.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
python3 -c "import json; d=json.load(open('authority/product-profile.json')); print(d['foundry_runtime_candidate_standing'], d['verified_runtime_candidate'])"
  # expect (pre-fix): ALIVE 458f0f88aee0060cddce3ffdaa7e2172a4f40a25
test -e evidence/foundry-runtime-candidate.json && echo "UNEXPECTED: exists" || echo "confirmed missing"
  # expect: confirmed missing

# After the fix:
python3 -c "import json; d=json.load(open('authority/product-profile.json')); print(d['foundry_runtime_candidate_standing'])"
  # expect: UNVERIFIED
python3 -m json.tool authority/product-profile.json >/dev/null && echo "parses clean"

git diff --stat   # must show only authority/product-profile.json, tickets/GL-EXP-042.md
```

## Evidence this ticket is grounded in (verified this session)

- `cat -n authority/product-profile.json` (run this session): confirms
  line 14 verbatim as `"foundry_runtime_candidate_standing": "ALIVE",` and
  line 22 verbatim as `"verified_runtime_candidate":
  "458f0f88aee0060cddce3ffdaa7e2172a4f40a25",`; confirms the file is 33
  lines total with no `evidence` key anywhere (`grep -n "\"evidence\""
  authority/product-profile.json`: zero matches, exit 1); confirms
  `promotion_authority` (line 23) is
  `"authority/project-001-promotion.json"`.
- `grep -rl "458f0f88" --include="*.json" --include="*.md" .`
  (run this session, worktrees excluded): returns exactly seven files --
  `README.md`, `tickets/GL-EXP-030.md`, `tickets/GL-EXP-026.md`,
  `authority/verifier-appliance-profile.json`,
  `authority/project-001-promotion.json`,
  `authority/product-profile.json`, `governance/claims-register.md`.
- `grep -n -B2 -A2 "458f0f88\|foundry-runtime-candidate"
  authority/project-001-promotion.json` (run this session): confirms
  `bounded_rails.foundry_runtime_candidate.evidence` is the single-entry
  array `["evidence/foundry-runtime-candidate.json"]`, the only cited
  evidence path for this candidate revision anywhere in the repository.
- `test -e evidence/foundry-runtime-candidate.json` (run this session):
  exits non-zero (missing). `ls -la evidence/` (run this session):
  confirms the directory exists but contains no
  `foundry-runtime-candidate.json`.
- Direct `Read` of `tickets/GL-ERRC-017.md`, `tickets/GL-EXP-026.md`, and
  `tickets/GL-EXP-030.md` in full (this session): confirms each ticket's
  Authored boundary claims exactly one distinct file/pair of files
  (`authority/project-001-promotion.json`;
  `authority/verifier-appliance-profile.json`; `README.md` +
  `governance/claims-register.md`, respectively) and none names
  `authority/product-profile.json`.
- `grep -l "product-profile.json" tickets/GL-*.md` (run this session):
  matches only `tickets/GL-ERRC-011.md` and `tickets/GL-EXP-026.md`.
  Direct `Read` of `tickets/GL-ERRC-011.md`'s Authored boundary section
  (this session): confirms it claims only four `scripts/verify_*.py`
  files, never `authority/product-profile.json` itself; its one prose
  mention of `product-profile.json` (around line 122) concerns the
  distinct `ggen_source_revision` field, used for an unrelated
  `EXPECTED_STABLE_GGEN` staleness comparison in those scripts.
  `tickets/GL-EXP-026.md`'s one mention of `product-profile.json` (in a
  `grep -n "authority/"` evidence listing) is likewise never an Authored
  boundary claim on that file.
- `grep -n "product-profile" tickets/OVERLAPS.md` (run this session):
  zero matches, exit 1 -- confirms no existing registry entry covers this
  file.
- `git rev-parse HEAD` (run this session):
  `bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's
  declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
duplicate-claim gap (the same unbacked `ALIVE` standing for the same
candidate revision, asserted in a fifth file none of `GL-ERRC-017`,
`GL-EXP-026`, or `GL-EXP-030` touches). The actual field edit has not been
made. Once `GL-ERRC-017` executes, re-verify its actual chosen standing
value for `bounded_rails.foundry_runtime_candidate` (per this ticket's
Hard Law 4) before applying this ticket's own edit, so all five files land
on the same honest value rather than diverging again through independent
execution order.
