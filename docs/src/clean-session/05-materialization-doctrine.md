# Source Materialization and Repository Doctrine

## Exact source identity

Resolve the requested base to an exact SHA before changing anything.

Record:

```text
repository
requested ref
resolved base SHA
base tree identity
working branch
head SHA
pull request
```

The base coordinate is immutable for the admitted task. A newer default-branch head is a different subject and requires a new admission decision.

## Source materialization ladder

Attempt source materialization through the strongest available path:

1. verified existing checkout;
2. exact-SHA local archive;
3. authenticated clone or fetch;
4. Git bundle;
5. GitHub archive at the exact SHA;
6. retained workflow artifact;
7. connector file-tree reconstruction;
8. Git tree and blob reconstruction;
9. dependency-closed sparse tree;
10. classified remote execution against the exact SHA.

An exact tree without `.git` may be sufficient for local build and verification. Publication identity remains separate and must still bind repository, base, tree, branch, and commit.

## Transport classification

For every failed materialization edge, record:

| Field | Meaning |
|---|---|
| route | exact transport attempted |
| subject | repository/ref/SHA/tree requested |
| observation | command, response, or connector result |
| failure class | DNS, TLS, authorization, absence, corruption, timeout, unsupported operation, or other typed class |
| consequence | what remains unavailable |
| next hypothesis | materially different route to test |

Do not retry an unchanged failure without a new hypothesis. Do not generalize a failure beyond its observed layer.

Examples:

```text
HTTPS clone failed at DNS
≠ GitHub API connector unavailable

container daemon absent
≠ OCI manifest and layer extraction unavailable

archive transport failed
≠ Git tree/blob reconstruction unavailable
```

## Tree reconstruction

When reconstructing through Git objects or connector files:

1. obtain the exact commit and tree identity;
2. enumerate the tree without truncation;
3. materialize only the dependency-closed paths needed for the acceptance boundary, unless a full tree is required;
4. preserve file modes and symlink topology;
5. verify blob identities or content digests;
6. record absent `.git` metadata as an execution constraint;
7. keep publication operations bound to the original Git object graph.

A sparse tree must be described as sparse. It cannot establish whole-repository claims unless closure of the omitted paths is independently proven irrelevant.

## Repository doctrine admission

Before editing, read the authority surfaces that exist, including:

- root `AGENTS.md`;
- nested `AGENTS.md` files;
- `SYSTEM.md`;
- architecture documents;
- manifests and lockfiles;
- task runners and Makefiles;
- CI workflows and test configuration;
- generation policy;
- release policy;
- contribution policy;
- verification and definition-of-done documents;
- trust-root restrictions.

Nested doctrine governs its subtree. Repository-local doctrine outranks general expectations.

## Doctrine extraction

Identify and record:

```text
canonical source surfaces
generated projections
forbidden editing surfaces
required toolchain versions
required acceptance commands
release boundaries
authority boundaries
time budgets
standing ceilings
```

Known versions from elsewhere in the ecosystem are not ambient defaults. A Rust nightly or Lean version is admitted only when the exact repository declares or depends on it.

Where applicable, preserve a repository-declared ggen generation-and-test wall-clock objective, such as five seconds. Do not export that budget to unrelated repositories without doctrine.

## Generated projection law

Generated files are not canonical editing surfaces unless repository doctrine explicitly declares otherwise.

The lawful repair path is:

```text
canonical graph or source
→ admitted query/template/configuration change
→ deterministic generation
→ projection identity check
→ behavioral verification
→ receipt
```

Hand-editing a projection may create apparent local correctness while breaking replay and authority correspondence.

## Fence contradictions

If authority surfaces contradict each other:

1. preserve both observations;
2. apply declared precedence;
3. refuse an irreversible transition when precedence cannot resolve the contradiction;
4. emit `REFUSED:AUTHORITY_CONTRADICTION` or repository-specific typed equivalent;
5. name the minimal authority decision required to continue.

Do not silently choose the document that enables the preferred implementation.
