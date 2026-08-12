# Enterprise Architecture Foundry — Completion ARD (Workstreams C–K)

Architecture requirements for closing the gap named in the
[Completion PRD](15-foundry-completion-prd.md). Each section names the real
verifier binary in `~/ggen/tools/architecture-foundry/src/bin/`, the real
refusal codes it can return (read directly from its source this session),
and what is and is not yet known about whether its real evidence exists.
Nothing here pre-guesses an answer a real investigation hasn't produced.

## C — Capability admission (`admit_capabilities.rs`)

**Real, `ADMITTED`.** Both `DISPOSITION_UNKNOWN` capabilities resolved
against `~/ggen`'s real current source (see PRD), on a new commit
(`b7db94e8e`, branch `agent/v26.8.1-resolve-2-dispositions`) — not by
editing the corpus's transcription. Re-running `admit_capabilities` after
re-admitting B against that corrected evidence: all 65 capabilities
admitted, `unknown_capabilities: 0`,
`disposition_counts: {ARCHIVED: 36, REFUSED: 12, REPLACED: 9, SUBSUMED: 8}`,
every predicate true (`no_capability_property_empty`,
`no_replacement_owner_missing`, `no_turtle_string_unterminated`,
`no_unknown_disposition`, `workstream_b_admitted`).

**Architecture lesson, real and load-bearing for D–K**: `admit_observation`
writes evidence into the corpus via `write_new` — a byte-for-byte `git show`
of the real source commit, receipted with a BLAKE3 digest. It is not an
editable document. A first attempt to fix the two capabilities by directly
editing `foundry/evidence/B/legacy-capabilities.ttl` in the corpus was
correctly refused downstream by `admit_capabilities` itself
(`RECEIPT_OUTPUT_DRIFT: expected <old digest>, observed <new digest>`) —
proof the digest chain actually catches tampering, not just schema gaps.
The real fix required: (1) making the correction at the actual source path
in `~/ggen`, on a new commit; (2) retracting B's stale admission (deleting
its generated outputs, resetting `state.json`'s B entry to `READY`); (3)
re-running `admit_observation` with `--evidence-ref` pointed at the new
commit; (4) only then re-running `admit_capabilities`. Any future
correction to already-admitted evidence for D–K must follow this same
path — fix at the source, retract, re-admit — never hand-edit a corpus
artifact directly.

## D — Kernel-corpus classification (`admit_classification.rs`)

**Real, `ADMITTED`.** `classify()`'s match arms cover exactly the four
real disposition values C's catalog contains
(`REPLACED`/`SUBSUMED`/`REFUSED`/`ARCHIVED`) — self-feeding from C's real
output, no new evidence needed. 65/65 classified, zero unclassified, zero
conflicts: `CORPUS_ARCHIVE: 36, CORPUS_HISTORICAL_IMPLEMENTATION: 17,
CORPUS_REFUSAL_WITNESS: 12`.

**Real tool bug found and fixed to get here**: `replay_all_receipts`
(`tools/architecture-foundry/src/lib.rs`) checked every historical
receipt's output digests independently against current corpus state.
`initialize-corpus` seeds `foundry/catalogs/capabilities.json` with an
empty digest, receipted in `initialization.json`; C legitimately replaces
that file with real content via `write_replace`, recording the new digest
in its own receipt. The old logic still checked `initialization.json`'s
stale expectation too — `RECEIPT_OUTPUT_DRIFT`, permanently blocking
every workstream from D onward regardless of real evidence. Fixed: for
each output path, only the causally-latest receipt's digest is checked
(receipts processed in `sorted_files` order, which for this repo's naming
coincides with real causal order). `replay_receipt` (used by
`verify_corpus` as a diagnostic, not a gate) was deliberately left
unchanged — flagging superseded receipts there is legitimate. Fix: ggen
commit `c73619246`, branch `agent/foundry-replay-latest-receipt-per-path`,
`cargo test` (real_git suite) 4/4 before use.

## E — Cross-repository extraction (`admit_extraction.rs`)

**Real, `BLOCKED`.** Refuses `REQUIRED_SOURCE_OBJECTS_UNRESOLVED` for all
17 real `REPLACED`/`SUBSUMED` capabilities (the ones D classified
`CORPUS_HISTORICAL_IMPLEMENTATION` — only these require resolved source;
`ARCHIVED`/`REFUSED` capabilities do not).

**Real tool bug found and fixed, but insufficient alone**: the tree-entry
prefix matcher built `format!("{requested}/")` without first trimming a
trailing slash already present on directory-shaped `legacy_source_path`
values (e.g. `crates/ggen-core/`) — produced an unmatchable double-slash
pattern. Fixed with `trim_end_matches('/')` (ggen commit `5816faac7`,
same branch, `cargo test` 4/4). All 17 still failed after this fix.

**The real, remaining, per-capability blocker** — not a single bug:

- Real investigation of `legacy_ggen_core_pipeline`
  (`historical_source_commit: 9cef6e40f`) shows that commit's own message
  is *"remove ggen-core, rewrite README from first principles"* — it is
  the **removal** commit; the source content lives at its parent
  (`9cef6e40f^`). `admit_classification.rs`'s own `recovery_command()`
  already encodes this convention (`git show {commit}^:{path}`);
  `admit_extraction.rs`'s tree resolution does not apply it. This likely
  explains several (not necessarily all) of the 17 — `legacy_ggen_a2a_mcp_server`,
  `legacy_ggen_lsp_mcp_server`, and `legacy_ggen_lsp_a2a_bridge` share the
  identical commit `bde78f7d5`, suggesting the same removal-commit pattern.
- Several `legacy_source_path` values are genuinely prose, not a single
  literal git path: `` `justfile` (`sync-dry:` recipe) vs. crates/ggen-engine/src/verbs/sync.rs ``,
  `crates/ggen-config/... vs. crates/ggen-engine/src/config.rs`,
  `crates/ggen-core/src/v6/receipt.rs or its PipelineConfig owner`,
  `crates/ggen-marketplace/src/**/metadata.rs` (a glob, likely not meant
  literally given the surrounding entries are plain paths).

**Real, `ADMITTED` (closed).** Two more real tool fixes were needed, plus
real per-capability evidence corrections, after the trailing-slash fix
above didn't resolve any of the 17 on its own:

- **Generic path normalization** (`normalize_legacy_path`): extended to
  strip parenthetical annotations, take the first path of a top-level
  comma-separated list, and strip `" vs. "`/`" vs "`/`" or "`
  comparison-or-hedge markers — verified against all 17 real evidence
  strings (`git log`/`git show` per capability) before writing: every
  `"vs."` case's legacy/first side is the real target, every `"or"`
  case's first clause is the concrete confirmed path, the one comma-list
  case's first entry is real.
- **Removal-commit parent fallback**: when the direct cited commit has no
  matching tree entries, retry at its parent — confirmed correct for 6 of
  17 via direct `git log`/`git ls-tree` before adding it as a general
  rule (not a blind retry). Resolved 16 of 17.
- **Globstar (`**`) zero-directory-level matching**: the last capability's
  evidence path (`crates/ggen-marketplace/src/**/metadata.rs`) needed
  standard globstar semantics (`**/` matches zero or more path segments,
  including no subdirectory at all) — the naive two-single-star
  implementation could never match a file with zero intervening
  directories. Fixed with real, standard globstar semantics.
- **3 real evidence corrections** at the source TTL, each grounded in
  direct investigation of `~/ggen`'s actual history: `legacy_genesis_schema_v2_crate`'s
  field described a search procedure rather than its result (resolved to
  the real deletion commit `5b8dd6407`); `legacy_ext_template_mode_update`'s
  path was prose with no literal file (resolved to
  `crates/ggen-daemon/src/generator.rs`, named directly in the real
  removal commit's own message); two capabilities' `historicalSourceCommit`
  said `"UNKNOWN"` despite their own `migrationPath`/`rollbackPath` fields
  already documenting a real resolution commit that was simply never
  copied into the right field.

Real result: `admit_extraction` admitted 65/65 components,
`unresolved_required_sources: 0`, 1141 unique real git blobs recovered
(1197 total source files) from `~/ggen`'s actual history. Every fix on
ggen branch `agent/foundry-replay-latest-receipt-per-path`
(tool fixes) and `agent/v26.8.1-fix-extraction-source-paths` (evidence
fixes), all `cargo test`-verified before use.

## F, G, H — Primitive/pack/equivalence (`admit_products.rs`, 3 stages)

**Real, `ADMITTED` (all three).** Fully self-feeding from C/D/E's real
outputs — no new evidence needed for F (10 primitives, all negative
falsifiers passed) or G (8 solution packs, all falsifiers passed). H's
first attempt refused `EQUIVALENCE_ADMISSION_REFUSED` (1/65 failures):
`legacy_ext2_exit_code_mutation_budget_threshold`'s real `REFUSED`
disposition (from C's fix) was missing its companion
`refusalCode`/`refusalRationale` fields — 23 of the expected 24 (12
`REFUSED` entries × 2 fields) were present in the real TTL; this was the
missing one. Added, grounded in the same real investigation that
resolved the disposition. B through H were then retracted and re-admitted
fresh against the corrected evidence. Real result: 65/65 equivalence
cases, 0 failures, 65/65 negative falsifiers passed.

## I — Independent verification (`admit_verification.rs`)

**Real, `ADMITTED`.** Fully self-contained — 7 zero-capability subsystems'
"system evidence" derives from already-real, already-committed artifacts
(state.json, receipt files, catalogs); 8 sabotage cases each deliberately
corrupt a real receipt's output digest and confirm the verifier refuses it.

**Real tool gap found and fixed**: `foundry/receipt-ownership.json` was
required by the governance and projection subsystems' evidence check, but
nothing in the entire program ever produced it — a grep across the whole
source tree found zero producers, only the one existence check. Implemented
as a real ownership audit (not a placeholder): for every `ADMITTED`
workstream A–H, cross-checks that `state.json`'s recorded `receipt_path`
points to a real receipt whose own `subject` field matches that
workstream's id. Real result: all 10 subsystems `ALIVE`, 8/8 sabotage
cases correctly refused, `external_verifier_passes: true`.

## J — Clean-room manufacture and replay (`admit_clean_room.rs`)

**Real, `ADMITTED`.** Real double clone-and-rebuild: clones both `--source`
and `--corpus` fresh via `git clone --local`, checks out the exact expected
heads, runs a real `cargo test --all-targets` and independent
`verify_corpus`/`replay_all_receipts`, twice, and compares the two runs
for semantic determinism.

**Two real, structural fixes needed**, both deeper than a code bug:

- `foundry/receipts/` was gitignored (`bootstrap.yaml`'s own
  `generated_directories`), so a genuinely independent `git clone` — exactly
  what this workstream correctly performs — always lacked every receipt,
  and `replay_all_receipts` always refused `RECEIPT_DIRECTORY_MISSING`
  inside the clean-room clone. This wasn't a code bug, it was a real design
  contradiction: receipts are this program's durable attestation record,
  not regeneratable output. Corrected: receipts are now tracked in git.
- `verify_corpus`'s own receipt-checking still used the pre-fix,
  per-receipt-independently logic (deliberately left alone during the D fix,
  on the premise that it was "diagnostic, not gating") — but its output
  feeds this workstream's real admission gate
  (`clean_room_verification_success` requires `invalid_receipts.is_empty()`),
  so that premise was wrong for this call site. Given the same
  latest-per-path fix as `replay_all_receipts`.

Real result: both clean-room runs succeeded, `replay_differences: 0`,
`generated_drift: 0`, `NO_SEMANTIC_CHANGE`.

## K — Fortune-scale reference reconstitution (`admit_reference.rs`)

**Real, `ADMITTED`.** Fully self-contained — manufactures a real minimal
Rust crate (`Cargo.toml`/`lib.rs`/`main.rs`/`architecture.json`/
`controls.json`/`replay.json`) from the admitted
`repository_manufacturing_platform` pack's 7 real primitives, compiles and
runs `cargo test` twice, checks byte-identical stdout/stderr/output-tree
digests across both runs. No new evidence needed. Real result:
`solution_admission: true`, `replay_match: true`, both runs exit 0.

## Terminal admission (`admit_final.rs`)

**Real, `ALIVE`.** Independently recomputes the terminal theorem from
durable artifacts alone: all 11 workstreams `ADMITTED`, 65 capabilities,
zero unknowns/failures/differences across every dimension,
`fortune_scale_reference_manufactured: true`, `receipts_replayed: 12`.
`standing: ALIVE`, `solution_admission: true`. See
`foundry/evidence/terminal-theorem.json` and
`foundry/receipts/solution-admission.json` for the durable record.

## Sequencing note (historical)

Per `foundry/workstreams/state.json`'s real dependency graph
(`A→B→C→D→E→F→G(→H)→I→J→K`, with H also depending on F), each workstream
was attempted strictly in order — a later workstream could not be
investigated in isolation before its dependencies were real, since its own
verifier binary requires the prior workstream's real `ADMITTED` state and
receipt chain as input. Every workstream's evidence requirement was
discovered by reading its actual binary immediately before running it, not
guessed in advance.

## See also

- [Completion PRD](15-foundry-completion-prd.md) — requirements and current real standing.
- [Enterprise Architecture Foundry Program](14-enterprise-architecture-foundry.md) — program overview.
- `governance/production-gaps.md` — general ledger this program's gap is cross-linked into.
