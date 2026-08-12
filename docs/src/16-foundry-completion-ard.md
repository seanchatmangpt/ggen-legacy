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

**Why this stops the automated chain**: blindly applying the `^` parent
offset to all 17 would be wrong for whichever are not removal commits;
picking one side of a `"X vs. Y"` comparison, or guessing what a glob
"really means," would be inventing a resolution — the same category of
move already refused for C's 2 dispositions, at roughly 8x the scope and
materially higher ambiguity (multiple candidate interpretations per
capability, not one unresolved value). Closing E requires the same
per-capability real investigation method used for C (check `~/ggen`'s
actual history for each of the 17, individually, before touching
anything), not a tool fix.

## F, G, H — Primitive/pack/equivalence (`admit_products.rs`, 3 stages)

**Not attempted.** One binary, three internal stages
(`require_stage`/`finish_stage` helpers). Real refusal codes present in
source: `EQUIVALENCE_DISPOSITION_UNKNOWN`, `PACK_INPUT_PRIMITIVES_EMPTY`,
`PRIMITIVE_ADMISSION_REFUSED`. Depends on E. **Unverified** real inputs for
any of the three stages.

## I — Independent verification (`admit_verification.rs`)

**Not attempted.** Real refusal codes present in source:
`RECEIPT_OUTPUT_DRIFT`, `RECEIPT_PORTFOLIO_INCOMPLETE`,
`RECEIPT_REPOSITORY_INVALID`, `RECEIPT_SCHEMA_INVALID`,
`RECEIPT_SUBJECT_DIGEST_INVALID`, `SYSTEM_EVIDENCE_MISSING`,
`SYSTEM_EVIDENCE_NEGATIVE_CONTROL_FAILED`,
`SYSTEM_EVIDENCE_RECEIPT_PORTFOLIO_INCOMPLETE`. Depends on G and H. This is
the richest refusal surface found in the binary set — likely requires a
complete, consistent receipt DAG across every prior workstream, which by
construction cannot be assembled until D–H are real.

## J — Clean-room manufacture and replay (`admit_clean_room.rs`)

**Not attempted.** Real refusal code present in source:
`CLEAN_ROOM_HEAD_MISMATCH`. Depends on I.

## K — Fortune-scale reference reconstitution (`admit_reference.rs`)

**Not attempted.** Real refusal code present in source:
`REFERENCE_PACK_PRIMITIVES_INVALID`. Depends on J. This is also the last
workstream before `admit_final.rs`'s terminal 11/11 admission — not read in
detail this pass.

## Sequencing requirement

Per `foundry/workstreams/state.json`'s real dependency graph
(`A→B→C→D→E→F→G(→H)→I→J→K`, with H also depending on F), each workstream
must be attempted in order — a later workstream cannot honestly be
investigated in isolation before its dependencies are real, since its own
verifier binary requires the prior workstream's real `ADMITTED` state and
receipt chain as input. This ARD therefore does not attempt to front-load
D–K's evidence requirements beyond what their source already reveals; each
gets the same one-at-a-time treatment C just received, in order.

## See also

- [Completion PRD](15-foundry-completion-prd.md) — requirements and current real standing.
- [Enterprise Architecture Foundry Program](14-enterprise-architecture-foundry.md) — program overview.
- `governance/production-gaps.md` — general ledger this program's gap is cross-linked into.
