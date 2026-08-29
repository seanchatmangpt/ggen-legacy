# ggen-legacy

## What this repo is

`ggen-legacy` performs **Verified Repository Reconstitution**: it reconstructs the
observable contract of a legacy repository, admits that contract into
machine-readable authority, manufactures a replacement repository, independently
verifies behavioral closure, replays the result, and computes whether the
predecessor may be retired (`README.md`). The pipeline (`AGENTS.md`):

```text
observe → align → admit/refuse → receive contract
→ construct → execute → verify → receipt → replay → bounded standing
```

This is not generic software engineering — treat every claim, dependency, and
action against the discipline below, not general instinct.

## Canonical authority (defer in this order)

1. [`AGENTS.md`](AGENTS.md)
2. [`RELEASE_CONTROL.md`](RELEASE_CONTROL.md)
3. [`authority/project-001-promotion.json`](authority/project-001-promotion.json)
4. [`product/PRD.md`](product/PRD.md)
5. [`architecture/ARD.md`](architecture/ARD.md)
6. [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md)
7. [`governance/claims-register.md`](governance/claims-register.md)
8. [`governance/enterprise-maturity-model.md`](governance/enterprise-maturity-model.md)

## Standing vocabulary

Report subsystem state as one of: `ALIVE` / `PARTIAL_ALIVE` / `UNKNOWN` /
`BLOCKED` / `BUILD_BROKEN` / `UNSUPPORTED` / `REFUSED`. Never claim an
unqualified "works" or "done" — this is the local instantiation of the global
`no-overclaiming-conversational.md` rule, applied per-subsystem via this repo's
own vocabulary (see `README.md`'s standing table for the current example).

## Evidence-first: observation is not admission

```text
O  = partial or stale observation
O* = admitted, aligned, grounded, bounded observation
A  = μ(O*)
R  = receipt(A)
```

No claim about historical behavior without a real `git log`/`git log --all`
commit citation. Per `docs/v26.8.1/90-legacy/91-ggen-legacy-definition.md`, a
candidate legacy capability is admitted only on a real commit that deleted,
absorbed/renamed, or left it in a currently-reproducible broken state — never on
filename pattern-matching alone. Where no commit is found, the field says
`UNKNOWN` explicitly (`ggen:DISPOSITION_UNKNOWN`) rather than guessing. Every
discovered capability gets one of six dispositions: `PRESERVED` / `SUBSUMED` /
`REPLACED` / `ARCHIVED` / `REFUSED` / `DISPOSITION_UNKNOWN`.

## Ticket-gated admission

Nothing executable is admitted without a deterministic ticket (`GL-*`, see
`tickets/`). `AGENTS.md`'s header names the active and concurrent executable
tickets for the current session — check it before starting executable work.

## Zero unreceipted actuation

No ambient shell, Git, package-manager, deployment, network, or durable
filesystem-write authority beyond what an admitted ticket grants. The LSP
runtime may analyze in-memory text and emit protocol messages only; the
planning subsystem may select/construct/execute declared local planner
subprocesses and verify receipts only — no broker, no ambient world-actuation.
Publication boundary is a draft pull request unless merge is explicitly
authorized (this matches, and does not relax, this session's global
hard-confirmation rules for outward-facing actions).

## Dependency boundaries

- `wasm4pm` must never become a direct native dependency; native use routes
  through `wasm4pm-compat` only where admitted
  (`docs/v26.8.1/10-system/13-dependency-boundaries.md`). ggen-legacy emits
  process evidence; it does not import process-mining analysis.
- `lsp-max` is the sole protocol boundary (`LspService`, `Server`, `Client`,
  `LanguageServer`, `lsp_types_max`). Hand-rolled framing/dispatch or a
  substitute runtime requires a new admission decision.

## Versioning

CalVer `vYY.M.D`. Current milestone directories: `docs/v26.8.1/`,
`planning/v26.8.1/` and `planning/v26.8.7/`, `product/v26.8.3/`,
`tools/v26.8.1/`.

## Verify

```bash
just ci-all                                    # cargo fmt/check/clippy/test, both workspaces
just planning-max                              # python3 planning/v26.8.7/verify.py --strict
python3 scripts/verify_docs.py --strict
python3 scripts/verify_foundry_provenance.py
python3 scripts/verify_foundry_bootstrap.py
python3 scripts/verify_offline_transport.py
bash appliance/bin/run-reference-e2e.sh
mdbook build docs
```

Run the relevant subset before claiming any subsystem `ALIVE` (see the global
`verification-before-completion` skill — evidence before assertions, always).

## Testing discipline

This repo's evidence/receipt discipline is the global Chicago-school testing
rule (`~/.claude/rules/testing-chicago-style.md`) taken further: real commits,
real verifiers, real replay — no fabricated standing, no interaction-based
mocking of collaborators this codebase owns.

## Gall's Law: evolve from prior art, don't design from scratch

"A complex system that works is invariably found to have evolved from a simple
system that worked." Per deep research (2026-08-20), every stage of this
pipeline has a published, working analogue — evolve toward these instead of
inventing the stage from zero:

| Pipeline stage | Prior art to evolve from | Source |
|---|---|---|
| `observe` (git archaeology) | GraphRepo (Driller/Miner/Mapper on Neo4j), PyDriller/RepoDriller, RefactoringMiner | arXiv:2008.04884; `github.com/mauricioaniche/repodriller` |
| `align`/`admit` (contract extraction) | AgentModernize's Behavioral Specification Graphs (DAG of rules/pre-postconditions/control-flow as trust boundary) | arXiv:2605.17535; `github.com/nazib123/agent-modernize` |
| `construct` (manufacture replacement) | Strangler Fig incremental migration (façade routing → incremental shift → decommission → façade removal) | Azure Architecture Center: strangler-fig pattern |
| `verify` (behavioral equivalence) | Deterministic multi-axis trace comparison + witness-search algorithms when search plateaus, inspired by the paper's agentic "Locksmith Loop"/deterministic parity checks (**correction, ultracode backlog item 18**: "Parity Gate" and the three named axes below are this repo's own synthesis/paraphrase — verified against the real paper text, that specific name and vocabulary do not appear in it); oracles derived from the *contract*, never from legacy source (avoids circularity — matches this repo's observation-is-not-admission rule already) | arXiv:2607.28271 (concept only, not the "Parity Gate" name); arXiv:2605.17535 |
| `receipt`/`replay` | SLSA v1.0 provenance (in-toto attestation, `builder.id` trust anchor) + `slsa-verifier`; Kettle for TEE-hardware-attested builds if provenance must bind to real hardware | slsa.dev/spec/draft/build-provenance; `github.com/slsa-framework/slsa-verifier` |
| Safety-net capture of current behavior | Michael Feathers' characterization/golden-master testing | standard MSR literature |

**Load-bearing caveat, not a footnote**: the closest published analogue
(AgentModernize's full multi-agent+feedback pipeline) reaches only **8–19%
behavioral-equivalence rate** on real benchmarks (naive baselines: 0%). Borrowing
this architecture does not by itself deliver reliable equivalence — this repo's
own extra rigor (real commit citations, ticket-gated admission, `UNKNOWN` over
guessing) is load-bearing on top of it, not redundant with it.

### Gall checkpoints — implementation order

Each checkpoint must reach a real, verifiable `PARTIAL_ALIVE`/`ALIVE` on its own
before the next one starts — don't build checkpoint N+1 against an unverified
checkpoint N.

1. **Archaeology checkpoint** — wire a real MSR tool (PyDriller or RepoDriller,
   not a hand-rolled `git log` parser) into `tools/*/legacy_archaeology.py`'s
   `mine()` step; verify it reproduces the same commits the current hand-curated
   `CATALOG` already cites.
2. **Contract checkpoint** — model `ontology/*/legacy-capabilities.ttl`
   individuals as a BSG-style DAG (rule/pre/postcondition/control-flow nodes)
   instead of flat individuals, so equivalence verification in checkpoint 4 has
   a real graph to walk, not prose.
3. **Manufacture checkpoint** — express the Foundry replacement-construction
   step as an explicit Strangler Fig façade (route to legacy by default, shift
   per-capability as each is admitted) rather than a single big-bang swap.
4. **Verify checkpoint** — implement a deterministic Parity Gate (trace
   comparison across a small fixed set of axes) as the first equivalence
   verifier, before reaching for LLM-driven witness generation; given the
   8–19% BER ceiling above, treat any LLM-assisted verification as a
   supplement to the deterministic gate, never a replacement for it.
5. **Receipt checkpoint** — emit SLSA v1.0-shaped provenance for each
   manufactured artifact and verify it with `slsa-verifier` (or an equivalent
   in-repo checker) before a capability's disposition can move off `UNKNOWN`.

Each checkpoint gets its own `GL-*` ticket per the ticket-gated admission rule
above — this section names the target architecture, it does not itself admit
any of it.

## Code discovery

Use `mcp__lumen__semantic_search` first for locating code, definitions, or
usages, per the global project index (`~/CLAUDE.md`); fall back to `grep`/`find`
only for exact literal lookups.

## See Also

- [`AGENTS.md`](AGENTS.md) — full executable-reconstruction authority
- [`README.md`](README.md) — mission, current standing table, verify commands
- [`docs/v26.8.1/90-legacy/91-ggen-legacy-definition.md`](docs/v26.8.1/90-legacy/91-ggen-legacy-definition.md) — legacy capability definition and disposition criteria
