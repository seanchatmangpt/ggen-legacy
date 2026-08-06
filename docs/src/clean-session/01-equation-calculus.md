# Equation, Foundation, and Calculus

## Governing equation

Use the Chatman Equation:

```text
A = μ(O*)
R = receipt(A)
```

Where:

- `O` is raw, partial, stale, ambiguous, unauthenticated, or otherwise untrusted observation.
- `O*` is admitted observation: identified, aligned, grounded, bounded, and authority-checked.
- `μ` is lawful manufacture under the admitted calculus.
- `A` is the resulting artifact, action, or system state.
- `R` is the receipt binding identity, authority, inputs, environment, execution, consequences, verification, and replay.

The equation establishes three hard restrictions:

1. Never manufacture from unadmitted `O`.
2. Never claim `A` without observed manufacture or execution.
3. Never claim standing without `R`.

An artifact may exist without standing. A command may run without proving the requested subject. A proof may establish a theorem without granting actuation authority. A workflow may exist without ever having executed. The receipt must bind the exact claimed transition.

## Admission of observation

Observation becomes `O*` only when all relevant predicates close:

| Predicate | Required question |
|---|---|
| identity | What exact repository, ref, SHA, tree, artifact, process, or subject was observed? |
| alignment | Does the observation address the requested boundary rather than an adjacent one? |
| grounding | What direct evidence supports it? |
| bounds | What time, environment, capability, authority, and scope limits apply? |
| authority | Who or what may admit, construct, actuate, verify, and publish? |
| freshness | Could the observation have changed since it was collected? |
| replayability | Can the observation and resulting transition be reproduced? |

Any unresolved predicate remains explicit. Unknown information is not silently converted into a default.

## Foundational order

Apply this ordering before implementation:

```text
Preserve
→ Fence / Chesterton analysis
→ Calculus
→ Exclusions
→ Falsifier
→ Extension
→ Operationalization
```

### Preserve

Identify behavior, interfaces, historical evidence, recovery paths, and authority boundaries that must survive the change. Preserve maximal reversible lawful possibilities before making irreversible selections.

### Fence / Chesterton analysis

Do not remove or bypass a mechanism until the invariant or historical reason it protects is understood. Where the reason is unknown, fence the mechanism and retain it until evidence permits a lawful change.

### Calculus

Define the system in terms of objects, morphisms, admission, closure, authority, actuation, receipts, replay, and standing. This prevents English-language similarity from being mistaken for semantic equivalence.

### Exclusions

State what is intentionally outside the task, what has no authority, what is unsupported, and what must not be inferred from the evidence.

### Falsifier

Name the observation that would invalidate each major assumption, verification result, or standing claim. A claim without a practical falsifier is not sufficiently bounded.

### Extension

Preserve lawful extension points and alternate routes. A single failed edge is topology, not graph failure.

### Operationalization

Translate the admitted calculus into executable commands, fixtures, schemas, tests, receipts, replay instructions, and publication steps.

## Required calculus

Every implementation task must identify the following. The admission rules and actuation boundaries must be explicit rather than inferred from adjacent mechanisms.

### Objects

Objects are the identity-bearing entities in the task graph. Typical objects include:

- repositories, refs, commits, trees, blobs, branches, and pull requests;
- source files, generated projections, schemas, ontologies, tickets, manifests, and lockfiles;
- toolchains, runtimes, containers, packages, caches, and portable capsules;
- commands, processes, protocol sessions, services, fixtures, and external implementations;
- intents, broker requests, consequences, receipts, replay records, and verifier reports.

### Morphisms

Morphisms are lawful transitions between objects, such as:

```text
raw request → parsed task capsule
ref → exact commit and tree
canonical graph → query result
query result → generated projection
projection → formal admission
admitted intent → broker actuation
actuation → observed consequence
consequence → verifier result
verifier result → receipt
receipt-bound intent → replay
exact head → draft pull request
```

Each morphism must declare its preconditions, authority, side effects, evidence, and failure states.

### Admission rules

Admission rules decide whether an observed object or proposed transition may enter manufacture. They include:

- exact identity resolution;
- authority checks;
- repository doctrine;
- schema or ontology closure;
- capability and toolchain compatibility;
- trust-root restrictions;
- cost and time bounds;
- safety and policy constraints;
- required witnesses and exclusions.

### Closure conditions

Closure conditions define when the requested boundary is complete. They must be behavioral where the request is behavioral. Examples include:

- exact CLI exits successfully and produces the expected artifact;
- service responds correctly over its real protocol boundary;
- generated projection is byte-identical on replay;
- all required protocol consumers complete real sessions;
- receipt verifies against the exact source, environment, and consequence;
- exact-head draft PR contains only the admitted diff.

### Authorities

Authority must be separated by function:

- who may select;
- who may construct;
- who may actuate;
- who may verify;
- who may assign standing;
- who may publish;
- who may merge, release, delete, archive, or decommission.

Possession of a connector or token is capability, not automatic task authority.

### Actuation boundaries

Actuation is any transition that changes machine, repository, service, external, or durable state. It requires an admitted intent and the exclusive DO path defined by BRCE.

### Receipts

A receipt must bind at least:

```text
subject identity
request and authority
admitted inputs
source and toolchain identities
environment and configuration
command or broker intent
exit or refusal state
observed consequence
verification result
hashes and artifacts
replay instruction
scope and standing
```

### Replay

Replay re-enters through the lawful actuation boundary using a receipt-bound intent. It is not an informal instruction to repeat a shell command outside BRCE.

### Standing

Standing is assigned only for the exact boundary supported by the receipt. A subsystem may be `ALIVE` while the wider product remains `PARTIAL_ALIVE` or `UNKNOWN`.

## Equivalence discipline

Do not reduce a Chatman construct to an analogy with a conventional system unless equivalence is demonstrated within the same boundaries.

A broker, workflow engine, policy layer, proof assistant, build system, semantic graph, or event log may be adjacent to a Chatman construct without being equivalent to it. Refutation requires the same subject, authorities, closure conditions, actuation boundary, receipt law, and replay semantics.

Adjacency is not refutation.
