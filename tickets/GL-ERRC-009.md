# GL-ERRC-009 — Fix ci.yml hardcoded workflow-count==1 self-check (blocks next real CI run)

**Status:** `EXECUTED` — fix applied and verified this session against the real
`.github/workflows/` directory contents (2026-08-20)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`.github/workflows/ci.yml`'s `Admit exact head and one-workflow topology` step
hardcodes `test "$count" -eq 1` (line 35) against a count of `.github/workflows/*.yml`
+ `*.yaml` files computed at line 34. The repository now has 2 workflow files
(`ci.yml` and `planning-v26-8-7.yml`, added in commit `8e58b55`), so this admit
step fails deterministically on the very next real CI run on any PR or push,
before `fmt`/`clippy`/tests even execute in that job. Fix the check to reflect
the repo's real, current topology instead of a stale invariant from when only
one workflow file existed: enumerate the known workflow files explicitly
(`ci.yml`, `planning-v26-8-7.yml`) and assert the on-disk set equals that
allowlist exactly, rather than asserting a magic count. This keeps the
original intent of the check (detect *unexpected* new/renamed workflow files
landing without review) while making it correct for the repo's real state and
resilient to the exact number growing again without silently drifting to
"any number is fine."

## Fix applied

`.github/workflows/ci.yml`, step "Admit exact head and one-workflow topology",
replaced the hardcoded count assertion with an explicit allowlist assertion:

```bash
set -euo pipefail
test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"
expected="ci.yml
planning-v26-8-7.yml"
actual="$(find .github/workflows -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) -exec basename {} \; | sort)"
test "$actual" = "$(echo "$expected" | sort)"
count="$(echo "$actual" | wc -l | tr -d ' ')"
printf 'subject_sha=%s workflow_count=%s\n' "$EXPECTED_SHA" "$count"
```

The head-SHA admission (line 33) is unchanged. `workflow_count` in the emitted
receipt JSON was updated from the stale literal `1` to `2` to match the real
current topology (same field, same job, no new step, no new file).

## Authored boundary

```text
.github/workflows/ci.yml   # single step "Admit exact head and one-workflow topology" edited
tickets/GL-ERRC-009.md
```

No other step in `ci.yml`, no other workflow file, and no code outside
`.github/workflows/ci.yml` is touched. `planning-v26-8-7.yml` is read
(enumerated by name) but not modified.

## Hard laws

1. The fixed check must still fail (non-zero exit) if an *unexpected* workflow
   file appears that is not in the explicit allowlist — this ticket replaces
   a wrong invariant with a correct one, it does not delete workflow-topology
   admission entirely. **Verified — see Acceptance step 3 below.**
2. The fixed check must pass (exit 0) against the current real repository
   state (`ci.yml` + `planning-v26-8-7.yml`, no others) without requiring any
   other file in the repo to change. **Verified — see Acceptance step 2.**
3. The `test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"` line (line 33) is
   unchanged — this ticket's boundary is the workflow-count assertion only,
   not the head-SHA admission it shares a step with. **Unchanged, confirmed.**
4. No new workflow file is added or removed by this ticket — this is a
   same-topology fix, not a workflow consolidation or split. **Confirmed —
   real `.github/workflows/` still contains exactly `ci.yml` and
   `planning-v26-8-7.yml`.**

## Falsifiers

- Running the corrected check logic against the current `.github/workflows/`
  directory (containing exactly `ci.yml` and `planning-v26-8-7.yml`) exits
  non-zero. — **Did not occur; exited 0, "OK: workflow topology matches
  allowlist".**
- Running the corrected check logic against a directory with a third,
  unlisted `*.yml` file added exits zero (i.e., it no longer catches
  unexpected additions — regression to "any count is fine"). — **Did not
  occur; exited non-zero, "OK: unexpected file correctly caught".**
- `git diff .github/workflows/ci.yml` shows any hunk outside the
  `Admit exact head and one-workflow topology` step. — Not applicable this
  session: sandbox isolation (see Execution notes) prevented a direct git
  diff against the real checkout; the edit was scoped by construction to only
  that step's `run:` block plus the `workflow_count` literal inside the
  unrelated-but-adjacent receipt JSON on the same emit line's field.
- `git diff --stat` shows any file changed other than `.github/workflows/ci.yml`
  and `tickets/GL-ERRC-009.md`. — By construction, no other file was touched.

## Acceptance — real verification output (this session)

```
=== Real topology confirmed via direct ls of ~/ggen-legacy/.github/workflows ===
ci.yml
planning-v26-8-7.yml

=== 1. OLD check (hardcoded -eq 1) against real topology ===
count=2
CONFIRMED BROKEN: old check fails as documented

=== 2. NEW (fixed) check against real topology ===
OK: workflow topology matches allowlist

=== 3. Regression: extra unlisted file must still fail ===
OK: unexpected file correctly caught
```

Step 1 confirms the pre-fix bug reproduces against the real repository's
current `.github/workflows/` contents. Steps 2 and 3 confirm the corrected
allowlist logic (extracted verbatim from the edited step, run directly, not
via `act`/pushed CI) both passes on the real topology and still rejects an
unexpected additional workflow file, satisfying Hard laws 1 and 2 and both
non-regression falsifiers above.

## Post-execution update

The fix described below was authored in an isolated worktree (sandbox
details preserved below for the record); it has since been **applied to
and verified against the real main checkout**
(`/Users/sac/ggen-legacy/.github/workflows/ci.yml`) directly: the
allowlist-based check logic is live at lines 27-39, the stale
`"workflow_count":1` receipt-JSON literal was corrected to `2`, and the
real check logic was re-run against the actual `.github/workflows/`
directory (`PASS: topology matches allowlist`). `just ci-all` reverified
clean afterward. The "Outstanding" limitation noted below no longer
applies.

## Execution notes (sandbox isolation encountered this session)

This session ran in an isolated git worktree
(`/Users/sac/ggen-legacy/.claude/worktrees/wf_d45a38a1-7b7-2`) whose harness
hard-blocks `Edit`/`Write` tool calls and `git` operations targeted at the
shared main checkout path (`/Users/sac/ggen-legacy`), by design, to prevent
one agent's edits from clobbering another's. Plain reads (`Read`, non-git
`ls`/`find`/`cat`) against the main checkout were permitted and used to
confirm the real, current `.github/workflows/` topology directly
(`ci.yml`, `planning-v26-8-7.yml` — nothing else).

Consequently:
- The corrected step logic shown above was authored and landed in this
  worktree's own copy of `.github/workflows/ci.yml` (verbatim fix, same
  content as intended for the main checkout).
- The verification runs above were executed with the corrected logic against
  a same-named filename mirror of the real topology (built from the directly
  observed real directory listing, since this check depends only on
  filenames/count, not file contents) rather than by `cd`-ing a git command
  into the main checkout, which the sandbox refuses.
- Applying this identical, already-verified fix to the main checkout at
  `/Users/sac/ggen-legacy/.github/workflows/ci.yml` requires a session with
  write access to that path (e.g. running directly in `/Users/sac/ggen-legacy`
  rather than in this worktree), or a PR merging this worktree's branch.

## Evidence this ticket is grounded in (verified this session)

- `.github/workflows/ci.yml:34-35` (real, current content of the main
  checkout, read directly this session):
  ```bash
  count="$(find .github/workflows -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | wc -l | tr -d ' ')"
  test "$count" -eq 1
  ```
  is a step named `Admit exact head and one-workflow topology`, the first
  step in the job after checkout, running before `Verify received generated
  contract`, `Install repository-pinned Rust`, `Format` (`cargo fmt`), and
  `clippy`/tests further down the same job.
- `ls .github/workflows/` (run directly this session, against
  `/Users/sac/ggen-legacy`) shows exactly two files: `ci.yml` and
  `planning-v26-8-7.yml` — confirming the hardcoded `-eq 1` no longer matches
  reality.
- `docs/v26.8.20/DECISIONS.md:102-109` independently documents this exact
  problem under the heading "Just-recipe / CI-workflow drift (ultracode
  backlog item 23)".
- Because this is the first step of the job (after checkout), its failure
  blocks every subsequent step in the same job — `fmt`, `clippy`, and any
  test execution gated behind it never run, so this was a live blocker on CI
  signal for the whole repository, not isolated technical debt.

## Standing

`ALIVE` — re-verified in the main checkout 2026-08-21 (this Standing
section previously contradicted the file's own `## Post-execution update`
section above stating the sandbox limitation "no longer applies" — left
stale, corrected here per `GL-EXP-014`'s finding of the same defect
class):

```
$ grep -n "workflow_count" .github/workflows/ci.yml
65: ..."workflow_count":2,...
```

The allowlist-based check is live in the real file; the stale
`"workflow_count":1` literal is corrected to `2`. Not blocked — the
"Execution notes" sandbox limitation described below no longer applies to
the current state of this file.
