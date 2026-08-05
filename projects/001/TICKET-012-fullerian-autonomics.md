# TICKET-012 — Fullerian Automation and Autonomics

## Identity

- **Repository:** `seanchatmangpt/ggen-legacy`
- **Exact base:** `8d6428f40c0d30d5983fb0ecdd16cab1c1328a23`
- **Project:** `001`
- **State transition:** `UNKNOWN → ALIVE` for the bounded reference autonomics subsystem only

## Authority

`AGENTS.md` → `RELEASE_CONTROL.md` → this ticket → `authority/fullerian-autonomics.json` → schema → runtime → independent verifier report.

## Problem

The repository documents observation, admission, planning, brokered actuation, receipt, replay, and standing, but it does not yet execute the Fuller-derived design calculus as a bounded autonomic loop. The implementation must preserve the distinction between Fuller canon and post-Fuller extensions rather than retroactively attributing admission, BRCE, receipt/replay, typed refusal, or scoped standing to Fuller.

## Preserve

Preserve the repository’s current G0–G9, SELECT/CONSTRUCT/DO, BRCE, exact-source, claim-ceiling, replay, and crown-separation laws. Do not modify generated appliance projections or the existing ten-subsystem reference crown.

## Fence

The new rail may write only a declared projection beneath its caller-supplied output directory. It has no repository, release, sunset, network, package, deployment, or external API authority.

## Calculus

1. **MONITOR:** collect provenance-bearing observations inside the exact system boundary.
2. **ANALYZE:** manufacture `O*` by admitting observations and refusing missing provenance, boundary mismatch, silent stakeholder externalization, or unknown ecological consequence.
3. **PLAN:** preserve the lawful candidate graph and select lexicographically by represented stakeholder coverage, known ecological consequence, reversible options, irreversible commitments, outcome/resource ratio, and stable identity.
4. **EXECUTE:** perform declared projection or refusal-evidence writes only through BRCE and issue an identity-bound deterministic receipt for either consequence.
5. **KNOWLEDGE:** retain canon, extensions, authority, inputs, receipts, negative controls, and replay evidence.

## Exclusions

- No repository crown.
- No production autonomy.
- No direct self-healing mutation of the governed subject.
- No claim of universal equivalence to Fuller’s canon.
- No ecological certification or completeness outside the represented boundary.
- No modification of existing generated appliance surfaces.

## Positive witnesses

- Two clean executions choose `preserve-fence-brce-intent`.
- The broker writes a projection plus receipt.
- Both executions are byte-identical.
- Receipt digests bind authority, program, selected candidate, and output.

## Negative falsifiers

Completion is falsified if direct execution, path escape, crown escalation, or missing provenance writes a governed projection; if any refusal evidence lacks a BRCE receipt; if replay differs; if the unbounded candidate wins; or if the report claims repository-level standing.

## Acceptance

```bash
python3 scripts/verify_fullerian_autonomics.py
python3 -m py_compile \
  scripts/run_fullerian_autonomics.py \
  scripts/verify_fullerian_autonomics.py
```

Expected verifier output:

```text
standing=ALIVE
claim_ceiling=REFERENCE_CONFORMANT
replay=REPLAY_MATCH
```

## Evidence

`evidence/fullerian-autonomics-verifier.json` is generated execution evidence and is not authority.
