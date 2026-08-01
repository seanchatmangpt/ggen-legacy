# ggen-legacy v26.8.1

**Verified Repository Reconstitution for Fortune 5-scale software estates.**

`ggen-legacy` reconstructs the observable contract of a legacy repository, admits that contract into machine-readable authority, manufactures a replacement repository, independently verifies behavioral closure, replays the result, and computes whether the predecessor may be retired.

> Reconstruct the contract. Manufacture the repository. Prove the standing.

## Project 001 standing

| Rail | State | Basis |
|---|---|---|
| Documentation and authority corpus | `ALIVE` | Exact-head workflow `30679448691`; mdBook 0.4.40 built; authority remained unchanged. |
| Verifier Appliance reference | `ALIVE` | Ten assurance subsystems independently re-derived; crown green; replay matched; reference Release Admission true. |
| Offline application transport | `ALIVE` | Two byte-identical bundles, sidecars, and receipts; extracted bundle verified itself offline. |
| Foundry runtime candidate | `ALIVE` | Exact candidate `458f0f88…` passed formatting, all targets including real-Git tests, and program validation. It is not the stable dependency. |
| Complete A–K foundry program | `PARTIAL_ALIVE` | Plan, receiving contract, schemas, and runtime candidate exist; A–K terminal predicates remain open. |
| Complete product implementation | `UNKNOWN` | Repository archaeology, replacement manufacture, equivalence, and real customer retirement are not yet complete. |
| External production standing | `UNKNOWN` | No real Fortune 5 deployment is claimed. |
| Compliance/certification | `REFUSED` | Controls and evidence mappings do not establish certification. |
| Real predecessor Sunset Admission | `UNKNOWN` | Reference Sunset Admission is correctly false; no predecessor retirement is claimed. |

The machine-readable promotion decision is [`authority/project-001-promotion.json`](authority/project-001-promotion.json).

Fortune 5-grade means the repository covers and operationalizes the complete enterprise decision surface—product, architecture, governance, security, privacy, resilience, operations, support, procurement, evidence, release, transport, and retirement. It does not mean a Fortune 5 company has deployed the product.

## Canonical authority

1. [`AGENTS.md`](AGENTS.md)
2. [`RELEASE_CONTROL.md`](RELEASE_CONTROL.md)
3. [`authority/project-001-promotion.json`](authority/project-001-promotion.json)
4. [`product/PRD.md`](product/PRD.md)
5. [`architecture/ARD.md`](architecture/ARD.md)
6. [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md)
7. [`governance/claims-register.md`](governance/claims-register.md)
8. [`governance/enterprise-maturity-model.md`](governance/enterprise-maturity-model.md)

## Verify

```bash
python3 scripts/verify_docs.py --strict
python3 scripts/verify_foundry_provenance.py
python3 scripts/verify_foundry_bootstrap.py
python3 scripts/verify_offline_transport.py
bash appliance/bin/run-reference-e2e.sh
mdbook build docs
```

The exact-head workflow additionally builds `ggen@0f39227c…`, performs two real `ggen sync run` executions, verifies byte-identical projections, tests the exact foundry runtime candidate, manufactures the offline bundle twice, and publishes immutable evidence.

Markdown and machine-readable authority are the source set. HTML, PDF, diagrams, generated coverage, verifier reports, and workflow artifacts are projections or evidence.
