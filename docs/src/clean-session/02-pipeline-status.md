# Pipeline, Authority, and Standing

## Canonical system pipeline

Model every system as:

```text
parse
→ route
→ admit or refuse
→ diagnose or repair
→ construct
→ actuate
→ observe consequence
→ verify
→ receipt
→ replay or hook
→ standing
```

The sequence is not decorative. Each transition is a checkpoint with distinct authority and evidence.

### Parse

Convert raw input into a typed candidate request without granting it authority.

### Route

Choose lawful capability surfaces and transports while preserving alternate routes.

### Admit or refuse

Resolve identity, bounds, authority, doctrine, and safety. Refusal must be typed and receipted.

### Diagnose or repair

Locate the first failed transition. Repair the earliest lawful cause rather than constructing a parallel path around an unexplained invariant.

### Construct

Manufacture reversible artifacts, plans, projections, code, fixtures, or intents. Construction does not itself change the external target state.

### Actuate

Perform the admitted state-changing transition exclusively through BRCE.

### Observe consequence

Inspect the actual postcondition rather than assuming the command produced it.

### Verify

Compare the observed consequence with the exact acceptance boundary.

### Receipt

Bind identity, authority, execution, consequence, verification, and replay.

### Replay or hook

Replay uses receipt-bound intent through BRCE. Hooks may manufacture new intents but may not actuate.

### Standing

Assign a bounded state only after receipt verification.

## SELECT, CONSTRUCT, and DO

Maintain strict separation among:

```text
SELECT
CONSTRUCT
DO
```

### SELECT

Selection chooses an admitted path from reversible alternatives. Selection may narrow the graph but has no ambient side-effect authority.

### CONSTRUCT

Construction manufactures candidate artifacts and intents. Raw input, model output, planner output, generated code, semantic derivation, formal proof, workflow configuration, and hooks remain construction products until separately admitted.

### DO

DO changes machine or external state. BRCE is the exclusive DO path:

```text
zero unreceipted actuation
```

No proof, model, workflow, generated artifact, semantic rule, or hook may self-authorize DO.

## BRCE law

Every broker attempt emits a receipt, including:

- success;
- typed refusal;
- tool failure;
- timeout;
- unsupported capability;
- blocked external dependency;
- partial consequence;
- replay mismatch.

A failed actuation attempt still has consequences and therefore requires a receipt. Absence of a success artifact is not absence of an event.

Replay must re-enter BRCE using the original or lawfully transformed receipt-bound intent. Direct command repetition outside the broker boundary is a new unreceipted actuation and is not replay.

## Status ontology

Use only these primary standing labels:

```text
UNKNOWN
PARTIAL_ALIVE
ALIVE
BLOCKED
BUILD_BROKEN
UNSUPPORTED
REFUSED:<typed_reason>
```

### `UNKNOWN`

The boundary has not been sufficiently observed. `UNKNOWN` is not admitted truth, not failure, and not permission to infer a default.

### `PARTIAL_ALIVE`

Some exact boundaries executed successfully, but requested closure is incomplete. Every closed and open boundary must be named separately.

### `ALIVE`

The exact admitted subject executed successfully and was re-observed against the acceptance boundary. `ALIVE` requires an execution receipt for the exact subject.

### `BLOCKED`

Every relevant lawful route was attempted or ruled out with evidence, and an external dependency prevents continuation. A single failed edge is insufficient.

### `BUILD_BROKEN`

The admitted source and toolchain reached construction, but construction failed. Missing tools or inaccessible source are not `BUILD_BROKEN` unless construction actually began against the admitted subject.

### `UNSUPPORTED`

The capability is absent from the available substrate and no lawful compatible implementation is available. `UNSUPPORTED` does not mean refused.

### `REFUSED:<typed_reason>`

Execution was intentionally denied by policy, authority, admission, trust-root, or safety law. The reason must be stable enough for deterministic handling and replay.

## Checkpoint discipline

Never promote any of the following directly to `ALIVE`:

- a workflow file;
- a pull request;
- a build script;
- an uploaded artifact;
- a connector object;
- a downloaded archive;
- a compilation checkpoint;
- a green status record without exact-head logs;
- a named “receipt” that does not bind execution;
- a proof that does not cover the runtime consequence;
- a test double substituted for a requested real boundary.

A checkpoint is not a crown.

## Evidence dimensions

Track these dimensions separately:

| Dimension | Question |
|---|---|
| observed | What was directly seen? |
| admitted | What was accepted into the task calculus, and why? |
| executed | What exact subject actually ran? |
| changed | What durable or external state changed? |
| verified | What acceptance condition was re-observed? |
| inferred | What follows by reasoning but was not directly observed? |
| refused | What was intentionally denied, under which rule? |
| blocked | Which external dependency remains after edge exhaustion? |
| unsupported | Which capability is absent with no lawful equivalent? |

A final receipt must not collapse these columns into a single narrative.

## Capability versus brand parity

A capability-equivalent substrate can close a capability requirement without proving exact-brand parity.

Example:

```text
Z3 capability: ALIVE through libz3
Exact z3 CLI: UNKNOWN
```

The same distinction applies to WASM runtimes, SSH implementations, Datalog engines, package managers, container engines, and protocol clients.
