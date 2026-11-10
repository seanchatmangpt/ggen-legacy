# CHARTER

Standing: PARTIAL

Subject: switch srve from ~/xaas (Ash, :4000) to a ggen-reconstituted backend with one CLI
(`ggen-create cutover plan|power|verify|rollback`). Tickets T-001..T-036 (INDEX.md).
Claim ceiling DOCUMENTED, tooling TESTED. `release_admitted` and `sunset_admitted` are false
(authority/v26.11.9/); nothing here retires ~/xaas or onengine-backend. As-of 2026-11-10.

## What exists and what was run

- `ggen-create cutover` (ggen-create docs/CUTOVER.md): plan, power, verify, rollback and a
  read-only `dryrun`. Unit-tested in tempdirs, including a byte-exact power/rollback round trip,
  refusal on drift, all-or-nothing flip and receipt-chain verification after a failed power.
- Dry-run on the real home (receipts/dry-run-latest.json): verdict NOT_READY. The tickets
  whose deliverables live in ggen-create and ggen-legacy score PASS_PREDICTED except T-031, whose
  scratch-run clause stays UNVERIFIED. Tickets that need srve/xaas work FAIL because that work
  was built only in a scratch tree and is not applied to srve.
- Scratch-tree build of the srve-side work (not in this repo): 21 of 36 tickets scored
  PASS_PREDICTED there; ontology semantics, backend pack skeleton, ETL changes, courts and kind
  scripts. T-007 and T-022 failed, and every T1/T2 clause was UNVERIFIED.
- Manifests under manifests/ are derived by scripts/dryrun/ from exact-SHA `git archive`
  extractions and carry `source_shas`; `scripts/dryrun/refresh_manifests.sh` regenerates them.
  They go stale when a source repo moves; the dry-run `fresh` clause reports that.

## Measured values (re-derive before citing; figures differ by commit)

- xaas d7e38a37: 67 AshPostgres resources, 289 actions (74 create, 97 update, 87 read, 19
  destroy, 12 generic), 162 migrations, 66 srve_* tables by replay. The working tree of ~/xaas
  carries more (uncommitted resources and migrations: 73 tables, 166 migrations).
- onengine-backend e78330aa: 840 route registrations, 237 Prisma models, 45 canonical classes.
- call-register.json: 629 rows (600 http, 20 rpc, 5 transport, 4 wrapper); the 290-generated
  figure is a summary field, not a row count. ontology work-order transitions: 48; Ash
  `transition(` entries in work_order.ex: 11 (a real parity gap, T-007).

## Decisions open (not blocking ticket start)

- D1 runtime: generated Ash on the BEAM is the only existing pack path; TypeScript needs packs.
- D2 location of the generated backend. D3 session shim vs token migration. D4 procurement scope.

## Incidents and limits

- A dry-run clause once executed ~/srve/bin/golden-court for real (it lacked the --backend flag
  and ran its seed/court steps against the xaas test database, MIX_ENV=test). Fixed: the dry-run
  now executes no repository script; only `bash -n` and a Python syntax parse are allowlisted.
- The census replay (ddl-census.json) uses a translator stub, not xaas's own migrator, so
  agreement with a real xaas database is UNVERIFIED.
- The dry-run report is not a dfcm v2 receipt (that shape needs work-order and provider fields).

## See Also

INDEX.md · DEPENDENCY-GRAPH.md · ggen-create docs/CUTOVER.md ·
~/srve/docs/plan/25-ecosystem-reconstitution-case-study.md
