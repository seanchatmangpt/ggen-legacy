# GL-EXP-029 — Eliminate the dead `legacy_disposition_summary` field in `subsystem_verifier.rs`'s `Manifest` struct

**Status:** `EXECUTED` — dead field deleted, build and full test suite verified green
**Standing:** `ALIVE` — drafted by standing ultracode exploration cron, executed and
verified this session

**Recovery note**: this was the "eliminate" quadrant's real, verified finding
from this pass; its file write did not land (0 of 4 quadrant writes this
pass failed silently). Reconstructed from the workflow's own returned
result, not re-invented.

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/src/bin/subsystem_verifier.rs:54`'s `Manifest` struct
declares `#[serde(default)] #[allow(dead_code)] legacy_disposition_summary:
serde_json::Value` — deserialized from the real fixture
`.ggen/v26.8.1/subsystem-evidence-manifest.json`, which populates it with
substantive per-subsystem data (`total_legacy_capabilities: 65`, per-
subsystem `closed`/`total`/`unknown` counts, `total_with_disposition_unknown`,
`total_with_matching_passed_equivalence_case`) — real, meaningful data the
independent verifier reads and then discards rather than cross-checking
against `CATALOG`. `grep -n "legacy_disposition_summary"` on the file
returns exactly one match, the declaration itself. Same class of fix
`GL-ERRC-015` (executed) already applied to this crate's dead
`read_coverage_csv_bytes()` function, here a struct field in a sibling
file `GL-ERRC-015` never touched.

## Authored boundary

```text
tools/v26.8.1/src/bin/subsystem_verifier.rs   # delete the dead field only
tickets/GL-EXP-029.md
```

## Hard laws

1. The field is either deleted outright, or (if a future ticket wants to
   actually use the data) wired into a real cross-check against `CATALOG`
   — this ticket only removes it, it does not add new verification logic.
2. `Manifest`'s other fields and every other struct in the file are
   untouched.

## Falsifiers

- `grep -n "legacy_disposition_summary" tools/v26.8.1/src/bin/subsystem_verifier.rs`
  still matches after this ticket executes.
- `cargo build`/`cargo test --manifest-path tools/v26.8.1/Cargo.toml
  --all-targets --locked` fails after the field is removed (would indicate
  something elsewhere actually depended on it, contradicting this
  ticket's own evidence).

Both falsifiers checked this session and neither triggered — see Evidence below.

## Acceptance (executed this session)

```bash
cd /Users/sac/ggen-legacy/.claude/worktrees/wf_dbca2a9c-5eb-1
grep -c "legacy_disposition_summary" tools/v26.8.1/src/bin/subsystem_verifier.rs   # -> 0
cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked                      # -> Finished, no warnings
cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked         # -> 15 passed; 0 failed
git diff --stat   # only subsystem_verifier.rs + this ticket file
```

## Evidence (this session, 2026-08-21)

Field removed — only the declared field itself and its two attribute lines,
per Hard Law 1 (deleted outright, no new logic added) and Hard Law 2
(every other field/struct in the file untouched):

```diff
     subsystems: Vec<SubsystemRecord>,
-    #[serde(default)]
-    #[allow(dead_code)]
-    legacy_disposition_summary: serde_json::Value,
     receipt_digest: String,
```

Falsifier 1 — grep for the removed field:

```
$ grep -c "legacy_disposition_summary" tools/v26.8.1/src/bin/subsystem_verifier.rs
0
```

Falsifier 2 — build:

```
$ cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked
   Compiling ggen-v26-8-1-verifier v26.8.1 (.../tools/v26.8.1)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 15.01s
```

No warnings (in particular no `unused import: serde_json::Value` or
dead-code warnings, confirming `serde_json::Value` and `serde::Deserialize`
remain used elsewhere in the file and nothing depended on the removed field).

Falsifier 2 — full test suite (`--all-targets`), real subprocess run, all
green:

```
$ cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked
running 0 tests   (unittests src/lib.rs)
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

running 13 tests   (unittests src/main.rs, document_evidence_sabotage_tests::*)
test result: ok. 13 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

running 0 tests   (unittests src/bin/project_coverage.rs)
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

running 0 tests   (unittests src/bin/subsystem_verifier.rs)
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

running 2 tests   (tests/verifier_boundary.rs)
test all_three_binaries_fail_closed_on_missing_root ... ok
test all_three_binaries_get_past_root_resolution_with_real_agents_md ... ok
test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

Total: 15 passed, 0 failed, across every target — nothing depended on the
removed field, confirming the ticket's own dead-code evidence.

Diff boundary check (Hard Law 2 / Authored boundary):

```
$ git diff --stat
 tools/v26.8.1/src/bin/subsystem_verifier.rs | 3 ---
 1 file changed, 3 deletions(-)
```

Only the 3 lines of the dead field (and its two `#[...]` attributes) were
removed; no other line in `subsystem_verifier.rs` changed, and no file
outside the authored boundary was touched.

## Standing

`ALIVE` — executed and verified this session (2026-08-21). Both falsifiers
in this ticket ran for real and neither triggered: the field is gone
(`grep -c` = 0) and both `cargo build` and `cargo test --all-targets`
pass clean with zero warnings and zero failures.
