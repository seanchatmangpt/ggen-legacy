# OSTAR DfCM preservation graph

This directory extends `GL-OSTAR-001` without inventing the missing authority contract.

## Preserve

The authority-vacuum study contains six candidate capabilities and five required final dispositions:

- `PRESERVED`
- `SUBSUMED`
- `REPLACED`
- `ARCHIVED`
- `REFUSED`

The existing admission law requires every admitted capability to receive exactly one final disposition and requires all five dispositions to be exercised.

Before evidence chooses semantics, DfCM preserves every **syntactically closed** assignment that satisfies that structural law. For six labelled capabilities mapped onto five labelled dispositions, the number of surjective assignments is:

```text
5! × S(6,5) = 120 × 15 = 1800
```

These are construction candidates, not authority claims. Every option remains:

```text
authority_state = NO_AUTHORITY
selection_state = UNSELECTED
selection_authority = false
actuation_authority = false
claim_ceiling = SYNTACTIC_CLOSURE_ONLY
```

## Fence

`dfcm_option_graph.py select` always returns:

```text
REFUSED:DFCM_SELECTION_REQUIRES_ADMISSION
```

A graph can only be reduced by explicit reversible constraints. Constraints may prune impossible edges, but they cannot grant selection or actuation authority.

## Evidence frontier

DfCM does not invent a tie-breaker when several evidence targets have equal topology value. The `frontier` command partitions the retained option graph by the disposition that would be learned for each capability and reports every equally maximal target.

```bash
python3 reconstitution/ostar/dfcm_option_graph.py frontier \
  --graph /tmp/ostar-dfcm-a.json
```

For the unpruned six-capability graph, every capability is equally informative:

```text
option_count = 1800
support per disposition = 360
entropy_bits = 2.321928094887
worst_case_remaining = 360
guaranteed_prunable = 1440
maximal_information_targets = all six capabilities
```

The frontier is `EVIDENCE_PARTITION_ONLY`. It grants neither evidence-acquisition authority nor selection/actuation authority. After lawful pruning, it is recomputed from the retained graph; a capability already fixed by evidence drops out of the maximal frontier rather than being queried again.

## Replay

```bash
python3 reconstitution/ostar/dfcm_option_graph.py construct \
  --study reconstitution/ostar/study.json \
  --out /tmp/ostar-dfcm-a.json

python3 reconstitution/ostar/dfcm_option_graph.py construct \
  --study reconstitution/ostar/study.json \
  --out /tmp/ostar-dfcm-b.json

python3 reconstitution/ostar/dfcm_option_graph.py replay \
  --left /tmp/ostar-dfcm-a.json \
  --right /tmp/ostar-dfcm-b.json
```

Expected result:

```text
REPLAY_MATCH
option_count = 1800
```

## Evidence pruning

A constraint is not an authority contract. It only states an allowed subset for a named capability.

```json
{
  "schema": "ggen.legacy.dfcm-constraints.v1",
  "selection_authority": false,
  "actuation_authority": false,
  "rules": [
    {
      "capability": "ostar-cli-load",
      "allowed_dispositions": ["REFUSED"]
    }
  ]
}
```

The resulting graph remains unselected and non-actuating. A later explicit O* authority contract must still bind exact evidence, observable surfaces, and the observation receipt before `authority_vacuum.py admit` can produce an `ADMITTED_CANDIDATE`.
