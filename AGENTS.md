# AGENTS.md — ggen-legacy executable reconstruction

## Authority and exact subject

This file governs `seanchatmangpt/ggen-legacy`.

- admitted reconstruction base: `70e599a599fedb7c62c965377cc2f80df1fa01ec`
- active executable ticket: `GL-LSP-001`
- concurrent executable ticket: `GL-PLAN-002`
- drafted tickets (see tickets/):
  - `GL-ARCH-003`: admitted executable ticket
  - `GL-AUTO-001`: `BLOCKED` — corrected 2026-08-21 by `GL-ERRC-023`. A fresh run of the
  - `GL-CONTRACT-004`: admitted, `NOT_STARTED` — drafted this session, not executed
  - `GL-ERRC-008`: admitted, `NOT_STARTED` — drafted by ultracode ERRC pass
  - `GL-ERRC-009`: `EXECUTED` — fix applied and verified this session against the real
  - `GL-ERRC-010`: admitted, `NOT_STARTED` — drafted by ultracode ERRC pass 3
  - `GL-ERRC-011`: EXECUTED
  - `GL-ERRC-012`: `EXECUTED` — planning-document split performed for real this
  - `GL-ERRC-013`: `EXECUTED` — fix applied and verified: `AGENTS.md` gained a
  - `GL-ERRC-014`: admitted, `NOT_STARTED` — drafted by ultracode ERRC pass 4
  - `GL-ERRC-015`: EXECUTED
  - `GL-ERRC-016`: EXECUTED
  - `GL-ERRC-017`: admitted, `NOT_STARTED` — drafted by ultracode ERRC pass 5
  - `GL-ERRC-018`: admitted, `NOT_STARTED` — drafted by ultracode ERRC pass 5
  - `GL-ERRC-019`: `EXECUTED` — fixed and verified this session (see "Execution evidence" below)
  - `GL-ERRC-020`: admitted, `NOT_STARTED` — drafted by standing ultracode exploration cron
  - `GL-ERRC-022`: `EXECUTED` — real recipe added, real binary compiled and invoked, see
  - `GL-ERRC-023`: `EXECUTED` — corrected `tickets/GL-AUTO-001.md` in place per Hard Laws 1-4
  - `GL-EXP-001`: `EXECUTED` — real fix landed in the main checkout and re-verified there
  - `GL-EXP-002`: `EXECUTED` — real fix landed in the main checkout and re-verified there
  - `GL-EXP-003`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-004`: admitted, NOT_STARTED — drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-005`: EXECUTED -- drafted by standing ultracode exploration cron (GL-EXP namespace), executed this session
  - `GL-EXP-006`: `EXECUTED` — real fix landed in the main checkout and re-verified there
  - `GL-EXP-007`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-008`: admitted, NOT_STARTED — drafted by standing ultracode exploration cron
  - `GL-EXP-009`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-010`: admitted, `NOT_STARTED` — drafted by standing ultracode exploration cron
  - `GL-EXP-011`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-012`: admitted, NOT_STARTED — drafted by standing ultracode exploration cron
  - `GL-EXP-013`: `EXECUTED` 2026-08-21 — real fix landed in the main checkout and re-verified there
  - `GL-EXP-014`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-015`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-016`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-017`: `EXECUTED` 2026-08-21 — real fix landed in the main checkout and re-verified there
  - `GL-EXP-018`: `EXECUTED` — the two rows this ticket specifies were added to
  - `GL-EXP-019`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-020`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-021`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-022`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-023`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-024`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-025`: EXECUTED -- fix landed and verified this session in worktree
  - `GL-EXP-026`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-027`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-028`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-029`: `EXECUTED` — dead field deleted, build and full test suite verified green
  - `GL-EXP-030`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-031`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-032`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-033`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-034`: admitted, `NOT_STARTED` -- drafted by standing ultracode exploration cron
  - `GL-EXP-035`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-036`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-037`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-038`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-039`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-040`: `EXECUTED` — both digests corrected in the main checkout and
  - `GL-EXP-041`: admitted, `NOT_STARTED` — drafted by standing ultracode exploration cron
  - `GL-EXP-042`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-043`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-044`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-045`: `EXECUTED` 2026-08-21 -- real fix landed in the main checkout and re-verified
  - `GL-EXP-046`: `EXECUTED` -- real fix landed in the main checkout and re-verified
  - `GL-EXP-047`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
  - `GL-EXP-048`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-049`: `EXECUTED` 2026-08-21 -- real fix landed in the main checkout and re-verified
  - `GL-EXP-050`: `EXECUTED` — re-run performed for real this session against the real
  - `GL-EXP-051`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-EXP-052`: admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
  - `GL-LSP-001`: (no Status: line in ticket file)
  - `GL-MANUFACTURE-005`: admitted, `NOT_STARTED` — drafted this session, not executed
  - `GL-PLAN-002`: admitted concurrent executable ticket  
  - `GL-RECEIPT-007`: admitted, `NOT_STARTED` — drafted this session, not executed
  - `GL-VERIFY-006`: admitted, `NOT_STARTED` — drafted this session, not executed
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

Hosted CI is not a substitute for local execution. `gh` and hosted CI are excluded for the original GL-LSP-001 task; GL-PLAN-002 may add a replay workflow as supplemental publication evidence, never as a substitute for local verification.

## Repair law

Preserve the exact failure, classify the failed transition, repair the earliest lawful cause, add a permanent guard, rerun that boundary, and expand only after success. Never rerun an unchanged failure without a new hypothesis.

## Publication safety

Resolve exact base and head before writing. Preserve unrelated work. Use non-force updates. Do not merge unless explicitly requested.

## Required receipt

Report repository/base/branch/head, producing ontology and projection identities, pinned lsp-max identity, transports, files changed, commands/exits, observed execution, replay, scoped standing, exclusions, and draft PR identity.

For GL-PLAN-002 also report the pinned MFW producer identity, engine probe/execution states, blocked/unsupported planner edges, orchestration receipt-chain head, and explicit statement that planning has no actuation authority.
