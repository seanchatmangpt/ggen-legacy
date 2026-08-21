# v26.8.20 — Gall's Law checkpoints: scope decisions

## Relationship to `planning/v26.8.20/README.md`

A separate candidate proposal already exists at `planning/v26.8.20/README.md`
(explicitly marked "candidate proposal, not admitted" — produced in a prior
session's exploration of `~/wasm4pm` and a `/deep-research` pass on a
`ggen-legacy-mcp` design). That document proposes a 6-skill/6-tool MCP
surface for the observe→admit→construct→verify→replay→retire pipeline and
flags, in its own "Open gaps" section, that it was **not checked against
`GL-LSP-001`/`GL-PLAN-002`'s real contracts** before proposing a `GL-MCP-00X`
ticket.

This session's work is independent and narrower: it executes Gall's Law
checkpoint 1 (archaeology) as a real ticket (`GL-ARCH-003`) and drafts
tickets for checkpoints 2–5. Neither document supersedes the other; a future
session admitting `GL-MCP-00X` should reconcile both against
`GL-ARCH-003`/`GL-CONTRACT-004`/`GL-MANUFACTURE-005`/`GL-VERIFY-006`/
`GL-RECEIPT-007` rather than re-deriving scope from either alone.

## Scope split for this pass

Per `CLAUDE.md`'s Gall's Law section (five checkpoints: archaeology →
contract → manufacture → verify → receipt), this session:

1. **Executed** `GL-ARCH-003` (archaeology) — the only checkpoint both
   self-contained (no dependency on the unmerged sibling-repo Foundry
   runtime) and additive (doesn't touch the 65 published TTL individuals).
2. **Drafted, `NOT_STARTED`** tickets for the remaining four checkpoints
   (`GL-CONTRACT-004`, `GL-MANUFACTURE-005`, `GL-VERIFY-006`,
   `GL-RECEIPT-007`), each scoped to a pilot/additive subset with named
   falsifiers and explicit exclusions, so a future session executes against
   a real ticket instead of re-deriving scope.

Rationale: this repo's own rules (ticket-gated admission, zero unreceipted
actuation, "no self-certification" per `tickets/GL-LSP-001.md`'s ADR-002
precedent) forbid silently building all five checkpoints in one unreviewed
pass — several require either external-runtime admission this repo cannot
unilaterally grant (manufacture, gated on `seanchatmangpt/ggen#544`'s
`runtime_dependency_admitted` flag) or a cross-repo digest-format decision
(receipt: BLAKE3 vs. SLSA's SHA-256-family digest fields) that is named as
an open question, not resolved here.

## Real finding worth flagging up front

`GL-ARCH-003`'s acceptance run surfaced that `CATALOG`'s cited
`historical_source_commit` hashes (e.g. `9cef6e40f`, `bde78f7d5`) are not
valid git objects in this worktree — this worktree's full `--all` history is
420 commits, and those hashes belong to a different producing repository's
history per the catalog's own prose. This is a pre-existing condition (not
introduced by this ticket) and is recorded as `UNKNOWN` in `GL-ARCH-003`
rather than silently assumed resolved.

## Exhaustive cross-repo commit-hash finding (ultracode backlog item 2)

A full cross-check of all 65 `CATALOG`/`EXT_CATALOG`/`EXT_CATALOG2` individuals
extracted 79 distinct hash tokens from their `historical_source_commit` fields
and ran `git cat-file -t`/`git rev-parse --verify` against each in this
worktree. **All 79 are unreachable** — not a sample, the complete set. This
worktree's own `--all` history (420 commits) contains none of the commits
`CATALOG` cites as evidence. The catalog's own prose already documents this
as citing a different producing repository's history in places (see
`GL-ARCH-003`'s earlier 2-hash finding), but the exhaustive check makes clear
this is the *universal* case, not an exception — every `historical_source_commit`
in this file currently refers to history this worktree does not contain.
This is named as `UNKNOWN` standing for the cross-repo linkage as a whole
(not per-entry), consistent with `GL-ARCH-003`'s existing framing, and is not
treated as a defect to silently fix — it is an open question for the repo
owner: either these commits should be documented as explicitly external
(with a named source repo per entry, not just prose), or a companion history
(e.g. a fetched remote of `seanchatmangpt/ggen`) needs to be made locally
resolvable so `historical_source_commit` claims can be independently verified
by a caller of `legacy_archaeology.py`, not just trusted from the original
curating session's notes.

## Stale foundry authority finding (ultracode backlog item 16)

`authority/foundry-work-program.json` and `foundry/bootstrap.yaml` both
claim the sibling-repo runtime PRs (`seanchatmangpt/ggen#544`, `#543`) are
`OPEN_DRAFT` / not admitted. Checked against the real `~/ggen` sibling repo:
both PRs are actually **merged** (2026-08-01), with further commits since.
Not acted on here — see `tickets/GL-MANUFACTURE-005.md`'s flagged note.
This is the repo owner's decision to make, not this session's.

## Disposition-confidence gap (ultracode backlog item 20)

Three of the 65 CATALOG individuals (`legacy_sync_audit_flag`,
`legacy_sync_dry_run_value_flag`, `legacy_ggen_toml_dual_schema`) assert a
definite disposition (`REFUSED`/`REPLACED`/`REPLACED`) while their own
`historical_source_commit` field is literally the string `"UNKNOWN"` —
inconsistent with the file's own stated admission criterion (disposition
confidence should track the cited primary evidence field). Their `notes`
fields do cite separate resolving evidence from a later session
("Superseded (agent/v26.8.1-disposition-repair, 2026-07-31)..."), but the
`historical_source_commit` field itself was never updated to reflect that
resolution. Not fixed here (touching CATALOG data requires the same
evidence-verification discipline the file's own docstring demands, which
this audit did not perform) — flagged for a future session to either update
`historical_source_commit` with the resolving evidence's citation, or
reconsider whether the disposition should be `DISPOSITION_UNKNOWN`.

## Just-recipe / CI-workflow drift (ultracode backlog item 23)

Two real, currently-reproducible problems found (not fixed here — outside
GL-ARCH-003's boundary, and `.github/workflows/`/`tools/v26.8.1/justfile`
belong to no admitted ticket in this session):

1. `.github/workflows/ci.yml:34-35` hardcodes `test "$count" -eq 1` for the
   number of workflow files in `.github/workflows/` — the repo now has 2
   (`ci.yml` + `planning-v26-8-7.yml`, added later in commit `8e58b55`).
   This self-check would fail on the next real CI run.
2. `tools/v26.8.1/justfile`'s `step-two` recipe currently fails for real
   (`python3 step_two.py --root ../..` exits 2, `step_two_standing=BUILD_BROKEN`),
   and `observe`/`crown` report `BUILD_BROKEN` standing due to git errors on
   an unreachable object `6b1ae24686bf31a9cbfa24dc0fa16c62bc47c5c6` referenced
   in the v26.8.1 verifier's corpus data — not present in this repo's history
   (consistent with this session's items 2/9 cross-repo-citation findings).

All pure lint/format/typecheck recipes (`fmt`/`check`/`clippy`, root and
v26 level) pass clean right now.

## Versioning note

`ggen-legacy` has no Cargo package version to bump for this milestone label
— its own versioning is the `README.md`/directory-name convention
(`docs/v26.8.20/`, `planning/v26.8.20/`), not a `Cargo.toml` `version` field.
No version bump was performed.
