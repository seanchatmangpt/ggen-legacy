# Enterprise Operations, SLO, Support, and Recovery

## Job lifecycle

```text
QUEUED → ORIENTING → OBSERVING → ADMITTING → PLANNING
→ MANUFACTURING → VERIFYING → REPLAYING
→ ADMISSION_DECISION → TERMINAL
```

Every transition emits an OCEL event and receipt or typed refusal.

## Incident priorities

- **P0:** unauthorized production actuation, evidence integrity compromise, cross-tenant data exposure, or incorrect Sunset Admission.
- **P1:** release-blocking outage, loss of admitted evidence, or widespread verifier failure.
- **P2:** degraded throughput, isolated failed observer/projector, or delayed evidence export.
- **P3:** documentation, usability, or noncritical defect.

Containment takes precedence over completion. Disable broker grants, preserve evidence, rotate credentials, snapshot coordinates, and open an incident ledger. Never delete suspect evidence during response.

## SLO target classes

These are targets, not observed commitments.

| Service | Indicator | Target class | Evidence required |
|---|---|---|---|
| Control plane | accepted-job availability | 99.9% monthly target | production telemetry and error budget |
| Evidence store | admitted-evidence durability | 11-nines target class | provider and restore evidence |
| Orchestration | terminal state within declared window | workload-specific | queue and duration percentiles |
| Receipt verification | verification latency | workload-specific p95 | controlled benchmark |
| Recovery | control-plane RTO | 4-hour target | DR exercise receipt |
| Recovery | admitted-evidence RPO | 15-minute target | replication and restore receipt |

A service agreement must define workload, exclusions, maintenance, measurement, and remedy.

## Business continuity and DR

The recovery object is admitted authority plus evidence, not mutable worker state. Required controls include replicated immutable evidence, authority backups, key recovery, dependency inventories, cold-start worker images, restoration drills, region-failure exercises, and customer export.

A DR exercise passes only when the restored system verifies receipts, reconstructs projections, preserves standing, and replays. Backup completion without restore is `PARTIAL_ALIVE` at most.

## Support target tiers

- **Standard:** business-hours support; next-business-day target.
- **Enterprise:** 24×7 P0/P1 intake; target P0 30 minutes and P1 2 hours.
- **Mission Critical:** named technical account team and joint runbooks; contract-defined targets.

These are product targets, not current commercial commitments. Emergency changes remain receipted and replayable.
