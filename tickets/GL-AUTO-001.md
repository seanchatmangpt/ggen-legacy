# GL-AUTO-001 — Autonomic Conversation Foundry

**Status:** `BLOCKED` — corrected 2026-08-21 by `GL-ERRC-023`. A fresh run of the
acceptance command against main checkout HEAD
`bce7f6386c4203784beaae426e40804636c4151a` refuses with
`REFUSED:FORBIDDEN_DIFF:...` (115 files outside this ticket's authored boundary,
relative to the admitted base in `## Subject` below) before reaching the
manufacture/replay/verification steps. Neither `GL_AUTO_001_AUTONOMIC_CROWN_ALIVE` nor
`GL_AUTO_001_CROWN_ALIVE` has been observed printed by this command in this
repository. See `## Standing` for the full re-verification.

## Subject

- repository: `seanchatmangpt/ggen-legacy`
- admitted base: `33dd18801fecce48a5022c2727d1cefdf450cc87`
- runtime: Python 3 standard library only
- authority: read admitted JSON input; write only beneath an explicit output directory
- claim ceiling: autonomic bootstrap projection only

## Purpose

Convert the bounded conversation into a zero-gap canonical graph and manufacture the minimum production package for Claude configuration, Toyota flow control, Genesis naming, PPDDL planning, Hygen bootstrap, receipts, replay, and standing.

## Automated production command

```bash
python3 scripts/run_autonomic_crown.py
```

This command replaces the former manual sequence. It:

1. compiles the foundry, verifier, and crown runner;
2. manufactures the complete projection set;
3. executes deterministic replay and mutation verification;
4. requires `gap_count = 0` and bounded standing `ALIVE`;
5. verifies the exact-base changed-file boundary when Git metadata is available;
6. writes `evidence/autonomic/GL-AUTO-001.json`.

**Corrected 2026-08-21 (`GL-ERRC-023`):** no pull-request workflow currently executes
this command. `.github/workflows/autonomic-crown.yml` does not exist in this
repository — confirmed via `test -f .github/workflows/autonomic-crown.yml`, re-checked
live at correction time; the only files present under `.github/workflows/` are
`ci.yml` and `planning-v26-8-7.yml`. Automated CI execution and evidence-receipt
upload for this command is aspirational, not current behavior. (The previous text of
this section asserted the workflow file executes the command and uploads the receipt;
that assertion was fabricated and has been removed.)

## Authored boundary

```text
.github/workflows/autonomic-crown.yml
autonomic/**
scripts/autonomic_finish.py
scripts/verify_autonomic_finish.py
scripts/run_autonomic_crown.py
fixtures/autonomic/**
tickets/GL-AUTO-001.md
evidence/autonomic/**
```

## Required behavior

- Bind admitted decisions to authority, acceptance, falsifier, and evidence.
- Freeze the nine-object constitutional calculus.
- Enforce one-piece flow with WIP limit one.
- Manufacture Claude agents, skills, settings, and andon hook.
- Manufacture Genesis 1+3 CLI tokens and reject collisions.
- Manufacture PPDDL domain and problem with action costs.
- Manufacture the Hygen bootstrap lower-bound templates.
- Surface no unresolved gaps for the admitted fixture.
- Produce byte-identical second manufacture.
- Refuse duplicate concepts, optimistic standings, unknown projections, WIP expansion, invalid CLI tokens, and incomplete decisions.

## Exclusions

- arbitrary raw-language transcript extraction;
- LLM invocation;
- autonomous Git publication or deployment;
- spiritual diagnosis or recovery certification;
- ecosystem-wide production standing.

## Acceptance

```bash
python3 scripts/run_autonomic_crown.py
```

**Aspirational success path** (not currently observed in this repository): if the
exact-base changed-file boundary check passes and every manufacture/replay/
verification step succeeds, this command is intended to print:

```text
GL_AUTO_001_AUTONOMIC_CROWN_ALIVE
```

with the inner verifier printing:

```text
GL_AUTO_001_CROWN_ALIVE
```

**Actual observed output, corrected 2026-08-21 (`GL-ERRC-023`):** re-run fresh against
main checkout HEAD `bce7f6386c4203784beaae426e40804636c4151a`, admitted base
`33dd18801fecce48a5022c2727d1cefdf450cc87` (see `## Subject`). The command refuses
before reaching the manufacture/replay/verification steps, because the working tree
has diverged from the admitted base by 115 files outside this ticket's authored
boundary. Exit code `1`. Real stdout (single line):

```text
REFUSED:FORBIDDEN_DIFF:.github/workflows/ci.yml,.github/workflows/planning-v26-8-7.yml,.github/workflows/verify-docs.yml,.github/workflows/verify-ggen-v26-8-1-migration.yml,.gitignore,AGENTS.md,Cargo.lock,Cargo.toml,FORWARD_DEPLOYMENT.md,ONBOARDING.md,architecture/v26.8.3/ARD.md,authority/ggen-create-receiving-contract.json,authority/v26.8.3/release-authority.json,docs/case-studies/FORTUNE_5_GGEN_CREATE.md,docs/src/SUMMARY.md,docs/src/clean-session/00-prime.md,docs/src/clean-session/01-equation-calculus.md,docs/src/clean-session/02-pipeline-status.md,docs/src/clean-session/03-capability-graph.md,docs/src/clean-session/04-task-environment.md,docs/src/clean-session/05-materialization-doctrine.md,docs/src/clean-session/06-environment-manufacture.md,docs/src/clean-session/07-inspection-implementation.md,docs/src/clean-session/08-verification-publication.md,docs/src/clean-session/09-completion-receipt.md,docs/v26.8.1/90-legacy/93-capability-equivalence-matrix.md,evidence/lsp-contract/receiver-report.json,evidence/lsp-contract/stdio-replay-2026-08-03.json,evidence/v26.8.3/peer-prd-ard-receipt.json,governance/production-gaps.md,justfile,ontology/v26.8.1/legacy-capabilities.ttl,packs/cyberpunk-tv-platform-replay/README.md,packs/cyberpunk-tv-platform-replay/capability-ledger.json,packs/cyberpunk-tv-platform-replay/receiving-contract.json,packs/cyberpunk-tv-platform-replay/verifier-spec.json,packs/cyberpunk-tv-platform-replay/verify_source.py,packs/nasa-dark-mode-replay/README.md,packs/nasa-dark-mode-replay/receiving-contract.json,packs/nasa-dark-mode-replay/verify_no_ci.py,packs/nasa-dark-mode-replay/verify_source.py,planning/v26.8.20/README.md,planning/v26.8.7/README.md,planning/v26.8.7/benchmark.py,planning/v26.8.7/capability.py,planning/v26.8.7/cli.py,planning/v26.8.7/common.py,planning/v26.8.7/engines.py,planning/v26.8.7/engines.toml,planning/v26.8.7/fixtures/benchmark-reference-leak.json,planning/v26.8.7/fixtures/benchmark.json,planning/v26.8.7/fixtures/career-capabilities.json,planning/v26.8.7/fixtures/career-domain.pddl,planning/v26.8.7/fixtures/career-problem.pddl,planning/v26.8.7/lib.py,planning/v26.8.7/manifest.toml,planning/v26.8.7/mfw-receiving-contract.json,planning/v26.8.7/ontology.ttl,planning/v26.8.7/orchestration.py,planning/v26.8.7/projections.py,planning/v26.8.7/queries/admissible-planners.rq,planning/v26.8.7/queries/blocked-children.rq,planning/v26.8.7/queries/receipt-chain.rq,planning/v26.8.7/schemas/engine-run-receipt.schema.json,planning/v26.8.7/schemas/goal-reconstruction.schema.json,planning/v26.8.7/schemas/orchestration-snapshot.schema.json,planning/v26.8.7/skdecide_classical_engine.py,planning/v26.8.7/tests/test_planning.py,planning/v26.8.7/verify.py,product/v26.8.3/PRD.md,rust-toolchain.toml,scripts/ci/guard-verifier-proof.sh,scripts/ci_errc.py,scripts/ci_step_receipt.py,scripts/tests/test_ci_errc.py,scripts/tests/test_ci_step_receipt.py,scripts/verify_docs.py,scripts/verify_ggen_create_bundle.py,src/analysis.rs,src/backend.rs,src/capabilities.rs,src/generated_contract.rs,src/main.rs,tests/analysis.rs,tests/analysis_boundary.rs,tests/contract.rs,tests/exit_code.rs,tests/fixtures/ggen_create_fortune5.json,tests/lsp_boundary.rs,tests/test_ggen_create_receiver.py,tickets/GL-LSP-001.md,tickets/GL-PLAN-002.md,tickets/TICKET-014-v26-8-3-prd-ard.md,tickets/TV-001-cyberpunk-platform-source-admission.md,tools/dsrust-disposition-proposer/Cargo.lock,tools/dsrust-disposition-proposer/Cargo.toml,tools/dsrust-disposition-proposer/src/main.rs,tools/ggen-verifier-cli-verify/.gitignore,tools/ggen-verifier-cli-verify/Cargo.lock,tools/ggen-verifier-cli-verify/Cargo.toml,tools/ggen-verifier-cli-verify/docs/chicago_tdd_tools_boundary.md,tools/ggen-verifier-cli-verify/ggen.lock,tools/ggen-verifier-cli-verify/ggen.toml,tools/ggen-verifier-cli-verify/schema/domain.ttl,tools/ggen-verifier-cli-verify/src/lib.rs,tools/ggen-verifier-cli-verify/templates/.gitkeep,tools/ggen-verifier-cli-verify/tests/chicago_tdd_tools_boundary.rs,tools/ggen-verifier-cli-verify/tests/chicago_tdd_tools_boundary_proof.rs,tools/ggen-verifier-cli-verify/tests/chicago_tdd_tools_boundary_runtime.rs,tools/v26.8.1/Cargo.lock,tools/v26.8.1/Cargo.toml,tools/v26.8.1/src/bin/subsystem_verifier.rs,tools/v26.8.1/src/coverage_projection.rs,tools/v26.8.1/tests/verifier_boundary.rs,verifiers/verify_ggen_v26_8_3.py
```

Neither `GL_AUTO_001_AUTONOMIC_CROWN_ALIVE` nor `GL_AUTO_001_CROWN_ALIVE` has been
observed printed by this command in this repository as of this correction. This
output is base-relative: as the admitted base above is advanced closer to `HEAD`, the
refused-file list will change, so re-run the command fresh to re-verify rather than
trusting this quoted output as durable truth.

## Standing

`BLOCKED` — re-verified live 2026-08-21 under `GL-ERRC-023`. The automated production
command (`python3 scripts/run_autonomic_crown.py`) exists and executes, but refuses
before performing any manufacture/replay/verification work: the current repository
state (main checkout HEAD `bce7f6386c4203784beaae426e40804636c4151a`) has 115 files
changed outside this ticket's authored boundary relative to the admitted base
(`33dd18801fecce48a5022c2727d1cefdf450cc87`), so the exact-base changed-file boundary
check (step 5 of `## Automated production command`) refuses with
`REFUSED:FORBIDDEN_DIFF:...` and exit code `1`. No CI workflow
(`.github/workflows/autonomic-crown.yml`) exists to automate this command or upload
its evidence receipt — only `.github/workflows/ci.yml` and
`.github/workflows/planning-v26-8-7.yml` are present under `.github/workflows/`.
Neither success string (`GL_AUTO_001_AUTONOMIC_CROWN_ALIVE` nor the inner
`GL_AUTO_001_CROWN_ALIVE`) has been observed printed by this command in this
repository. This status reflects this ticket's admitted base being far behind current
`HEAD`, and the absence of the CI workflow it claimed — not a demonstrated defect in
the underlying `autonomic/` manufacture/replay/verify machinery, which this run never
reached. No claim of `ALIVE` or `EXECUTED` standing is made for any part of this
ticket.
