# GL-EXP-033 — Eliminate the false "committed fixture" premise: `.ggen/v26.8.1/subsystem-evidence-manifest.json` is gitignored and never auto-generated

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE` (documentation/decision-level only -- no `.gitignore` edit performed by this ticket)
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/src/bin/subsystem_verifier.rs:40` hardcodes the binary's
default manifest input path as a `const`:

```rust
const MANIFEST_REL: &str = ".ggen/v26.8.1/subsystem-evidence-manifest.json";
```

Verified this session: `git ls-files .ggen/` returns **zero matches** --
nothing under `.ggen/` is tracked by git at all. `git check-ignore -v
.ggen/v26.8.1/subsystem-evidence-manifest.json` confirms why:
`.gitignore:17:.ggen/` -- a blanket exclusion rule. `grep -rn
"subsystem_evidence_manifest\.py" justfile .github/workflows/*.yml
tools/v26.8.1/src/bin/subsystem_verifier.rs` finds only one hit, a comment
in `subsystem_verifier.rs` itself noting the generator is "architecturally
separate" -- the generator (`tools/v26.8.1/subsystem_evidence_manifest.py`,
the sole script capable of producing this file) is never invoked by CI or
`justfile`. A genuinely fresh clone of this repository has neither the
manifest file nor any automated step that would create it.

**This directly contradicts how multiple admitted tickets describe this
exact file.** `tickets/GL-EXP-031.md` (admitted, `NOT_STARTED`, read in
full this session) runs a real adversarial exploit against what its own
prose calls "the real, currently-committed
`.ggen/v26.8.1/subsystem-evidence-manifest.json` fixture" (its Evidence
section, verbatim) -- a factual claim `git ls-files` disproves directly.
`tickets/GL-ERRC-016.md`, `tickets/GL-ERRC-019.md`, `tickets/GL-EXP-001.md`
(all `EXECUTED`) each quote real `cargo build`/`cargo test` runs against
this same working tree without noting that the fixture their own verified
runs implicitly depend on for full end-to-end behavior (as opposed to the
unit/integration test suite, which this session confirmed below does not
exercise the default binary path) is untracked.

**Verified this session with a real, reverted experiment**, not asserted
from reading source alone: moved
`.ggen/v26.8.1/subsystem-evidence-manifest.json` aside (to a scratch
backup, confirmed via `diff` to be byte-identical before/after restore)
and re-ran `cargo test --manifest-path tools/v26.8.1/Cargo.toml
--all-targets --locked` with the fixture absent:

```text
running 13 tests
... (document_evidence_sabotage_tests, 13/13 ok)
running 2 tests
... (tests/verifier_boundary.rs, 2/2 ok)
```

All 15 tests still passed -- confirming the `cargo test` suite itself does
**not** exercise `subsystem_verifier`'s default `MANIFEST_REL` path (no
test invokes the compiled binary against its own default manifest
location; `tests/verifier_boundary.rs`'s two tests both pass `--manifest`
explicitly to a `TempDir` fixture). This means the missing-fixture gap is
currently invisible to `cargo test`, but is real and load-bearing the
moment anyone runs the compiled `subsystem_verifier` binary directly with
no `--manifest` override -- exactly what `GL-EXP-031`'s own adversarial
exploit, and any real admission-workflow invocation of this binary, does.
The moved file was restored and independently re-verified byte-identical
to its pre-move content via `diff` before this ticket was drafted; `git
status --porcelain -- .ggen/` is empty (as expected for a gitignored,
untracked path) both before and after.

**Severity note, not glossed over**: this gap is currently non-triggering
in real CI, because `GL-EXP-032` (admitted, `NOT_STARTED`) already
establishes that `tools/v26.8.1` is never built or tested by real CI at
all today. But `GL-EXP-032`'s own proposed fix -- adding `cargo test
--manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked` as a real
CI step -- would land on exactly the same fresh-checkout-in-CI runner
where this manifest is absent. Per this session's own live experiment
above, the `cargo test` suite itself would still pass (it doesn't reach
the default-manifest binary path), so `GL-EXP-032` executing as currently
scoped would **not** be broken by this gap -- but any future CI step that
runs the compiled `subsystem_verifier` binary directly (e.g. as a real
admission gate, not just `cargo test`) would immediately hit
`MANIFEST_REL`'s absence on a fresh runner. Naming this now, before that
step is added, is cheaper than discovering it after.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- checked this session, no existing section for `.gitignore`,
`.ggen/v26.8.1/subsystem-evidence-manifest.json`, or
`tools/v26.8.1/subsystem_evidence_manifest.py`.)

```text
tickets/GL-EXP-033.md
```

This ticket is a pure finding -- it does not edit `.gitignore`, does not
commit the fixture, does not modify `tools/v26.8.1/subsystem_evidence_manifest.py`
or `tools/v26.8.1/src/bin/subsystem_verifier.rs`, and does not edit
`tickets/GL-EXP-031.md`'s own wording (that ticket's own re-verification at
execution time, per its own Hard Laws, would re-derive the same fact this
ticket names). Deciding the actual resolution -- (a) narrow
`.gitignore`'s `.ggen/` rule and commit a real fixture, or (b) wire
`subsystem_evidence_manifest.py`'s generation into `justfile`/CI as a
pre-step before anything reads `MANIFEST_REL`'s default path -- is a
repo-owner/follow-up-ticket decision, not made unilaterally here, matching
this repo's own established precedent (`GL-ERRC-010`, `GL-ERRC-020`,
`GL-EXP-010`) of naming a real gap and its candidate resolutions without
silently picking one.

## Hard laws

1. This ticket does not modify `.gitignore`, any file under `.ggen/`, or
   `tools/v26.8.1/subsystem_evidence_manifest.py`/`subsystem_verifier.rs`.
2. The reverted experiment described in Outcome must be exactly that --
   reverted, with a byte-identical restore independently confirmed via
   `diff` before this ticket is considered drafted (already done this
   session; see Evidence).
3. This ticket names exactly two candidate resolutions (commit the
   fixture with a narrowed `.gitignore`, or auto-generate it as a
   justfile/CI pre-step) without choosing between them -- a future
   execution of this ticket (or a dedicated follow-up) makes that call
   explicitly, with its own re-verification, not this drafting pass.

## Falsifiers

- `git ls-files .ggen/` returns a non-empty result at execution time
  (i.e., the file is already tracked, falsifying this ticket's premise).
- `grep -rn "subsystem_evidence_manifest\.py" justfile
  .github/workflows/*.yml` returns a real invocation at execution time
  (i.e., the generator is already wired in, falsifying this ticket's
  premise).
- `cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets
  --locked` fails when the fixture is absent (would mean this ticket's own
  "currently invisible to `cargo test`" claim is wrong -- re-run and
  correct if so).
- `git diff --stat` after this ticket touches any file outside
  `tickets/GL-EXP-033.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the gap before touching anything:
git ls-files .ggen/
  # expect: no output (nothing tracked)
git check-ignore -v .ggen/v26.8.1/subsystem-evidence-manifest.json
  # expect: .gitignore:17:.ggen/	.ggen/v26.8.1/subsystem-evidence-manifest.json
grep -rn "subsystem_evidence_manifest\.py" justfile .github/workflows/*.yml
  # expect: no output (zero matches)
grep -n "MANIFEST_REL" tools/v26.8.1/src/bin/subsystem_verifier.rs
  # expect: 40:const MANIFEST_REL: &str = ".ggen/v26.8.1/subsystem-evidence-manifest.json";

git diff --stat   # must show only tickets/GL-EXP-033.md
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- `grep -n "MANIFEST_REL" tools/v26.8.1/src/bin/subsystem_verifier.rs`:
  `40:const MANIFEST_REL: &str = ".ggen/v26.8.1/subsystem-evidence-manifest.json";`.
- `git ls-files .ggen/`: zero output (exit 0, empty stdout) -- confirmed
  nothing under `.ggen/` is tracked.
- `git check-ignore -v .ggen/v26.8.1/subsystem-evidence-manifest.json`:
  `.gitignore:17:.ggen/	.ggen/v26.8.1/subsystem-evidence-manifest.json`.
- `grep -rn "subsystem_evidence_manifest\.py" justfile
  .github/workflows/*.yml tools/v26.8.1/src/bin/subsystem_verifier.rs`:
  exactly one hit, a comment inside `subsystem_verifier.rs` noting the
  generator is "architecturally separate" -- no real invocation anywhere.
- Real, reverted experiment this session: moved
  `.ggen/v26.8.1/subsystem-evidence-manifest.json` to a scratch backup
  (`/tmp/gl-exp-ggen-check/.ggen-backup/v26.8.1/subsystem-evidence-manifest.json`),
  ran `cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets
  --locked` with the fixture absent: real output, `13 passed; 0 failed`
  (`document_evidence_sabotage_tests`) and `2 passed; 0 failed`
  (`tests/verifier_boundary.rs`) -- all 15 tests green without the
  fixture, confirming `cargo test` never exercises the default-manifest
  binary path. Restored the file via `cp`; independently confirmed via
  `diff` against the untouched scratch-backup copy that the restored file
  is byte-identical (`diff ... && echo "IDENTICAL"` printed
  `IDENTICAL -- restore confirmed correct`); confirmed
  `python3 -c "hashlib.sha256(...)"` on the restored file:
  `d15ee3d806d71b5275079205b37b931175734e3f5880bb27d75efff237611fbb`;
  `git status --porcelain -- .ggen/` empty before and after, as expected
  for a gitignored path.
- Direct `Read` of `tickets/GL-EXP-031.md` in full this session: its own
  Evidence section states verbatim "against the real, currently-committed
  `.ggen/v26.8.1/subsystem-evidence-manifest.json` fixture" -- the exact
  claim this ticket's `git ls-files` check disproves.
- `grep -l "coverage_projection\|subsystem_verifier" tickets/GL-*.md`:
  confirms `GL-ERRC-015`, `GL-ERRC-016`, `GL-ERRC-019`, `GL-EXP-001`,
  `GL-EXP-005`, `GL-EXP-031` all cite real `cargo build`/`cargo test` runs
  in this same working tree; none of their own text notes the fixture's
  untracked status.
- `cat tickets/GL-EXP-032.md`'s own Outcome section (read this session):
  confirms `tools/v26.8.1` is not currently built or tested by real CI --
  the reason this gap is not yet triggering a live CI failure.
- `grep -n "\.ggen/\|subsystem-evidence-manifest" tickets/OVERLAPS.md`:
  zero matches -- no existing registry entry for either path.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
fixture-provenance gap (a real, reverted experiment confirming `cargo
test` doesn't currently depend on the missing file, and a real `git
ls-files`/`check-ignore` pair confirming the file is genuinely untracked
despite being described as "committed" by `GL-EXP-031`). No `.gitignore`
edit, fixture commit, or generator-wiring has been made; which resolution
to choose is left to a future session or the repo owner.
