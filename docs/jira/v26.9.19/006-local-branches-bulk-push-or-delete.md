# ggen-legacy: triage 15 local-only branches

- Standing: OPEN
- Created: 2026-09-19 (v26.9.19 gh survey wave)
- Source: local branches with commits not on `origin/main` and no upstream
- Evidence: `git rev-list --count origin/main..<branch>` > 0 for each: agent/add-architecture-foundry-tool:1 worktree-wf_14d41261-3fe-1:1 worktree-wf_14d41261-3fe-2:1 worktree-wf_14d41261-3fe-3:1 worktree-wf_2d1bd891-8f3-1:1 worktree-wf_2d1bd891-8f3-2:1 worktree-wf_c50257bb-165-1:1 worktree-wf_c50257bb-165-2:1 worktree-wf_d45a38a1-7b7-1:1 worktree-wf_d45a38a1-7b7-2:1 worktree-wf_d45a38a1-7b7-3:1 worktree-wf_d4a5bdab-bb5-1:1 worktree-wf_d4a5bdab-bb5-2:2 worktree-wf_dbca2a9c-5eb-1:1 worktree-wf_dbca2a9c-5eb-2:1

## Work to complete
- Triage each branch: push (`git push -u origin <branch>`) or delete after confirming the commits are obsolete/recoverable. Batch the work; record decisions in History.

## Acceptance
- Every listed branch is pushed or deleted; no local-only branch with unique commits remains.

## History
- 2026-09-19 | OPEN | survey found 15 local-only branches | full list above | triage pending
