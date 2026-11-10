# retirement-manifest

Standing: PARTIAL

Ticket T-034. Every entry of xaas/lib/xaas (scratch tree) has an owner. Sizes: du -sk.
Owner kinds: KEEP (core), KEEP-CHECK, owner repo, new repo, drop. Assignments are
proposals pending D1/D2; items marked UNVERIFIED lack confirmed consumers.

## Manifest

| entry | size | owner kind | target / note |
|---|---|---|---|
| a2a | 24K | owner repo | ash_a2a |
| a2a.ex | 4K | owner repo | ash_a2a |
| accounts | 92K | KEEP | core |
| accounts.ex | 4K | KEEP | core |
| actuation | 48K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| actuation.ex | 36K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| application.ex | 12K | KEEP | shared infra for new backend (platform) |
| architecture | 8K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| ash_typescript_manifest.ex | 4K | owner repo | ggen / ggen_igniter (generation capital) |
| autofde | 20K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| aws_repo.ex | 4K | KEEP-CHECK | AWS adapters; UNVERIFIED use by core |
| aws_repo_adapters | 8K | KEEP-CHECK | AWS adapters; UNVERIFIED use by core |
| billing | 204K | KEEP | core |
| billing.ex | 4K | KEEP | core |
| bridges | 76K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| case_studies | 104K | drop | non-core; docs/demo only; UNVERIFIED consumers |
| castle | 4K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| castle.ex | 40K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| causal_receipt | 16K | new repo | non-core platform/research repo |
| checks | 12K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| chicago | 88K | owner repo | chicago-tdd-tools |
| chicago.ex | 8K | owner repo | chicago-tdd-tools |
| compat | 4K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| conference | 36K | drop | non-core; docs/demo only; UNVERIFIED consumers |
| conference.ex | 4K | drop | non-core; docs/demo only; UNVERIFIED consumers |
| coupling | 20K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| coupling.ex | 4K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| cs2 | 24K | owner repo | chicago-tdd-tools |
| datalayer | 20K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| deployment | 20K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| dev_seeds.ex | 20K | KEEP | shared infra for new backend (platform) |
| eds | 20K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| fabric | 32K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| fabric.ex | 8K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| gall | 56K | owner repo | zcode-cli gall-work |
| generated | 48K | owner repo | ggen / ggen_igniter (generation capital) |
| generation | 48K | owner repo | ggen / ggen_igniter (generation capital) |
| generation.ex | 4K | owner repo | ggen / ggen_igniter (generation capital) |
| governance | 608K | new repo | non-core platform/research repo |
| governance.ex | 4K | new repo | non-core platform/research repo |
| graphlaw | 20K | owner repo | ggen / ggen_igniter (generation capital) |
| graphlaw.ex | 4K | owner repo | ggen / ggen_igniter (generation capital) |
| hammer.ex | 4K | KEEP | shared infra for new backend (platform) |
| hddl | 8K | owner repo | ggen / ggen_igniter (generation capital) |
| igniter | 16K | owner repo | ggen / ggen_igniter (generation capital) |
| igniter.ex | 4K | owner repo | ggen / ggen_igniter (generation capital) |
| ledger | 28K | KEEP | into billing |
| ledger.ex | 4K | KEEP | into billing |
| legacy_repo.ex | 4K | KEEP | shared infra for new backend (platform) |
| library | 172K | KEEP-CHECK | needs check; aliases Governance 1 |
| library.ex | 4K | KEEP-CHECK | needs check; aliases Governance 1 |
| local.yaml | 4K | KEEP | shared infra for new backend (platform) |
| mailer.ex | 4K | KEEP | shared infra for new backend (platform) |
| marketplace | 48K | owner repo | ggen-marketplace |
| marketplace.ex | 4K | owner repo | ggen-marketplace |
| ocel | 64K | new repo | ocel repo; serv_engine aliases it 16x, port behind emit port |
| ocel.ex | 4K | new repo | ocel repo; serv_engine aliases it 16x, port behind emit port |
| ontology | 8K | owner repo | ggen / ggen_igniter (generation capital) |
| operations | 332K | KEEP-CHECK | check; aliases Semantics, Governance, Castle |
| operations.ex | 4K | KEEP-CHECK | check; aliases Semantics, Governance, Castle |
| pack.ex | 40K | owner repo | ggen / ggen_igniter (generation capital) |
| planning | 36K | new repo | non-core fabric/ops repo; UNVERIFIED consumers |
| platform | 120K | KEEP | core |
| platform.ex | 4K | KEEP | core |
| postgrex_types.ex | 4K | KEEP | shared infra for new backend (platform) |
| procurement | 12K | KEEP | core (scope per D4) |
| procurement.ex | 4K | KEEP | core (scope per D4) |
| prom_ex.ex | 4K | KEEP | shared infra for new backend (platform) |
| prom_ex_plugins | 4K | KEEP | shared infra for new backend (platform) |
| receipt | 36K | new repo | non-core platform/research repo |
| release.ex | 4K | KEEP | shared infra for new backend (platform) |
| repo.ex | 4K | KEEP | shared infra for new backend (platform) |
| research_runtime | 168K | new repo | non-core platform/research repo |
| resource.ex | 4K | KEEP | shared infra for new backend (platform) |
| retireable_register.ex | 16K | drop | superseded by this manifest |
| runtime | 260K | new repo | non-core platform/research repo |
| sa2a | 80K | owner repo | ash_a2a |
| secrets.ex | 4K | KEEP | shared infra for new backend (platform) |
| security | 8K | KEEP | core |
| security.ex | 8K | KEEP | core |
| seed_guard.ex | 4K | KEEP | shared infra for new backend (platform) |
| self_digest | 36K | new repo | non-core platform/research repo |
| semantics | 236K | new repo | non-core platform/research repo |
| serv_engine | 1096K | KEEP | core |
| sjira | 148K | owner repo | ggen / ggen_igniter (generation capital) |
| sparql_bridge.ex | 12K | owner repo | ggen / ggen_igniter (generation capital) |
| storage.ex | 12K | KEEP | shared infra for new backend (platform) |
| system_authority.ex | 4K | KEEP | shared infra for new backend (platform) |
| telemetry | 68K | new repo | non-core platform/research repo |
| temporal_memory | 28K | new repo | non-core platform/research repo |
| temporal_memory.ex | 4K | new repo | non-core platform/research repo |
| trimtab | 120K | new repo | non-core platform/research repo |
| tunnel | 32K | new repo | non-core platform/research repo |
| ultracode | 2000K | new repo | ultracode-runtime repo (lease/dispatch kernel, 44k LOC) |
| ultracode.ex | 4K | new repo | ultracode-runtime repo (lease/dispatch kernel, 44k LOC) |
| vault.ex | 4K | KEEP | shared infra for new backend (platform) |
| witness | 32K | new repo | non-core platform/research repo |
| witness.ex | 4K | new repo | non-core platform/research repo |
| workbench | 8K | new repo | non-core platform/research repo |
| zoe | 52K | new repo | non-core platform/research repo |

## Cross-domain alias scan (keep-list -> non-core)

Counts from grep of `Xaas.<Module>` in keep-list dirs:

| from | to | count | disposition |
|---|---|---|---|
| serv_engine | Ocel | 16 | port OCEL emit behind a port or move ocel with core |
| billing | Governance | 23 | blocker: move governance subset to core or abstract |
| billing | Ultracode | 2 | cut alias |
| accounts | Governance | 1 | cut or port |
| accounts | Marketplace | 3 | cut or port |
| platform | Governance | 6 | blocker as billing |
| operations | Semantics | 15 | decide with KEEP-CHECK |
| operations | Governance | 12 | decide with KEEP-CHECK |
| operations | Castle | 3 | decide |
| operations | Witness | 2 | decide |
| library | Governance | 1 | decide |

procurement, security, ledger: zero such aliases.

## See Also

scope-decisions.md · side-effects.md · ../tickets/T-034-non-core-domain-retirement-manifest.md
