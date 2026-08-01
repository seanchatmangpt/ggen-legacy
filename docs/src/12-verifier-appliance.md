# Customer-Controlled Verifier Appliance

The verifier appliance is the executable answer to the Fortune 5 trust question: the customer does not need to inspect every source line, but it must own execution, hidden challenges, trust roots, evidence, replay, and final decision authority.

`ggen sync run` manufactures the appliance from `ontology/assurance-program.ttl` through `packs/ggen-legacy-assurance-pack`.

## Executable surfaces

- bounded claim and trust-root policy;
- Repository Standing Portfolio builder;
- independent verifier;
- customer-hidden challenge contract;
- SHA-256 artifact and evidence binding;
- SLSA v1 / in-toto provenance statement;
- real OpenSSL signature validation;
- append-only hash-chained transparency log;
- deterministic replay across customer VPC, independent lab, and recovery-site profiles;
- testing-authority and legal-recourse gates;
- separate Release Admission and Sunset Admission computation.

## Trust theorem

```text
ggen manufactures
customer executes
independent verifier measures
customer or third party attests
customer owns evidence and decision authority
```

The reference E2E crosses real process, filesystem, cryptographic, log, receipt, and replay boundaries. Its `ALIVE` result is bounded to the reference assurance fixture. It does not establish product production standing or authorize legacy retirement.
