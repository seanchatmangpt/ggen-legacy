# ggen-legacy planning v26.8.7 — combinatorial-max search graph

`GL-PLAN-002` adds a bounded planning/search/verification substrate without widening world-actuation authority.

The admitted flow is:

```text
benchmark observation
→ anti-leak goal reconstruction
→ finite capability graph
→ preserve all lawful reversible edges
→ select one bounded WIP child
→ manufacture intent (construct-only)
→ independent receipt
→ admit child
→ resume/replan parent
→ candidate POWL / MFW projection
→ receipt-chain replay
```

## What is deliberately maximal

The subsystem preserves multiple representations and execution edges instead of forcing one planner or one projection:

- immutable capability fact graph and deterministic bounded A* checkpoint;
- benchmark goal-state reconstruction with reference-solution leak refusal;
- classical PDDL feature classification that preserves unsupported requirements rather than simplifying them;
- exact `skdecide-classical-engine <domain> <problem> <plan-out>` process boundary using registered `Astar` when scikit-decide is present;
- Fast Downward LAMA and VAL registry edges, independently probed and typed when unavailable;
- MFW universal JSON projection with the pinned 18-family planner vocabulary;
- POWL-like RDF projection using PROV-O, DCTERMS, SKOS, and P-Plan semantics;
- recursive `blocked → child → manufacture-intent → verify → admit → resume` orchestration;
- machine-readable schemas, RDF ontology, SPARQL query surfaces, receipts, replay, negative fixtures, CLI, verifier, and CI replay.

The maximal graph is bounded by ontology, finite fixture state, declared engines, authority, and receipts. One unavailable planner is topology, not graph failure.

## Authority fences

Planning **selects** only. The subsystem has no broker and no ambient actuation authority. `manufacture_intent()` creates an intent with `authority=construct-only` and `actuation=none`. Hooks or projections cannot execute it. A child capability becomes admitted only after an independent receipt matches the exact subject.

The in-repo A* is a verifier/checkpoint for the finite capability graph. It is not evidence that scikit-decide executed. Likewise, an engine registry entry or `--help` witness is not solver success.

## Local verification

```bash
python3 planning/v26.8.7/verify.py --strict
python3 -m unittest discover -s planning/v26.8.7/tests -v
planning/v26.8.7/skdecide_classical_engine.py --help
```

`verify.py` separates observed, admitted, executed, changed, verified, inferred, refused, blocked, and unsupported evidence. Its maximum standing is `PARTIAL_ALIVE`; repository/release `ALIVE` remains governed by `RELEASE_CONTROL.md`.

## Falsifiers

The subsystem is invalid if any of these occur:

1. a benchmark containing a reference/gold solution is accepted;
2. unsupported PDDL is silently rewritten into a supported subset;
3. an engine entry is treated as successful execution without an observed process receipt;
4. a planner or hook directly actuates world state;
5. a child is admitted without an exact-subject independent verification receipt;
6. a tampered event chain replays as valid;
7. a candidate projection is promoted to release or production standing;
8. failure of one planner edge deletes other lawful reversible edges.
