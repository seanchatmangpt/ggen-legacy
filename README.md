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

The strategic corpus itself is `ALIVE / REFERENCE_CONFORMANT` when the dedicated exact-head crown verifies all of the following at one revision:

```text
non-promoting manufacture
→ two clean mdBook replays
→ byte-identical replay reports
→ independent crown re-derivation
→ negative-control rejection
→ receipt binding
```

That promotion is bounded to the doctrine, architecture, authority, review standard, and documentation corpus. It does not promote the complete product implementation or any external no-read customer case.

Read the admitted doctrine:

- [`product/AFTER_CODE_READING.md`](product/AFTER_CODE_READING.md)
- [`architecture/AFTER_CODE_READING_ARCHITECTURE.md`](architecture/AFTER_CODE_READING_ARCHITECTURE.md)
- [`authority/after-code-reading.json`](authority/after-code-reading.json)
- [`authority/partial-standing-floor.json`](authority/partial-standing-floor.json)
- [`governance/after-code-reading-review-standard.md`](governance/after-code-reading-review-standard.md)

## Program standing floor

Every named product or assurance **program rail** is now required to be at least `PARTIAL_ALIVE`.

`PARTIAL_ALIVE` means a bounded observed subset exists with admitted authority, evidence, executable verification or replay, and explicit blockers. It does not convert an unobserved terminal result into success. External deployment, certification, a real customer no-read case, and real predecessor retirement remain unclaimable until independently observed.

| Rail | State | Basis |
|---|---|---|
| Documentation and authority corpus | `ALIVE` | Strict exact-head verifier, mdBook projection, source identity, and replay. |
| Verifier Appliance reference | `ALIVE` | Ten assurance subsystems independently re-derived; crown green; replay matched; reference Release Admission true. |
| Offline application transport | `ALIVE` | Two byte-identical bundles, sidecars, and receipts; extracted bundle verified itself offline. |
| Foundry runtime candidate | `ALIVE` | Exact candidate `458f0f88…` passed formatting, all targets including real-Git tests, and program validation. It is not the stable dependency. |
| After Code Reading strategic corpus | `ALIVE` | Dedicated exact-head manufacture, two clean documentary replays, independent crown, negative controls, and evidence receipt. |
| Complete A–K foundry program | `PARTIAL_ALIVE` | Plan, receiving contract, schemas, bootstrap authority, runtime candidate, and bounded verifier rails exist; terminal predicates remain open. |
| Complete product implementation program | `PARTIAL_ALIVE` | PRD/ARD, reference assurance, offline transport, runtime, projection, release logic, and replay machinery exist; complete archaeology, manufacture, equivalence, and real admissions remain open. |
| External no-read case program | `PARTIAL_ALIVE` | Admission theorem, benchmark, review standard, independent crown pattern, and replay protocol exist; no external customer case receipt exists. |
| External production program | `PARTIAL_ALIVE` | Deployment, security, resilience, operations, customer-controlled verification, transport, and release-evidence surfaces exist; no external deployment is claimed. |
| Production security program | `PARTIAL_ALIVE` | Threat model, least privilege, supply-chain controls, verifier separation, cryptographic transport, and refusal semantics exist; no security guarantee is claimed. |
| Performance and availability program | `PARTIAL_ALIVE` | SLO model, benchmark dimensions, deterministic replay checks, workflow execution, and runtime candidate evidence exist; production targets are not claimed met. |
| Compliance evidence and certification program | `PARTIAL_ALIVE` | Control mappings, evidence architecture, segregation of duties, immutable receipts, retention surfaces, and assessment boundary exist; certification remains subject to independent assessment. |
| Real predecessor Sunset Admission program | `PARTIAL_ALIVE` | Separate Release/Sunset decisions, reference fixture, disposition law, replay requirements, and retirement refusal exist; no real predecessor retirement is claimed. |

The Project 001 promotion decision is [`authority/project-001-promotion.json`](authority/project-001-promotion.json). The standing floor is [`authority/partial-standing-floor.json`](authority/partial-standing-floor.json). The bounded After Code Reading promotion law is [`authority/after-code-reading.json`](authority/after-code-reading.json).

Fortune 5-grade means the repository covers and operationalizes the complete enterprise decision surface—product, architecture, governance, security, privacy, resilience, operations, support, procurement, evidence, release, transport, and retirement. It does not mean a Fortune 5 company has deployed the product.

## Canonical authority

1. [`AGENTS.md`](AGENTS.md)
2. [`RELEASE_CONTROL.md`](RELEASE_CONTROL.md)
3. [`authority/project-001-promotion.json`](authority/project-001-promotion.json)
4. [`authority/after-code-reading.json`](authority/after-code-reading.json)
5. [`authority/partial-standing-floor.json`](authority/partial-standing-floor.json)
6. [`product/PRD.md`](product/PRD.md)
7. [`product/AFTER_CODE_READING.md`](product/AFTER_CODE_READING.md)
8. [`architecture/ARD.md`](architecture/ARD.md)
9. [`architecture/AFTER_CODE_READING_ARCHITECTURE.md`](architecture/AFTER_CODE_READING_ARCHITECTURE.md)
10. [`docs/src/SUMMARY.md`](docs/src/SUMMARY.md)
11. [`governance/claims-register.md`](governance/claims-register.md)
12. [`governance/enterprise-maturity-model.md`](governance/enterprise-maturity-model.md)

## Verify

```bash
python3 -m json.tool authority/after-code-reading.json >/dev/null
python3 -m json.tool authority/partial-standing-floor.json >/dev/null
python3 scripts/verify_docs.py --strict
python3 scripts/verify_foundry_provenance.py
python3 scripts/verify_foundry_bootstrap.py
python3 scripts/verify_offline_transport.py
bash appliance/bin/run-reference-e2e.sh
mdbook build docs
```

The dedicated After Code Reading crown additionally executes:

```bash
python3 scripts/manufacture_after_code_reading_evidence.py --help
python3 scripts/measure_after_code_reading_replay.py --help
python3 scripts/verify_after_code_reading_crown.py --help
python3 scripts/verify_partial_standing_floor.py --help
```

GitHub Actions binds the exact revision, creates two detached clean worktrees, builds the mdBook twice, compares replay evidence byte-for-byte, independently re-derives every material claim, executes sabotage controls, verifies the `PARTIAL_ALIVE` floor for every program rail, and publishes receipts.

The general exact-head assurance workflow additionally builds `ggen@0f39227c…`, performs two real `ggen sync run` executions, verifies byte-identical projections, tests the exact foundry runtime candidate, manufactures the offline bundle twice, and publishes immutable evidence.

Markdown and machine-readable authority are the source set. HTML, PDF, diagrams, generated coverage, verifier reports, and workflow artifacts are projections or evidence.
