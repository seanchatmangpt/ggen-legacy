# AGENTS.md — ggen-legacy executable reconstruction

## 0. Authority and exact subject

This file governs every human or automated change in `seanchatmangpt/ggen-legacy`.

- admitted reconstruction base: `70e599a599fedb7c62c965377cc2f80df1fa01ec`
- active executable ticket: `GL-LSP-001`
- required LSP runtime: `lsp-max`
- pinned runtime revision: `seanchatmangpt/lsp-max@220d3251e959f6a58ce0311e995b31a85f98240c`
- publication boundary: draft pull request unless the user explicitly authorizes merge

The repository began as a documentation-only bootstrap. That fence remains the default. Executable source is admitted only by a deterministic ticket naming its contract, authority, dependency closure, witnesses, falsifiers, commands, receipt, replay rule, and exclusions.

## 1. Mission

Reconstruct observable legacy behavior, encode it as admitted authority, implement the smallest lawful executable boundary, execute that exact boundary locally, and preserve evidence sufficient for replay and later release or sunset decisions.

```text
observe → align → admit/refuse → construct → execute
→ verify → receipt → replay → bounded standing
```

For `GL-LSP-001`:

```text
LSP bytes → lsp-max framing and dispatch
→ admitted document state → ggen analysis
→ lsp-max client response/notification → receipt
```

A custom JSON-RPC transport or Python substitute is outside the admitted final architecture.

## 2. Foundational order

Every material change follows:

1. Preserve the prior purpose and recovery path.
2. Fence unsafe or unadmitted transitions.
3. Define objects, morphisms, admission, closure, authority, actuation, receipt, and replay.
4. State exclusions.
5. Name a falsifier against the same subject and boundary.
6. Preserve reversible lawful extension points.
7. Bind implementation to commands and evidence.

Historical corpus material remains evidence even when a new executable projection is admitted. Adjacency is not refutation.

## 3. Absolute invariants

### 3.1 Zero unreceipted actuation

No release, deployment, migration, deletion, retirement, external network operation, or durable mutation outside the working tree occurs without explicit authority and a receipt.

The language server may analyze in-memory document text and emit protocol responses. It has no ambient shell, package-manager, Git, deployment, network, or filesystem-write authority.

### 3.2 Observation is not admission

```text
O  = partial or stale observation
O* = admitted, aligned, grounded, bounded observation
A  = μ(O*)
R  = receipt(A)
```

Track observed, admitted, executed, changed, verified, inferred, refused, blocked, and unsupported separately.

### 3.3 lsp-max is the protocol boundary

The executable server must use:

- `lsp_max::LspService`
- `lsp_max::Server`
- `lsp_max::Client`
- `lsp_max::LanguageServer`
- `lsp_max::lsp_types_max`

Do not hand-roll Content-Length framing, JSON-RPC dispatch, client notification plumbing, or substitute another LSP runtime without a new admission decision.

### 3.4 Protocol purity

Standard output is exclusively the LSP protocol channel. Tracing and refusal details go to standard error. `clippy::print_stdout` is denied.

### 3.5 Exact dependency identity

`lsp-max` must be pinned to an exact Git revision or exact released version admitted by the ticket. Floating branches and unbounded semver ranges are refused for the runtime authority edge.

### 3.6 No self-certification

Source, generated documentation, an authored status file, or an unexecuted test cannot grant `ALIVE`. The exact candidate must compile and execute locally against the pinned runtime.

### 3.7 Checkpoint is not crown

A parser test, capability assertion, compile check, or smoke exchange proves only its named boundary. Repository, release, production, certification, and sunset standing remain separate.

## 4. Typed states

Use exactly:

- `UNKNOWN` — insufficient observation or admission.
- `PARTIAL_ALIVE` — a bounded subset executed; required checks remain open.
- `ALIVE` — every conjunct in the declared bounded scope executed and replayed.
- `BLOCKED` — required authority, dependency, permission, transport, artifact, or toolchain unavailable.
- `BUILD_BROKEN` — an admitted build command executed with an available toolchain and failed.
- `UNSUPPORTED` — outside the declared product boundary.
- `REFUSED:<CODE>` — policy or admission law rejected the operation.

No toolchain means `BLOCKED:TOOLCHAIN_UNAVAILABLE`, not `BUILD_BROKEN`. Source inspection is not execution.

## 5. Authority precedence

1. `AGENTS.md`
2. `RELEASE_CONTROL.md`
3. admitted tickets under `tickets/`
4. admitted machine-readable authority
5. schemas, gates, and verifier contracts
6. executable source and fixtures at the exact candidate
7. PRD and ARD
8. explanatory documentation
9. generated reports
10. assumptions

A contradiction returns `BLOCKED:AUTHORITY_CONTRADICTION`.

## 6. GL-LSP-001 boundary

Admitted authored paths:

```text
Cargo.toml
rust-toolchain.toml
src/**
tests/**
tickets/GL-LSP-001.md
docs/lsp/**
```

Required behavior:

1. Start `lsp_max::Server` over stdin/stdout.
2. Advertise only implemented capabilities.
3. Track open documents with full synchronization.
4. Publish deterministic Turtle, TOML/ggen-manifest, and Tera diagnostics.
5. Clear diagnostics on close.
6. Execute completion, hover, document symbols, formatting, and quick-fix code actions through the `LanguageServer` implementation.
7. Refuse incremental changes while full sync is advertised.
8. Keep stdout free of tracing or prose.
9. Compile, lint, test, and replay locally against the exact `lsp-max` revision.

## 7. Verification ladder

Run the cheapest high-information gates first:

```text
cargo fmt --all -- --check
→ cargo check --all-targets
→ cargo clippy --all-targets -- -D warnings
→ cargo test --all-targets
→ real stdio initialize/open/change/close exchange
→ malformed-message and refusal fixtures
→ deterministic replay
```

Do not use GitHub Actions as a substitute for local execution. Hosted CI may supplement a local receipt only when the user permits it.

## 8. Repair law

On failure:

1. preserve the exact command, exit status, and stderr;
2. classify the failed transition;
3. repair the narrowest lawful cause;
4. add a permanent guard or fixture;
5. rerun the failed boundary;
6. expand only after success.

Never rerun an unchanged failure without a new hypothesis.

## 9. Git and publication safety

Resolve the exact base and current branch head before writing. Preserve unrelated work. Use non-force branch updates. Do not merge unless explicitly requested. `gh` and GitHub CI are excluded for this task.

## 10. Required receipt

Report:

- repository, original base, branch, candidate SHA, and pinned `lsp-max` SHA;
- O and O*;
- transport and toolchain attempts with typed failures;
- files changed and removed;
- commands and exit statuses;
- observed execution boundaries;
- replay result;
- scoped standing and exclusions;
- draft PR identity.

> Preserve the contract. Use lsp-max. Execute locally. Replay the receipt.
