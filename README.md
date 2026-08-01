# ggen-legacy v26.8.1

**Verified Repository Reconstitution for the era after human code reading leaves the production critical path.**

`ggen-legacy` reconstructs the observable contract of a legacy repository, admits that contract into machine-readable authority, manufactures a replacement repository, independently verifies behavioral closure, replays the result, and computes whether the predecessor may be retired.

> Reconstruct the contract. Manufacture the repository. Prove the standing.

## After Code Reading

Machine implementation throughput can exceed human source-inspection throughput. An organization that uses agents to generate implementation but still requires people to read every line has accelerated one workstation while preserving the human inspection bottleneck that limits the factory.

`ggen-legacy` contributes **Verified Repository Reconstitution** to a larger category stack:

- **After Manual Code** — the transition from manual construction to machine-scale manufacture;
- **After Code Reading** — the boundary where mandatory human source inspection leaves the critical path;
- **Proof-Carrying Software Manufacturing** — the method of admitted requirements, planning, bounded authority, independent falsification, evidence, standing, receipts, and replay;
- **Software Systems Manufacturer** — the accountable profession governing mission, architecture, risk, acceptance, and irreversible decisions.

Code is intermediate manufacturing material. The product is a verified business capability or conforming operational system.

The hard invariant is:

```text
no-read claim
→ named replacement control
→ independent verifier
→ operational evidence
→ explicit standing
→ receipt
→ clean replay
```

A no-read claim is falsified when a human must inspect implementation to determine acceptance because the requirement, architecture, behavior, or evidence model is insufficient.

Read the admitted doctrine:

- [`product/AFTER_CODE_READING.md`](product/AFTER_CODE_READING.md)
- [`architecture/AFTER_CODE_READING_ARCHITECTURE.md`](architecture/AFTER_CODE_READING_ARCHITECTURE.md)
- [`authority/after-code-reading.json`](authority/after-code-reading.json)
- [`governance/after-code-reading-review-standard.md`](governance/after-code-reading-review-standard.md)

## Project 001 standing

| Rail | State | Basis |
|---|---|---|
| Documentation and authority corpus | `ALIVE` | Exact-head workflow `30679448691`; mdBook 0.4.40 built; authority remained unchanged. |
| Verifier Appliance reference | `ALIVE` | Ten assurance subsystems independently re-derived; crown green; replay matched; reference Release Admission true. |
| Offline application transport | `ALIVE` | Two byte-identical bundles, sidecars, and receipts; extracted bundle verified itself offline. |
| Foundry runtime candidate | `ALIVE` | Exact candidate `458f0f88…` passed formatting, all targets including real-Git tests, and program validation. It is not the stable dependency. |
| Complete A–K foundry program | `PARTIAL_ALIVE` | Plan, receiving contract, schemas, and runtime candidate exist; A–K terminal predicates remain open. |
| After Code Reading strategic corpus | `PARTIAL_ALIVE` | Doctrine, target architecture, review standard, and machine-readable authority are present; exact-head verification and replay remain required. |
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
4. [`authority/after-code-reading.json`](authority/after-code-reading.json)
5. [`product/PRD.md`](product/PRD.md)
6. [`product/AFTER_CODE_READING.md`](product/AFTER_CODE_READING.md)
7. [`architecture/ARD.md`](architecture/ARD.md)
8. [`architecture/AFTER_CODE_READING_ARCHITECTURE.md`](architecture/AFTER_CODE_READING_ARCHITECTURE.md)
9. [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md)
10. [`governance/claims-register.md`](governance/claims-register.md)
11. [`governance/enterprise-maturity-model.md`](governance/enterprise-maturity-model.md)

## Verify

```bash
python3 -m json.tool authority/after-code-reading.json >/dev/null
python3 scripts/verify_docs.py --strict
python3 scripts/verify_foundry_provenance.py
python3 scripts/verify_foundry_bootstrap.py
python3 scripts/verify_offline_transport.py
bash appliance/bin/run-reference-e2e.sh
mdbook build docs
```

The exact-head workflow additionally builds `ggen@0f39227c…`, performs two real `ggen sync run` executions, verifies byte-identical projections, tests the exact foundry runtime candidate, manufactures the offline bundle twice, and publishes immutable evidence.

Markdown and machine-readable authority are the source set. HTML, PDF, diagrams, generated coverage, verifier reports, and workflow artifacts are projections or evidence.
