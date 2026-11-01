# v26.11.1 Target-State Ledger — press-release diff (2026-10-31)

> **STATUS (2026-10-31): PARTIALLY SUPERSEDED by the 80/20 re-scope**
> (OPERATOR-DECISIONS.md D15–D18, third operator block). GAP rows 1–2 (full
> SPARQL algebra; full substrate parity) are DEFERRED with the full-parity
> campaign (12-full-parity-campaign.md); "parity to purrdf" is scoped to the
> four first-class targets (arrow landed, duckdb critical path, sql whole +
> 4 goldens, n3 whole + suite + discovery). TRUE NOW rows are unaffected
> (receipted; D18 keeps arrow landed as-is). The Law's parity predicate is now
> 4-target parity, not full parity. ABI-v2 is PENDING-OPERATOR (D18). Deep
> per-claim reconciliation is owned by the W7-class doc lane.

The operator's v26.11.1 press release is the completion contract. Every claim
diffed against tree truth (receipts: evidence/*.json + wave reports). W10's
verdict + the docs reconcile against this ledger; the goal hook evaluates
"finished with parity to purrdf" against it.

## TRUE NOW (receipted)

| Claim | Receipt |
|---|---|
| `stardf-columnar` total-order deterministic storage (BTreeSet dictionary, byte-frozen goldens) | S9/S10/F3 receipts; columnar_manifest.sha256 |
| CanonArrow ABI-frozen C FFI egress (13-export freeze, 64-row slabs, 192-byte ASK frame, domain digests) | ABI-FREEZE.md; c_smoke; F8 82/0 ladder |
| Zero-copy boundary egress (stream courts, CAS release, ownership tags) | stream_courts 6/6; cross_allocator flip |
| Formal gates: license-compat, anti-vacuity, mutant-refusal courts | R1 exit 0; F1/F1a; mutant flips witnessed |
| 13-export frozen ABI header | `crates/stardf-arrow-capi/include/stardf_arrow.h` (release says `stardf/arrow/include/` — path erratum to fix in the release text) |

## IN FLIGHT (completion campaign wf_2130cfdc-9f1)

| Claim | Wave |
|---|---|
| Native in-process `stardf_scan()` DuckDB VTab | W5 (rehome court → scan scaffold → 6 courts + mutant) |
| SQL-in-RDF compiler (purrdf-sql surface) | W2/W3 (algebra+results+slice) |
| Full workspace ladder + commit c3–c6 | W10 arbiter → coordinator |
| avec W3 gate (BEAM/NIF consumption via real court) | W6 lane a01–a03 |

## GAP (work order — the campaign does NOT yet cover)

1. **"Full SPARQL 1.1/1.2 multiset algebra engine"** — D12 explicitly did NOT
   vendor the 215K eval crate; the admitted slice is the minimal evaluator
   (~48–50K wholesale per P5). "Full" requires the eval wave (rewrite-from-
   documented-decisions ~30–35K, P5 §PORT INPUT) — queued into the full-parity
   campaign (12-full-parity-campaign.md W4/W5).
2. **"Full purrdf substrate parity"** — the 450K-LOC full-parity campaign
   (12-full-parity-campaign.md) — queued post-arbiter.
3. **"Formally Verified Sovereignty"** — no formal verification exists
   anywhere in the tree. Either register as a target (proof artifacts would be
   a new work order) or amend the release to "machine-gated sovereignty"
   (what exists: anti-vacuity + mutant-refusal courts). Flagged to operator.
4. **Release errata**: header path (`stardf/arrow/include/` →
   `crates/stardf-arrow-capi/include/`); the `{0,0}` delta claim is the avec
   BEAM ops_scan precedent, not the stardf VTab (whose courts assert
   allocation-identity, not a zero-delta constant).

## Law

No GA standing until W10's structured verdict returns parity=true ∧
finished=true with zero unresolved blockers AND the gap rows are either
landed or amended out of the release. The release is the target, not a
receipt.
