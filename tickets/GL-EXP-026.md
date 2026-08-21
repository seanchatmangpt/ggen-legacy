# GL-EXP-026 — Reduce verifier-appliance-profile.json's duplicate unbacked `foundry_runtime_candidate` ALIVE claim

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`authority/verifier-appliance-profile.json:17-20` (read directly this
session):

```json
"verified_foundry_runtime_candidate": {
    "revision": "458f0f88aee0060cddce3ffdaa7e2172a4f40a25",
    "standing": "ALIVE",
    "runtime_dependency_admitted": false
}
```

`authority/project-001-promotion.json` (read directly this session)
carries the identical candidate revision in two places:
`evidence_basis.verified_runtime_candidate` and
`bounded_rails.foundry_runtime_candidate.exact_head`, both
`458f0f88aee0060cddce3ffdaa7e2172a4f40a25` -- byte-identical to the hash
above. `bounded_rails.foundry_runtime_candidate` reads:

```json
"foundry_runtime_candidate": {
    "standing": "ALIVE",
    "scope": "exact candidate verification only; not admitted as the stable manufacturing dependency",
    "exact_head": "458f0f88aee0060cddce3ffdaa7e2172a4f40a25",
    "runtime_dependency_admitted": false,
    "evidence": ["evidence/foundry-runtime-candidate.json"]
}
```

`test -e evidence/foundry-runtime-candidate.json` (run this session):
missing. This is the exact same nonexistent file `tickets/GL-ERRC-017.md`
(read in full this session) identifies in its own Outcome section as the
`foundry_runtime_candidate` rail's *sole* cited evidence: "its `evidence`
array names exactly one file (`evidence/foundry-runtime-candidate.json`),
that file does not exist, and it has zero other cited evidence -- meaning
that rail's `"standing": "ALIVE"` claim has, by this file's own citation
mechanism, no locatable backing whatsoever, not partial backing." That
ticket's Hard Law 1 accordingly drops
`bounded_rails.foundry_runtime_candidate.standing` from `ALIVE` to
`UNVERIFIED` -- but its Authored boundary (read directly this session)
names exactly one target file:

```text
authority/project-001-promotion.json   # standing fields + new missing_evidence arrays only
tickets/GL-ERRC-017.md
```

`verifier-appliance-profile.json` is never mentioned in
`tickets/GL-ERRC-017.md` (`grep -n "verifier-appliance-profile"
tickets/GL-ERRC-017.md`, run this session: zero matches, exit 1). Yet
`verifier-appliance-profile.json` asserts the identical unbacked claim for
the identical revision, and is explicitly cross-referential with
`project-001-promotion.json`: `verifier-appliance-profile.json`'s own
`promotion_authority` field (line 8) reads
`"authority/project-001-promotion.json"` -- it names that file as its
authorizing source, not the reverse. `verifier-appliance-profile.json` has
no `evidence` array of its own anywhere in the file (`grep -n "\"evidence\""
authority/verifier-appliance-profile.json`, run this session: zero
matches; the file is 54 lines total, read in full this session) -- so its
`verified_foundry_runtime_candidate.standing: "ALIVE"` claim has, if
anything, *less* locatable citation machinery than the sibling field
`GL-ERRC-017` is already fixing, not more.

If `GL-ERRC-017` executes exactly as currently scoped, the result is a
corrected `project-001-promotion.json` (`foundry_runtime_candidate.standing:
"UNVERIFIED"`) sitting next to an uncorrected
`verifier-appliance-profile.json` still asserting
`verified_foundry_runtime_candidate.standing: "ALIVE"` for the same
revision, the same missing evidence, and the same underlying gap --
undoing the fix's own purpose by leaving a second, uncorrected copy
standing right next to the corrected one. `grep -iln
"verifier-appliance-profile" tickets/GL-*.md tickets/OVERLAPS.md` (run this
session): zero matches -- no ticket in the corpus, including
`GL-ERRC-017` itself, names this file. This ticket closes that gap: reduce
`verifier-appliance-profile.json`'s `verified_foundry_runtime_candidate.
standing` from `ALIVE` to `UNVERIFIED`, mirroring `GL-ERRC-017`'s Hard Law
1 disposition for the sibling field it targets, so both copies of the same
claim read the same honest standing instead of one corrected and one
stale.

## Authored boundary

(No overlap with any existing ticket's Authored boundary was found: `grep
-iln "verifier-appliance-profile" tickets/GL-*.md tickets/OVERLAPS.md`, run
this session, returns zero matches. `GL-ERRC-017`'s own Authored boundary
claims only `authority/project-001-promotion.json`, a different file, so no
`tickets/OVERLAPS.md` row is added by this ticket -- the two tickets fix
the same underlying fact in two disjoint files, not the same file, and the
overlap-registry rule in `tickets/OVERLAPS.md`'s own header is scoped to
same-file Authored-boundary claims. This relationship is instead recorded
in prose above and in this ticket's own Standing section below, since it is
motivation/lineage, not a file-path conflict.)

```text
authority/verifier-appliance-profile.json   # verified_foundry_runtime_candidate.standing field only
tickets/GL-EXP-026.md
```

No other field in `verifier-appliance-profile.json` (`standing`,
`standing_scope`, `promotion_authority`, `ggen`, `customer_controls_
execution`, `portable_offline_transport_standing`, `required_digest_
bindings`, `replay_environments`, `nonclaims`, etc.) is touched -- this
ticket is scoped to the one duplicate-and-unbacked field identified above.
No file is deleted, moved, or regenerated. `evidence/foundry-runtime-
candidate.json` is not manufactured by this ticket (that would launder an
unverified build artifact into a checked-in claim, the same reasoning
`GL-ERRC-017` already states for the sibling field).

## Hard laws

1. `verified_foundry_runtime_candidate.standing` becomes `"UNVERIFIED"`,
   not `"REFUSED"` or silently left `"ALIVE"` -- matching `GL-ERRC-017`'s
   Hard Law 1 disposition for the identical claim in the sibling file, for
   the identical reason (the claim itself, e.g. "exact candidate
   verification only," may still be true; only the *evidence for it* is
   confirmed not currently locatable).
2. `revision` (the hash) and `runtime_dependency_admitted` (`false`) are
   left byte-identical -- this ticket narrows the standing verdict only,
   it does not touch or reinterpret the candidate identity or the
   dependency-admission flag.
3. No field outside `verified_foundry_runtime_candidate.standing` in
   `authority/verifier-appliance-profile.json` is modified, including the
   file's own top-level `standing: "ALIVE"` (a broader claim about the
   whole appliance-profile document, scoped to "customer-controlled
   reference assurance fixture" generally, not specifically to this one
   runtime-candidate sub-claim) -- if a future session finds the top-level
   `standing` field's own composition logic requires revisiting given this
   sub-field's downgrade, that is flagged as a follow-up, not silently
   resolved by this ticket.
4. If `GL-ERRC-017` executes before this ticket and its execution finds
   `bounded_rails.foundry_runtime_candidate.standing` should for any reason
   land somewhere other than `UNVERIFIED` (per its own Hard Law 3's
   re-verification allowance), this ticket's execution re-checks that
   outcome and matches it rather than mechanically applying `UNVERIFIED`
   regardless of what the sibling ticket actually did.

## Falsifiers

- `python3 -c "import json; d=json.load(open('authority/verifier-appliance-profile.json')); print(d['verified_foundry_runtime_candidate']['standing'])"`
  prints `UNVERIFIED`, not `ALIVE`.
- `python3 -c "import json; d=json.load(open('authority/verifier-appliance-profile.json')); print(d['verified_foundry_runtime_candidate']['revision'], d['verified_foundry_runtime_candidate']['runtime_dependency_admitted'])"`
  still prints `458f0f88aee0060cddce3ffdaa7e2172a4f40a25 False` unchanged.
- `python3 -m json.tool authority/verifier-appliance-profile.json` still
  parses as valid JSON after the edit (schema/structure preserved, only
  the one field value changes).
- `git diff --stat` after this ticket touches only
  `authority/verifier-appliance-profile.json` and `tickets/GL-EXP-026.md`.
- The top-level `standing` field (line 6, `"ALIVE"`) is unchanged by this
  ticket (Hard Law 3) -- a diff touching that line without a separate,
  explicitly-scoped ticket justifying it is out of bounds.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
python3 -c "import json; d=json.load(open('authority/verifier-appliance-profile.json')); print(d['verified_foundry_runtime_candidate'])"
  # expect (pre-fix): {'revision': '458f0f88aee0060cddce3ffdaa7e2172a4f40a25', 'standing': 'ALIVE', 'runtime_dependency_admitted': False}
test -e evidence/foundry-runtime-candidate.json && echo "UNEXPECTED: exists" || echo "confirmed missing"
  # expect: confirmed missing

# After the fix:
python3 -c "import json; d=json.load(open('authority/verifier-appliance-profile.json')); print(d['verified_foundry_runtime_candidate']['standing'])"
  # expect: UNVERIFIED
python3 -m json.tool authority/verifier-appliance-profile.json >/dev/null && echo "parses clean"

git diff --stat   # must show only authority/verifier-appliance-profile.json, tickets/GL-EXP-026.md
```

## Evidence this ticket is grounded in (verified this session)

- `python3 -m json.tool authority/verifier-appliance-profile.json` and
  `cat -n authority/verifier-appliance-profile.json` (run this session):
  confirms lines 17-20 verbatim as quoted in Outcome, confirms the file is
  54 lines total with no `evidence` key anywhere
  (`grep -n "\"evidence\"" authority/verifier-appliance-profile.json`:
  zero matches, exit 1), confirms `promotion_authority` (line 8) is
  `"authority/project-001-promotion.json"`.
- `python3 -m json.tool authority/project-001-promotion.json` (run this
  session): confirms `evidence_basis.verified_runtime_candidate` and
  `bounded_rails.foundry_runtime_candidate.exact_head` are both
  `458f0f88aee0060cddce3ffdaa7e2172a4f40a25`, byte-identical to
  `verifier-appliance-profile.json`'s `verified_foundry_runtime_candidate.
  revision`; confirms `bounded_rails.foundry_runtime_candidate.evidence`
  is the single-entry array `["evidence/foundry-runtime-candidate.json"]`.
- `test -e evidence/foundry-runtime-candidate.json` (run this session):
  exits non-zero (missing). `ls evidence/` (run this session): confirms
  the directory exists (`appliance/`, `autonomic/`,
  `foundry-bootstrap-verifier.json`, `foundry-provenance-verifier.json`,
  `local-docs-verifier.json`, `lsp-contract/`,
  `offline-transport-provenance.json`, `v26.8.3/`) but contains no
  `foundry-runtime-candidate.json`.
- Direct `Read` of `tickets/GL-ERRC-017.md` in full (117 lines, this
  session): confirms its Outcome section's "zero locatable evidence, full
  stop" finding for the `foundry_runtime_candidate` rail, its Hard Law 1
  (`UNVERIFIED` disposition), and its Authored boundary naming exactly
  `authority/project-001-promotion.json` and `tickets/GL-ERRC-017.md` --
  no other file.
- `grep -n "verifier-appliance-profile" tickets/GL-ERRC-017.md` (run this
  session): zero matches, exit 1 -- confirms `GL-ERRC-017` never names the
  file this ticket targets.
- `grep -iln "verifier-appliance-profile" tickets/GL-*.md tickets/OVERLAPS.md`
  (run this session): zero matches -- confirms no ticket in the corpus,
  and no `OVERLAPS.md` entry, currently names
  `authority/verifier-appliance-profile.json`, so this ticket's Authored
  boundary claims a genuinely unclaimed file and no `OVERLAPS.md` row is
  required under that registry's own same-file-conflict scope.
- `grep -n "authority/" tickets/OVERLAPS.md tickets/GL-*.md` (run this
  session): confirms the only other tickets touching any `authority/*.json`
  file are `GL-ERRC-011.md` (three different files: `product-profile.json`,
  `foundry-work-program.json`, `offline-verifier-transport.json`),
  `GL-ERRC-020.md` and `GL-EXP-010.md`/`GL-MANUFACTURE-005.md` (all three
  on `foundry-work-program.json`, already reconciled in
  `tickets/OVERLAPS.md`'s own `authority/foundry-work-program.json`
  section), `GL-LSP-001.md` (`lsp-contract.json`), and `GL-ERRC-017.md`
  (`project-001-promotion.json`) -- none touch
  `verifier-appliance-profile.json`.
- `git rev-parse HEAD` (run this session):
  `bce7f6386c4203784beaae426e40804636c4151a`, matching this ticket's
  declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
duplicate-claim gap (the same unbacked `ALIVE` standing for the same
candidate revision, asserted in a second file `GL-ERRC-017` does not
touch). The actual field edit has not been made. Once `GL-ERRC-017`
executes, re-verify its actual chosen standing value for
`bounded_rails.foundry_runtime_candidate` (per this ticket's Hard Law 4)
before applying this ticket's own edit, so the two files land on the same
honest value rather than diverging again through independent execution
order.
