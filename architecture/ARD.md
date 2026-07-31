# Architecture Requirements Document — ggen-legacy v26.8.1

## 0. Claims reconciliation

This ARD is a target architecture projection of `product/PRD.md`. It does not claim that production components already execute.

| Architecture claim | Ceiling | Standing |
|---|---|---|
| Component, boundary, and data models are documented | `DOCUMENTED` | `PARTIAL_ALIVE` |
| Bootstrap JSON authority validates | `SCHEMA_VALIDATED` after verifier execution | `PARTIAL_ALIVE` |
| Production services compile or execute | none | `UNKNOWN` |
| Production scale, security, and availability are proven | none | `UNKNOWN` |

`AGENTS.md`, `RELEASE_CONTROL.md`, admitted authority, and the PRD take precedence.

## 1. Architecture style

The target is a projectional ontology compiler and evidence-bearing repository foundry. A canonical graph owns domain and architecture meaning. Source, configuration, tests, documentation, diagrams, plans, reports, and receipts are projections or evidence surfaces.

```text
parse → route → admit/refuse → diagnose/repair
      → construct → actuate → receipt → replay/hook
```

Construction is reversible. Consequential actuation is brokered. Standing is independently computed.

## 2. Logical planes

### Observation Plane

Adapters inspect Git history, trees, packages, commands, configuration, tests, workflows, generated files, public APIs, diagnostics, migrations, deployment manifests, runtime traces, and downstream contracts.

### Admission Plane

Graph storage, SHACL shapes, policy rules, provenance validation, contradiction detection, and source-coordinate validation convert observations into bounded authority.

### Planning Plane

The planner creates deterministic G0–G9 work DAGs, candidate lattices, dependency closure, disposition tasks, equivalence cases, and verifier assignments.

### Manufacturing Plane

Projectors produce governed repository artifacts. One writer or named merge law owns every exclusive output.

### Actuation Plane

A broker executes approved filesystem, process, network, deployment, and external API mutations. Observers, planners, and projectors receive no ambient production authority.

### Verification Plane

Independent suites execute witnesses, falsifiers, unit/property/integration/E2E, security, chaos, stress, benchmark, receipt validation, and replay.

### Evidence Plane

Immutable evidence, OCEL events, content identities, provenance, verifier reports, and receipt chains bind observed consequences.

### Release/Sunset Plane

Crown verifiers compute Release Admission and Sunset Admission. Reports are projections of the decision, not decision sources.

## 3. Building-block calculus

One canonical GBB kernel represents Building Blocks. Profiles compose it; they do not fork architecture truth.

- **GBB:** stable semantic Building Block.
- **bblock:** reusable implementation or projection capability.
- **pack:** immutable atomic capability distribution with identity, contract, dependencies, controls, verifier, and receipts.
- **profile:** deterministic composition of blocks and packs for an operating context.
- **ABB:** architecture requirement block.
- **SBB:** solution block satisfying an ABB at an exact coordinate.

Composition conflicts fail closed. Ordered inputs determine composition identity. External packs carry compatibility law, bounded write authority, hidden-dependency disclosure, identity/version, consumer capabilities, conformance evidence, portable receipts, and substitution rules.

## 4. Data architecture

The canonical model includes Repository, Revision, Tree, Artifact, Observer, Observation, Capability, Contract, AuthorityAssertion, Disposition, EquivalenceCase, Witness, Falsifier, Verifier, EvidenceArtifact, Receipt, Replay, ReleaseAdmission, SunsetAdmission, Actor, WorkOrder, Control, Risk, and Exception.

Use PROV-O for provenance; DCAT/DCTERMS for catalog metadata; SKOS for controlled terms; SHACL for admission; ODRL for policy where appropriate; OCEL for object-centric events; QUDT for measurements; SOSA for observations.

## 5. Trust boundaries

1. untrusted repository input;
2. observation sandbox;
3. admission boundary;
4. authority store;
5. projector boundary;
6. broker actuation boundary;
7. immutable evidence boundary;
8. external verifier boundary;
9. customer production boundary.

Data crossing a boundary identifies schema, provenance, integrity, confidentiality, purpose, retention, and verifier.

## 6. Deployment model

The target supports customer-controlled single tenancy, isolated workers, private networking, customer-managed keys, approved artifact stores, and outbound-deny execution. A managed control plane may coordinate jobs without receiving source or secret access where policy forbids it.

Deployment profiles declare tenancy, region, residency, key ownership, egress, worker isolation, evidence destination, retention, support, RTO, and RPO.

## 7. Security architecture

Least privilege and separation of duties apply to observer, planner, projector, broker, verifier, release approver, and sunset approver. No role may both mutate production and independently certify the same consequence.

Supply-chain controls include pinned dependencies, reproducible builds, SBOM, provenance, signature verification, vulnerability scanning, license policy, and artifact quarantine.

## 8. Resilience

Jobs checkpoint by Gall stage. Each stage uses immutable inputs and idempotent outputs. Recovery resumes from the last admitted receipt rather than worker memory. Replay distinguishes semantic fields from volatile timestamps.

## 9. Observability

Every stage emits structured events tied to project, repository, revision, capability, work order, actor, evidence, receipt, and prior event. Metrics include queue time, WIP, observer coverage, admission refusals, capability closure, equivalence pass rate, replay divergence, evidence age, and release blockers.

## 10. Verification architecture

The required report is `ggen.verifier.report.v1` or an admitted compatible successor. It records exact revision, tree digest, toolchain, policy/ontology digests, suite inventory, commands, crossed boundaries, evidence artifacts, pass/fail/blocked/unsupported checks, refusal codes, benchmarks, replay, standing, and verifier identity.

Mocks may support isolated unit tests. Crown evidence crosses real declared boundaries.
