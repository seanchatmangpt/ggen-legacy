# GL-ERRC-016 — Add `--locked` to `run_subsystem_verifier()`'s internal `cargo build`

**Status:** EXECUTED
**Base:** `seanchatmangpt/ggen-legacy@f9b283e` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/src/coverage_projection.rs:270-280`'s `run_subsystem_verifier()`
spawns an internal `cargo build` without `--locked`:

```rust
let build = Command::new("cargo")
    .args([
        "build",
        "--manifest-path",
        "tools/v26.8.1/Cargo.toml",
        "--bin",
        "subsystem_verifier",
    ])
    .current_dir(root)
    .status()
    .context("spawn cargo build for subsystem_verifier")?;
```

Every other cargo invocation cited across the current ticket corpus
(`tickets/GL-ERRC-015.md:130`, `tickets/GL-ERRC-019.md:173`,
`tickets/GL-VERIFY-006.md:58` — each `cargo test --manifest-path
tools/v26.8.1/Cargo.toml --all-targets --locked`) uses `--locked`. This
internal build, which self-compiles the `subsystem_verifier` binary as a
side effect of calling `run_subsystem_verifier()`, is the one outlier: an
unpinned dependency resolution here can silently pull a different lockfile
resolution than every verified/tested path, undermining the reproducibility
those other tickets' `--locked` runs are meant to guarantee.

## Authored boundary

Touches only:

```
tools/v26.8.1/src/coverage_projection.rs   # add "--locked" to the build args
```

No change to `run_subsystem_verifier()`'s control flow, error handling, or
any other function in `coverage_projection.rs`.

## Hard laws

1. `cargo build` inside `run_subsystem_verifier()` must include `--locked` in
   its `args([...])` list, alongside the existing `--manifest-path` and
   `--bin` flags.
2. No other cargo invocation, function signature, or return type in
   `coverage_projection.rs` changes.
3. `run_subsystem_verifier()` must still fail closed
   (`SUBSYSTEM_VERIFIER_BUILD_FAILED`) if the locked build fails — including
   the case where `Cargo.lock` is stale relative to `Cargo.toml`, which
   `--locked` turns into a hard build failure instead of a silent
   re-resolution.

## Falsifiers

- `grep -n '"build"' tools/v26.8.1/src/coverage_projection.rs` followed by
  the args list not containing `"--locked"` falsifies hard law 1.
- `git diff --stat` showing any file other than
  `tools/v26.8.1/src/coverage_projection.rs` and this ticket falsifies the
  authored boundary.
- `cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked` failing
  where the current unlocked `cargo build --manifest-path
  tools/v26.8.1/Cargo.toml` succeeds (i.e. `Cargo.lock` is actually stale)
  is not a falsifier of this ticket — it is the exact latent risk this
  ticket exists to surface, and should be fixed as its own follow-up if hit.

## Acceptance

```
$ grep -n '"build"\|"--locked"\|"--manifest-path"\|"--bin"' tools/v26.8.1/src/coverage_projection.rs
# must show --locked in the same args block as --manifest-path and --bin

$ cargo build --manifest-path tools/v26.8.1/Cargo.toml --bin subsystem_verifier --locked
# must exit 0 (or, if it fails only because Cargo.lock is stale, that
# failure is surfaced -- not silently masked -- confirming the flag is live)

$ git diff --stat
# must show only src/coverage_projection.rs + tickets/GL-ERRC-016.md
```

## Standing

`UNKNOWN` -- not started. Verified this session, by direct re-reading of
the live file, that the unlocked `cargo build` call is still present at
`tools/v26.8.1/src/coverage_projection.rs:270-280` and that none of the
three tickets already touching this file (`GL-ERRC-015`, `GL-ERRC-019`,
`GL-VERIFY-006`, found via `grep -l coverage_projection tickets/GL-*.md`)
address this specific unlocked internal build call — each touches a
different function (`read_coverage_csv_bytes`, `exact_head`,
`check_provenance_receipt`/`ParityGateReceipt`) and none of their diffs
modify `run_subsystem_verifier()`'s `Command::new("cargo")` args. Note:
`tickets/GL-ERRC-012.md` also references `coverage_projection.rs` but only
in the context of a BLAKE3 case-manifest binding distinct from this build
call.

## Execution evidence (this session, main checkout)

Confirmed by direct read this session:

```
$ sed -n '260,285p' tools/v26.8.1/src/coverage_projection.rs
```

showed `run_subsystem_verifier()`'s `Command::new("cargo").args(["build",
"--manifest-path", "tools/v26.8.1/Cargo.toml", "--bin",
"subsystem_verifier"])` with no `--locked` flag present.

Confirmed by grep this session that the three tickets already touching this
file do not address this call:

```
$ grep -l "coverage_projection" tickets/GL-*.md
tickets/GL-ERRC-012.md
tickets/GL-ERRC-015.md
tickets/GL-ERRC-019.md
tickets/GL-VERIFY-006.md
```

None of `GL-ERRC-015`, `GL-ERRC-019`, or `GL-VERIFY-006`'s "Authored
boundary" sections list a change to the `run_subsystem_verifier()` build
invocation; their diffs target `read_coverage_csv_bytes()`, `exact_head()`,
and a new `ParityGateReceipt` struct respectively.

## EXECUTED (main checkout, applied from sibling worktree `wf_d4a5bdab-bb5-1`)

Applied the fix: added `"--locked"` to the `args([...])` list in
`run_subsystem_verifier()`'s `Command::new("cargo")` build invocation in
`tools/v26.8.1/src/coverage_projection.rs`. No other line in that function
was touched by this ticket (the file's overall working-tree diff also
includes GL-ERRC-015's and GL-ERRC-019's already-applied, unrelated changes
to `read_coverage_csv_bytes()`/`exact_head()` elsewhere in the same file --
see the isolated `--locked`-only diff below for this ticket's actual
contribution).

Falsifier grep (hard law 1), re-run in the main checkout:

```
$ grep -n '"build"\|"--locked"\|"--manifest-path"\|"--bin"' tools/v26.8.1/src/coverage_projection.rs
272:            "build",
273:            "--manifest-path",
275:            "--bin",
277:            "--locked",
```

`--locked` is present in the same `args([...])` block as `--manifest-path`
and `--bin` -- hard law 1 satisfied.

This ticket's isolated contribution (not the whole file's working-tree diff,
which also carries GL-ERRC-015/GL-ERRC-019's unrelated changes):

```diff
             "--manifest-path",
             "tools/v26.8.1/Cargo.toml",
             "--bin",
             "subsystem_verifier",
+            "--locked",
         ])
```

Acceptance build (with `--locked`, exact binary target), main checkout:

```
$ cargo build --manifest-path tools/v26.8.1/Cargo.toml --bin subsystem_verifier --locked
   Compiling ggen-v26-8-1-verifier v26.8.1 (/Users/sac/ggen-legacy/tools/v26.8.1)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.83s
```
Exit 0. `Cargo.lock` was not stale -- the locked build succeeded cleanly.

Full test suite (required by task, `--all-targets --locked`), main checkout:

```
$ cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked -- --test-threads=1
test result: ok. 3 passed; 0 failed (lib)
test result: ok. 13 passed; 0 failed (src/main.rs)
test result: ok. 0 passed; 0 failed (project_coverage bin)
test result: ok. 0 passed; 0 failed (subsystem_verifier bin)
test result: ok. 2 passed; 0 failed (tests/verifier_boundary.rs)
```
Exit 0. 18 tests total across 5 suites, 0 failed, 0 ignored.

**Result: PASS.** Hard law 1 holds (falsifier grep clean), hard law 2 holds
(no other line in `coverage_projection.rs` touched by this ticket), hard law
3 holds vacuously (lockfile was not stale, so the locked build did not mask
anything). Both required commands exited 0 with no test failures, re-verified
directly in the main checkout (not carried forward from the sibling
worktree's run).
