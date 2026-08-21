# Innovation Exploration — Cycle Report (v26.9.1 Capstone)

## 1. Top 3 Candidates

### 1. dsrust/Groq disposition proposer never wired into the admission workflow
**Score: 10** (Novelty 2, Feasibility 5, Leverage 3)

`tools/dsrust-disposition-proposer`'s `propose-disposition` CLI is a real, tested tool that proposes a legacy-capability disposition from the same five evidence fields `admit_capabilities.rs` admits on, but nothing (no justfile target, no CI step, no import) wires it into the admission workflow.

Justification: not a new capability — the tool is already built and tested — just wiring an existing CLI into an existing pipeline as an optional pre-step. A single justfile target (plus optional CI step) is easily a one-session change, and it gives the admission workflow an optional LLM-suggested disposition without touching the admission logic itself.

Location: `/Users/sac/ggen-legacy/tools/dsrust-disposition-proposer/src/main.rs:1-80`

### 2. planning/v26.8.7 CLI subcommands not exposed through any top-level ggen-legacy verb
**Score: 10** (Novelty 2, Feasibility 5, Leverage 3)

`planning/v26.8.7/cli.py` implements a full A*-based capability planner CLI (`reconstruct-goal`, `solve-capabilities`, `classify-pddl`, `orchestrate`, `replay`, `verify-plan`, `probe-engine`, `run-engine`) with real subprocess-based tests, but it's only invokable directly as a Python script — not reachable from the Rust `ggen-legacy` binary or any justfile target.

Justification: plumbing, not new logic — the planner already exists and is tested. Adding a `just` target or a thin `ggen-legacy plan` subcommand shelling out to `cli.py` is small and well-bounded. Unlocks discoverability of an already-built A* planner for future work.

Location: `/Users/sac/ggen-legacy/planning/v26.8.7/cli.py:9-144`

### 3. wasm4pm OCLA algorithm not in the algorithm registry
**Score: 9** (Novelty 2, Feasibility 5, Leverage 2)

`wasm4pm/src/advanced/ocla.rs` implements a real object-centric footprint abstraction (`OCLanguageAbstraction::create_from_ocel`) alongside sibling advanced algorithms, but unlike them it does not appear in the TypeScript CLI/MCP algorithm registry (`apps/wasm4pm/src/engines/algorithms.ts`), making it reachable only by writing new Rust code.

Justification: registration/plumbing gap, not a new algorithm. Adding one registry entry plus a wasm binding call is trivial and well within one session. Unlocks OCLA for CLI/MCP users, though it's a single point fix with no compounding effect elsewhere.

Location: `/Users/sac/wasm4pm/wasm4pm/src/advanced/ocla.rs:1-45`

## 2. Full Ranked Table

| Rank | Score | Title | Novelty | Feasibility | Leverage | Lens |
|---|---|---|---|---|---|---|
| 1 | 10 | dsrust/Groq disposition proposer never wired into the admission workflow | 2 | 5 | 3 | unexploited-capability |
| 2 | 10 | planning/v26.8.7 CLI subcommands not exposed through any top-level ggen-legacy verb | 2 | 5 | 3 | unexploited-capability |
| 3 | 9 | wasm4pm OCLA algorithm not in the algorithm registry | 2 | 5 | 2 | unexploited-capability |
| 4 | 9 | wasm4pm/ocpq -> ggen/praxis-graphlaw: object-centric query results never feed the RDF law-state engine | 3 | 2 | 4 | cross-repo-integration |
| 5 | 9 | wasm4pm/prolog8+wasm4pm-cognition -> ggen-legacy/evidence-verifier: hand-authored admission JSON could be real proof-engine output | 3 | 2 | 4 | cross-repo-integration |
| 6 | 9 | Promote the bounded-admission grant/resume loop into a real CLI verb | 2 | 4 | 3 | ambition-vs-implementation-gap |
| 7 | 9 | clap-noun-verb README pins a stale, two-minor-version-old release on announcement day | 1 | 5 | 3 | external-facing-gap |
| 8 | 9 | ERRC follow-through loop is a hand-maintained tracker, not a reusable skill | 2 | 4 | 3 | workflow-tooling-leverage |
| 9 | 8 | ggen/ggen-graph (oxigraph) -> ggen-legacy/ontology+authority corpus never loaded into a SPARQL store | 2 | 3 | 3 | cross-repo-integration |
| 10 | 8 | praxis README has no Quickstart section | 1 | 5 | 2 | external-facing-gap |
| 11 | 8 | ggen README's Quickstart contradicts the newest CHANGELOG entry's install story | 1 | 5 | 2 | external-facing-gap |
| 12 | 8 | Codify the numbered-findings + synthesis output convention into the config-audit skill itself | 1 | 5 | 2 | workflow-tooling-leverage |
| 13 | 7 | Live workflow sockets for late-arriving artifacts outside the synthetic tick loop | 2 | 2 | 3 | ambition-vs-implementation-gap |
| 14 | 5 | Native nested POWL composition still lawfully flattened at the runner adapter | 2 | 1 | 2 | ambition-vs-implementation-gap |

## 3. Recommended Next Action

Wire `tools/dsrust-disposition-proposer`'s `propose-disposition` CLI into the admission workflow as an optional pre-step: add a `just admit-propose-disposition` (or equivalent) justfile target that invokes the CLI ahead of `admit_capabilities.rs`, passing the same five evidence fields, and surface its suggested disposition as an optional annotation in the admission output (not a gate). This is the tied-highest-score item, has the highest feasibility-to-effort ratio of the top candidates (single justfile target against an already-tested, already-built tool), and is the most concretely scoped: no schema design, no cross-repo dependency work, no new proof-engine mapping — just one wiring step.
