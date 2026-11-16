# ggen-legacy migration plan v26.11.16

Standing: UNVERIFIED

## Identity
- Path: /Users/sac/ggen-legacy
- Remote: https://github.com/seanchatmangpt/ggen-legacy
- Branch: fix/v26.9.29-ci-gates@964009f7 (origin: ahead 9)
- Last commit: 2026-11-09; commits: 286; size: 984 MB (.git 272 MB, tools/ 31 MB)
- Languages/build: Rust (Cargo.toml, justfile), ggen.toml, ontology/, authority/
- Nested repos: none

## Observed state
- Dirty 12330: essentially all are ` D stardf/**` — 12297 under `stardf/arrow`, plus
  stardf/docs, stardf/.claude, stardf/CLAUDE.md, MOVE-TO-HOME-READY.md, README-MOVE-NOTE.md.
  The `stardf` tree was moved out (to ~/stardf per its move notes) but the deletion is
  uncommitted. Untracked 9 (docs/jira entries etc.).
- Ahead 9 unpushed. Stash: 129 (census). Unpushed/gone branches: 20 (agent/*, integrate*/*,
  fix/gl-lsp-001 gone, agent/add-dsrust-groq gone).
- No target/ present. `.ggen/` present.

## What it is
Verified Repository Reconstitution: reconstructs a legacy repo's observable contract, admits
it into machine-readable authority, manufactures a replacement, verifies closure.

## Classification
ACTIVE (census agrees; Nov 2026 commits).

## Migration risk
HIGH. 9 unpushed commits, 129 stashes, ~20 local branches, and a 12k-file uncommitted
deletion of stardf/ that must be recorded as a move, not lost.

## Recommended action
COMMIT-PUSH
1. `cd /Users/sac/ggen-legacy && git status --porcelain | grep -v '^ D stardf' | head`
2. DECISION: confirm stardf now lives at /Users/sac/stardf (own repo) — then
   `git add -A stardf && git commit -m "chore: stardf moved to ~/stardf"`
3. `git add -A && git commit -m "docs: pending jira + untracked"`
4. `git push origin fix/v26.9.29-ci-gates` ; `git push --all origin` (DECISION: prune
   integrate*/* branches instead of pushing).
5. Stashes: `git bundle create <archive>/ggen-legacy.bundle --all` plus manual stash triage.
6. CLONE-FRESH afterwards; move `.ggen/` keys via secure channel.

## First commands on the new machine
`cargo check --workspace` then `just --list`

## See Also
- ../v26.11.9/
- /Users/sac/docs/jira/v26.11.16/README.md
