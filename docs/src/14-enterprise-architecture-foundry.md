# Enterprise Architecture Foundry Program

This chapter admits bounded projections of the Enterprise Architecture Foundry plan and runtime authored in `seanchatmangpt/ggen` PRs #543 and #544.

The plan source coordinate is:

```text
PR #543
999db36647feeb2dfd0bd2250d2db2ef00b887c4
base: a35086e7a12e2ff1724f307d2ef47eb165fcae29
```

The runtime source coordinate is:

```text
PR #544
7313d60266111bca7ff21257b71f68a6535e7294
base: 999db36647feeb2dfd0bd2250d2db2ef00b887c4
path: tools/architecture-foundry
```

Both pull requests remain open and draft. Their standing is not transferred. The stable manufacturing kernel used by Project 001 remains `ggen@0f39227c102e0ac7519f0f27561356227a518653`.

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

The machine-readable projection is `authority/foundry-work-program.json`.

## Rust runtime provenance

PR #544 implements a standalone Rust control plane at `tools/architecture-foundry`. The runtime is designed to validate the A–K graph, bind clean source and corpus heads, initialize typed corpus state, execute non-destructive extraction, issue BLAKE3 lineage receipts, admit workstreams from independently authored evidence, verify lineage, replay receipt-bound outputs, and refuse final `ALIVE` until all final predicates close.

Its declared command surface is:

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

Its real-boundary suite is `tools/architecture-foundry/tests/real_git.rs`. The suite creates real temporary Git repositories, commits checkpoints, extracts a real file, verifies lineage, replays receipts, and exercises workstream-A admission.

Project 001 records this as design and implementation provenance only. `runtime_dependency_admitted=false` remains mandatory until the branch is merged or another exact coordinate is independently admitted. The current verifier appliance does not execute code from PR #544.

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
