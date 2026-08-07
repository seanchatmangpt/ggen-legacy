# Production Gaps

This document lists what stands between the current repo state and the formal
Release Admission (G8) / Sunset Admission (G9) bar defined in
[`RELEASE_CONTROL.md`](../RELEASE_CONTROL.md), for each item currently
`UNKNOWN` or `REFUSED` in [`governance/claims-register.md`](claims-register.md).
It exists so "production usable" work stays honest about which gaps are
closeable by writing code and which are business/org decisions outside a
code change's reach — per `RELEASE_CONTROL.md`'s own rule that a lower
ceiling must not be phrased as a higher one.

## What an engineering pass can close (and this pass did)

These items were concrete, code-fixable blockers, not governance gaps:

- Dirty/uncommitted working tree on `fix/gl-lsp-001-unblock-rust-runtime`
  (dependency bumps, new boundary tests, an onboarding doc, a local CI gate)
  — committed in logical groups; `cargo fmt --check`, `cargo clippy -D
  warnings`, and `cargo test --all-targets --locked` are clean on both the
  root workspace and `tools/v26.8.1`.
- A prompt-injection payload embedded in the untracked `ONBOARDING.md` —
  stripped before committing.
- `scripts/ci/guard-verifier-proof.sh` silently assumed a single-machine
  absolute path (`GGEN_REPO=/Users/sac/ggen`) — now requires the env var
  explicitly and fails loudly with setup instructions if unset.
- PR #19 (ggen-create bundle receiver)'s failing `verify` check — root
  cause was a stale branch relative to a `verify_docs.py` fix already on
  `main`, not a defect in the PR's own diff.
- No single local command reproduced what CI gates — added a root
  `justfile` (`just ci-all`) mirroring
  `.github/workflows/gl-lsp-001-runtime.yml`'s ladder exactly for both
  workspaces.

## What remains — and who/what closes it

These map directly to `governance/claims-register.md`'s `UNKNOWN`/`REFUSED`
rows. None of them close from a code change in this repo; each names its
actual unblock action.

| Claim | Standing | What actually closes it |
|---|---|---|
| CLM-005 — production security | `UNKNOWN` | An independent security assessment against the real deployed system. No such system exists yet to assess. |
| CLM-006 — SOC 2 / regulatory compliance | `REFUSED` | A third-party compliance audit. `RELEASE_CONTROL.md` explicitly forbids self-asserting this ceiling. |
| CLM-007 — production performance/availability | `UNKNOWN` | Longitudinal production telemetry from a real deployment. Cannot be produced by tests against fixtures. |
| CLM-008 — real predecessor Sunset Admission | `UNKNOWN` | A real legacy repository, a real predecessor system, and an explicit, receipted, authorized retirement decision (`RELEASE_CONTROL.md`: "Project 001 must not fabricate retirement"). This is a customer/business decision, not a technical one. |
| CLM-013 — complete product is production-ready | `UNKNOWN` | Depends on CLM-003 (most target architecture systems — archaeology, admission, manufacture, equivalence, verification, replay, standing, sunset — remain `PARTIAL_ALIVE`/unimplemented) and CLM-012 (A–K foundry program terminal predicates still open). This is a real, large implementation gap, not a paperwork one — see next section. |

## What remains — and *is* code-shaped, but out of this pass's scope

Unlike the table above, these are implementation gaps a future engineering
pass could close. Listed here so they aren't silently dropped:

- CLM-003 / CLM-012: the target architecture's archaeology, admission,
  manufacture, equivalence, verification, replay, and standing systems are
  mostly `DOCUMENTED`/`PARTIAL_ALIVE`, not `TESTED`/`REFERENCE_CONFORMANT`.
  Closing this is the actual multi-month scope of "complete the A–K
  foundry program," not something an 80/20 pass reaches.
- `lsp-max` dependency is pinned to an unmerged branch of
  `seanchatmangpt/lsp-max` (see the comment on that dependency in
  `Cargo.toml`) — unblocked by merging that branch upstream or cutting a
  release tag, both of which are actions in that sibling repo, not this one.
- `scripts/ci/guard-verifier-proof.sh` is real and useful but stays a local
  dogfood gate, not CI, because it hard-depends on a sibling `~/ggen`
  checkout at a path only meaningful on this machine. Wiring it into CI
  would need that dependency vendored, published, or otherwise made
  CI-reachable — a decision about how `ggen`/`ggen-legacy`/`ggen-create`
  are meant to be checked out together, not a one-line fix.
- The ggen-create ↔ ggen-legacy bundle-receiving pipeline (PR #19 on this
  repo, `agent/power-ggen-legacy-fortune5` on `ggen-create`) is designed
  and each half works in isolation, but the producer pin (`ggen-create`
  commit `a0a9133`, v0.4.0) is stale against `ggen-create`'s current main
  (v26.8.6) — closing this means re-pinning to a current commit once both
  branches merge, not a gap in this repo alone.
