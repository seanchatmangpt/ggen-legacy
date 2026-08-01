# Independent Subsystem Evidence and Read-Only Crown

This chapter integrates the v26.8.1 reconstruction work developed in `seanchatmangpt/ggen` PR #540 without transferring that open branch's standing into this repository.

The stable manufacturing coordinate remains:

```text
seanchatmangpt/ggen
0f39227c102e0ac7519f0f27561356227a518653
```

The observed design coordinate is:

```text
seanchatmangpt/ggen PR #540
a35086e7a12e2ff1724f307d2ef47eb165fcae29
```

PR #540 is design provenance only. It is not the executable ggen dependency for Project 001.

## Manifest is a claim, not authority

`appliance/bin/build-subsystem-evidence.py` manufactures a subsystem-evidence manifest from declared source sets and observed reference evidence. The manifest identifies evidence. It does not grant standing.

`appliance/bin/verify-subsystem-evidence.py` is a separately implemented verifier. It independently re-derives:

- exact source head;
- generator and verifier identities;
- manifest receipt digest;
- authority and implementation digests;
- primary evidence checks;
- negative-control outcomes;
- observer closure;
- document-evidence closure;
- replay, release, and sunset conditions.

The verifier does not import the manifest generator.

## Ten assurance subsystems

The bounded verifier-appliance crown is conjunctive across:

1. bounded claims;
2. customer control;
3. independent verification;
4. hidden challenges;
5. artifact bindings;
6. signature and transparency;
7. replay;
8. testing authority;
9. legal recourse;
10. release and sunset separation.

Every subsystem must be independently reported `ALIVE` for the reference crown.

## Observation law

`appliance/bin/observe-project.py` executes five observer classes:

- Git history;
- current tracked tree;
- authority surfaces;
- workflow surfaces;
- generated surfaces.

Each observer records `attempted`, `result_count`, and `errors`. A successful zero result is therefore distinguishable from an observer that was never attempted.

## DocumentEvidenceRecord

`authority/document-evidence.json` assigns every mdBook chapter:

- an authority reference;
- an implementation reference;
- a verifier reference;
- a legacy or historical reference.

`appliance/bin/build-document-evidence-index.py` resolves and hashes those objects. This replaces keyword-presence checks with object-level evidence linkage.

## Coverage manufacture and crown purity

`appliance/bin/project-subsystem-coverage.py` is the only subsystem-coverage projector. It manufactures `subsystem-coverage.json` from the independent verifier report.

`appliance/bin/verify-crown.py` does not write coverage. It recomputes the expected projection in memory, byte-compares the committed or staged projection, and refuses `GENERATED_COVERAGE_DRIFT`.

The crown may write its own verifier report. It may not repair the evidence it judges.

## Bounded result

The reference crown may reach `ALIVE` only for:

```text
scope = verifier-appliance-reference
```

It does not establish:

- complete ggen-legacy product standing;
- unrestricted program equivalence;
- external Fortune 5 production standing;
- regulatory certification;
- real predecessor Sunset Admission.
