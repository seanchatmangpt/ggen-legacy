# Enterprise Architecture Foundry Program

**Real update, 2026-08-12**: this program reached genuine terminal `ALIVE`
standing — all 11 workstreams (A–K) independently admitted, receipted, and
verified. See the [Completion PRD](15-foundry-completion-prd.md) and
[Completion ARD](16-foundry-completion-ard.md) for the full real history.
The runtime (originally PR #544 below) has since **moved from
`seanchatmangpt/ggen` to this repo** (`tools/architecture-foundry`),
matching its actual role — every one of its binaries admits things into
`ggen-legacy` specifically. The coordinates below are the real historical
record of how the program started; they are not the current state.

This chapter admits bounded projections of the Enterprise Architecture Foundry plan, Rust runtime, and receiving boundary authored today across `seanchatmangpt/ggen` PRs #543 and #544 and `seanchatmangpt/ggen-legacy` PR #2.

The plan source coordinate is:

```text
PR #543
999db36647feeb2dfd0bd2250d2db2ef00b887c4
base: a35086e7a12e2ff1724f307d2ef47eb165fcae29
```

The current runtime candidate coordinate is:

```text
PR #544
f831e4d9fa80fe345349ce5d6e0fff41e6eb2a4a
base: 999db36647feeb2dfd0bd2250d2db2ef00b887c4
path: tools/architecture-foundry
upstream dedicated runtime workflow: success
```

The receiving-boundary coordinate is:

```text
ggen-legacy PR #2
eeaa99ef65c1438a3dea100af775aee222aac9c8
workflow run: 30678135632
observed runtime: 0175ead9748a7f41018ec037828865ae11cfe267
corpus merge head: 7e83360e88b73df4d3b65dceaa8c0b5538cd36a4
```

All three pull requests remain open and draft. Their standing is not transferred. The stable manufacturing kernel used by Project 001 remains `ggen@0f39227c102e0ac7519f0f27561356227a518653`.

## Repository topology

```text
ggen
= Repository Manufacturing Kernel

ggen-legacy
= Enterprise Architecture Foundry Corpus

manufactured customer repositories
= Admitted Solution Instances
```

`ggen-legacy` is not a dead archive. Legacy means that a system has accumulated enough behavioral and architectural evidence to be mined for reusable knowledge.

## Five corpus layers

The foundry keeps these layers separate:

```text
observed source
→ admitted evidence
→ generalized primitive
→ composed solution pack
→ executable reference witness
```

Copied code without provenance, disposition, destination admission, recovery evidence, equivalence, and cross-repository receipts is not corpus formation.

## Agent roles

The admitted work program defines eight non-interchangeable roles:

1. observer agent;
2. disposition agent;
3. extraction agent;
4. primitive-generalization agent;
5. pack-composition agent;
6. equivalence agent;
7. independent-verifier agent;
8. integration agent.

An agent may recommend a state transition. Only the designated verifier may assign final standing.

## A–K work program

The workstreams are dependency ordered:

| ID | Workstream | Owner |
|---|---|---|
| A | Exact-head baseline | integration agent |
| B | Exhaustive observation | observer agent |
| C | Capability admission | disposition agent |
| D | Kernel-corpus classification | disposition agent |
| E | Cross-repository extraction | extraction agent |
| F | Primitive generalization | primitive-generalization agent |
| G | bblock and solution-pack composition | pack-composition agent |
| H | Full equivalence closure | equivalence agent |
| I | Independent verification | independent-verifier agent |
| J | Clean-room manufacture and replay | integration agent |
| K | Fortune-scale reference reconstitution | pack-composition agent |

The machine-readable projections are:

- `authority/foundry-work-program.json`
- `foundry/bootstrap.yaml`
- `schemas/migration-manifest.schema.json`
- `schemas/workstream-report.schema.json`
- `schemas/final-evidence.schema.json`

## Rust runtime evidence

PR #544 implements a standalone Rust control plane at `tools/architecture-foundry`. The runtime validates the A–K graph, binds clean source and corpus heads, initializes typed corpus state, executes non-destructive extraction, issues BLAKE3 lineage receipts, admits workstreams from independently authored evidence, verifies lineage, replays receipt-bound outputs, and refuses final `ALIVE` until all final predicates close.

Its command surface is:

```text
validate-program
baseline
initialize-corpus
extract
admit-workstream
admit-solution
verify
replay
```

Three same-day evidence rails are preserved:

1. Runtime head `7313d602…` failed three real-Git tests because its workflow ran workspace-wide formatting before requiring a clean source worktree.
2. The receiving workflow ran runtime head `0175ead9…` with manifest-scoped formatting; four real-Git tests passed, replay matched, and standing correctly remained `PARTIAL_ALIVE`.
3. Current runtime head `f831e4d9…` has a successful dedicated runtime workflow and is independently compiled and tested by Project 001 CI at its exact coordinate.

Project 001 still records `runtime_dependency_admitted=false`. Exact candidate verification is evidence, not automatic dependency or product promotion.

## Receiving contract

`foundry/bootstrap.yaml` is canonical JSON-subset YAML so it can be consumed by YAML systems while remaining deterministically parseable with the standard JSON parser.

It binds:

- stable ggen manufacturing head;
- foundry plan head;
- receiving runtime head;
- current runtime candidate head;
- corpus base;
- A–K initial states;
- migration, workstream, and final-evidence schemas;
- refusal conditions;
- the terminal theorem.

The migration manifest allows exactly five final dispositions: `PRESERVED`, `SUBSUMED`, `REPLACED`, `ARCHIVED`, and `REFUSED`. The final-evidence schema allows `ALIVE` only when every terminal predicate is structurally closed.

## Initial solution packs

The first Fortune-scale architecture families are:

- repository manufacturing platform;
- enterprise developer platform;
- governed data lakehouse platform;
- event and integration platform;
- identity and policy enforcement platform;
- AI and agent execution platform;
- process evidence and observability platform;
- regulated release and supply-chain platform.

These are planned foundry outputs. They are not claimed implemented by Project 001.

## Cross-repository law

Every extraction from `ggen` to `ggen-legacy` must bind source repository, commit, path, digest, capability IDs, disposition, destination, destination digest, replacement owner, migration evidence, equivalence report, and receipt.

Every manufacture into a customer repository must bind customer observation, selected primitives and packs, foundry and kernel coordinates, plan digest, generated tree, verifier report, replay report, and solution standing.

## Hard blocks

A valid hard block is limited to inaccessible required source, unavailable boundary credentials, irrecoverable historical evidence, legally prohibited transfer, or a genuinely non-derivable accountable business decision.

Queued runners, elapsed time, task count, context size, successful agent return, and intermediate refusal are not hard blocks.

## Terminal theorem

```text
ggen_kernel_admitted=true
ggen_legacy_corpus_admitted=true
unknown_capabilities=0
unknown_dispositions=0
unknown_standings=0
unassigned_verifiers=0
missing_equivalence_cases=0
equivalence_failures=0
replay_differences=0
cross_repository_receipts_valid=true
fortune_scale_reference_manufactured=true
solution_admission=true
standing=ALIVE
```

Project 001 closes only the verifier-appliance reference scope. It does not claim that the complete A–K foundry program has reached this theorem.
