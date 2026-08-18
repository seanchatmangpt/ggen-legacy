# GL-OSTAR-001 — OSTAR authority-vacuum reconstitution

## Outcome

Implement the first real `ggen-legacy` case study around OSTAR/OntoStar without pretending
that one LLM-produced codebase already defines the system. The observation stage must preserve
every exact artifact as evidence, expose contradictions, and terminate in `NO_AUTHORITY`.

An explicit O* contract may later be admitted over bounded observable surfaces. Admission does
not establish unrestricted program equivalence, runtime `ALIVE`, release standing, or Sunset
Admission.

## Exact starting subjects

- `seanchatmangpt/ggen-legacy@af218b480ad23f0218a907bbc46d80fa43eb42c5`
- `seanchatmangpt/ostar@a392e009400c83d5e175b508c4e3008e189945d3`
  through GitHub connector artifact observations; the private tree is not mounted here.
- `seanchatmangpt/open-ontologies@19110557537ffdbc7590a4243c36b1e5bfc1e58e`
  through an exact local checkout.
- the BusinessOS embedded OSTAR checkout remains unmaterialized and therefore `UNKNOWN`.

## Calculus

```text
LegacyArtifact → Observation
Observation × CardinalityLaw → Conflict | ConsistentObservation
ObservationSet → NO_AUTHORITY
NO_AUTHORITY × ExplicitAuthorityContract → O*_candidate | REFUSED
O*_candidate × ScopedEquivalenceEvidence → bounded standing
```

The admission engine does not infer intended program meaning. Rice's theorem forbids a general
decider for non-trivial semantic properties of arbitrary programs. This ticket changes the
problem by requiring an explicit bounded authority contract and named observable surfaces.

## Exclusions

- no canonical repository is selected by recency, name, README, or majority vote;
- no handbook-derived source enters EMPIRE;
- no private OSTAR source is copied into this public repository;
- no unrestricted semantic equivalence claim;
- no human/model/planner output receives ambient DO authority;
- no predecessor retirement.

## Falsifiers

- an observer can set authority or select a canonical subject;
- a universal-equivalence contract is accepted;
- a final capability remains `UNKNOWN`;
- referenced evidence does not exist;
- a required-refusal study closes without a `REFUSED` disposition;
- two identical runs produce different receipt digests;
- receipt tampering survives replay.

## Acceptance

```bash
python3 tools/v26.8.1/test_authority_vacuum.py -v
python3 tools/v26.8.1/authority_vacuum.py observe \
  --study reconstitution/ostar/study.json \
  --subject-root ontostar-open-ontologies=/exact/open-ontologies \
  --out /tmp/ostar-observation-a.json
python3 tools/v26.8.1/authority_vacuum.py observe \
  --study reconstitution/ostar/study.json \
  --subject-root ontostar-open-ontologies=/exact/open-ontologies \
  --out /tmp/ostar-observation-b.json
python3 tools/v26.8.1/authority_vacuum.py replay \
  --left /tmp/ostar-observation-a.json \
  --right /tmp/ostar-observation-b.json
```
