# GL-PAAS-001 — Ontology-manufactured Ash PaaS

## Status

`PARTIAL_ALIVE` until the exact generated Elixir subject is executed by the repository court.

## Outcome

Manufacture a provider-neutral PaaS control-plane kernel from admitted RDF using canonical ggen. The manufactured application uses Ash Framework for the operational resource model, AshR2RML for deterministic Ash↔RDF/SHACL/R2RML projection, and Reactor for orchestration. External side effects are legal only through an injected BRCE executor that returns a bound receipt.

## Authority

Source authority is `packs/ggen-ash-paas-pack/ontology.ttl` plus its fail-closed gate. Public vocabularies are semantic dependencies, not execution authorities. ODRL statements describe policy; they never grant ambient DO authority. Generated files under `consumer/paas/` are projections and MUST NOT be hand-edited.

The construction chain is:

`public ontology profile → ggen admission → generated Ash/Reactor source → AshR2RML semantic compilation → Reactor intent → BRCE → receipt → replay`.

## Public semantic alignment

- Schema.org — service/application semantics.
- W3C PROV-O — deployment and receipt provenance.
- W3C DCAT — catalog semantics.
- DCMI DCTERMS — identifiers/titles/version metadata.
- W3C ODRL — policy description only.
- QUDT — metering quantity semantics.
- SKOS — service tier concept schemes.
- W3C SHACL — admission constraints.
- W3C R2RML — relational projection.

The pack records these IRIs with `dcterms:conformsTo`; it does not perform ambient network ontology fetches during manufacture or request handling.

## SELECT / CONSTRUCT / DO

- SELECT: `ControlPlane.select/1` ranks reversible candidate maps. No execution authority.
- CONSTRUCT: `ProvisionReactor` admits a request and manufactures a deterministic intent digest.
- DO: only the injected module implementing `GgenLegacyPaaS.BRCE` may actuate.
- RECEIPT: DO is accepted only when the returned receipt binds `receipt_id`, `intent_digest`, and `replay_key` to the exact intent.

Hooks, RDF, SHACL, ODRL, model output, templates, and Reactor plans have no ambient actuation authority.

## Acceptance

1. `python3 packs/ggen-ash-paas-pack/gates/verify_pack.py` exits 0.
2. Exact canonical ggen dry-run admits the untouched ontology and refuses a mutation that disables `paas:brceRequired`.
3. Canonical ggen manufactures `consumer/paas/mix.exs`, `consumer/paas/lib/ggen_legacy_paas.ex`, and `consumer/paas/test/ggen_legacy_paas_test.exs` twice with byte-identical output.
4. The generated app resolves the exact AshR2RML source SHA recorded by this ticket, compiles, and passes `mix test`.
5. Tests observe deterministic `AshR2RML.compile_ash_ttl_bundle/1` output containing the public ontology IRIs.
6. Tests execute `AshR2RML.Reactor.Pipeline` against the exact generated Ash resource closure.
7. Tests execute the PaaS provisioning Reactor with a receipting BRCE fixture and refuse an unbound receipt.
8. No test or template introduces request-time ggen execution, direct shell/network actuation, or file writes in the runtime control plane.

## Pinned construction identities

- ggen: `1e9fcb9679a61460fbd641415cb72511c7e50b33`
- ash_r2rml: `067954ad406fd637fd47646bdb10c4580809c79d`

## Exclusions

This ticket does not claim provider provisioning, cloud credentials, billing settlement, multi-region failover, a Phoenix/GraphQL/JSON:API edge, or external production ALIVE. Those are lawful extensions once a concrete provider contract is admitted. This ticket establishes the provider-neutral semantic/control-plane manufacturing kernel.

## Falsifiers

Any of the following invalidates standing:

- ggen admits `paas:brceRequired false`;
- a generated runtime calls ggen at request time;
- Reactor calls shell, HTTP, provider SDK, or filesystem mutation directly instead of BRCE;
- an actuation result without a bound receipt is accepted;
- two manufactures from the same admitted graph differ;
- AshR2RML output omits the admitted public class/property IRIs;
- generated application tests fail against the pinned AshR2RML identity.
