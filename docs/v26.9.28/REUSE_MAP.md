# v26.9.28 reuse map

v26.9.28 is intentionally a composition release.

## Reused without reimplementation

- **ggen** — pinned v26.9.28 manufacturing runtime (`ff96f04e…`), kept distinct from marketplace content identity.

- **ggen-marketplace** — reusable semantic manufacturing basis and pack
  composition. The marketplace is prior art, not copied templates.
- **ggen_igniter** — provenance and deterministic projection.
- **ash_r2rml** — virtual knowledge graph/read-plane federation.
- **GraphLaw** — RDF/N3/Datalog/SPARQL/SHACL/ShEx/OWL-RL law boundary.
- **ash_a2a** — SA2A consequence protocol, CommandBus boundary, replanning
  envelopes, receipts.
- **XaaS** — runtime core, provider fabric, BRCE, receipts and replay.
- **Affidavit** — cryptographic trust plane.
- **ash_pplan / Beam4PM / Ferroplan** — HDDL/FOND/TLA+/process/replanning.
- **WASM4PM / GymAct / AutoFDE / DSPy-WASM** — portable execution,
  experiments, falsification and typed model interfaces.
- **UNRDF / GitVan** — OCEL 2 evidence and least-authority receipt transport.

## Candidate evidence preserved without promotion

The lock records the current AshA2A production-cutover checkpoint and Affidavit
PQC/trust-plane PR as `CANDIDATE`. They can be used as research evidence and
future composition inputs, but they do not widen the standing of the pinned
mainline owners.

## Why this matters

The manufacturing basis grows without requiring ggen-legacy to grow a second
implementation of every subsystem. Reconstitution therefore scales with
**recoverable contracts + reusable semantic prior**, not with the amount of
handwritten replacement code stored in this repository.

## Candidate adjacency preserved

- **ash_graphlaw** — current bridge repository from GraphLaw into the Ash ecosystem; recorded as `CANDIDATE` until its manufactured extension court establishes standing.
- **ggen-ecosystem** — current governed distribution/composition root is v26.9.29 and reports `BLOCKED[REQUIRES_REPUBLISH]`; recorded as `CANDIDATE` evidence rather than imported standing into v26.9.28.


## Landed during the v26.9.28 composition cut

- **GraphLaw PR #16** landed the authority-free SA2A exact-subject evidence matrix; the lock now pins main at `4e4873c…`.
- **AshA2A PRs #61–62** landed the C1 consequence runtime and portable RFC8785 PreparedEffect identity; the lock now pins main at `0f08b8c…`.
- Open strengthening PRs remain CANDIDATE only: marketplace #530, AshR2RML #49, ash_graphlaw #1, Affidavit #102, WASM4PM #648, GymAct #155, and GitVan #28.
