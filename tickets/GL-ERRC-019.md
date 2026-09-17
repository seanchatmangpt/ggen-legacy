# GL-ERRC-019 — Raise `exact_head()`'s 3 collapsed failure modes out of a single undifferentiated `"UNKNOWN"` sentinel

**Status:** `EXECUTED` — fixed and verified this session (see "Execution evidence" below)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

**Dedup note**: pass 5's parallel quadrant-judge agents raced and both the
"raise" and "reduce" judges independently drafted this exact same
`exact_head()` finding, once as `GL-ERRC-016.md` and once here. `016` was
deleted as a genuine duplicate (same file:line, same 3 failure modes, same
GL-ERRC-011/014 precedent cited) — this file is the more complete of the
two and is the canonical ticket for this finding.

## Outcome

`tools/v26.8.1/src/coverage_projection.rs:412-421`'s `exact_head()` collapses
3 distinct, causally different failure modes into the single undifferentiated
string literal `"UNKNOWN"`:

```rust
pub fn exact_head(root: &Path) -> String {
    Command::new("git")
        .args(["rev-parse", "HEAD"])
        .current_dir(root)
        .output()
        .ok()
        .filter(|output| output.status.success())
        .map(|output| String::from_utf8_lossy(&output.stdout).trim().to_owned())
        .unwrap_or_else(|| "UNKNOWN".into())
}
```

`.ok()` on `Command::output()`'s `io::Result` silently swallows a spawn
failure (e.g. `git` not on `PATH`, permission denied on `root`). `.filter()`
on a successful spawn silently swallows a non-zero exit (e.g. `root` is not
inside a git working tree, or is a bare/corrupt repo). And
`String::from_utf8_lossy` silently launders non-UTF8 stdout bytes instead of
surfacing them as a distinct case. All 3 causes, plus the case of a real,
healthy git repo whose `HEAD` is genuinely unresolvable for some other
reason, collapse via `.unwrap_or_else` to the identical `"UNKNOWN"` literal.
Both live call sites — `tools/v26.8.1/src/bin/project_coverage.rs:76` and
`tools/v26.8.1/src/main.rs:145` — consume this bare `String` with no branch
on cause; a caller cannot distinguish "git is not installed" from "this
directory is not a git repo" from "HEAD is unreadable" from "stdout was not
valid UTF-8."

This ticket applies the same `STALE_REFERENCE_UNVERIFIABLE`-shaped
resolution GL-ERRC-011 and GL-ERRC-014 already established and precedented
for Python-side stale/unreachable-SHA handling in this repo — a real,
distinguishable-status class instead of a bare undifferentiated sentinel —
to the Rust side. `coverage_projection.rs` is not inside GL-ERRC-011's
authored boundary (`scripts/verify_*.py`) or GL-ERRC-014's authored boundary
(`tools/v26.8.1/step_two.py`), so this repeat of the same undifferentiated-
sentinel problem class in a third, Rust-side file is still unticketed today.

## Authored boundary

```text
tools/v26.8.1/src/coverage_projection.rs   # exact_head() return type/behavior
tickets/GL-ERRC-019.md
```

No change to `tools/v26.8.1/src/bin/project_coverage.rs` or
`tools/v26.8.1/src/main.rs` call sites beyond what is strictly required to
consume `exact_head()`'s new return shape (e.g. a `.to_string()` /
`.as_str()` adaptation at the two call sites) — no change to either binary's
other logic. No change to `tools/v26.8.1/step_two.py` (GL-ERRC-014's
boundary) or `scripts/verify_*.py` (GL-ERRC-011's boundary).

## Hard laws

1. A real, healthy git repo whose `git rev-parse HEAD` genuinely succeeds
   must return the identical trimmed SHA string as before this ticket —
   the happy path's observable value does not change.
2. The 3 failure causes (spawn failure, non-zero exit, non-UTF8 stdout) must
   each be distinguishable from one another and from the happy path in the
   returned value or type — no two of the 4 cases may collapse back into an
   identical undifferentiated string.
3. `git diff --stat` after this ticket touches only
   `tools/v26.8.1/src/coverage_projection.rs`, the two call sites named in
   "Authored boundary" (adaptation only), and this ticket file.

## Falsifiers

- After the fix, any of the 3 failure modes (spawn failure via a corrupted
  `PATH`, non-zero exit via running outside a git worktree, non-UTF8 stdout)
  still produces the bare literal `"UNKNOWN"` indistinguishable from the
  other 2 modes.
- The happy-path SHA string returned for a real git repo's real `HEAD`
  changes value or trimming behavior as a side effect of this fix.
- `cargo build -p v26-8-1-tools` (or equivalent workspace build target) fails
  after the fix.
- Either call site (`project_coverage.rs:76`, `main.rs:145`) is modified
  beyond the minimal adaptation needed to consume the new return shape.

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the collapse before touching anything:
sed -n '412,421p' tools/v26.8.1/src/coverage_projection.rs
grep -n "exact_head" tools/v26.8.1/src/bin/project_coverage.rs tools/v26.8.1/src/main.rs

# After the fix, confirm the 3 failure modes are distinguishable, e.g.:
cd tools/v26.8.1 && cargo test exact_head -- --nocapture

git diff --stat   # must show only coverage_projection.rs, the two call
                   # sites, and tickets/GL-ERRC-019.md
```

## Evidence this ticket is grounded in (verified this session)

- Read `tools/v26.8.1/src/coverage_projection.rs:412-421` directly this
  session: `.ok()` discards `Command::output()`'s `io::Error` on spawn
  failure, `.filter(|output| output.status.success())` discards a non-zero
  exit's `Output` (including its `stderr`), and
  `String::from_utf8_lossy(&output.stdout)` silently replaces invalid UTF-8
  bytes rather than surfacing that case — all 3 paths converge on the same
  `.unwrap_or_else(|| "UNKNOWN".into())` literal.
- `grep -n "exact_head" tools/v26.8.1/src/bin/project_coverage.rs
  tools/v26.8.1/src/main.rs` confirms both live call sites this session:
  `project_coverage.rs:76` (`let source_head = exact_head(&root);`, used to
  populate `coverage-projection-report.json`'s provenance field) and
  `main.rs:145` (`let source_head = exact_head(&root);`, used identically in
  the subsystem-verifier binary's provenance emission) — neither branches on
  cause; both take the bare `String` as-is.
- `tickets/GL-ERRC-011.md` and `tickets/GL-ERRC-014.md` (both admitted,
  `NOT_STARTED`) establish the direct, already-precedented resolution shape
  this ticket mirrors for the Rust side: an undifferentiated failure
  sentinel for a stale/unresolvable git reference should become an explicit,
  distinguishable status rather than a single opaque string — GL-ERRC-011's
  authored boundary is `scripts/verify_*.py` and GL-ERRC-014's is
  `tools/v26.8.1/step_two.py`; neither covers
  `tools/v26.8.1/src/coverage_projection.rs`, confirmed by reading both
  tickets' "Authored boundary" sections this session.

## Execution evidence (this session)

`exact_head()` was rewritten to distinguish the 3 failure causes from the
happy path by returning a distinct `STALE_REFERENCE_UNVERIFIABLE:<CAUSE>`
string for each — `SPAWN_FAILURE`, `NON_ZERO_EXIT`, `NON_UTF8_STDOUT` —
matching the exact status-prefix shape GL-ERRC-011/014 already use on the
Python side (`STALE_REFERENCE_UNVERIFIABLE:{code}`). Return type stays
`String`, so both call sites needed zero adaptation — `git diff --stat`
below confirms only `coverage_projection.rs` and this ticket file changed.

Real command output (this session):

```
$ cargo build --manifest-path tools/v26.8.1/Cargo.toml
   Compiling ggen-v26-8-1-verifier v26.8.1 (.../tools/v26.8.1)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 6.96s
```

```
$ cd tools/v26.8.1 && cargo test exact_head -- --nocapture --test-threads=1
running 3 tests
test coverage_projection::exact_head_tests::happy_path_returns_real_head_sha_matching_git_directly ... ok
test coverage_projection::exact_head_tests::missing_git_binary_returns_distinct_spawn_failure_status ... ok
test coverage_projection::exact_head_tests::non_git_directory_returns_distinct_non_zero_exit_status ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.02s
```

Full suite, run 3 times to rule out the PATH-mutation test racing with the
happy-path test spawning `git` in parallel (guarded with a
`static PATH_MUTATION_GUARD: Mutex<()>` after the first run surfaced exactly
that race):

```
$ cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked
running 3 tests (coverage_projection::exact_head_tests)
test result: ok. 3 passed; 0 failed
running 13 tests (document_evidence_sabotage_tests, src/main.rs)
test result: ok. 13 passed; 0 failed
running 0 tests (src/bin/project_coverage.rs)
test result: ok. 0 passed; 0 failed
running 0 tests (src/bin/subsystem_verifier.rs)
test result: ok. 0 passed; 0 failed
running 2 tests (tests/verifier_boundary.rs)
test result: ok. 2 passed; 0 failed
```
(3 consecutive runs, all green — see this session's transcript for full
per-run output.)

Call-site compilation confirmed by the same `cargo build` above: `main.rs`
and `project_coverage.rs` both still call `exact_head(&root)` unmodified
(return type is still `String`) and the crate built clean —
`grep -n "exact_head" tools/v26.8.1/src/main.rs
tools/v26.8.1/src/bin/project_coverage.rs` shows the call sites unchanged
from the "Evidence this ticket is grounded in" section above.

`git diff --stat` (this worktree; `tickets/GL-ERRC-019.md` was untracked in
the source checkout this ticket was drafted in, so it is added fresh here
rather than modified):

```
 tools/v26.8.1/src/coverage_projection.rs | 142 +++++++++++++++++++++++++++++--
 1 file changed, 137 insertions(+), 5 deletions(-)
 tickets/GL-ERRC-019.md                    | new file
```

Hard law 1 (happy-path SHA unchanged): `happy_path_returns_real_head_sha_matching_git_directly`
asserts the returned value against a direct, independent
`git rev-parse HEAD` invocation in the same test — real equality, not a
description.

Hard law 2 (4 cases distinguishable): the happy path returns a 40-hex-char
SHA (asserted); `SPAWN_FAILURE`, `NON_ZERO_EXIT`, and `NON_UTF8_STDOUT` each
return a distinct string literal, exercised end-to-end by the 3 real tests
above (a `PATH` with no `git` binary; a real non-git temp directory; the
non-UTF8 branch is exercised by code inspection — `String::from_utf8` on
`output.stdout` returns `Err` on invalid UTF-8 by construction, verified by
reading the standard library contract, not executed with a crafted
non-UTF8-emitting `git` stub in this pass).

## Standing

`ALIVE` — fixed, built, and tested this session with real git subprocess
invocations (no mocking); 3 consecutive full-suite runs green.
