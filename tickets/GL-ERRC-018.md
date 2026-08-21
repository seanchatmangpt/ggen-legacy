# GL-ERRC-018 — Create a machine-checkable admission gate for CATALOG disposition-confidence

**Status:** admitted, `NOT_STARTED` — drafted by ultracode ERRC pass 5
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`docs/v26.8.20/DECISIONS.md`'s "Disposition-confidence gap (ultracode
backlog item 20)" finding — 3 of 65 `CATALOG` individuals
(`legacy_sync_audit_flag`, `legacy_sync_dry_run_value_flag`,
`legacy_ggen_toml_dual_schema`) assert a definite disposition
(`REFUSED`/`REPLACED`/`REPLACED`) while their own `historical_source_commit`
field is literally the string `"UNKNOWN"`, contradicting the file's own
stated admission criterion (`tools/v26.8.1/legacy_archaeology.py:27-37`'s
docstring: disposition confidence should track cited primary evidence) —
was found, documented, and explicitly **not fixed**, twice: once in the
ultracode loop (item 20) and once again independently by this pass's own
re-verification (confirmed live: `legacy_archaeology.py:345-388` still
shows all three `historical_source_commit="UNKNOWN -- ..."` strings paired
with definite dispositions). This session also confirmed **no
machine-checkable gate exists anywhere in the repo** to catch this class of
bug: none of the eight `scripts/verify_*.py` files reference
`historical_source_commit` at all (`grep -l historical_source_commit
scripts/*.py` returns nothing), and no CI workflow step runs any check
against `CATALOG`'s internal field consistency. That means the exact bug
this session re-confirmed by hand can recur silently for any of the other
62 individuals, or reappear in these same 3 after a future edit, with
nothing short of a human re-reading all 65 entries catching it — the
precise failure mode a *ticket documenting the bug* cannot itself prevent.
This ticket creates a new, additive `scripts/verify_catalog_disposition_confidence.py`
that parses `ontology/v26.8.1/legacy-capabilities.ttl` (the published TTL
`to_turtle()` emits, not the Python source, so the check runs against what
actually shipped) and asserts, for every `ggen:LegacyCapability` individual:
if `ggen:disposition` is one of the definite terminal values
(`PRESERVED`/`SUBSUMED`/`REPLACED`/`ARCHIVED`/`REFUSED` — the same enum
`GL-MANUFACTURE-005` is extending, unaffected by that ticket since this one
only reads the field), then `ggen:historicalSourceCommit` (or whatever the
TTL's actual predicate name is, confirmed by inspection during
implementation) must not be the literal string `"UNKNOWN"` nor start with
`"UNKNOWN --"`. A violation exits non-zero with every offending slug named
explicitly (not just a count), so the failure is immediately actionable.
This does not resolve the 3 existing violations (that requires the
evidence-verification judgment call `DECISIONS.md` already deferred to a
future session) and does not silently exempt them — the new script fails
loudly on current `HEAD` by design until they're actually fixed, and this
ticket's own falsifiers require that failure to be reproduced, not
avoided.

## Authored boundary

```text
scripts/verify_catalog_disposition_confidence.py   # new
tickets/GL-ERRC-018.md
```

`ontology/v26.8.1/legacy-capabilities.ttl`,
`tools/v26.8.1/legacy_archaeology.py`, and every other existing
`scripts/verify_*.py` file are read but not modified by this ticket — fixing
the 3 known violations, or wiring this new script into `.github/workflows/`
CI, are both explicitly out of scope (the former needs the repo-owner
evidence judgment call `DECISIONS.md` already deferred; the latter is a
natural, obvious follow-up this ticket deliberately leaves to a session that
can also confirm the new script's runtime cost and false-positive rate
against a real CI run, rather than bundling an untested new check straight
into the gating pipeline in the same ticket that authored it).

## Hard laws

1. The new script is read-only against `legacy-capabilities.ttl` — it must
   not write, reformat, or otherwise mutate the TTL file in any code path,
   including its own error paths.
2. Definite-disposition-with-UNKNOWN-provenance is a **fail**, always —
   this script does not get a `--allow` flag or skip-list mechanism to
   exempt the 3 known violations; it must exit non-zero against the current
   `HEAD` state, and that non-zero exit on the real, current file is this
   ticket's own primary acceptance evidence, not a bug to work around.
3. No new dependency beyond what's already available for TTL parsing in
   this repo (check `tools/v26.8.1/requirements.txt`, added by
   `GL-ARCH-003`, for an existing RDF library before adding a new one; if
   none exists, a minimal line-oriented parser scoped only to the two
   predicates this check needs is acceptable and preferable to a new heavy
   dependency for a single-purpose admission check).
4. The script's failure output names every offending individual's slug
   (its `ggen:LegacyCapability` subject/local name) on its own line — a bare
   "N violations found" count without names is not sufficient per this
   ticket's own stated purpose (loud, actionable, not just detected).
5. This ticket does not touch `GL-MANUFACTURE-005`'s disposition-enum
   extension (`ROUTED_LEGACY`/`SHADOW_VERIFIED`/`SHIFTED`) — those
   intermediate states are non-terminal by that ticket's own design and are
   out of scope for this check's definite-disposition list unless a future
   session decides otherwise; this ticket's definite-value list is fixed to
   the 5 terminal values that exist in the schema today.

## Falsifiers

- `python3 scripts/verify_catalog_disposition_confidence.py` run against
  the real, current `ontology/v26.8.1/legacy-capabilities.ttl` on this
  ticket's `Base` commit exits **non-zero** and its output names all three
  of `legacy_sync_audit_flag`, `legacy_sync_dry_run_value_flag`, and
  `legacy_ggen_toml_dual_schema` explicitly.
- A synthetic TTL fixture with one individual carrying `disposition
  "PRESERVED"` and `historicalSourceCommit "abc123..."` (a real-looking
  hash, not `"UNKNOWN"`) produces a **clean** (zero-violation, exit 0) run
  when it is the only individual in the fixture — proving the check is not
  vacuously failing on unrelated grounds.
- A synthetic TTL fixture with one individual carrying `disposition
  "REFUSED"` and `historicalSourceCommit "UNKNOWN"` (exact literal, no
  trailing explanation) is caught — proving the check does not only match
  the `"UNKNOWN -- ..."` explained form the 3 real violations happen to use
  today.
- `grep -n historical_source_commit scripts/*.py` after this ticket's
  execution shows the new script (proving it was actually added, not just
  described).

## Acceptance (not yet run — ticket not started)

```bash
python3 scripts/verify_catalog_disposition_confidence.py   # once written: nonzero exit + named offending slugs on the 3 known violations
```

## Standing

`UNKNOWN` — not started. See `tickets/AUDIT-REPORT.md`'s check-1 finding
(this ticket was missing `## Acceptance` and `## Standing` entirely, ending
right after Falsifiers, until this edit) and this ticket's own Outcome
section for the grounding evidence (3 named CATALOG individuals with a
definite disposition paired with `historical_source_commit: "UNKNOWN"`).
