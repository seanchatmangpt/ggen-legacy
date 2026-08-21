# GL-ERRC-012 — Split golden-trace corpus design out of GL-VERIFY-006

**Status:** `EXECUTED` — planning-document split performed for real this
session. Evidence: `grep -c "golden-trace" tickets/GL-VERIFY-006.md` → `1`
(pointer line only, heading retained); `grep -c "golden-trace"
tickets/GL-ERRC-012.md` → `23` (full relocated section present, this
ticket's own prose plus the section); `diff` of the relocated section
(this file's lines 134-157) against the pre-edit original
(`tickets/GL-VERIFY-006.md`'s former lines 131-153) shows exactly one
line-pair difference — the intended cross-reference update ("design
above." → "design in `tickets/GL-VERIFY-006.md`.") — with the schema
name, `captured_*` field list, integration point, and example-file path
byte-identical; `tickets/GL-VERIFY-006.md`'s lines 1-130 (the
`ParityGateReceipt` design, Hard Laws, falsifiers, acceptance commands)
are byte-identical to the pre-edit original (`diff` empty); `git status
--porcelain` in the executing worktree shows only these two ticket files
touched (`?? tickets/GL-ERRC-012.md`, `?? tickets/GL-VERIFY-006.md`),
nothing else. See this session's PASS/FAIL report for full command
transcripts.
**Base:** `seanchatmangpt/ggen-legacy@f9b283e`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tickets/GL-VERIFY-006.md`'s "Pre-derived design: golden-trace corpus"
section (lines 128-154) is a complete, independently-executable design —
a `ggen.legacy-equivalence.golden-trace-corpus.v1` JSON schema, a
`captured_*`-field convention for all 10 `SURFACE_CHECKERS`, and a named
integration point (one case-source discriminator branch in `run_case`) —
bundled inside a ticket whose primary Outcome (`ParityGateReceipt` +
BLAKE3 case-manifest binding in `coverage_projection.rs`) is a *different*
piece of work with its own Hard Laws, its own Rust authored-boundary
files, and its own falsifiers. The two designs share no code path: the
golden-trace corpus only touches `equivalence_runner.py`'s Python-side
`run_case` case-source branch and adds no new Rust struct, while
`ParityGateReceipt` only touches the BLAKE3-binding Rust struct and the
report-emission call site — they can be implemented, reviewed, and
falsified independently. Splitting them into two tickets lets a future
session execute either one without inheriting the other's authored
boundary or Hard Laws, and lets `GL-VERIFY-006` shrink to a single
coherent unit of work (the receipt-binding piece) instead of silently
growing scope by carrying an unrelated Feathers-style corpus design as a
subsection. This ticket does no new design work — it relocates the
already-complete golden-trace corpus section verbatim (updating only
cross-references) out of `GL-VERIFY-006.md` and into this new ticket file,
and removes that section (replaced with a one-line pointer) from
`GL-VERIFY-006.md`.

## Authored boundary

```text
tickets/GL-VERIFY-006.md   # remove "Pre-derived design: golden-trace corpus" section, replace with pointer to this ticket
tickets/GL-ERRC-012.md     # new ticket carrying the relocated design verbatim
```

No code file (`tools/v26.8.1/equivalence_runner.py`,
`tools/v26.8.1/src/coverage_projection.rs`) is touched by this ticket —
this is a planning-document split only, moving already-written design
prose between two `NOT_STARTED` tickets. Neither ticket's design content
is altered in substance by the move.

## Hard laws

1. The golden-trace corpus design's content (schema shape, `captured_*`
   field list, integration point description) is moved verbatim — no new
   design decisions are introduced by the split itself.
2. `GL-VERIFY-006.md`'s `ParityGateReceipt` design, Hard Laws, falsifiers,
   and acceptance commands are unchanged by this ticket — only the
   golden-trace subsection is removed.
3. **Correction (per `tickets/AUDIT-REPORT.md`'s check-2 finding — this Hard
   Law previously contradicted the Outcome section above, which correctly
   states this ticket touches no code file)**: this ticket's *split* touches
   only the two ticket `.md` files. The *implementation* the split's design
   describes — `equivalence_runner.py`'s `run_case` case-source branch and
   the new example JSON file at
   `packs/legacy-equivalence-verifier-pack/consumer/legacy-equivalence/
   golden-trace-corpus.example.json` — belongs to whichever future session
   executes this split-off ticket's design, not to this document-split
   ticket itself. That future implementation would not overlap
   `GL-VERIFY-006`'s Rust-side `coverage_projection.rs` boundary — the two
   split tickets remain independently executable in either order, or
   concurrently, without file-level conflict beyond the shared Python file
   (`equivalence_runner.py`), which each would touch at a different, named
   location (`run_case`'s case-source branch vs. the trace-object/
   receipt-emission call site).
4. This ticket does not implement the golden-trace corpus — it only
   relocates the design. Implementation remains `NOT_STARTED` work for a
   future session, same as it was inside `GL-VERIFY-006` before the split.

## Falsifiers

- `tickets/GL-VERIFY-006.md` after this ticket still contains the full
  golden-trace corpus prose (i.e., the split didn't actually remove it).
- This ticket's carried-over design differs in substance (schema fields,
  integration point, example file path) from what `GL-VERIFY-006.md`
  contained before the split.
- `git diff --stat` shows any file changed other than the two ticket
  files.
- `GL-VERIFY-006.md`'s `ParityGateReceipt` Hard Laws/falsifiers/acceptance
  section shows any content change beyond the removed subsection.

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy
grep -c "golden-trace" tickets/GL-VERIFY-006.md   # expect 1 (a pointer line only, not the full section)
grep -c "golden-trace" tickets/GL-ERRC-012.md      # expect the full section present
diff <(git show HEAD:tickets/GL-VERIFY-006.md | sed -n '128,154p') \
     <(sed -n '/## Pre-derived design: golden-trace corpus/,/^## Standing/p' tickets/GL-ERRC-012.md | head -n -1) \
  || echo "review diff: confirm relocation is verbatim modulo cross-references"
git diff --stat   # must show only tickets/GL-VERIFY-006.md and tickets/GL-ERRC-012.md
```

## Evidence this ticket is grounded in (verified this session)

- `tickets/GL-VERIFY-006.md:131-153` (**correction, per
  `tickets/AUDIT-REPORT.md`'s check-4 finding**: previously cited as
  128-154/"27 lines" — re-verified against current HEAD), the
  section headed "## Pre-derived design: golden-trace corpus (ultracode
  backlog item 22)" — ~23 lines, self-contained: full schema-name
  (`ggen.legacy-equivalence.golden-trace-corpus.v1`), field convention,
  integration point (`run_case`'s case-source discriminator branch), and
  target example-file path, with no forward or backward reference to the
  `ParityGateReceipt` section immediately above it (lines 82-126) beyond
  the shared header line "Complements the pre-derived `ParityGateReceipt`
  design above" — a soft cross-reference, not a code or schema dependency.
- `docs/v26.8.20/ultracode-loop-progress.md:71` (**correction, per
  `tickets/AUDIT-REPORT.md`'s check-4 finding**: previously cited as line 38,
  which contains unrelated content) (item 22, this session's
  own prior work log): "design golden-trace corpus format for
  equivalence_runner.py — DONE. Full JSON schema ... + 3-entry worked
  example designed ... Recorded in GL-VERIFY-006.md." Confirms the design
  was completed as a standalone deliverable and only *filed* inside
  `GL-VERIFY-006` for lack of its own ticket at the time — not because it
  depends on that ticket's `ParityGateReceipt` work.
- `tickets/GL-VERIFY-006.md`'s own Authored boundary (lines 19-23) lists
  exactly two code files
  (`tools/v26.8.1/equivalence_runner.py`,
  `tools/v26.8.1/src/coverage_projection.rs`) and never names
  `packs/legacy-equivalence-verifier-pack/` — the golden-trace corpus
  section's own target path
  (`packs/legacy-equivalence-verifier-pack/consumer/legacy-equivalence/
  golden-trace-corpus.example.json`) is a file the ticket's own Authored
  boundary never declared, meaning the ticket's Hard Laws could not
  legitimately gate that file's creation as written — a concrete
  scope-boundary inconsistency this split resolves by giving the corpus
  design its own boundary that does declare that path.

## Pre-derived design: golden-trace corpus (ultracode backlog item 22)

Complements the pre-derived `ParityGateReceipt` design in
`tickets/GL-VERIFY-006.md`. Per Feathers'
characterization/golden-master technique (capture real behavior once, as a
frozen baseline, not a spec): a `ggen.legacy-equivalence.golden-trace-corpus.v1`
sibling format to `case_manifest.json`, where the legacy side's output is
`captured_*` static data instead of a live re-run — so equivalence checks
survive legacy-environment loss (the point of "legacy"). Reuses this
runner's own vocabulary (`normalization_policy`, `expected_disposition`,
`observable_surfaces`) as a drop-in sibling, one `captured_*` field per
surface checker (`captured_stdout`/`captured_exit_code`/`captured_stderr`,
`captured_generated_bytes` base64, `captured_filesystem_delta` path→size
map, `captured_receipt_fields`, `captured_events`). `ARCHIVED`/
`recovery_result` cases stay manifest-only (recovery inherently needs a live
run). Integration: one case-source discriminator branch at the top of
`run_case` builds a synthetic legacy `AdapterResult` from `captured_*`
fields instead of calling `run_adapter`; all 10 existing `SURFACE_CHECKERS`
are reused unmodified since they only consume two `AdapterResult` objects.
Full worked JSON schema + 3-entry example available in this session's
backlog-item-22 agent transcript; write it to
`packs/legacy-equivalence-verifier-pack/consumer/legacy-equivalence/golden-trace-corpus.example.json`
when this ticket executes.

## Standing

`PARTIAL_ALIVE` — this ticket's own scope (the document split) is
`EXECUTED`, verified above. The golden-trace corpus *format itself*
remains `UNKNOWN`/`NOT_STARTED`: this ticket only relocated the already-
written design; implementing it in `equivalence_runner.py` (the
`run_case` case-source branch and the example JSON file) remains out of
scope until a future session explicitly starts that implementation.
