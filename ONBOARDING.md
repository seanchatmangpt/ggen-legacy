# Welcome to ggen-legacy

## How We Use Claude

Based on Sean Chatman's usage over the last 30 days:

Work Type Breakdown:
  TODO — not enough session data yet to break this down

Top Skills & Commands:
  TODO — no slash command usage recorded yet

Top MCP Servers:
  TODO — no MCP server usage recorded yet

## Your Setup Checklist

### Codebases
- [ ] ggen-legacy — https://github.com/seanchatmangpt/ggen-legacy

### MCP Servers to Activate
- TODO — none observed in usage data yet

### Skills to Know About
- TODO — none observed in usage data yet

## Team Tips

- Read `~/.claude/CLAUDE.md` and this repo's `CLAUDE.md`/`AGENTS.md` before making changes — they encode our git workflow (fix-forward only, no `git reset --hard`) and tool preferences.
- Prefer `mcp__lumen__semantic_search` (or whichever semantic search MCP is configured) over `grep -r`/`find` for locating code — it indexes across language boundaries a single grep pattern can't.
- Use LSP tools (`goToDefinition`, `findReferences`, `hover`) instead of text search when navigating Rust/Java/TypeScript — faster and more accurate than grep for symbol lookups.
- Commits are immutable in this workflow: fix issues by adding new commits, never rewriting history. `git revert` is fine when you need to undo something already merged.
- Before claiming a fix or feature works, run it and show the output — don't assert success without verification.
- Keep PRs scoped: don't bundle refactors into bug fixes or vice versa.

## Get Started

1. Clone `ggen-legacy` and open it in Claude Code.
2. Skim `CLAUDE.md`/`AGENTS.md` in the repo root for project-specific context.
3. Pick a small, well-scoped issue (a good first task is usually labeled `good-first-issue` or similar in the tracker) and walk through the fix-forward workflow end to end: branch, change, verify, PR.
4. Ask in the team channel if anything in this guide is unclear — it's meant to evolve as our usage patterns change.
