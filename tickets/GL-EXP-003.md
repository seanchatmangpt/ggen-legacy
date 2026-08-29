# GL-EXP-003 — Raise `project_coverage_rows`'s undifferentiated `None`-branch fallback to a status distinguishable from a legitimately-checked unknown-standing subsystem

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/src/coverage_projection.rs:172-202`'s `project_coverage_rows`
loops over the 10 `CANONICAL_SUBSYSTEMS` entries and, for each, looks up a
matching entry in the `standings` slice `subsystem_verifier` actually
reported:

```rust
pub fn project_coverage_rows(standings: &[SubsystemVerifierStanding]) -> Vec<CoverageRow> {
    let by_subsystem: std::collections::BTreeMap<&str, &SubsystemVerifierStanding> = standings
        .iter()
        .map(|s| (s.subsystem.as_str(), s))
        .collect();
    let mut projected = Vec::with_capacity(CANONICAL_SUBSYSTEMS.len());
    for (document, subsystem, authority_sources, implementation_sources) in CANONICAL_SUBSYSTEMS {
        let (standing, legacy_disposition, verifier) = match by_subsystem.get(subsystem) {
            Some(s) => (
                s.standing.clone(),
                aggregate_legacy_disposition(s).to_owned(),
                SUBSYSTEM_VERIFIER_SOURCE_REL.to_owned(),
            ),
            None => (
                "UNKNOWN".to_owned(),
                "UNKNOWN".to_owned(),
                "UNASSIGNED".to_owned(),
            ),
        };
        // ...
    }
    projected
}
```

The `None` arm fires whenever `by_subsystem` (built from `subsystem_verifier`'s
own report) has no entry keyed by that canonical subsystem name. It emits the
literal triple `standing="UNKNOWN"`, `legacy_disposition="UNKNOWN"`,
`verifier="UNASSIGNED"` -- indistinguishable from what a `Some(s)` match would
produce if `subsystem_verifier` genuinely inspected that subsystem and
concluded, as real evidence, that its standing is unknown (`s.standing ==
"UNKNOWN"`). A reader of `docs/v26.8.1/coverage-matrix.csv` (or a caller of
`project_coverage_rows` directly) cannot tell "the external verifier checked
this subsystem and honestly found unknown standing" apart from "the external
verifier's report doesn't mention this subsystem at all, for whatever
reason" -- e.g. a rename or typo drift between the two independently
maintained lists that must agree by naming convention alone: `CANONICAL_SUBSYSTEMS`
(`coverage_projection.rs:93`, a Rust constant) and `SUBSYSTEMS`
(`tools/v26.8.1/subsystem_evidence_manifest.py:226`, a Python dict), or a
`subsystem_verifier` bug that silently drops a subsystem from its own report,
or a truncated/corrupt `subsystem-verifier-report.json`. Today the 10 keys in
both lists happen to match exactly (`governance`, `system`, `engine`, `graph`,
`projection`, `evidence`, `products`, `verification`, `economics`, `legacy`
-- reconfirmed this session by reading both sources directly), so the gap is
currently silent, not currently triggered -- which is exactly the shape of
config-drift bug that stays invisible until the two lists next diverge, at
which point the projected coverage-matrix.csv silently reports a fabricated
"UNKNOWN"/"UNASSIGNED" row that reads identically to a legitimately-checked
finding, and the crown's byte-compare (this module's entire reason for
existing, per its own module doc at lines 1-26) would happily certify that
fabricated row as canonical.

This is the same undifferentiated-sentinel problem class GL-ERRC-019 already
fixed in this exact file for `exact_head()` (3 collapsed git-failure causes
-> `STALE_REFERENCE_UNVERIFIABLE:<CAUSE>`), but that ticket's authored
boundary is scoped to `exact_head()`'s return type/behavior only and
explicitly does not touch `project_coverage_rows`. GL-VERIFY-006 (admitted,
`NOT_STARTED`) touches a different function in this same file
(`check_provenance_receipt`, lines 371-403) for a different concern (binding
a receipt to a case-manifest digest) and does not mention
`project_coverage_rows` or its `None` branch anywhere in its "Outcome" or
"Authored boundary" sections. No other ticket in `tickets/` references
`project_coverage_rows`.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
check there before assuming sole ownership of a path below.)

```text
tools/v26.8.1/src/coverage_projection.rs   # project_coverage_rows' None-branch fallback only
tickets/GL-EXP-003.md
```

No change to `CANONICAL_SUBSYSTEMS`' data (document/subsystem/
authority_sources/implementation_sources columns), to
`aggregate_legacy_disposition`, to `exact_head` (already resolved by
GL-ERRC-019), to `check_provenance_receipt` (GL-VERIFY-006's boundary), to
`tools/v26.8.1/subsystem_evidence_manifest.py`'s `SUBSYSTEMS` dict, or to
either call site (`tools/v26.8.1/src/bin/project_coverage.rs`,
`tools/v26.8.1/src/main.rs`) beyond what is strictly required to consume the
`None`-branch's new, distinguishable return shape.

## Hard laws

1. A canonical subsystem with a genuine, real `Some(s)` match in
   `by_subsystem` -- including one whose real `s.standing` is itself the
   string `"UNKNOWN"` -- must produce the identical row it produces today;
   the `Some` arm's observable output does not change.
2. The `None` arm (no matching entry in `by_subsystem` at all) must produce a
   `standing` and/or `verifier` value that is textually distinguishable from
   every value the `Some` arm can produce for a real, checked subsystem --
   no legitimate `Some(s)` output and the `None` fallback may ever collapse
   to the same string.
3. `project_coverage_rows` remains a pure, in-memory function with no
   filesystem I/O (per the module's own architectural invariant, lines
   168-171) -- the fix is a change to the `None` arm's literal(s), not a new
   side effect.
4. `git diff --stat` after this ticket touches only
   `tools/v26.8.1/src/coverage_projection.rs` and this ticket file (plus
   minimal call-site adaptation only if the changed literal breaks an
   existing exact-string comparison elsewhere, none is known to exist today).

## Falsifiers

- After the fix, a `standings` slice missing a canonical subsystem entirely
  still produces a row whose `standing`/`verifier` values are byte-identical
  to some real, checked `Some(s)` output the `Some` arm can legitimately
  produce.
- The happy-path `Some(s)` row (a canonical subsystem present in `standings`,
  including one whose real standing is `"UNKNOWN"`) changes value as a side
  effect of this fix.
- `project_coverage_rows` gains a filesystem read, write, or other I/O side
  effect it does not have today.
- `cargo build` (from `tools/v26.8.1/`) fails after the fix.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the collapse before touching anything:
sed -n '172,202p' tools/v26.8.1/src/coverage_projection.rs

# After the fix, add/run a real unit test in coverage_projection.rs that
# calls project_coverage_rows with a `standings` slice missing one of the
# 10 CANONICAL_SUBSYSTEMS entries, and a second test with a standings entry
# whose real s.standing == "UNKNOWN", asserting the two rows differ:
cd tools/v26.8.1 && cargo test project_coverage_rows -- --nocapture

git diff --stat   # must show only coverage_projection.rs and
                   # tickets/GL-EXP-003.md
```

## Evidence this ticket is grounded in (verified this session)

- Read `tools/v26.8.1/src/coverage_projection.rs:172-202` directly this
  session: confirmed the `match by_subsystem.get(subsystem)` construct with
  `Some(s) => (s.standing.clone(), aggregate_legacy_disposition(s).to_owned(),
  SUBSYSTEM_VERIFIER_SOURCE_REL.to_owned())` and
  `None => ("UNKNOWN".to_owned(), "UNKNOWN".to_owned(),
  "UNASSIGNED".to_owned())` verbatim, exactly as quoted above.
- Confirmed `CANONICAL_SUBSYSTEMS` is a Rust constant at
  `coverage_projection.rs:93`, whose own doc comment (lines 28-44) states it
  was "transcribed once from the human-curated subsystem/document mapping
  (matching `tools/v26.8.1/subsystem_evidence_manifest.py`'s `SUBSYSTEMS`
  dict...)".
- Read `tools/v26.8.1/subsystem_evidence_manifest.py` directly this session:
  `SUBSYSTEMS: dict[str, dict] = {` begins at line 226; extracted its 10 keys
  programmatically this session --
  `['governance', 'system', 'engine', 'graph', 'projection', 'evidence',
  'products', 'verification', 'economics', 'legacy']` -- and confirmed they
  match the 10 subsystem names in `CANONICAL_SUBSYSTEMS`
  (`coverage_projection.rs:93-154`) exactly, in the same order, as of this
  commit. This confirms the two lists are currently in sync (the gap is not
  presently triggered) while also confirming they are two independently
  maintained, differently typed (Python `dict` vs. Rust `&[(&str,&str,&str,&str)]`)
  artifacts with no programmatic cross-check binding them together.
- `grep -n 'mod tests\|#\[test\]' tools/v26.8.1/src/coverage_projection.rs`
  this session: the only test module present is `exact_head_tests`
  (lines 445-556, added by GL-ERRC-019). `project_coverage_rows`,
  `resolve_root`, and `aggregate_legacy_disposition` have zero `#[test]`
  coverage in this file.
- Read `tickets/GL-ERRC-019.md` in full this session: its "Authored
  boundary" section scopes the ticket to `exact_head()`'s return
  type/behavior only; `project_coverage_rows` is not named anywhere in that
  ticket.
- Read `tickets/GL-VERIFY-006.md` in full this session: its "Outcome" and
  "Authored boundary" sections target `check_provenance_receipt` (cited
  therein as lines 370-401, re-verified this session as lines 371-403 at
  current HEAD) for a `ParityGateReceipt`/case-manifest-digest concern;
  `project_coverage_rows` and its `None` branch are not mentioned.

## Standing

`UNKNOWN` -- not started. This ticket only establishes that the `None`
branch's fallback must become distinguishable from a real `Some(s)` result;
the specific replacement literal(s) or typed shape (e.g. a distinct
`"SUBSYSTEM_UNMAPPED"` standing value, a distinct verifier marker, or a
richer typed `CoverageRow` field) are left to implementation, not decided
here.
