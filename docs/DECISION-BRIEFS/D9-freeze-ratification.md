# D9 — GL-STARDF-002 Freeze Expansion: Operator Ratification Brief

Status: **PENDING-OPERATOR** (admits nothing; only operator ratification + an amended
`ABI-FREEZE.md` admits exports — ticket §1)

Cites, does not re-derive: `stardf/arrow/tickets/GL-STARDF-002-freeze-expansion.md`
(the ticket), `stardf/arrow/docs/ABI-FREEZE.md` (frozen 13),
`stardf/docs/jira/v26.10.31/06-phase0-columnar-sql-duckdb.md` §5/§8.2/§10.4 (phase0 doc).

## 1. The decision

The v26.9.29 ABI-FREEZE covers 13 batch/stream exports only (ABI-FREEZE.md:6-26). The
SQL/query port (phase0 §5, P0-10) needs query/UPDATE/serialize exports whose carrier
types do not exist in the stardf-arrow CAPI yet. GL-STARDF-002 enumerates a 21-export
option set (17 query/UPDATE + 4 serialize; purrdf spellings VERIFIED by grep against
`~/purrdf/crates/rdf-capi/include/purrdf.h`, 2026-10-31; stardf spellings are
PROPOSAL, ticket §2/§8) and three ratification tiers. This brief asks the operator to
ratify one.

## 2. Tier options and exact carrier drag

Carrier drag per ticket §3 (line refs are purrdf.h):

| Carrier | purrdf.h ref | Dragged by |
|---|---|---|
| `ResultKind` enum | :558-578 | every query/update export |
| `QueryGovernors` struct | :1204 | governed/update-governed/entailment families |
| `GovernorEvidence` | :1299 | governed families (`expression_errors: uint64_t[8]`, append-only) |
| `Evidence` union member `query` | :1334 | governed families |
| `PartialCertificate` | : carrier for update atomicity | Tier B+ (governed families) |
| `RowCursor` | :1071 | all result-set exports (SELECT → `**out_rows`) |
| geo/division selectors | geo_session, geo_point_index, division_policy | `*_with_geo`, division |
| CanonArrow encoder types | `query_canon_arrow` | `query_canon_arrow` |

- **Tier A — Minimal (3 exports + 4 carriers)** (ticket §4): `stardf_query`,
  `stardf_query_governed`, `stardf_query_governors_init`, plus lifecycle
  (cursor/buffer/error/free) reusing the frozen 13. Carriers: ResultKind,
  QueryGovernors, GovernorEvidence, RowCursor. Does NOT cover Update, CanonArrow
  egress, geo/xpath-regex axes. Per the ticket: "smallest lawful increment that lets
  W2 scaffold (bridge query) proceed."
- **Tier B — Tier A + `stardf_update_governed` + `stardf_query_canon_arrow`**:
  adds carrier `PartialCertificate` (update atomicity certificate chain per phase0
  §5 GO on atomicity-tested Update).
- **Tier C — full 21-export parity**: all 17 query/UPDATE + 4 serialize; serialize
  exports are ABI-append-only per the pre-1.0 rule (phase0 §5).

## 3. Enforcement gate (tier-independent)

`nm -gU target/{debug,release}/libstardf_arrow_capi.dylib | grep -c
stardf_query|stardf_update|stardf_serialize` must be **0 before ratification**
(ticket §5.1); after ratification, a mechanical `nm -gU` diff of the built dylib against
the ratified export table, exit 1 on any symbol present in dylib-but-absent-from-table
(and vice versa, modulo the declared `_blake3_compress_in_place_portable` hygiene item,
ABI-FREEZE.md:27-30). Non-conforming failures are REFUSED, not skipped — a gate that
cannot exit 1 is VACUOUS and fails the court (ticket §5.3; falsifiers F1/F2/F3 at ticket §7).

## 4. Recommendation: ratify Tier A

The ticket itself names Tier A as approved-on-ratification ("smallest lawful increment",
ticket §4). Grounds:

1. **No admitted consumer needs more.** Zero SQL/duckdb consumer need is stated anywhere
   (phase0 §9); avec's first unmet need is the columnar seam (CONSUMER_REQUIREMENTS
   T1-T4 all LANDED, phase0 §9). Tier A is exactly what W2 scaffold (bridge query)
   needs to proceed; Tier B's Update/CanonArrow and Tier C's serialize axes have no
   admitted consumer demand yet.
2. **Smallest drag.** Tier A drags 4 carriers; Tier B adds PartialCertificate and the
   Update atomicity surface; Tier C drags geo/division selectors and CanonArrow encoder
   types. Under append-only pre-1.0 ABI law (phase0 §5), later tiers can be ratified as
   new ABI-FREEZE revisions without re-opening Tier A — Tier A is reversible-forward,
   not a dead end.
3. **Gate scope stays tight.** A 3-export ratified table is a small `nm -gU` diff
   surface; F3 (carrier drag violating the tier boundary) is trivially checkable at
   Tier A size.

## 5. What each tier unblocks downstream (SQL wave dispatch)

Phase0 §9 wave plan: W1 contract → W2 scaffold → W3 integration → W4 equivalence → W5 CI.
Query/SQL dispatch is blocked at W2 (bridge query) until a tier is ratified.

| Tier | Unblocks |
|---|---|
| A | W2 bridge-query scaffold; W3 = one purrdf golden class via new exports (ticket §6) |
| B | W2 + SPARQL 1.1 Update (phase0 §5 GO, atomicity-tested) + query→CanonArrow egress surface |
| C | Full W1 census parity: all 21 P0-10 exports (phase0 §5), no further freeze revisions |

Tier A unblocks the W2 bridge-query scaffold only. Tier B additionally unblocks the
Update/CanonArrow surface. Tier C completes the P0-10 census with one ratification.

## 6. Nonclaims

- No export has landed; query-surface standing is UNKNOWN until ratification + first
  `nm` diff receipt (ticket §8).
- This brief admits no exports and amends no ABI-FREEZE.md. Only operator ratification
  ("RATIFIED: Tier A/B/C" written into the ticket + a new ABI-FREEZE.md revision) admits.
- stardf-side symbol names remain PROPOSAL (mechanical `purrdf_ → stardf_` rename);
  purrdf.h is the authoritative enumeration on disagreement (ticket §8).
- The recommendation is the ticket's own, restated with grounds; this brief adds no new
  verification beyond citations.
