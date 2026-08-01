# ggen-legacy Enterprise Architecture Foundry

`ggen-legacy` is not a dead-code archive. It is the executable enterprise architecture corpus
used by `ggen` to reconstitute and manufacture new solution architectures.

## Repository role

```text
ggen
= Repository Manufacturing Kernel

ggen-legacy
= Executable Enterprise Architecture Foundry Corpus

manufactured repositories
= Admitted solution instances
```

This repository preserves provenance-bound historical implementations, admitted capability
records, generalized architecture primitives, bblocks, solution packs, reference witnesses,
migration evidence, negative controls, equivalence cases, verifier reports, lineage receipts,
and Fortune-scale reference architectures.

## Authority

The governing program is maintained in `seanchatmangpt/ggen`:

- `docs/architecture-foundry/work-program.yaml`
- `docs/architecture-foundry/AGENT_EXECUTION_CONTRACT.md`
- `docs/architecture-foundry/GGEN_LEGACY_MIGRATION_PLAN.md`
- `tools/architecture-foundry`

The Rust controller validates the A-K workstream graph, binds both repository heads, initializes
this corpus, executes receipt-bound extraction, verifies lineage, admits workstreams, replays
receipts, and computes standing.

## Bootstrap

The machine-readable bootstrap contract is `foundry/bootstrap.yaml`. The first lawful operation
is an exact-head baseline followed by corpus initialization from clean clones of both
repositories.

No historical component is copied here without:

- source repository and exact source head;
- source and destination paths;
- BLAKE3 content digest;
- capability identifiers;
- closed disposition;
- replacement owner;
- rationale and recovery path;
- lineage record;
- extraction receipt.

No source implementation is removed from `ggen` until its destination is admitted and its
migration, recovery, equivalence, and replay evidence pass.

## Standing

This repository begins as `NOT_INITIALIZED`. A committed file, successful agent, or completed
copy operation does not promote standing. `ALIVE` requires all A-K workstreams, final predicates,
independent verification, exact-head receipts, and clean-room replay.
