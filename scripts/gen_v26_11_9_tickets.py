"""Generate the v26.11.9 tickets, INDEX and DEPENDENCY-GRAPH.

Usage: python3 scripts/gen_v26_11_9_tickets.py   then   scripts/add_dryrun_sections.py
Env DRYRUN_REPORT=<json from `ggen-create cutover dryrun`> adds the current dry-run standing
to INDEX.md. Counts quoted in ticket text are measured values with their source SHA; the
manifests under docs/jira/v26.11.9/manifests/ are the derivations of record.
"""
import json, os, textwrap
from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "docs/jira/v26.11.9")
S="~/srve"; X="~/xaas (read-only reference)"; GC="~/ggen-create"; GL="~/ggen-legacy"
T=[]
def t(n,slug,title,wave,deps,repo,scope,acc,gates,fals,src):
    T.append(dict(n=n,slug=slug,title=title,wave=wave,deps=deps,repo=repo,scope=scope,acc=acc,gates=gates,fals=fals,src=src))

# ---- W0 foundation
t(1,"cutover-cli-skeleton","cutover CLI skeleton: plan, power, verify, rollback","W0",[],GC,
 "Add four skills to ggen-create SKILLS: cutover.plan (CONSTRUCT), cutover.power (DO_INTENT, confirm, no session), cutover.verify (SELECT), cutover.rollback (DO_INTENT, confirm). Dispatch branches lazy-import a new cutover.py. Add argparse `cutover` subcommands and an elif in run(). Base is ggen-create's Broker (digest-sealed intent, hash-chained ReceiptStore), not a new Rust CLI; osx-clnr is the structural reference only. `just cutover` in srve is a one-line alias.",
 ["`ggen-create skills list` shows the four cutover.* skills with the stated authority and confirm flags.","`cutover power` without --confirm exits with ACTUATION_CONFIRMATION_REQUIRED_REFUSED.","plan run twice on the same subject yields byte-identical JSON and touches no file outside output_root."],
 ["cd ~/ggen-create && python3 -m unittest tests/test_cutover.py","cd ~/ggen-create && ggen-create --json skills list | grep -c cutover"],
 "power runs with the confirm gate removed, or plan output differs between two runs.","L11, L18")
t(2,"cutover-receipt-and-sunset-schema","Cutover receipt chain and sunset-admission schema","W0",[1],GL+" schemas/ + "+GC,
 "Extend schemas/sunset-admission.schema.json (today only schema/admitted/state) with predecessor SHA, release-admission ref, replay digest and authorization-receipt ref. Two receipt shapes exist and are not interchangeable: the cutover receipt follows ~/.claude/dfcm/receipt.schema.json v2 (identity.subject_sha, subject_before/after sha256, replay.commands with output_sha256, standing with broken_term on REFUSED/BLOCKED/UNSUPPORTED, plus a provider_ext block holding the lock_content_root root, the ggen portable_receipt digest and the old backend's last SHA); the xaas predecessor receipt used for sunset follows ggen.legacy.receipt.v1. Cutover receipts chain through ReceiptStore; failures write BLOCKED receipts. Byte-replay: regenerate from clean state, recompute lock_content_root (ggen-ecosystem scripts/lock_content_root.py --check) and pack_digest, require equality, else REFUSED(code). Rollback emits a mirror receipt linked via predecessor_work_order_ids. See T-035 for the retirement gate.",
 ["A sunset payload missing any of the four new fields fails schema validation.","Flipping one byte in a generated file makes the replay verifier report REFUSED, not ALIVE.","`ggen-create receipt chain` passes after plan, power, verify, rollback; a failed phase leaves a BLOCKED receipt.","Receipts carry the five fields identity/authority/consequence/replay/standing."],
 ["cd ~/ggen-legacy && python3 -c \"import json,jsonschema\"  # schema loads","cd ~/ggen-create && ggen-create --json receipt chain"],
 "A payload without a replay digest validates, or a failed phase writes no receipt.","L10, L11, L19 (receipt lane; re-read at fill)")
t(3,"cutover-preflight-gate","Preflight gate: refuse switch unless prerequisites hold","W0",[1],GC+" + "+S,
 "cutover.plan runs a preflight and refuses (typed, with broken_term) unless: srve_* migrations applied, auth bridge (T-020) configured, KP07 shared-table tripwire green, Release Admission admitted:true, two-probe identity law passes on the candidate, and legacy write-freeze is declared.",
 ["Each unmet prerequisite maps to one typed refusal code.","With all prerequisites met preflight exits 0 and records its inputs in the plan."],
 ["cd ~/ggen-create && python3 -m unittest tests/test_cutover.py -k preflight"],
 "Preflight passes with a missing migration or with release_admitted:false.","L20, L14, L10")
t(4,"fe-single-backend-origin","Frontend: one backend-origin variable feeds every call site","W0",[],S+"/servengine-frontend",
 "Introduce one resolver (VITE_BACKEND_ORIGIN) replacing the chain VITE_XAAS_AUTH_URL / API_URL / RPC_URL / RPC_BASE_URL / VITE_BASE_URL. Remove the 8 non-test hardcoded http://localhost:4000 fallbacks (jsonApiClient.ts:29, ashRpcClient.ts:46, queries/core.ts:28, backendHealth.ts:12, dispatch-queue.queries.ts:10, XaasDemo/SurveyCaptureGrid.tsx:129, three *.court.test.ts, vite.config.ts ashAdminProxy). Courts read the origin variable. VITE_LOCAL_API_PROXY and VITE_XAAS_PROXY_URL derive from it.",
 ["`grep -rn localhost:4000 src vite.config.ts` returns no non-test hits.","Setting only the origin variable sends every request to that host (network-tab check in a court).","The *.court.test.ts files run against a second port."],
 ["cd ~/srve/servengine-frontend && grep -rn 'localhost:4000' src vite.config.ts","cd ~/srve/servengine-frontend && npx tsc --noEmit"],
 "A request still reaches another host after only the origin variable changes.","L12")
t(5,"ontology-executable-action-semantics","Ontology: executable action semantics on sv:Action","W0",[],S+"/ontology",
 "servengine-current.ttl models 459 actions but carries no executable semantics (guard on 1 action; sv:Policy has no expressions; no validations, changes, calculations, identities, invariants). Add machine-readable predicates for guard, validation, change, policy expression, actor role, side effect; extend servengine-current.shacl.ttl so an action missing them fails. Domain-data shapes, not only ontology-shape checks.",
 ["SHACL fails on any sv:Action lacking guard/validation/change/policy predicates (or an explicit `none`).","Counts re-derived by SPARQL, not recalled."],
 ["cd ~/srve && ggen sync run --dry-run","cd ~/srve && python3 scripts/check-cardinality.py"],
 "An Ash action with a validate or change that the ontology lacks passes SHACL.","L08, L01")
t(6,"ontology-align-one-sv-and-verify-current","Align one: and sv:; verify against introspection","W0",[5],S+"/ontology",
 "Add the missing one:-to-sv: alignment (class, property, enum). Verify servengine-current.ttl (regex-derived, UNVERIFIED) against Ash introspection of the pinned xaas SHA f0154ac1 so counts (recorded as 311 vs 459 actions) agree; remove UNVERIFIED only on a receipt.",
 ["SPARQL reports zero unmapped one:CanonicalProperty and zero unmapped statuses.","Introspection counts equal ontology counts for resources, actions, policies, enums."],
 ["cd ~/srve && ggen sync run --dry-run"],
 "A canonical property with no sv:Attribute counterpart, or any count mismatch against introspection.","L08, L05, L01")
t(7,"wo-transitions-guarded","Work-order state machine: 48 transitions as guarded, queryable facts","W0",[5],S+"/ontology + queries",
 "work-order-lifecycle.ttl holds 48 one:transition triples with free-text evidence; sv: holds 11. Reify each with machine-readable guard, actor role and side effect; extend queries/wo-transitions.rq. Visit and proposal guards (visit_status_transition_guard, proposal_status_guard, client_update_status_guard) are modeled the same way or listed as residue (T-008).",
 ["48/48/48 agreement across legacy FSM, ontology and Ash transition list.","No guard exists only inside rdfs:comment text."],
 ["cd ~/srve && ggen sync run --dry-run"],
 "A transition with its guard only in comment text, or a legal/illegal edge accepted/rejected differently.","L08, L01, L07")
t(8,"resource-classification-manifest","Manifest: every Ash resource and action tagged generated vs residue","W0",[6],S+"/ontology + docs",
 "Produce a derived manifest of every AshPostgres resource (67 at xaas d7e38a37; the working tree carries more uncommitted ones) and every action, tagged generated or custom-handler, with the grep derivation commands recorded in the file head (CONTRACT.md pattern). Tag totals must equal the totals recorded in the manifest derivation (74 create, 97 update, 87 read, 19 destroy, 12 generic at xaas d7e38a37).",
 ["Every resource and action has exactly one tag.","Tag totals equal derivation-command totals."],
 ["cd ~/xaas && grep -rl 'data_layer: AshPostgres' lib/xaas/serv_engine | wc -l"],
 "A resource or action found in xaas with no tag.","L01")
t(9,"onengine-route-inventory","Route inventory extractor and OpenAPI reconciliation for onengine-backend","W0",[],S+"/onengine-backend (read-only) + scripts",
 "Emit a machine-readable inventory (method, path, module, auth middleware, controller) for every route registration (840 at onengine-backend e78330aa, router.<verb>, public and app variants). Reconcile against swagger/output/openapi.yaml (148 paths, 185 verbs, about a fifth of the routes) and apiDefinition/. The inventory is the legacy half of parity; onengine-backend is not edited.",
 ["Inventory count equals the derivation grep count exactly.","A diff lists every undocumented route."],
 ["cd ~/srve/onengine-backend && grep -rEc 'router\\.(get|post|put|patch|delete)\\(' src/modules | awk -F: '{s+=$2} END{print s}'"],
 "A route registered in the Express app but absent from the inventory.","L06")
t(10,"fe-called-action-scope","Cutover scope: actions and prefixes the frontend actually calls","W0",[],S+"/servengine-frontend",
 "From src/lib/xaas/__register__/call-register.json (rows split by kind; the 290-generated figure is a summary field, the rows hold about 20 RPC entries) and the /api/* prefix census, produce the authoritative cutover-scope file: domains, RPC actions, REST prefixes. Everything outside it is non-scope (T-035). Prefix to controller mapping is traced, not inferred from names.",
 ["Scope file lists each called action and prefix with its owning domain.","Every prefix in src/ appears in the file."],
 ["cd ~/srve/servengine-frontend && jq '.rows | length' src/lib/xaas/__register__/call-register.json"],
 "A prefix or RPC action called by the FE is missing from the scope file.","L02, L16, L12")
t(11,"srve-ddl-census-and-replay-diff","srve_* DDL census and replay-diff harness","W0",[],S,
 "Census final-state DDL of every srve_* table (66 at xaas d7e38a37 from 162 committed migrations; the working tree adds uncommitted migrations) plus resource_snapshots (56 srve entries; not sole source). Build a harness comparing pg_dump --schema-only of generated SQL against the xaas-migrated DB: columns, types, defaults, NOT NULL, FKs, Ash-named indexes, raw execute() alterations (srve_notes.work_order_id nullability).",
 ["Census lists every table with columns; count reconciles with migrations grep.","Harness diff is empty on the xaas DB compared with itself and non-empty on a mutated fixture."],
 ["cd ~/xaas && grep -rhoE 'create table\\(:srve_[a-z_0-9]+' priv/repo/migrations | sort -u | wc -l"],
 "A table in migrations missing from the census, or an injected column change not flagged.","L04")
t(12,"shared-table-tripwire-extension","Extend shared-table tripwire from 13 to all srve_* tables","W0",[11],S+"/onengine-backend (test only)",
 "src/xaas-contract EXPECTED_SHARED_TABLES covers the original 13; 60 srve_* tables are unguarded. Extend the contract test to every table with its owning resource. Prisma stays unmodeled for srve_*.",
 ["Contract test names every census table.","Adding a table without an entry fails the test."],
 ["cd ~/srve/onengine-backend && npx jest __tests__/sharedTables.contract.test.ts"],
 "A table added in xaas with no test entry still passes.","L04, L06")
t(13,"prisma-model-coverage-and-tenant-policy","Prisma model coverage manifest and tenant-key policy","W0",[6],S+"/ontology + docs",
 "Classify all 237 models (re-derive; count recorded in the manifest) as canonical, tenant-only, legacy or unmapped against canonical.ttl (45 classes carry an aggregate) and the four aggregates in docs/plan/12. State tenant-keyed vs global per class (suppliers are global after migration 20260715173000; canonical.ttl:208 keeps per-tenant WO numbers). Generated code enforces the policy.",
 ["No model unclassified; every one: class has a backing model.","Per-class tenant policy table matches generated DDL."],
 ["cd ~/srve/onengine-backend && grep -c '^model ' prisma/schema.prisma"],
 "Generated code tenant-scopes a global supplier or leaves a tenant-keyed class unscoped.","L05")
t(14,"procurement-dispatch-scope-decision","Decision: procurement, dispatch, forms, W9 scope","W0",[10,13],S+"/docs",
 "Procurement (40k lines, 160 routes, 17.6k-line service.ts, external flight/part/email/quotation integrations), dispatcher/sweep/ranking tables and form builder have no one: class. Record per area: in-scope with ontology classes added, ported behind ports, or out-of-scope with explicit UNSUPPORTED row. Cutover refuses to route a table with no owner.",
 ["Every area has a recorded disposition and owner.","Integration helpers are isolated behind ports for any in-scope area."],
 ["cd ~/srve && grep -c 'procurement' ontology/procurement.ttl"],
 "A procurement route routed by the cutover with no recorded owner.","L05, L06, L16")

# ---- W1 construct
t(15,"pack-resources-from-ontology","Backend pack: generate resources from the srve ontology","W1",[5,6,8],S+"/packs/srve-backend-pack (new)",
 "Pack modeled on ggen-docs-reconstitution-pack and reusing xaas-ash-core-pack + canonical-ash-projection-generator from ggen-marketplace. Existing packs emit shell commands and semantic-map TTL, not resource source, so add templates that render attributes, relationships, identities and code interfaces. Decision D1 (CHARTER): generated Ash on the BEAM is the only existing pack path; a TypeScript target needs new packs.",
 ["`ggen sync run` emits one resource per srve entity; command count equals entity count.","Second sync is byte-stable.","Output compiles with no hand edit."],
 ["cd ~/srve && ggen sync run --dry-run && ggen sync run && ggen sync run && git status --short packs generated"],
 "Emitted source needs a hand edit to compile, or the second sync differs.","L09, L01, L08")
t(16,"pack-migrations-ddl","Backend pack: migrations that replay to byte-equivalent DDL","W1",[11,15],S+"/packs/srve-backend-pack",
 "Generate the migration chain (including execute() alterations and updated_at backfill order) so the pack owns the srve_* chain instead of xaas. Both backends must never run migrations against the same DB (schema_migrations conflict): the cutover hands ownership over once.",
 ["T-011 harness diff is empty against the xaas-migrated DB.","schema_migrations ownership recorded in the cutover plan."],
 ["cd ~/srve && ./scripts/ddl_replay_diff.sh"],
 "Two backends run migrations on one DB, or any column default/index name differs.","L04, L09")
t(17,"pack-router-and-rpc-envelope","Backend pack: router and RPC envelope parity","W1",[10,15],S+"/packs/srve-backend-pack",
 "Generate POST /internal-api/rpc/run and /rpc/validate for every RPC action in the cutover scope manifest with {success,data|errors} kept on 400/401; rpc routes declared before any catch-all forward; typed 400 on malformed fields spec (validate_rpc_fields); interpolated error handler parity; bearer plus X-Tenant-Id and acting-entity-id handling; CORS OPTIONS 204.",
 ["Every in-scope RPC action returns the envelope shape; 400/401 keep it.","Malformed fields returns typed 400, never 500.","rpc/run never returns no_route_found."],
 ["cd ~/srve/servengine-frontend && XAAS_TEST_URL=$CANDIDATE npx vitest run --config vitest.process.config.ts"],
 "Any action returns non-JSON or a bare error body.","L02")
t(18,"pack-policies-and-parity-matrix","Backend pack: policies with an allow/deny parity matrix","W1",[5,15],S+"/packs/srve-backend-pack",
 "71 serv_engine files use Ash.Policy.Authorizer. Generate policies from sv:Policy expressions (T-005) and prove them with an actor x tenant x action allow/deny matrix captured from xaas and replayed on the candidate.",
 ["Matrix identical on tenant isolation and role cases.","Masked money fields null, never 0."],
 ["cd ~/srve && ./scripts/policy_matrix_diff.sh"],
 "Any tenant-isolation or role case diverges.","L01, L03")
t(19,"residue-custom-handlers","Custom handlers for ontology-inexpressible logic","W1",[8,15],S+"/packs/srve-backend-pack (cnv:CustomBehavior)",
 "Port as registered handlers: the ~19 operations/changes (nte_guard, quote_margin_guard, acceptance_token_guard, assign_provider_guard, check_in_out_guard, close_out_invoice_paid_guard, intake, convert_to_project, generate_proposal, auto_dispatch, place_dial_call, transmit_client_update, ...), commercial changes and w9 campaign changes, alignment_matcher (247 LOC), auto_dispatch (215), htn_planner/dynamic_planner (321), IngestAndMatchReactor, telephony/client_update/proposal_generator/site_enrichment adapters (contract declared, impl stubbed). Handwritten residue listed as UNSUPPORTED rows until ported.",
 ["Each handler is registered and invoked from its generated action.","Residue table lists every unported handler as UNSUPPORTED."],
 ["cd ~/srve && ./scripts/handler_registry_check.sh"],
 "A generated action runs without invoking its handler.","L01")
t(20,"auth-session-bridge","Auth and session bridge","W1",[17],S+"/packs/srve-backend-pack",
 "xaas is token-based (AshAuthentication, bcrypt, magic-link, TokenResource revocation); legacy is an opaque session-id in a DynamoDB row with codes NO_SESSION_ID/INVALID_SESSION/SESSION_EXPIRED/SESSION_REVOKED. Decide shim vs move clients to tokens, then implement. Cover the 21 parity cases: roleScope both and 403 SWITCH_REQUIRED, entity-login permission rows, acting-entity cross-tenant 403 with super-admin scope all, fail-closed money writes, 401-first for empty envelopes, impersonation write authority. Revoked/expired short-circuit with no IdP call.",
 ["21 cases replayed against the candidate with identical status and code.","Revoked session rejected with network blocked.","Rollback expires bridged sessions cleanly."],
 ["cd ~/srve && ./scripts/auth_parity_cases.sh"],
 "A servengine-only role gets 200 at an entity login, or switching forces a global logout.","L03, L20")
t(21,"health-two-probe-and-cors","Two-probe identity law and CORS on the candidate","W1",[17],S+"/packs/srve-backend-pack",
 "GET /health returns 200 unauthenticated with no DB access; unauthenticated GET /api/health returns 401 'missing or invalid Bearer token'; /internal-api/health token-gated; OPTIONS preflight 204. The probe must reject wrong servers (ForeignBackendError class).",
 ["Probe passes on the candidate and refuses a stub that serves /api/health 200."],
 ["cd ~/srve/servengine-frontend && XAAS_TEST_URL=$CANDIDATE npx playwright test --project=chromium-desktop \\\n  playwright/globalSetup-tony.ts"],
 "/api/health returns 200 with no token, or OPTIONS /health returns 404.","L02, L13")
t(22,"generated-contracts-and-openapi","Contracts and OpenAPI generated from the backend schema","W1",[9,15],S+"/servengine-frontend/packages/contracts",
 "Hand-written packages/contracts (schemas.ts, woStatus.ts, woTransitions.ts) is deleted in favor of generated output; regenerate src/contracts/xaas-generated/{ash_rpc,ash_types,ash_zod}.ts from the candidate. Emit OpenAPI covering 100% of the T-009 inventory (legacy covers ~21%). ash_typescript/ash_surface are unverified candidates; confirm the emitting mix task on a fixture first.",
 ["Backend schema change changes contracts output.","OpenAPI diff versus inventory is empty."],
 ["cd ~/srve && ggen sync run && git status --short servengine-frontend/packages/contracts"],
 "A backend schema change does not change the contracts output.","L12, L06, L09")
t(23,"etl-write-path-and-vocab","ETL: verify the write path and reconcile status vocabularies","W1",[11],S+"/scripts/etl",
 "etl.ts (848 lines, 10 aggregates, PARTIAL_ALIVE) has only a verified dry run. Run the real write into a scratch DB with per-aggregate src/dst count and checksum. Reconcile vocabularies in one table (WO 23 mapped keys to 8 atoms; 25 DB rows vs 29 enum constants unreconciled; invoice 5 keys; SP 3 keys): every legacy value mapped or rejected, no silent fallback to draft/onboarding. Add DDL preflight gate and PRESERVATION_MAP (planned, not in etl.ts).",
 ["Second run changes neither row count nor checksum.","unmapped* is empty on a real dump; fallbacks fail loudly."],
 ["cd ~/srve/scripts/etl && npx tsx etl.ts --dry-run"],
 "A second run changes counts, or any fallback is hit silently.","L07, L20")
t(24,"etl-extended-aggregates","ETL: extend to the ~35 aggregates and backfill post-ETL fields","W1",[23,16],S+"/scripts/etl",
 "Implement docs/plan/21 wave by wave (about 35 aggregates, 15 vocabulary maps) behind the DM migration waves. Aggregates without target DDL are skipped with warning. Backfill what ETL cannot write: srve_tenants.org_id, derived SP caches, overdue status, note authors.",
 ["Each aggregate ships with map, checksum and spot-check.","Post-ETL fields non-NULL after the backfill step."],
 ["cd ~/srve/scripts/etl && npx tsx etl.ts --dry-run --all"],
 "An aggregate with no target DDL fails the run instead of skipping.","L07")

# ---- W2 verify
t(25,"http-golden-court","HTTP golden court ported from the Elixir courts","W2",[17,18],S+"/servengine-frontend/playwright + vitest",
 "Restate golden_lifecycle_court_test.exs (ingest to invoice, NTE refusal, 7 OCEL events, cross-tenant invoice masking) and golden_saga_replay_court over HTTP only, driven by XAAS_TEST_URL. Extract the HTTP contract from the route census and ConnCase wire courts (json_api_route_census, entity_surface_rpc, cors, correlation_id, clients_tenant_scope).",
 ["Passes against ~/xaas :4000 and the candidate; fails against a stub backend."],
 ["cd ~/srve/servengine-frontend && XAAS_TEST_URL=http://localhost:4000 npx vitest run golden"],
 "The court passes against a stub backend.","L13")
t(26,"backend-neutral-seed","Backend-neutral seed fixture","W2",[17],S+"/scripts",
 "Replace `mix run priv/repo/seeds/golden_amc_work_order.exs` with an HTTP/JSON fixture loader (wo-cycle/00-seed-xaas.client.ts is the seed idiom; dev_seed_controller exists in xaas).",
 ["Same fixture seeds two backends to identical readbacks."],
 ["cd ~/srve && ./scripts/seed_fixture.sh $URL"],
 "Omitting a fixture field is not detected by the readback diff.","L13")
t(27,"golden-court-backend-flag","bin/golden-court --backend URL","W2",[25,26],S+"/bin/golden-court",
 "Add --backend: skip mix steps, run only the HTTP courts and two-probe identity. Restore src/test/realServer.ts and setup.process.ts (referenced by real-backend.yml, not found) so FE court 3 stops skipping loudly.",
 ["Dead port exits non-zero at the identity probe with no mix invoked.","fe_golden_wire prints PASS, not SKIP."],
 ["cd ~/srve && bin/golden-court --backend http://localhost:4000"],
 "fe_golden_wire still prints SKIP.","L13")
t(28,"replay-determinism","Deterministic replay: byte-stable second sync","W2",[15,16,17],GL+" + "+S,
 "Release Admission requires clean deterministic replay. Two full generate runs at the same subject produce identical output digests and identical receipt-chain head.",
 ["Two replays: identical digest set and chain head."],
 ["cd ~/srve && ggen sync run && sha256sum -r generated/* > /tmp/a && ggen sync run && sha256sum -r generated/* > /tmp/b && diff /tmp/a /tmp/b"],
 "Digests differ or replay is not clean.","L10")
t(29,"independent-verifier-and-negative-controls","Independent verifier with negative controls","W2",[25,28],GL+"/verifiers",
 "A verifier distinct from the producer runs the same request set against xaas and the candidate with equal results, and negative controls are refused. Generated output has no runtime dependency on xaas source. There is no v26.9.28 verifier today (verifiers/ holds only verify_ggen_v26_8_3.py).",
 ["Equal results on the request set; each negative control refused.","Producer output is never its own verifier."],
 ["cd ~/ggen-legacy && python3 verifiers/verify_srve_cutover.py --subject $SHA"],
 "The producer's own output is the only verifier, or a negative control is admitted.","L10")

# ---- W3 cutover/infra
t(30,"kind-scripts-parametrize-backend","Parametrize kind scripts, align Postgres, replace asset-hash smoke","W3",[17],S+"/scripts + justfile",
 "kind-bootstrap.sh, kind_doctor.sh, kind-smoke-test.sh hardcode cluster kind-xaas, deployment xaas, image xaas:local. Accept BACKEND=ggen. Postgres: KinD uses postgres:16-alpine while compose uses pgvector/pgvector:pg15 and migrations may need the vector extension (verify). Smoke test checks hashed assets (index-DHFaKXPx.js); replace with one API route plus a DB query, assets discovered not hardcoded. `just cutover backend=<xaas|ggen>` recipe.",
 ["grep for xaas:local and deployment/xaas in scripts/kind* returns nothing.","Smoke fails against a dead backend and passes after an FE rebuild."],
 ["cd ~/srve && grep -n 'xaas:local\\|deployment/xaas' scripts/kind*"],
 "A frontend rebuild breaks the smoke test.","L14")
t(31,"freeze-delta-switch-rollback","Write freeze, delta sync, atomic switch, rollback","W3",[3,23,32],GC+" + "+S,
 "cutover.power sequence: legacy write-freeze, final delta ETL to zero diff, flip origin (T-004) and per-family VITE_XAAS_FAMILY_* flags, verify, sign-off gate. cutover.rollback restores xaas as active in one command. Irreversible: writes accepted on srve_* (needs reverse ETL or freeze), session format switch (users re-login), legacy table drops and decommission (deferred entirely), notification/email sends. Rollback must leave no rows written only to the new store.",
 ["Rollback restores a working :4000 xaas and zero rows exist only in the new store.","Power refuses when freeze not declared."],
 ["cd ~/ggen-create && ggen-create cutover plan --dry-run"],
 "Rollback leaves rows written only to the new backend.","L20, L11")
t(32,"side-effect-inventory","Side-effect inventory with cutover behavior","W3",[10],S+"/docs",
 "Name an owner and cutover behavior (pause, drain, dual-send) for S3 presign (B13 unported), email/notifications, Oban poll jobs, Reactor sagas (RFC-0042), Sentry, DynamoDB sessions, in-flight work orders. DynamoDB/Sentry/tenant_id-drop risks were not confirmed in any read doc: mark UNVERIFIED until grepped.",
 ["Every side effect has an owner and behavior; unverified items marked UNVERIFIED."],
 ["cd ~/srve && grep -rln 'dynamodb\\|sentry' docs servengine-frontend/src | head"],
 "Duplicate emails sent or in-flight jobs lost on a rehearsal.","L20")
t(33,"downstream-parity","Downstream parity: receipts, OCEL ndjson, pins","W3",[28],S+" + ~/zoela + ~/chatman-ecosystem",
 "No other repo calls :4000 at runtime. Contract surfaces: ggen_igniter receipt_from_xaas must parse candidate receipts; gymact castle_feed (parse_xaas_ndjson) must pass test_castle_feed.py on candidate OCEL ndjson; zoela target-architecture.md pin xaas/main@42fd0ce and chatman-ecosystem release.ttl must be refreshed post-cutover; cmms census packs xaas-ash-core / xaas-castle-bridge inventoried; confirm xaas path deps on ggen_igniter/ash_a2a unchanged.",
 ["Candidate receipts parse; gymact test passes; stale pins named in the plan."],
 ["cd ~/gymact && python3 -m pytest tests/test_castle_feed.py"],
 "A receipt or ndjson line from the candidate fails its downstream parser.","L15")
t(34,"non-core-domain-retirement-manifest","Retirement manifest for xaas non-core domains","W3",[10],S+"/docs",
 "Assign each lib/xaas directory an owner (repo, new repo, drop): ultracode (44k LOC), governance (7.2k), semantics, sjira, sa2a/a2a, zoe, gall, witness/ocel/receipt group, marketplace, conference, research dirs. Keep list: serv_engine, procurement, billing, accounts, platform, security, ledger (into billing); operations and library need a check. Cross-domain scan: any alias from keep-list modules into non-core modules.",
 ["Every directory has an owner.","Scan lists keep-list to non-core aliases with disposition."],
 ["cd ~/xaas && ls lib/xaas | wc -l"],
 "A lib/xaas directory has no owner, or a keep-list module aliases a dropped domain.","L16, L15")
t(35,"sunset-admission-separate-actuation","Sunset admission is a separate authorized actuation","W3",[2,28,29],GL,
 "Switch-over is not retirement. cutover never deletes, archives or decommissions ~/xaas or onengine-backend. Sunset needs its own exact predecessor receipt (ggen.legacy.receipt.v1 with ALIVE standing for xaas at an exact SHA, covering every endpoint srve calls), Release Admission admitted:true, independent verification (T-029), and a separate receipted authorization. Retirement emits a TOMBSTONES file in the gym-ecosystem gitgym-removal-20260903.md shape (old SHA, claimed vs observed role, evidence commands with captured output that were actually run); foundry/bootstrap.yaml shows the nonclaims pattern (standing_transferred:false).",
 ["cutover source contains no delete/archive path for xaas.","Sunset refuses while release_admitted:false."],
 ["cd ~/ggen-create && grep -rn 'rmtree\\|unlink' src/ggen_create/cutover.py"],
 "The switchover command touches or deletes ~/xaas, or sunset admits with release_admitted:false.","L10, L19")
t(36,"doctrine-and-memory-updates","Update backend-law rule, memory and srve README after cutover","W3",[31],"~/.claude + "+S,
 "xaas-servengine-backend-law (xaas sole backend, :3002 forbidden) contradicts the operator's 2026-11-09 direction; rewrite it for the new backend identity. Update the srve memory file and srve README boot order (xaas Postgres/mix/phx.server). Only after T-031 passes.",
 ["Rule, memory and README name the new backend; no rule requires xaas."],
 ["grep -rn 'xaas' ~/.claude/rules/xaas-servengine-backend-law.md"],
 "A rule still requires :4000 xaas after cutover.","L12, L14")

def fold(cmd):
    out, cur = [], cmd
    while len(cur) > 98:
        i = cur[5:98].rfind(' && ')
        if i < 0:
            break
        i += 5
        out.append(cur[:i] + ' \\')
        cur = '  && ' + cur[i + 4:]
    out.append(cur)
    return "\n".join(out)


def wrap(s,ind=""):
    return "\n".join(textwrap.wrap(s,98,initial_indent=ind,subsequent_indent=ind))
def bl(x): return "\n".join(textwrap.fill(i,98,initial_indent="- ",subsequent_indent="  ") for i in x)
for k in T:
    fn=f"T-{k['n']:03d}-{k['slug']}.md"
    deps=", ".join(f"T-{d:03d}" for d in k['deps']) or "none"
    body=f"""# T{k['n']:03d} — {k['title']}

Standing: REGISTERED

Wave: {k['wave']} · Depends on: {deps}
Owned paths: {k['repo']}
Research lanes: {k['src']}

## Scope

{wrap(k['scope'])}

## Acceptance

{bl(k['acc'])}

## Gates (verbatim, not yet run)

```bash
{chr(10).join(fold(g) for g in k['gates'])}
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t{k['n']:03d}-{k['slug']}.md (under docs/jira/v26.11.9/)
{wrap('Falsifier: '+k['fals'])}

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
"""
    open(f"{D}/tickets/{fn}","w").write(body)
# INDEX + DEPENDENCY GRAPH
standing = {}
report = os.environ.get("DRYRUN_REPORT")
if report and Path(report).is_file():
    data = json.loads(Path(report).read_text())
    standing = {t["ticket"]: (t["tier"], t["standing"]) for t in data["tickets"]}
idx=["# INDEX","","Standing: REGISTERED","",
     "Entry format: ticket, wave, tier, dry-run standing (`ggen-create cutover dryrun`,",
     "receipts/; blank = no report), title, dependencies.",""]
for k in T:
    tier, st = standing.get("T-%03d" % k['n'], ("", ""))
    deps = ", ".join("T-%03d" % d for d in k['deps']) or "none"
    head = f"- T-{k['n']:03d} [{k['wave']} {tier} {st}] {k['title']} (needs: {deps})"
    idx.append(textwrap.fill(" ".join(head.split()), 98, subsequent_indent="  "))
idx+=["","## See Also","","CHARTER.md · DEPENDENCY-GRAPH.md",""]
open(f"{D}/INDEX.md","w").write("\n".join(idx))
g=["# DEPENDENCY-GRAPH","","Standing: REGISTERED","","```mermaid","graph LR"]
for k in T:
    for d in k['deps']: g.append(f"  T{d:03d} --> T{k['n']:03d}")
g+=["```","","## See Also","","INDEX.md",""]
open(f"{D}/DEPENDENCY-GRAPH.md","w").write("\n".join(g))
print(len(T),"tickets")
