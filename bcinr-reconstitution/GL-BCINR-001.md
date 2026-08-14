# GL-BCINR-001 — Reconstitute BCINR claim/evidence authority

## Outcome

Establish an independently verifiable generated contract that separates BCINR claim kinds, evidence kinds, receipt shapes, authority fences, and scoped standing before changing BCINR runtime code.

## Exact producer

- repository: `seanchatmangpt/ggen`
- admitted producer base: `162e466d8f07d0a75a468b4441b4bc8b1aad369b`
- producer branch: `agent/bcinr-evidence-contract-reconstitution`
- authority: `self-host/bcinr-evidence-contract/ontology.ttl`
- generator: `self-host/bcinr-evidence-contract/ggen.toml`
- expected projection path: `generated/bcinr-evidence-contract.json`

## Exact receiver

- repository: `seanchatmangpt/ggen-legacy`
- admitted receiver base: `49c3a1eddf3d90560b9471573b6455dc240fe752`
- receiver branch: `agent/bcinr-evidence-contract-receiver`
- independent verifier: `bcinr-reconstitution/verify_contract.py`

## Required laws

1. `INSPECTION_NOT_EXECUTION`
2. `CITATION_NOT_PROOF_RECEIPT`
3. `BRANCHLESS_IS_TARGET_INDEXED`
4. `BOUNDED_NOT_BIG_O`
5. `DOC_HIDDEN_NOT_AUTHORITY_FENCE`
6. `NO_AMBIENT_DO`
7. `EXACT_SUBJECT_STANDING`

## Required claim kinds

- `BOUNDED_WORK`
- `TARGET_BRANCHLESS`
- `SEMANTIC_EQUIVALENCE`
- `PROOF`
- `RUNTIME_RECEIPT`
- `AUTHORITY_FENCE`
- `SCOPED_STANDING`

## Falsifiers

Refuse the contract if any required law or claim kind is missing, if formal citation evidence can claim `ALIVE`, if proof-receipt or execution-receipt fields are incomplete, if the producer/receiver/consumer identities drift silently, or if the contract claims ambient actuation authority.

## Exclusions

This ticket does not modify BCINR runtime code, does not manufacture the projection without ggen execution, does not bind mfact proof terms, does not perform object-code audits, and does not grant repository or release standing.

## Replay

```bash
cd /path/to/ggen/self-host/bcinr-evidence-contract
ggen sync run --config ggen.toml
python3 /path/to/ggen-legacy/bcinr-reconstitution/verify_contract.py \
  --contract /path/to/ggen/generated/bcinr-evidence-contract.json
```
