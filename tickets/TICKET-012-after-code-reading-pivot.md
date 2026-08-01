# TICKET-012 — Admit and crown the After Code Reading strategic corpus

## Identity

- **Release:** `v26.8.1`
- **Exact base:** `8d6428f40c0d30d5983fb0ecdd16cab1c1328a23`
- **Type:** documentation, authority, product, architecture, governance, evidence, replay, and crown admission
- **Expected transition:** bounded strategic corpus from `UNKNOWN` through `PARTIAL_ALIVE` to exact-head `ALIVE / REFERENCE_CONFORMANT`
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

The repository defines Verified Repository Reconstitution but requires one governing engineering boundary for the condition in which machine implementation throughput exceeds human source-inspection throughput.

Without a crowned strategic corpus:

- no-read language may be mistaken for absent accountability;
- tests may be treated as the complete replacement for source inspection;
- architecture, authority, planning, actuation, process evidence, standing, receipts, and replay may remain disconnected;
- repositories and public explanations may describe adjacent tools rather than one industrial program;
- benchmark claims may optimize code volume instead of verified consequences per human inspection unit;
- documentation may assert the doctrine without independently replaying the exact corpus.

## Bounded scope

Admit and independently crown a strategic authority corpus defining:

- **After Manual Code** as the broad transition;
- **After Code Reading** as the engineering boundary;
- **Proof-Carrying Software Manufacturing** as the method;
- **Software Systems Manufacturer** as the accountable profession;
- Verified Repository Reconstitution as the ggen-legacy product contribution;
- the control loop replacing mandatory source inspection;
- the human responsibilities retained;
- project-to-lane mappings;
- claim ceilings, benchmarks, pull-request questions, and falsifiers;
- non-promoting evidence manufacture;
- two clean documentary replays;
- an independent read-only crown and sabotage controls.

## Inputs

- current `ggen-legacy` authority, PRD, ARD, claims register, and mdBook;
- the 2026-07-23 public statement at the exact X coordinate above;
- the existing repository doctrines for admission, manufacture, independent verification, receipts, replay, Release Admission, and Sunset Admission.

## Outputs

### Strategic authority and projections

- `authority/after-code-reading.json`
- `product/AFTER_CODE_READING.md`
- `architecture/AFTER_CODE_READING_ARCHITECTURE.md`
- `governance/after-code-reading-review-standard.md`
- `docs/src/15-after-code-reading.md`
- updates to `README.md`, `AGENTS.md`, `RELEASE_CONTROL.md`, `product/PRD.md`, `architecture/ARD.md`, `governance/claims-register.md`, and `docs/src/SUMMARY.md`

### Executable assurance

- `scripts/manufacture_after_code_reading_evidence.py`
- `scripts/measure_after_code_reading_replay.py`
- `scripts/verify_after_code_reading_crown.py`
- `.github/workflows/after-code-reading-crown.yml`
- workflow artifact containing manufacture, replay, crown, and SHA-256 evidence files

## Exclusions

- no claim that the complete production implementation is `ALIVE`;
- no claim that the complete A–K foundry program is closed;
- no claim that a real predecessor has received Sunset Admission;
- no claim that source reading is universally prohibited;
- no claim that tests alone prove correctness;
- no claim that Robert C. Martin endorses this repository or its architecture;
- no claim that the full ecosystem already executes as one closed production system;
- no replacement of the existing Verified Repository Reconstitution category;
- no promotion beyond the exact bounded strategic corpus verified by the crown.

## Positive witnesses

1. strategic terms are defined once and used consistently;
2. every no-read claim names replacement controls;
3. every human responsibility removed from the critical path has a corresponding machine control and verifier;
4. the PRD and ARD distinguish strategic-corpus standing from runtime implementation standing;
5. the claims register distinguishes historical observation, strategic interpretation, corpus standing, and product standing;
6. the mdBook links and builds the admitted chapter;
7. the authority JSON parses and names the dedicated promotion workflow;
8. the evidence manufacturer remains non-promoting and emits at most `PARTIAL_ALIVE`;
9. two detached clean worktrees produce byte-identical replay reports;
10. the independent crown re-derives source, authority, projection, replay, and claim-ceiling fields;
11. sabotage controls for missing category authority, producer self-certification, replay divergence, and missing receipts are rejected;
12. the crown report binds the exact revision and tree and emits `ALIVE / REFERENCE_CONFORMANT` for the strategic corpus only.

## Negative falsifiers

The pivot or its crown is false or incomplete when any of the following is observed:

- acceptance still requires a human to inspect implementation because requirements, architecture, or evidence are insufficient;
- an agent-generated test suite is the only verifier of agent-generated implementation;
- successful planning silently authorizes actuation;
- unknown evidence is promoted into success;
- generated output becomes independent authority;
- a no-read claim omits admission, independent falsification, standing, receipt, or replay;
- documentation claims implementation or production evidence that has not been observed;
- the external tweet is represented as product proof or endorsement;
- the producer grants itself `ALIVE`;
- the two clean replays diverge;
- the crown accepts a missing or invalid receipt;
- strategic-corpus standing is generalized to the complete product.

## Verification commands

```bash
python3 -m json.tool authority/after-code-reading.json >/dev/null
python3 scripts/verify_docs.py --strict
mdbook build docs
python3 scripts/manufacture_after_code_reading_evidence.py --help
python3 scripts/measure_after_code_reading_replay.py --help
python3 scripts/verify_after_code_reading_crown.py --help
```

The exact-head workflow executes the full producer, clean replay, independent crown, negative-control, and evidence-upload sequence.

## Evidence paths

- `/tmp/after-code-reading-manufacture.json`
- `/tmp/after-code-reading-replay-a.json`
- `/tmp/after-code-reading-replay-b.json`
- `/tmp/after-code-reading-evidence.sha256`
- `evidence/after-code-reading-crown.json`
- immutable workflow artifact named for the exact candidate SHA

## Receipt

The ticket does not hand-author an execution receipt. The dedicated workflow binds exact source, tree, authority, producer output, two replay outputs, independent verifier output, negative controls, and SHA-256 identities.

## Replay

Two detached clean worktrees at the same candidate commit must independently execute the strict documentation verifier and mdBook projection. Their machine-readable replay reports must be byte-identical and establish:

```text
NO_SEMANTIC_CHANGE
NO_GENERATED_DRIFT
REPLAY_MATCH
```

## Acceptance

The bounded strategic corpus reaches `ALIVE / REFERENCE_CONFORMANT` only when the dedicated exact-head crown reports:

```text
producer_standing=PARTIAL_ALIVE
producer_final_admission_allowed=false
clean_replay_count=2
replay_match=true
producer_verifier_separated=true
negative_controls=PASS
receipt_valid=true
release_admitted=true
standing=ALIVE
```

This acceptance does not promote the complete product implementation, complete A–K foundry closure, external production standing, or any real predecessor Sunset Admission.
