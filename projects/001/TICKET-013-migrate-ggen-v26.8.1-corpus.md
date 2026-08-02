# TICKET-013 — Migrate ggen v26.8.1 corpus into ggen-legacy

## Identity

- Source repository: `seanchatmangpt/ggen`
- Exact source: `8351af4c5bbbf60bd99ab8417752a1762c6ea4e3`
- Destination repository: `seanchatmangpt/ggen-legacy`
- Exact destination base: `8d6428f40c0d30d5983fb0ecdd16cab1c1328a23`
- Owner: `ggen-legacy` corpus authority
- Expected transition: `UNKNOWN -> PARTIAL_ALIVE`

## Authority

`ggen` remains the generalized repository-manufacturing kernel. `ggen-legacy` owns the versioned architecture corpus, historical capability evidence, planning portfolio, equivalence witnesses, and corpus-specific verifier runtime.

## Bounded scope

- `docs/v26.8.1`
- `ontology/v26.8.1`
- `planning/v26.8.1`
- `tools/v26.8.1`
- `packs/legacy-equivalence-verifier-pack`
- source workflow evidence that directly references those surfaces

## Observable contract

The destination must preserve every admitted byte, relative path, executable bit represented by Git, BLAKE3 tree identity, planning result, SHACL result, and standalone verifier-runtime test. The source-removal PR must later prove that `ggen` plus this exact corpus reconstructs the pre-removal behavior.

## Exclusions

- generalized `ggen` engine, graph, projection, receipt, replay, CLI, LSP, and pack-resolution code;
- `tools/architecture-foundry` generic extraction/admission machinery;
- repository-level `ALIVE`, release admission, or sunset admission;
- deletion from `ggen` before the destination migration PR exists and the composed source-removal verifier passes.

## Positive witnesses

1. Exact source/destination BLAKE3 identity for every migrated component.
2. JSON Schema validation of the migration manifest.
3. Python compilation of migrated scripts.
4. `planning/v26.8.1/verify_planning.py` succeeds.
5. SHACL validation succeeds through `tools/v26.8.1/validate_shacl.py`.
6. The standalone Rust verifier workspace formats and tests successfully.
7. Replaying the migration verifier produces the same normalized report.

## Negative falsifiers

- missing source file;
- occupied destination path;
- source/destination byte drift;
- path escape;
- malformed or stale source coordinate;
- altered manifest digest;
- missing lineage, equivalence, verifier, or receipt evidence.

## Acceptance commands

```bash
python3 scripts/verify_ggen_v26_8_1_migration.py --source-root .source-ggen
python3 planning/v26.8.1/verify_planning.py
python3 tools/v26.8.1/validate_shacl.py --root .
cargo fmt --manifest-path tools/v26.8.1/Cargo.toml --all -- --check
cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets
```

## Evidence and replay

- Manifest: `migrations/ggen-v26.8.1/migration-manifest.json`
- Per-component lineage: `migrations/ggen-v26.8.1/lineage/*.json`
- Equivalence: `migrations/ggen-v26.8.1/equivalence-report.json`
- Verifier: `migrations/ggen-v26.8.1/verifier-report.json`
- Receipt: `migrations/ggen-v26.8.1/migration-receipt.json`

Completion is falsified if any migrated path differs from the exact source coordinate or if the post-migration source-removal composition cannot reproduce the declared verification behavior.
