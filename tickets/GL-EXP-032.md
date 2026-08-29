# GL-EXP-032 — Create the missing CI coverage for `tools/v26.8.1` and `tools/dsrust-disposition-proposer` (two real, portable Cargo crates real CI never builds, tests, or lints)

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`cargo metadata --no-deps --format-version 1` run at the repo root this
session reports exactly one workspace member:

```json
["ggen-legacy-lsp"]
```

confirmed by `grep -c "\[workspace\]" Cargo.toml` at the repo root
returning `0` -- the root `Cargo.toml` is a single bare package with no
`[workspace]` table, so it has no members outside itself.
`tools/v26.8.1/Cargo.toml`, `tools/ggen-verifier-cli-verify/Cargo.toml`,
and `tools/dsrust-disposition-proposer/Cargo.toml` are three independent
Cargo projects (each declares its own `[workspace]` root, confirmed by
`Read`) entirely outside this graph.

`.github/workflows/ci.yml` (read in full this session, 73 lines, one
`verify` job) runs exactly five Rust commands: `cargo fmt --all -- --check`,
`cargo check --all-targets --locked`, `cargo clippy --all-targets --locked
-- -D warnings`, `cargo test --all-targets --locked`, and `cargo test
--locked --test lsp_boundary -- --nocapture` -- every one a bare
invocation from the repo root, no `--manifest-path`, no `cd`, so each
necessarily targets only the single `ggen-legacy-lsp` package `cargo
metadata` confirmed. `.github/workflows/planning-v26-8-7.yml` (read in
full this session, 25 lines) runs two Python commands
(`planning/v26.8.7/verify.py`, `skdecide_classical_engine.py --help`) --
no Rust at all.

```
$ grep -n "tools/" .github/workflows/*.yml
(no output, exit 1)
$ grep -n "manifest-path\|cd tools" .github/workflows/*.yml
(no output, exit 1)
$ grep -n "just ci-all\|just v26-ci\|just " .github/workflows/*.yml
(no output, exit 1)
```

No workflow, on any path, ever reaches into any of the three `tools/`
crates.

**The local reproduction path exists but is never invoked by CI.**
`justfile`'s `ci-all: ci v26-ci` target (comment: "the single local command
a new engineer can run to reproduce what CI gates") already runs
`tools/v26.8.1`'s full fmt/check/clippy/test ladder via `v26-ci:
v26-fmt v26-check v26-clippy v26-test` -- but that comment is currently
false: `git grep -n "just ci-all\|just v26-ci"
.github/workflows/*.yml` returns nothing, so CI itself never runs
`ci-all` or `v26-ci`; only a human choosing to run it locally exercises
`tools/v26.8.1`. `tools/dsrust-disposition-proposer` has no equivalent
justfile ladder at all -- its only recipe, `propose-disposition`, is a bare
`cargo run` wired for manual CLI invocation, and its own header comment
states plainly: "Not part of `ci`/`ci-all`/`v26-ci` and not invoked from
any workflow -- a human runs this by hand."

**This corpus's own EXECUTED tickets cite exactly this local-only path as
their acceptance evidence, not a CI receipt.** `GL-ERRC-015` ("Acceptance
(executed this session)"), `GL-ERRC-016` ("Acceptance build ... main
checkout"), `GL-ERRC-019` (`EXECUTED` -- fixed and verified this session),
and `GL-EXP-001` (`EXECUTED` -- real fix landed and re-verified) each
quote `cargo test --manifest-path tools/v26.8.1/Cargo.toml ...` run by
hand as their evidence. `GL-ERRC-022` (`EXECUTED`) wires
`propose-disposition` into `justfile` but never adds `cargo test` for that
crate to any recipe or workflow. A regression to any of the fixes these
four EXECUTED tickets claim to have landed and verified -- in either
crate -- would merge cleanly through the real, live GitHub Actions gate on
every future PR, because that gate has never once compiled, tested, or
linted either one.

**Verified this session that both crates are, right now, cleanly
CI-ready with zero blockers**, run directly from the repo root:

```
$ cargo fmt --manifest-path tools/v26.8.1/Cargo.toml -- --check
(exit 0)
$ cargo clippy --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked -- -D warnings
(exit 0, "Finished `dev` profile")
$ cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked
... test result: ok. 13 passed; 0 failed ...   (document_evidence_sabotage_tests)
... test result: ok. 0 passed; 0 failed ...    (project_coverage.rs unittests)
... test result: ok. 0 passed; 0 failed ...    (subsystem_verifier.rs unittests)
... test result: ok. 2 passed; 0 failed ...    (tests/verifier_boundary.rs)

$ cargo fmt --manifest-path tools/dsrust-disposition-proposer/Cargo.toml -- --check
(exit 0)
$ cargo clippy --manifest-path tools/dsrust-disposition-proposer/Cargo.toml --all-targets --locked -- -D warnings
(exit 0, "Finished `dev` profile")
$ cargo test --manifest-path tools/dsrust-disposition-proposer/Cargo.toml --all-targets --locked
running 4 tests
test tests::text_extracts_a_present_string_field ... ok
test tests::text_defaults_to_empty_string_when_field_is_missing ... ok
test tests::text_defaults_to_empty_string_when_field_is_not_a_string ... ok
test tests::signature_instructions_constrain_proposed_disposition_to_the_five_value_vocabulary ... ok
test result: ok. 4 passed; 0 failed
```

`tools/dsrust-disposition-proposer`'s 4 tests (added in commit `60abd88`,
confirmed by `git show --stat 60abd88`: "add real unit tests for text()
and the disposition vocabulary constraint") construct `dsrust::Example`/
`Prediction` values directly and assert on `text()`'s real return value
and the real signature-instructions string -- no network call, no
`GROQ_API_KEY` needed (confirmed by reading the four test bodies: none
constructs a `dsrust` client or awaits a live call). They are hermetic and
safe to run unconditionally in CI.

**`tools/ggen-verifier-cli-verify` is a real, documented exception, not an
oversight -- verified this session, not assumed.** Its own Cargo.toml
description states it is "a local, machine-specific dogfood consumer
wiring two sibling repos together, not something intended to build in
isolation." Running its test suite directly this session confirms why:

```
$ cargo test --manifest-path tools/ggen-verifier-cli-verify/Cargo.toml --all-targets --locked
...
thread 'ggen_verifier_bad_root_fails_closed' panicked: "CliHarness run failed:
  binary not found: 'ggen-v26-8-1-verifier' (checked CARGO_BIN_EXE_* and PATH)"
thread 'receiptctl_help_lists_verbs' panicked: "CliHarness run failed:
  binary not found: 'receiptctl' (checked CARGO_BIN_EXE_* and PATH)"
test result: FAILED. 0 passed; 7 failed
```

`scripts/ci/guard-verifier-proof.sh` (read in full this session) is this
repo's own documented gate for this crate, and it requires a `GGEN_REPO`
environment variable pointing at a **sibling checkout of the separate
`seanchatmangpt/ggen` repository** ("This gate cross-verifies against a
sibling checkout of seanchatmangpt/ggen (for chicago-tdd-tools-pack and
the ggen/receiptctl binaries)"), refusing outright if it is unset. Neither
`GGEN_REPO`, `receiptctl`, `ggen-verifier-cli-verify`, nor
`guard-verifier-proof` appears anywhere in either workflow file
(`grep -n` this session, zero matches) -- this repo's real GitHub Actions
`actions/checkout` step only ever fetches `ggen-legacy` itself, so this
crate's own gate script cannot run in that environment as CI is
configured today without also provisioning a second repository checkout.
This is a genuine, separate piece of work (deciding whether/how to
checkout a second repo in CI, or otherwise satisfy `GGEN_REPO`), not
something this ticket can fold in as an equal-effort third item -- see
Hard Law 2.

**No existing ticket covers this gap.** `grep -il "workspace\b"
tickets/GL-*.md` (run this session, not the possibly-stale grep result
from prior corpus notes) matches exactly four files: `GL-ERRC-019.md`,
`GL-EXP-007.md`, `GL-EXP-019.md`, `GL-LSP-001.md`. Reading each: `GL-
ERRC-019`'s hit is `lsp-max`'s own upstream Cargo `[workspace]` table
described as a defect *in that dependency*, unrelated to this repo's CI;
`GL-EXP-007`'s two hits are both inside a literal string constant
(`"# Chicago-TDD boundary test workspace\n"`) planted by a test fixture,
not prose about Cargo workspace topology; `GL-EXP-019`'s hit is `cargo
test -p v26_8_1_tools (or the equivalent workspace test invocation)` --
proposing a *local* reproduction command for its own fix, not CI wiring;
`GL-LSP-001`'s hit is inside its provisional `lsp-max` pin note, also
about the upstream dependency, not this repo's CI topology. None proposes
adding CI coverage for `tools/v26.8.1` or `tools/dsrust-disposition-
proposer`. `GL-EXP-024` (the closest analog in spirit) adds one Python
`unittest` step to `planning-v26-8-7.yml` for `planning/v26.8.7`, a
wholly separate Python subsystem with its own workflow file; it does not
touch `ci.yml` or any Rust `tools/` crate.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- checked there and against every ticket's Authored boundary before
writing this section. `.github/workflows/ci.yml` is also claimed by
`GL-ERRC-009` (`EXECUTED`), whose own Authored boundary scopes itself to
exactly one existing step, `"Admit exact head and one-workflow
topology"` -- this ticket adds new steps elsewhere in the same job and
does not touch that step, its `expected`/`actual` workflow-file-list
logic, or the `workflow_count` it emits (this ticket adds zero new
workflow *files*, so that count stays `2`). `justfile` already has an
`OVERLAPS.md` section listing six prior tickets across its recipe list;
this ticket adds a seventh row rather than a new section. Both overlaps
disclosed in `tickets/OVERLAPS.md` by this same write.)

```text
.github/workflows/ci.yml   # new steps appended to the existing `verify` job, for tools/v26.8.1 and tools/dsrust-disposition-proposer only
justfile                   # new dsrust-fmt/dsrust-check/dsrust-clippy/dsrust-test/dsrust-ci recipes; ci-all's dependency list extended to include dsrust-ci
tickets/GL-EXP-032.md
tickets/OVERLAPS.md        # add a `.github/workflows/ci.yml` section; add a row to the existing `justfile` section
```

No change to `tools/v26.8.1/**`, `tools/dsrust-disposition-proposer/**`,
or `tools/ggen-verifier-cli-verify/**` themselves (this ticket wires
existing, already-passing commands into CI; it does not alter either
crate's source, tests, or Cargo manifest). No change to
`.github/workflows/planning-v26-8-7.yml` or any other workflow file. No
attempt to wire `tools/ggen-verifier-cli-verify` into CI (per Hard Law 2)
and no change to `scripts/ci/guard-verifier-proof.sh`.

## Hard laws

1. The new `ci.yml` steps run the exact commands already verified in
   Outcome above (`cargo fmt --manifest-path <crate>/Cargo.toml --
   --check`, `cargo check --all-targets --locked`, `cargo clippy
   --all-targets --locked -- -D warnings`, `cargo test --all-targets
   --locked`, each with the matching `--manifest-path`) for
   `tools/v26.8.1` and `tools/dsrust-disposition-proposer` only -- not a
   paraphrase, not `just ci-all` invoked as an opaque black box (CI's
   existing five Rust steps are already inlined raw `cargo` invocations,
   not `just`-wrapped; the new steps follow that same established style
   for consistency and auditability).
2. `tools/ggen-verifier-cli-verify` is explicitly out of scope. This
   ticket does not add it to CI, does not stub or skip its
   `guard-verifier-proof.sh` gate, and does not modify that script. The
   `GGEN_REPO`/sibling-checkout requirement documented in Outcome is a
   real, separate piece of design work (a second `actions/checkout`
   step against `seanchatmangpt/ggen`, or another mechanism) left for a
   dedicated follow-on ticket, not silently dropped nor smuggled in here.
3. The new steps are additive to the existing `verify` job -- they do
   not reorder, replace, or change the pass/fail semantics of any of the
   five existing Rust steps or the "Admit exact head and one-workflow
   topology" step (`GL-ERRC-009`'s claim).
4. `workflow_count` stays `2` -- this ticket adds no new `.yml`/`.yaml`
   file under `.github/workflows/`.
5. The new `justfile` recipes (`dsrust-fmt`, `dsrust-check`,
   `dsrust-clippy`, `dsrust-test`, `dsrust-ci`) mirror the existing
   `v26-*`/`v26-ci` naming and structure exactly (one recipe per cargo
   subcommand, then an aggregate). `ci-all`'s dependency list becomes
   `ci v26-ci dsrust-ci` so the "single local command a new engineer can
   run to reproduce what CI gates" comment becomes true for all three
   Rust targets CI will now actually gate (root workspace, `v26.8.1`,
   `dsrust-disposition-proposer`) -- not just an aspiration.
   `propose-disposition`'s existing recipe body and its own header
   comment are left unmodified.
6. If any of the crates' commands behaves differently on CI's
   `ubuntu-24.04` runner than in this session's local run, that must be
   recorded honestly in this ticket's execution evidence -- this ticket
   adds enforcement of already-passing local commands; it does not get
   to silently skip or alter a test to make CI green.
7. `tickets/OVERLAPS.md` gains the two disclosures named in Authored
   boundary above, added by this same write.
8. `git diff --stat` after this ticket touches only
   `.github/workflows/ci.yml`, `justfile`, `tickets/GL-EXP-032.md`, and
   `tickets/OVERLAPS.md`.

## Falsifiers

- After the fix, `grep -n "manifest-path tools/v26.8.1\|manifest-path
  tools/dsrust-disposition-proposer" .github/workflows/ci.yml` still
  returns no match.
- The new steps are not additive -- they alter, reorder ahead of, or
  change the exit semantics of any of the five existing Rust steps or
  the "Admit exact head and one-workflow topology" step.
- `.github/workflows/ci.yml`'s `expected`/`workflow_count` logic is
  touched, or a new file under `.github/workflows/` is added, changing
  `workflow_count` away from `2`.
- `tools/ggen-verifier-cli-verify` is wired into CI, or
  `scripts/ci/guard-verifier-proof.sh` is modified, by this ticket.
- Any test in either crate is skipped, deleted, weakened, or altered to
  make it pass, rather than the CI step running the crate's existing,
  already-passing suite as-is.
- `justfile`'s `propose-disposition` recipe body or header comment is
  modified.
- `tickets/OVERLAPS.md` is not updated with both disclosures named above.
- `git diff --stat` after this ticket touches any file outside
  `.github/workflows/ci.yml`, `justfile`, `tickets/GL-EXP-032.md`, and
  `tickets/OVERLAPS.md`.

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these
are the exact commands to run once the fix lands, not yet-observed
outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
grep -n "tools/" .github/workflows/*.yml
  # expect: no output (zero matches)
grep -n "just ci-all\|just v26-ci\|just " .github/workflows/*.yml
  # expect: no output (zero matches)

# Reconfirm both crates are green in isolation (the commands the new
# steps will run, unmodified):
cargo fmt --manifest-path tools/v26.8.1/Cargo.toml -- --check
cargo clippy --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked -- -D warnings
cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked
cargo fmt --manifest-path tools/dsrust-disposition-proposer/Cargo.toml -- --check
cargo clippy --manifest-path tools/dsrust-disposition-proposer/Cargo.toml --all-targets --locked -- -D warnings
cargo test --manifest-path tools/dsrust-disposition-proposer/Cargo.toml --all-targets --locked
  # expect: all six commands exit 0, matching this ticket's Outcome section

# After the fix:
grep -n "manifest-path tools/v26.8.1\|manifest-path tools/dsrust-disposition-proposer" .github/workflows/ci.yml
  # expect: the new steps' run: lines
just --list | grep dsrust
  # expect: dsrust-fmt, dsrust-check, dsrust-clippy, dsrust-test, dsrust-ci
just ci-all
  # expect: exits 0, now genuinely exercising root + v26.8.1 + dsrust-disposition-proposer

git diff --stat   # must show only .github/workflows/ci.yml, justfile,
                   # tickets/GL-EXP-032.md, tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `cargo metadata --no-deps --format-version 1` at the repo root this
  session: one package, `ggen-legacy-lsp`.
- `grep -c "\[workspace\]" Cargo.toml` this session: `0`.
- Direct `Read` of `tools/v26.8.1/Cargo.toml`,
  `tools/ggen-verifier-cli-verify/Cargo.toml`,
  `tools/dsrust-disposition-proposer/Cargo.toml` this session: each opens
  with its own `[workspace]` table.
- Direct `Read` of `.github/workflows/ci.yml` in full this session (`wc
  -l` confirms 73 lines): exactly five Rust `run:` steps, all bare
  `cargo` invocations with no `--manifest-path`.
- Direct `Read` of `.github/workflows/planning-v26-8-7.yml` in full this
  session (`wc -l` confirms 25 lines): two Python `run:` steps, no Rust.
- `grep -n "tools/" .github/workflows/*.yml`,
  `grep -n "manifest-path\|cd tools" .github/workflows/*.yml`,
  `grep -n "just ci-all\|just v26-ci\|just " .github/workflows/*.yml`,
  `grep -n "GGEN_REPO\|receiptctl\|ggen-verifier-cli-verify\|guard-
  verifier-proof" .github/workflows/*.yml`: all four run this session,
  all zero matches.
- Direct `Read` of `justfile` in full this session: `ci-all: ci v26-ci`
  (line 37), `v26-ci: v26-fmt v26-check v26-clippy v26-test` (line 33),
  `propose-disposition`'s header comment states verbatim "Not part of
  `ci`/`ci-all`/`v26-ci` and not invoked from any workflow."
- Direct `Read` of `tickets/GL-ERRC-015.md`, `GL-ERRC-016.md`,
  `GL-ERRC-019.md`, `GL-EXP-001.md`, `GL-ERRC-022.md` this session:
  Status lines confirmed `EXECUTED` (verbatim, for all five); each cites
  a local `cargo test --manifest-path tools/v26.8.1/Cargo.toml ...` (or,
  for `GL-ERRC-022`, a bare `cargo run --manifest-path
  tools/dsrust-disposition-proposer/Cargo.toml ...`) as its acceptance
  evidence, run by hand this session or a prior one -- never a CI
  receipt.
- `git show --stat 60abd88` this session: confirms the commit message
  ("add real unit tests for text() and the disposition vocabulary
  constraint") and that it touches
  `tools/dsrust-disposition-proposer/src/main.rs`.
- `grep -n "#\[test\]" tools/dsrust-disposition-proposer/src/main.rs`
  this session: 4 matches, lines 130, 141, 149, 162.
- Real, direct execution this session (not simulated) of all six
  fmt/clippy/test commands for `tools/v26.8.1` and
  `tools/dsrust-disposition-proposer`: all six exit `0`, full output
  captured in Outcome above (13+0+0+2 tests passing for `v26.8.1`, 4
  tests passing for `dsrust-disposition-proposer`).
- Real, direct execution this session of `cargo test --manifest-path
  tools/ggen-verifier-cli-verify/Cargo.toml --all-targets --locked`:
  `FAILED. 0 passed; 7 failed`, every failure `binary not found ...
  (checked CARGO_BIN_EXE_* and PATH)` for `ggen-v26-8-1-verifier` or
  `receiptctl`.
- Direct `Read` of `scripts/ci/guard-verifier-proof.sh` in full this
  session: requires `GGEN_REPO` env var (a sibling `seanchatmangpt/ggen`
  checkout) or refuses with exit `1`; builds `receiptctl` from
  `$GGEN_REPO/examples/receiptctl`.
- `grep -il "workspace\b" tickets/GL-*.md` this session: exactly
  `GL-ERRC-019.md`, `GL-EXP-007.md`, `GL-EXP-019.md`, `GL-LSP-001.md`
  (four files -- re-run directly this session, not assumed from any
  prior corpus note). Per-file `grep -n "workspace"` on each this
  session confirms none discusses CI coverage of `tools/v26.8.1` or
  `tools/dsrust-disposition-proposer` (see Outcome for the per-file
  breakdown).
- `grep -l "\.github/workflows/ci\.yml" tickets/GL-*.md`,
  `grep -l "tools/v26\.8\.1" tickets/GL-*.md`,
  `grep -l "tools/dsrust-disposition-proposer" tickets/GL-*.md`, and
  `grep -l "^justfile\|\`justfile\`" tickets/GL-*.md`, all run this
  session: confirms which existing tickets touch these paths; reading
  each candidate's `## Authored boundary` section directly (not just the
  grep hit) confirms only `GL-ERRC-009` (`EXECUTED`, one disjoint step of
  `ci.yml`) claims edit-ownership of any part of `ci.yml`'s content, and
  no ticket claims a `justfile` recipe this ticket's new
  `dsrust-fmt`/`dsrust-check`/`dsrust-clippy`/`dsrust-test`/`dsrust-ci`
  names would collide with.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base and the Base most other tickets in
  this corpus were drafted against.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
CI-coverage gap (confirmed live, this session, by directly running the
exact commands the new CI steps would run) and the two
`tickets/OVERLAPS.md` disclosures its own Hard Law 7 requires. No
workflow or justfile edit has been made.
