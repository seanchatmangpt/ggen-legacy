# Architecture Requirements Document — ggen-legacy v26.8.1

## 0. Claims reconciliation

This ARD is a target architecture projection of `product/PRD.md`. It does not claim that production components already execute.

| Architecture claim | Ceiling | Standing |
|---|---|---|
| Component, boundary, and data models are documented | `DOCUMENTED` | `PARTIAL_ALIVE` |
| After Code Reading control architecture is documented | `DOCUMENTED` | `PARTIAL_ALIVE` |
| Bootstrap JSON authority validates | `SCHEMA_VALIDATED` after verifier execution | `PARTIAL_ALIVE` |
| Production services compile or execute | none | `UNKNOWN` |
| A no-read reference manufacture has independent replay | none | `UNKNOWN` |
| Production scale, security, and availability are proven | none | `UNKNOWN` |

`AGENTS.md`, `RELEASE_CONTROL.md`, admitted authority, and the PRD take precedence.

## 1. Architecture style

The target is a projectional ontology compiler and evidence-bearing repository foundry. A canonical graph owns domain and architecture meaning. Source, configuration, tests, documentation, diagrams, plans, reports, and receipts are projections or evidence surfaces.

```text
parse → route → admit/refuse → diagnose/repair
      → construct → actuate → receipt → replay/hook
```

Construction is reversible. Consequential actuation is brokered. Standing is independently computed.

The architecture operates within **After Code Reading**. Mandatory human implementation inspection may leave the production critical path only when it is replaced by admitted requirements, executable architecture, full planning, bounded actuation, independent falsification, operational evidence, standing, receipts, and replay.

Code is intermediate manufacturing material. The product is a verified replacement capability and a computed release/retirement decision.

## 2. Logical planes

### Mission Plane

Humans own business consequences, architecture, invariants, risk, standards, acceptance criteria, verifier design, evidence interpretation, exceptions, and irreversible decisions.

The Mission Plane is the primary human interface. It shall not depend on manual implementation reconstruction to define acceptance.

### Observation Plane

Adapters inspect Git history, trees, packages, commands, configuration, tests, workflows, generated files, public APIs, diagnostics, migrations, deployment manifests, runtime traces, and downstream contracts.

### Admission Plane

Graph storage, SHACL shapes, policy rules, provenance validation, contradiction detection, and source-coordinate validation convert observations into bounded authority.

### Architecture Plane

Machine-readable architecture owns component boundaries, dependency direction, trust zones, output ownership, generated-surface ownership, data contracts, performance budgets, security/privacy constraints, lifecycle rules, and retirement conditions.

Architecture conformance must be mechanically inspectable. A no-read claim is blocked when architectural drift can only be discovered by a human reading source.

### Planning Plane

The planner creates deterministic G0–G9 work DAGs, candidate lattices, dependency closure, disposition tasks, equivalence cases, verifier assignments, no-change outcomes, abstention, refusal, recovery, and bounded probabilistic policies where required.

Planning selects candidate consequences. It does not authorize actuation.

### Manufacturing Plane

Projectors produce governed repository artifacts. One writer or named merge law owns every exclusive output.

The plane may manufacture application, service, integration, infrastructure, policy, tests, schemas, deployment, observability, documentation, and evidence projections. Generated implementation remains work in process until independent verification assigns standing.

### Actuation Plane

A broker executes approved filesystem, process, network, deployment, and external API mutations. Observers, planners, projectors, and verifiers receive no ambient production authority.

The hard invariant is:

```text
selection ≠ authorization ≠ execution
```

### Inspection Plane

Mechanical inspection executes compilation, type checking, static analysis, dependency and license policy, architecture conformance, unit/property/integration/contract/black-box tests, fuzzing, mutation testing, security, performance, chaos, stress, and generated-output drift detection.

Inspection evidence is necessary but cannot grant standing when the producer is the only verifier.

### Verification Plane

Independent suites execute witnesses, falsifiers, unit/property/integration/E2E, security, chaos, stress, benchmark, receipt validation, and replay.

The verifier rederives material claims from authority and observed artifacts. It must expose counterexamples and typed refusal.

### Process Evidence Plane

Structured events establish what actually executed, in which order, under which authority, with which inputs, side effects, failures, retries, and terminal consequences.

Source projections describe what was manufactured. Process evidence establishes what moved.

### Evidence Plane

Immutable evidence, OCEL events, content identities, provenance, verifier reports, and receipt chains bind observed consequences.

### Standing Plane

A crown verifier assigns exactly one bounded state:

- `PARTIAL_ALIVE`
- `ALIVE`
- `BLOCKED`
- `BUILD_BROKEN`
- `UNKNOWN`
- `UNSUPPORTED`

Reports project standing. They do not create it independently.

### Release/Sunset Plane

Crown verifiers compute Release Admission and Sunset Admission. Reports are projections of the decision, not decision sources.

### Improvement Plane

Abnormalities follow:

```text
abnormality → stop → root cause → countermeasure
→ authority/standard revision → manufacture → verify → receipt
```

Manual patching of generated output is prohibited.

## 3. Building-block calculus

One canonical GBB kernel represents Building Blocks. Profiles compose it; they do not fork architecture truth.

- **GBB:** stable semantic Building Block.
- **bblock:** reusable implementation or projection capability.
- **pack:** immutable atomic capability distribution with identity, contract, dependencies, controls, verifier, and receipts.
- **profile:** deterministic composition of blocks and packs for an operating context.
- **ABB:** architecture requirement block.
- **SBB:** solution block satisfying an ABB at an exact coordinate.

Composition conflicts fail closed. Ordered inputs determine composition identity. External packs carry compatibility law, bounded write authority, hidden-dependency disclosure, identity/version, consumer capabilities, conformance evidence, portable receipts, and substitution rules.

Every block participating in a no-read claim declares the manual task removed, replacement control, introduced risk, authority, verifier, evidence, receipt, replay, and falsifier.

## 4. Data architecture

The canonical model includes Repository, Revision, Tree, Artifact, Observer, Observation, Capability, Contract, AuthorityAssertion, Disposition, EquivalenceCase, Witness, Falsifier, Verifier, EvidenceArtifact, Receipt, Replay, ReleaseAdmission, SunsetAdmission, Actor, WorkOrder, Control, Risk, Exception, HumanInspectionTask, ReplacementControl, PlanningPolicy, ActuationAuthorization, OperationalConsequence, NoReadAdmission, and PostReadingThroughputMeasurement.

Use PROV-O for provenance; DCAT/DCTERMS for catalog metadata; SKOS for controlled terms; SHACL for admission; ODRL for policy where appropriate; OCEL for object-centric events; QUDT for measurements; SOSA for observations.

## 5. Trust boundaries

1. untrusted repository input;
2. observation sandbox;
3. admission boundary;
4. authority store;
5. planning boundary;
6. projector/manufacturing boundary;
7. broker actuation boundary;
8. immutable evidence boundary;
9. external verifier boundary;
10. customer production boundary;
11. Release Admission boundary;
12. Sunset Admission boundary.

Data crossing a boundary identifies schema, provenance, integrity, confidentiality, purpose, retention, authority, and verifier.

## 6. Deployment model

The target supports customer-controlled single tenancy, isolated workers, private networking, customer-managed keys, approved artifact stores, and outbound-deny execution. A managed control plane may coordinate jobs without receiving source or secret access where policy forbids it.

Deployment profiles declare tenancy, region, residency, key ownership, egress, worker isolation, evidence destination, retention, support, RTO, and RPO.

## 7. Security architecture

Least privilege and separation of duties apply to observer, planner, projector, broker, verifier, release approver, and sunset approver. No role may both mutate production and independently certify the same consequence.

Supply-chain controls include pinned dependencies, reproducible builds, SBOM, provenance, signature verification, vulnerability scanning, license policy, and artifact quarantine.

Removing source inspection introduces risk of hidden architectural drift, malicious generated behavior, verifier collusion, specification omission, and false confidence. These are modeled as explicit threats and cannot be compensated by reward or throughput.

## 8. Resilience

Jobs checkpoint by Gall stage. Each stage uses immutable inputs and idempotent outputs. Recovery resumes from the last admitted receipt rather than worker memory. Replay distinguishes semantic fields from volatile timestamps.

## 9. Observability

Every stage emits structured events tied to project, repository, revision, capability, work order, actor, plan or policy, authorization, evidence, receipt, and prior event.

Metrics include queue time, WIP, observer coverage, admission refusals, capability closure, equivalence pass rate, replay divergence, evidence age, release blockers, manual source lines read, human inspection time, verified consequences, unnecessary actions avoided, and Post-Reading Throughput.

## 10. Verification architecture

The required report is `ggen.verifier.report.v1` or an admitted compatible successor. It records exact revision, tree digest, toolchain, policy/ontology digests, suite inventory, commands, crossed boundaries, evidence artifacts, pass/fail/blocked/unsupported checks, refusal codes, benchmarks, replay, standing, and verifier identity.

For a no-read claim it additionally records:

- exact product boundary;
- human inspection task removed;
- manual source lines read and written;
- human attention time;
- admitted requirement and architecture identities;
- planner or deterministic production law;
- no-change/abstention/refusal coverage;
- actuation authority;
- producer-verifier separation;
- operational evidence;
- receipt validity;
- replay result;
- same-object falsifier.

Mocks may support isolated unit tests. Crown evidence crosses real declared boundaries.

## 11. No-read admission architecture

A bounded capability may receive `NoReadAdmission=true` only when:

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

Any unknown or failed predicate blocks the claim. The result is bound to the exact capability, source, authority, toolchain, verifier, and replay.

## 12. Failure semantics

Required typed failures include:

- `AUTHORITY_CONTRADICTION`
- `OBSERVATION_INCOMPLETE`
- `ARCHITECTURE_DRIFT`
- `POLICY_NOT_CLOSED`
- `UNAUTHORIZED_ACTUATION`
- `SELF_CERTIFICATION_LOOP`
- `EVIDENCE_MISSING`
- `RECEIPT_INVALID`
- `REPLAY_DIVERGENCE`
- `NO_READ_CONTROL_INCOMPLETE`

Failure preserves the last admitted state unless an independently authorized, receipted repair occurs.

## 13. Same-object falsifier

The architecture fails its After Code Reading objective when acceptance still requires human source inspection because semantic, architectural, behavioral, operational, or evidentiary authority cannot establish the necessary distinction elsewhere.

It also fails when the producer's own tests or reports are the only basis for standing.
