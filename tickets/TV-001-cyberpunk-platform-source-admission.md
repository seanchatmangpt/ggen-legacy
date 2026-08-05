# TV-001 — Cyberpunk Television Platform Source Admission

## Identity

| Field | Value |
|---|---|
| Ticket | `TV-001` |
| Category | deterministic source admission |
| Owner | `packs/cyberpunk-tv-platform-replay` |
| Receiving repository/base | `seanchatmangpt/ggen@70e599a599fedb7c62c965377cc2f80df1fa01ec` |
| Source repository/base | `seanchatmangpt/ggen@8351af4c5bbbf60bd99ab8417752a1762c6ea4e3` |
| Admitted source head | `1d384907883e6458372a2da8f3de63ca60890633` |
| Source branch/path | `agent/cyberpunk-tv-platform-v1` / `packs/cyberpunk-tv-platform` |

## Authority

1. `AGENTS.md`
2. `RELEASE_CONTROL.md`
3. `packs/cyberpunk-tv-platform-replay/receiving-contract.json`
4. `packs/cyberpunk-tv-platform-replay/capability-ledger.json`
5. `packs/cyberpunk-tv-platform-replay/verifier-spec.json`
6. source ontology, SHACL shapes, rules, queries, templates, fixtures, manifest, and exact-head workflow

## G1 fence

The platform is not the generated Vite application, compiled WASM, screenshots, or documentation. Preserve:

```text
public ontology / canon / rights / procedure
→ SPARQL + N3 + Datalog closure
→ ggen manufacture
→ generated nightly Rust/WASM body
→ UNRDF/Oxigraph semantic substrate
→ Mermaid/mmdio structural projection
→ deck.gl spatial-temporal projection
→ bounded television interaction
→ BLAKE3 receipt
→ replay
```

## Admitted source scope

This ticket admits only the read-only receiver, verifier, capability ledger, workflow, evidence, and replay capsule under:

```text
packs/cyberpunk-tv-platform-replay/
tickets/TV-001-cyberpunk-platform-source-admission.md
.github/workflows/cyberpunk-tv-replay.yml
evidence/cyberpunk-tv/
```

It does not authorize a second hand-written platform implementation in `ggen-legacy`.

## Observable contract

The receiver must preserve and independently verify:

- public RDF/OWL/DCAT/PROV/SKOS/ODRL authority and SHACL admission;
- explicit ordered SPARQL SELECT/CONSTRUCT projections;
- N3 and Datalog settlement closure without direct actuation;
- double ggen manufacture with no generated drift;
- generated nightly Rust/WASM identity, capability, drift, and receipt primitives;
- UNRDF/Oxigraph semantic query execution;
- Mermaid/mmdio and deck.gl projections from the same semantic subject;
- cinema, matrix, construct, governance, market, and receipt television modes;
- RDF-derived remote and accessibility profiles;
- user-authorized media binding and synchronized watch-party intents;
- Robert's Rules governance and two-party BLAKE3-anchored SPARQL escrow;
- ODRL rights projection;
- broker-routed intent plus consequence/refusal receipts;
- exact-tree BLAKE3 manufacture receipt;
- deterministic replay;
- real Chromium execution evidence.

## Positive witnesses

```text
exact source head
required_paths missing=0
capability count=22 and unknown_dispositions=0
strict SHACL admission
all queries explicit and ordered
ggen sync exit=0 twice
NO_GENERATED_DRIFT
Rust tests exit=0
WASM build exit=0
browser build exit=0
Chromium execution with console_errors=0
semantic node correspondence
six TV modes observed
valid escrow=adopted-awaiting-brce
invalid escrow!=adopted
receipt algorithm=blake3-256
REPLAY_MATCH
```

## Negative falsifiers

Any one falsifies completion:

- source identity differs;
- required authority or morphism is absent;
- generated output is promoted to authority;
- any capability lacks exactly one disposition;
- a query has implicit projection or nondeterministic result order;
- repeat manufacture differs;
- Rust/WASM is named but not built and loaded;
- browser evidence omits UNRDF, Mermaid, deck.gl, remote, governance, escrow, or receipts;
- a declared material interaction bypasses the broker receipt path;
- same proposal commitment or absent quorum reaches adoption;
- invalid fixture reaches adoption;
- receipt is not BLAKE3-256;
- replay differs;
- the executing source assigns repository standing to itself.

## Verification ladder

```bash
python3 packs/cyberpunk-tv-platform-replay/verify_source.py \
  --source /exact/ggen/packs/cyberpunk-tv-platform \
  --contract packs/cyberpunk-tv-platform-replay/receiving-contract.json \
  --ledger packs/cyberpunk-tv-platform-replay/capability-ledger.json \
  --output evidence/cyberpunk-tv/source-verification.json

cargo build -p ggen-cli-lib --bin ggen
cd packs/cyberpunk-tv-platform
/path/to/ggen sync
/path/to/ggen sync
cd generated
npm install --no-audit --no-fund
npx playwright install --with-deps chromium
npm run check
```

## Receipt and replay

The final independent receipt binds receiving base, source base/head/tree, authority and capability-ledger digests, toolchain identities, commands and exits, manufactured-tree root, runtime receipt root, browser evidence, replay result, verifier identity, and aggregate standing.

Replay starts from clean exact checkouts and requires:

```text
NO_SEMANTIC_CHANGE
NO_GENERATED_DRIFT
REPLAY_MATCH
```

## Exclusions

Copyrighted media distribution, production identity/payment/legal settlement, app-store submission, deployed global relay infrastructure, production availability/stress/chaos/benchmark claims, release admission, and predecessor retirement are excluded.

## State transition

```text
UNKNOWN
→ PARTIAL_ALIVE when the exact browser/TV slice passes identity, manufacture, execution, receipt, and replay
→ ALIVE only after the independent crown passes with zero unknown capabilities, dispositions, or required standings
```

Release Admission and Sunset Admission remain false unless separately computed.
