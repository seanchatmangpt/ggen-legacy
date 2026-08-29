# GL-ERRC-015 — Eliminate dead `read_coverage_csv_bytes()` in `tools/v26.8.1/src/coverage_projection.rs`

**Status:** EXECUTED
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/src/coverage_projection.rs:233` defines `pub fn
read_coverage_csv_bytes(root: &Path) -> Result<Vec<u8>>`, which reads the
on-disk `coverage-matrix.csv` bytes verbatim (no deserialize/reserialize
round-trip). It has zero callers anywhere in `tools/v26.8.1/src/` — the only
match for its name repo-wide (scoped to that crate) is its own definition.
Because it is `pub`, it is invisible to clippy's default `dead_code` lint
(which only fires on private items), so the crate's existing "clean clippy"
claim does not contradict this finding — clippy was never checking this
function. By contrast, the sibling function `exact_head` (same file, line
412) has two real call sites: `tools/v26.8.1/src/main.rs:145` and
`tools/v26.8.1/src/bin/project_coverage.rs:76`, both via the
`v26_8_1_tools::coverage_projection::exact_head` re-export. This ticket
removes the dead function only; `exact_head` and every other function in the
file are untouched.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before assuming sole ownership of a path below.)

```text
tools/v26.8.1/src/coverage_projection.rs   # delete read_coverage_csv_bytes() only
tickets/GL-ERRC-015.md
```

No change to `exact_head`, `write_coverage_csv`, `serialize_coverage_csv`, or
any other function in `coverage_projection.rs`. No change to
`tools/v26.8.1/src/main.rs`, `tools/v26.8.1/src/bin/project_coverage.rs`, or
any other file in the crate.

## Hard laws

1. Only `read_coverage_csv_bytes` (its doc comment and body, lines 229–235)
   is deleted from `coverage_projection.rs` — no other function, struct,
   constant, or import in the file is touched.
2. `cargo build`/`cargo check` for the `v26_8_1_tools` crate must succeed
   identically before and after this ticket (the function has no callers, so
   removing it cannot break compilation).
3. `git diff --stat` after this ticket touches only
   `tools/v26.8.1/src/coverage_projection.rs` and this ticket file.

## Falsifiers

- A caller of `read_coverage_csv_bytes` exists anywhere in the repo
  (`grep -rn "read_coverage_csv_bytes"` returns more than the definition
  line after removal fails to compile, or a match exists outside
  `tools/v26.8.1/src/coverage_projection.rs` before removal).
- `cargo build -p v26_8_1_tools` (or equivalent) fails after the deletion.
- `git diff --stat` shows any file other than
  `tools/v26.8.1/src/coverage_projection.rs` and `tickets/GL-ERRC-015.md`
  changed.
- `exact_head` or any other function's line count, signature, or behavior
  changes as a side effect of this fix.

## Acceptance (executed this session)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm dead-code premise before touching anything:
grep -rn "read_coverage_csv_bytes" tools/v26.8.1/src/
# Expect exactly one match: the definition at coverage_projection.rs:233

# After deletion:
grep -n "read_coverage_csv_bytes" tools/v26.8.1/src/coverage_projection.rs \
  && echo "STILL PRESENT (ticket not complete)" || echo "removed"
cd tools/v26.8.1 && cargo build 2>&1 | tail -20

git diff --stat   # must show only src/coverage_projection.rs + tickets/GL-ERRC-015.md
```

## Evidence this ticket is grounded in (verified this session)

- `grep -rn "read_coverage_csv_bytes" tools/v26.8.1/src/` returns exactly one
  line: `tools/v26.8.1/src/coverage_projection.rs:233:pub fn
  read_coverage_csv_bytes(root: &Path) -> Result<Vec<u8>> {` — the
  definition itself, no call sites.
- `Read` of `tools/v26.8.1/src/coverage_projection.rs` lines 225–240 confirms
  the function's full extent: a doc comment (lines 229–232) explaining it
  reads `coverage-matrix.csv` bytes verbatim for byte-compare purposes, and a
  three-line body (233–235) calling `fs::read`.
- By contrast, `grep -rn "exact_head" tools/v26.8.1/src/` returns the
  definition at line 412 plus real call sites at
  `tools/v26.8.1/src/main.rs:145` (`let source_head = exact_head(&root);`)
  and `tools/v26.8.1/src/bin/project_coverage.rs:76` (same pattern), via
  re-exports listed in `main.rs:10` and `project_coverage.rs:22` — confirming
  `exact_head` is live and this ticket does not touch it.
- `grep -n "^pub fn\|^fn " tools/v26.8.1/src/coverage_projection.rs` lists
  all 11 top-level functions in the file; `grep -n "mod tests\|#\[test\]"`
  on the same file returns no matches, confirming
  `read_coverage_csv_bytes` is not exercised by an in-file unit test either
  — it is unreferenced by any code path in the crate.

## Standing

`ALIVE` — executed and verified this session in an isolated worktree
(`/Users/sac/ggen-legacy/.claude/worktrees/wf_d45a38a1-7b7-1`).

Commands run, in order, with real output:

```
$ grep -rn "read_coverage_csv_bytes" tools/v26.8.1/src/
tools/v26.8.1/src/coverage_projection.rs:233:pub fn read_coverage_csv_bytes(root: &Path) -> Result<Vec<u8>> {
```
(exactly one match, the definition — premise reconfirmed)

Deleted lines 229–235 (doc comment + body) from
`tools/v26.8.1/src/coverage_projection.rs`. No other line in the file was
touched.

```
$ grep -n "read_coverage_csv_bytes" tools/v26.8.1/src/coverage_projection.rs && echo "STILL PRESENT" || echo "removed"
removed
```

```
$ cargo build --manifest-path tools/v26.8.1/Cargo.toml
   Compiling ggen-v26-8-1-verifier v26.8.1 (/Users/sac/ggen-legacy/.claude/worktrees/wf_d45a38a1-7b7-1/tools/v26.8.1)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 8.35s
```

```
$ cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked
    Finished `test` profile [unoptimized + debuginfo] target(s) in 8.72s
     Running unittests src/lib.rs (v26_8_1_tools-de0a6ede17e071fb)
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

     Running unittests src/main.rs (ggen_v26_8_1_verifier-46595d42c5ac4b51)
test result: ok. 13 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

     Running unittests src/bin/project_coverage.rs (project_coverage-d4a23836d57ea6c8)
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

     Running unittests src/bin/subsystem_verifier.rs (subsystem_verifier-dce96cd4fdc408c8)
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

     Running tests/verifier_boundary.rs (verifier_boundary-3425b9965ef23c70)
test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```
(15 tests total, 0 failed)

```
$ git diff --stat
 tools/v26.8.1/src/coverage_projection.rs | 8 --------
 1 file changed, 8 deletions(-)
```
(only the authored file changed; `tickets/GL-ERRC-015.md` was untracked in
this worktree branch prior to this session, so it does not appear in
`git diff --stat` against HEAD — it is a new file, added per the ticket's
own authored boundary.)

All three falsifiers checked negative: no remaining caller, build/test
succeed, diff scoped to the one authored file (plus this ticket file, which
is new rather than modified).
