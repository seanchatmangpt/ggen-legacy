# ggen-docs-reconstitution-pack

A doc-first ggen pack for reconstructing `ggen-legacy` without treating prose as runtime authority.

## What it manufactures

The pack turns one RDF graph into five synchronized surfaces:

1. one deterministic Markdown page per `gdoc:Document`;
2. an mdBook-compatible `SUMMARY.md`;
3. a `RECONSTITUTION_MAP.md` that binds documented capabilities to observables, verifiers, falsifiers, recovery, and standing ceilings;
4. a bounded `CLAIMS.md` register;
5. a machine-readable `EVIDENCE.ttl` projection inventory.

The seed graph mirrors the existing v26.8.1 documentation decomposition: governance, system, engine, graph, projection, evidence, products, verification, economics, and legacy equivalence. The ten reconstruction targets cover manifest parsing, RDF loading, SPARQL, Tera projection, write ownership, receipts/replay, CLI, LSP, packs/marketplace, and self-hosting.

## Authority model

`ontology.ttl` is this pack's authored semantic surface. Generated Markdown/Turtle are projections. The ggen receipt chain, when generation actually executes, is separate evidence of the actuation. A generated page cannot promote a runtime target beyond its observed execution evidence.

Public vocabularies carry generic semantics (`dcterms`, `prov`, `skos`, RDF/RDFS/XSD); the `gdoc` namespace is limited to documentation/reconstitution concepts that are specific to this pack.

## Fail-closed law

`gates/invalid-doc-model.rq` refuses generation when a document lacks identity/title/path/source/sections, when output paths collide or leave `consumer/docs/`, when a target lacks observable/verifier/falsifier/recovery/source metadata, or when documentation attempts to claim a standing above `GENERATED`.

`shapes.ttl` mirrors the portable structural contract for independent SHACL validators. The SPARQL gate remains the ggen-native admission boundary.

## Run

From this directory with an admitted ggen binary:

```bash
ggen sync run --dry-run
ggen sync run
```

Expected generated tree:

```text
consumer/docs/
├── 00-governance.md
├── 10-system.md
├── 20-engine.md
├── 30-graph.md
├── 40-projection.md
├── 50-evidence.md
├── 60-products.md
├── 70-verification.md
├── 80-economics.md
├── 90-legacy.md
├── CLAIMS.md
├── EVIDENCE.ttl
├── RECONSTITUTION_MAP.md
└── SUMMARY.md
```

A clean second sync should be byte-stable for the same ontology/templates/toolchain. Do not call the pack generation path `ALIVE` until that exact execution and receipt/replay path has been observed.

## Extension law

Add new document/section/claim/target individuals to `ontology.ttl`; do not fork templates for domain content. Add a new template only when introducing a genuinely different projection type. Preserve deterministic `ORDER BY`, bounded output paths, explicit standing ceilings, and typed falsifiers.
