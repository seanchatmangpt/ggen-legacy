# GL-EXP-005 — Eliminate the regressed duplicate `fresh_git_head()` in `subsystem_verifier.rs`

**Status:** EXECUTED -- drafted by standing ultracode exploration cron (GL-EXP namespace), executed this session
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/src/bin/subsystem_verifier.rs:242-251` privately declares
`fn fresh_git_head(root: &Path) -> String`, a second, independent
implementation of "run `git rev-parse HEAD` in `root`, return the trimmed
SHA" that duplicates -- and has now regressed relative to -- the canonical
`pub fn exact_head` in `tools/v26.8.1/src/coverage_projection.rs:428-443`.
Confirmed this session via direct `Read` of both functions and
`diff <(sed -n '428,443p' tools/v26.8.1/src/coverage_projection.rs) <(sed -n '242,251p' tools/v26.8.1/src/bin/subsystem_verifier.rs)`:
the two bodies are structurally different, not a cosmetic rename. The private
copy is exactly the pre-fix shape GL-ERRC-019 replaced:

```rust
fn fresh_git_head(root: &Path) -> String {
    Command::new("git")
        .args(["rev-parse", "HEAD"])
        .current_dir(root)
        .output()
        .ok()                                              // swallows spawn failure
        .filter(|o| o.status.success())                     // swallows non-zero exit
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())  // launders non-UTF8 stdout
        .unwrap_or_else(|| "UNKNOWN".into())                 // collapses all 3 into one literal
}
```

`coverage_projection.rs::exact_head()`'s own doc comment (lines 405-427)
states it exists precisely to stop "distinguishing the 3 causally different
ways this can fail instead of collapsing them into a single undifferentiated
`"UNKNOWN"` sentinel (GL-ERRC-019)", returning instead
`STALE_REFERENCE_UNVERIFIABLE:SPAWN_FAILURE`,
`STALE_REFERENCE_UNVERIFIABLE:NON_ZERO_EXIT`, or
`STALE_REFERENCE_UNVERIFIABLE:NON_UTF8_STDOUT` for the three failure causes,
and the real, unmodified SHA string on the happy path. `fresh_git_head` still
has all three failure causes collapsed via `.ok()` /
`.filter(|o| o.status.success())` / `String::from_utf8_lossy` /
`.unwrap_or_else(|| "UNKNOWN".into())` -- the identical 3-cause collapse
GL-ERRC-019's own outcome section describes verbatim, now proven to exist a
second, unfixed time in the same crate.

Real call site confirmed at `subsystem_verifier.rs:471-478`:

```rust
let fresh_head = fresh_git_head(&root);
let source_head_matches = fresh_head == manifest.exact_source_head;
if !source_head_matches && !observe_only {
    bail!(
        "WRONG_SOURCE_HEAD: manifest claims {} but this checkout's HEAD is {}",
        manifest.exact_source_head,
        fresh_head
    );
}
```

A bare `"UNKNOWN"` surfacing in that error message (e.g. when this binary
runs in an environment where `git` isn't on `PATH`, or `root` isn't a git
working tree) hides which of the 3 causes actually fired -- exactly the
diagnosability gap GL-ERRC-019 closed for `exact_head()`'s callers, still
open here. `fresh_head` is also persisted verbatim into the on-disk report at
`verifier_fresh_source_head: fresh_head` (line 623, field declared
`verifier_fresh_source_head: String` at line 138), so the undifferentiated
sentinel would also propagate into
`.ggen/v26.8.1/subsystem-verifier-report.json` for any downstream consumer.

Confirmed this session that the fix is a pure drop-in: `main.rs:8-11` and
`project_coverage.rs:20-23` both already `use
v26_8_1_tools::coverage_projection::{..., exact_head, ...}` and call the
canonical function directly -- `subsystem_verifier.rs` is the sole remaining
binary that does not import it, exactly mirroring the
already-established-but-narrower pattern GL-EXP-001 names for
`resolve_root()` in this same file. `exact_head`'s return type
(`String`) is identical to `fresh_git_head`'s, and no other code in
`subsystem_verifier.rs` pattern-matches on the literal `"UNKNOWN"` string in
connection with `fresh_head` (confirmed via `grep -n "UNKNOWN"
tools/v26.8.1/src/bin/subsystem_verifier.rs` -- the file's other `"UNKNOWN"`
occurrences at lines 585/597 are for unrelated legacy-disposition string
literals, not `fresh_head`), so swapping the call is behavior-compatible at
the type level and strictly more diagnosable at the value level.

Confirmed via `grep -l fresh_git_head tickets/*.md` (zero matches this
session) that no existing ticket covers this duplicate. `GL-EXP-001.md`
(admitted, `NOT_STARTED`) already establishes the identical "eliminate the
private copy, import the canonical, already-fixed function" pattern for this
same binary's `resolve_root()` duplicate, one function below it in the same
file -- but that ticket's own Authored Boundary and Hard Laws name only
`resolve_root` (its Falsifiers grep specifically for `^fn resolve_root`, and
its Outcome section's diff spans lines 233-247 / 376-390, entirely disjoint
from `fresh_git_head`'s 242-251/428-443). This is a second, distinct
instance of the exact same anti-pattern, not covered by GL-EXP-001's
authored boundary, and additionally worse than GL-EXP-001's target because
this duplicate has actively regressed (lost a fix already landed on the
canonical function) rather than merely never having received it.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below. This ticket's
target function, `fresh_git_head`, is textually adjacent to but distinct
from GL-EXP-001's `resolve_root` target in the same file; the two tickets'
edits do not overlap line ranges as authored, but both touch
`subsystem_verifier.rs` and should not be executed concurrently without
re-checking line numbers against whichever lands first.)

```text
tools/v26.8.1/src/bin/subsystem_verifier.rs   # delete private fresh_git_head(), import canonical exact_head
tickets/GL-EXP-005.md
```

No change to `tools/v26.8.1/src/coverage_projection.rs` (the canonical
`exact_head` itself), `tools/v26.8.1/src/main.rs`, or
`tools/v26.8.1/src/bin/project_coverage.rs` -- those already call the
canonical function and are not touched. No change to
`tools/v26.8.1/tests/verifier_boundary.rs`'s test bodies -- its existing
`all_three_binaries_fail_closed_on_missing_root` and
`all_three_binaries_get_past_root_resolution_with_real_agents_md` tests
already exercise all three binaries black-box via real subprocess execution
and both currently pass (see Evidence below), so they serve as a build/link
regression proof for this ticket even though neither test directly exercises
`fresh_git_head`/`exact_head`'s head-mismatch path.

## Hard laws

1. `subsystem_verifier.rs`'s private `fn fresh_git_head` (lines 242-251) is
   deleted outright, not merely marked deprecated or left dead.
2. `subsystem_verifier.rs` calls the canonical
   `v26_8_1_tools::coverage_projection::exact_head` in its place (via a
   `use` import, matching `main.rs`'s and `project_coverage.rs`'s existing
   import style) at both call sites currently reading `fresh_git_head(&root)`
   (line 471) and the identifier `fresh_head` used at lines 472, 477, and
   623 is otherwise unchanged (still holds whatever `String` the head-lookup
   returns).
3. `tools/v26.8.1/src/coverage_projection.rs`'s canonical `exact_head` itself
   is not modified by this ticket -- this is a call-site consolidation, not
   a behavior change to the shared logic.
4. `WRONG_SOURCE_HEAD` error text at lines 474-478 and the persisted
   `verifier_fresh_source_head` report field at line 623 must, after this
   fix, be capable of showing a `STALE_REFERENCE_UNVERIFIABLE:<CAUSE>` value
   instead of a bare `"UNKNOWN"` when `git rev-parse HEAD` fails in `root` --
   i.e. the fix must actually route through `exact_head`'s cause-differentiated
   sentinel, not merely delete the dead code while leaving some other
   `"UNKNOWN"`-producing shim in place.
5. Both existing tests in `tools/v26.8.1/tests/verifier_boundary.rs`
   (`all_three_binaries_fail_closed_on_missing_root` and
   `all_three_binaries_get_past_root_resolution_with_real_agents_md`) must
   still pass unmodified after this ticket, proving the crate still builds
   and `subsystem_verifier`'s externally observable root-resolution behavior
   is undisturbed by this unrelated internal change.

## Falsifiers

- `grep -n "^fn fresh_git_head" tools/v26.8.1/src/bin/subsystem_verifier.rs`
  still matches after this ticket executes (private copy not actually
  removed).
- `grep -n "unwrap_or_else(|| \"UNKNOWN\"" tools/v26.8.1/src/bin/subsystem_verifier.rs`
  still matches after this ticket executes (the collapsing sentinel pattern
  survived under a different name).
- `cargo test --manifest-path tools/v26.8.1/Cargo.toml --test
  verifier_boundary --locked` fails or changes its passing test count from
  the current `2 passed; 0 failed`.
- `cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked` fails to
  compile after the import is added (e.g. a visibility or path error).
- `git diff --stat` after this ticket touches any file outside
  `tools/v26.8.1/src/bin/subsystem_verifier.rs` and `tickets/GL-EXP-005.md`.

**Checked against the real fix this session -- see `## Evidence` and
`## Standing` below for the actual observed output (superseding the
"not yet run" framing this section originally carried while the ticket
was still `NOT_STARTED`).**

## Acceptance (executed this session -- see Evidence/Standing below)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the duplication and its regression before touching anything:
diff <(sed -n '428,443p' tools/v26.8.1/src/coverage_projection.rs) \
     <(sed -n '242,251p' tools/v26.8.1/src/bin/subsystem_verifier.rs)
grep -n "^fn fresh_git_head" tools/v26.8.1/src/bin/subsystem_verifier.rs

# After the fix, confirm the private copy is gone and the import is present:
grep -n "^fn fresh_git_head" tools/v26.8.1/src/bin/subsystem_verifier.rs && echo "UNEXPECTED: still present"
grep -n "exact_head\|fresh_head" tools/v26.8.1/src/bin/subsystem_verifier.rs

# Confirm the crate still builds and the black-box regression tests still pass:
cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked
cargo test --manifest-path tools/v26.8.1/Cargo.toml --test verifier_boundary --locked

git diff --stat   # must show only tools/v26.8.1/src/bin/subsystem_verifier.rs + tickets/GL-EXP-005.md
```

## Evidence this ticket is grounded in (verified this session)

- Direct `Read` of `tools/v26.8.1/src/bin/subsystem_verifier.rs:220-280` --
  confirms `fn fresh_git_head` at lines 242-251, byte-for-byte as quoted in
  Outcome, and its call site at lines 470-479 (`let fresh_head =
  fresh_git_head(&root);` through the `WRONG_SOURCE_HEAD` bail).
- Direct `Read` of `tools/v26.8.1/src/coverage_projection.rs:400-459` --
  confirms `pub fn exact_head` at lines 428-443 with its GL-ERRC-019 doc
  comment (405-427) and the 3 distinct `STALE_REFERENCE_UNVERIFIABLE:*`
  return values, plus its own `#[cfg(test)] mod exact_head_tests` starting
  at line 445.
- `diff <(sed -n '428,443p' tools/v26.8.1/src/coverage_projection.rs)
  <(sed -n '242,251p' tools/v26.8.1/src/bin/subsystem_verifier.rs)` -- real
  output this session: fully divergent bodies (`match` on `Err`/`Ok(..) if
  !success`/`Ok(..)` with 3 distinct sentinel strings, vs. an `.ok().filter(
  ).map().unwrap_or_else()` chain collapsing to a single `"UNKNOWN"`).
- `grep -n "fresh_git_head\|fresh_head" tools/v26.8.1/src/bin/subsystem_verifier.rs`
  -- real output this session: declaration at 242, call at 471, comparison
  at 472, use in the bail message at 477, persisted into the report struct
  at 623 (`verifier_fresh_source_head: fresh_head`, field typed `String` at
  line 138).
- `sed -n '1,15p' tools/v26.8.1/src/main.rs` and `sed -n '15,25p'
  tools/v26.8.1/src/bin/project_coverage.rs` -- real output this session:
  both binaries already `use v26_8_1_tools::coverage_projection::{...,
  exact_head, ...}`, confirming the import is already the crate's
  established pattern and directly available (same package, `[lib] name =
  "v26_8_1_tools"`) with no new dependency.
- `grep -n "UNKNOWN\|verifier_fresh_source_head"
  tools/v26.8.1/src/bin/subsystem_verifier.rs` -- real output this session:
  confirms no other logic in the file pattern-matches on the literal
  `"UNKNOWN"` in connection with `fresh_head` specifically (the other
  `"UNKNOWN"`-adjacent lines, 359/576/585/597, are legacy-disposition string
  handling, unrelated to git-head resolution).
- `grep -l fresh_git_head tickets/*.md` -- real output this session: no
  matches (empty result, confirmed exit status and empty stdout); no ticket
  currently references this function.
- `cat tickets/GL-EXP-001.md` -- confirms its Outcome/Authored
  boundary/Hard laws/Falsifiers name only `resolve_root` (lines 375-391 /
  233-248), a disjoint line range and disjoint function from
  `fresh_git_head` (242-251) / `exact_head` (428-443) targeted here.
- `head -5 tickets/GL-ERRC-019.md` -- confirms that ticket's title and scope
  ("Raise `exact_head()`'s 3 collapsed failure modes out of a single
  undifferentiated `"UNKNOWN"` sentinel") is the fix `fresh_git_head` still
  lacks; `GL-ERRC-019.md` itself only ever touched
  `coverage_projection.rs`, never `subsystem_verifier.rs`.
- `ls tools/v26.8.1/tests/` -- confirms `verifier_boundary.rs` is the only
  test file in this crate's `tests/` directory, i.e. the same 2-test
  regression surface GL-EXP-001 relies on is the applicable one here too.
- `git rev-parse HEAD` -- `bce7f6386c4203784beaae426e40804636c4151a`, same
  base commit as GL-EXP-001, confirming both tickets are drafted against the
  identical working-tree state.

## Evidence

Falsifiers actually run this session (all 5 named in `## Falsifiers`
above, executed in this order):

1. `grep -n "^fn fresh_git_head" tools/v26.8.1/src/bin/subsystem_verifier.rs`
   -- expected no match, got no match (exit 1). Passed.
2. `grep -n 'unwrap_or_else(|| "UNKNOWN"' tools/v26.8.1/src/bin/subsystem_verifier.rs`
   -- expected no match, got no match (exit 1). Passed.
3. `cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked` -- clean
   build, no warnings. Passed.
4. `cargo test --manifest-path tools/v26.8.1/Cargo.toml --test
   verifier_boundary --locked` -- `2 passed; 0 failed; 0 ignored`, matching
   Hard Law 5's required count exactly. Passed.
5. `git diff --stat` (scoped review of authored files) -- full repo diff
   showed 17 changed files, but all 16 files other than
   `subsystem_verifier.rs` were already uncommitted/modified before this
   session started (confirmed against the initial `git status` call taken
   at session start, which showed the identical 17-file diff and the same
   untracked `GL-*.md` ticket set prior to any edit this session). This
   ticket's own edits are scoped exactly to `subsystem_verifier.rs` (the
   `fresh_git_head` deletion + `exact_head` import/call-site swap) and
   `tickets/GL-EXP-005.md` (this Status/Evidence/Standing update). Passed.

**`falsifiers_passed: true`** -- all 5 falsifiers above resolved to their
non-triggering (safe) outcome; none of the regression conditions they
guard against occurred.

Diff stat for the authored file, as observed this session:

```text
tools/v26.8.1/src/bin/subsystem_verifier.rs | 35 ++---------------------------
1 file changed, 2 insertions(+), 33 deletions(-)
```
(plus `tickets/GL-EXP-005.md`, untracked new-file content updated with this
Status/Evidence/Standing section.)

Separately, this session ran the repo-wide verification gate,
`just ci-all`, in `/Users/sac/ggen-legacy` (foreground background task,
waited for completion). Overall exit code: **0 (PASS)**.

- **Workspace 1 -- root** (`ggen-legacy-lsp` / `ggen-lsp`, `Cargo.toml` at
  repo root):
  - `cargo fmt --all -- --check`: PASS (no diff)
  - `cargo check --all-targets --locked`: PASS
  - `cargo clippy --all-targets --locked -- -D warnings`: PASS (no warnings)
  - `cargo test --all-targets --locked -- --test-threads=1`: PASS -- 18
    tests passed, 0 failed, 0 ignored, across lib unittests, main
    unittests, `tests/analysis.rs`, `tests/analysis_boundary.rs`,
    `tests/contract.rs`, `tests/exit_code.rs`, `tests/lsp_boundary.rs`.
- **Workspace 2 -- `tools/v26.8.1`** (`ggen-v26-8-1-verifier`, invoked via
  `just -f tools/v26.8.1/justfile {fmt,check,clippy}` plus a direct
  `cargo test`):
  - `fmt` (`cargo fmt --manifest-path Cargo.toml -- --check`): PASS
  - `check` (`cargo check --manifest-path Cargo.toml`): PASS
  - `clippy` (`cargo clippy --manifest-path Cargo.toml --all-targets -- -D
    warnings`): PASS (no warnings)
  - `cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets
    --locked -- --test-threads=1`: PASS -- 18 tests passed, 0 failed, 0
    ignored, across lib unittests (`coverage_projection`), main unittests
    (`document_evidence_sabotage_tests`, 13 cases), `project_coverage`/
    `subsystem_verifier` binary unittests (0 tests each), and
    `tests/verifier_boundary.rs` (2 tests, the same 2 cited in the
    falsifiers above).

Grand total across both workspaces: **36 tests passed, 0 failed, 0
ignored**. Full raw `just ci-all` log:
`/private/tmp/claude-501/-Users-sac-ggen-legacy/87a9b589-243d-4eb5-b50c-e957cd0f71db/scratchpad/ci-all.log`
(session-scoped scratchpad path -- not part of this repo's tracked tree).

Separately measured this session: `git status --porcelain -uall | wc -l`
-> real output **97** (97 changed/untracked paths in the working tree,
current branch `agent/add-dsrust-groq-disposition-proposer`). This count
reflects the whole working tree, not just this ticket's own edits --
per the falsifier-5 analysis above, 96 of those 97 paths pre-date this
ticket's own two-file edit.

## Standing

`PARTIAL_ALIVE` -- executed this session. `subsystem_verifier.rs`'s private
`fresh_git_head()` (was lines 240-249 at execution time; the file's line
numbers had already shifted from the ticket's original 242-251 quote because
GL-EXP-001's `resolve_root` deletion had already landed uncommitted in this
same working tree) is deleted outright; the sole call site (was line 451, now
440) now reads `let fresh_head = exact_head(&root);`, reached via
`use v26_8_1_tools::coverage_projection::{exact_head, resolve_root};`
(line 37), matching `main.rs`'s and `project_coverage.rs`'s existing braced
multi-import style. `fresh_head`'s downstream uses (comparison, the
`WRONG_SOURCE_HEAD` bail message, and `verifier_fresh_source_head: fresh_head`
in the persisted report) are byte-for-byte unchanged, per Hard Law 2.

Real falsifier output this session:

```text
$ grep -n "^fn fresh_git_head" tools/v26.8.1/src/bin/subsystem_verifier.rs
(no output, exit 1)

$ grep -n 'unwrap_or_else(|| "UNKNOWN"' tools/v26.8.1/src/bin/subsystem_verifier.rs
(no output, exit 1)

$ cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked
   Compiling ggen-v26-8-1-verifier v26.8.1 (/Users/sac/ggen-legacy/tools/v26.8.1)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.76s

$ cargo test --manifest-path tools/v26.8.1/Cargo.toml --test verifier_boundary --locked
running 2 tests
test all_three_binaries_fail_closed_on_missing_root ... ok
test all_three_binaries_get_past_root_resolution_with_real_agents_md ... ok
test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 7.33s
```

`git diff tools/v26.8.1/src/bin/subsystem_verifier.rs` confirms the edit
introduced by this ticket is exactly: the new braced `use` import, the
`fresh_git_head` fn deletion, and the one call-site swap -- no other hunk in
that file's diff is attributable to this ticket (the `legacy_disposition_summary`
field removal and `resolve_root` deletion hunks pre-date this session's work,
already uncommitted in the working tree from other tickets, confirmed via
`git status` before this ticket's edits began). This ticket's own edits did
not touch any file other than `subsystem_verifier.rs` and this ticket file.

Repo-wide `just ci-all` (both workspaces: root `ggen-legacy-lsp`/`ggen-lsp`
and `tools/v26.8.1`) also re-run this session and passed cleanly end to
end -- exit code 0, 36 total tests passed (18 + 18), 0 failed, 0 ignored,
fmt/check/clippy clean in both workspaces (see `## Evidence` above for the
full per-workspace breakdown). This is a stronger confirmation than the
scoped `verifier_boundary` test alone (Hard Law 5's minimum bar): it
additionally proves the sibling `ggen-legacy-lsp`/`ggen-lsp` workspace,
which does not depend on `tools/v26.8.1` at all, was unaffected, and that
neither workspace's clippy lints regressed from this ticket's `use`-import
and call-site change.

`PARTIAL_ALIVE` (not full `ALIVE`) because this ticket's own scope is a
single-function call-site consolidation inside a much larger, mostly
`NOT_STARTED` `GL-EXP`/`GL-ERRC` backlog (`tickets/OVERLAPS.md` lists
several sibling `NOT_STARTED` tickets touching the same file), and because
the working tree carries 97 total changed/untracked paths from other,
independently-tracked tickets -- this ticket's own authored boundary is
fully executed and verified, but repo-wide standing is not being claimed
beyond what this ticket touched.
