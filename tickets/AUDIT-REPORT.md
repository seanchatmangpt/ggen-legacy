# GL-*.md Ticket Audit Report

Checklist (4 items applied to each ticket):
1. Required header sections present (Status/Base/Standing ceiling/Publication, Outcome, Authored boundary, Hard laws, Falsifiers, Acceptance, Standing)
2. Status line matches real repo state / Standing claims are evidenced, not bare assertion
3. Authored-boundary file overlaps with other tickets are explicitly disclosed
4. No fabricated or unverifiable factual/citation claims

19 tickets audited. 5 pass all four checks. 14 fail at least one. Ranked worst first below.

## Failing tickets, worst first

### 1. GL-AUTO-001.md — worst in corpus
Fails checks 1, 2, and 4.
- Missing almost every required header: no Status line, no Publication line, no "Standing ceiling" heading, no Outcome section, no Hard laws section, no Falsifiers section, no Standing section. Only Subject/Purpose/Automated production command/Authored boundary/Required behavior/Exclusions/Acceptance are present.
- No Status line at all, so production-behavior claims (acceptance string `GL_AUTO_001_AUTONOMIC_CROWN_ALIVE`) have no grounding section.
- Running `python3 scripts/run_autonomic_crown.py` live produces `REFUSED:FORBIDDEN_DIFF:...`, not the promised success string — the Acceptance claim does not hold in the real repo.
- Fabricated claim: asserts `.github/workflows/autonomic-crown.yml` executes the command and uploads evidence; that workflow file does not exist.

### 2. GL-ERRC-017.md
Fails checks 1 and 4.
- Missing both "## Acceptance" and "## Standing" sections entirely.
- Fabricated citation: claims a prior finding "mirrors docs/v26.8.20/DECISIONS.md's own item-12 finding" — DECISIONS.md has no item 12 (only items 2, 16, 20, 23), and none of the real items discuss this ticket's subject matter.

### 3. GL-LSP-001.md
Fails checks 1, 2 (unverifiable due to 1), and 3 (unverifiable due to 1).
- Missing nearly all required structure: no Status, Base, Standing ceiling, Publication, Outcome, or Authored boundary sections; only Falsifiers, Acceptance, and Standing exist, with no explicit Hard laws heading (uses "Admission"/"Observable contract"/"Positive witnesses" instead).
- Because there's no Status line, Status-vs-reality cannot be checked, and because there's no Authored boundary, overlap with other tickets cannot be assessed.
- Check 4 spot check passed (evidence files exist, code claims verified) — the missing structure, not fabrication, is what fails this ticket.

### 4. GL-ERRC-013.md
Fails checks 3 and 4.
- Undisclosed overlap: both GL-ERRC-013 and GL-PLAN-002 claim `AGENTS.md` in their Authored boundary; neither ticket acknowledges the other.
- Fabricated/broken Acceptance commands: the ticket's own verification greps (`grep "^- active executable ticket: GL-LSP-001$"`, anchored without backticks) do not match the real AGENTS.md content (which wraps values in backticks) — both commands fail even against a correct, untouched file.

### 5. GL-MANUFACTURE-005.md
Fails checks 3 and 4.
- Undisclosed overlap: claims `scripts/verify_foundry_bootstrap.py` in its Authored boundary; GL-ERRC-011 (Status EXECUTED) also claims the same file for the same kind of change, with no cross-reference either direction.
- Fabricated line-number claim: cites the disposition enum at `schemas/migration-manifest.schema.json:117-124`; the enum actually lives at lines 106-113.

### 6. GL-VERIFY-006.md
Fails checks 3 and 4.
- Undisclosed overlap: claims `tools/v26.8.1/src/coverage_projection.rs` in its Authored boundary (new code placed immediately before `exact_head`) with no cross-reference to GL-ERRC-019 (which modifies `exact_head` itself) or GL-ERRC-015 (which deletes a function in the same file) — contrast with GL-ERRC-012, which does explicitly reconcile its own overlap with this same ticket.
- Fabricated line-range claim: cites `check_provenance_receipt` at lines 378-410; the function actually spans 370-401, and the cited range bleeds 9 lines into the next function.

### 7. GL-ARCH-003.md
Fails checks 1 and 3.
- Missing the required "## Falsifiers" header (17 of 19 sibling tickets use it explicitly); this ticket folds equivalent content into a differently-titled section instead.
- Undisclosed overlap: both this ticket and GL-ERRC-008 claim `tools/v26.8.1/legacy_archaeology.py` in their Authored boundary; GL-ERRC-008 notes the overlap, but GL-ARCH-003 itself does not (the requirement is that each side carries the note, not just one).
- Checks 2 and 4 pass — Standing is honestly capped at PARTIAL_ALIVE with real command-derived evidence, and spot-checked commit/code citations verified.

### 8. GL-ERRC-012.md
Fails checks 2 (internal consistency) and 4.
- Internal self-contradiction: the Authored boundary section states no code file is touched ("planning-document split only"), but Hard Law 3 in the same file claims `equivalence_runner.py`'s `run_case` branch as this ticket's own authored boundary — directly contradictory.
- Fabricated citation: cites `docs/v26.8.20/ultracode-loop-progress.md:38` for an item-22 note; the real item-22 text is at line 71, and line 38 contains unrelated content.
- Minor factual imprecision: claims a cited section spans "lines 128-154 / 27 lines"; it actually runs 128-150 (~23 lines).
- Checks 1 and 3 pass.

### 9. GL-ERRC-018.md
Fails check 1 only.
- Missing both "## Acceptance" and "## Standing" sections entirely (file ends right after Falsifiers), unlike sibling NOT_STARTED tickets (GL-ERRC-013, GL-ERRC-019) which both include these sections even when marked "not yet run."
- Checks 2, 3, 4 pass — no Standing-vs-reality mismatch, no undisclosed authored-boundary overlap, and all spot-checked code/data citations verified exactly.

### 10. GL-PLAN-002.md
Fails checks 1 and 2 (consequential).
- Missing a required "## Standing" section entirely, despite a "Standing ceiling: PARTIAL_ALIVE" claim on the header line.
- Because there's no in-file Standing section, the PARTIAL_ALIVE claim has no exhibited evidence in the ticket itself (an independent live run of `planning/v26.8.7/verify.py --strict` confirms the claim is true in the real repo, but the ticket doesn't show that work).
- Checks 3 and 4 pass — no undisclosed authored-boundary overlap, and all spot-checked paths/commands verified.

### 11. GL-ERRC-011.md
Fails check 3 only.
- Undisclosed overlap: both this ticket and GL-MANUFACTURE-005 claim `scripts/verify_foundry_bootstrap.py` in their Authored boundary; neither notes the other.
- Checks 1, 2, 4 all pass, including a live re-run of all 4 referenced verification scripts confirming their claimed ALIVE/PARTIAL_ALIVE output.

### 12. GL-ERRC-014.md
Fails check 4 only.
- Fabricated precision: claims a grep for a specific commit hash "locates the citation in exactly two files"; a live re-run of the same grep finds a third matching file (`docs/v26.8.1/document-evidence-index.md`) not counted in the ticket's claim.
- Checks 1, 2, 3 all pass, including a live confirmation that the cited commit hash is indeed unreachable via `git cat-file -e`.

### 13. GL-ERRC-015.md
Fails check 3 only.
- Undisclosed overlap: claims sole ownership of `tools/v26.8.1/src/coverage_projection.rs`, but GL-VERIFY-006 and GL-ERRC-019 both also claim authored-boundary stakes in the same file — and this ticket set's own convention (used elsewhere by GL-ERRC-012/GL-ERRC-019) is to call out such overlaps explicitly, which this ticket does not.
- Checks 1, 2, 4 pass, including a live diff confirming the exact 8-line deletion the ticket describes.

### 14. GL-RECEIPT-007.md
Fails check 4 only.
- Fabricated citation: invokes "GL-LSP-001.md's ADR-002 handling" as precedent; GL-LSP-001.md has a "No self-certification" invariant but contains no ADR-002 label or section anywhere.
- Checks 1, 2, 3 pass, including a live re-run of `dsse_wrap.py selftest` confirming the described sign/verify/tamper-detection round trip.

## Passing tickets

- GL-CONTRACT-004.md
- GL-ERRC-008.md
- GL-ERRC-009.md
- GL-ERRC-010.md
- GL-ERRC-019.md

## Overall ticket-corpus health

Of 19 GL-*.md tickets, 5 (26%) pass all four checks cleanly and 14 (74%) fail at least one, but the failure modes cluster in a way that is more encouraging than the raw ratio suggests: no ticket was found to fabricate a completed EXECUTED status or falsely claim ALIVE standing for work that isn't done — every Status/Standing mismatch found was either a missing section (structural incompleteness, the most common single failure) or a real but narrow fact error (a wrong line number, an off-by-one file count, a broken grep anchor, or an unacknowledged file-overlap with a sibling ticket). The most severe failures are concentrated in three outlier tickets — GL-AUTO-001 (near-total structural absence plus a live-failing acceptance claim and a fabricated CI workflow reference), GL-ERRC-017 (missing sections plus a citation to a nonexistent DECISIONS.md item), and GL-LSP-001 (missing nearly all required headers, though its underlying evidence held up under spot-check) — while the remaining eleven failing tickets each have one or two contained, correctable defects (most commonly an undisclosed Authored-boundary overlap between two tickets both touching the same source file, or a small citation/line-number error caught by direct verification against the live repo). The corpus's discipline around NOT_STARTED tickets is notably strong: none of them overclaim standing, and every EXECUTED ticket's core command-output evidence was independently re-run and confirmed accurate. The dominant, recurring, fixable pattern is coordination hygiene between concurrently-drafted tickets that both stake Authored-boundary claims on the same file (coverage_projection.rs and verify_foundry_bootstrap.py each accumulate three-way undisclosed overlaps), suggesting the corpus would benefit most from a lightweight cross-ticket boundary-registry check at admission time rather than from tightening per-ticket evidentiary standards, which are already largely well-enforced.
