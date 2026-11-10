# T019 — Custom handlers for ontology-inexpressible logic

Standing: REGISTERED

Wave: W1 · Depends on: T-008, T-015
Owned paths: ~/srve/packs/srve-backend-pack (cnv:CustomBehavior)
Research lanes: L01

## Scope

Port as registered handlers: the ~19 operations/changes (nte_guard, quote_margin_guard,
acceptance_token_guard, assign_provider_guard, check_in_out_guard, close_out_invoice_paid_guard,
intake, convert_to_project, generate_proposal, auto_dispatch, place_dial_call,
transmit_client_update, ...), commercial changes and w9 campaign changes, alignment_matcher (247
LOC), auto_dispatch (215), htn_planner/dynamic_planner (321), IngestAndMatchReactor,
telephony/client_update/proposal_generator/site_enrichment adapters (contract declared, impl
stubbed). Handwritten residue listed as UNSUPPORTED rows until ported.

## Acceptance

- Each handler is registered and invoked from its generated action.
- Residue table lists every unported handler as UNSUPPORTED.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ./scripts/handler_registry_check.sh
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t019-residue-custom-handlers.md (under docs/jira/v26.11.9/)
Falsifier: A generated action runs without invoking its handler.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-019`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/exists] handler registry
  - paths:
    - `srve:packs/srve-backend-pack/handlers/registry.toml`
- [T0/count] registry lists the 22 residue handlers
  - paths:
    - `srve:packs/srve-backend-pack/handlers/registry.toml`
  - pattern: `^name = `
  - n: `22`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
