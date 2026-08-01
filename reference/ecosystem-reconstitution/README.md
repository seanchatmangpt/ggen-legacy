# Same-Day Ecosystem Reconstitution

This authored corpus teaches the Enterprise Architecture Foundry how to reconstruct the repositories changed on 2026-07-31 without flattening their Git histories or converting pull-request narration into source authority.

## Preserved boundary

The existing A-K foundry program remains authoritative. This checkpoint adds only authored inputs, independent verifiers, real-boundary witnesses, and a read-only exact-source workflow.

It does not edit:

- `foundry/foundry-manifest.json`;
- `foundry/catalogs/*.json`;
- `foundry/workstreams/state.json`;
- `foundry/workstreams/*/admission-report.json`;
- `foundry/lineage/**/*.json`;
- `foundry/receipts/*.json`;
- `foundry/standing.json`.

Those surfaces remain controller-owned consequences.

## Reconstruction calculus

```text
same-day GitHub observation
→ exact repository and source-object admission
→ merged/candidate/transport disposition
→ dependency-closed reconstruction order
→ exact Git fetch and tree observation
→ repository-owned validation obligation
→ BLAKE3 source receipt
→ clean-room replay
→ foundry admission
```

A merged consequence, an active candidate, and a closed-unmerged candidate are different objects. The manifest preserves all three. `clnrm` remains lineage-only because its same-day change explicitly exists as temporary verification transport and is not intended to merge.

## Corpus

`authority/ecosystem-reconstitution/2026-07-31.repositories.json` binds:

- 19 repositories;
- 18 product repositories;
- 1 transport-only repository;
- 26 exact source objects;
- each repository's dependencies, reconstruction strategy, and repository-native validation commands;
- `BRCE` as the only consequential broker;
- `direct_actuation=false`;
- `final_admission_allowed=false`;
- authored-source standing `UNKNOWN`.

The corpus uses the exact `ggen-legacy` execution base:

```text
be95d8a47e241458f5e6670d79d3932e4107b011
```

The PR head is bound externally by GitHub Actions to avoid circular self-hashing.

## Verification

Local structural and deterministic replay:

```bash
python3 -m compileall -q verifiers witnesses
python3 witnesses/test_ecosystem_reconstitution.py
python3 verifiers/verify_ecosystem_reconstitution.py verify \
  --manifest authority/ecosystem-reconstitution/2026-07-31.repositories.json \
  --output target/ecosystem-reconstitution \
  --digest-mode sha256-observation
```

The SHA-256 mode is explicitly non-promoting and exists only where a BLAKE3 provider is unavailable. The exact-head workflow installs `blake3==1.0.9`, issues BLAKE3 plan and contract receipts, then attempts to fetch every exact Git source. A source that cannot be fetched with the workflow's available authority emits `BLOCKED`; it is never inferred absent or admitted.

The witness suite executes six typed falsifiers:

- duplicate repository;
- malformed canonical SHA;
- repository dependency cycle;
- direct actuation;
- transport promoted into product authority;
- canonical source not present in the admitted source set.

## Standing ceiling

`PARTIAL_ALIVE` is available only for the bounded manifest → deterministic plan → BLAKE3 receipt transformation and for exact source objects successfully fetched and observed by the workflow.

The aggregate ecosystem remains `UNKNOWN` until every product repository has:

1. an exact source tree receipt;
2. its own doctrine read and preserved;
3. its declared validation ladder executed;
4. generated-output replay where applicable;
5. negative falsifier evidence;
6. a verified `ggen-receipt/v2`;
7. clean-room replay;
8. foundry admission.

No source branch is merged, retired, or actuated by this checkpoint.
