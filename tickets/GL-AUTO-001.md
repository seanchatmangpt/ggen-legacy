# GL-AUTO-001 — Autonomic Conversation Foundry

## Subject

- repository: `seanchatmangpt/ggen-legacy`
- admitted base: `33dd18801fecce48a5022c2727d1cefdf450cc87`
- runtime: Python 3 standard library only
- authority: read admitted JSON input; write only beneath an explicit output directory
- claim ceiling: deterministic conversation-to-projection bootstrap

## Purpose

Reduce a structured design conversation to a canonical concept graph, manufacture deterministic operator and planning projections, and emit the smallest unresolved decision set.

```text
conversation observations
→ normalize
→ admit/refuse
→ canonical concept graph
→ deterministic projections
→ gap ledger
→ receipt
→ replay comparison
```

## Authored boundary

```text
autonomic/**
scripts/autonomic_finish.py
scripts/verify_autonomic_finish.py
fixtures/autonomic/**
tickets/GL-AUTO-001.md
```

## Required behavior

1. Accept a JSON observation bundle with explicit source identity.
2. Preserve observed, inferred, proposed, decided, blocked, unsupported, and refused claims separately.
3. Reject unknown standing values and duplicate concept identifiers.
4. Build a stable, sorted canonical graph.
5. Manufacture a Working Backwards brief, Claude operator contract, PPDDL problem, architecture summary, and gap ledger.
6. Never execute generated commands, modify repositories, call networks, or publish.
7. Write atomically beneath the supplied output directory only.
8. Emit a SHA-256 receipt binding input, canonical graph, projections, output manifest, and claim ceiling.
9. Re-running with identical input must produce byte-identical outputs and receipt.
10. A verifier must execute the fixture twice, compare trees byte-for-byte, and exercise negative fixtures.

## Falsifiers

- duplicate concept IDs are accepted;
- inferred claims are promoted to observed or decided;
- generated output escapes the output directory;
- generated commands execute;
- unknown standings are accepted;
- unresolved decisions disappear from the gap ledger;
- second execution differs from the first;
- receipt omits input or projection identity.

## Exclusions

- natural-language extraction from arbitrary chat transcripts;
- LLM invocation;
- Git, shell, network, package manager, deployment, or BRCE actuation;
- spiritual diagnosis or recovery certification;
- final project naming decisions;
- ecosystem `ALIVE` standing.

## Acceptance

```bash
python3 scripts/verify_autonomic_finish.py
```

Successful execution establishes only `ALIVE` for the bounded local foundry fixture and verifier subject.