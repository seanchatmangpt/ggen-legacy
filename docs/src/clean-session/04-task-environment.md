# Task Admission and Environment Orientation

## Initial task parsing

Convert every request into an explicit task capsule:

```text
repo=<owner/repository or capability graph>
base=<requested ref and resolved exact SHA>
task=<requested outcome>
acceptance=<exact command, behavior, artifact, or evidence>
constraints=<authority, time, portability, compatibility, scope>
```

Infer reversible details from repository doctrine, prior admitted context, and the request. Ask a question only when a choice is both necessary and irreversible and cannot be inferred lawfully.

Do not ask the user to repeat information already supplied. Do not stop at a plan when implementation is requested. Do not promise background work. Manufacture the strongest lawful result in the current session.

## Task admission record

Before changing source, record:

| Field | Required content |
|---|---|
| requested subject | user language preserved without premature normalization |
| resolved repository | canonical implementation location or capability graph |
| requested base | branch, tag, commit, archive, or other source coordinate |
| resolved base | exact commit SHA and tree identity |
| acceptance | strongest repository-native behavioral proof |
| authorities | read, write, actuation, publication, merge, release |
| constraints | scope, portability, compatibility, time, cost, safety |
| assumptions | explicit, falsifiable, and reversible where possible |
| exclusions | non-goals and forbidden surfaces |

Never silently move the base after admission. If upstream changes, the original base remains the subject unless a new admission is recorded.

## Environment orientation

Before editing, inventory the actual clean-session environment. Rediscover every capability; do not assume prior paths, caches, checkouts, or toolchains survived.

### Workspace and source transport

Inspect and record:

- mounted directories;
- conversation attachments;
- library files;
- existing checkouts;
- Git repositories and remotes;
- archive files and Git bundles;
- workflow artifacts and source snapshots;
- connector-only repository objects;
- writable paths;
- disk space.

A GitHub connector object is not a mounted source tree. A filename is not proof of a filesystem path. A prior session’s `/mnt/data` coordinate is not current evidence.

### Source-control capabilities

Inventory:

- `git`;
- `gh`;
- GitHub connector functions;
- authenticated installations;
- readable repositories;
- writable repositories;
- branch permissions;
- pull-request permissions;
- Actions permissions;
- artifact download capabilities.

Separate identity, capability, and authority. A token may be authenticated but lack write authority. A connector may expose repository objects without providing a local checkout.

### Network and transport

Test relevant edges separately:

- DNS resolution;
- raw TCP egress;
- TLS with SNI;
- HTTP redirects;
- authenticated GitHub API transport;
- release-asset transport;
- package mirrors;
- OCI registry transport;
- internal artifact gateways.

Do not conflate DNS failure with total network failure. Do not conflate container network failure with connector or host-side transport failure. Record the layer at which failure occurred.

### Build and execution tools

Inventory at least the tools relevant to the task, including:

- Rust, Cargo, Rustup, Rustfmt, Clippy;
- Lean, Lake, Elan;
- Erlang, Elixir, Mix, Dialyzer;
- Wasmtime, Wasmer, `wasm-tools`, `wasm-ld`;
- Z3, CVC5, Soufflé, and solver libraries;
- Git, GitHub CLI, SSH executables, and SSH2 libraries;
- Docker, Podman, Buildah, Skopeo, chroot, and namespaces;
- Python, Node, Go, Java, Clang, and GCC;
- package managers and local caches;
- language registries;
- system shared libraries and static binaries;
- QEMU and alternate-architecture support.

For every executable used in evidence, capture:

```text
path
version
architecture
exit status
dynamic-library closure
relevant environment variables
```

Use `ldd`, file-format inspection, package metadata, or equivalent evidence where ABI compatibility matters.

## Orientation output

The orientation phase should produce a bounded environment ledger, not a generic inventory dump. Each entry should state:

```text
capability
observed implementation
identity/version
available transport
required authority
standing
relevance to acceptance
```

The ledger becomes part of `O*` and later receipts.

## Clean-session invariant

A clean session starts from `UNKNOWN`. Prior receipts may be considered evidence only when source, validator, toolchain, configuration, environment, and acceptance identities match. Even then, the current exact subject must be independently established.
