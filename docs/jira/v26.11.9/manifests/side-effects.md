# side-effects

Standing: PARTIAL

Ticket T-032. Every side effect has an owner and cutover behavior; items not
confirmed by grep are UNVERIFIED. Owners are proposed (D1/D2 open).

| side effect | evidence | owner | cutover behavior | standing |
|---|---|---|---|---|
- **S3 presign (B13 unported)**
  - evidence: env-inventory.md S3_*; template-topology.md s3
  - owner: new backend
  - cutover behavior: pause uploads; keep legacy presign until ported
  - standing: PARTIAL
- **email / notifications**
  - evidence: xaas lib/xaas/mailer.ex, Swoosh in config
  - owner: new backend
  - cutover behavior: dual-send forbidden; drain legacy queue, then switch
  - standing: PARTIAL
- **Oban poll jobs**
  - evidence: xaas health_controller, mix tasks (Oban refs)
  - owner: new backend
  - cutover behavior: pause, drain in-flight, re-enqueue
  - standing: PARTIAL
- **Reactor sagas (RFC-0042)**
  - evidence: srve/docs/plan/23 IngestAndMatchReactor
  - owner: new backend
  - cutover behavior: drain sagas before switch
  - standing: PARTIAL
- **Sentry**
  - evidence: srve servengine-frontend/src/main.tsx imports @sentry/react
  - owner: frontend
  - cutover behavior: keep DSN; backend side UNVERIFIED
  - standing: PARTIAL
- **DynamoDB sessions**
  - evidence: dynamos-and-sessions.md; 7 tables in template-topology.md
  - owner: auth bridge (T-020)
  - cutover behavior: expire on rollback
  - standing: PARTIAL
- **DynamoDB rate limits**
  - evidence: ops-runbook.md rateLimiter.ts
  - owner: new backend
  - cutover behavior: replace; TTL-only expiry
  - standing: PARTIAL
- **tenant_id drop risk**
  - evidence: migration-audit-extract.md: DROP COLUMN tenant_id
  - owner: operator
  - cutover behavior: UNVERIFIED on target DBs; do not apply
  - standing: UNVERIFIED
- **in-flight work orders**
  - evidence: no doc read
  - owner: new backend
  - cutover behavior: UNVERIFIED; drain before cutover
  - standing: UNVERIFIED

Grep notes: no Sentry or DynamoDB reference exists in xaas lib or config
(grep run, zero hits). Gate command run output: UNVERIFIED.

## See Also

auth-bridge-decision.md · scope-decisions.md · retirement-manifest.md
