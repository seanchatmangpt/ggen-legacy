# Chatman Capability Graph

Repositories are implementation locations. They are not themselves the ontology of capabilities.

Orient work around the capability graph below.

| Capability | Typical implementation surfaces |
|---|---|
| admitted configuration and observation carriers | `star-toml`, `O*.toml` |
| semantic admission and closure | Graphlaw, RDF, SPARQL, SHACL, quarantined N3 |
| deterministic manufacturing | `ggen` |
| planning and workflow semantics | PDDL, POWL v2, MFW, planner adapters |
| formal admission and certification | Lean, Lake, `mfact`, theorem receipts |
| process execution evidence | `wasm4pm`, AIR, Erlang transition core, OTP, AtomVM |
| exclusive actuation and consequences | BRCE broker |
| release governance | `cargo-cicd` |
| protocol completeness and machine tooling | `lsp-max`, LSP 3.18, LSIF 0.6.0 |
| runtime semantic memory | Tree-sitter, Salsa, Oxigraph |
| intent manufacture | Knowledge Hooks |
| dependency and compatibility closure | BCINR and repository-specific compatibility layers |

## Canonical correspondence

Preserve this correspondence across repositories and artifacts:

```text
canonical graph
→ query
→ ggen
→ generated projection
→ formal admission
→ runtime
→ BRCE
→ receipt
→ replay
→ release
```

The intended division is:

```text
ggen renders
Lean admits
mfact certifies
BRCE actuates
receipts establish standing
```

No layer may silently inherit the authority of another.

## Canonical graph

The graph is the authoritative semantic object when repository doctrine declares it canonical. It represents admitted entities, relationships, constraints, provenance, policy, and execution-relevant meaning.

The graph must remain distinguishable from:

- source observations;
- generated filesystem projections;
- runtime memory;
- proof artifacts;
- receipts;
- explanatory prose.

## Query

Queries select bounded views from the admitted graph. A query result is a construction input, not actuation authority. Query identity, graph identity, parameters, and result digest should be receipted where they influence manufacture.

## ggen

`ggen` deterministically renders admitted graph views into projections. Generated artifacts are projections, not canonical editing surfaces, unless repository doctrine explicitly declares otherwise.

A lawful generation receipt binds:

- graph identity;
- query identity;
- template identity;
- ggen version or exact source coordinate;
- configuration;
- output tree and digests;
- deterministic replay result.

## Formal admission

Lean admits propositions inside its formal boundary. `mfact` may certify admitted theorem and artifact relationships. Neither proof nor certification grants ambient runtime actuation.

Proof standing and runtime standing must remain separate:

```text
theorem admitted ≠ runtime executed
runtime executed ≠ theorem admitted
```

Both may be required for a higher closure condition.

## Runtime and process evidence

Runtime surfaces execute the admitted behavior under bounded capabilities. `wasm4pm`, AIR, Erlang transition cores, OTP, or AtomVM may provide process evidence and deterministic transition semantics.

Runtime evidence should bind:

- exact executable identity;
- input and state identity;
- transition sequence;
- outputs and side effects;
- timing where relevant;
- refusal and failure paths;
- replay equivalence.

## BRCE and consequence

BRCE is the exclusive DO path. Every attempted external or durable consequence must be admitted and receipted. Downstream systems may propose intents; they may not bypass the broker.

## Release

Release governance consumes exact artifacts and evidence. A successful build or verifier does not itself authorize release. Release Admission is a distinct authority decision with its own receipt.

## Public ontology preference

Prefer public ontology terms and canonical graphs over private English-language conventions when the terms are semantically and operationally bound:

- PROV-O;
- DCAT;
- DCTERMS;
- SKOS;
- SHACL;
- ODRL;
- FOAF;
- OCEL;
- FIBO;
- QUDT;
- SOSA.

Do not add vocabularies decoratively. Every imported term must participate in at least one of:

- admission;
- policy or authority evaluation;
- execution planning;
- evidence capture;
- provenance;
- projection;
- verification;
- receipt interpretation.

An ontology term that changes no admissible behavior, evidence, or query is documentation, not operational semantics.

## Cross-repository identity

Cross-repository work must preserve source and destination identities independently. A lawful transfer or manufacture binds:

```text
source repository, commit, tree, and path
→ source object digest and authority
→ transformation or projection identity
→ destination repository, base, path, and tree
→ destination digest
→ verification and replay
→ standing and nonclaims
```

A repository can host a projection without owning the canonical capability. A receiving repository can validate a contract without certifying the producing kernel.
