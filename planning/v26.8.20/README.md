# ggen-legacy planning v26.8.20 — ggen-legacy-mcp design proposal (pre-ticket)

**Standing: candidate proposal, not admitted.** No ticket naming authority is claimed here —
per `AGENTS.md`, "Executable source is admitted only by a deterministic ticket naming
authority... The repository began as a documentation-only bootstrap." This document exists so
a continuing agent or human can review and, if warranted, formally admit it (e.g. as
`GL-MCP-001`) rather than re-deriving the design from scratch. Nothing here is executable
source; nothing here should be treated as `ALIVE` or `PARTIAL_ALIVE` standing.

## Origin

Produced in a separate Claude Code session (2026-08-20/21) via: exploration of `~/wasm4pm`
(5 parallel Lumen-backed Explore agents), a review of a proposed drift-reconciliation design
against this account's real, grounded "Design for Combinatorial Maximalism" doctrine
(`~/ggen-marketplace/packs/ggen-combinatorial-maximalism-pack`), then a `/deep-research`
workflow (6 search angles, 23 sources fetched, 25 claims adversarially 3-vote verified: 21
confirmed, 4 refuted) asking what a pure Claude Code + ggen implementation of *this repo's own
methodology* — observe → admit → construct → verify → replay → retire — would need in terms of
Claude Code skills, subagents, orchestration, and an MCP server surface.

**Honesty note, carried forward from that research's own caveats**: no public source describes
"ggen-legacy" or "ggen-legacy-mcp" specifically — everything below is this account's own
architectural synthesis applying real, cited public patterns (MCP tool-surface design, Claude
Code workflow primitives, strangler-fig modernization, SLSA provenance) to this repo's real,
already-existing methodology. Treat the structure as a starting design, not verified fact.

## The proposed flow

```text
observe legacy target's real behavior (characterization-test style, not a spec)
→ admit captured behavior as RDF facts against a gla:-prefixed contract ontology
→ construct: ggen sync drives ontology.ttl -> gates/*.rq -> templates -> replacement code
→ verify: replay the observed contract against the constructed replacement, diff outputs
→ replay: re-run N times, BLAKE3-receipt each run
→ retire: compute standing (ALIVE / PARTIAL_ALIVE / UNKNOWN / REFUSED) for the predecessor
```

## 6 Claude Code skills (auto-discovered, one per stage)

| Skill | Triggers on | Does |
|---|---|---|
| `ggen-legacy:observe-contract` | "reconstruct the contract of X" | Characterization-test-style behavior capture (Feathers' technique) — real input→output pairs as a golden-master baseline, never a spec of intended behavior |
| `ggen-legacy:admit-contract` | "admit this contract" | Converts captured behavior into RDF facts against a `gla:` ontology (same shape as this session's `agp:CodegenTarget`/`aac:AshConnector` packs) |
| `ggen-legacy:construct-replacement` | "manufacture the replacement" | Drives `ggen sync` |
| `ggen-legacy:verify-closure` | "verify behavioral closure" | Replays the observed contract against the constructed replacement; strangler-fig façade/proxy pattern if traffic-shifting is in scope |
| `ggen-legacy:replay` | "replay X" | Re-runs N times, BLAKE3-receipts each run |
| `ggen-legacy:retire-predecessor` | "can X be retired" | Computes standing; never deletes without explicit authorization |

Each skill should dispatch to its own context-isolated subagent type rather than running
inline, matching this repo's own multi-agent/git discipline (`AGENTS.md` §9) of concurrent
fleets not polluting each other's working context.

## Orchestration

A Claude Code `Workflow` script (JavaScript, `agent()`/`pipeline()`/`parallel()` primitives),
not ad hoc chat turns: `pipeline()` for the sequential observe→admit→construct→verify→
replay→retire chain (each stage consumes the prior stage's output), `parallel()` inside
`verify` for adversarial cross-checking (3-vote pattern — the same mechanism this proposal's
own research claims were verified with).

## `ggen-legacy-mcp`: 7 scoped tools (6 lifecycle stages, `admit` split in two — see below),
## not a kitchen-sink server

```
observe_contract(target_path) -> ContractId               # read-only
propose_admit(contract_id) -> AdmissionCandidateId         # write, but non-final
confirm_admit(candidate_id, human_authorization) -> GraphAdmissionId  # write, scoped credentials, requires explicit authorization
construct_replacement(admission_id) -> BuildId              # invokes ggen sync
verify_closure(build_id, contract_id) -> Receipt            # read-only, ggen.legacy.*.verifier.v1-shaped
replay(receipt_id, n) -> ReplayReport                        # read-only
retire_predecessor(receipt_id) -> Standing                   # destructive, separate scope
```

**Prototyped split (2026-08-21):** the original single `admit_contract` tool was split into
`propose_admit`/`confirm_admit` to close the deep-research pass's own open question ("does
`admit` need to be split further into propose-admit and confirm-admit tools?"). Rationale:
`admit_contract` writes to the graph — a real, standing-changing action — but this repo's own
`candidate != verified != authorized != actuated` line (via
[[combinatorial-maximalism-review]]'s framing, and this repo's own ticket-gated-admission rule
in `AGENTS.md`) means a contract becoming a real graph admission should not be a single
irreversible call. `propose_admit` writes a non-final `AdmissionCandidateId` (inspectable,
diffable, revocable) without changing repo standing; `confirm_admit` requires an explicit
`human_authorization` argument (not inferred from context) and is the only tool that actually
changes admitted authority. This mirrors `retire_predecessor`'s existing destructive-tool
scoping — both `confirm_admit` and `retire_predecessor` are the two truly irreversible-standing
tools in this surface and should share the same credential scope, distinct from the four
propose/read tools. Not yet implemented against a real MCP server — this is the tool-surface
prototype, not a working server.

Confirmed by 2+ independent sources (AWS MCP strategy guide, community MCP best-practice
guides): a small, bounded, single-responsibility tool surface beats a kitchen-sink API — tool
definitions consume real context budget, and industry benchmarks cited in the research show up
to 236x token growth / ~9.5% accuracy drop as tool-surface size grows unbounded. Six
lifecycle-stage tools stays comfortably inside the 8-12-tools-per-bounded-domain range multiple
guides converge on.

**Security detail worth keeping, not just noting**: `admit_contract` and `retire_predecessor`
(the two write/destructive tools) need credentials scoped separately from the four read-only
tools. AWS's worked example: an agent hallucinating a delete action against a scoped-down
READ/CREATE-only token fails safely; the same hallucination against inherited admin credentials
succeeds destructively. This is the same `authorized != actuated` line this repo's own
methodology already draws — the scoped-credential mechanism is just a concrete way to enforce
it in an MCP tool surface specifically.

## Confirmed vs. refuted (carry forward, don't re-derive)

**Confirmed (high confidence, 3-0 or 2-1 vote)**:
- Claude Code dynamic workflows (script-controlled, `agent()`/`pipeline()`/`parallel()`,
  scales to hundreds of steps via script variables not agent context) fit this lifecycle
  directly.
- Skills are auto-discovered from description text; subagents isolate context per stage.
- MCP tool surfaces should be small/bounded/single-responsibility.
- Strangler-fig's façade/proxy pattern requires legacy source access and
  request-interceptability — this bounds when the whole retire/replace methodology even
  applies; it is not universally applicable.
- SLSA build provenance (BuildDefinition/RunDetails split, signer-identity binding,
  `slsa-verifier` tooling) is the closest existing public analogue for a machine-readable
  observable contract and a receipt-verification step.
- Characterization tests (Feathers) capture actual current behavior as a baseline, not a
  correctness spec — the right conceptual model for the `observe` stage specifically.
- RDFGraphGen (arXiv:2407.17941) demonstrates SHACL shape graphs can drive *generation*, not
  just validation — a template for how `ontology.ttl` + `gates/*.rq` could drive the
  `construct` stage.

**Refuted, don't rebuild on these (voted down 0-3 or 1-2)**:
- "MCP servers should default to read-only + OAuth-gate writes" — refuted as stated; the
  surviving, weaker claim is only "scope credentials separately," not a specific OAuth
  mechanism.
- "MCP tools should wrap workflows instead of raw API endpoints, 3x more accurate" — refuted,
  don't cite this specific number.
- "SEDCoT verifies via symbolic execution + delta debugging" — refuted; the real technique is
  closer to test-case minimization for repair guidance, a softer analogue for `verify_closure`
  than literal symbolic execution.
- "Characterization tests blacklist any deviation, directly analogous to observe/verify/replay"
  — refuted; the safer surviving claim is only that characterization tests model
  behavior-capture-as-baseline, not the full verification mechanics.

## Open gaps this proposal does not close

1. **Corrected 2026-08-21 (real, was wrong):** the original version of this gap assumed
   `verify_closure` needed a bridge between BLAKE3 hashing (the wasm4pm repo's own convention,
   not this repo's) and SLSA-style attestation. Checked `docs/src/07-verification.md` and a real
   receipt on disk (`evidence/foundry-provenance-verifier.json`) directly: **ggen-legacy already
   has its own native, git-commit-hash-based, schema-versioned receipt format**
   (`schema: "ggen.legacy.<domain>.verifier.v1"`; fields include `exact_head`, `runtime_head`,
   `workflow_run`, `standing`, and an explicit `nonclaims` array naming what is *not* claimed —
   `docs/src/07-verification.md:47`: "A receipt binds run, project, exact source, authority
   digest, toolchain, environment, inputs, outputs, actuator, exit status, verifier results,
   time, lineage, and standing"). This is already structurally close to SLSA's
   BuildDefinition/RunDetails split (source commit + builder/toolchain identity + outcome). The
   real remaining gap is narrower than originally stated: `verify_closure` should emit a receipt
   in **this existing `ggen.legacy.*.verifier.v1` family** (e.g.
   `ggen.legacy.mcp.verify-closure.v1`), reusing `exact_head`/`standing`/`nonclaims`, not
   BLAKE3 and not raw SLSA — no new format needs inventing, just a new schema instance in the
   family that already exists.
2. **No prior art found for a `workflow()`-composed strangler-fig traffic-replay loop**
   (incrementally re-routing and monitoring via workflow primitives specifically) — this would
   be a novel application if pursued, not a confirmed pattern. **Content-addressed build
   caching as a closer replay analogue than SLSA specifically (researched 2026-08-21):** Nix's
   and Bazel's remote-cache model (a deterministic input hash keys a cache entry; a cache hit
   means "this exact input set was already built, replay the stored output instead of
   rebuilding") maps onto the `replay` stage more directly than SLSA's attestation model does —
   SLSA answers "can I trust who built this," Nix/Bazel-style caching answers "have I already
   computed this exact result, so replay is a lookup, not re-execution." `replay(receipt_id, n)`
   could key on the same `exact_head`+authority-digest inputs this repo's real receipts already
   record, treating a matching prior receipt as a cache hit rather than re-running the full
   `construct`→`verify` chain each time. This wasn't validated against a real implementation in
   this pass — a design sketch, not a confirmed pattern, same evidentiary weight as the
   strangler-fig-replay item above.

## Checked against `GL-LSP-001` / `GL-PLAN-002` (real, 2026-08-21) — no conflict, but a more
## authoritative prior-art source was found and should supersede parts of this proposal

Read `authority/lsp-contract.json` (`GL-LSP-001`) and
`planning/v26.8.7/mfw-receiving-contract.json` (`GL-PLAN-002`) directly. Neither defines any
tool, schema, or method colliding with this proposal's 6-tool surface:

- `GL-LSP-001`'s contract is a concrete LSP (Language Server Protocol) reconstruction —
  real JSON-RPC methods (`initialize`, `textDocument/completion`, `textDocument/hover`, etc.),
  a real invariant set (`ZERO_UNRECEIPTED_ACTUATION`, `STDOUT_FRAME_PURITY`,
  `LEGACY_INDEPENDENT_RECEIVER`, `PROJECTION_FIXED_POINT`, ...), for `crates/ggen-lsp`
  specifically. Different domain entirely from a generic repo-reconstruction MCP surface.
- `GL-PLAN-002`'s contract (`schema: ggen.legacy.mfw-receiving-contract.v1`) receives planning
  problems FROM the separate `seanchatmangpt/mfw` repo and projects them through
  `planning/v26.8.7/lib.py::project_mfw_request` — a bounded PDDL-style search/planning
  substrate, not a repo-reconstruction pipeline. Its `planning_types` list includes `mcp_bound`
  as one *category of planning problem* (a plan whose actions are MCP tool calls), not an MCP
  *server* — no overlap with this proposal's tool surface.

**More important finding than "no conflict," found while checking this**: `~/ggen-legacy/
CLAUDE.md` already contains a real, specific "Gall's Law" prior-art table — grounded in named
papers, not the generic public-pattern research this proposal's `/deep-research` pass found:

| Stage | This proposal's source | `CLAUDE.md`'s more specific source |
|---|---|---|
| observe | Characterization tests (Feathers, generic) | GraphRepo, PyDriller/RepoDriller, RefactoringMiner (arXiv:2008.04884) — real MSR tooling |
| admit | (not specifically sourced) | AgentModernize's Behavioral Specification Graphs — DAG of rules/pre/postconditions (arXiv:2605.17535) |
| construct | Strangler-fig (generic Azure pattern) | Same, but with an explicit "façade routing → incremental shift → decommission" checkpoint order |
| verify | SLSA provenance (generic) | "Parity Gate" deterministic multi-axis trace comparison + arXiv:2607.28271, with an explicit, load-bearing caveat: the closest published full pipeline (AgentModernize) reaches only **8-19% behavioral-equivalence rate** on real benchmarks |
| receipt/replay | SLSA v1.0 + `slsa-verifier` (same conclusion, independently reached) | Same, plus Kettle for TEE-hardware-attested builds as an optional harder variant |

`CLAUDE.md` also names 5 ordered "Gall checkpoints" (archaeology → contract → manufacture →
verify → receipt), each needing its own `GL-*` ticket, each required to reach real
`PARTIAL_ALIVE`/`ALIVE` before the next starts — a stricter sequencing discipline than this
proposal's 6-tool MCP surface implies (this proposal's tools could be built in any order since
they're just a dispatch surface; `CLAUDE.md`'s checkpoints are a strict build order for the
underlying implementation those tools would eventually call).

**Recommendation for whoever continues this**: `CLAUDE.md`'s Gall's Law table is the
higher-authority source (it's this repo's own canonical doctrine, more specific, and dated more
recently than this proposal's research pass) — treat this proposal's MCP tool surface (Section
"`ggen-legacy-mcp`") as still plausible as an eventual dispatch layer, but implement the
underlying `observe`/`admit`/`construct`/`verify` logic those tools call against `CLAUDE.md`'s
named prior art (PyDriller, Behavioral Specification Graphs, Parity Gate) instead of the
generic patterns this proposal's own research found, and follow the 5 Gall checkpoints' build
order rather than building all 6 MCP tools in parallel. The 8-19% BER ceiling `CLAUDE.md` cites
should also be surfaced as a real, load-bearing caveat in any admission decision — this
proposal's research pass did not find that number and would have understated the real
difficulty without this cross-check.

## Prototype: `observe_contract`/`propose_admit`/`confirm_admit` (real, executed, 2026-08-21)

A real, working prototype of these 3 tools' logic exists at
`/private/tmp/claude-501/-Users-sac/ee8647b0-66c0-4dc2-87fd-c624c56fa508/scratchpad/
ggen-legacy-mcp-prototype/observe_admit.py` — deliberately kept **outside** this repo, since
`AGENTS.md`'s ticket-gated-admission rule means it has no standing to live here without a real
`GL-*` ticket. Real, executed self-test output (`python3 observe_admit.py
~/ggen-legacy/planning/v26.8.20`):

- `observe_contract`: real `git log` + real file walk + real SHA-256 digest of the observed
  target → `contract-68640745eb2976ae`.
- `propose_admit`: real, non-final JSON candidate file written, `status: "proposed"`.
- `confirm_admit` **without** `human_authorization`: correctly refused
  (`PermissionError: human_authorization must be a real, non-empty string, not inferred or
  defaulted`).
- `confirm_admit` **with** real authorization: correctly promotes to `status: "admitted"`.

This is the one concrete enforcement point proving the `propose_admit`/`confirm_admit` split
(and the broader `authorized != actuated` line) isn't just documented prose — the refusal path
was actually exercised and actually raised. `construct_replacement`/`verify_closure`/`replay`/
`retire_predecessor` were not prototyped this pass.

## Next step, not taken here

Formal admission (a real `GL-MCP-00X` ticket in `tickets/`, an entry in `AGENTS.md`'s active/
concurrent ticket list, a received contract authority file) is a decision for whoever continues
this work — this document is the candidate, not the admission.
