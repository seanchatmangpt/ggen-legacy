# Product Requirements Document — ggen-legacy v26.8.1

## 0. Claims reconciliation

This PRD is product authority for the v26.8.1 target. It does not assert that the target implementation already exists.

| Claim | Ceiling | Standing |
|---|---|---|
| Verified Repository Reconstitution is the product category | `DOCUMENTED` | `PARTIAL_ALIVE` |
| After Code Reading is the governing engineering boundary | `DOCUMENTED` | `PARTIAL_ALIVE` |
| Project 001 documentation bootstrap exists | `SCHEMA_VALIDATED` after verifier execution | `PARTIAL_ALIVE` |
| Production archaeology, manufacture, equivalence, and admission engines exist | `DOCUMENTED` target | `UNKNOWN` |
| A complete no-read reference manufacture has been independently replayed | none | `UNKNOWN` |
| Fortune 5 production deployment exists | none | `UNKNOWN` |
| SOC 2 or regulatory compliance exists | refused claim | `REFUSED` |

`RELEASE_CONTROL.md` governs claim ceilings. The ARD must not widen this PRD.

## 1. Product thesis

Legacy replacement fails when an organization produces new code but cannot prove what the old system promised, which behaviors still have standing, what was intentionally removed, whether downstream consumers remain safe, or whether the predecessor may be retired.

`ggen-legacy` closes that gap by converting repository history into executable manufacturing authority and an independently verified standing decision.

The broader engineering problem is that machine implementation throughput can exceed human source-inspection throughput. A replacement process that requires people to read every manufactured line preserves human reading as the final production bottleneck.

`ggen-legacy` therefore contributes Verified Repository Reconstitution to **After Code Reading**: the transition in which mandatory implementation reading leaves the critical path and is replaced by admitted requirements, executable architecture, full planning, bounded authority, independent falsification, operational evidence, standing, receipts, and replay.

Code is intermediate manufacturing material. The product is a verified replacement capability and a computed Release/Sunset decision.

## 2. Customer

The primary customer is a large enterprise carrying one or more critical repositories whose replacement, consolidation, or retirement is blocked by undocumented behavior, conflicting authority, incomplete migration, generated drift, lost maintainers, uncertain compatibility, or evidentiary obligations.

Economic buyers include the CIO, CTO, VP Engineering, Head of Architecture, Head of Platform Engineering, modernization executive, risk executive, and business owner accountable for continuity.

Operational users include principal engineers, solution architects, platform teams, assurance engineers, security teams, technical program managers, auditors, and migration leads.

## 3. Customer outcomes

A completed engagement shall deliver:

1. Repository Archaeology Graph;
2. Legacy Capability Ledger;
3. Manufacturing Authority;
4. Manufactured Replacement Repository;
5. Equivalence Evidence Portfolio;
6. Repository Standing Report;
7. Deterministic Rebuild Receipt;
8. Sunset Admission decision;
9. Post-Reading Throughput report;
10. bounded no-read admission or explicit refusal.

The replacement source tree alone is not the product.

## 4. Product tiers

### Repository Observation

Non-mutating archaeology, capability inventory, architecture map, explicit unknowns, drift findings, and estimated reconstitution surface.

### Repository Reconstitution

Authority, projections, replacement implementation, adapters, test and verifier suites, migration ledger, and deterministic rebuild.

### Repository Admission

Independent verification, clean-room replay, standing computation, Release Admission, and Sunset Admission.

### Repository Foundry Operations

Continuous authority-governed manufacture and verification for future changes.

### After Code Reading Admission

A bounded determination of whether a declared replacement capability can be accepted without mandatory human source inspection because all replacement controls, independent verification, operational evidence, receipts, and replay have standing.

## 5. Functional requirements

### PRD-FR-001 — Exact source resolution

Bind every claim to an exact repository coordinate and tree digest.

### PRD-FR-002 — Exhaustive bounded observation

Inventory every declared historical and current surface. Distinguish zero findings from an unexecuted observer.

### PRD-FR-003 — Capability identity and provenance

Each capability records identity, historical owner, source commit/path, observable contract, current owner, disposition, equivalence case, verifier, receipt, and standing.

### PRD-FR-004 — Semantic admission

Observed facts become authority only after schema, SHACL, policy, provenance, and contradiction checks.

### PRD-FR-005 — Disposition closure

Every final capability receives exactly one disposition: `PRESERVED`, `SUBSUMED`, `REPLACED`, `ARCHIVED`, or `REFUSED`.

### PRD-FR-006 — Observable-contract equivalence

Compare declared behavior including exit code, stdout/stderr, generated bytes, filesystem changes, diagnostics, events, receipt structure, side effects, recovery, and refusal behavior.

### PRD-FR-007 — Ontology-owned manufacture

One admitted semantic fact drives every lawful dependent projection. Generated projections do not become a second authority.

### PRD-FR-008 — Combinatorial maximalism

Explore bounded reversible candidate lattices, admit only combinations passing fail-closed gates, and route mutation through one broker.

### PRD-FR-009 — Independent verification

The replacement cannot certify itself. External verifiers compute standing from authority, implementation, witnesses, falsifiers, evidence, receipts, and replay.

### PRD-FR-010 — Receipts and replay

Every material actuation produces a receipt. A clean-room second run establishes `NO_SEMANTIC_CHANGE`, `NO_GENERATED_DRIFT`, and `REPLAY_MATCH` or returns typed failure.

### PRD-FR-011 — Release and sunset separation

Release Admission and Sunset Admission are separate computed decisions.

### PRD-FR-012 — Typed refusal

Refusals identify object, law, observed value, expected value, state before/after, repair, and evidence. Refused mutation preserves state.

### PRD-FR-013 — Repository estates

Support single repositories, monorepos, and bounded multi-repository estates with explicit cross-repository ownership and capability relations.

### PRD-FR-014 — Enterprise integration

Support evidence-bound integration with source control, CI, artifact stores, identity, ticketing, EA/CMDB, observability, and approved actuation brokers.

### PRD-FR-015 — Manual inspection displacement declaration

Every no-read product claim shall identify the exact human implementation-reading task removed, the bounded product object, and the point at which reading previously constrained throughput.

### PRD-FR-016 — Replacement-control completeness

Every removed human inspection task shall map to admitted requirements, executable architecture, planning or deterministic production law, independent falsification, operational evidence, standing, receipt, and replay.

### PRD-FR-017 — Human authority retention

The product shall preserve explicit human authority over mission, business consequences, architecture, invariants, risk, acceptance, verifier design, exceptions, and irreversible decisions.

### PRD-FR-018 — Planning, abstention, and no-change

The product shall represent lawful action, prohibition, no-change, abstention, uncertainty, recovery, and required evidence. A system that can only mutate is nonconforming.

### PRD-FR-019 — Actuation separation

Selection, authorization, and execution shall remain distinct. No planner, observer, projector, or verifier receives ambient production authority.

### PRD-FR-020 — Architecture conformance without source review

The product shall detect declared boundary, dependency, trust-zone, output-ownership, policy, and lifecycle violations mechanically. Architectural standing shall not depend exclusively on a human reading implementation.

### PRD-FR-021 — Producer-verifier separation

Agent-generated implementation and agent-generated tests may not be the sole basis for acceptance. A separate verifier shall rederive material claims and expose counterexamples.

### PRD-FR-022 — Runtime consequence evidence

The product shall record what actually executed, in which order, under which authority, with which inputs, side effects, failures, retries, and terminal consequences.

### PRD-FR-023 — No-read admission

A bounded capability may claim that manual implementation reading was not required only when exact source and authority are bound, replacement controls pass, independent replay matches, and standing is `ALIVE` for that exact object.

### PRD-FR-024 — Post-Reading Throughput

The product shall measure verified engineering consequences against human inspection time, elapsed time, compute, and coordination. Generated code volume, commits, and tokens remain machine-utilization metrics rather than product throughput.

### PRD-FR-025 — Same-object falsifier

Every no-read claim shall name the observation that would prove the claim false for the same product boundary. The default falsifier is that acceptance still requires human source inspection because semantic, architectural, behavioral, operational, or evidentiary authority is insufficient.

## 6. Nonfunctional requirements

### Determinism

Same admitted inputs and toolchain produce byte-identical governed outputs after declared normalization.

### Security

Default deny, least privilege, isolated execution, secret minimization, digest/signature policy, immutable evidence, and broker-only actuation.

### Resilience

Checkpointable jobs, idempotent replay, bounded retries, immutable inputs, recoverable partial state, and engagement-specific RTO/RPO profiles.

### Performance

Publish observation throughput, projection throughput, verifier latency, storage growth, replay cost, human inspection time, and verified-consequence throughput with workload and environment metadata.

### Auditability

Trace every final decision from source coordinate through authority, planner, authorization, verifier, evidence, receipt, and approver.

### Portability

Use public vocabularies and portable schemas where they preserve the required distinctions.

### Explainability

Expose requirements, architecture, selected plan or policy, counterexamples, verifier reports, runtime evidence, standing, and receipt lineage above the implementation layer.

## 7. Enterprise controls

The target defines controls for identity, change management, secure development, vulnerability management, evidence retention, segregation of duties, incident response, backup/recovery, vendor risk, privacy, legal hold, and customer export.

Control mappings organize evidence. They do not establish compliance.

## 8. Exclusions

v26.8.1 does not promise unrestricted program equivalence, automatic recovery of human intent, universal language support, guaranteed retirement, zero-touch migration, direct autonomous production actuation, certification without independent evidence, universal elimination of source reading, or correctness from tests alone.

The product does not forbid source inspection. It refuses to treat source inspection as the only or mandatory basis of trust while claiming machine-scale manufacture.

## 9. After Code Reading admission theorem

For a bounded capability:

```text
requirements_admitted=true
architecture_constraints_executable=true
planning_closed=true
no_change_and_refusal_represented=true
actuation_brokered=true
producer_verifier_separated=true
positive_witnesses_passed=true
negative_falsifiers_passed=true
operational_evidence_bound=true
receipt_valid=true
replay_match=true
manual_implementation_reading_required=false
standing=ALIVE
```

A failure or unknown value blocks the unqualified no-read claim.

## 10. Launch theorem

```text
unknown_capabilities=0
unknown_dispositions=0
unknown_standings=0
unassigned_verifiers=0
missing_equivalence_cases=0
equivalence_failures=0
replay_differences=0
release_admitted=true
sunset_admitted=true
standing=ALIVE
```

Project 001 uses a separate bootstrap theorem and must not fabricate external Sunset Admission.
