# GL-EXP-019 — Raise `git_provenance::run()`'s undifferentiated `Option::None` collapse out of `document_head_is_fresh`'s provenance-freshness check

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/src/main.rs:625-633`'s private `git_provenance::run()` collapses
3 causally distinct failure modes into the single undifferentiated Rust value
`Option::None`:

```rust
fn run(root: &Path, args: &[&str]) -> Option<String> {
    Command::new("git")
        .args(args)
        .current_dir(root)
        .output()
        .ok()
        .filter(|out| out.status.success())
        .map(|out| String::from_utf8_lossy(&out.stdout).trim().to_owned())
}
```

`.ok()` on `Command::output()`'s `io::Result` silently swallows a spawn
failure (e.g. `git` not on `PATH`, permission denied on `root`). `.filter()`
on a successful spawn silently swallows a non-zero exit (e.g. a malformed
revision range, a corrupt object). And `String::from_utf8_lossy` silently
launders non-UTF8 stdout bytes instead of surfacing them as a distinct case.
All 3 causes collapse into the identical `None`, exactly the same 3-way
collapse GL-ERRC-019 named and fixed for `coverage_projection.rs::exact_head()`
and that GL-EXP-005/GL-EXP-011/GL-EXP-015 each found unfixed a second, third,
and fourth time in other files. This is a 5th, currently-unticketed instance
of the identical anti-pattern class.

`run()` is not dead code and not test-only plumbing -- it backs 3 public
functions in the same module, confirmed by direct `Read` this session
(`tools/v26.8.1/src/main.rs:635-676`):

- `pub fn is_git_repo(root: &Path) -> bool` (line 639) — `run(...).as_deref()
  == Some("true")`. Here `run()`'s `None` is caught by an intentional,
  differentiated fallback (a non-git fixture correctly falls back to strict
  equality per the doc comment at lines 636-638), so this call site is *not*
  itself a collapse — it is the one place `run()`'s `None` is already handled
  meaningfully.
- `pub fn last_commit_touching(root: &Path, at: &str, path: &str) ->
  Option<String>` (line 655) — `run(...).filter(|s| !s.is_empty())`. Here
  `run()`'s `None` (spawn failure / non-zero exit / non-UTF8 stdout) is
  indistinguishable from the function's own legitimate "no history for this
  path" `None` (an empty-but-successful `git log` result also filters to
  `None`) — a second, compounding collapse on top of `run()`'s own.
- `pub fn changed_paths_between(root: &Path, from: &str, to: &str) ->
  Option<Vec<String>>` (line 674) — `run(...).map(...)`. Here `run()`'s
  `None` passes straight through as the function's own `None`, with zero
  differentiation added or removed.

Both of the latter two feed the real, load-bearing `document_head_is_fresh()`
(line 683), which decides whether a `document-evidence-index` record's
`source_head` still legitimately attests to its document's current content —
confirmed by direct `Read` this session:

- `last_commit_touching`'s `None` (line 697-701) is matched at line 700-701
  (`else { return false; }`) with the comment "No history for this path
  reachable from HEAD -- cannot attest freshness." This is the identical
  `false` outcome as the function's OWN legitimate "genuinely no commit
  history for this path" case — `run()`'s 3 infrastructure-failure causes and
  this one content-fact cause are now 4 causes collapsed into 1 boolean.
- `changed_paths_between`'s `None` (line 716-721) falls into the match arm's
  `_ => false` catch-all (line 720), the identical branch a real, substantive
  finding takes (a non-empty changed-path set outside
  `GENERATED_EVIDENCE_ARTIFACT_PATHS`, i.e. genuine content drift). A `git
  diff` that could not even be run and a `git diff` that ran and found real,
  un-exempted drift are indistinguishable to this function's caller.

`document_head_is_fresh`'s sole call site (`main.rs:883-897`, confirmed by
direct `Read` this session) turns any `false` return into the identical
`DOCUMENT_HEAD_STALE` finding and identical error message
(`"sourceHead '{}' no longer attests to '{}' as of current HEAD
'{current_head}'"`), incrementing `gap_count` regardless of which of the (now)
4+ underlying causes produced it. A downstream consumer of this tool's
findings output cannot distinguish "this document's content genuinely
drifted since `source_head`" from "git was transiently unavailable, exited
non-zero, or returned non-UTF8 bytes while this tool was trying to check" —
the same class of false-positive/false-negative ambiguity GL-ERRC-019,
GL-EXP-005, GL-EXP-011, and GL-EXP-015 each treat as the defect worth fixing
in their own target files.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
check there before assuming sole ownership of a path below. `main.rs` is a
contended file: `GL-ERRC-015`, `GL-EXP-003`, `GL-ERRC-019`, `GL-EXP-007`,
`GL-EXP-001`, and `GL-EXP-005` all reference it, but every one of those
targets `main.rs:1-15` (the `use v26_8_1_tools::coverage_projection::{...}`
import block) and/or `main.rs:145` (`let source_head = exact_head(&root);`) —
confirmed this session via `grep -n "main.rs" tickets/GL-ERRC-015.md
tickets/GL-EXP-003.md tickets/GL-ERRC-019.md tickets/GL-EXP-007.md
tickets/GL-EXP-001.md tickets/GL-EXP-005.md`. None references the private
`git_provenance` module (lines 620-724) or `document_head_is_fresh`
(lines 683-724) by name or line number. This ticket's target has no line-range
overlap with any of them.)

```text
tools/v26.8.1/src/main.rs   # git_provenance::run() return type/behavior,
                             # and the 3 call sites (is_git_repo,
                             # last_commit_touching, changed_paths_between)
                             # and document_head_is_fresh's consumption of
                             # them, only
tickets/GL-EXP-019.md
```

No change to `main.rs:1-15`'s import block, `main.rs:145`'s `exact_head(&root)`
call site, `commit_exists`, `is_ancestor_or_equal` (both already use direct
`Command` + `.status()`, not `run()`, and are out of scope), the
`GENERATED_EVIDENCE_ARTIFACT_PATHS` exemption list itself, or any file under
`tools/v26.8.1/src/coverage_projection.rs`, `tools/v26.8.1/src/bin/
subsystem_verifier.rs`, `tools/v26.8.20/observe_contract.py`, or
`appliance/bin/verify-standing-portfolio.py` (GL-ERRC-019's, GL-EXP-005's,
GL-EXP-011's, and GL-EXP-015's respective targets — already fixed or
separately ticketed).

## Hard laws

1. A real git repo where `git <args>` genuinely succeeds must return the
   identical trimmed stdout string as before this ticket for `is_git_repo`,
   `last_commit_touching`, and `changed_paths_between`'s happy paths — no
   change to observable success-path values or types.
2. The 3 verified failure causes in `run()` -- spawn failure (`Command::output`
   returning `Err`), non-zero exit (`out.status.success()` false), and
   non-UTF8 stdout (`String::from_utf8_lossy`'s replacement-character path) --
   must each be distinguishable from one another and from a genuine "ran
   successfully but returned no/empty content" outcome, in whatever
   replaces the current bare `Option<String>` return type.
3. `is_git_repo`'s existing intentional non-git-fixture fallback (line
   636-638's documented behavior: `run()` returning empty/`None` for a
   `TempDir` with no `.git` causes correct fallback to strict `source_head ==
   current_head` equality) is preserved byte-for-byte — this ticket must not
   regress any existing sabotage-test fixture's behavior for the "not a git
   repo at all" case, only differentiate the *other* failure causes from each
   other and from content-based `None`/`false` outcomes.
4. `document_head_is_fresh`'s existing behavior for every case that is
   currently correct is unchanged: identical `source_head`s still return
   `true` immediately; a `source_head` that fails `commit_exists` still
   returns `false`; content genuinely unchanged since `source_head` (via
   `is_ancestor_or_equal`) still returns `true`; a real, non-exempted changed
   path still produces a `DOCUMENT_HEAD_STALE` finding. Only the
   underlying-cause differentiation for `run()`'s 3 failure modes (and their
   downstream propagation through `last_commit_touching` /
   `changed_paths_between`) changes.
5. `git diff --stat` after this ticket touches only `tools/v26.8.1/src/main.rs`
   and this ticket file.

## Falsifiers

- After the fix, any of `run()`'s 3 verified failure modes (a corrupted
  `PATH` for spawn failure, a `git log`/`git diff` invocation against a
  malformed revision range for non-zero exit, a fixture with genuinely
  non-UTF8 `git` output for the third) still produces a value
  indistinguishable from either of the other two, or from a real "ran
  successfully, empty/no result" outcome.
- `is_git_repo`'s documented non-git-`TempDir` fallback to strict equality
  (the behavior every existing sabotage test in this file's `mod tests`
  depends on) changes as a side effect of this fix.
- The happy-path SHA/diff-list values returned by `is_git_repo`,
  `last_commit_touching`, or `changed_paths_between` for a real git repo
  change value, trimming, or line-splitting behavior as a side effect of
  this fix.
- `cargo test -p v26_8_1_tools` (or the equivalent workspace test invocation
  covering `tools/v26.8.1/src/main.rs`'s `mod tests`) fails, or any of the
  13 pre-existing `#[test]` items regresses, after this fix.
- `git diff --stat` after this ticket touches any file outside
  `tools/v26.8.1/src/main.rs` and `tickets/GL-EXP-019.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the collapse before touching anything:
sed -n '620,724p' tools/v26.8.1/src/main.rs
grep -n "git_provenance::" tools/v26.8.1/src/main.rs

# After the fix, confirm the 3 failure modes are distinguishable with real
# subprocess invocations (no mocked Command output), per this account's
# Chicago-style testing discipline: a real corrupted PATH for spawn failure,
# a real non-zero-exit git invocation (e.g. a bogus revision range) for the
# second, and a real fixture producing non-UTF8 git stdout for the third.

# Confirm the tool's own basic operation still works end to end:
cargo run -p v26_8_1_tools --bin ggen_v26_8_1_verifier -- --observe-only
echo "EXIT:$?"

# Confirm no regression in the file's existing test suite:
cargo test -p v26_8_1_tools

git diff --stat   # must show only tools/v26.8.1/src/main.rs and
                   # tickets/GL-EXP-019.md
```

## Evidence this ticket is grounded in (verified this session)

- Direct `sed -n '625,633p' tools/v26.8.1/src/main.rs` this session:
  `git_provenance::run()` byte-for-byte as quoted in Outcome — the identical
  `.ok().filter(|out| out.status.success()).map(|out|
  String::from_utf8_lossy(&out.stdout).trim().to_owned())` collapse-to-`None`
  shape as GL-ERRC-019's `exact_head()`, GL-EXP-005's `fresh_git_head()`, and
  GL-EXP-011's `git_head()`.
- `grep -n "fn run(root: &Path\|pub fn is_git_repo\|pub fn
  last_commit_touching\|pub fn changed_paths_between\|fn
  document_head_is_fresh" tools/v26.8.1/src/main.rs` this session: confirmed
  exact line numbers — `run` at 625, `is_git_repo` at 639,
  `last_commit_touching` at 655, `changed_paths_between` at 674,
  `document_head_is_fresh` at 683 — matching the candidate item's citation
  exactly.
- Direct `Read` of `tools/v26.8.1/src/main.rs:683-722` this session:
  confirmed `last_commit_touching`'s `None` branch (line 697-701) returns
  `false` with the comment "No history for this path reachable from HEAD --
  cannot attest freshness," and `changed_paths_between`'s `None` falls into
  the `_ => false` catch-all at line 720 — the identical branch a real,
  substantive non-exempted-drift finding takes (`Some(changed) if
  !changed.is_empty()` guard failing for either reason lands in the same
  arm).
- Direct `Read` of `tools/v26.8.1/src/main.rs:860-897` this session:
  confirmed `document_head_is_fresh`'s sole call site (line 883-887) turns
  any `false` into the identical `DOCUMENT_HEAD_STALE` finding (line
  888-896) with an identical error-message template — no branch anywhere
  in the caller distinguishes cause.
- `grep -rln "git_provenance\|document_head_is_fresh" tickets/*.md` this
  session: zero matches (exit code 1) — no existing ticket names this
  module or function.
- `grep -n "mod tests\|#\[test\]" tools/v26.8.1/src/main.rs` this session:
  exactly 13 `#[test]` items in the file (lines 1375, 1403, 1411, 1421,
  1432, 1446, 1456, 1466, 1476, 1486, 1496, 1507, 1518), none of which
  targets `git_provenance` — confirmed via `grep -n "git_provenance"
  tools/v26.8.1/src/main.rs`, which returns only the module declaration
  (line 621) and its 5 in-module call sites (lines 686, 694, 699, 704, 716),
  zero references inside the `#[cfg(test)]` region. The one `run(...)` test
  helper found in that region (`fn run(fixture: &Fixture) -> Vec<Finding>`
  at line 1359) is a same-named but semantically unrelated fixture-execution
  helper for the file's `Finding`-validation tests, not a test of
  `git_provenance::run()`.
- `grep -rln "tools/v26.8.1/src/main.rs" tickets/*.md` this session:
  6 tickets reference `main.rs` (`GL-ERRC-015`, `GL-EXP-003`, `GL-ERRC-019`,
  `GL-EXP-007`, `GL-EXP-001`, `GL-EXP-005`); per-ticket `grep -n "main.rs"`
  on each confirms every citation is to `main.rs:1-15`'s import block or
  `main.rs:145`'s `exact_head(&root)` call site, none to the
  `git_provenance` module or `document_head_is_fresh` — no boundary overlap.
- `grep -n "current_head\|fn validate_document_evidence" tools/v26.8.1/src/
  main.rs` and the call site at line 558 this session: confirmed
  `document_head_is_fresh` is reachable from `main()`'s real execution path
  (`validate_document_evidence(documents, root, source_head, findings)` at
  line 558), not dead code — it runs on every real invocation of this
  binary against a document-evidence-index.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- `cat tickets/GL-ERRC-019.md`, `tickets/GL-EXP-005.md`,
  `tickets/GL-EXP-011.md`, `tickets/GL-EXP-015.md` this session: confirmed
  each is a real, prior instance of the identical undifferentiated-sentinel
  anti-pattern (GL-ERRC-019 `EXECUTED`/fixed; GL-EXP-005/011/015 `admitted,
  NOT_STARTED`), each scoped to a distinct file/language/tool-generation with
  no line-range overlap with this ticket's target.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
undifferentiated-`None`-collapse finding for `git_provenance::run()` and its
propagation into `document_head_is_fresh`; the actual cause-distinguishing
return shape (matching the `STALE_REFERENCE_UNVERIFIABLE:<CAUSE>`-style
convention GL-ERRC-011/014 established on the Python side and GL-ERRC-019
mirrored on the Rust side) and its Chicago-style real-subprocess test
coverage have not been implemented.
