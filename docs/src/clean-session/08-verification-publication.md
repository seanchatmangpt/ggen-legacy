# Verification, Capsules, and Publication

## Acceptance selection

Choose the acceptance boundary in this order:

1. exact user-specified command or behavior;
2. documented repository command;
3. repository-native task-runner command;
4. narrowest existing verifier covering the boundary;
5. a new bounded verifier when no adequate verifier exists.

Never substitute a unit test for a requested:

- CLI execution;
- service behavior;
- integration;
- protocol session;
- browser interaction;
- end-to-end flow;
- release artifact;
- replay proof.

## Verification ladder

Run verification from the cheapest, highest-information gates toward broader gates:

```text
format
→ static analysis
→ compile
→ narrow unit
→ package tests
→ integration
→ protocol consumer
→ end-to-end
→ self-play
→ multiple real implementations
→ chaos
→ stress
→ benchmark
→ machine-readable verifier report
```

Parallelize independent gates. Stop expansion when a lower boundary fails, repair it, then continue.

## Boundary-specific evidence

| Gate | Evidence required |
|---|---|
| format | exact formatter, files, version, and clean result |
| static analysis | exact analyzer, configuration, diagnostics, and exit |
| compile | source coordinate, toolchain, target, features, and artifact identity |
| unit | named test set and result |
| integration | real components and transport boundaries |
| protocol consumer | actual sessions with admitted consumers |
| end-to-end | user-visible entrypoint through observed consequence |
| self-play | generated scenario corpus, seed, coverage, and falsifiers |
| real implementations | identities and versions of independent counterparts |
| chaos/stress | fault model, duration, limits, and recovery evidence |
| benchmark | hardware, build profile, dataset, methodology, and variance |
| verifier report | exact subject, checks, errors, standing, hashes, and replay |

## Local capsule preference

Prefer a locally replayable validation capsule:

```text
Source Capsule
× Validation Pack
× Execution Mode
× Toolchain Capsule
→ Receipt DAG
```

### Source Capsule

Binds exact repository, commit, tree, submodules, generated status, patches, and dependency closure.

### Validation Pack

Contains commands, fixtures, schemas, expected consequences, negative cases, and standing rules.

### Execution Mode

Defines native, containerized, WASM, emulated, remote, or capability-equivalent execution and its limitations.

### Toolchain Capsule

Binds compilers, runtimes, libraries, system dependencies, architecture, ABI, and environment.

### Receipt DAG

Preserves dependency and consequence relationships among all executed gates. A later receipt references rather than obscures earlier failures and repairs.

## Receipt reuse

A prior verifier receipt may be reused only when these identities match:

- source;
- validator;
- toolchain;
- configuration;
- environment;
- acceptance boundary.

Even when they match, prove the exact current subject separately. Reuse can reduce repeated verification; it cannot silently transfer standing to a different subject.

## GitHub as source and publication graph

GitHub is the source and publication graph, not the sole truth source.

For requested code or documentation changes:

1. resolve exact base SHA;
2. create a purpose branch;
3. make intentional bounded changes;
4. run local verification;
5. commit intentionally;
6. push without force;
7. open a draft pull request;
8. inspect CI for the exact head SHA;
9. inspect failing logs, not only status metadata;
10. repair and update the same branch where appropriate;
11. produce a publication receipt.

Never merge unless explicitly requested. Never close pull requests because they are stale, failing, superseded, or inconvenient. Never silently change base.

Do not claim Actions success when jobs are queued, skipped, pending, cancelled, absent, or associated with a different head.

## Connector publication path

When local Git transport is unavailable but connector writes are authorized, publication may use Git object manufacture:

```text
blob
→ tree based on exact base tree
→ commit with exact parent
→ branch ref
→ draft pull request
```

Preserve expected identities at every transition. Connector publication does not substitute for local execution; it substitutes only for the unavailable transport.

## CI relationship

GitHub CI supplements local proof. It is not the source of truth.

A green check without exact-head logs and artifact identity is insufficient. A queued runner is neither completion nor proof of workflow failure. A hosted result cannot prove a local environment property unless that equivalence is part of the admitted acceptance boundary.

## Progress communication

For multi-step work, provide brief progress updates approximately every two or three tool calls or whenever a meaningful boundary changes.

Useful updates state:

- what has been admitted;
- what is now `ALIVE`;
- the first real failure discovered;
- the route currently under test;
- what changed in the system graph.

Do not narrate every command. Do not tell the user to wait. Do not provide a future completion estimate. Do not stop merely because the task is difficult or tool-heavy.
