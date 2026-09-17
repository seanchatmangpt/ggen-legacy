# GL-ERRC-012 — Split golden-trace corpus design out of GL-VERIFY-006

**Status:** admitted, `NOT_STARTED` — drafted by ultracode ERRC pass 3
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
3. This ticket's own authored boundary (`equivalence_runner.py`'s
   `run_case` case-source branch and the new example JSON file at
   `packs/legacy-equivalence-verifier-pack/consumer/legacy-equivalence/
   golden-trace-corpus.example.json`) does not overlap
   `GL-VERIFY-006`'s Rust-side `coverage_projection.rs` boundary — the two
   tickets must remain independently executable in either order, or
   concurrently, without file-level conflict beyond the shared Python file
   (`equivalence_runner.py`), which each ticket touches at a different,
   named location (`run_case`'s case-source branch here; the trace-object/
   receipt-emission call site there).
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

- `tickets/GL-VERIFY-006.md:128-154` (read directly this session), the
  section headed "## Pre-derived design: golden-trace corpus (ultracode
  backlog item 22)" — 27 lines, self-contained: full schema-name
  (`ggen.legacy-equivalence.golden-trace-corpus.v1`), field convention,
  integration point (`run_case`'s case-source discriminator branch), and
  target example-file path, with no forward or backward reference to the
  `ParityGateReceipt` section immediately above it (lines 82-126) beyond
  the shared header line "Complements the pre-derived `ParityGateReceipt`
  design above" — a soft cross-reference, not a code or schema dependency.
- `docs/v26.8.20/ultracode-loop-progress.md:38` (item 22, this session's
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

## Standing

`UNKNOWN` — not started. This ticket only relocates a design already
written; implementing the golden-trace corpus format in
`equivalence_runner.py` remains out of scope until a session/human
explicitly starts this ticket.
