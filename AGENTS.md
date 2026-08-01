# AGENTS.md — Enterprise Architecture Foundry Constitution

This repository is an executable architecture corpus. Agents must manufacture evidence-bound
artifacts; they must not treat this repository as a dump of obsolete files.

## Authority order

1. this constitution;
2. `foundry/bootstrap.yaml`;
3. the exact committed `ggen` work program and Rust foundry controller;
4. admitted schemas, manifests, and ontology;
5. exact source and corpus heads;
6. executable positive witnesses and negative falsifiers;
7. BLAKE3 receipts and replay reports;
8. generated projections;
9. prose summaries.

A lower authority cannot promote or contradict a higher authority.

## Non-negotiable invariants

- `ZERO_UNRECEIPTED_ACTUATION`
- `NO_SELF_CERTIFICATION`
- `EXACT_HEAD_EVIDENCE`
- `GENERATED_PROJECTIONS_ARE_NOT_AUTHORITY`
- `NO_UNKNOWN_CAPABILITY_AT_FINAL_ADMISSION`
- `NO_UNKNOWN_DISPOSITION_AT_FINAL_ADMISSION`
- `NO_SOURCE_REMOVAL_BEFORE_DESTINATION_ADMISSION`
- `CLEAN_ROOM_REPLAY_REQUIRED`
- `AGENT_COMPLETION_DOES_NOT_PROMOTE_STANDING`

## Generated surfaces

The Rust `ggen-foundry` controller owns these surfaces after initialization:

- `foundry/foundry-manifest.json`
- `foundry/catalogs/*.json`
- `foundry/workstreams/state.json`
- `foundry/workstreams/*/admission-report.json`
- `foundry/lineage/**/*.json`
- `foundry/receipts/*.json`
- `foundry/standing.json`

Do not hand-edit them. Repair the admitted input, migration manifest, evidence report, or runtime,
then regenerate.

## Agent inputs

Agents may author bounded inputs under:

- `migration/` — extraction manifests conforming to the migration schema;
- `evidence/` — real reports produced by executed boundaries;
- `authority/` — admitted RDF, SHACL, SPARQL, schemas, and architecture decisions;
- `witnesses/` — executable positive witnesses and negative falsifiers;
- `verifiers/` — independent verifier implementations;
- `reference/` — Fortune-scale reference authority and manufactured outputs.

An input is not evidence merely because it is committed. Evidence must bind real execution,
state, process, causality, or externally verified content.

## Required execution sequence

1. Resolve exact `ggen` and `ggen-legacy` heads.
2. Refuse dirty worktrees before bounded manufacture.
3. Validate the `ggen` work program with the Rust controller.
4. Create or verify the exact-head baseline.
5. Execute one bounded migration or workstream operation.
6. Inspect every generated artifact and receipt.
7. Commit the bounded checkpoint.
8. Run independent verification and receipt replay against the committed heads.
9. Promote standing only through the controller.

## Migration law

Every extracted component must carry:

- stable component identifier;
- source exact head;
- corpus parent head;
- source path;
- destination path;
- content digest;
- capability identifiers;
- disposition other than `UNKNOWN`;
- replacement owner;
- evidence-supported rationale;
- lineage record;
- extraction receipt.

Extraction is copy-first and non-destructive. Deletion from `ggen` is a later operation that
requires destination admission, compatibility evidence, recovery evidence, equivalence closure,
and replay.

## Workstream law

The governing workstreams are A through K. An agent returning successfully does not admit its
workstream. Promotion requires:

- all dependencies admitted;
- exact source and corpus heads;
- every declared predicate equal to the work program;
- non-empty verifier identity;
- evidence files whose BLAKE3 digests verify;
- an immutable admission report;
- an admission receipt.

## Testing law

Use real Git repositories, filesystems, subprocesses, parsers, verifiers, and receipts. Do not use
mocks, fabricated hashes, synthetic success records, empty proof files, bypass flags, or
hardcoded `ALIVE` results.

A negative fixture must fail for its intended reason. A refusal caused by an unrelated missing
file does not prove the targeted safeguard.

## Standing law

Intermediate states may be `NOT_INITIALIZED`, `PARTIAL_ALIVE`, `BUILD_BROKEN`, or another typed
refusal. Final `ALIVE` requires:

- all A-K workstreams admitted;
- all final predicates satisfied;
- zero unknown capabilities, dispositions, and standings;
- zero unassigned verifiers;
- complete equivalence coverage;
- valid cross-repository receipts;
- Fortune-scale reference manufacture;
- clean-room replay match;
- independent final verifier identity.

Runner congestion, elapsed time, context size, task count, and successful agent completion are
not hard blocks.
