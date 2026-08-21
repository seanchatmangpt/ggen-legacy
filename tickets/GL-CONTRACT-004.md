# GL-CONTRACT-004 — pilot BSG-style contract graph (Gall checkpoint 2)

**Status:** admitted, `NOT_STARTED` — drafted this session, not executed
**Base:** `seanchatmangpt/ggen-legacy@f9b283e`
**Standing ceiling:** `PARTIAL_ALIVE` (pilot subset only)
**Publication:** draft pull request; no merge authority

## Outcome

Instantiate `ggen:HistoricalImplementation`/`ggen:CurrentImplementation`/
`ggen:ObservableContract` (declared in `ontology/v26.8.1/ontology.ttl:182-194`
but never populated by `to_turtle()`) for a **3-5 capability pilot subset**
of the 65 published `LegacyCapability` individuals, and add a
`ggen:ContractRule` class with typed `ggen:precondition`/`ggen:postcondition`
+ `ggen:dependsOnRule` edges — replacing free-text `ordering_requirements`
(e.g. `legacy_archaeology.py:395`) with real graph edges, for that pilot only.

## Authored boundary

```text
ontology/v26.8.1/ontology.ttl          # additive classes/properties only
ontology/v26.8.1/legacy-capabilities.ttl  # pilot individuals only, additive
tickets/GL-CONTRACT-004.md
```

The other 60+ published individuals, `ggen:equivalenceVerifier`/
`negativeFalsifier`'s existing `"UNASSIGNED"` value, and the flat
`input_contract`/`output_contract`/`error_contract` string fields all remain
untouched outside the pilot.

## Pilot subset (named per Hard Law 1 — ultracode backlog item 3 fix: this
was previously required but not actually named)

Five individuals, chosen for having non-trivial `ordering_requirements`
prose to convert into real edges and for spanning more than one disposition:

1. `legacy_ggen_core_pipeline` (`REPLACED`) — has explicit pipeline-stage
   ordering prose.
2. `legacy_process_intelligence_local_analysis` (`SUBSUMED`) — directly
   relevant to this repo's own `wasm4pm`/`wasm4pm-compat` boundary rule
   already in `CLAUDE.md`.
3. `legacy_ggen_a2a_mcp_server` (`SUBSUMED`)
4. `legacy_ggen_lsp_mcp_server` (`SUBSUMED`)
5. `legacy_ggen_lsp_a2a_bridge` (`SUBSUMED`) — 3-4-5 together are the
   MCP/A2A-into-`ggen-lsp` fold-in cited in
   `docs/v26.8.1/90-legacy/91-ggen-legacy-definition.md:51`, a natural
   dependency-edge cluster to pilot the DAG model on.

If, once implementation starts, a named individual turns out to have no
real ordering/precondition content to convert (empty/trivial
`ordering_requirements`), swap it for another `SUBSUMED` individual and
record the substitution here rather than silently picking a different one.

**Escape hatch triggered (ultracode backlog item 4, verified by reading the
real Python source):** 3 of the 5 named pilots have `ordering_requirements
="UNKNOWN"` verbatim — not real prose to convert:
`legacy_ggen_a2a_mcp_server`, `legacy_ggen_lsp_mcp_server`,
`legacy_ggen_lsp_a2a_bridge`. Hard Law 3 requires every `ContractRule` edge
cite the source sentence it replaces; `"UNKNOWN"` has no sentence to cite.
Only `legacy_ggen_core_pipeline` and `legacy_process_intelligence_local_analysis`
survive with real, convertible `ordering_requirements` text. **Before
execution, a future session must pick 3 replacement `SUBSUMED` individuals
with real ordering prose and record them here** — this was not done in this
design pass (out of scope for a schema-design-only review); do not execute
this ticket against only 2 pilots without either doing that substitution or
formally reducing the ticket's stated pilot size to 2 in this file first.

## Proposed schema (design only — not yet written to ontology.ttl)

Decision: **string-literal precondition/postcondition, not sub-resources** —
both surviving pilots' `ordering_requirements` collapse to a single binary
precedes-relation, not a compound boolean expression; a sub-resource would
be schema overhead with nothing to hang off it yet (Gall's Law: the simple
working shape first). `ggen:orderingRequirements` prose is retained on the
individual, not deleted — the new rule cites it, doesn't replace it.

```turtle
ggen:ContractRule a owl:Class ;
  rdfs:comment "A single ordering constraint decomposed from a LegacyCapability's ordering_requirements prose. Cites the source sentence it replaces via rdfs:comment." .

ggen:precondition a owl:DatatypeProperty ; rdfs:domain ggen:ContractRule ; rdfs:range xsd:string .
ggen:postcondition a owl:DatatypeProperty ; rdfs:domain ggen:ContractRule ; rdfs:range xsd:string .
ggen:dependsOnRule a owl:ObjectProperty ; rdfs:domain ggen:ContractRule ; rdfs:range ggen:ContractRule .
ggen:hasContractRule a owl:ObjectProperty ; rdfs:domain ggen:LegacyCapability ; rdfs:range ggen:ContractRule .

# legacy_ggen_core_pipeline — cites: "Single-pass render, not the current
# 5-stage Resolve/Enrich/Extract/Render/Write pipeline"
ggen:rule_core_pipeline_single_pass a ggen:ContractRule ;
  rdfs:comment "Cites legacy_ggen_core_pipeline's ordering_requirements verbatim above." ;
  ggen:precondition "Template + context data available (ggen.toml + .specify/*.ttl loaded)" ;
  ggen:postcondition "Output rendered and written in a single pass, with no separate Resolve/Enrich/Extract stages" .
ggen:legacy_ggen_core_pipeline ggen:hasContractRule ggen:rule_core_pipeline_single_pass .

# legacy_process_intelligence_local_analysis — cites: "analysis ran after
# OCEL emission, in the same process"
ggen:rule_pi_ocel_emitted_first a ggen:ContractRule ;
  rdfs:comment "Cites legacy_process_intelligence_local_analysis's ordering_requirements verbatim above." ;
  ggen:precondition "OCEL event stream has been emitted during sync (ggen-graph/ocel/{pack_events,lifecycle}.rs)" ;
  ggen:postcondition "Local discovery/conformance/fitness/precision/variant analysis executes, in the same process as emission" .
ggen:legacy_process_intelligence_local_analysis ggen:hasContractRule ggen:rule_pi_ocel_emitted_first .
```

**Real divergence from the source paper (ultracode backlog item 5, verified
against the actual AgentModernize paper, arXiv:2605.17535):** the paper's
formal BSG model is `G=(V,E,Pre,Post,Inv)` — invariants (`Inv`) are a
first-class third component alongside pre/postconditions. This schema has no
invariant slot. This is a real, named omission relative to the paper's model
(not just a naming gap), deliberately deferred: neither pilot's
`ordering_requirements` prose expresses an invariant (a "must always hold"
condition, as opposed to a before/after precede-relation), so there's
nothing real to convert yet — adding `ggen:invariant` speculatively would
violate Hard Law 3 the same way fabricating an edge would. A future ticket
extending the pilot should add `ggen:invariant` (string literal, same
pattern as precondition/postcondition) when a real individual's prose
actually expresses one.

`ggen:dependsOnRule` is declared but intentionally unpopulated for these two
— each decomposes to one precede-relation internal to itself, not a
cross-rule dependency; it activates once a 3rd/4th/5th pilot with real
cross-capability ordering prose is substituted in per the escape-hatch note
above.

## Hard laws

1. Pilot subset is fixed at ticket-admission time (not discovered ad hoc)
   and named explicitly in this file before any TTL is written.
2. No wholesale schema migration — the other ~60 individuals keep their
   current flat shape until a separate ticket admits migrating them.
3. `ggen:ContractRule` edges must derive from the pilot capability's existing
   `ordering_requirements` prose, not invented — every edge cites the source
   sentence it replaces.
4. `ggen:equivalenceVerifier`/`negativeFalsifier` for pilot individuals may
   move off `"UNASSIGNED"` only if bound to a real, runnable command —
   never a placeholder string.

## Falsifiers

- A pilot individual's new `ContractRule` graph contradicts its own
  `ordering_requirements` prose (the prose isn't deleted, only superseded —
  contradiction between the two is a ticket failure).
- `to_turtle()` (or its successor) emits malformed Turtle for a pilot
  individual (parse-check with a real TTL parser, not eyeballing).
- A non-pilot individual's TTL output changes at all (diff must be empty
  outside the pilot's own block).

## Acceptance (not yet run — ticket not started)

```bash
# once implemented:
python3 tools/v26.8.1/legacy_archaeology.py emit
git diff ontology/v26.8.1/legacy-capabilities.ttl   # only pilot individuals change
# parse-validate the emitted Turtle with a real parser (e.g. rdflib.Graph().parse(...))
```

## Standing

`UNKNOWN` — not started. This ticket exists so a future session executes
against a real, bounded scope instead of re-deriving it; see
`CLAUDE.md`'s Gall's Law checkpoint 2 and this session's Explore finding
(`ontology.ttl:182-194`, `:236-241`) for the grounding.
