# GL-EXP-001 — Eliminate the byte-for-byte duplicate `resolve_root()` in `subsystem_verifier.rs`

**Status:** `EXECUTED` — real fix landed in the main checkout and re-verified there
2026-08-21 (this ticket's own on-disk Status line was previously left at
`NOT_STARTED` despite the code fix landing in a prior pass — a genuine
record-keeping gap, closed here; see `docs/v26.9.1/RELEASE-NOTES.md`'s
"honest conclusion" section for the full account of that gap).
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

## Hard laws

1. `subsystem_verifier.rs`'s private `fn resolve_root` (lines 375-391) is
   deleted outright, not merely marked deprecated or left dead.
2. `subsystem_verifier.rs` calls the canonical
   `v26_8_1_tools::coverage_projection::resolve_root` in its place (via a
   `use` import, matching `main.rs`'s and `project_coverage.rs`'s existing
   import style) -- behavior at the call site (line 410) is unchanged.
3. `tools/v26.8.1/src/coverage_projection.rs`'s canonical `resolve_root`
   itself is not modified by this ticket -- this is a call-site
   consolidation, not a behavior change to the shared logic.
4. Both existing tests in `tools/v26.8.1/tests/verifier_boundary.rs`
   (`all_three_binaries_fail_closed_on_missing_root` and
   `all_three_binaries_get_past_root_resolution_with_real_agents_md`) must
   still pass unmodified after this ticket, proving `subsystem_verifier`'s
   externally observable root-resolution behavior (exit code, stderr
   wording, and the positive real-`AGENTS.md` path) is bit-for-bit
   unchanged despite the internal implementation now being a shared import
   instead of a private copy.

## Falsifiers

- `grep -n "^fn resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs`
  still matches after this ticket executes (private copy not actually
  removed).
- `cargo test --manifest-path tools/v26.8.1/Cargo.toml --test
  verifier_boundary --locked` fails or changes its passing test count from
  the current `2 passed; 0 failed`.
- `cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked` fails to
  compile after the import is added (e.g. a visibility or path error).
- `git diff --stat` after this ticket touches any file outside
  `tools/v26.8.1/src/bin/subsystem_verifier.rs` and `tickets/GL-EXP-001.md`.

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the fix lands, not yet-observed outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy
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

## Evidence this ticket is grounded in (verified this session)

- `diff <(sed -n '233,247p' tools/v26.8.1/src/coverage_projection.rs) <(sed -n '376,390p' tools/v26.8.1/src/bin/subsystem_verifier.rs)`
  -- real output this session, single-line diff:
  `std::env::current_dir()?` vs. `env::current_dir()?`, otherwise identical.
- `grep -n "resolve_root" tools/v26.8.1/src/bin/*.rs tools/v26.8.1/src/*.rs`
  -- real output this session confirms `main.rs` (line 10, import) and
  `project_coverage.rs` (line 22, import) both consume the canonical
  function; `subsystem_verifier.rs` (line 375) alone still declares its own.
- `cat tools/v26.8.1/Cargo.toml` -- confirms a single package with
  `[lib] name = "v26_8_1_tools"` and all three binaries (`ggen-v26-8-1-verifier`,
  `subsystem_verifier`, `project_coverage`) as `[[bin]]` targets of that same
  package, so the import path used by the other two binaries is directly
  available to `subsystem_verifier.rs` with no new dependency.
- `sed -n '1,14p' tools/v26.8.1/tests/verifier_boundary.rs` -- the test
  file's own doc comment names "the copies in each `src/bin/*.rs`" as an
  already-known but unaddressed duplication.
- `grep -l "subsystem_verifier" tickets/*.md` -- real output this session:
  `GL-AUTO-001.md`, `GL-ERRC-015.md`, `GL-ERRC-016.md`, `GL-ERRC-019.md`;
  none of the four reference `subsystem_verifier.rs`'s private `resolve_root`.
- `cd tools/v26.8.1 && cargo test --test verifier_boundary --locked` -- real
  output this session: `running 2 tests ... test
  all_three_binaries_fail_closed_on_missing_root ... ok` and `test
  all_three_binaries_get_past_root_resolution_with_real_agents_md ... ok`,
  `test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered
  out` -- confirms the pre-fix baseline both regression tests this ticket
  relies on are currently green, so any post-fix failure is attributable to
  this ticket's own change.

## Standing

`ALIVE`, re-verified in the main checkout 2026-08-21:

```
$ grep -n "^fn resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs
(no match — private copy gone)
$ grep -n "use v26_8_1_tools::coverage_projection::resolve_root" tools/v26.8.1/src/bin/subsystem_verifier.rs
37:use v26_8_1_tools::coverage_projection::resolve_root;
$ just ci-all
... test result: ok. 2 passed; 0 failed ... (verifier_boundary.rs)
exit 0
```

Canonical `resolve_root()` in `coverage_projection.rs` untouched
(`git diff --stat` on that file: empty), satisfying this ticket's own
Hard Law 3.
