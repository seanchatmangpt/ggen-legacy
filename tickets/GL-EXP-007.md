# GL-EXP-007 — Raise `resolve_root()`'s content-blind `AGENTS.md` check to a real content/marker validation

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

The canonical `resolve_root()` in `tools/v26.8.1/src/coverage_projection.rs:232-248`
(re-read directly this session, matches verbatim) admits any directory as a
valid repository root as soon as it finds a file literally named `AGENTS.md`
in the walk-up-from-cwd loop:

```rust
pub fn resolve_root(args: &[String]) -> Result<PathBuf> {
    let explicit = args
        .windows(2)
        .find(|pair| pair[0] == "--root")
        .map(|pair| PathBuf::from(&pair[1]));
    let mut current = explicit.unwrap_or(std::env::current_dir()?);
    loop {
        if current.join("AGENTS.md").is_file() {
            return current
                .canonicalize()
                .context("canonicalize repository root");
        }
        if !current.pop() {
            bail!("repository root not found; pass --root <path>");
        }
    }
}
```

Line 239's only admission test is `current.join("AGENTS.md").is_file()` --
no `fs::read`, no content check, no marker-string match. This repo's own
`tools/v26.8.1/tests/verifier_boundary.rs:53-78`
(`all_three_binaries_get_past_root_resolution_with_real_agents_md`, re-run
live this session: `running 2 tests ... test
all_three_binaries_get_past_root_resolution_with_real_agents_md ... ok ...
test result: ok. 2 passed; 0 failed`) proves this is not an edge case but
the tested, intended behavior: it plants
`ws.write_file("AGENTS.md", "# Chicago-TDD boundary test workspace\n")` --
one line, content unrelated to this repo's real `AGENTS.md` -- and asserts
all three real compiled binaries (`ggen-v26-8-1-verifier`,
`subsystem_verifier`, `project_coverage`) get past root resolution with it.
By contrast, this repo's real `AGENTS.md` at the true root is a substantive,
239-line, 10801-byte file whose first lines identify the exact repo it
governs: `# AGENTS.md — ggen-legacy executable reconstruction` /
`This file governs \`seanchatmangpt/ggen-legacy\`.` (confirmed by direct
read this session) -- a real, checkable marker the current admission logic
never looks at.

The same content-blind body is duplicated verbatim (module-qualification
aside) in `tools/v26.8.1/src/bin/subsystem_verifier.rs:375-391` (confirmed
by direct read this session: identical `current.join("AGENTS.md").is_file()`
test at line 382). That duplicate is `GL-EXP-001`'s (admitted, `NOT_STARTED`)
own target for deletion-in-favor-of-import, not a second copy of this
ticket's concern -- see Authored boundary below.

**Two existing tickets were checked and neither covers this gap.**
`grep -il resolve_root tickets/*.md` (re-run this session) returns exactly
`GL-EXP-001.md` and `GL-EXP-003.md`:

- `GL-EXP-001.md` (admitted, `NOT_STARTED`) is a call-site deduplication
  only -- deleting `subsystem_verifier.rs`'s private copy in favor of
  importing the canonical function. Its own Hard Law 3 states verbatim:
  "`tools/v26.8.1/src/coverage_projection.rs`'s canonical `resolve_root`
  itself is not modified by this ticket -- this is a call-site
  consolidation, not a behavior change to the shared logic." Its Authored
  boundary states "No change to `tools/v26.8.1/src/coverage_projection.rs`
  (the canonical `resolve_root` itself)". The existence-vs-content gap is
  explicitly out of that ticket's scope.
- `GL-EXP-003.md` (admitted, `NOT_STARTED`) targets a different function in
  the same file, `project_coverage_rows`'s undifferentiated `None`-branch
  fallback (lines 172-202). Its own text mentions `resolve_root` exactly
  once, at line 176, inside its "Evidence" section's grep-derived coverage
  inventory ("`project_coverage_rows`, `resolve_root`, and
  `aggregate_legacy_disposition` have zero `#[test]` coverage in this
  file") -- not in its Authored-boundary exclusion list, and not as any
  quoted "No change to ... resolve_root" clause. (The candidate write-up
  that proposed this ticket asserted such a quoted Authored-boundary
  exclusion clause exists in `GL-EXP-003.md`; re-checked directly this
  session, no such clause or quote appears anywhere in the file --
  corrected here rather than repeated, per this ticket corpus's own
  precedent in `GL-EXP-004.md`'s "Correction to the candidate's own
  evidence" paragraph.) `GL-EXP-003` neither modifies nor discusses
  `resolve_root`'s validation logic; its one mention is incidental grep
  output, not scope.

**`docs/v26.9.1/RELEASE-NOTES.md` narrates this exact finding but misattributes
it to ticket coverage that doesn't exist.** Lines 483-490 (re-read directly
this session) read:

```text
- `GL-EXP-003`/`004` (raise/create): `project_coverage_rows()`'s
  `None`-branch fallback is undifferentiated from a legitimately-unknown
  subsystem (same class of bug `GL-ERRC-019` already fixed for
  `exact_head()`, in the same file, different function); `resolve_root()`
  verifies only that a file named `AGENTS.md` exists, never its content —
  proven by this repo's own `verifier_boundary.rs` test, which plants an
  unrelated one-line file under that name and confirms all 3 binaries
  accept it as a valid repo root.
```

This bundles the `resolve_root()` content-blindness finding into the same
bullet as `GL-EXP-003`/`004`, reading as though ticket `004` covers it. It
does not: `tickets/GL-EXP-004.md`, read in full this session, is entirely
about wiring `planning/v26.8.7/cli.py`'s 10 subcommands into `justfile` as
an optional pass-through recipe -- `grep -n "resolve_root\|AGENTS.md"
tickets/GL-EXP-004.md` (re-run this session) returns zero matches anywhere
in that file's Outcome, Authored boundary, Hard laws, Falsifiers,
Acceptance, or Evidence sections. This is the same
release-notes/real-ticket-content mismatch pattern already present
elsewhere in this doc (the `gl-lsp-001-runtime.yml` bullet nearby), and it
means the underlying `resolve_root()` gap remains genuinely unticketed
until this ticket.

**Also checked:** `GL-EXP-002.md` (dead absolute-path dev-dependency) is
unrelated to root resolution. No other `GL-*` ticket in `tickets/` (23
files, `grep -il resolve_root tickets/*.md` confirmed only the two above)
references `resolve_root` at all.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` --
check there before assuming sole ownership of a path below.)

```text
tools/v26.8.1/src/coverage_projection.rs   # resolve_root() content check only
tools/v26.8.1/tests/verifier_boundary.rs   # add negative content-check test(s)
tickets/GL-EXP-007.md
```

No change to `subsystem_verifier.rs`'s private `resolve_root` copy
(lines 375-391) -- that file's disposition (delete private copy, import
canonical) is `GL-EXP-001`'s exclusive boundary. **Disclosed dependency**:
if this ticket executes before `GL-EXP-001`, `subsystem_verifier`'s own
binary will still accept content-blind `AGENTS.md` files via its
un-deduplicated private copy until `GL-EXP-001` also lands; this ticket
does not attempt to fix that copy directly to avoid conflicting with
`GL-EXP-001`'s ownership of that file. No change to `main.rs`'s or
`project_coverage.rs`'s call sites beyond what is strictly required to keep
compiling against `resolve_root`'s existing `Result<PathBuf>` signature. No
change to `CANONICAL_SUBSYSTEMS`, `project_coverage_rows`, or any other
function in `coverage_projection.rs` -- this ticket's diff is scoped to the
body of `resolve_root` (lines 232-248) plus its own new test coverage.

## Hard laws

1. `resolve_root()` must reject a directory whose only qualifying file is
   an `AGENTS.md` that fails a real content check -- at minimum, the file
   must be non-empty and must contain a repo-identifying marker (e.g. the
   literal substring `ggen-legacy`, matching this repo's real `AGENTS.md`
   opening line) rather than being accepted on `is_file()` alone. The exact
   marker string/shape is left to implementation, not decided here (same
   pattern as `GL-EXP-003`'s Standing note leaving its replacement literal
   to implementation).
2. A directory whose `AGENTS.md` passes the new content check must resolve
   identically to today's behavior -- the positive path (a real,
   substantive `AGENTS.md`, including this repo's own) is not changed.
3. `resolve_root`'s public signature (`fn resolve_root(args: &[String]) ->
   Result<PathBuf>`) is unchanged -- this is a body-only behavior
   tightening, not an API change, so `main.rs`/`project_coverage.rs`'s
   existing call sites need no edits.
4. The existing `tools/v26.8.1/tests/verifier_boundary.rs` test
   `all_three_binaries_fail_closed_on_missing_root` must still pass
   unmodified.
5. A new test (unit-level in `coverage_projection.rs`, and/or an addition
   to `verifier_boundary.rs` mirroring its existing `TempWorkspace`
   pattern) must plant an `AGENTS.md`-named file that fails the new content
   check (e.g. empty, or lacking the marker) and assert `resolve_root`
   fails closed on it -- proving the negative branch the current test suite
   has zero coverage of.

## Falsifiers

- After the fix, `tools/v26.8.1/tests/verifier_boundary.rs`'s existing
  `all_three_binaries_get_past_root_resolution_with_real_agents_md` test
  (which plants `"# Chicago-TDD boundary test workspace\n"`) still needs to
  be weakened or deleted rather than kept passing on content that satisfies
  the new check as-is, without the test itself being updated to plant
  qualifying content deliberately.
- A directory with an empty, zero-byte `AGENTS.md` (or one otherwise
  clearly not this repo's) still resolves successfully after the fix.
- `resolve_root`'s signature changes, forcing edits to
  `tools/v26.8.1/src/main.rs` or `tools/v26.8.1/src/bin/project_coverage.rs`
  beyond what compiles unmodified today.
- `cargo test --manifest-path tools/v26.8.1/Cargo.toml --test
  verifier_boundary --locked` fails, or its currently-passing 2 tests drop
  below 2 (only additions, no regressions, are acceptable).
- `cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked` fails to
  compile after the change.
- `git diff --stat` touches `tools/v26.8.1/src/bin/subsystem_verifier.rs`
  (that file's disposition belongs to `GL-EXP-001`, not this ticket).

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the fix lands, not yet-observed outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
sed -n '232,248p' tools/v26.8.1/src/coverage_projection.rs
cd tools/v26.8.1 && cargo test --test verifier_boundary --locked && cd ../..
# expect: running 2 tests ... 2 passed; 0 failed

# After the fix, reconfirm the positive path (this repo's own real
# AGENTS.md) still resolves:
cd tools/v26.8.1 && cargo run --bin project_coverage -- --root /Users/sac/ggen-legacy 2>&1 | head -5; cd ../..

# Reconfirm the new negative-path test exists and passes, and the existing
# two tests are unmodified and still pass:
cd tools/v26.8.1 && cargo test --test verifier_boundary --locked && cd ../..
# expect: 3 (or more) passed; 0 failed

cd tools/v26.8.1 && cargo build --locked && cd ../..

git diff --stat   # must show only coverage_projection.rs, verifier_boundary.rs,
                   # and tickets/GL-EXP-007.md -- never subsystem_verifier.rs
```

## Evidence this ticket is grounded in (verified this session)

- `sed -n '232,248p' tools/v26.8.1/src/coverage_projection.rs` -- real
  output this session, matches the quoted function body verbatim,
  confirming `current.join("AGENTS.md").is_file()` (line 239) is the sole
  admission test with no content read anywhere in the function.
- `sed -n '53,78p' tools/v26.8.1/tests/verifier_boundary.rs` -- real output
  this session, confirms `all_three_binaries_get_past_root_resolution_with_real_agents_md`
  plants `"# Chicago-TDD boundary test workspace\n"` under `AGENTS.md` and
  asserts all 3 binaries get past root resolution with it.
- `cd tools/v26.8.1 && cargo test --test verifier_boundary --locked` --
  real output this session: `running 2 tests ... test
  all_three_binaries_fail_closed_on_missing_root ... ok ... test
  all_three_binaries_get_past_root_resolution_with_real_agents_md ... ok ...
  test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered
  out` -- confirms the pre-fix baseline is currently green.
- `ls -la AGENTS.md; wc -l AGENTS.md` -- real output this session: a real,
  10801-byte, 239-line file at the true repo root, opening with
  `# AGENTS.md — ggen-legacy executable reconstruction` /
  `This file governs \`seanchatmangpt/ggen-legacy\`.` -- confirming this
  repo's real root marker file has substantive, identifiable content that
  the current check never inspects.
- `grep -il resolve_root tickets/*.md` -- real output this session:
  `tickets/GL-EXP-001.md`, `tickets/GL-EXP-003.md`, no others.
- Read `tickets/GL-EXP-001.md` in full this session: Hard Law 3 and the
  Authored-boundary section both explicitly state the canonical
  `resolve_root` is not modified by that ticket (call-site dedup only).
- Read `tickets/GL-EXP-003.md` in full this session, and
  `grep -n "resolve_root" tickets/GL-EXP-003.md` (real output: one match,
  line 176, inside the Evidence section's test-coverage inventory sentence)
  -- confirms `resolve_root` appears there only incidentally, not as an
  Authored-boundary exclusion clause and not as any "No change to ...
  resolve_root" quote; no such quote exists in the file. This corrects an
  inaccurate citation in the candidate write-up that proposed this ticket.
- `sed -n '375,391p' tools/v26.8.1/src/bin/subsystem_verifier.rs` -- real
  output this session, confirms the private duplicate at line 382 carries
  the identical `current.join("AGENTS.md").is_file()` content-blind check,
  and that `GL-EXP-001` (not this ticket) owns that file's disposition.
- `grep -n "" docs/v26.9.1/RELEASE-NOTES.md | sed -n '480,495p'` -- real
  output this session, confirms lines 483-490 narrate the exact
  `resolve_root()` content-blindness finding under a `GL-EXP-003`/`004`
  bullet.
- `grep -n "resolve_root\|AGENTS.md" tickets/GL-EXP-004.md` -- real output
  this session: zero matches. Read `tickets/GL-EXP-004.md` in full this
  session: its Outcome, Authored boundary, Hard laws, and Evidence sections
  are entirely about wiring `planning/v26.8.7/cli.py` into `justfile`;
  `resolve_root` and `AGENTS.md`-content validation are never mentioned.
- `ls tickets/GL-EXP-*.md` -- real output this session: `GL-EXP-001.md`
  through `GL-EXP-004.md` exist; `GL-EXP-005.md`/`GL-EXP-006.md` do not;
  `GL-EXP-007.md` did not exist prior to this ticket being written.
- Read `tickets/GL-EXP-002.md` directly this session: confirmed unrelated
  (a dead absolute-path dev-dependency in a different crate's
  `Cargo.toml`), not a `resolve_root` ticket.
- `grep -n "mod.*test\|#\[test\]\|fn.*resolve_root"
  tools/v26.8.1/src/coverage_projection.rs` -- real output this session:
  the only test module in the file is `exact_head_tests`; `resolve_root`
  has zero `#[test]` coverage at the unit level, and
  `verifier_boundary.rs`'s two black-box tests never exercise a
  content-failing (as opposed to existence-failing) `AGENTS.md`.

## Standing

`UNKNOWN` -- not started. This ticket only establishes that `resolve_root()`'s
`AGENTS.md` admission test must be raised from existence-only to a real
content/marker check, and that neither `GL-EXP-001`, `GL-EXP-003`, nor
`GL-EXP-004` actually covers this gap despite `RELEASE-NOTES.md`'s bundled
citation. The specific marker string/content-check shape is left to
implementation, not decided here. No code has been written or run beyond
the read-only verification commands captured above.
