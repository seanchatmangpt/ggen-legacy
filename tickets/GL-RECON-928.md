# GL-RECON-928 — Compose the v26.9.28 repository reconstitution fabric

## Subject

- repository: `seanchatmangpt/ggen-legacy`
- exact base: `16a5c4f1051ecb0a98b06897e89e4e956be4d9b0`
- release: `v26.9.28`
- change class: semantic composition + independent verification
- default standing: `PARTIAL_ALIVE`

## Goal

Upgrade Verified Repository Reconstitution to consume the strongest existing
v26.9.28 ecosystem capabilities without implementing second copies of those
capabilities in ggen-legacy.

## Reuse law

```text
retrieve existing owner
→ bind exact subject
→ preserve its authority ceiling
→ compose through a typed contract
→ manufacture
→ independently verify
→ receipt/replay
```

Invent a local implementation only when an existing owner cannot satisfy the
required contract.

## Required owner boundaries

- ggen-marketplace: semantic source and reusable manufacturing basis
- ggen_igniter: provenance/projection
- ash_r2rml: VKG/read plane, authority NONE
- GraphLaw: semantic law/evidence
- ash_a2a: consequence construction
- XaaS: exclusive consequential DO/BRCE
- Affidavit: cryptographic trust, never authorization
- ash_pplan + Beam4PM + Ferroplan: planning/process/replanning
- WASM4PM + GymAct + AutoFDE + DSPy-WASM: portable execution/falsification
- UNRDF + GitVan: event and receipt evidence

## Positive witnesses

1. every required capability owner is pinned to a 40-character SHA;
2. exactly one component owns `CONSEQUENTIAL_DO`;
3. the read plane cannot acquire actuation authority;
4. trust cannot become authorization;
5. candidate branch work is represented without promotion;
6. HDDL preserves observe→admit→plan→manufacture→verify→receipt→replay→release;
7. FOND keeps failed-edge outcomes explicit rather than collapsing the graph;
8. the TLA+ release model names receipts and replay before release;
9. producer receipts remain non-promoting;
10. two clean producer runs are byte-identical;
11. required external exact SHAs are fetchable;
12. the independent crown binds the exact local revision and tree.

## Falsifiers

- mutable branch/tag identity is accepted as authority;
- another repository becomes a second BRCE owner;
- a generated artifact becomes canonical source;
- an open candidate silently widens mainline standing;
- a producer grants itself `ALIVE`;
- replay diverges;
- an exact external owner cannot be resolved;
- release is promoted without replay;
- Sunset Admission is inferred from Release Admission.

## Exclusions

This ticket does not merge or certify the external repositories. It records
their exact observed subjects and authority roles. External runtime behavior
retains the standing established by each owner repository's own courts.

## Acceptance

```text
local_contract=PASS
negative_controls=PASS
required_remote_subjects=PASS
producer_a=PARTIAL_ALIVE
producer_b=PARTIAL_ALIVE
replay_match=true
independent_crown=ALIVE
release_admitted=true
sunset_admitted=false
```
