# scope-decisions

Standing: PARTIAL

Ticket T-014. Dispositions per area; D1-D4 stay OPEN pending operator choice.
Cutover refuses to route any table or route with no owner (falsifier).

## Open decisions (recorded, not decided)

| id | question | options | recommendation |
|---|---|---|---|
- **D1**
  - question: runtime for new backend
  - options: (a) Ash generated via ggen; (b) hand-written Ash; (c) NestJS port
  - recommendation: (a): matches ontology-first law
- **D2**
  - question: where the runtime lives
  - options: (a) new repo; (b) srve/packs/srve-backend-pack; (c) inside xaas
  - recommendation: (a) or (b); avoid coupling to xaas non-core
- **D3**
  - question: auth bridge
  - options: (a) session-id shim; (b) move clients to tokens
  - recommendation: (b) long-term, (a) only for rollback window (see T-020)
- **D4**
  - question: procurement scope
  - options: (a) in-scope now; (b) port behind ports; (c) out-of-scope UNSUPPORTED
  - recommendation: (b) behind ports; ontology/procurement.ttl classes first

## Per-area disposition (provisional until D4)

Sources: srve/docs/plan/16-legacy-parity-spec.md, 17-cutover-mustwork.md,
docs/audit/xaas/00-recon-synthesis.md. Sizes from the T-014 ticket (legacy
procurement ~40k lines, ~160 routes, 17.6k-line service.ts).

| area | disposition | owner | notes |
|---|---|---|---|
- **procurement (flight/part/email/quotation)**
  - disposition: PORT BEHIND PORTS (pending D4)
  - owner: new backend
  - notes: xaas lib/xaas/procurement is 12K; not parity
- **dispatcher / sweep / ranking tables**
  - disposition: IN-SCOPE
  - owner: new backend
  - notes: xaas matcher absent (recon); Reactor RFC-0042
| form builder | UNSUPPORTED (explicit row) | none | no xaas or ontology class found; UNVERIFIED |
| W9 requests | UNSUPPORTED (explicit row) | none | legacy prefix /w9-requests; UNVERIFIED |
| availability bands | IN-SCOPE | new backend | thresholds in plan 16 |

Integration helpers (flight, part, email, quotation) are isolated behind ports
for any in-scope area; port interfaces are UNVERIFIED (not yet written).

## Gate

`grep -c procurement ontology/procurement.ttl` run: UNVERIFIED (not run here).

## See Also

auth-bridge-decision.md · side-effects.md · retirement-manifest.md · ../INDEX.md
