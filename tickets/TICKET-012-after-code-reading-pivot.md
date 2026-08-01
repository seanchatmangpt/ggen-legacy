# TICKET-012 — Admit the After Code Reading strategic pivot

## Identity

- **Release:** `v26.8.1`
- **Exact base:** `8d6428f40c0d30d5983fb0ecdd16cab1c1328a23`
- **Type:** documentation, authority, product, architecture, and governance admission
- **Expected transition:** bounded strategic corpus from `UNKNOWN` to `PARTIAL_ALIVE`
- **Owner:** Sean Chatman

## Authority

1. `AGENTS.md`
2. `RELEASE_CONTROL.md`
3. this ticket
4. admitted authority under `authority/`
5. `product/PRD.md`
6. `architecture/ARD.md`

## External observation

On 2026-07-23, Robert C. Martin publicly stated that his current strategy is not to read agent-written implementation because mandatory reading would prevent him from obtaining the productivity benefit. He described replacing implementation reading with an extensive constraint and test gauntlet.

- Primary public coordinate: `https://x.com/unclebobmartin/status/2080257779395154409`
- Corroborating discussion: `https://raphamoura.dev/en/blog/o-direito-de-nao-ler-o-codigo/`
- Related research: `https://arxiv.org/abs/2606.13175`

The external statement is an observed historical event. It does not prove this repository's thesis, implementation, market adoption, or production standing.

## Problem

The current corpus defines Verified Repository Reconstitution but does not yet name the broader engineering boundary exposed when machine implementation throughput exceeds human source-inspection throughput.

Without a governing doctrine:

- no-read language may be mistaken for absent accountability;
- tests may be treated as the complete replacement for source inspection;
- architecture, authority, planning, actuation, process evidence, standing, receipts, and replay may remain disconnected;
- repositories and public explanations may describe adjacent tools rather than one industrial program;
- benchmark claims may optimize code volume instead of verified consequences per human inspection unit.

## Bounded scope

Admit a strategic authority corpus defining:

- **After Manual Code** as the broad transition;
- **After Code Reading** as the engineering boundary;
- **Proof-Carrying Software Manufacturing** as the method;
- **Software Systems Manufacturer** as the accountable profession;
- Verified Repository Reconstitution as the ggen-legacy product contribution;
- the control loop replacing manual source inspection;
- the human responsibilities retained;
- project-to-lane mappings;
- claim ceilings, benchmarks, PR questions, and falsifiers.

## Inputs

- current `ggen-legacy` authority, PRD, ARD, claims register, and mdBook;
- the 2026-07-23 public statement at the exact X coordinate above;
- the existing repository doctrines for admission, manufacture, independent verification, receipts, replay, Release Admission, and Sunset Admission.

## Outputs

- `authority/after-code-reading.json`
- `product/AFTER_CODE_READING.md`
- `architecture/AFTER_CODE_READING_ARCHITECTURE.md`
- `governance/after-code-reading-review-standard.md`
- `docs/src/15-after-code-reading.md`
- updates to `README.md`, `AGENTS.md`, `RELEASE_CONTROL.md`, `product/PRD.md`, `architecture/ARD.md`, `governance/claims-register.md`, and `docs/src/SUMMARY.md`

## Exclusions

- no production implementation source;
- no claim that source reading is universally prohibited;
- no claim that tests alone prove correctness;
- no claim that Robert C. Martin endorses this repository or its architecture;
- no claim that the full ecosystem already executes as one closed system;
- no `ALIVE` promotion without exact-head verification and replay;
- no replacement of the existing Verified Repository Reconstitution category.

## Positive witnesses

1. strategic terms are defined once and used consistently;
2. every no-read claim names the replacement controls;
3. every human responsibility removed from the critical path has a corresponding machine control and verifier;
4. the PRD and ARD preserve their target/documented ceilings;
5. the claims register distinguishes historical observation, strategic interpretation, and implementation standing;
6. the mdBook links the admitted chapter;
7. the authority JSON parses and contains no predeclared `ALIVE` state.

## Negative falsifiers

The pivot is false or incomplete when any of the following is observed:

- acceptance still requires a human to inspect implementation because requirements, architecture, or evidence are insufficient;
- an agent-generated test suite is the only verifier of agent-generated implementation;
- successful planning silently authorizes actuation;
- unknown evidence is promoted into success;
- generated output becomes independent authority;
- a no-read claim omits admission, independent falsification, standing, receipt, or replay;
- documentation claims implementation or production evidence that has not been observed;
- the external tweet is represented as product proof or endorsement.

## Verification commands

```bash
python3 -m json.tool authority/after-code-reading.json >/dev/null
python3 scripts/verify_docs.py --strict
mdbook build docs
```

Additional exact-head repository checks remain governed by `AGENTS.md` and `RELEASE_CONTROL.md`.

## Evidence paths

- generated mdBook output from CI;
- strict documentation-verifier report;
- exact PR diff;
- workflow run bound to the candidate commit.

## Receipt

No execution receipt is hand-authored by this ticket. CI or an admitted verifier must bind the exact source, authority, commands, results, and environment.

## Replay

A clean checkout must reproduce the same authority parse and mdBook projection with:

```text
NO_SEMANTIC_CHANGE
NO_GENERATED_DRIFT
REPLAY_MATCH
```

## Acceptance

The bounded documentation and authority pivot may reach `PARTIAL_ALIVE` after exact-head validation and mdBook replay. It may reach `ALIVE` only under the applicable bootstrap crown. It does not promote the complete product implementation, ecosystem integration, or external production standing.
