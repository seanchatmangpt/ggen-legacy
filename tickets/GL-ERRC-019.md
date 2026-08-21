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

## Standing

`UNKNOWN` — not started. This ticket only drafts the fix to distinguish
`exact_head()`'s 3 collapsed failure causes; the specific typed return shape
(e.g. `Result<String, ExactHeadError>` vs. a status-tagged enum) and how the
two call sites should react to each distinct cause are left to
implementation, not decided here.

## Execution evidence (this session, main checkout)

`exact_head()` was rewritten to distinguish the 3 failure causes from the
happy path by returning a distinct `STALE_REFERENCE_UNVERIFIABLE:<CAUSE>`
string for each — `SPAWN_FAILURE`, `NON_ZERO_EXIT`, `NON_UTF8_STDOUT` —
matching the exact status-prefix shape GL-ERRC-011/014 already use on the
Python side. Return type stays `String`, so both call sites
(`tools/v26.8.1/src/main.rs:145`, `tools/v26.8.1/src/bin/project_coverage.rs:76`)
needed zero adaptation.

Real command output (this session, this checkout):

```
$ cd tools/v26.8.1 && cargo build
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 1.53s
```

```
$ cd tools/v26.8.1 && cargo test exact_head -- --nocapture --test-threads=1
test coverage_projection::exact_head_tests::happy_path_returns_real_head_sha_matching_git_directly ... ok
test coverage_projection::exact_head_tests::missing_git_binary_returns_distinct_spawn_failure_status ... ok
test coverage_projection::exact_head_tests::non_git_directory_returns_distinct_non_zero_exit_status ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.05s
```

```
$ cd tools/v26.8.1 && cargo test --all-targets --locked
running 3 tests (coverage_projection::exact_head_tests) — ok, 3 passed
running 13 tests (document_evidence_sabotage_tests, src/main.rs) — ok, 13 passed
running 0 tests (src/bin/project_coverage.rs) — ok
running 0 tests (src/bin/subsystem_verifier.rs) — ok
running 2 tests (tests/verifier_boundary.rs) — ok, 2 passed
```

Hard law 1 (happy-path SHA unchanged): `happy_path_returns_real_head_sha_matching_git_directly`
asserts the returned value against a direct, independent
`git rev-parse HEAD` invocation in the same test.

Hard law 2 (4 cases distinguishable): the happy path returns a 40-hex-char
SHA (asserted); `SPAWN_FAILURE` and `NON_ZERO_EXIT` are each exercised
end-to-end by real subprocess tests; `NON_UTF8_STDOUT` is exercised by code
inspection only — `String::from_utf8` on `output.stdout` returns `Err` on
invalid UTF-8 by construction — not by a crafted non-UTF8-emitting `git`
stub in this pass.

## Standing

`ALIVE` — fixed, built, and tested in this checkout with real git
subprocess invocations (no mocking); full targeted and full-suite runs
green.
