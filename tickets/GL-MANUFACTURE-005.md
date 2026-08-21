# GL-MANUFACTURE-005 — routing-state disposition extension (Gall checkpoint 3)

**Status:** admitted, `NOT_STARTED` — drafted this session, not executed
**Base:** `seanchatmangpt/ggen-legacy@f9b283e`
**Standing ceiling:** `PARTIAL_ALIVE` (schema only — no runtime)
**Publication:** draft pull request; no merge authority

## Outcome

Extend `schemas/migration-manifest.schema.json`'s `component.disposition`
enum (currently `PRESERVED|SUBSUMED|REPLACED|ARCHIVED|REFUSED`,
`schemas/migration-manifest.schema.json:106-113`) with intermediate routing
states preceding the terminal ones — `ROUTED_LEGACY` (default) →
`SHADOW_VERIFIED` → `SHIFTED` — expressing the Strangler Fig façade pattern
this repo's `construct` stage currently lacks (per this session's Explore
finding: no routing/façade code exists anywhere in the repo; disposition is
a single one-shot terminal value today).

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before assuming sole ownership of a path below.)

```text
schemas/migration-manifest.schema.json   # disposition enum only
scripts/verify_foundry_bootstrap.py      # EXPECTED_DISPOSITIONS, in lockstep
tickets/GL-MANUFACTURE-005.md
```

## ⚠ Stale premise found (ultracode backlog item 16 — flagged, not acted on)

This ticket's exclusion below was written assuming PR `seanchatmangpt/ggen#544`
(and its companion `#543`) are unmerged drafts, per
`authority/foundry-work-program.json:19` (`"status": "OPEN_DRAFT"`) and
`foundry/bootstrap.yaml:8,16` (`runtime_dependency_admitted: false`,
`standing_transferred: false`). **Checked against the real sibling repo
(`~/ggen`, `gh pr view`): both #544 and #543 are actually `MERGED`**
(2026-08-01), and `tools/architecture-foundry` has received further commits
since on that repo. This repo's authority files (`foundry-work-program.json`,
`bootstrap.yaml`) are stale relative to the real sibling-repo state.

**This finding is NOT acted on here** — flipping `runtime_dependency_admitted`
or `standing_transferred` to `true` is exactly the kind of admission decision
this repo's ticket-gating exists to prevent from happening incidentally
inside an audit pass. It is named so the repo owner (or a dedicated
follow-up ticket) can decide whether to admit the now-merged runtime,
re-verify its current state on the sibling repo first, and update
`authority/foundry-work-program.json`/`foundry/bootstrap.yaml` deliberately.
Until that happens, this ticket's exclusion below stands as originally
written — treat `runtime_dependency_admitted: false` as this repo's current
authority-of-record, not as this finding's correction.

## Explicit exclusion — the hard boundary of this ticket

This ticket **does not** admit an actual router/dispatcher runtime. The real
construct/execute engine is an unmerged draft PR in a sibling repository
(`authority/foundry-work-program.json:16-58`:
`seanchatmangpt/ggen#544`, `tools/architecture-foundry`,
`"runtime_dependency_admitted": false`) — this repo cannot unilaterally flip
that flag or treat the sibling PR as merged. This ticket only prepares the
*data shape* a future router would read; it stays schema/doc-level.

## Hard laws

1. New enum values are additive/ordered before the existing terminal values
   — no existing terminal disposition value is renamed or removed.
2. `verify_foundry_bootstrap.py`'s `EXPECTED_DISPOSITIONS` update happens in
   the same commit as the schema change — never out of lockstep (an
   unsynced pair silently breaks the existing bootstrap verifier).
3. `runtime_dependency_admitted` stays `false` in `foundry/bootstrap.yaml`
   and `authority/foundry-work-program.json` — this ticket doesn't touch it.
4. No claim of `ALIVE`/`SHIFTED` standing for any real capability — this
   ticket only prepares the enum, it doesn't move anything through it.

## Pre-derived diff (ultracode backlog item 11 — ready to apply on execution)

Exact diffs, not yet applied (this ticket is `NOT_STARTED`):

```diff
--- a/schemas/migration-manifest.schema.json
+++ b/schemas/migration-manifest.schema.json
         "disposition": {
           "enum": [
+            "ROUTED_LEGACY",
+            "SHADOW_VERIFIED",
+            "SHIFTED",
             "PRESERVED",
             "SUBSUMED",
             "REPLACED",
             "ARCHIVED",
             "REFUSED"
           ]
         },
```

```diff
--- a/scripts/verify_foundry_bootstrap.py
+++ b/scripts/verify_foundry_bootstrap.py
 EXPECTED_DISPOSITIONS = [
+    "ROUTED_LEGACY",
+    "SHADOW_VERIFIED",
+    "SHIFTED",
     "PRESERVED",
     "SUBSUMED",
     "REPLACED",
     "ARCHIVED",
     "REFUSED",
 ]
```

`MIGRATION_DISPOSITION_LAW`'s check is strict ordered-list equality — both
diffs insert the 3 new values in the same order, first, before the 5
existing terminal values, so the two stay in lockstep as required by Hard
Law 2. No other file in the repo references this enum literal.

## Falsifiers

- Any existing terminal disposition value's meaning changes.
- `verify_foundry_bootstrap.py` and the schema enum diverge.
- This ticket's diff touches `tools/architecture-foundry/` or flips
  `runtime_dependency_admitted`.

## Acceptance (not yet run — ticket not started)

```bash
python3 scripts/verify_foundry_bootstrap.py   # must still pass against the extended enum
```

## Standing

`UNKNOWN` — not started. See `CLAUDE.md`'s Gall's Law checkpoint 3 and this
session's Explore finding on `authority/foundry-work-program.json` and
`schemas/migration-manifest.schema.json`.
