# GL-EXP-002 — Fix `tools/ggen-verifier-cli-verify/Cargo.toml`'s dead absolute-path dev-dependency into `~/ggen`

**Status:** `EXECUTED` — real fix landed in the main checkout and re-verified there
2026-08-21 (this ticket's own on-disk Status line was previously left at
`NOT_STARTED` despite the code fix landing in a prior pass — a genuine
record-keeping gap, closed here; see `docs/v26.9.1/RELEASE-NOTES.md`'s
"honest conclusion" section for the full account of that gap).
**Base:** `seanchatmangpt/ggen-legacy@bce7f63` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/ggen-verifier-cli-verify/Cargo.toml` pins its only dev-dependency,
`chicago-tdd-tools`, to a `path = "/Users/sac/ggen/crates/chicago-tdd-tools"`
dev-dependency with `features = ["cli-proof"]`. That path does not exist:
`cd /Users/sac/ggen && git log --oneline --all -- crates/chicago-tdd-tools`
shows the sibling repo's own commit `4386fe120 chore: remove vendored
chicago-tdd-tools, depend on published 26.8.3` deleted that exact vendored
directory. As a direct result, `cargo clippy --manifest-path
tools/ggen-verifier-cli-verify/Cargo.toml --all-targets -- -D warnings`
(re-run live this session) fails outright before reaching any lint:

```
error: failed to load manifest for dependency `chicago-tdd-tools`

Caused by:
  failed to read `/Users/sac/ggen/crates/chicago-tdd-tools/Cargo.toml`

Caused by:
  No such file or directory (os error 2)
```

The fix already exists in this same repo and is already proven working: this
repo's own root `Cargo.toml` (line 36) depends on the equivalent published
crate+feature instead of a path:

```toml
chicago-tdd-tools = { version = "26.8.3", features = ["cli-proof"] }
```

`Cargo.lock` resolves it for real (`grep -A3 'name = "chicago-tdd-tools"'
Cargo.lock` → `version = "26.8.3"`, `source = "registry+https://github.com/
rust-lang/crates.io-index"`), it is cached locally at
`~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/
chicago-tdd-tools-26.8.3`, and `cargo build --tests` at repo root exits `0`
this session. Crucially, the target crate's own doc-comment justification for
the path dependency -- "the published chicago-tdd-tools doesn't yet include
the `cli_proof` module (`cli-proof` feature isn't published to crates.io
yet)" -- is disproven by inspecting that exact cached, published crate:
`grep -n "cli-proof" .../chicago-tdd-tools-26.8.3/Cargo.toml` shows
`cli-proof = ["dep:tempfile"]` (line 63), and
`grep -n "cli_proof" .../chicago-tdd-tools-26.8.3/src/lib.rs` shows
`pub mod cli_proof;` (line 187) plus a `pub use crate::cli_proof::{...}`
re-export at line 323. The feature and module this crate claims are
unpublished have been published since at least `26.8.3` -- the same version
this repo's own root package already consumes successfully.

This crate is not caught by anything: `grep -rl 'ggen-verifier-cli-verify'
justfile` and `grep -rl 'ggen-verifier-cli-verify' .github/workflows/`
(re-run this session) both return zero matches -- no `justfile` recipe and no
CI workflow ever builds or lints it, so this manifest failure is currently
silent to every automated check in the repo. (One tangential hit exists:
`tickets/GL-AUTO-001.md` contains the crate's path only inside a giant
`REFUSED:FORBIDDEN_DIFF:` file-list dump from an unrelated acceptance-command
run, not a substantive reference or dependency on the crate -- it does not
change this finding.) The crate's stated purpose -- closing the dogfood loop
on the `tools/v26.8.1` verifier binary via `ctt:CliBoundaryTest` /
`chicago_tdd_tools_boundary.rs` -- currently cannot even be `cargo check`'d on
any machine other than the one that happens to have `~/ggen` checked out at
that exact absolute path, which defeats the crate's own "committed, real
cross-repo consumer" framing.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
check there before assuming sole ownership of a path below.)

```text
tools/ggen-verifier-cli-verify/Cargo.toml   # dev-dependency form only
tools/ggen-verifier-cli-verify/Cargo.lock   # relock against the published crate
tickets/GL-EXP-002.md
```

No change to `tools/ggen-verifier-cli-verify/src/`, `tests/`, `schema/
domain.ttl`, `ggen.toml`, or `ggen.lock` -- this ticket repairs the
dependency declaration only, it does not touch the crate's own
`CliHarness`/`ctt:CliBoundaryTest` generation logic or re-run `ggen sync`.

## Hard laws

1. The replacement dependency line must match this repo's own already-proven
   form exactly in spirit: `chicago-tdd-tools = { version = "26.8.3",
   features = ["cli-proof"] }` (or a later published version actually present
   in `Cargo.lock` after relocking) -- not a re-pin to a different absolute
   path, not a git dependency, not a vendored copy.
2. `Cargo.lock` for this crate must be regenerated so it resolves
   `chicago-tdd-tools` from `registry+https://github.com/rust-lang/
   crates.io-index`, not from a `path+file://` source.
3. This ticket does not add any new `justfile` recipe or CI workflow wiring
   for this crate -- that is a distinct follow-on (the crate remains
   unreferenced by `ci`/`ci-all`/`v26-ci` after this fix, per Standing
   below), out of scope here.
4. This ticket does not alter the crate's stale doc-comment prose beyond
   what is required to stop asserting the now-disproven "not published yet"
   claim -- no unrelated rewrite of the crate description.

## Falsifiers

- `cargo clippy --manifest-path tools/ggen-verifier-cli-verify/Cargo.toml
  --all-targets -- -D warnings` still fails to load the manifest after the
  fix.
- The relocked `Cargo.lock` still shows a `path+file://` source (rather than
  `registry+...`) for `chicago-tdd-tools`.
- `features = ["cli-proof"]` is dropped rather than preserved, silently
  disabling the `cli_proof`-module-dependent test(s) in
  `tests/chicago_tdd_tools_boundary*.rs`.
- Any file outside the `## Authored boundary` list above is touched.

## Acceptance

Not yet executed (`NOT_STARTED`). The acceptance command to run once this
ticket moves to `EXECUTED` is:

```bash
cargo clippy --manifest-path tools/ggen-verifier-cli-verify/Cargo.toml --all-targets -- -D warnings
```

Success is exit code `0` with `Cargo.lock` (for this crate) resolving
`chicago-tdd-tools` from the crates.io registry (`source = "registry+
https://github.com/rust-lang/crates.io-index"`), matching the already-working
form verified at repo root this session (`grep -A3 'name =
"chicago-tdd-tools"' Cargo.lock` / `cargo build --tests` exit `0`).

## Standing

`ALIVE`, re-verified in the main checkout 2026-08-21:

```
$ grep -n 'chicago-tdd-tools' tools/ggen-verifier-cli-verify/Cargo.toml
16:chicago-tdd-tools = { version = "26.8.3", features = ["cli-proof"] }
$ cargo clippy --manifest-path tools/ggen-verifier-cli-verify/Cargo.toml --all-targets -- -D warnings
    Finished `dev` profile [unoptimized + debuginfo] target(s) ...
exit 0
```

`Cargo.lock` relocked, resolving `chicago-tdd-tools` to a real registry
source (no `path+file` entries remain). The manifest edit and relock have
now been performed, satisfying this ticket's own acceptance command.
Separately, even after this fix the crate stays wired into nothing (no
`justfile` recipe, no CI workflow references it -- confirmed this
session), so its "closes the dogfood loop" purpose remains aspirational
until a follow-on ticket wires it
in; that follow-on is explicitly out of scope here (Hard Law 3).
