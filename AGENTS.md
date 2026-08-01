# AGENTS.md — ggen-legacy v26.8.1

## 0. Root authority

This file is the normative contract for every human or automated agent operating in `ggen-legacy`.

- **Release:** `v26.8.1`
- **Category:** Verified Repository Reconstitution
- **Platform:** ggen Repository Manufacturing System
- **Method:** Evidence-Driven Repository Manufacture
- **Initial engagement:** Project 001 — ggen-legacy Self-Reconstitution

The repository begins as a non-production-source bootstrap. It must manufacture and verify the authority that will later manufacture the implementation. `ggen-legacy` is the first project governed by `ggen-legacy`.

## 1. Mission

Reconstruct the real behavioral contract of a legacy repository, encode it as machine-readable authority, manufacture a replacement from that authority, prove behavioral closure, and compute whether the predecessor may be retired.

```text
history → observation → admission → authority → manufacture
→ equivalence → independent verification → receipt → replay
→ Release Admission → Sunset Admission
```

The customer outcome is not “new code exists.” The outcome is that replacement standing is proven and retirement is admitted or refused.

## 2. Absolute invariants

### Zero unreceipted actuation

No material publication, mutation, release, deployment, migration, deletion, retirement, or external side effect may occur without a receipt.

### Observation is not admission

```text
O  = partial or stale observation
O* = admitted, aligned, complete, grounded, bounded observation
A  = μ(O*)
R  = receipt(A)
```

Preserve the distinction between observed, inferred, admitted, refused, unsupported, and unknown.

### No self-certification

The repository, implementing agent, generated report, coverage matrix, or documentation may not grant standing to itself. Standing is computed by an independent verifier over authority, implementation, witnesses, falsifiers, evidence, receipts, and replay.

### No silent unknowns

Zero findings and no observation are different states. An unexecuted observer remains `UNKNOWN`. No unknown capability, disposition, verifier, equivalence case, or standing may survive final admission.

### No hand-edited generated output

Repair authority, template, projector, or input. Do not patch generated artifacts to create apparent conformance.

### Checkpoint is not crown

A local passing check proves only its declared scope. Only the crown verifier may assign repository-level `ALIVE`.

### Exact source identity

Every implementation or verification claim is bound to an exact commit SHA and tree digest.

## 3. Project 001

The first admitted corpus is non-production-source authority:

- AGENTS and release law;
- Working Backwards press release, PR/FAQ, and Vision 2030;
- PRD and ARD;
- category and terminology authority;
- ontology, schema, policy, and decision specifications;
- verifier and evidence contracts;
- positive and negative fixtures;
- G0–G9 checkpoint law;
- security, privacy, resilience, operations, procurement, and support documents;
- deterministic source-admission tickets.

These artifacts do not prove that production implementation exists.

### Bootstrap theorem

Project 001 is complete only when terminology is consistent; every normative requirement has an owner; every output has a projector or implementation owner; every claim has a verifier; every refusal has a falsifier; launch gates are machine-readable; generation is reproducible; receipt and replay requirements are explicit; and the repository reports its actual bounded state.

Until executable exact-head verification and replay are observed, the maximum state is `PARTIAL_ALIVE`.

## 4. Bootstrap scope

Allowed surfaces include Markdown, mdBook, RDF/JSON/TOML authority, SHACL, schemas, fixtures, verifier specifications, read-only CI, and evidence examples.

Production implementation source is refused until a deterministic ticket admits it. Absent admission, do not add top-level `src/`, `crates/`, `packages/`, `cmd/`, `internal/`, `app/`, `lib/`, `services/`, or `runtime/`.

Also refused: hidden implementation, copied source without provenance, fake receipts, manually authored execution results, predeclared `ALIVE`, release tags without Release Admission, or Sunset Admission without a closed capability ledger.

A source-admission ticket must name authority, scope, observable contract, implementation boundary, toolchain, owner, positive witnesses, negative falsifiers, verification commands, receipt, replay, exclusions, and acceptance.

## 5. Authority precedence

1. `AGENTS.md`
2. `RELEASE_CONTROL.md`
3. admitted machine-readable authority under `authority/`
4. validated schemas and SHACL shapes
5. `product/PRD.md`
6. `architecture/ARD.md`
7. accepted decisions and deterministic tickets
8. verifier specifications
9. mdBook and explanatory documentation
10. generated reports
11. agent assumptions

A contradiction produces `BLOCKED / AUTHORITY_CONTRADICTION`. Do not silently choose the convenient instruction.

## 6. Required law-state workflow

Every material task follows:

```text
parse → route → observe → admit/refuse → diagnose/repair
→ manufacture → verify → receipt → replay → admission decision
```

- **Parse:** repository, exact base, outcome, acceptance, constraints, evidence.
- **Route:** observation, authority, documentation, schema, plan, fixture, verifier, implementation, repair, release, or sunset.
- **Observe:** inspect the complete relevant surface and record unobserved areas.
- **Admit/refuse:** validate before authority; return typed refusal for contradiction or missing basis.
- **Repair:** fix the earliest lawful cause: authority → schema → projector → implementation → verifier → evidence.
- **Manufacture:** produce only declared artifacts.
- **Verify:** narrow first, then expand.
- **Receipt:** bind source, authority, tools, inputs, outputs, results, environment, and state.
- **Replay:** re-execute from clean state.
- **Decide:** Release and Sunset are computed and separate.

## 7. G0–G9 Gall checkpoints

### G0 — Orient
Resolve tools, permissions, repository, exact base, authority, and constraints.

### G1 — Fence
Preserve purpose and dependencies before replacement or deletion. Record exclusions, falsifier, and retirement condition.

### G2 — Observe
Inventory the bounded current and historical contract. Unexecuted observers remain explicit.

### G3 — Admit
Validate observations into semantic authority. Refuse contradictions and missing required properties.

### G4 — Plan
Create a deterministic, dependency-closed manufacture and verification DAG.

### G5 — Manufacture
Project declared repository artifacts from authority. Refuse hand-edited generated output.

### G6 — Verify
Execute positive witnesses, negative falsifiers, schemas, integration, E2E, security, chaos, stress, and benchmark as required.

### G7 — Replay
Re-run from a clean state and require:

```text
NO_SEMANTIC_CHANGE
NO_GENERATED_DRIFT
REPLAY_MATCH
```

### G8 — Release Admission
Compute whether the manufactured replacement may release.

### G9 — Sunset Admission
Compute whether the predecessor may retire. Actual deletion is a separate irreversible, authorized, receipted actuation.

## 8. Typed states

Use exactly:

- `PARTIAL_ALIVE` — observed success for a bounded subset; crown open.
- `ALIVE` — complete declared scope observed and crown passed.
- `BLOCKED` — required dependency, authority, permission, artifact, or evidence unavailable.
- `BUILD_BROKEN` — declared build/manufacture command executed and failed.
- `UNKNOWN` — insufficient observation or admission.
- `UNSUPPORTED` — outside declared product boundary.

Policy may return `REFUSED`. Never translate `UNKNOWN → ALIVE`, `UNSUPPORTED → REFUSED`, `PARTIAL_ALIVE → ALIVE`, agent completion → checkpoint completion, or checkpoint completion → crown completion.

## 9. Capability disposition law

Each final LegacyCapability has exactly one disposition:

- `PRESERVED`
- `SUBSUMED`
- `REPLACED`
- `ARCHIVED`
- `REFUSED`

Each records identity, provenance, observable contract, rationale, owner, equivalence/refusal case, verifier, evidence, receipt, and standing. A refusal requires a negative contract and falsifier.

## 10. Repository doctrine

Read governing authority, ticket, adjacent docs, schemas, fixtures, verifier specifications, and status before writing. Preserve architecture and vocabulary. Make bounded diffs. Do not delete apparently stale work before proving provenance, purpose, dependency, disposition, and retirement condition. One failed transport or tool edge is not graph failure. Do not replace exact evidence with memory.

## 11. Git and publication safety

Resolve exact base before editing. Preserve unrelated user work. Do not use destructive Git commands without explicit authorization. Commits map to deterministic tickets or coherent acceptance boundaries. Publication requires diff review, verification, receipt, intentional commit, branch push, draft PR, and check inspection. A tag requires Release Admission.

## 12. Ticket doctrine

A valid ticket contains identity, title, authority, exact base, problem, bounded scope, inputs, outputs, exclusions, owner, positive witnesses, negative falsifiers, acceptance commands, evidence paths, receipt, replay, and expected state transition.

“What would falsify completion?” must be answerable.

## 13. Verification ladder

```text
protocol/unit
→ property/fuzz
→ stdio and HTTP integration
→ black-box CLI E2E
→ security
→ chaos
→ stress
→ benchmark
→ replay
→ external verifier report
```

Mocks may support isolated units. Crown evidence crosses real declared process, filesystem, serialization, protocol, database/service, receipt, and replay boundaries.

The machine-readable report records exact revision, tree digest, toolchain, authority digests, suites, commands, crossed boundaries, evidence, pass/fail/blocked/unsupported checks, refusal codes, benchmarks, replay, standing, and verifier identity.

## 14. Evidence and receipts

Every material claim names claim, scope, source identity, authority identity, verifier, execution, result, artifact digest, exclusions, and typed state.

A receipt binds version, run, project, exact source, authority digest, ticket, toolchain, environment, input/output digests, actuator, exit status, verifier results, time, lineage, and final state. Do not hand-author execution receipts.

## 15. Documentation and claim law

Documentation distinguishes current fact, admitted design, future target, example, unsupported claim, and unresolved question. It may explain authority but cannot prove implementation, execution, receipt validity, replay, Release Admission, Sunset Admission, or production standing.

Do not write future functionality in present tense unless the document explicitly labels it as target behavior.

## 16. Ontology and schema law

Prefer PROV-O, DCAT, DCTERMS, SKOS, SHACL, ODRL, FOAF, OCEL, QUDT, SOSA, and FIBO where applicable. Create local terms only when public vocabularies fail to preserve the required distinction.

SHACL and schemas are admission boundaries. They reject missing identity/provenance, contradictory or multiple dispositions, missing verifier/equivalence cases, illegal standing transitions, self-certification loops, and missing receipt linkage.

## 17. Preserve → Fence → Calculus

Before replacing an established surface, record:

1. **Preserve:** purpose and dependency.
2. **Fence:** boundary protecting valid behavior.
3. **Calculus:** admitted transformation.
4. **Exclusions:** what is outside the claim.
5. **Falsifier:** same-object observation proving the change wrong.
6. **Extension:** lawful future capability.
7. **Operationalization:** commands, fixtures, verifiers, receipts, and replay.

Adjacency is not refutation.

## 18. v26.8.1 launch law

The future product crown requires:

```text
unknown_capabilities=0
unknown_dispositions=0
unknown_standings=0
unassigned_verifiers=0
missing_equivalence_cases=0
equivalence_failures=0
replay_differences=0
release_admitted=true
sunset_admitted=true
standing=ALIVE
```

Project 001 uses a separate bootstrap crown and must not fabricate a predecessor or Sunset Admission.

## 19. Required task report

Every task reports state, exact base SHA, scope, files changed, authority affected, commands, observed results, receipts, replay status, exclusions, remaining unknowns, blockers, and next lawful checkpoint.

## 20. Immediate bootstrap order

1. repository doctrine;
2. product vocabulary;
3. Project 001 charter;
4. PRD;
5. ARD;
6. ontology and admission rules;
7. evidence, receipt, verifier, release, and sunset schemas;
8. positive, negative, contradiction, and replay fixtures;
9. G0–G9 verifier specifications;
10. deterministic source-admission tickets;
11. first implementation;
12. full verification ladder;
13. clean-room replay;
14. Project 001 crown.

The repository must first manufacture the authority that will manufacture the implementation.

> Reconstruct the contract. Manufacture the repository. Prove the standing.
