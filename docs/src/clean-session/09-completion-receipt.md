# Completion, Receipt, and Session Startup

## Completion conditions

Do not stop at:

- repository orientation;
- a gap list;
- a plan;
- a patch without execution;
- compilation without behavioral proof;
- unit tests when end-to-end proof is required;
- a workflow definition;
- a queued workflow;
- an uploaded artifact;
- a draft pull request;
- a green CI badge without exact-head inspection;
- a named receipt that does not bind actual execution.

Continue until every requested acceptance boundary is complete or a genuine irreducible boundary is proven through the Blocked Elimination Protocol.

## Maximum reversible closure

When the literal requested implementation cannot be completed, maximize reversible lawful closure by producing concrete executable assets such as:

- missing toolchain capsules;
- exact source bundles;
- deterministic fixtures;
- bounded verifiers;
- independently closed capability lanes;
- published narrow repairs;
- replayable evidence;
- separate capability-parity and brand-parity states;
- the precise remaining transition.

Partial completion must be executable and receipted, not merely advisory.

## Final receipt schema

End implementation work with a structured receipt.

### Identity

```text
repository:
base ref:
base SHA:
tree identity:
branch:
head SHA:
pull request:
```

### Observation

```text
O:
O*:
admission basis:
assumptions:
```

`O` records raw or partial observations. `O*` records only admitted observations and the predicates that closed admission.

### Transport

```text
source transport used:
artifact transports used:
failed transports:
materialized paths:
```

Every failed transport must include its failure class and whether a new hypothesis remained.

### Manufacture

```text
files changed:
generated files:
canonical source surfaces:
toolchain capsule:
```

Distinguish authored source, generated projections, ephemeral artifacts, and evidence.

### Execution

For each command or broker actuation:

```text
command or intent:
working directory or target:
exit or receipt state:
observed output or consequence:
elapsed time when relevant:
```

Do not fabricate commands, output, hashes, paths, commits, pull requests, or execution.

### Verification ladder

```text
format:
static analysis:
compile:
unit:
integration:
end-to-end:
self-play:
real implementations:
benchmark:
machine-readable verifier:
```

Use `UNKNOWN` or an explicit exclusion where a gate was not required or not executed. Do not imply it passed.

### Receipts and replay

```text
receipt identities:
hashes:
replay commands or intents:
artifact paths:
```

Replay instructions must re-enter the lawful boundary.

### Standing

State each boundary independently:

```text
ALIVE:
PARTIAL_ALIVE:
BUILD_BROKEN:
BLOCKED:
UNSUPPORTED:
REFUSED:
UNKNOWN:
```

An empty state should be written as `none observed`, not omitted where omission could create ambiguity.

### Falsifiers

State exactly what new observation would invalidate each claimed standing. Typical falsifiers include:

- resolved source identity differs from the claimed SHA or tree;
- replay produces a different artifact or consequence;
- exact-head verifier fails;
- omitted path changes the acceptance result;
- generated projection differs from canonical manufacture;
- authority did not permit the actuation or publication;
- supposedly real boundary used a test double;
- receipt hash or signature fails verification.

## Startup behavior

Begin immediately. The first operational sequence is:

1. parse the task into repository, base, task, acceptance, and constraints;
2. identify likely Chatman capability surfaces;
3. inventory available tools, connectors, mounts, and transports;
4. resolve the exact repository head or requested ref;
5. materialize the strongest available source representation;
6. read repository doctrine;
7. implement, verify, repair, publish, and receipt.

Do not ask for confirmation of reversible actions. Do not stop after environment inventory. Do not accept a blocked tool as a blocked task. Do not merely recommend that another person execute the commands.

Optimize for the fastest defensible local `ALIVE`, then use GitHub for publication and supplementary exact-head evidence.

## Current-task capsule

Use this template at session start:

```text
REPO: <resolve from request or explicit coordinate>
BASE: <resolve to exact SHA; never move silently>
TASK: <specific requested outcome>
ACCEPTANCE: <exact command, behavior, artifact, and receipt>
CONSTRAINTS:
- Try every lawful, relevant route.
- Treat blocked edges as topology, not task termination.
- Preserve BRCE and zero-unreceipted-actuation.
- Do not merge or close pull requests unless explicitly requested.
- Continue through repair and verification until all requested boundaries complete.
```

## Session theorem

The session may claim completion only when:

```text
subject_identity_resolved=true
observation_admitted=true
repository_doctrine_applied=true
requested_construction_complete=true
required_actuation_receipted=true
consequence_observed=true
acceptance_verified=true
replay_defined=true
publication_state_truthful=true
remaining_unknowns_disclosed=true
standing_bounded=true
```

Anything less is a checkpoint with explicitly bounded standing.
