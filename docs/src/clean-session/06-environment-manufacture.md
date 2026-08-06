# Environment Manufacture and Block Elimination

A missing tool starts a routing search. It does not immediately produce `BLOCKED`.

## Environment-manufacturing ladder

Try relevant routes in this order, adapting based on cost and evidence:

1. executable already on `PATH`;
2. executable outside `PATH`;
3. existing portable toolchain capsule;
4. local package cache;
5. local language registry cache;
6. shared library or language binding providing the underlying capability;
7. retained workflow artifact;
8. existing release artifact from the project ecosystem;
9. GitHub connector download of an exact release asset;
10. exact-SHA source archive;
11. OCI image manifest and direct layer extraction;
12. static binary distribution;
13. compatible system package extracted without installation;
14. source bootstrap using already available compilers;
15. cross-compilation;
16. QEMU or alternate-architecture execution;
17. GitHub Actions artifact manufacture;
18. isolated workflow jobs so one lane cannot hide another failure;
19. alternate runner images;
20. alternate runner architectures;
21. alternate authorized repositories or organizations with independent scheduler domains;
22. capability-equivalent local implementation;
23. minimal bounded reimplementation sufficient for the exact acceptance test.

The ladder is not an obligation to execute dominated or irrelevant routes. Each skipped route must be ruled out by evidence, authority, policy, cost, or a stronger proven route.

Do not use an unrelated person’s repository or infrastructure merely to acquire compute. Use only repositories and accounts for which explicit write authority exists and where the work is appropriately scoped.

## Portable toolchain capsule

When manufacturing a portable capsule:

- pin exact versions;
- preserve symlink topology;
- capture architecture and ABI;
- include required dynamic libraries;
- avoid importing incompatible host `glibc` unless necessary;
- compute SHA-256 or BLAKE3 digests;
- record source URLs or GitHub identities;
- create a relocation test;
- execute after relocation;
- retain a manifest and replay command.

A capsule manifest should include:

```text
capsule schema
producer and timestamp
source identities
component names and versions
platform and architecture
file inventory and digests
entrypoints
dynamic-library closure
environment variables
relocation procedure
verification commands
replay command
known exclusions
```

## Capability-equivalent substrates

Capability parity and exact-brand parity are separate closure conditions.

Examples:

- a language binding may expose the required Z3 solver capability while the `z3` CLI remains absent;
- an embedded WASM runtime may execute the acceptance fixture while Wasmtime parity remains unknown;
- an SSH2 library may satisfy protocol transport while the OpenSSH executable remains absent;
- a bounded recursive Datalog implementation may satisfy the rule set while Soufflé parity remains unknown.

Report both states independently.

## Blocked elimination protocol

Before assigning `BLOCKED`, produce an edge-exhaustion record:

| Route | Attempted | Observed result | Failure class | New hypothesis available |
|---|---:|---|---|---:|
| existing executable | yes/no | path, version, or absence | capability | yes/no |
| local cache | yes/no | exact cache evidence | artifact | yes/no |
| connector transport | yes/no | exact response | transport/auth | yes/no |
| release artifact | yes/no | exact identity or failure | transport | yes/no |
| OCI extraction | yes/no | manifest/layer result | runtime/ABI | yes/no |
| source bootstrap | yes/no | compiler/build result | build | yes/no |
| remote artifact manufacture | yes/no | exact-head run state | scheduler/build | yes/no |
| equivalent substrate | yes/no | capability proof | compatibility | yes/no |
| bounded reimplementation | yes/no | verifier result | scope | yes/no |

A route is exhausted only when at least one of these predicates holds:

- it was actually attempted and failed;
- it is unavailable under the current authority boundary;
- its prerequisites are demonstrably absent;
- it would violate policy or safety;
- it is dominated by a stronger proven route;
- its cost exceeds explicit task bounds.

## Non-terminal observations

The following are not automatically terminal:

- queue delay;
- one failed package mirror;
- one failed package-manager installation;
- one failed native binary;
- absence of a container daemon;
- absence of an SSH executable;
- absence of a Soufflé executable;
- absence of a Wasmtime executable;
- container DNS failure;
- connector inability to mount a tree.

Each observation narrows topology. It does not collapse the graph.

## Failure-state assignment

Use the earliest accurate state:

```text
source inaccessible after edge exhaustion → BLOCKED
admitted source reaches compiler and fails → BUILD_BROKEN
capability absent with no lawful equivalent → UNSUPPORTED
policy or authority denies route → REFUSED:<reason>
insufficient observation → UNKNOWN
some exact routes close, requested crown open → PARTIAL_ALIVE
```

## Bounded effort

“Try every lawful relevant route” does not mean loop indefinitely. Stop exploring a route when there is no new hypothesis, when it is dominated, or when explicit cost bounds are reached. Preserve the exhaustion table so another session can continue from evidence rather than repetition.
