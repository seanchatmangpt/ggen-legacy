# Release Control — ggen-legacy v26.8.1

## Purpose

This document governs claims, candidate promotion, evidence ceilings, Release Admission, and Sunset Admission. Where explanatory documentation conflicts with this document, this document wins.

## Precedence

`AGENTS.md` → `RELEASE_CONTROL.md` → admitted machine-readable authority → PRD → ARD → schemas/verifier specifications → mdBook → generated reports.

The PRD owns product intent. The ARD mirrors and operationalizes it without widening it.

## Claim ceilings

| Ceiling | Meaning |
|---|---|
| `DOCUMENTED` | Requirement or design is stated. |
| `SCHEMA_VALIDATED` | Machine-readable authority conforms structurally. |
| `GENERATED` | A declared projector produced an artifact. |
| `COMPILED` | Implementation compiled at an exact coordinate. |
| `TESTED` | Declared witnesses executed. |
| `REFERENCE_CONFORMANT` | Independent verification established the bounded contract. |
| `PRODUCTION_PROVEN` | Longitudinal external evidence established production standing. |

A lower ceiling must not be phrased as a higher ceiling.

## Claim discipline

Allowed: control defined, evidence field defined, exception identified, evidence bundle assembled, assessment pending, independent audit required.

Forbidden without independent evidence: compliant, certified, passed SOC 2, SOC 2-ready, guaranteed secure, zero risk, production-proven.

## After Code Reading claim law

The historical observation that an external practitioner publicly described not reading agent-written implementation has ceiling `DOCUMENTED_EXTERNAL_OBSERVATION`. It does not prove this repository's doctrine, implementation, endorsement, market adoption, or production standing.

The phrases **After Manual Code**, **After Code Reading**, **Proof-Carrying Software Manufacturing**, and **Software Systems Manufacturer** are strategic and category authority at ceiling `DOCUMENTED` until their declared controls execute at an exact source identity.

A bounded claim that software was manufactured without manual source inspection may rise only through the following ladder:

| Ceiling | Required observation |
|---|---|
| `DOCUMENTED` | Human task removed and replacement controls are specified. |
| `SCHEMA_VALIDATED` | Machine-readable authority and gates validate. |
| `GENERATED` | Declared projectors manufacture the bounded product. |
| `COMPILED` | Manufactured implementation compiles at an exact coordinate. |
| `TESTED` | Positive witnesses and negative falsifiers execute. |
| `REFERENCE_CONFORMANT` | An independent verifier confirms requirements, architecture, planning, actuation separation, operational evidence, receipt, and clean replay without requiring manual implementation reading for acceptance. |
| `PRODUCTION_PROVEN` | Longitudinal external evidence shows the same bounded model operating in production. |

The unqualified phrase “manufactured without reading code” is forbidden unless evidence records:

- the exact product boundary;
- manual source lines read and written;
- human attention time;
- admitted requirements and architecture;
- planner and abstention behavior;
- actuation authority;
- producer-verifier separation;
- witnesses and falsifiers;
- operational evidence;
- standing;
- receipt validity;
- clean replay.

Tests alone do not satisfy the claim. A producer's own tests, reports, or confidence cannot promote the result. `ALIVE` remains impossible without exact-head independent verification and replay.

## Exact-head promotion

Promotion requires a verifier report whose subject equals the candidate commit and tree. Workflows are read-only, pin external actions, do not repair or push source, and publish immutable evidence.

The release ladder is:

```text
protocol/unit → property/fuzz → stdio+HTTP integration
→ black-box CLI E2E → security → chaos → stress
→ benchmark → replay → external verifier report
```

Stopping lower requires a bounded non-crown state.

## Bootstrap crown

```text
required_documents_missing=0
broken_book_links=0
invalid_authority_documents=0
invalid_schemas=0
forbidden_overclaims=0
undisclosed_unknowns=0
documentation_replay_differences=0
bootstrap_release_admitted=true
```

This crown does not prove product implementation.

## Release and sunset

Release Admission asks whether the replacement may release. Sunset Admission asks whether a real predecessor may retire. Project 001 must not fabricate retirement. Deletion, archival, or decommissioning is a separate irreversible, explicitly authorized, receipted actuation.
