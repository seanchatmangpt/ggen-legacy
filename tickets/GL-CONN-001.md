# GL-CONN-001 — Enterprise Architecture Manufacturing Connection

## Subject

Project the already-admitted Enterprise Architecture Foundry corpus into the
dependency-neutral `urn:ggen:enterprise-connection:v1` transport used by
`ggen-create`, `ggen-marketplace`, `ggen`, and GymAct.

## Authority

This ticket is CONSTRUCT-only. It may read the admitted foundry work program,
workstream state, admitted capability graph, committed admission reports, and
local receipts when present. It may emit a deterministic JSON envelope. It has
no Git, network, shell, cloud, deployment, retirement, or BRCE DO authority.

## Exact inputs

- `authority/foundry-work-program.json`
- `foundry/workstreams/state.json`
- `foundry/evidence/B/legacy-capabilities.ttl`
- `foundry/workstreams/<ID>/admission-report.json` for workstreams whose state
  is exactly `ADMITTED`, with bytes independently checked against the
  authoritative `report_digest`
- optional `foundry/receipts/...` corroboration when present locally

`foundry/receipts/` is intentionally ignored by repository law as generated
local evidence. Therefore a clean cross-repository checkout must not require
those files to exist. Missing committed admission reports or report-digest
drift are refusals.

Documentation prose, READY/BLOCKED workstreams, local ignored projections, and
a PR object cannot promote standing.

## Required behavior

1. Refuse an invalid producer revision, work-program/state schema drift,
   program identity mismatch, unsafe paths, missing/tampered committed
   admission report, report/workstream identity mismatch, or a false admission
   predicate.
2. Bind all admitted inputs by SHA-256 transport content identity.
3. Preserve the foundry capability set and invariants.
4. Emit `stage=RECONSTITUTE`, `parent=null`, and `do_authority=false`.
5. Preserve `PARTIAL_ALIVE` as a ceiling for the connection projection even if
   A-K later closes; external Fortune 5 production is never inferred here.
6. Emit compact sorted UTF-8 JSON deterministically.
7. Hand off only the immutable envelope to `ggen-create`; no sibling worktree
   is a runtime prerequisite of this exporter.

## Falsifiers

- two exports from the same bytes differ;
- an `ADMITTED` workstream lacks a committed admission report;
- committed admission-report bytes disagree with `report_digest`;
- an admission report contains a false predicate or wrong workstream id;
- ignored local receipt absence is incorrectly promoted to a repository
  evidence failure;
- `do_authority` becomes true;
- READY/BLOCKED workstreams are represented as admitted evidence;
- an unsafe relative path escapes the repository;
- complete product/cloud standing is inferred from this projection.

## Verification

```bash
python3 tests/test_enterprise_connection.py
python3 scripts/export_enterprise_connection.py \
  --root . \
  --revision "$(git rev-parse HEAD)" \
  --out /tmp/reconstitute.connection.json
```

The cross-repository Connection Crown additionally consumes this exact output
through ggen-create → marketplace → ggen → GymAct and verifies the parent
digest chain.

## Rollback

Delete this ticket, exporter, and test from the purpose branch. No source
system, cloud environment, default branch, or external actuator is changed.
