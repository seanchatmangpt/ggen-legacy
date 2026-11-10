# INDEX

Standing: REGISTERED

Entry format: ticket, wave, tier, dry-run standing (`ggen-create cutover dryrun`,
receipts/; blank = no report), title, dependencies.

- T-001 [W0 T0 PASS_PREDICTED] cutover CLI skeleton: plan, power, verify, rollback (needs: none)
- T-002 [W0 T0 PASS_PREDICTED] Cutover receipt chain and sunset-admission schema (needs: T-001)
- T-003 [W0 T0 PASS_PREDICTED] Preflight gate: refuse switch unless prerequisites hold (needs:
  T-001)
- T-004 [W0 T0 FAIL] Frontend: one backend-origin variable feeds every call site (needs: none)
- T-005 [W0 T0 FAIL] Ontology: executable action semantics on sv:Action (needs: none)
- T-006 [W0 T2 FAIL] Align one: and sv:; verify against introspection (needs: T-005)
- T-007 [W0 T0 FAIL] Work-order state machine: 48 transitions as guarded, queryable facts (needs:
  T-005)
- T-008 [W0 T0 PASS_PREDICTED] Manifest: every Ash resource and action tagged generated vs residue
  (needs: T-006)
- T-009 [W0 T0 PASS_PREDICTED] Route inventory extractor and OpenAPI reconciliation for onengine-
  backend (needs: none)
- T-010 [W0 T0 PASS_PREDICTED] Cutover scope: actions and prefixes the frontend actually calls
  (needs: none)
- T-011 [W0 T1 UNVERIFIED] srve_* DDL census and replay-diff harness (needs: none)
- T-012 [W0 T0 FAIL] Extend shared-table tripwire from 13 to all srve_* tables (needs: T-011)
- T-013 [W0 T0 PASS_PREDICTED] Prisma model coverage manifest and tenant-key policy (needs: T-006)
- T-014 [W0 T0 PASS_PREDICTED] Decision: procurement, dispatch, forms, W9 scope (needs: T-010,
  T-013)
- T-015 [W1 T1 FAIL] Backend pack: generate resources from the srve ontology (needs: T-005, T-006,
  T-008)
- T-016 [W1 T1 FAIL] Backend pack: migrations that replay to byte-equivalent DDL (needs: T-011,
  T-015)
- T-017 [W1 T2 FAIL] Backend pack: router and RPC envelope parity (needs: T-010, T-015)
- T-018 [W1 T2 FAIL] Backend pack: policies with an allow/deny parity matrix (needs: T-005, T-015)
- T-019 [W1 T0 FAIL] Custom handlers for ontology-inexpressible logic (needs: T-008, T-015)
- T-020 [W1 T2 UNVERIFIED] Auth and session bridge (needs: T-017)
- T-021 [W1 T2 BLOCKED] Two-probe identity law and CORS on the candidate (needs: T-017)
- T-022 [W1 T1 FAIL] Contracts and OpenAPI generated from the backend schema (needs: T-009, T-015)
- T-023 [W1 T1 FAIL] ETL: verify the write path and reconcile status vocabularies (needs: T-011)
- T-024 [W1 T1 FAIL] ETL: extend to the ~35 aggregates and backfill post-ETL fields (needs: T-023,
  T-016)
- T-025 [W2 T2 FAIL] HTTP golden court ported from the Elixir courts (needs: T-017, T-018)
- T-026 [W2 T2 FAIL] Backend-neutral seed fixture (needs: T-017)
- T-027 [W2 T0 FAIL] bin/golden-court --backend URL (needs: T-025, T-026)
- T-028 [W2 T1 UNVERIFIED] Deterministic replay: byte-stable second sync (needs: T-015, T-016,
  T-017)
- T-029 [W2 T0 PASS_PREDICTED] Independent verifier with negative controls (needs: T-025, T-028)
- T-030 [W3 T0 FAIL] Parametrize kind scripts, align Postgres, replace asset-hash smoke (needs:
  T-017)
- T-031 [W3 T0 PASS_PREDICTED] Write freeze, delta sync, atomic switch, rollback (needs: T-003,
  T-023, T-032)
- T-032 [W3 T0 PASS_PREDICTED] Side-effect inventory with cutover behavior (needs: T-010)
- T-033 [W3 T1 UNVERIFIED] Downstream parity: receipts, OCEL ndjson, pins (needs: T-028)
- T-034 [W3 T0 PASS_PREDICTED] Retirement manifest for xaas non-core domains (needs: T-010)
- T-035 [W3 T0 PASS_PREDICTED] Sunset admission is a separate authorized actuation (needs: T-002,
  T-028, T-029)
- T-036 [W3 T0 FAIL] Update backend-law rule, memory and srve README after cutover (needs: T-031)

## See Also

CHARTER.md · DEPENDENCY-GRAPH.md
