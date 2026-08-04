# Autonomic Conversation Foundry

This directory defines the bounded `GL-AUTO-001` protocol.

## Input contract

The foundry accepts JSON containing:

- `subject`: exact conversation or corpus identity;
- `concepts`: canonical IDs, labels, kinds, states, evidence, dependencies, and decisions;
- `projections`: requested deterministic projection types;
- `constraints`: authority, privacy, WIP, and stopping rules.

The input is already structured observation. Arbitrary chat parsing is excluded from this ticket.

## Canonical states

`observed`, `admitted`, `inferred`, `proposed`, `decided`, `blocked`, `unsupported`, and `refused` are process states.

Formal standing remains:

- `UNKNOWN`
- `PARTIAL_ALIVE`
- `ALIVE`
- `BLOCKED`
- `BUILD_BROKEN`
- `UNSUPPORTED`
- `REFUSED:<CODE>`

The foundry never promotes a claim merely because it appears coherent.

## Manufactured projections

The 80/20 projection set is:

1. `ARCHITECTURE.md` — canonical concepts and relationships;
2. `WORKING_BACKWARDS.md` — future-state press release and FAQ inputs;
3. `CLAUDE.md` — bounded reference-operator contract;
4. `ppddl/problem.pddl` — planning problem over unresolved concepts;
5. `GAPS.json` — irreducible decisions and blockers;
6. `RECEIPT.json` — deterministic identity and replay evidence.

These files are projections. The admitted input bundle remains the authority.

## Execution

```bash
python3 scripts/autonomic_finish.py \
  --input fixtures/autonomic/conversation.json \
  --output /tmp/ggen-legacy-foundry
```

Verification:

```bash
python3 scripts/verify_autonomic_finish.py
```

## Authority boundary

The foundry may create and replace files only inside the explicit output directory. It does not execute generated commands, edit repositories, access networks, invoke models, or publish changes.