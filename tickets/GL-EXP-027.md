# GL-EXP-027 — `verify_lsp_contract.py`'s `HANDLER_ABSENT` check cannot detect that 14 advertised LSP capabilities are silent no-op stubs

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`src/capabilities.rs` (read in full this session, 64 lines) unconditionally
advertises capabilities including `definitionProvider` (line 19),
`referencesProvider` (line 20), `renameProvider` (lines 21-24, with
`prepare_provider: Some(true)`), `workspaceSymbolProvider` (line 26),
`foldingRangeProvider` (line 34), `semanticTokensProvider` (lines 35-55,
`full: Some(SemanticTokensFullOptions::Bool(true))`), `inlayHintProvider`
(line 56), `codeLensProvider` (lines 57-59), and `callHierarchyProvider`
(line 60) -- confirmed via `grep -n
"definition_provider\|references_provider\|rename_provider\|semantic_tokens_provider\|workspace_symbol_provider\|call_hierarchy_provider\|folding_range_provider\|code_lens_provider"
src/capabilities.rs`, which returns exactly lines `19,20,21,26,34,35,57,60`.

`src/backend.rs` (read in full this session, 460 lines) implements the 14
corresponding `LanguageServer` handlers as unconditional no-ops that ignore
their `_params` entirely, byte-for-byte:

```rust
// lines 302-306
async fn goto_definition(
    &self, _params: GotoDefinitionParams,
) -> Result<Option<GotoDefinitionResponse>> {
    Ok(None)
}

// lines 308-310
async fn references(&self, _params: ReferenceParams) -> Result<Option<Vec<Location>>> {
    Ok(Some(Vec::new()))
}

// lines 322-324
async fn rename(&self, _params: RenameParams) -> Result<Option<WorkspaceEdit>> {
    Ok(None)
}

// lines 336-340
async fn symbol(
    &self, _params: WorkspaceSymbolParams,
) -> Result<Option<Vec<SymbolInformation>>> {
    Ok(Some(Vec::new()))
}

// lines 405-409, 411-415, 417-419, 421-423
async fn folding_range(&self, _params: FoldingRangeParams) -> Result<Option<Vec<FoldingRange>>> { Ok(Some(Vec::new())) }
async fn semantic_tokens_full(&self, _params: SemanticTokensParams) -> Result<Option<SemanticTokensResult>> { Ok(None) }
async fn inlay_hint(&self, _params: InlayHintParams) -> Result<Option<Vec<InlayHint>>> { Ok(Some(Vec::new())) }
async fn code_lens(&self, _params: CodeLensParams) -> Result<Option<Vec<CodeLens>>> { Ok(Some(Vec::new())) }

// lines 425-458: prepare_call_hierarchy, incoming_calls, outgoing_calls,
// prepare_type_hierarchy, supertypes, subtypes -- all six, identically,
// `Ok(Some(Vec::new()))`
```

Cross-referencing `authority/lsp-contract.json` (run this session) confirms
these 14 `legacy_handler` names map to exactly these capabilities:
`goto_definition`->`definitionProvider`, `references`->`referencesProvider`,
`rename`->`renameProvider`, `symbol`->`workspaceSymbolProvider`,
`folding_range`->`foldingRangeProvider`,
`semantic_tokens_full`->`semanticTokensProvider`,
`inlay_hint`->`inlayHintProvider`, `code_lens`->`codeLensProvider`,
`prepare_call_hierarchy`/`incoming_calls`/`outgoing_calls`->`callHierarchyProvider`,
`prepare_type_hierarchy`/`supertypes`/`subtypes`->`typeHierarchyProvider`.

For every one of these 14 methods, the handler's return value for a real
request (a symbol that genuinely has definitions/references/callers, a
document with foldable regions, etc.) is byte-identical to its return value
for a request with no matches: `Ok(None)` or `Ok(Some(Vec::new()))`
regardless of input. A real LSP client cannot distinguish "the server looked
and found nothing" from "the server never looked."

`scripts/verify_lsp_contract.py` (read in full this session, 136 lines) is
the CI-gating check this repository relies on for `GL-LSP-001`'s "Advertise
every implemented capability truthfully" contract clause (`GL-LSP-001.md`
`## Observable contract`, point 4) and for its `## Falsifiers` entry
"capability without handler." Its only two content-level checks are both
textual presence checks, not behavioral ones:

- `HANDLER_ABSENT` (lines 63-68): `re.search(rf'\basync\s+fn\s+{re.escape(handler)}\b',
  backend)` -- true the moment a function with that name exists, regardless
  of its body.
- `CAPABILITY_ABSENT` (lines 70-84): true the moment the capability's string
  name (or its snake_case form) appears anywhere in `capabilities.rs` +
  `backend.rs`'s concatenated source text.

Neither check parses or evaluates the function body. Ran fresh this session
against unmodified `HEAD`:

```
$ python3 scripts/verify_lsp_contract.py --report /tmp/gl_exp_027_check.json
{
  ...
  "findings": [],
  "standing": "ALIVE",
  ...
}
$ echo $?
0
```

Real execution, not simulated: `findings: []`, `standing: "ALIVE"`, exit
`0`, with all 14 stub handlers present in the working tree unchanged. This
is the repository's own CI gate (`.github/workflows/ci.yml:41`: `run:
python3 scripts/verify_lsp_contract.py`) passing identically whether these
14 handlers perform real resolution or are complete no-ops.

`GL-LSP-001.md`'s own `## Standing` section additionally treats
`cargo test --all-targets` exiting 0 as part of its `ALIVE` runtime
standing, and its stdio-replay evidence
(`evidence/lsp-contract/stdio-replay-2026-08-03.json`, read in full this
session) is offered as satisfying the falsifier "hierarchy requests return
lawful responses." That replay's own captured observation is
`"prepare_type_hierarchy_response": []` -- an empty response accepted as
"lawful" without checking whether an empty result is the *correct* result
for the fixture document, which is exactly the ambiguity this ticket names:
a genuinely-empty result and a stub's always-empty result are recorded
identically as passing evidence. Neither `cargo test --all-targets` nor
this stdio replay closes the gap, because no Rust-level test exercises
these handlers at all. A complete grep across every stub handler's exact
function name, run this session --

```
$ grep -n "goto_definition\|references\|\brename\b\|\bsymbol\b\|folding_range\|semantic_tokens_full\|inlay_hint\|code_lens\|prepare_call_hierarchy\|incoming_calls\|outgoing_calls\|prepare_type_hierarchy\|supertypes\|subtypes" tests/*.rs
tests/analysis.rs:60:fn turtle_prefixes_inside_iri_references_are_not_reported() {
```

-- returns exactly one match, an unrelated Turtle-diagnostics test whose
name happens to contain the substring "references" (it tests
`GGEN-TTL-001` false-positive suppression on IRI refs, per this
repository's own `26ff775` commit, not the LSP `references` handler). Zero
real coverage of any of the 14 stub handlers across `tests/analysis.rs`,
`tests/analysis_boundary.rs`, `tests/contract.rs`, `tests/exit_code.rs`, or
`tests/lsp_boundary.rs`.

No existing ticket names this gap: `grep -iln
"goto_definition\|semantic_tokens\|prepare_type_hierarchy\|workspace_symbol\|incoming_calls\|outgoing_calls\|code_lens\|inlay_hint\|folding_range"
tickets/GL-*.md` (run this session) returns zero matches.

## Authored boundary

(Cross-ticket file overlaps are tracked in `tickets/OVERLAPS.md` -- see the
new `src/backend.rs`, `src/capabilities.rs`,
`scripts/verify_lsp_contract.py` section added by this ticket. `GL-LSP-001`
has no formal `## Authored boundary` section (it predates that convention,
using `## Identity` instead), but its `## Observable contract`, `##
Positive witnesses`, and `## Falsifiers` sections claim exactly these three
files as the basis for its own `ALIVE` source-contract standing. This
ticket's finding is a gap *in that same standing claim*, not a change to
the files that would conflict with `GL-LSP-001`'s own scope -- disclosed in
`OVERLAPS.md` rather than assumed away.)

```text
scripts/verify_lsp_contract.py   # add one new behavioral finding class; additive
tickets/GL-EXP-027.md
tickets/OVERLAPS.md   # add src/backend.rs / src/capabilities.rs / scripts/verify_lsp_contract.py section
```

No change to `src/backend.rs` or `src/capabilities.rs` themselves -- this
ticket does not implement real symbol resolution (that is a separate,
much larger body of work outside `GL-EXP` scope); it only proposes making
the existing CI gate honest about what it does and does not verify.

## Hard laws

1. This ticket does not implement real LSP symbol resolution, renaming, or
   any of the 14 stub handlers' actual logic -- that is out of scope. It
   only addresses `verify_lsp_contract.py`'s inability to distinguish a
   real handler from a stub.
2. Any fix stays inside `scripts/verify_lsp_contract.py`'s existing
   `verify()` function shape (its dict-based finding-codes convention,
   e.g. `HANDLER_ABSENT:...`, `CAPABILITY_ABSENT:...`) -- a new finding
   code (e.g. `HANDLER_STUB:...`) fits this existing pattern rather than
   introducing a new report schema.
3. A fix must not produce false positives against real, intentionally-empty
   handlers (e.g. a handler that legitimately returns `Ok(None)` for a
   request type this repository has decided never to support) -- any
   detection heuristic (such as "function body is a single trivial return
   statement with an unused/underscore-prefixed params argument") must be
   named explicitly as a heuristic with a documented false-positive/
   false-negative boundary, not asserted as a semantic proof of stubness.
4. This ticket does not modify `GL-LSP-001.md`'s own text -- it is a
   distinct, disclosed ticket per the `OVERLAPS.md` entry this ticket adds.
5. `git diff --stat` after this ticket touches only
   `scripts/verify_lsp_contract.py`, `tickets/GL-EXP-027.md`, and
   `tickets/OVERLAPS.md`.

## Falsifiers

- `python3 scripts/verify_lsp_contract.py` continues to report `standing:
  ALIVE` / `findings: []` against the current, unmodified stub handlers
  after the fix lands (the gap this ticket names is not closed).
- The fix's stub-detection heuristic is not documented as a heuristic (Hard
  Law 3) -- i.e. it is presented as if it proves absence of a real
  implementation rather than flags a suspicious pattern for human review.
- `git diff --stat` after this ticket touches any file outside
  `scripts/verify_lsp_contract.py`, `tickets/GL-EXP-027.md`, and
  `tickets/OVERLAPS.md`.
- `tickets/OVERLAPS.md` is not updated with this ticket's new section
  (Hard Law 5 / this ticket's own `## Authored boundary` note).

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the fix lands, not yet-observed outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
python3 scripts/verify_lsp_contract.py --report /tmp/gl-exp-027-before.json
python3 -c "import json; d=json.load(open('/tmp/gl-exp-027-before.json')); assert d['standing']=='ALIVE' and d['findings']==[]"
  # expect: no assertion error -- confirms the gap still exists

# After adding a stub-detection finding class:
python3 scripts/verify_lsp_contract.py --report /tmp/gl-exp-027-after.json
python3 -c "import json; d=json.load(open('/tmp/gl-exp-027-after.json')); print(d['standing']); print(d['findings'])"
  # expect: findings lists the 14 stub handlers by name (or standing
  # reflects a new, distinct status such as PARTIAL_ALIVE, per Hard Law 2's
  # existing-schema convention), and the finding text names itself as a
  # heuristic per Hard Law 3

grep -n "src/backend.rs\|src/capabilities.rs\|scripts/verify_lsp_contract.py" tickets/OVERLAPS.md
  # expect: the new disclosed section this ticket adds

git diff --stat   # must show only scripts/verify_lsp_contract.py,
                   # tickets/GL-EXP-027.md, tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- Direct `Read` of `src/capabilities.rs` in full (64 lines) this session,
  and `grep -n
  "definition_provider\|references_provider\|rename_provider\|semantic_tokens_provider\|workspace_symbol_provider\|call_hierarchy_provider\|folding_range_provider\|code_lens_provider"
  src/capabilities.rs`: exact lines `19,20,21,26,34,35,57,60`, confirmed
  against the direct read.
- Direct `Read` of `src/backend.rs:290-459` this session: confirms all 14
  stub-handler bodies quoted above, byte for byte against the live file.
- Direct `Read` of `scripts/verify_lsp_contract.py` in full (136 lines)
  this session: confirms `HANDLER_ABSENT` (lines 63-68, regex
  `\basync\s+fn\s+{handler}\b` against raw source text) and
  `CAPABILITY_ABSENT` (lines 70-84, substring presence against
  concatenated source text) are the sole content-level checks; neither
  parses or evaluates a function body.
- `python3 scripts/verify_lsp_contract.py --report /tmp/gl_exp_027_check.json`,
  run for real this session against unmodified `HEAD`: exit `0`,
  `"standing": "ALIVE"`, `"findings": []` -- direct proof the existing gate
  cannot see these 14 stubs.
- `grep -n "goto_definition\|references\|\brename\b\|\bsymbol\b\|folding_range\|semantic_tokens_full\|inlay_hint\|code_lens\|prepare_call_hierarchy\|incoming_calls\|outgoing_calls\|prepare_type_hierarchy\|supertypes\|subtypes"
  tests/*.rs` this session (a complete pattern covering all 14 handler
  names, run across all five files in `tests/`, including `tests/
  exit_code.rs` and `tests/lsp_boundary.rs` which an earlier, narrower
  pattern omitted checking explicitly): exactly one match,
  `tests/analysis.rs:60`, a Turtle-diagnostics test
  (`turtle_prefixes_inside_iri_references_are_not_reported`) unrelated to
  the LSP `references` handler -- confirmed by reading that test's body
  this session, and cross-referenced against commit `26ff775` ("fix(lsp):
  stop GGEN-TTL-001 firing on comments, literals, and IRI refs").
- `python3 -c "..."` against `authority/lsp-contract.json` this session:
  confirms the exact `legacy_handler`->`capability` mapping for all 14
  stub handlers, quoted in Outcome.
- Direct `Read` of `evidence/lsp-contract/stdio-replay-2026-08-03.json` in
  full this session: confirms `"prepare_type_hierarchy_response": []` is
  the one hierarchy-method response this repository's own real stdio
  replay captured, accepted as "lawful" without a check that empty is the
  *correct* answer for the fixture document.
- `grep -n "verify_lsp_contract" .github/workflows/ci.yml`: line 41,
  confirms this script is the live CI gate, not a dormant or advisory
  check.
- Direct `Read` of `tickets/GL-LSP-001.md` in full this session: confirms
  it has no `## Authored boundary` heading (`grep -n "^## "
  tickets/GL-LSP-001.md` lists `Identity, Admission, Observable contract,
  Positive witnesses, Falsifiers, Acceptance, Standing` only), and that its
  `## Observable contract` point 4 ("Advertise every implemented
  capability truthfully"), `## Positive witnesses` ("every non-framework
  received method has a `LanguageServer` handler"), and `## Falsifiers`
  ("capability without handler") are the exact clauses this ticket's
  finding bears on.
- `grep -iln
  "goto_definition\|semantic_tokens\|prepare_type_hierarchy\|workspace_symbol\|incoming_calls\|outgoing_calls\|code_lens\|inlay_hint\|folding_range"
  tickets/GL-*.md` this session (47 ticket files present): zero matches --
  no existing ticket names this gap.
- `grep -l "src/capabilities.rs" tickets/GL-*.md`: `GL-AUTO-001.md` only
  (a bare filename inside its 115-file `REFUSED:FORBIDDEN_DIFF:...` dump,
  not a claimed Authored-boundary file -- confirmed by reading that
  ticket's own `## Subject`/`## Authored boundary` in full this session,
  neither of which lists `src/capabilities.rs`). `grep -l
  "src/backend.rs" tickets/GL-*.md`: `GL-AUTO-001.md` (same non-substantive
  pattern) and `GL-LSP-001.md` (the real claim, addressed above).

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
capability-truthfulness gap (the CI gate's own inability to distinguish a
real handler from a no-op stub, and the 14 affected handlers this
verification names precisely) and the `tickets/OVERLAPS.md` disclosure
this ticket's own Hard Law 5 requires. No fix to
`scripts/verify_lsp_contract.py` has been made.
