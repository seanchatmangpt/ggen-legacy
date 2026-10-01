# ggen-legacy Ash PaaS pack

`GL-PAAS-001` manufactures a provider-neutral Elixir PaaS control-plane kernel from one admitted RDF graph.

## Manufacturing topology

```text
ontology.ttl (authority)
  ├─ public ontology alignment: Schema.org / PROV-O / DCAT / DCTERMS / ODRL / QUDT / SKOS
  ├─ SHACL + SPARQL refusal gates
  ▼
ggen @ 1e9fcb9679a61460fbd641415cb72511c7e50b33
  ▼
consumer/paas (generated; never edit)
  ├─ Ash resources and domain
  ├─ AshR2RML deterministic RDF/SHACL/R2RML projection
  ├─ AshR2RML Reactor semantic pipeline
  └─ ProvisionReactor → injected BRCE → bound receipt/replay
```

AshR2RML is pinned to `067954ad406fd637fd47646bdb10c4580809c79d` so the generated consumer is not coupled to a floating semantic compiler.

## Boundaries

- ggen runs at construction time, never request time.
- Ash is the manufactured operational model.
- AshR2RML compiles deterministic semantic projections and returns path/content graphs; it does not acquire filesystem authority.
- Reactor orchestrates admitted computation and the BRCE call; it has no shell/provider/network adapter of its own.
- ODRL models policy semantics only. It is not an authority token.
- Public ontology IRIs are pinned semantic identifiers; runtime manufacture does not fetch them over the network.
- The included ETS data layer is the provider-neutral executable kernel, not a production persistence claim.

## Verification

```bash
python3 gates/verify_pack.py

# With canonical ggen available:
ggen sync run --dry-run
ggen sync run
cd consumer/paas
mix deps.get
mix test
```

The first command is a local structural court. The ggen + Mix sequence is the runtime court. Only the latter can establish `ALIVE` for the generated PaaS kernel.
