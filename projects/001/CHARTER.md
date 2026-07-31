# Project 001 Charter — ggen-legacy Self-Reconstitution

## Objective

Create the complete non-production-source authority required to admit and govern the first implementation phase of ggen-legacy v26.8.1.

## In scope

AGENTS, release control, PRD, ARD, mdBook, decisions, machine-readable product/checkpoint authority, schemas, fixtures, documentation verifier, enterprise controls, threat model, operational model, procurement package, and source-admission backlog.

## Out of scope

Production archaeology, projection, actuation, equivalence, and external-verifier implementation; real customer data; real Fortune 5 representation; production deployment; certification; and actual Sunset Admission.

## Acceptance

```bash
python3 scripts/verify_docs.py --strict
```

The verifier must return `PARTIAL_ALIVE` and refuse inference of product `ALIVE` from documentary closure.
