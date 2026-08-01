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

## Offline verifier transport

`appliance/bin/build-offline-bundle.sh` manufactures a deterministic portable bundle containing the appliance, admitted authority, schemas, ontology, ggen pack, reference fixtures, repository law, and a self-verifying SHA-256 manifest.

The builder:

- binds the exact `ggen-legacy` source head;
- binds the stable ggen manufacturing coordinate;
- excludes customer source and credentials;
- requires no network connection during verification;
- writes an offline activation script that removes proxy configuration;
- writes a manifest verifier;
- normalizes archive time, owner, group, ordering, and gzip metadata;
- produces a portable bundle receipt;
- must produce byte-identical archives and receipts on a second build at the same source head.

The bundle class is `PORTABLE_APPLICATION_BUNDLE`. It intentionally does not claim to contain hermetic Python or OpenSSL runtimes. Exact runtime identities remain evidence inputs. A future hermetic transport may extend this boundary without changing the standing contract.

The transport pattern is informed by `seanchatmangpt/ggen` PR #537 at `4bd2df69362c2708551f870c3dac36bce97898c2`. Its dedicated offline-toolchain workflow succeeded, while its broader CI and Quality workflows failed. Project 001 therefore imports the proven deterministic transport pattern without transferring branch-wide standing or admitting that branch as a dependency.
