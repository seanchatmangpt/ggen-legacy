# AGENTS.md — ggen-legacy executable reconstruction

## Authority and exact subject

This file governs `seanchatmangpt/ggen-legacy`.

- admitted reconstruction base: `70e599a599fedb7c62c965377cc2f80df1fa01ec`
- active executable ticket: `GL-LSP-001`
- concurrent executable ticket: `GL-PLAN-002`
- concurrent reconstitution ticket: `GL-OSTAR-001`
- protocol runtime: `lsp-max`
- pinned runtime: `seanchatmangpt/lsp-max@220d3251e959f6a58ce0311e995b31a85f98240c`
- received contract authority: `authority/lsp-contract.json`
- producing ontology: `seanchatmangpt/ggen:self-host/lsp-contract/ontology.ttl`
- publication boundary: draft pull request unless merge is explicitly authorized

The repository began as a documentation-only bootstrap. Executable source is admitted only by a deterministic ticket naming authority, exact dependencies, observable behavior, witnesses, falsifiers, verification, receipts, replay, and exclusions.

## Mission

Reconstruct observable legacy behavior, receive generalized contracts from the ggen manufacturing kernel, implement an independent executable witness, and preserve evidence sufficient for replay.

```text
observe → align → admit/refuse → receive contract
→ construct → execute → verify → receipt → replay → bounded standing
```

For `GL-LSP-001`:

```text
ggen ontology → ggen projection → received JSON/Rust contract
→ lsp-max framing and dispatch → admitted document state
→ ggen analysis behavior → receiver verifier → receipt
```

For `GL-PLAN-002`:

```text
benchmark observation → anti-leak goal reconstruction → finite reversible search graph
→ preserve all lawful planner/child edges → select bounded WIP child
→ construct-only manufacture intent → independent receipt → admit child
→ resume/replan parent → candidate POWL/MFW projections → replay
```

For `GL-OSTAR-001`:

```text
exact artifact census → contradictory observations → NO_AUTHORITY
→ bounded Rice fence → explicit O* admission or typed refusal
→ scoped equivalence → receipt → replay → EMPIRE candidate handoff
```

The receiver may validate and execute a contract. It may not alter the producing ontology, certify the ggen kernel, or convert source agreement into runtime `ALIVE`.

## Foundational order

1. Preserve prior purpose and recovery.
2. Fence unadmitted transitions.
3. Define objects, morphisms, authority, actuation, receipt, and replay.
4. State exclusions.
5. Name falsifiers against the exact subject.
6. Preserve reversible lawful extension points.
7. Bind implementation to executable acceptance.

Historical corpus material remains evidence. Adjacency is not refutation.

## Absolute invariants

### Zero unreceipted actuation

The LSP may analyze in-memory text and emit protocol messages. It has no ambient shell, Git, package-manager, deployment, network, or durable filesystem-write authority.

The planning subsystem may select candidates, construct plans/projections/intents, execute declared local planner subprocesses, and verify receipts. It has no broker and no ambient world-actuation authority. Planner or hook output never actuates directly.

### Observation is not admission

```text
O  = partial or stale observation
O* = admitted, aligned, grounded, bounded observation
A  = μ(O*)
R  = receipt(A)
```

Track observed, admitted, executed, changed, verified, inferred, refused, blocked, and unsupported separately.

### lsp-max is the protocol boundary

The runtime uses `LspService`, `Server`, `Client`, `LanguageServer`, and `lsp_types_max`. Hand-rolled framing, JSON-RPC dispatch, or substitute runtimes require a new admission decision.

### Generated contract ownership

`authority/lsp-contract.json`, `src/generated_contract.rs`, and `docs/lsp/CONTRACT.md` are projections of the ggen ontology. Do not hand-edit them. Update the producing ontology and templates, run ggen, copy the exact projections, and execute the independent receiver verifier.

### Representation synchronization

The received JSON and Rust contract must agree on every required method, surface, diagnostic, version, and schema. The runtime must implement every received handler and advertise every received capability truthfully. Drift is `BUILD_BROKEN`, not a warning.

### Protocol purity

Stdout is exclusively LSP framing. Tracing and refusals go to stderr. `clippy::print_stdout` remains denied.

### Exact dependency identity

`lsp-max` remains pinned to an exact Git revision or an exact admitted release.

External planning contracts remain pinned to exact observed producer identities. A connector object or registry entry is not a mounted tree or executed planner.

### No self-certification

Generated files, verifier source, documentation, and unexecuted tests cannot grant runtime `ALIVE`. The exact Rust candidate must compile, execute real stdio exchanges, and replay locally.

Planning source, projections, internal reference search, registry entries, and `--help` witnesses cannot grant external planner `ALIVE`. Exact-subject execution is required.

### Checkpoint is not crown

Contract synchronization proves only representation agreement. It does not prove runtime, release, production, certification, or sunset standing.

`planning/v26.8.7/verify.py` has a `PARTIAL_ALIVE` ceiling and cannot promote repository/release standing.

## Typed states

Use `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`, `UNSUPPORTED`, and `REFUSED:<CODE>` precisely.

No toolchain means `BLOCKED:TOOLCHAIN_UNAVAILABLE`, not `BUILD_BROKEN`. Source inspection is not execution.

## Authority precedence

1. `AGENTS.md`
2. `RELEASE_CONTROL.md`
3. admitted tickets
4. `authority/lsp-contract.json`
5. schemas and verifier contracts
6. executable source and fixtures
7. PRD/ARD
8. explanatory documentation
9. generated reports
10. assumptions

Contradiction returns `BLOCKED:AUTHORITY_CONTRADICTION`.

## GL-LSP-001 authored boundary

```text
AGENTS.md
Cargo.toml
rust-toolchain.toml
src/**
tests/**
tickets/GL-LSP-001.md
docs/lsp/**
authority/lsp-contract.json
scripts/verify_lsp_contract.py
evidence/lsp-contract/**
```

Required behavior:

1. Use lsp-max over stdin/stdout.
2. Implement the complete received method set.
3. Advertise only implemented capabilities; dynamic type hierarchy is lawful.
4. Track full-sync open documents.
5. Analyze all received source surfaces.
6. Emit all receiver-owned diagnostic families, including `GGEN-SRC-004`.
7. Clear diagnostics on close.
8. Refuse incremental changes while full sync is advertised.
9. Keep stdout frame-pure.
10. Independently verify the received JSON, generated Rust, runtime handlers, capabilities, analyzers, and no-actuation boundary.

## GL-PLAN-002 concurrent authored boundary

```text
AGENTS.md                              # this admission extension only
justfile                               # planning-max target only
.github/workflows/planning-v26-8-7.yml
planning/v26.8.7/**
tickets/GL-PLAN-002.md
```

Required behavior:

1. Reconstruct benchmark goal constraints without consuming reference/gold solutions.
2. Preserve the maximal finite reversible capability graph before selection.
3. Keep consequential child WIP bounded while retaining all candidate child edges.
4. Treat unsupported PDDL/planner edges as topology; never silently simplify or delete them.
5. Keep scikit-decide, Fast Downward, VAL, MFW, POWL, and internal finite-search evidence distinct.
6. Manufacture intents only; no hook or planner output has direct actuation authority.
7. Admit a child only through an exact-subject independent verification receipt.
8. Resume and replan blocked parents after child admission.
9. Emit and deterministically replay a tamper-evident orchestration event chain.
10. Never promote subsystem, repository, release, or production standing from planner success.

## GL-OSTAR-001 concurrent authored boundary

```text
AGENTS.md                              # this admission extension only
tickets/GL-OSTAR-001.md
tools/v26.8.1/authority_vacuum.py
tools/v26.8.1/test_authority_vacuum.py
tools/v26.8.1/equivalence_runner.py    # bounded-scope metadata only
reconstitution/ostar/**
```

Required behavior:

1. Treat every OSTAR/OntoStar repository, checkout, document, and executable as an observation; none is canonical by discovery.
2. Begin in `NO_AUTHORITY`; an observer may not name a canonical subject or self-promote evidence.
3. Record contradictory observations without choosing a winner.
4. Fence Rice's theorem precisely: no universal semantic decider or unrestricted equivalence claim.
5. Admit only an explicitly authored, digest-bound O* contract over named observable surfaces.
6. Require exact source coordinates and preserve unmaterialized subjects as `BLOCKED`/`UNKNOWN` topology.
7. Close every admitted capability to exactly one of `PRESERVED`, `SUBSUMED`, `REPLACED`, `ARCHIVED`, or `REFUSED`; final admission contains no `UNKNOWN`.
8. Treat a required-refusal study with no `REFUSED` disposition as `REFUSED:SCOPING_FAILURE_NO_REFUSAL`.
9. Manufacture no consequential action; the output is an EMPIRE construction candidate only.
10. Bind observation/admission artifacts to deterministic receipts and prove replay without volatile timestamps.

## Verification ladder

```text
python3 scripts/verify_lsp_contract.py
→ cargo fmt --all -- --check
→ cargo check --all-targets
→ cargo clippy --all-targets -- -D warnings
→ cargo test --all-targets
→ real stdio initialize/open/change/close/hierarchy exchange
→ malformed-message and refusal fixtures
→ deterministic replay
```

For `GL-PLAN-002`:

```text
python3 -m unittest discover -s planning/v26.8.7/tests -v
→ python3 planning/v26.8.7/verify.py --strict
→ planning/v26.8.7/skdecide_classical_engine.py --help
→ exact external planner/MFW replay when those runtimes/trees are observed available
```

For `GL-OSTAR-001`:

```text
python3 tools/v26.8.1/test_authority_vacuum.py -v
→ python3 tools/v26.8.1/authority_vacuum.py observe --study reconstitution/ostar/study.json --subject-root ontostar-open-ontologies=<exact checkout> --out <report-a>
→ repeat to <report-b>
→ python3 tools/v26.8.1/authority_vacuum.py replay --left <report-a> --right <report-b>
```

Hosted CI is not a substitute for local execution. `gh` and hosted CI are excluded for the original GL-LSP-001 task; GL-PLAN-002 may add a replay workflow as supplemental publication evidence, never as a substitute for local verification.

## Repair law

Preserve the exact failure, classify the failed transition, repair the earliest lawful cause, add a permanent guard, rerun that boundary, and expand only after success. Never rerun an unchanged failure without a new hypothesis.

## Publication safety

Resolve exact base and head before writing. Preserve unrelated work. Use non-force updates. Do not merge unless explicitly requested.

## Required receipt

Report repository/base/branch/head, producing ontology and projection identities, pinned lsp-max identity, transports, files changed, commands/exits, observed execution, replay, scoped standing, exclusions, and draft PR identity.

For GL-PLAN-002 also report the pinned MFW producer identity, engine probe/execution states, blocked/unsupported planner edges, orchestration receipt-chain head, and explicit statement that planning has no actuation authority.

## 21. After Code Reading law

`ggen-legacy` operates within the broader transition in which mandatory human source inspection may leave the software-production critical path. The governing method is **Proof-Carrying Software Manufacturing**.

Code is intermediate manufacturing material. The product is a verified business capability or conforming operational system.

A no-read claim is lawful only when it names:

1. the human implementation-reading task removed;
2. the machine control replacing it;
3. the authority defining intended consequences;
4. the architecture rule preventing drift;
5. planning, no-change, abstention, and refusal semantics;
6. the separate actuation authority;
7. the independent verifier;
8. positive witnesses and negative falsifiers;
9. runtime evidence;
10. explicit standing;
11. receipt and clean replay;
12. the same-object falsifier.

The human retains mission, architecture, invariants, risk, standards, acceptance, verifier design, evidence interpretation, exceptions, and irreversible decisions.

Never translate “the human did not read the implementation” into “the implementation was trusted.” The only admissible translation is:

```text
manual inspection removed
→ replacement controls admitted
→ independent falsification executed
→ evidence bound
→ standing computed
→ receipt valid
→ replay matched
```

A no-read claim is falsified when acceptance still requires human source inspection because requirements, architecture, behavior, or evidence cannot establish the necessary distinction elsewhere.

The strategic authority is `authority/after-code-reading.json`. Product and architecture projections are `product/AFTER_CODE_READING.md` and `architecture/AFTER_CODE_READING_ARCHITECTURE.md`.

> Reconstruct the contract. Manufacture the repository. Prove the standing.
>>>>>>> origin/agent/after-code-reading-pivot-v26.8.1
