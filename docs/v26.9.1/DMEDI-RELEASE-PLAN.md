# v26.9.1 Release Plan — DMEDI Structure

**Status: planning document, not a completion claim.** This maps the DMEDI
(Define → Measure → Explore → Develop → Implement) methodology onto
`ggen-legacy`'s actual, already-in-progress work toward v26.9.1, its first
announced release. Every figure below is a real count from the current
repo state (`git status`, `tickets/*.md` Status lines), not an estimate.
Standing values follow `CLAUDE.md`'s vocabulary — nothing here is claimed
`ALIVE` without cited evidence, per this repo's own discipline.

The mapping isn't decorative: DMEDI's Explore phase (concept generation,
concept selection via weighted scoring, hypothesis testing) is, structurally,
what this repo's standing ERRC exploration loop already does — this
document names that correspondence rather than building a parallel process.

---

## Define

**Charter.** `ggen-legacy` performs Verified Repository Reconstitution:
reconstruct a legacy repository's observable contract, admit it into
machine-readable authority, manufacture a replacement, independently verify
behavioral closure, and compute whether the predecessor may retire
(`README.md`, `CLAUDE.md`). v26.9.1 is the first release this project
*announces* — a claim about readiness for external eyes, not just internal
progress.

**MGPP (Multi-Generational Plan).** Real milestone lineage, from directory
evidence: `v26.8.1` (documentation-only bootstrap, `docs/v26.8.1/`) →
`v26.8.7` (concurrent planning-engine ticket `GL-PLAN-002`,
`planning/v26.8.7/`) → `v26.8.20` (this session's Gall's-Law-checkpoint work
and the 25-item ultracode backlog, `docs/v26.8.20/`) → **v26.9.1** (first
announced release, this document) → future generations undefined, per
`README.md`'s own honesty about "Complete product implementation: `UNKNOWN`."

**Risk register** (real, cited, not hypothetical):

| Risk | Source | Severity |
|---|---|---|
| `transparency-log.py`'s `verify()` has no external anchor — reproduced truncation, un-revocation, and chain-rebuild attacks all report `valid:true` | `tickets/GL-ERRC-010.md`, `docs/v26.8.20/ultracode-loop-progress.md` item 10 | High — undermines the receipt chain's evidentiary value |
| `authority/foundry-work-program.json`/`foundry/bootstrap.yaml` claim sibling-repo PRs are unmerged; real state (`gh pr view`) is `MERGED` | `tickets/GL-ERRC-021.md`, flagged 3× before remediation | Medium — stale authority-of-record |
| `authority/project-001-promotion.json` cites 5 evidence files that don't exist on disk; one rail's `ALIVE` claim has zero locatable backing | `tickets/GL-ERRC-017.md` | Medium — an `ALIVE` claim with no checkable evidence |
| `GL-AUTO-001.md` fabricates a CI workflow's existence and its own acceptance command doesn't pass | `tickets/GL-ERRC-020.md` | Medium — corpus-integrity defect, pre-existing |
| All `CATALOG` `historical_source_commit` hashes (79/79 checked) are unreachable in this worktree's history | `docs/v26.8.20/DECISIONS.md` | Low-Medium — named `UNKNOWN`, not silently assumed resolved |

**Communication plan.** `docs/v26.9.1/RELEASE-NOTES.md` (what shipped, what
didn't, corrected in place rather than rewritten when facts changed) +
`docs/v26.9.1/CHANGELOG.md` (append-only log) + this document (structure) +
`docs/v26.9.1/innovation-candidates.md` (explicitly `CANDIDATE`, not release
content — kept separate so future-work ideas never leak into a readiness
claim).

## Measure

**Scorecard — ticket corpus, real counts as of this session:**

- 23 tickets total in `tickets/`
- 7 executed with real evidence (`GL-ARCH-003`, `GL-ERRC-009`, `-011`,
  `-013`, `-015`, `-019`, `GL-PLAN-002`)
- 14 drafted, `NOT_STARTED` (real backlog, not vaporware — each carries
  falsifiers and acceptance commands per `tickets/AUDIT-REPORT.md`'s audit)
- 2 structurally broken pre-existing tickets (`GL-AUTO-001`, `GL-LSP-001` —
  missing required sections; `GL-AUTO-001`'s remediation is itself
  `GL-ERRC-020`)

**Measurement systems analysis.** Is `just ci-all` a trustworthy gauge?
Yes, by construction: it runs real `cargo fmt --check`/`check`/`clippy -D
warnings`/`test --all-targets --locked` against two real workspaces, no
mocked collaborators (per this repo's Chicago-style testing discipline) —
confirmed green after every batch of changes this session, not asserted
once and assumed to hold.

**Process capability.** `tickets/AUDIT-REPORT.md` (a real discover→verify→
synthesize sweep via the `config-audit` skill) found 14/19 tickets failing
at least one of 4 checks *before* this session's fixes — but zero tickets
fabricating a completed `EXECUTED` status or a false `ALIVE` claim. The
failure mode was structural (missing sections) or narrow factual error
(wrong line number, miscounted grep), not integrity failure. All findings
from that audit have since been corrected in place, with visible correction
notes rather than silent rewrites.

**Voice of the customer.** The "customer" for v26.9.1 is whoever reads
`README.md`'s standing table and decides whether to trust a claim — future
Claude sessions, the repo owner, and (once announced) external readers.
Their real need: a standing claim they can independently re-verify, per
this repo's entire evidentiary design (receipts, replay, bounded standing).

## Explore

This phase *is* the standing exploration capability already running
(`~/.claude/workflows/innovation-explorer.js`, and the ERRC cron
`a4cf4d20`), not a separate planning exercise:

- **Concept generation** = multi-lens agent sweeps (unexploited-capability,
  cross-repo-integration lenses) surfacing 14 candidates this session
  (`docs/v26.9.1/innovation-candidates.md`).
- **Concept selection (Pugh/AHP-equivalent)** = the novelty×feasibility×
  leverage weighted scoring each candidate receives, by a skeptic judge
  instructed not to give 5s across the board.
- **Hypothesis testing** = the adversarial-verify pattern used throughout
  this session's tickets (independent re-run of every cited claim; e.g.
  `GL-ARCH-003`'s "adversarial self-review" section, `tickets/AUDIT-REPORT.md`
  itself).
- **Design FMEA equivalent** = the risk register in Define, above — each
  entry names a real failure mode with a cited severity, not a hypothetical.

Top surfaced concepts, not yet promoted to release scope: wiring
`dsrust-disposition-proposer` into admission (`GL-ERRC-022`), exposing
`planning/v26.8.7/cli.py`'s A* planner via a `just` verb, and (external to
this repo) registering wasm4pm's OCLA algorithm in its CLI/MCP registry.

## Develop

**Detailed design** lives in each ticket's Hard Laws + Falsifiers sections —
that combination *is* this repo's design-requirements format (a Hard Law is
a design constraint; a Falsifier is the test that would catch its
violation), already DOE-adjacent in spirit: each ticket names the exact
factors held constant (e.g. `GL-ERRC-019`'s Hard Law 1: the happy-path SHA
must not change) and the exact response verified (3 real subprocess-backed
tests, not simulated).

**Reliability, in the DMEDI sense of "does it hold up over repeated
trials"**: every ticket this session was re-verified at least twice — once
at drafting, once independently by either `tickets/AUDIT-REPORT.md`'s audit
or a later reconciliation pass — and `just ci-all` was re-run after each
batch of changes, not trusted from a single green run.

**Robust design.** The `STALE_REFERENCE_UNVERIFIABLE:<CAUSE>` pattern
(`GL-ERRC-011`, `-014`, `-019`) is a real robust-design instance: instead of
one brittle failure mode (`"UNKNOWN"` swallowing 3+ distinct causes), the
fix makes the failure surface distinguishable and diagnosable under the
input variation (missing binary, wrong directory, corrupted encoding) that
would previously have collapsed to the same opaque signal.

## Implement

**Prototype and pilot** = worktree-isolated execution (`isolation: 'worktree'`
agents), each ticket's fix authored and verified in an isolated copy before
being reconciled into the real main checkout — a real prototype/pilot
distinction, not a metaphor: this session caught and fixed a case where a
verified worktree fix (`GL-ERRC-009`) hadn't actually reached the shared
checkout yet, exactly the gap a pilot phase exists to catch.

**Process control** = the two standing crons (`a4cf4d20` exploration,
`b77220ca` release-prep), each session-scoped and auto-expiring after 7
days — a real, bounded control mechanism keeping the release-prep process
moving without needing a human to manually re-trigger every pass.

**Implementation planning — the honest remaining backlog** (14
`NOT_STARTED` tickets, ranked by what blocks an announcement most):

1. `GL-ERRC-010` — transparency-log external anchor (highest severity, see
   Define's risk register)
2. `GL-ERRC-017` — reduce `project-001-promotion.json`'s unbacked `ALIVE`
   claims to what's actually locatable
3. `GL-ERRC-021` — remediate stale foundry-authority merge-status claims
4. `GL-ERRC-020` — fix `GL-AUTO-001`'s fabricated CI-workflow claim
5. Everything else (`GL-CONTRACT-004`, `GL-MANUFACTURE-005`, `GL-VERIFY-006`,
   `GL-RECEIPT-007`, `GL-ERRC-008`/`012`/`014`/`016`/`018`/`022`) — real,
   scoped, but lower-severity relative to an announcement decision.

**DMEDI Capstone — what "ready to announce" actually requires**, stated as
a falsifiable checklist rather than a vibe:

- [ ] Items 1-4 above execute with real evidence (not just drafted)
- [ ] `just ci-all` green (already true, reverify at announcement time)
- [ ] `README.md`'s standing table's `UNKNOWN` rails either resolve or are
      explicitly excluded from the v26.9.1 claim scope
- [ ] `tickets/AUDIT-REPORT.md` re-run clean (0/N failing) or every
      remaining failure explicitly accepted as out-of-scope with a named
      reason

**Not yet checked** — this document does not itself claim v26.9.1 is ready.
That determination is exactly what the checklist above exists to make
falsifiable, not what this planning document asserts.

## See also

- `docs/v26.9.1/RELEASE-NOTES.md` — real, corrected-in-place progress log
- `docs/v26.9.1/innovation-candidates.md` — Explore-phase output, `CANDIDATE` only
- `tickets/AUDIT-REPORT.md` — the Measure-phase corpus scorecard
- `tickets/OVERLAPS.md` — cross-ticket boundary registry (a Develop-phase
  design-for-manufacture concern: don't let two "manufacturing" tickets
  silently collide on the same file)
- `CLAUDE.md`'s Gall's Law section — the prior-art table this whole
  methodology already evolves from, per this repo's own standing instruction
  not to design from scratch
