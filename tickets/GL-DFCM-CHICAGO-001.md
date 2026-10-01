# GL-DFCM-CHICAGO-001 — Fortune-5 greenfield enterprise reconstruction

## Outcome

Exercise a complete, bounded Procure-to-Pay reconstruction from admitted observations through DfCM combinatorial option generation, PPDDL projection, planner selection, CONSTRUCT-only intent, exclusive BRCE DO, receipt binding, deterministic manufacture, and replay.

This is greenfield: no incumbent implementation is treated as the specification. The fixture names the complete bounded business surface under test: supplier onboarding, requisition, purchase order, approval, goods receipt, invoice, three-way match, payment, and audit trail.

## Exact external identities

- ggen-ecosystem: `f42aa25c4974a0d5a701ed0e08f3bce46d69d115`
- autofde-lab: `8ece5884c6e776093cd08beb80c5d1c9a8d05a3d`
- gymact: `dc8c8add4edd525e14815e44d03b84b347abfcc8`

These are provenance/admission anchors. The bounded court does not falsely claim those repositories executed inside the in-process test.

## DfCM surface

The court enumerates all `3 strategies × 5 failure injections = 15` combinations before selection. `big_bang`, `dual_run`, and `canary` are scored by reversibility, coverage, blast radius, and learning rate. Selection is deterministic and preserves the highest reversible option surface; the current admitted model selects `canary`.

Every strategy is crossed with supplier-master drift, approval partition, duplicate invoice, receipt loss, and payment timeout. Losing any required strategy, failure, capability, or unique owner is a refusal rather than partial success.

## Calculus

```text
O
→ O* exact admission
→ DfCM 15-option closure
→ deterministic strategy frontier
→ PPDDL problem projection
→ planner portfolio / meta-selection
→ CONSTRUCT_ONLY intent
→ BRCE DO
→ artifact
→ digest-bound receipt
→ replay
```

External planners are represented as explicit unavailable edges; the executable bounded planner is `deterministic-dfcm`. This prevents an unavailable dependency from being silently promoted to execution evidence.

## Authority

SELECT and CONSTRUCT never acquire DO. `brce_do` is the sole actuation boundary in this court and refuses unauthorized execution. The BRCE witness is in-process and sets `external_actuation=false`; it proves the authority/receipt topology, not production ERP or cloud actuation.

## Determinism

Two manufactures from the same exact admitted scenario and subject SHA must have identical artifact bytes, identical artifact SHA-256, identical receipt content, and a matched replay.

## Required negative controls

- `REFUSED[STALE_SHA]`
- `REFUSED[MUTABLE_IDENTITY]`
- `REFUSED[MALFORMED_ADMISSION]`
- `REFUSED[OWNERSHIP_COLLISION]`
- `REFUSED[UNAUTHORIZED_DO]`
- `REFUSED[UNBOUND_RECEIPT]`
- `REFUSED[RECEIPT_TAMPER]`
- `UNSUPPORTED[ECOSYSTEM_CONTAINER_AMD64]`

The fixture admits `linux/arm64`; `linux/amd64` is deliberately an explicit unsupported edge because the observed ecosystem container surface is arm64-only.

## Acceptance

```bash
python3 tools/v26.8.29/test_chicago_greenfield.py -v
python3 tools/v26.8.29/chicago_greenfield.py \
  --scenario fixtures/chicago-greenfield/fortune5-p2p.json \
  --subject-sha <exact-40-hex-git-sha>
```

GitHub Actions additionally checks out the exact PR head, executes the nine falsifier tests, executes the clean path twice, compares both summary and receipt bytes, verifies replay, verifies the typed amd64 edge, and preserves evidence as an artifact.

## Standing ceiling

`ALIVE` applies only to the exact in-process greenfield reconstruction court after observed execution. It does not imply external provider actuation, live ERP replacement, or execution of the pinned external repositories.
