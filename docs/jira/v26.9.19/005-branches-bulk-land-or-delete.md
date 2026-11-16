# ggen-legacy: triage 28 PR-less unmerged remote branches

- Standing: OPEN
- Created: 2026-09-19 (v26.9.19 gh survey wave)
- Source: origin branches not merged into `main` with no open PR
- Evidence: `git branch -r --no-merged origin/main`: agent/autonomic-conversation-foundry agent/bootstrap-enterprise-architecture-foundry agent/document-chatman-ecosystem-v1 agent/enterprise-architecture-foundry-v1 agent/enterprise-architecture-foundry-v1-exec agent/errc-80-20-ci agent/fullerian-autonomics agent/ggen-legacy-lsp-max agent/ggen-legacy-lsp-runtime agent/gl-dspy-001-dsrust-reconstitution agent/pcq-marketplace-reference agent/reconstitute-same-day-ecosystem-v1 agent/unrdf-package-reconstitution feat/ggen-docs-reconstitution-pack worktree-wf_14d41261-3fe-1 worktree-wf_14d41261-3fe-2 worktree-wf_14d41261-3fe-3 worktree-wf_2d1bd891-8f3-1 worktree-wf_2d1bd891-8f3-2 worktree-wf_c50257bb-165-1 worktree-wf_c50257bb-165-2 worktree-wf_d45a38a1-7b7-1 worktree-wf_d45a38a1-7b7-2 worktree-wf_d45a38a1-7b7-3 worktree-wf_d4a5bdab-bb5-1 worktree-wf_d4a5bdab-bb5-2 worktree-wf_dbca2a9c-5eb-1 worktree-wf_dbca2a9c-5eb-2

## Work to complete
- Triage each branch: land (open a PR) or delete (`git push origin --delete <branch>`). Work in batches; record decisions in History.

## Acceptance
- `git branch -r --no-merged origin/main` is empty after `git fetch --prune`.

## History
- 2026-09-19 | OPEN | survey found 28 PR-less branches | full list above | triage pending
