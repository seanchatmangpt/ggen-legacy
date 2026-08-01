# Procurement and Due Diligence

## Enterprise package

Procurement should receive:

- product category, scope, ownership, roadmap, and support model;
- architecture and data-flow diagrams;
- threat model and security architecture;
- SDLC, change control, exact-head CI, and verification ladder;
- SBOM, dependency, provenance, signature, vulnerability, and license policy;
- privacy, residency, retention, deletion, legal hold, and subprocessors;
- incident response, business continuity, DR, SLO, RTO, and RPO evidence;
- penetration-test and independent-assessment results when available;
- customer export and termination procedures;
- contract, insurance, financial, and continuity diligence.

## Current disclosure

Project 001 provides the product, architecture, governance, security, operations, procurement, schemas, fixtures, and verifier design. Production implementation, external audits, penetration tests, benchmark receipts, uptime history, customer references, and external Sunset Admission remain `UNKNOWN` unless separately supplied.

## Supply chain

Required target controls include immutable dependency coordinates and lockfiles, SBOM, source/build provenance, signature verification where policy requires it, vulnerability and malicious-package scanning, license policy, hermetic or bounded builds, isolated builders, secret-free build inputs, artifact quarantine, and exact-head rebuild/replay.

A passing scanner alone does not establish supply-chain standing.

## Licensing and IP

The repository contains an MIT license at initial commit `3c6480eb8a9d4c84474fd0f99ca21787cb424f2f`. Customer source, credentials, evidence, and generated customer artifacts remain governed by their originating rights and contract.

Every external pack exposes identity, version, source, digest, license, transitive dependencies, consumer capabilities, and substitution rules. No pack may conceal a dependency or license obligation.

## Compliance claim boundary

Allowed wording includes control defined, evidence assembled, exception identified, and assessment pending. The product does not claim certification or regulatory compliance without an independent authority and evidence.
