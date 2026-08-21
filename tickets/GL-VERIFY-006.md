# GL-VERIFY-006 — Parity Gate trace object + receipt binding (Gall checkpoint 4)

**Status:** admitted, `NOT_STARTED` — drafted this session, not executed
**Base:** `seanchatmangpt/ggen-legacy@f9b283e`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

Extend `tools/v26.8.1/equivalence_runner.py` (435 lines; already a real,
data-driven Parity-Gate-shaped comparator with four observable-surface
checkers: `generated_bytes`, `filesystem_delta`, `receipt_fields`,
`event_order`) with a formal trace object and a `ParityGateReceipt`
following the BLAKE3-binding pattern already implemented in
`tools/v26.8.1/src/coverage_projection.rs`'s `check_provenance_receipt`
(lines 370-401, re-verified against current HEAD — see `tickets/AUDIT-REPORT.md`,
this citation was previously stale at 378-410) — binding the runner's own report to the exact
case-manifest digest it ran against.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before assuming sole ownership of a path below.)

```text
tools/v26.8.1/equivalence_runner.py       # trace object, ParityGateReceipt emission
tools/v26.8.1/src/coverage_projection.rs  # ParityGateReceipt struct, following check_provenance_receipt's shape
tickets/GL-VERIFY-006.md
```

`equivalence_runner.py`'s existing adapter-pair execution, normalization
policies, and disposition semantics (`PRESERVED`/`SUBSUMED`/`REPLACED` diff
all surfaces; `ARCHIVED` checks recovery; `REFUSED` checks fail-closed)
remain unchanged — this ticket adds a binding receipt around them, it does
not rewrite the comparator.

## Hard laws

1. `ParityGateReceipt` binds via BLAKE3 to the exact case-manifest file the
   run consumed — not a filename, the actual content hash.
2. A receipt without a matching case-manifest digest is `BUILD_BROKEN`, per
   this repo's existing `check_provenance_receipt` drift-flagging convention
   (flag, never silently repair).
3. No new digest/hash algorithm choice beyond BLAKE3 in this ticket — SLSA
   digest-compatibility is GL-RECEIPT-007's explicit open question, not
   this ticket's.

## Falsifiers

- Receipt validates against a case-manifest that wasn't actually the one run.
- A tampered case-manifest (single byte changed) still validates.
- Trace object drops or reorders an `event_order` surface's events relative
  to the existing `EVENT:`-prefixed stdout convention.

## Acceptance (not yet run — ticket not started)

```bash
python3 tools/v26.8.1/equivalence_runner.py --report evidence/parity-gate/receiver-report.json
cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked
```

## Pre-work findings (ultracode backlog item 6 — audit before execution)

Concrete bugs found in `equivalence_runner.py` this ticket's implementation
must fix, not just extend:

1. **`receipt_fields` and `event_order` never call `normalize_text()`**
   (`equivalence_runner.py:257-268`, `:271-276`), despite the module
   docstring (lines 62-65) claiming normalization applies to both. A case
   declaring `normalization_policy: strip_timestamps` gets zero
   normalization on these two surfaces — any receipt/event line containing
   a timestamp spuriously fails. This is a real correctness bug in already-
   existing code, not a gap this ticket introduces; fix it as part of this
   ticket's scope alongside the new trace object.
2. **`AdapterResult.timed_out` is captured but never consulted** by any of
   the ten surface checkers or `run_case`. A `REFUSED`-disposition case's
   `exit_code` checker (`:172-176`) cannot distinguish a legitimate refusal
   from a hung adapter killed by timeout (`exit_code=-1` either way) — a
   hung current adapter can pass as "refused." The new `ParityGateReceipt`
   should record `timed_out` explicitly and fail closed on it.
3. **Empty directories and 0-byte files are invisible** to
   `_tree_manifest`/`generated_bytes` — an adapter that produces nothing at
   all can pass as equivalent to another adapter that produces nothing at
   all, silently treating "both failed to run" as "both succeeded
   identically." Worth a dedicated non-empty-output assertion.
4. **Zero test coverage** for `generated_bytes`, `filesystem_delta`,
   `side_effects`, `receipt_fields`, `event_order`, `recovery_result` —
   only `stdout`+`exit_code` are exercised by
   `tools/v26.8.1/legacy_subsystem_verification_test.py`'s two tests. This
   ticket's acceptance should add real Chicago-style tests for the other
   surfaces, not just the trace/receipt addition.

## Pre-derived design (ultracode backlog item 7 — ready to implement)

`ParityGateReceipt` follows `coverage_projection.rs`'s existing
`CoverageProjectionReceipt`/`check_provenance_receipt` pattern exactly
(absent-receipt-file ⇒ `Ok(None)`, not a drift condition; recompute
ground-truth digests from what's actually on disk, never trust the
receipt's own claim; field-by-field mismatch named, never silently
repaired). Lives in the same file (after `check_provenance_receipt`,
before `exact_head`), not a new module — that file is already the crate's
one home for this receipt pattern.

```rust
#[derive(Debug, Deserialize)]
pub struct ParityGateReceipt {
    pub case_manifest_blake3: String,
    pub equivalence_report_blake3: String,
    pub case_manifest_path: String,
    pub equivalence_gate_passed: bool,
}

pub fn case_manifest_digest(root: &Path) -> Result<String> { /* blake3::hash of case_manifest.json bytes */ }

pub fn check_parity_gate_receipt(
    root: &Path,
    current_case_manifest_digest: &str,
    current_equivalence_report_bytes: &[u8],
) -> Result<Option<String>> { /* same 5-step shape as check_provenance_receipt */ }
```

Real gap this closes: `equivalence_runner.py`'s report currently only
records `manifest_path` (a string), never a digest of the manifest's
bytes — nothing today detects a case-manifest being swapped/edited between
manufacture and verification. Test plan: `#[cfg(test)]` unit tests in
`coverage_projection.rs` using `tempfile::TempDir` (already a dev-dependency)
for the four cases (absent/match/manifest-mismatch/report-mismatch), plus a
`tests/verifier_boundary.rs`-style boundary test — the latter needs a new
`src/bin/parity_gate.rs` binary (analogous to `project_coverage.rs`) since
nothing currently drives `equivalence_runner.py` from a compiled binary.

## Pre-derived design: golden-trace corpus

Relocated verbatim to `tickets/GL-ERRC-012.md` (see the "Pre-derived
design" section there) as part of the GL-ERRC-012 planning-document split;
this ticket's own `ParityGateReceipt` design, Hard Laws, and acceptance
commands above are unaffected by the move.

## Standing

`UNKNOWN` — not started. See `CLAUDE.md`'s Gall's Law checkpoint 4 and this
session's Explore finding on `equivalence_runner.py` and
`coverage_projection.rs`'s existing BLAKE3-binding pattern.
