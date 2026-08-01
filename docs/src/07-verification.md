# Verification, Receipts, and Replay

## Verification constitution

The ladder is:

```text
protocol/unit
→ property/fuzz
→ stdio and HTTP integration
→ black-box CLI E2E
→ security
→ chaos
→ stress
→ benchmark
→ replay
→ external verifier report
```

Mocks may support isolated units. Crown evidence crosses the real process, filesystem, serialization, protocol, database/service, receipt, and replay boundaries named by the claim.

## Required negative fixtures

- missing or stale observation;
- missing or duplicate owner;
- missing dimension or duplicate candidate;
- constraint or resource violation;
- path and symlink escape;
- unowned write;
- direct actuation;
- premature release or sunset authorization;
- missing, tampered, reordered, or duplicate receipt;
- replay divergence;
- source-head identity mutation;
- consent, jurisdiction, retention, or postcondition mismatch where applicable.

A refusal is a first-class result and preserves state. It binds code, object, law, observed, expected, state before, state after, repair, and evidence.

## Verifier report

`ggen.verifier.report.v1` records exact subject revision and tree digest, toolchain, policy and ontology digests, suite inventory, commands, crossed boundaries, evidence artifacts, checks, refusal codes, benchmark measurements, replay result, aggregate standing, and verifier identity.

The replacement, generated report, and implementing agent cannot assign their own standing.

## Receipts

A receipt binds run, project, exact source, authority digest, toolchain, environment, inputs, outputs, actuator, exit status, verifier results, time, lineage, and standing.

A receipt records what occurred. It does not enlarge a claim beyond the verifier’s evidence ceiling.

## OCEL evidence

Object-centric events connect work order, actor, capability, repository, artifact, receipt, and prior event. Logical time or deterministic ordering governs replay; wall-clock time remains an observation.

## Replay

Replay executes from a clean state and requires:

```text
NO_SEMANTIC_CHANGE
NO_GENERATED_DRIFT
REPLAY_MATCH
```

The replay contract declares volatile fields and normalization. Duplicate receipt identity is checked before chain position so a duplicate attempt cannot corrupt verifier state.

## Release and sunset

Release Admission answers whether the replacement may release. Sunset Admission answers whether a real predecessor may retire. A replacement may be releasable while historical closure remains blocked.

Actual deletion or decommissioning is separate and requires explicit customer authority and a receipt.
