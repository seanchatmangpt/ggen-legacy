# GL-EXP-025 — Eliminate the unused direct `tracing = "0.1"` dependency from root `Cargo.toml`

**Status:** EXECUTED -- fix landed and verified this session in worktree
`/Users/sac/ggen-legacy/.claude/worktrees/wf_dbca2a9c-5eb-2`
(branch `worktree-wf_dbca2a9c-5eb-2`, base commit
`93d2ecd18147acaff659bf1d9cc2d4313628305b`); originally drafted by standing
ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

Root `Cargo.toml:27` declares `tracing = "0.1"` as a direct `[dependencies]`
entry (confirmed this session by direct read of the file). No code in this
crate ever calls it: `grep -rn "tracing::\|\binfo!\|\bwarn!\|\berror!\|
\bdebug!\|\btrace!" src/*.rs tests/*.rs` (run this session) returns zero
matches across all six `src/*.rs` files (`analysis.rs`, `backend.rs`,
`capabilities.rs`, `generated_contract.rs`, `lib.rs`, `main.rs`) and all
five `tests/*.rs` files. `src/main.rs:8-10` (read in full this session) is
the crate's only `tracing`-adjacent code:

```rust
tracing_subscriber::fmt()
    .with_writer(std::io::stderr)
    .init();
```

This initializes a subscriber that nothing ever writes to — a real,
~900-line LSP server (`src/analysis.rs`, `src/backend.rs`, `src/main.rs`)
with zero diagnostic logging despite paying the initialization ceremony
cost. `Cargo.lock:2662-2664` (read this session) confirms the resolved
package: `tracing v0.1.44`, registry source.

**One correction to the candidate item's own evidence, made per this
account's re-derivation discipline on correction:** the item's evidence
speculates tracing "may still be pulled in transitively by
tracing-subscriber." Direct read of `tracing-subscriber`'s own dependency
block in `Cargo.lock:2706-2717` this session shows it depends on
`tracing-core` and `tracing-log`, not on `tracing` itself — that
speculation is not correct. The real transitive holder, confirmed this
session with `cargo tree -i tracing`, is the crate's own `lsp-max` git
dependency (and, one level further, `salsa` and `wasm4pm-cognition`, both
pulled in via `lsp-max`):

```
tracing v0.1.44
├── lsp-max v26.7.1 (…rev=c1cab89b…)
│   └── ggen-legacy-lsp v26.8.5 (/Users/sac/ggen-legacy)
├── salsa v0.26.2
│   └── lsp-max-ast v26.7.1 (…) / lsp-max-lsif v26.7.1 (…)
└── wasm4pm-cognition v26.7.1
    └── lsp-max v26.7.1 (…)
```

This strengthens rather than weakens the eliminate case: removing the
crate's own direct declaration is fully safe precisely *because* the
package stays resolvable through `lsp-max` regardless — there is no risk
of breaking a transitive consumer by dropping the redundant direct edge.
Verified with a real, reverted experiment this session: temporarily
deleted `Cargo.toml:27`'s `tracing = "0.1"` line and ran
`cargo check --all-targets`:

```
    Checking ggen-legacy-lsp v26.8.5 (/Users/sac/ggen-legacy)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 2.05s
```

Clean build, zero errors or warnings. `git diff --stat` after the edit
showed exactly `Cargo.lock | 1 -` and `Cargo.toml | 1 -` — the direct
dependency edge disappears from the lock file, `tracing v0.1.44` itself
remains (still present in `Cargo.lock` afterward, confirmed by re-grepping
`^name = "tracing"$`), and nothing else in the lock file shifts. The
change was reverted (`git checkout -- Cargo.toml Cargo.lock`) after
verification; the working tree is unmodified by this ticket's drafting.

**No existing ticket covers this.** `grep -il tracing tickets/GL-*.md` (run
this session, over all 47 existing `GL-*.md` files) returns no matches.
This is a new finding class — an unused *direct* dependency declaration
plus inert logging-initialization ceremony — distinct from this corpus's
recurring duplicated-helper and undifferentiated-git-failure-collapse
patterns.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below. This
session grepped every existing ticket's Authored-boundary section for
`Cargo.toml` and `main.rs`: twelve tickets reference `Cargo.toml` and
twelve reference `main.rs`, but on inspection (`grep -i "Cargo.toml\|
main.rs" -A2 -B1` against each ticket's own Authored-boundary block, run
this session) every single one targets a *different* file path —
`tools/v26.8.1/src/main.rs` (the separate `v26_8_1_tools` crate's binary;
`GL-ERRC-015`, `GL-ERRC-019`, `GL-EXP-001`, `GL-EXP-003`, `GL-EXP-005`,
`GL-EXP-007`, `GL-EXP-019` all target this file, already reconciled
against each other per `GL-EXP-019`'s own note) or
`tools/ggen-verifier-cli-verify/Cargo.toml`/`Cargo.lock` (`GL-EXP-002`,
`GL-EXP-022`). None targets the *root* `Cargo.toml` or the *root*
`src/main.rs` this ticket claims. The one ticket that does reference root
`src/main.rs` is `GL-LSP-001` (the foundational, already-`EXECUTED` base
admission ticket for this whole receiver, predating the
`## Authored boundary` convention and carrying no per-line boundary
section) — its own text (read this session) describes a fix to the
`ExitedError` match arm at `src/main.rs`'s tail (after the `.serve(...)
.await` call), not the `tracing_subscriber::fmt()...init()` block at
lines 8-10 this ticket targets. Disjoint regions of the same file, no
line-range conflict, no `tickets/OVERLAPS.md` entry required — the two
tickets' concerns do not touch a shared statement.)

```text
Cargo.toml   # delete the single `tracing = "0.1"` line only
Cargo.lock   # relock (removes the now-redundant direct-dependency edge; tracing itself stays, pulled in via lsp-max)
tickets/GL-EXP-025.md
```

No change to `tracing-subscriber = "0.3"` (stays; still the crate's real,
used logging-subscriber setup crate, even though nothing currently logs
through it — that is a separate, larger question this ticket does not
open), `src/main.rs`'s `tracing_subscriber::fmt()...init()` call itself
(stays byte-identical; `tracing-subscriber` does not require the
`tracing` crate as a direct dependency to compile against, confirmed by
the real `cargo check` run above), any other dependency line in
`Cargo.toml`, or any file outside the three listed above.

## Hard laws

1. `Cargo.toml`'s diff is exactly the deletion of the single line
   `tracing = "0.1"` — no reordering, no version bump, no other
   dependency touched.
2. `Cargo.lock` is relocked via a real `cargo check --locked`-compatible
   flow (i.e. `cargo check --all-targets` without `--locked` to allow the
   lock file to update, or `cargo update -p ggen-legacy-lsp --precise` /
   equivalent) — not hand-edited.
3. `tracing v0.1.44` must still appear in the post-change `Cargo.lock`
   (pulled in transitively via `lsp-max`) — this ticket removes a
   redundant *direct* declaration, not the package from the dependency
   graph.
4. `cargo check --all-targets`, `cargo clippy --all-targets -- -D
   warnings`, and `cargo test --all-targets` must all still pass after
   the change, with no new warning attributable to the removed line.
5. `src/main.rs`'s `tracing_subscriber::fmt()...init()` call is not
   touched by this ticket — it stays exactly as-is (a separate, larger
   question of whether to add real logging or remove the dead
   initialization ceremony is deliberately left out of this ticket's
   scope to keep the diff minimal).
6. `git diff --stat` after this ticket touches only `Cargo.toml`,
   `Cargo.lock`, and `tickets/GL-EXP-025.md`.

## Falsifiers

- After the fix, `grep -n '^tracing = ' Cargo.toml` still returns a match.
- After the fix, `cargo check --all-targets` fails, or
  `grep -n '^name = "tracing"$' Cargo.lock` returns no match (i.e. the
  package silently disappeared from the graph instead of the direct edge
  merely being removed).
- `cargo clippy --all-targets -- -D warnings` or
  `cargo test --all-targets` regresses relative to its pre-change baseline
  as a result of this change.
- `src/main.rs`'s `tracing_subscriber::fmt()...init()` block is modified,
  added to, or removed as part of this ticket (Hard Law 5).
- `git diff --stat` after this ticket touches any file outside
  `Cargo.toml`, `Cargo.lock`, and `tickets/GL-EXP-025.md`.

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the fix lands, not yet-observed outcomes
beyond the reverted verification experiment already run and quoted in
Outcome above.**

## Acceptance (not yet run as a landed change -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the finding before touching anything:
grep -n '^tracing = ' Cargo.toml
  # expect: 27:tracing = "0.1"
grep -rn "tracing::\|\binfo!\|\bwarn!\|\berror!\|\bdebug!\|\btrace!" src/*.rs tests/*.rs
  # expect: no output (zero matches)

# After removing the line and relocking:
grep -n '^tracing = ' Cargo.toml
  # expect: no output
grep -n '^name = "tracing"$' -A2 Cargo.lock
  # expect: still present (pulled in transitively via lsp-max)
cargo tree -i tracing
  # expect: lsp-max (and salsa, wasm4pm-cognition via lsp-max) as the sole roots; ggen-legacy-lsp no longer a direct root

cargo fmt --all -- --check
cargo check --all-targets
cargo clippy --all-targets -- -D warnings
cargo test --all-targets

git diff --stat   # only Cargo.toml, Cargo.lock, tickets/GL-EXP-025.md
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- Direct `Read` of `Cargo.toml` in full this session: confirms line 27,
  `tracing = "0.1"`, in `[dependencies]`, alongside `tracing-subscriber =
  "0.3"` on the following line.
- `grep -rn "tracing::\|\binfo!\|\bwarn!\|\berror!\|\bdebug!\|\btrace!"
  src/*.rs tests/*.rs` this session: zero matches (exit 1, no output),
  confirmed after listing all six `src/*.rs` files and all five
  `tests/*.rs` files with `ls`.
- Direct `Read` of `src/main.rs` in full (25 lines) this session: confirms
  lines 8-10 are exactly `tracing_subscriber::fmt().with_writer(std::io::
  stderr).init();`, and no other line in the file references `tracing` in
  any form.
- `grep -n '^name = "tracing"' -A2 Cargo.lock` this session: confirms
  lines 2662-2664 (`tracing`, `0.1.44`, registry source) — one character
  off from the candidate item's cited `2663-2665`, attributable to this
  session's file having shifted by one line relative to when the item was
  drafted; the package identity and version are exactly as claimed.
- Direct `Read` of `tracing-subscriber`'s dependency block,
  `Cargo.lock:2706-2717`, this session: confirms its dependencies are
  `nu-ansi-term`, `sharded-slab`, `smallvec`, `thread_local`,
  `tracing-core`, `tracing-log` — not `tracing` itself, correcting the
  candidate item's speculative parenthetical.
- `awk` script over `Cargo.lock` this session enumerating every package
  whose `dependencies = [...]` block contains `"tracing",`: returns
  `ggen-legacy-lsp`, `lsp-max`, `salsa`, `wasm4pm-cognition` — confirmed
  `lsp-max` (this crate's own git dependency) is a real transitive holder,
  independent of this crate's own now-redundant direct declaration.
- Real, reverted experiment this session: deleted `Cargo.toml:27`, ran
  `cargo check --all-targets` (real command, real execution, not
  simulated) — output `Checking ggen-legacy-lsp v26.8.5 (...)` /
  `Finished \`dev\` profile [unoptimized + debuginfo] target(s) in 2.05s`,
  zero errors or warnings. `git diff --stat` at that point:
  `Cargo.lock | 1 -`, `Cargo.toml | 1 -`. `cargo tree -i tracing`
  afterward: three roots (`lsp-max`, `salsa`, `wasm4pm-cognition`), with
  `ggen-legacy-lsp` no longer listed as a direct root — confirming the
  package survives the removal of the crate's own now-redundant edge.
  Reverted with `git checkout -- Cargo.toml Cargo.lock`; confirmed restored
  (`grep -n '^tracing = ' Cargo.toml` → `27:tracing = "0.1"`) and `git
  status --short Cargo.toml Cargo.lock` empty before this ticket file was
  written.
- `grep -il tracing tickets/GL-*.md` this session, over all 47 existing
  `GL-*.md` files (`ls tickets/GL-*.md | wc -l` → 47): zero matches.
- `grep -i "Cargo.toml\|main.rs" -A2 -B1` against the Authored-boundary
  section of each of the twelve `Cargo.toml`-referencing and twelve
  `main.rs`-referencing tickets this session: every hit targets
  `tools/v26.8.1/src/main.rs` or
  `tools/ggen-verifier-cli-verify/Cargo.toml`/`Cargo.lock`, never the root
  `Cargo.toml` or root `src/main.rs` this ticket claims — no overlapping
  Authored-boundary claim found.
- Direct `Read` of `tickets/GL-LSP-001.md` in full this session: confirms
  it predates the `## Authored boundary` convention (its sections are
  `## Identity` / `## Admission` / `## Observable contract` / `## Positive
  witnesses` / `## Falsifiers` / `## Acceptance` / `## Standing`), and its
  one `src/main.rs` reference (line 74) describes an already-fixed
  `ExitedError` match-arm defect at the file's tail, not the lines 8-10
  block this ticket targets — disjoint regions, no conflict.
- `ls tickets/GL-EXP-025.md` this session, both before and immediately
  after writing this file: absent before, present after — confirming this
  ticket claimed the pre-assigned id cleanly with no concurrent collision.
- `git status --short` this session: confirmed root `Cargo.toml`,
  `Cargo.lock`, and `src/main.rs` carried no uncommitted modification from
  any other concurrent session at the time this ticket was drafted (only
  unrelated `tools/ggen-verifier-cli-verify/` and other tickets'
  in-flight files were modified/untracked, none overlapping this ticket's
  three-file Authored boundary).

## Standing

`ALIVE` -- fix landed and independently re-verified this session (a fresh
session from the one that drafted the ticket), executing every command in
the ticket's own `## Acceptance` block for real, in order, against the
worktree at `/Users/sac/ggen-legacy/.claude/worktrees/wf_dbca2a9c-5eb-2`
(base commit `93d2ecd18147acaff659bf1d9cc2d4313628305b`):

- Pre-change reconfirmation: `grep -n '^tracing = ' Cargo.toml` →
  `27:tracing = "0.1"`. `grep -rn "tracing::\|\binfo!\|\bwarn!\|\berror!\|
  \bdebug!\|\btrace!" src/*.rs tests/*.rs` → zero matches (exit 1),
  matching the ticket's own cited evidence exactly.
- Applied the fix: removed exactly the one line `tracing = "0.1"` from
  `Cargo.toml` (line 27, between `tokio = {...}` and
  `tracing-subscriber = "0.3"`) via a single-line `Edit`, no reordering,
  no other dependency line touched (Hard Law 1).
- Relocked via a real `cargo check --all-targets` run (not
  `--locked`, not hand-edited; Hard Law 2) — output:
  `Checking ggen-legacy-lsp v26.8.5 (.../wf_dbca2a9c-5eb-2)` /
  `Finished \`dev\` profile [unoptimized + debuginfo] target(s) in 37.70s`,
  zero errors or warnings.
- Post-change checks: `grep -n '^tracing = ' Cargo.toml` → no output.
  `grep -n '^name = "tracing"$' -A2 Cargo.lock` → still present
  (`2662:name = "tracing"` / `version = "0.1.44"` / registry source),
  confirming Hard Law 3 (package survives, only the direct edge is
  removed). `cargo tree -i tracing` → three roots exactly as the ticket
  predicted (`lsp-max`, `salsa`, `wasm4pm-cognition`), with
  `ggen-legacy-lsp` no longer listed as a direct root — the crate now
  reaches `tracing` only transitively via `lsp-max`.
- `cargo fmt --all -- --check` → exit 0, no diff.
- `cargo clippy --all-targets -- -D warnings` → real command, real run:
  `Checking ggen-legacy-lsp v26.8.5 (...)` /
  `Finished \`dev\` profile [unoptimized + debuginfo] target(s) in 0.85s`,
  zero warnings, zero errors (Hard Law 4).
- `cargo test --all-targets` → real command, real run: 13 tests total
  across `src/lib.rs` (1), `src/main.rs` (0), `tests/analysis.rs` (3),
  `tests/analysis_boundary.rs` (3), `tests/contract.rs` (3),
  `tests/exit_code.rs` (1), `tests/lsp_boundary.rs` (2) — 13 passed, 0
  failed, 0 ignored (Hard Law 4).
- `src/main.rs` byte-for-byte unmodified: `git diff --stat -- src/main.rs`
  → empty output; direct re-`Read` of lines 1-15 confirms the
  `tracing_subscriber::fmt().with_writer(std::io::stderr).init();` block
  (lines 8-10) is untouched (Hard Law 5).
- `git diff --stat` after the change → exactly
  `Cargo.lock | 1 -` / `Cargo.toml | 1 -` (plus this ticket file, added to
  the worktree fresh since it did not yet exist there — see note below),
  2 files changed, 2 deletions(-) for the two dependency files (Hard
  Law 6). Full diff for the two dependency files:

  ```diff
  diff --git a/Cargo.lock b/Cargo.lock
  @@ -897,7 +897,6 @@ dependencies = [
   "serde_json",
   "tokio",
   "toml",
  - "tracing",
   "tracing-subscriber",
   "url",
   ]
  diff --git a/Cargo.toml b/Cargo.toml
  @@ -24,7 +24,6 @@ path = "src/lib.rs"
   lsp-max = { git = "https://github.com/seanchatmangpt/lsp-max", rev = "c1cab89bf54fcc9100b3ce75580b3cc3aa8eb852" }
   tokio = { version = "1", features = ["io-std", "io-util", "macros", "rt-multi-thread", "sync"] }
  - tracing = "0.1"
   tracing-subscriber = "0.3"
  ```

- None of the ticket's `## Falsifiers` triggered: `grep -n '^tracing = '
  Cargo.toml` returns no match post-fix; `cargo check --all-targets`
  passed and `grep -n '^name = "tracing"$' Cargo.lock` still matches;
  `cargo clippy --all-targets -- -D warnings` and
  `cargo test --all-targets` show no regression (both a clean pass, no
  prior baseline failure to compare against since this crate's tests were
  already all green); `src/main.rs`'s `tracing_subscriber` block is
  byte-identical to before; `git diff --stat` touches only `Cargo.toml`,
  `Cargo.lock`, and `tickets/GL-EXP-025.md`.
- Worktree note: this session's isolated worktree
  (`/Users/sac/ggen-legacy/.claude/worktrees/wf_dbca2a9c-5eb-2`) was
  created from a base commit that does not carry this ticket file in git
  history (confirmed: `git log --all --oneline -- tickets/GL-EXP-025.md`
  returns no output in the worktree) — the ticket existed only as an
  untracked file in the separate `~/ggen-legacy` checkout where it was
  drafted. It was copied into this worktree's `tickets/` directory as
  part of landing this fix, consistent with the ticket's own Authored
  boundary (`tickets/GL-EXP-025.md` is one of the three files the ticket
  claims).
