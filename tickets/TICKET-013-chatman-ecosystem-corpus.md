# TICKET-013 — Chatman Ecosystem Architecture Corpus

## Identity

- **Repository:** `seanchatmangpt/ggen-legacy`
- **Exact base:** `cab1f69ded52bb3ece8b46ad6c38688b7cf198d6`
- **Target branch:** `agent/document-chatman-ecosystem-v1`
- **Expected transition:** `UNKNOWN → PARTIAL_ALIVE` for the authored ecosystem documentation rail

## Authority

- `AGENTS.md`
- `authority/ecosystem-reconstitution/2026-07-31.repositories.json`
- `authority/ecosystem-reconstitution/architecture.md`
- retained Enterprise Architecture as Strategy corpus
- retained Chatman ecosystem project history

## Problem

The repository contains an executable same-day repository cohort and an A–K foundry corpus, but it does not yet contain one canonical authority graph that distinguishes ecosystem capabilities, repository realizations, morphisms, authority boundaries, and standing.

Treating the 19-repository cohort as the entire ecosystem would erase known capabilities whose exact source objects have not yet been admitted. Treating repositories as capabilities would collapse architecture identity into implementation location.

## Bounded scope

Create authored, non-promoting surfaces under:

- `authority/chatman-ecosystem/`
- `ontology/chatman-ecosystem/`
- `docs/chatman-ecosystem/`
- `verifiers/`
- `witnesses/`
- `.github/workflows/`

Do not edit controller-owned `foundry/**`.

## Outputs

1. canonical ecosystem authority graph;
2. Draft 2020-12 JSON Schema;
3. RDF projection using public provenance and descriptive vocabularies;
4. SHACL admission shapes;
5. readable architecture atlas;
6. independent structural verifier;
7. mutation-based falsifier suite;
8. exact-head GitHub workflow;
9. README entrypoint.

## Positive witnesses

- exactly 26 initial capability records;
- exactly 19 Cohort 001 repository realizations;
- capability and repository identities remain distinct;
- every relationship names a contract and requires a receipt;
- only BRCE may declare actuation capability;
- no relationship declares direct actuation;
- transport-only `clnrm` has no product authority;
- the architecture document names every capability.

## Negative falsifiers

The verifier must refuse:

1. duplicate capability identity;
2. unknown repository realization;
3. non-BRCE actuation capability;
4. direct-actuation relationship;
5. transport promoted into product authority;
6. `ALIVE` claim without evidence;
7. undocumented capability;
8. self-certification relationship.

## Acceptance

```bash
python3 -m compileall -q verifiers witnesses
python3 -m json.tool authority/chatman-ecosystem/ecosystem.json >/dev/null
python3 verifiers/verify_chatman_ecosystem.py --output target/chatman-ecosystem-verifier.json
python3 witnesses/test_chatman_ecosystem.py
```

Exact-head CI additionally installs `jsonschema`, `rdflib`, and `pyshacl` and requires JSON Schema, RDF syntax, and SHACL conformance.

## Exclusions

- exact-source admission for capabilities outside Cohort 001;
- repository-owned validation execution;
- semantic equivalence across repositories;
- changes to source repositories;
- generated foundry projection updates;
- aggregate ecosystem `ALIVE`;
- Release Admission or Sunset Admission.

## Falsifier

Completion is false if a reader or machine cannot distinguish capability identity from repository identity, cannot determine where authority may cross a boundary, or can introduce a direct actuation or self-certification path without verifier refusal.
