# Inspection and Implementation Law

## Inspection path

Inspect the implementation from:

```text
entrypoint
→ routing
→ admission
→ domain logic
→ construction
→ actuation
→ consequence observation
→ receipt
→ output
→ verifier
```

The objective is to identify the first failed transition, not to label the entire system broken.

### Entrypoint

Determine how the exact user-facing or machine-facing request enters the system. Verify argument parsing, protocol framing, configuration loading, and identity binding.

### Routing

Confirm the request reaches the intended capability and that fallback routes preserve semantics and authority.

### Admission

Inspect validation, authorization, policy, schema, ontology, compatibility, and trust-root checks. Distinguish refusal from error.

### Domain logic

Trace the exact behavior requested, including state transitions, invariants, and negative paths.

### Construction

Identify generated artifacts, plans, intents, temporary files, or runtime objects and their canonical sources.

### Actuation

Locate the exclusive side-effect boundary. Confirm BRCE mediates DO and that no alternate ambient actuation path exists.

### Consequence observation

Find how actual postconditions are observed. A successful return code is not always the requested consequence.

### Receipt

Verify that success, failure, timeout, refusal, and partial consequence all produce identity-bound receipts.

### Output

Confirm the user-visible or machine-visible output accurately reflects observed standing and does not promote inference.

### Verifier

Inspect whether the verifier covers the exact acceptance boundary independently enough to detect implementation drift.

## Repair the lawful path

Repair the existing lawful path before creating a parallel architecture. A parallel implementation can bypass an unknown fence, duplicate authority, split receipts, or invalidate replay.

Preserve:

- public and internal interfaces;
- authority boundaries;
- receipts and replay;
- portability;
- deterministic behavior;
- typed failures;
- required backward compatibility;
- canonical-source-to-projection correspondence.

## Implementation law

Make the smallest coherent bounded diff that closes the requested behavior.

Default to no more than twelve changed files unless dependency closure requires more. The bound is a diagnostic forcing function, not a license to leave an incoherent change. When closure requires more, state why.

Do not:

- perform unrelated refactors;
- fabricate execution evidence;
- weaken tests;
- mock the acceptance boundary merely to turn CI green;
- hand-edit generated outputs;
- introduce unnecessary dependencies;
- hide failures behind broad exception handling;
- collapse typed failures into generic errors;
- bypass BRCE;
- add unreceipted actuation;
- merge or close pull requests without explicit instruction;
- modify trust-root surfaces without admission and authority.

## Permanent repair encoding

When a permanent failure mode is discovered, encode the repair as one or more of:

- test;
- fixture;
- typed refusal;
- schema constraint;
- verifier;
- theorem;
- receipt invariant;
- admission guard;
- deterministic replay case.

The implementation is incomplete when the immediate symptom is fixed but the same transition can regress without detection.

## Failure-directed repair loop

Use this loop:

```text
preserve evidence
→ classify failure
→ locate first failed transition
→ form a materially new hypothesis
→ repair the narrowest cause
→ encode a permanent guard
→ rerun the failed boundary
→ expand verification after success
```

Never rerun an unchanged failure without a new hypothesis.

## Combinatorial maximalism

Preserve maximal reversible lawful possibilities before irreversible selection.

Bound the graph by:

- ontology;
- capability;
- authority;
- cost;
- evidence;
- acceptance.

A failed edge changes the topology. It does not prove the graph has no path. Conversely, maximalism does not permit speculative expansion beyond the task’s admitted scope.

## Generated and canonical surfaces

Before editing any file, classify it:

```text
canonical authored source
generated projection
received contract
runtime state
fixture
evidence artifact
receipt
report
cache
```

Edit only the lawful source surface. Regenerate projections. Preserve received-contract provenance. Do not commit ephemeral runtime state unless doctrine requires it.

## Trust-root changes

Changes to authority schemas, policy roots, signing identities, admission logic, or release gates are higher-risk transitions. They require:

- explicit task relevance;
- authority confirmation;
- narrower alternatives ruled out;
- negative fixtures;
- independent verification;
- explicit receipt and falsifier.

A test failure is not authority to weaken the trust root.
