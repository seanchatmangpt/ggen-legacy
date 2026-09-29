# v26.9.28 architecture — contract recovery over an external capability fabric

## Owner graph

| Plane | Canonical owner | ggen-legacy role |
|---|---|---|
| Manufacturing runtime | ggen | Execute the pinned deterministic manufacture semantics |
| Semantic manufacturing basis | ggen-marketplace | Select/compose admitted packs |
| Projection/provenance | ggen_igniter | Deterministic projection boundary |
| Read federation | ash_r2rml | Consume VKG evidence with authority NONE |
| Semantic law | GraphLaw | Admit/refuse semantic propositions |
| Consequence protocol | ash_a2a | Construct consequence envelopes |
| Consequential actuation | XaaS | Exclusive BRCE DO boundary |
| Cryptographic trust | Affidavit | Identity/integrity; never authorization |
| Planning authority | ash_pplan | Planner contracts and formal planning |
| Runtime/replanning | beam4pm + ferroplan | Process/recovery execution |
| Portable execution/evidence | wasm4pm + GymAct + AutoFDE | Bounded consumers/falsifiers |
| Process evidence | UNRDF + GitVan | OCEL and least-authority receipt transport |

## Architectural law

```text
SELECT ≠ CONSTRUCT ≠ DO
trust ≠ authorization
observation ≠ admission
generated ≠ authoritative
candidate ≠ released
release ≠ sunset
```

The only `CONSEQUENTIAL_DO` owner in the v26.9.28 lock is
`seanchatmangpt/xaas`. Every other component contributes construction,
evidence, trust, planning, or verification without acquiring that authority.

## Legacy universality boundary

ggen-legacy does not claim a universal semantic equivalence decider. A
repository is reconstitutable when its required observable contract can be
bounded, represented, admitted, manufactured, and independently falsified.
Rice-style unrestricted equivalence remains outside the admitted boundary.

The goal is not source preservation. The goal is preservation or intentional
replacement of the admitted observable contract.
