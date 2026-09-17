# GL-EXP-002 — Fix `tools/ggen-verifier-cli-verify/Cargo.toml`'s dead absolute-path dev-dependency into `~/ggen`

**Status:** EXECUTED -- fix applied and acceptance command re-run live this
session (see "Execution evidence" below); originally admitted/NOT_STARTED,
drafted by standing ultracode exploration cron (GL-EXP namespace)
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

All four falsifiers were checked live this session after applying the fix
and found not to hold -- see "Execution evidence" below.

## Acceptance

**EXECUTED.** The acceptance command was re-run live this session:

```bash
cargo clippy --manifest-path tools/ggen-verifier-cli-verify/Cargo.toml --all-targets -- -D warnings
```

Result: exit code `0`. Real terminal output (final lines of the first,
cold-cache run that actually did the relock, followed by a clean immediate
re-run showing the cached `Finished` result and the checked exit code):

```
    Updating crates.io index
     Locking 8 packages to latest compatible versions
      Adding chicago-tdd-tools v26.8.9
      Adding chicago-tdd-tools-proc-macros v26.8.9
    Updating serde_spanned v0.6.9 -> v1.1.1
    Updating toml v0.8.23 -> v1.1.4+spec-1.1.0
    Updating toml_datetime v0.6.11 -> v1.1.1+spec-1.1.0
      Adding toml_parser v1.1.3+spec-1.1.0
      Adding toml_writer v1.1.2+spec-1.1.0
    Updating winnow v0.7.15 -> v1.0.4
   Compiling proc-macro2 v1.0.107
   ... (full dependency graph compiles clean) ...
   Compiling chicago-tdd-tools v26.8.9
    Checking ggen-verifier-cli-verify v0.1.0 (.../tools/ggen-verifier-cli-verify)
   Compiling chicago-tdd-tools-proc-macros v26.8.9
    Checking tempfile v3.27.0
    Checking tokio v1.53.1
    Checking chrono v0.4.45
    Checking serde_yaml v0.9.34+deprecated
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 9.91s

$ cargo clippy --manifest-path tools/ggen-verifier-cli-verify/Cargo.toml --all-targets -- -D warnings; echo "EXIT_CODE=$?"
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.04s
EXIT_CODE=0
```

No `warning:` or `error:` lines appear anywhere in the clippy output
(`grep -iE "warning|error"` over the full transcript of the second run
returns zero matches, confirmed live this session).

Success criterion satisfied: `Cargo.lock` (for this crate) now resolves
`chicago-tdd-tools` from the crates.io registry, matching the already-working
form at repo root:

```
$ grep -A4 'name = "chicago-tdd-tools"$' tools/ggen-verifier-cli-verify/Cargo.lock
name = "chicago-tdd-tools"
version = "26.8.9"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "9c2a73444d211e0137bf7de7a6cc19e327e1a25a44fbd0b7ea641385844ef758"
dependencies = [
```

(`26.8.9` rather than `26.8.3` -- Cargo resolved the caret-compatible
`version = "26.8.3"` requirement in `Cargo.toml` to the newest published
compatible release actually available in the registry index at execution
time, which Hard Law 1 explicitly permits: "or a later published version
actually present in `Cargo.lock` after relocking".)

### Execution evidence (falsifier-by-falsifier, re-checked live this session)

1. **Manifest load / clippy exit code** -- `cargo clippy --manifest-path
   tools/ggen-verifier-cli-verify/Cargo.toml --all-targets -- -D warnings`
   exits `0` (shown above). Falsifier does not hold.
2. **Lock source** -- `grep -c "path+file" tools/ggen-verifier-cli-verify/
   Cargo.lock` → `0`. The only `chicago-tdd-tools` entry in the relocked
   `Cargo.lock` is `source = "registry+https://github.com/rust-lang/
   crates.io-index"` (shown above). Falsifier does not hold.
3. **`cli-proof` feature preserved** -- `Cargo.toml`'s dev-dependency line
   still reads `chicago-tdd-tools = { version = "26.8.3", features =
   ["cli-proof"] }`; `grep -rn "cli_proof" tools/ggen-verifier-cli-verify/
   tests/` still finds `use chicago_tdd_tools::cli_proof::CliHarness;` in
   `tests/chicago_tdd_tools_boundary_runtime.rs` and the doc-comment
   reference in `tests/chicago_tdd_tools_boundary.rs`, and both compiled
   clean under `--all-targets` above (a dropped feature would have failed
   to resolve `cli_proof` at that `use` site). Falsifier does not hold.
4. **Authored-boundary-only diff** -- `git status --porcelain` inside the
   execution worktree shows exactly two modified paths:
   ```
    M tools/ggen-verifier-cli-verify/Cargo.lock
    M tools/ggen-verifier-cli-verify/Cargo.toml
   ```
   both listed in `## Authored boundary` above (this ticket file itself was
   written fresh into the same worktree rather than showing as a
   modification, since it did not previously exist as a tracked file there).
   No file outside the authored boundary was touched. Falsifier does not
   hold.

The `Cargo.toml` dev-dependency line after the fix:

```toml
[dev-dependencies]
# Published crate + feature, matching this repo's own root Cargo.toml.
chicago-tdd-tools = { version = "26.8.3", features = ["cli-proof"] }
```

Per Hard Law 4, only the doc-comment directly asserting the disproven
"not published yet" claim was removed; no other part of the crate
description (including the still-accurate `ggen.toml`-pack-reference half
of the `NOTE:` sentence in the `[package] description` field, which this
ticket's boundary does not authorize touching) was rewritten.

## Standing

`PARTIAL_ALIVE` -- this ticket's evidence (the manifest-load failure, the
sibling repo's own commit that deleted the vendored path, the root
`Cargo.toml`/`Cargo.lock`'s already-working published-crate form, and the
published crate's own `Cargo.toml`/`lib.rs` disproving the "not published
yet" claim) was independently re-verified live this session with real
commands against real files in both `~/ggen-legacy` and the sibling
`~/ggen` repo -- no fabrication, no reliance on the candidate's evidence
text alone. The fix, relock, and full falsifier re-check above were then
executed live in the same session (`EXECUTED`). Standing ceiling stays
`PARTIAL_ALIVE` rather than promoting further because, per Hard Law 3, the
crate remains wired into nothing after this fix (no `justfile` recipe, no
CI workflow references it -- confirmed this session), so its "closes the
dogfood loop" purpose remains aspirational until a follow-on ticket wires it
in; that follow-on stays explicitly out of scope here.
