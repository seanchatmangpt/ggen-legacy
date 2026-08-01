# After Code Reading

## The historical hinge

On July 23, 2026, Robert C. Martin publicly described a strategy of not reading the implementation produced by his agents because mandatory source inspection would prevent him from obtaining their productivity benefit. Instead, he described an extensive gauntlet of tests, executable scenarios, QA procedures, quality metrics, mutation testing, coverage, and related constraints.

Primary public coordinate:

`https://x.com/unclebobmartin/status/2080257779395154409`

The importance of this event is not celebrity endorsement. It is the clarity of the boundary it exposes:

> **Machines can produce implementation faster than humans can inspect it. An organization that keeps mandatory line-by-line source review as the governing gate preserves human reading as the final production ceiling.**

The tweet is an external observation. It does not prove this repository's doctrine, implementation, market adoption, or standing.

## The lane

The complete body of work now resolves into one question:

> **What replaces human code reading as the basis of software trust?**

The answer is not blind acceptance. It is not a better prompt. It is not test coverage in isolation.

The answer is **Proof-Carrying Software Manufacturing**:

```text
mission
→ admitted requirements
→ machine-readable production law
→ full planning
→ manufacture
→ authorized actuation
→ independent falsification
→ operational evidence
→ standing
→ receipt
→ replay
→ kaizen
```

## Category stack

- **After Manual Code** — the broad transition from manual implementation construction to machine-scale manufacture.
- **After Code Reading** — the engineering boundary where mandatory source inspection leaves the production critical path.
- **Proof-Carrying Software Manufacturing** — the method replacing reading with admitted controls and evidence.
- **Software Systems Manufacturer** — the accountable profession governing mission, architecture, risk, acceptance, and irreversible decisions.
- **Verified Repository Reconstitution** — the `ggen-legacy` product contribution: reconstruct, manufacture, verify, replay, and compute retirement standing.

The relationship is fixed:

> **After Manual Code is the transition. After Code Reading is the boundary. Proof-Carrying Software Manufacturing is the method. Software Systems Manufacturer is the profession. Verified Repository Reconstitution is the ggen-legacy product contribution.**

## Why ordinary AI-assisted development is insufficient

The old production model is:

```text
human writes
→ human reads
→ tests run
→ software ships
```

The common agentic model is:

```text
machine writes rapidly
→ human reads slowly
→ tests run
→ software ships
```

That is mechanized writing attached to artisanal inspection. The factory has not been redesigned.

A post-reading system instead operates as:

```text
human governs intended consequences
→ requirements and architecture become authority
→ planners select lawful routes
→ machinery constructs
→ independent machinery attacks the result
→ runtime evidence records what happened
→ standing is computed
→ receipts bind the path
→ clean replay establishes reproducibility
```

Code is intermediate manufacturing material. The product is a verified business capability or conforming operational system.

## What replaces source inspection

### Admitted requirements

Business requirements, architecture rules, security policy, data contracts, infrastructure constraints, accepted dependencies, performance budgets, obligations, and refusal conditions become bounded authority.

Plausible agent inference remains inference until admitted.

### Full planning

Planning selects intended state transitions before implementation exists. It must model lawful action, prohibition, no-change, abstention, uncertainty, recovery, risk, and required evidence.

### Bounded manufacture

Generators and agents manufacture complete capability surfaces: application, service, integration, infrastructure, policy, tests, deployment, observability, documentation, and evidence projections.

### Separated actuation

Selection, authorization, and execution remain distinct:

```text
selection ≠ authorization ≠ execution
```

A planner cannot silently become an actuator.

### Mechanical inspection

Compilation, type checking, static analysis, dependency rules, architecture conformance, unit/property/integration/black-box testing, fuzzing, mutation testing, security analysis, stress, chaos, and replay inspect the product mechanically.

### Independent falsification

The producer does not certify itself. Separate verifiers rederive claims and must be able to return counterexamples and typed refusal.

### Operational evidence

Source projections describe what was manufactured. Process evidence establishes what executed, under which authority, in which order, with which inputs, failures, retries, and terminal consequences.

### Standing

Every bounded object receives an explicit state:

```text
PARTIAL_ALIVE
ALIVE
BLOCKED
BUILD_BROKEN
UNKNOWN
UNSUPPORTED
```

Editorial confidence is not standing.

### Receipts and replay

Receipts bind source, authority, plan, toolchain, authorization, execution, verifier results, evidence, and lineage. Replay re-executes from clean state.

The question changes from “Who read the code?” to:

> **What did this artifact survive, who authorized its requirements, which independent mechanisms tried to falsify it, and can the complete run be replayed?**

## The human role

The doctrine does not reduce accountability. It moves human judgment to the larger system boundary.

Humans retain authority over:

- mission and business consequences;
- architecture and invariants;
- risk and security boundaries;
- acceptance criteria;
- verifier design;
- evidence interpretation;
- exceptions;
- irreversible decisions;
- Release and Sunset authorization.

The accountable human need not know every implementation line. The accountable human must know the law under which every result was admitted, generated, inspected, refused, accepted, released, or retired.

## How the ecosystem maps

| Surface | Contribution after code reading |
|---|---|
| `ggen` | Manufactures governed software systems from admitted semantic authority. |
| `ggen-legacy` | Reconstructs predecessor contracts and determines replacement and retirement standing. |
| `ferroplan` | Plans deterministic work and probabilistic policies, including abstention and risk. |
| BRCE | Preserves selection/authorization/execution separation and zero unreceipted actuation. |
| `wasm4pm` | Supplies runtime process evidence, conformance, receipt, and replay. |
| TCPS | Operates the factory through pull, standard work, jidoka, andon, poka-yoke, and kaizen. |
| Ontologies, Graphlaw, SHACL | Supply machine-readable production law and admission. |
| `mfact`, Lean | Prove bounded invariants and countermodels. |
| MFW, POWL, planner portfolio | Explore alternative production routes and policy semantics. |
| Receipts and replay | Replace attention assertions with evidence of production. |

## Why ggen-legacy is central

A greenfield project can pretend that its requirements are known. A legacy repository cannot.

Its behavior is distributed across history, tests, consumers, configurations, operational traces, undocumented interfaces, and former maintainers. Therefore, removing code reading from legacy replacement requires more than generating new implementation.

`ggen-legacy` must:

1. observe the predecessor without treating observation as authority;
2. reconstruct the bounded observable contract;
3. admit that contract into semantic authority;
4. close every capability disposition;
5. manufacture a replacement;
6. independently compare consequences;
7. bind evidence and replay;
8. compute Release Admission;
9. compute Sunset Admission separately;
10. refuse retirement when closure is incomplete.

The replacement tree alone is not the product.

The product is a standing decision over the complete replacement and retirement boundary.

## Benchmarking the lane

The primary metric is:

```text
Post-Reading Throughput
=
verified engineering consequences
/
(human inspection time + elapsed time + compute + coordination)
```

Relevant measures include verified consequences, human attention, manual source lines read, admitted requirements, architecture violations, mutation score, fuzz failures, security findings, replay, receipt completeness, unnecessary actions avoided, cost, and time to standing.

The signature demonstration is:

> **A bounded capability was manufactured, independently verified, receipted, and replayed while the accountable human read zero implementation lines.**

That claim is forbidden unless the human inspection boundary was measured and every replacement control passed.

## Falsifier

The doctrine fails for a declared product boundary when:

- a human must inspect implementation to determine acceptance because semantic or evidentiary authority is insufficient;
- the producer's own generated tests are the only verifier;
- architecture can drift without mechanical detection;
- planning silently authorizes actuation;
- missing evidence becomes success;
- receipts cannot reproduce the run;
- `ALIVE` is assigned without independent replay;
- the system cannot represent no-change, refusal, or unsupported scope.

## Public positioning

> **ggen-legacy is Verified Repository Reconstitution for the era after human code reading leaves the critical path. It reconstructs what a legacy repository promised, manufactures a replacement from admitted authority, independently proves bounded closure, binds the result into receipts, replays it, and computes whether the predecessor may retire.**

The public event is the hinge. The code-reading bottleneck is the problem. Proof-Carrying Software Manufacturing is the answer. The repository corpus is the bounded implementation program.
