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

No fix applied yet -- this ticket is drafted, not executed.

## EXECUTED (this session, worktree `wf_d4a5bdab-bb5-1`)

Applied the fix: added `"--locked"` to the `args([...])` list in
`run_subsystem_verifier()`'s `Command::new("cargo")` build invocation in
`tools/v26.8.1/src/coverage_projection.rs`. No other line in that function,
or any other function in the file, was touched.

Falsifier grep (hard law 1):

```
$ grep -n '"build"\|"--locked"\|"--manifest-path"\|"--bin"' tools/v26.8.1/src/coverage_projection.rs
280:            "build",
281:            "--manifest-path",
283:            "--bin",
285:            "--locked",
```

`--locked` is present in the same `args([...])` block as `--manifest-path`
and `--bin` -- hard law 1 satisfied, falsifier does not trigger.

Diff scope (authored boundary):

```
$ git diff --stat
 tools/v26.8.1/src/coverage_projection.rs | 1 +
 1 file changed, 1 insertion(+)
```

Only `coverage_projection.rs` changed in this worktree's git tree -- no
other source file touched. (This ticket file itself is not a tracked file
in the repo's git history in either the main checkout or this worktree, so
it is not part of the tracked diff; its content is the acceptance/evidence
record, updated directly per task instructions.)

Acceptance build (with `--locked`, exact binary target):

```
$ cargo build --manifest-path tools/v26.8.1/Cargo.toml --bin subsystem_verifier --locked
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.10s
```
Exit 0. `Cargo.lock` was not stale -- the locked build succeeded cleanly,
confirming the flag is live and the lockfile is currently in sync with
`Cargo.toml` (satisfies hard law 3's non-masking requirement vacuously:
there was no staleness to mask).

Full manifest build (unlocked, sanity check nothing else broke):

```
$ cargo build --manifest-path tools/v26.8.1/Cargo.toml
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 9.57s
```
Exit 0.

Full test suite (required by task, `--all-targets --locked`):

```
$ cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked
running 0 tests (unittests src/lib.rs) ... ok
running 13 tests (unittests src/main.rs, document_evidence_sabotage_tests::*) ... ok. 13 passed; 0 failed
running 0 tests (unittests src/bin/project_coverage.rs) ... ok
running 0 tests (unittests src/bin/subsystem_verifier.rs) ... ok
running 2 tests (tests/verifier_boundary.rs) ... ok. 2 passed; 0 failed
```
Exit 0. 15 tests total, 0 failed, 0 ignored.

**Result: PASS.** All three hard laws hold, both falsifiers checked clean,
both required commands (`cargo build --manifest-path
tools/v26.8.1/Cargo.toml` and `cargo test --manifest-path
tools/v26.8.1/Cargo.toml --all-targets --locked`) exited 0 with no test
failures.
