# AGENTS.md — ggen-legacy active reconstruction runtime

## 0. Authority and exact subject

This file is the normative operating contract for every human or automated agent working in `ggen-legacy`.

- **Repository:** `seanchatmangpt/ggen-legacy`
- **Admitted base for this transition:** `70e599a599fedb7c62c965377cc2f80df1fa01ec`
- **Category:** Verified Repository Reconstitution
- **Current executable program:** bounded ggen language-server reference runtime
- **Kernel relationship:** `ggen` remains the manufacturing kernel; `ggen-legacy` owns legacy observation, executable reference behavior, equivalence fixtures, and retirement evidence.

The previous constitution described a documentation-only bootstrap and categorically refused implementation directories. That fence was correct before source admission. It is no longer a permanent product boundary. A deterministic source-admission ticket may now admit executable code without weakening receipt, replay, authority, or non-self-certification law.

## 1. Mission

Reconstruct observable legacy behavior, admit it as bounded authority, manufacture an executable replacement or reference implementation, prove the declared contract against real boundaries, and preserve enough evidence to decide release and eventual predecessor retirement.

```text
observe → align → admit/refuse → construct → execute
→ verify → receipt → replay → bounded standing
```

The current priority is the language-server path, launched from source with `python3 bin/ggen-lsp`:

```text
LSP bytes → framed JSON-RPC → admitted method
→ document state → analysis → diagnostics/features
→ framed response/notification → protocol receipt
```

## 2. Foundational order

Every material change follows this order:

1. **Preserve** — identify the purpose, consumers, provenance, and recovery path.
2. **Fence** — retain the safety boundary that prevented an invalid transition.
3. **Calculus** — name objects, morphisms, admission rules, closure, authority, actuation, receipt, and replay.
4. **Exclusions** — state what the claim does not cover.
5. **Falsifier** — identify an observation against the same subject and boundary that would disprove completion.
6. **Extension** — preserve reversible lawful paths for future capability.
7. **Operationalization** — bind commands, fixtures, verifier output, receipts, and replay.

Adjacency is not refutation. A new implementation does not invalidate the historical corpus; it adds an admitted executable projection.

## 3. Absolute invariants

### 3.1 Zero unreceipted actuation

No publication, release, deployment, migration, deletion, retirement, external network operation, or durable mutation outside the working tree may occur without explicit authority and a receipt.

The LSP runtime has no ambient shell, network, package-manager, Git, or deployment authority. Protocol handlers may analyze in-memory document text and return protocol messages. Filesystem mutation is refused unless a later ticket separately admits it.

### 3.2 Observation is not admission

```text
O  = partial or stale observation
O* = admitted, aligned, grounded, bounded observation
A  = μ(O*)
R  = receipt(A)
```

Track observed, admitted, executed, changed, verified, inferred, refused, blocked, and unsupported separately.

### 3.3 No self-certification

Source, generated documentation, a passing unit test, or an implementation-authored status field cannot crown itself. Bounded standing requires an independent verifier process that executes the exact declared subject and negative controls.

### 3.4 Protocol purity

Standard output is exclusively the LSP Content-Length framed JSON-RPC channel. Logs and refusal details go to standard error. Any unframed standard-output byte is a protocol defect.

### 3.5 Exact identity

Every executable claim binds:

- repository and exact base;
- source-manifest digest;
- toolchain identity;
- verifier identity;
- command and exit status;
- crossed process/protocol boundaries;
- exclusions and standing ceiling.

### 3.6 No hidden unknowns

An unexecuted feature is `UNKNOWN`, not passing. An unavailable toolchain is `BLOCKED`, not evidence that the implementation fails. Unsupported scope is `UNSUPPORTED`, not policy refusal.

### 3.7 Checkpoint is not crown

A parser test, handler test, or smoke exchange proves only its named boundary. Repository-wide `ALIVE`, release admission, production standing, and sunset admission remain separate claims.

## 4. Typed states

Use exactly:

- `UNKNOWN` — insufficient observation or admission.
- `PARTIAL_ALIVE` — observed success for a bounded subset; required declared checks remain open.
- `ALIVE` — every conjunct in the explicitly declared bounded scope executed and replayed.
- `BLOCKED` — a required authority, dependency, permission, artifact, transport, or toolchain is unavailable.
- `BUILD_BROKEN` — an admitted build or manufacture command executed and failed.
- `UNSUPPORTED` — outside the declared product boundary.
- `REFUSED:<CODE>` — policy or admission law rejected the operation.

Never collapse `UNKNOWN → ALIVE`, `UNSUPPORTED → REFUSED`, `BLOCKED → BUILD_BROKEN`, or checkpoint success → repository crown.

## 5. Authority precedence

1. `AGENTS.md`
2. `RELEASE_CONTROL.md`
3. admitted tickets under `tickets/`
4. admitted machine-readable authority under `authority/`
5. schemas, gates, and verifier contracts
6. executable source and fixtures at the exact subject
7. PRD and ARD
8. explanatory documentation
9. generated reports
10. agent assumptions

A contradiction returns `BLOCKED:AUTHORITY_CONTRADICTION`. Do not silently choose the convenient instruction.

## 6. Source-admission law

Executable source is permitted only when a ticket names:

- identity and exact base;
- authority and owner;
- observable contract;
- implementation boundary;
- toolchain and dependency closure;
- positive witnesses;
- negative falsifiers;
- verification commands;
- evidence and receipt paths;
- replay rule;
- exclusions;
- expected state transition.

`GL-LSP-001` admits the bounded language-server runtime under:

```text
bin/ggen-lsp
src/ggen_lsp/**
tests/test_lsp_*.py
scripts/verify_lsp.py
docs/lsp/**
evidence/lsp-reference/**
```

This admission does not authorize unrelated application, service, deployment, package-registry, or infrastructure source.

## 7. LSP observable contract

The bounded reference runtime must cross a real subprocess/stdio boundary and prove:

1. `initialize` returns named server information and only implemented capabilities.
2. standard output contains only valid Content-Length framed JSON-RPC.
3. `textDocument/didOpen` stores the exact document and publishes diagnostics.
4. `textDocument/didChange` replaces full-sync content and republishes diagnostics.
5. `textDocument/didClose` removes state and publishes an empty diagnostic set.
6. Turtle, TOML/ggen manifests, and Tera surfaces receive deterministic diagnostics.
7. completion, hover, definition, references, rename, document symbols, workspace symbols, formatting, range formatting, code actions, folding ranges, semantic tokens, inlay hints, and code lenses either execute or are not advertised.
8. malformed JSON receives a typed JSON-RPC parse error without poisoning the next valid request.
9. unknown requests receive method-not-found.
10. `shutdown` replies successfully and `exit` terminates cleanly.
11. repeated execution over identical inputs produces semantically identical protocol outputs.
12. no handler executes shell commands, opens network connections, writes governed files, or imports third-party packages.

## 8. LSP refusal boundary

The runtime refuses:

- invalid or oversized transport frames;
- non-UTF-8 JSON bodies;
- non-object JSON-RPC messages;
- unsupported methods represented as successful execution;
- partial incremental changes while only full synchronization is advertised;
- file or network actuation through protocol payloads;
- stdout logging;
- a standing claim above the verifier's observed scope.

Transport-fatal refusals use `GGEN-LSP-TRANSPORT-*` on stderr and a nonzero process exit. Recoverable JSON-RPC errors use standard protocol error codes.

## 9. Construction and generated-surface law

Authored source lives under the ticket-owned paths. Generated evidence is produced only by its declared verifier. Repair source or verifier logic rather than hand-editing a report to create apparent conformance.

The verifier report excludes itself from the source-manifest digest, then binds every authored input by SHA-256. Re-running the verifier without source changes must reproduce identical JSON bytes.

## 10. Verification ladder

Run the cheapest high-information gates first:

```text
source compile
→ analyzer unit tests
→ real subprocess framing tests
→ initialize/open/change/close lifecycle
→ feature requests
→ malformed-message and unknown-method falsifiers
→ stdout-purity assertion
→ deterministic verifier replay
```

Rust compatibility with the historical `ggen/crates/ggen-lsp` implementation is a separate rail. If Rust is unavailable, report `BLOCKED:TOOLCHAIN_UNAVAILABLE`; do not substitute that block for failure of the executable reference runtime.

## 11. Git and publication safety

Resolve the exact base before editing. Preserve unrelated branches and user work. Do not use destructive Git commands or force-push. Publication sequence:

```text
inspect → admit plan → implement → verify → replay
→ review bounded diff → intentional commit → non-force branch update
→ draft pull request
```

GitHub Actions and hosted CI are not evidence for `GL-LSP-001`. Local execution is required. Never merge unless explicitly requested.

## 12. Ticket doctrine

A valid ticket is deterministic and answers “what observation would falsify completion?” It contains identity, title, authority, exact base, problem, scope, inputs, outputs, exclusions, owner, witnesses, falsifiers, commands, evidence, receipt, replay, and expected state transition.

## 13. Required task receipt

Every completed task reports:

- repository, base, branch, and candidate SHA;
- O and O*;
- transport attempts and typed failures;
- files changed and authority affected;
- commands and exit statuses;
- observed protocol boundaries;
- verifier report and replay result;
- scoped standing;
- exclusions, blockers, and falsifiers.

> Preserve the contract. Admit the source. Execute the boundary. Replay the receipt.
