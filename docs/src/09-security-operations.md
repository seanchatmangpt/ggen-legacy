# Security, Privacy, Operations, and Resilience

## Security posture

Legacy repositories are untrusted input. Observation runs in isolated least-privilege workers with bounded filesystem access and controlled egress. Repository content cannot grant execution authority.

Observers are read-only. Projectors write only declared outputs. The broker holds narrow mutation capabilities. Verifiers cannot mutate production. Release and Sunset authorities are separate. Evidence is immutable and exportable.

Principal threats include command injection, path/symlink escape, secret exfiltration, authority poisoning, ambiguous ownership, stale-head verification, generated-output tampering, receipt forgery/reordering/duplication, direct broker bypass, self-certification, retention/residency violations, premature authorization, and destructive cleanup of unobserved behavior.

## Privacy and data governance

Engagement intake classifies source, secrets, personal and regulated data, residency, retention, deletion, legal hold, approved subprocessors, and export restrictions. Data crossing a trust boundary declares schema, provenance, integrity, confidentiality, purpose, retention, and verifier.

Risk acceptance identifies owner, scope, duration, compensating control, residual risk, review date, and receipt. Exceptions cannot silently become permanent defaults.

## Deployment

Preferred enterprise deployment is customer-controlled single tenancy with isolated workers, private networking, customer-managed keys, outbound deny, and customer-owned evidence storage. Managed coordination is possible only within the declared data boundary.

Profiles declare region, tenancy, residency, key owner, egress, worker image, source access, secrets, evidence destination, retention, SLO, RTO, RPO, and support.

## Operations

Job flow is:

```text
QUEUED → ORIENTING → OBSERVING → ADMITTING → PLANNING
→ MANUFACTURING → VERIFYING → REPLAYING
→ ADMISSION_DECISION → TERMINAL
```

Every transition emits an event and receipt or typed refusal.

P0 events include unauthorized actuation, evidence integrity compromise, cross-tenant exposure, and incorrect Sunset Admission. Containment takes precedence over completion. Disable broker grants, preserve evidence, rotate credentials, snapshot coordinates, and open an incident ledger.

## SLO target classes

SLOs are target classes, not current commitments. Candidate targets include control-plane availability, job terminal-state latency, evidence durability, receipt-verification latency, 4-hour control-plane RTO, and 15-minute admitted-evidence RPO. A contract must define workload, exclusions, maintenance, measurement, and remedy.

## Resilience and recovery

Gall checkpoints are recovery boundaries. Workers are disposable; authority and evidence are durable. Jobs resume from the last admitted receipt.

Testing covers worker loss, queue duplication, storage degradation, network partition, dependency outage, stale authority, partial generation, verifier timeout, and evidence-store failover.

Backup completion is not recovery proof. Restore, receipt verification, projection reconstruction, and replay must execute at the declared RTO/RPO profile.

## Support

Support may offer Standard, Enterprise, and Mission Critical tiers, but these remain commercial targets until a signed service agreement exists. Emergency work does not override receipt, replay, or verifier law.
