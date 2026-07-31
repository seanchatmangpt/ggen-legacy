# ggen-legacy v26.8.1

**Verified Repository Reconstitution for Fortune 5-scale software estates.**

`ggen-legacy` reconstructs the observable contract of a legacy repository, admits that contract into machine-readable authority, manufactures a replacement repository, independently verifies behavioral closure, replays the result, and computes whether the predecessor may be retired.

> Reconstruct the contract. Manufacture the repository. Prove the standing.

## Project 001 standing

| Rail | State | Basis |
|---|---|---|
| Documentation and authority corpus | `PARTIAL_ALIVE` | Local verifier passes; exact-head GitHub Actions receipt remains pending. |
| Product implementation | `UNKNOWN` | Project 001 intentionally begins without production source. |
| External production standing | `UNKNOWN` | No real Fortune 5 deployment is claimed. |
| Compliance/certification | `REFUSED` | Controls and evidence mappings do not establish certification. |

Fortune 5-grade means the documentation covers the complete enterprise decision surface—product, architecture, governance, security, privacy, resilience, operations, support, procurement, evidence, release, and retirement. It does not mean production execution has already occurred.

## Canonical authority

1. [`AGENTS.md`](AGENTS.md)
2. [`RELEASE_CONTROL.md`](RELEASE_CONTROL.md)
3. [`product/PRD.md`](product/PRD.md)
4. [`architecture/ARD.md`](architecture/ARD.md)
5. [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md)
6. [`governance/claims-register.md`](governance/claims-register.md)
7. [`governance/enterprise-maturity-model.md`](governance/enterprise-maturity-model.md)

## Verify

```bash
python3 scripts/verify_docs.py --strict
mdbook build docs
```

Markdown and machine-readable authority are the source set. HTML, PDF, diagrams, and workflow reports are projections or evidence.
