# GL-ERRC-003 — Autonomous Fortune 5 self-reconstitution

## Exact admission

- repository: `seanchatmangpt/ggen-legacy`
- admitted base: `ef2502522a01ef413c588f9ee135139b097efb7b`
- authority: `authority/fortune5-reconstitution.json`
- claim ceiling: `FORTUNE5_SELF_RECONSTITUTION_ANALYSIS_ONLY`
- actuation authority: none outside the caller-supplied analysis output directory

## Purpose

Make ggen-legacy continuously reconstitute its own Fortune-5 product standing instead of relying on narrative memory or manually synchronized readiness lists.

The subsystem reconstructs one bounded object graph from current repository authority:

```text
14 PRD functional requirements
+ 13 claims
+ 21 enterprise maturity dimensions × P/N/R = 63 proof obligations
+ 11 foundry workstreams A–K
= 101 exact reconstitution objects
```

It then inventories independent repository evidence, preserves external qualification gates, computes an ERRC disposition/work queue, emits deterministic projections, receipts the source/output identities, and independently replays the whole result.

## Chesterton / sunk-cost law

Existing artifacts receive observation rights, not continuation authority. The subsystem may identify stale assertions or topology for ELIMINATE/REDUCE/RAISE/CREATE treatment, but it must not automatically delete, rewrite, promote, merge, deploy, certify, or retire anything.

## Authored boundary

```text
authority/fortune5-reconstitution.json
scripts/reconstitute_fortune5.py
scripts/verify_fortune5_reconstitution.py
tickets/GL-ERRC-003.md
.github/workflows/ci.yml
.github/workflows/planning-v26-8-7.yml   # eliminated into the single CI court
justfile
```

## Required behavior

1. Recover exactly 14 `PRD-FR-*` requirements from current PRD authority.
2. Recover exactly 13 `CLM-*` claims and preserve source standing separately from computed evidence.
3. Expand exactly 21 maturity dimensions into 63 conjunctive positive/negative/replay obligations.
4. Recover exactly 11 A–K foundry workstreams.
5. Refuse cardinality drift rather than silently dropping authority objects.
6. Exclude generated reconstitution outputs from their own evidence index.
7. Preserve CLM-005/006/007/008/013 as external gates that local execution cannot promote.
8. Detect workflow-topology drift against the admitted single-workflow architecture.
9. Detect known machine-readable/narrative standing drift without auto-promoting authority.
10. Emit `matrix.json`, `work-queue.json`, `report.md`, and `receipt.json` deterministically.
11. Bind source and output digests into a replay identity.
12. Independently execute the engine twice and require byte-identical output trees.
13. Kill cardinality-drift and rogue-workflow negative controls.
14. Emit construct-only ERRC work orders with `REFUSED:AMBIENT_ACTUATION`.
15. Never claim external production, compliance, security, performance, or Sunset standing.

## CI ERRC

The branch repairs a concrete reconstitution defect present on the admitted base: PR #25 introduced a second planning workflow after PR #26 had established a one-workflow CI topology, while `ci.yml` still refused any workflow count other than one.

ERRC treatment:

- **ELIMINATE** the standalone planning workflow file;
- **REDUCE** hosted workflow topology back to one exact-subject court;
- **RAISE** that court to execute LSP, planning, and Fortune-5 self-reconstitution boundaries;
- **CREATE** the autonomous reconstitution matrix, work queue, receipt, replay, and mutation court.

## Acceptance

```text
workflow_count=1
reconstitution_objects=101
external_claims_auto_promoted=0
ambient_work_orders=0
engine_replay=REPLAY_MATCH
cardinality_mutant=KILLED
workflow_mutant=KILLED
claim_ceiling=FORTUNE5_SELF_RECONSTITUTION_ANALYSIS_ONLY
standing=PARTIAL_ALIVE
```

`PARTIAL_ALIVE` is the maximum standing of this subsystem. It cannot promote the complete product or any external Fortune 5 claim.
