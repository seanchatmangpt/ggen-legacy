# ggen-legacy v26.8.1

**Verified Repository Reconstitution for Fortune 5-scale software estates.**

`ggen-legacy` reconstructs the observable contract of a legacy repository, admits that contract into machine-readable authority, manufactures a replacement repository, independently verifies behavioral closure, replays the result, and computes whether the predecessor may be retired.

> Reconstruct the contract. Manufacture the repository. Prove the standing.

## Project 001 standing

| Rail | State | Basis |
|---|---|---|
| Documentation and authority corpus | `PARTIAL_ALIVE` | Local verifier passes; exact-head GitHub Actions remains authoritative. |
| Verifier Appliance reference implementation | `PARTIAL_ALIVE` | Local real-boundary E2E passes; exact-head ggen manufacture is pending. |
| Complete product implementation | `UNKNOWN` | Archaeology, reconstitution, and external repository admission remain unimplemented. |
| External production standing | `UNKNOWN` | No real Fortune 5 deployment is claimed. |
| Compliance/certification | `REFUSED` | Controls and evidence mappings do not establish certification. |

Fortune 5-grade means the repository covers the complete enterprise decision surface—product, architecture, governance, security, privacy, resilience, operations, support, procurement, evidence, release, and retirement. It does not mean a Fortune 5 company has deployed the product.

## Verifier Appliance

The admitted Project 001 source phase now includes a ggen pack that manufactures a customer-controlled Repository Standing Portfolio toolchain:

```text
ggen manufactures
customer executes
independent verifier measures
customer or third party attests
customer owns the evidence and decision authority
```

The reference rail performs real RSA-PSS signing, customer-hidden runtime challenges, digest and SLSA/in-toto provenance binding, append-only transparency chaining, independent cross-check verification, deterministic replay, and separate Release/Sunset decisions.

```bash
bash appliance/bin/run-reference-e2e.sh
```

## Canonical authority

1. [`AGENTS.md`](AGENTS.md)
2. [`RELEASE_CONTROL.md`](RELEASE_CONTROL.md)
3. [`product/PRD.md`](product/PRD.md)
4. [`architecture/ARD.md`](architecture/ARD.md)
5. [`ontology/assurance-program.ttl`](ontology/assurance-program.ttl)
6. [`packs/ggen-legacy-assurance-pack/`](packs/ggen-legacy-assurance-pack/)
7. [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md)
8. [`governance/claims-register.md`](governance/claims-register.md)

## Verify

```bash
python3 scripts/verify_docs.py --strict
bash appliance/bin/run-reference-e2e.sh
mdbook build docs
```

The exact-head workflow additionally builds `seanchatmangpt/ggen@0f39227c102e0ac7519f0f27561356227a518653`, executes `ggen sync run` twice, proves committed projection identity, and uploads the verifier evidence.
