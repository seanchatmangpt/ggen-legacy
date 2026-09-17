# GL-EXP-001 — Eliminate the byte-for-byte duplicate `resolve_root()` in `subsystem_verifier.rs`

**Status:** EXECUTED -- private `resolve_root()` deleted from
`subsystem_verifier.rs` (was lines 375-391) and replaced with
`use v26_8_1_tools::coverage_projection::resolve_root;` (line 37), verified
this session (see "Execution evidence" section below for real command
output).
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/src/bin/subsystem_verifier.rs:375-391` privately re-implements
`resolve_root()` -- the same "explicit `--root <path>`, else walk up from cwd
looking for `AGENTS.md`" logic already defined once, canonically, as
`pub fn resolve_root` in `tools/v26.8.1/src/coverage_projection.rs:232-248`
(part of the crate's `v26_8_1_tools` lib target). Confirmed this session via
`diff <(sed -n '233,247p' tools/v26.8.1/src/coverage_projection.rs) <(sed -n '376,390p' tools/v26.8.1/src/bin/subsystem_verifier.rs)`:
the only diff line is `std::env::current_dir()?` (canonical) vs.
`env::current_dir()?` (private copy) -- the same call via a different `use`
alias; the walk-up-for-`AGENTS.md` body is otherwise character-for-character
identical.

Both of the crate's other two binaries already import and reuse the
canonical function instead of re-declaring it:

- `tools/v26.8.1/src/main.rs:10` imports `resolve_root` from
  `v26_8_1_tools::coverage_projection`, and its own line 326 carries the
  comment `// resolve_root / exact_head now live in v26_8_1_tools::coverage_projection`
  -- i.e. `main.rs` was itself already migrated off a private copy at some
  point.
- `tools/v26.8.1/src/bin/project_coverage.rs:21-22` imports the same
  canonical `resolve_root` and calls it directly at line 62.

`subsystem_verifier.rs` is the sole remaining holdout with a private copy
(`fn resolve_root` at line 375, called internally at line 410). The crate's
own `Cargo.toml` already declares a `[lib] name = "v26_8_1_tools"` alongside
all three `[[bin]]` targets in the same package, so `subsystem_verifier.rs`
importing from the lib is not a new architectural pattern -- it is the
existing pattern the other two binaries already follow, applied to the one
binary that doesn't yet follow it.

The crate's own test suite already names this duplication as a known,
unaddressed issue: `tools/v26.8.1/tests/verifier_boundary.rs:12-14`'s doc
comment on `all_three_binaries_fail_closed_on_missing_root` reads "All three
binaries share the same `resolve_root` walk-up-for-AGENTS.md logic (see
`src/coverage_projection.rs::resolve_root` **and the copies in each
`src/bin/*.rs`**)" -- written in the plural, as if more than one binary still
carried a private copy, when in fact (per the import-site check above) only
`subsystem_verifier.rs` does today.

Searched all 23 other `GL-*.md` tickets in `tickets/` (`grep -l
"subsystem_verifier" tickets/*.md`) for any that reference this specific
duplication: 4 mention `subsystem_verifier` at all (`GL-AUTO-001.md`,
`GL-ERRC-015.md`, `GL-ERRC-016.md`, `GL-ERRC-019.md`), and none of the four
touch its private `resolve_root` copy -- `GL-ERRC-016` targets
`run_subsystem_verifier()`'s `cargo build` invocation in
`coverage_projection.rs` (a different function, already fixed with
`--locked` per the working tree's current `git diff`), and `GL-ERRC-015`/
`GL-ERRC-019` only quote `subsystem_verifier.rs`'s test-harness output
incidentally. This finding is new.

**Real drift risk this eliminates:** the private copy means a future
correctness fix to the canonical `resolve_root()` (for example, the kind of
cause-differentiated error handling `GL-ERRC-019`/`coverage_projection.rs`'s
own `exact_head()` recently added, per this session's `git diff
tools/v26.8.1/src/coverage_projection.rs`) would silently not propagate to
`subsystem_verifier.rs`'s private copy unless a human remembers to
hand-sync a second file that looks -- and until now, functionally is --
identical. Importing the canonical function removes that silent-divergence
window entirely rather than requiring anyone to remember to keep two
copies in lockstep.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below.)

```text
tools/v26.8.1/src/bin/subsystem_verifier.rs   # delete private resolve_root(), import canonical
tickets/GL-EXP-001.md
```

No change to `tools/v26.8.1/src/coverage_projection.rs` (the canonical
`resolve_root` itself), `tools/v26.8.1/src/main.rs`, or
`tools/v26.8.1/src/bin/project_coverage.rs` -- those already call the
canonical function and are not touched. No change to
`tools/v26.8.1/tests/verifier_boundary.rs`'s test bodies (its existing
`all_three_binaries_fail_closed_on_missing_root` and
`all_three_binaries_get_past_root_resolution_with_real_agents_md` tests
already exercise all three binaries' root-resolution behavior black-box via
real subprocess execution, so they serve as this ticket's regression proof
unmodified); only the stale plural "copies in each `src/bin/*.rs`" doc
comment on that test may be corrected to singular as part of this ticket,
since after the fix only zero (not one, not several) binaries carry a
private copy.

**Execution note on the optional doc-comment correction:** this section's
"may be corrected" permission for `verifier_boundary.rs`'s stale plural doc
comment directly conflicts with this ticket's own Falsifiers and Acceptance
sections, both of which treat *any* diff outside
`tools/v26.8.1/src/bin/subsystem_verifier.rs` and `tickets/GL-EXP-001.md` as
a failure condition. Since the doc-comment edit was only ever optional
("may"), while the diff-scope restriction is stated as a hard, mechanically
checked failure condition, execution left `verifier_boundary.rs` completely
untouched -- satisfying the stricter of the two constraints. The plural
doc-comment wording is now stale (post-fix, zero binaries carry a private
copy) but out of this ticket's executed scope.

## Hard laws

1. `subsystem_verifier.rs`'s private `fn resolve_root` (lines 375-391) is
   deleted outright, not merely marked deprecated or left dead.
   **DONE** -- `grep -n "^fn resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs`
   returns no match.
2. `subsystem_verifier.rs` calls the canonical
   `v26_8_1_tools::coverage_projection::resolve_root` in its place (via a
   `use` import, matching `main.rs`'s and `project_coverage.rs`'s existing
   import style) -- behavior at the call site (line 410) is unchanged.
   **DONE** -- `use v26_8_1_tools::coverage_projection::resolve_root;` added
   at line 37; call site `let root = resolve_root(&args)?;` (now line 393
   after the deletion shifted line numbers) unchanged.
3. `tools/v26.8.1/src/coverage_projection.rs`'s canonical `resolve_root`
   itself is not modified by this ticket -- this is a call-site
   consolidation, not a behavior change to the shared logic.
   **DONE** -- `git diff --stat tools/v26.8.1/src/coverage_projection.rs`
   is empty (file untouched).
4. Both existing tests in `tools/v26.8.1/tests/verifier_boundary.rs`
   (`all_three_binaries_fail_closed_on_missing_root` and
   `all_three_binaries_get_past_root_resolution_with_real_agents_md`) must
   still pass unmodified after this ticket, proving `subsystem_verifier`'s
   externally observable root-resolution behavior (exit code, stderr
   wording, and the positive real-`AGENTS.md` path) is bit-for-bit
   unchanged despite the internal implementation now being a shared import
   instead of a private copy.
   **DONE** -- see Execution evidence below: `2 passed; 0 failed`, same as
   the pre-fix baseline.

## Falsifiers

- `grep -n "^fn resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs`
  still matches after this ticket executes (private copy not actually
  removed). **Checked post-fix: no match (falsifier did not trigger).**
- `cargo test --manifest-path tools/v26.8.1/Cargo.toml --test
  verifier_boundary --locked` fails or changes its passing test count from
  the current `2 passed; 0 failed`. **Checked post-fix: still `2 passed; 0
  failed` (falsifier did not trigger).**
- `cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked` fails to
  compile after the import is added (e.g. a visibility or path error).
  **Checked post-fix: builds clean, `Finished` (falsifier did not
  trigger).**
- `git diff --stat` after this ticket touches any file outside
  `tools/v26.8.1/src/bin/subsystem_verifier.rs` and `tickets/GL-EXP-001.md`.
  **Checked post-fix: `git diff --stat` shows only
  `tools/v26.8.1/src/bin/subsystem_verifier.rs` modified (1 file changed, 1
  insertion(+), 18 deletions(-)); `tickets/GL-EXP-001.md` is a new,
  previously-untracked file in this worktree (falsifier did not trigger).**

## Acceptance (executed this session -- real output below)

```bash
cd /Users/sac/ggen-legacy/.claude/worktrees/wf_14d41261-3fe-3
# Reconfirm the duplication before touching anything:
diff <(sed -n '233,247p' tools/v26.8.1/src/coverage_projection.rs) \
     <(sed -n '376,390p' tools/v26.8.1/src/bin/subsystem_verifier.rs)
grep -n "^fn resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs

# After the fix, confirm the private copy is gone and the import is present:
grep -n "^fn resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs && echo "UNEXPECTED: still present"
grep -n "resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs

# Confirm the crate still builds and the black-box regression tests still pass:
cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked
cargo test --manifest-path tools/v26.8.1/Cargo.toml --test verifier_boundary --locked

git diff --stat   # must show only tools/v26.8.1/src/bin/subsystem_verifier.rs + tickets/GL-EXP-001.md
```

## Execution evidence (real output this session)

Diff of the private copy (pre-fix) vs. the canonical function -- confirmed
identical modulo the `std::env::` vs. `env::` alias, consistent with the
ticket's original finding.

Post-fix confirmation, private function removed:

```text
$ grep -n "^fn resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs
(no output -- not present)

$ grep -n "resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs
37:use v26_8_1_tools::coverage_projection::resolve_root;
393:    let root = resolve_root(&args)?;
```

Final diff of `subsystem_verifier.rs` (1 file changed, 1 insertion(+), 18
deletions(-)):

```diff
@@ -34,6 +34,7 @@ use std::env;
 use std::fs;
 use std::path::{Path, PathBuf};
 use std::process::Command;
+use v26_8_1_tools::coverage_projection::resolve_root;

 const THIS_BINARY_SOURCE_REL: &str = "tools/v26.8.1/src/bin/subsystem_verifier.rs";
 const MANIFEST_REL: &str = ".ggen/v26.8.1/subsystem-evidence-manifest.json";
@@ -372,24 +373,6 @@ fn extract_quoted(s: &str) -> Option<String> {
     Some(rest[..end].to_owned())
 }

-fn resolve_root(args: &[String]) -> Result<PathBuf> {
-    let explicit = args
-        .windows(2)
-        .find(|pair| pair[0] == "--root")
-        .map(|pair| PathBuf::from(&pair[1]));
-    let mut current = explicit.unwrap_or(env::current_dir()?);
-    loop {
-        if current.join("AGENTS.md").is_file() {
-            return current
-                .canonicalize()
-                .context("canonicalize repository root");
-        }
-        if !current.pop() {
-            bail!("repository root not found; pass --root <path>");
-        }
-    }
-}
-
 fn manifest_path(args: &[String], root: &Path) -> PathBuf {
     args.windows(2)
         .find(|pair| pair[0] == "--manifest")
```

`cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked`:

```text
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.03s
```
(exit 0, no warnings, no errors)

`cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked`
(relevant tail):

```text
     Running unittests src/lib.rs (tools/v26.8.1/target/debug/deps/v26_8_1_tools-...)
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

     Running unittests src/main.rs (tools/v26.8.1/target/debug/deps/ggen_v26_8_1_verifier-...)
test result: ok. 13 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

     Running unittests src/bin/project_coverage.rs (...)
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

     Running unittests src/bin/subsystem_verifier.rs (...)
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

     Running tests/verifier_boundary.rs (tools/v26.8.1/target/debug/deps/verifier_boundary-...)
running 2 tests
test all_three_binaries_fail_closed_on_missing_root ... ok
test all_three_binaries_get_past_root_resolution_with_real_agents_md ... ok
test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

All 5 test binaries in the crate: `ok`, 0 failures total (15 passed across
`lib.rs` + `main.rs` + `project_coverage.rs` + `subsystem_verifier.rs` unit
tests + `verifier_boundary.rs` integration tests combined). The two
`verifier_boundary` tests this ticket's Hard Law 4 names both pass, matching
the pre-fix baseline (`2 passed; 0 failed`) exactly -- `subsystem_verifier`'s
externally observable root-resolution behavior is unchanged.

`git diff --stat` (post-fix, in worktree
`.claude/worktrees/wf_14d41261-3fe-3`):

```text
 tools/v26.8.1/src/bin/subsystem_verifier.rs | 19 +------------------
 1 file changed, 1 insertion(+), 18 deletions(-)
```

Only `subsystem_verifier.rs` is modified; `tickets/GL-EXP-001.md` itself did
not exist as a tracked file in this worktree's branch history prior to this
session (the branch predates this ticket's drafting in the shared
checkout), so it is added here rather than shown as a modification -- both
paths named in the Authored boundary, no other path touched.

## Standing

`PARTIAL_ALIVE` -- executed and verified this session. Private
`resolve_root()` deleted from `subsystem_verifier.rs`; canonical
`v26_8_1_tools::coverage_projection::resolve_root` imported and called in
its place; canonical function itself unmodified; both named regression
tests in `verifier_boundary.rs` pass unmodified with the same `2 passed; 0
failed` count as the pre-fix baseline; crate builds clean with `--locked`;
diff scope confined to the two authored paths. Ceiling remains
`PARTIAL_ALIVE` (not promoted to full `ALIVE`) because this execution
happened in an isolated worktree with no merge authority, per this ticket's
own "Publication: draft pull request; no merge authority" -- the fix is
real and verified, but not yet merged to `main`.
