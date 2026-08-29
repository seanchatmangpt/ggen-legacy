# GL-EXP-031 — Raise `subsystem_verifier.rs`'s self-certification check to actually verify `content_sha256`

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.1/src/bin/subsystem_verifier.rs`'s own module doc comment
(lines 1-27) states this binary's entire reason for existing is that it
"treats every field of the manifest as a CLAIM, never as ground truth,"
and names four specific fields it independently re-derives from disk/git/
subprocess rather than trusting: file digests, `exact_source_head`, test
results, and legacy disposition. `verifier_identity.content_sha256` is a
fifth manifest-claimed field with exactly the same shape -- a hash the
generator (`subsystem_evidence_manifest.py`) computes over its own source
file and writes into the manifest -- but it is the one field this binary
never independently re-checks. Confirmed this session by reading the
committed `HEAD` copy of the file
(`git show HEAD:tools/v26.8.1/src/bin/subsystem_verifier.rs`, 643 lines):

```rust
#[derive(Debug, Deserialize)]
struct VerifierIdentity {
    path: String,
    #[allow(dead_code)]
    content_sha256: String,
    role: String,
}
```

(lines 58-63, `#[allow(dead_code)]` on `content_sha256` at line 60 --
already an admission in the source that the field is unused). The
self-certification check itself, at lines 430-441:

```rust
// Refuse if the manifest's declared generator identity is this very
// verifier binary (same source path) or claims to already be the
// verifier -- a component cannot certify itself.
let self_cert_ok = manifest.verifier_identity.path != THIS_BINARY_SOURCE_REL
    && manifest.verifier_identity.role == "manifest-generator";
if !self_cert_ok {
    bail!(
        "SELF_CERTIFICATION_REFUSED: manifest verifier_identity ({}, role={}) must not be this verifier binary itself",
        manifest.verifier_identity.path,
        manifest.verifier_identity.role
    );
}
```

compares only `path` and `role`. `grep -n content_sha256
tools/v26.8.1/src/bin/subsystem_verifier.rs` against the committed `HEAD`
copy returns exactly one hit, the struct-field declaration at line 61 --
the field is deserialized and then never read again anywhere in the file:
never hashed against, never compared, never passed to any function. The
already-imported `sha2::{Digest, Sha256}` (line 31, used elsewhere in the
file at line ~165 to hash subsystem authority-source files) is never
applied to `verifier_identity.path`'s real on-disk bytes.

This is not a theoretical gap -- verified this session with a real,
adversarial run of the actual compiled binary. The committed fixture
`.ggen/v26.8.1/subsystem-evidence-manifest.json` currently has an honest
`verifier_identity` (`path: tools/v26.8.1/subsystem_evidence_manifest.py`,
`content_sha256: d3738be8...4087bc`, `role: manifest-generator`), and this
session independently confirmed
`hashlib.sha256(open('tools/v26.8.1/subsystem_evidence_manifest.py','rb').read()).hexdigest()`
matches that value exactly today. I then copied the fixture, overwrote
only `content_sha256` with a fabricated value (`"deadbeef" * 8`, leaving
the real `path` and `role` untouched), and ran the real compiled
`subsystem_verifier` binary against the corrupted copy:

```
$ ./tools/v26.8.1/target/debug/subsystem_verifier --root . \
    --manifest /tmp/.../corrupted-manifest.json --observe-only --no-cache
governance     standing=UNKNOWN
system         standing=UNKNOWN
...
legacy         standing=ALIVE
report=/Users/sac/ggen-legacy/.ggen/v26.8.1/subsystem-verifier-report.json
$ echo $?
0
```

The binary did not bail with `SELF_CERTIFICATION_REFUSED` (or any other
error) and ran to completion, exit code `0`, producing a full report. The
written report's own `self_cert_check_passed` field reads `true`
(`python3 -c "import json;print(json.load(open('.ggen/v26.8.1/subsystem-verifier-report.json'))['self_cert_check_passed'])"`
-- real output this session: `True`). A manifest whose
`verifier_identity.content_sha256` is stale (copied forward after
`subsystem_evidence_manifest.py` was edited) or outright fabricated passes
identically to a manifest from a genuinely-unmodified generator -- exactly
the self-certification gap this file's own docstring exists to close.

The blast radius is larger than a single run: `self_cert_check_passed` is
itself persisted into the on-disk report (`VerifierReport.self_cert_check_passed`,
struct field at line 141, set from `self_cert_ok` at line 626) and is one
of the five conditions `load_cache_hit()` checks (line 227-238) before
letting a *later* invocation skip re-verification entirely (line 232:
`&& cached.self_cert_check_passed`). Because the field is always `true`
whenever `path`/`role` pass (regardless of `content_sha256`), a single run
against a manifest with a fabricated hash produces a cached "passed"
report that a subsequent invocation (without `--no-cache`) would accept
without re-running any checks at all.

Searched all 51 tickets for existing coverage: `grep -il
"content_sha256\|self_cert_ok" tickets/GL-*.md` returns zero matches. This
is a distinct defect class from the two other admitted tickets already
touching this same file (`GL-EXP-001`, `resolve_root()` duplication, lines
375-391 of `HEAD`, `EXECUTED`; `GL-EXP-005`, `fresh_git_head()`
duplication, lines 242-251 of `HEAD`, `NOT_STARTED`) -- both of those are
code-duplication findings in unrelated functions; this is an
unverified-claim gap in the self-certification check itself, disjoint line
ranges from both (58-63, 430-441, 141, 232, 626 vs. 233-248/375-391 and
242-251/428-443).

## Authored boundary

(Cross-ticket file overlaps are tracked in `tickets/OVERLAPS.md` -- see the
disclosed row added there as part of this same ticket. `GL-EXP-001` and
`GL-EXP-005` both already claim other, disjoint parts of this same file;
this ticket's target -- the `VerifierIdentity` struct, the `self_cert_ok`
check, `VerifierReport.self_cert_check_passed`, and `load_cache_hit()`'s
use of it -- does not overlap either of their named line ranges, but all
three should not be executed concurrently without re-checking line numbers
against whichever lands first.)

```text
tools/v26.8.1/src/bin/subsystem_verifier.rs   # add real content_sha256 re-hash + comparison to the self-certification check
tickets/GL-EXP-031.md
tickets/OVERLAPS.md                            # disclosed-overlap row only
```

No change to `tools/v26.8.1/subsystem_evidence_manifest.py` (the generator
already computes and writes a correct `content_sha256` -- confirmed this
session at line 498, `"content_sha256": sha256_file(generator_path)` --
this ticket closes the verifier-side gap only, not a generator-side bug).
No change to `tools/v26.8.1/src/coverage_projection.rs`. No change to
`.ggen/v26.8.1/subsystem-evidence-manifest.json` (the real, honest,
currently-committed fixture is not touched; a corrupted copy used for
adversarial testing lives only in a scratch temp directory, never
committed).

## Hard laws

1. `subsystem_verifier.rs` must independently re-hash the real file at
   `root.join(&manifest.verifier_identity.path)` with the already-imported
   `Sha256` (matching the hashing style already used in this same file for
   subsystem authority-source digests) and compare the resulting hex
   digest against `manifest.verifier_identity.content_sha256`, folding the
   result into the self-certification decision (i.e. `self_cert_ok` must
   become `false`, and the check must `bail!`, whenever the digests
   disagree, in addition to the existing `path`/`role` checks).
2. The `#[allow(dead_code)]` attribute on `VerifierIdentity::content_sha256`
   (line 60 of the current `HEAD`) is removed, because the field becomes
   genuinely read.
3. A missing or unreadable file at `verifier_identity.path` (e.g. the
   generator script was deleted or the path is wrong) must also cause
   self-certification to fail closed with a clear, distinguishable error
   -- not panic, not silently treat as a hash match.
4. The existing `path != THIS_BINARY_SOURCE_REL && role ==
   "manifest-generator"` checks are preserved unchanged as a precondition
   -- this ticket adds a check, it does not relax or remove either
   existing one.
5. `VerifierReport.self_cert_check_passed` (and therefore
   `load_cache_hit()`'s cache-validity condition at line 232) must reflect
   the combined result (identity fields AND hash match), not just the old
   two-field check, so a cached "passed" report can no longer exist for a
   manifest whose `content_sha256` never matched the real file.
6. Both existing tests in `tools/v26.8.1/tests/verifier_boundary.rs`
   (`all_three_binaries_fail_closed_on_missing_root` and
   `all_three_binaries_get_past_root_resolution_with_real_agents_md`) must
   still pass unmodified, proving the crate still builds and the binary's
   externally observable root-resolution behavior is undisturbed.
7. The real, currently-committed `.ggen/v26.8.1/subsystem-evidence-manifest.json`
   fixture (whose `content_sha256` genuinely matches
   `tools/v26.8.1/subsystem_evidence_manifest.py` today) must still pass
   self-certification after the fix -- this ticket must not turn a
   currently-honest manifest into a false refusal.

## Falsifiers

- `grep -n "content_sha256" tools/v26.8.1/src/bin/subsystem_verifier.rs`
  still shows only the struct-field declaration after this ticket executes
  (field still never read).
- `grep -n "allow(dead_code)]" tools/v26.8.1/src/bin/subsystem_verifier.rs
  | grep -B1 content_sha256`-equivalent check still shows the attribute
  present above `content_sha256` (proves the field was never actually
  wired in).
- The adversarial repro from this ticket's Outcome section -- copy the
  real fixture, overwrite only `content_sha256` with a fabricated value,
  run the real compiled binary with `--manifest <corrupted copy>
  --observe-only --no-cache` -- still exits `0` / does not bail with a
  hash-mismatch error after the fix lands.
- The real, unmodified `.ggen/v26.8.1/subsystem-evidence-manifest.json`
  fixture starts failing self-certification after the fix (false
  positive introduced).
- `cargo test --manifest-path tools/v26.8.1/Cargo.toml --test
  verifier_boundary --locked` fails or changes its passing count from the
  current `2 passed; 0 failed`.
- `cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked` fails to
  compile.
- `git diff --stat` after this ticket touches any file outside
  `tools/v26.8.1/src/bin/subsystem_verifier.rs`, `tickets/GL-EXP-031.md`,
  and the disclosed row added to `tickets/OVERLAPS.md`.

**Not yet checked against a real fix (ticket is `NOT_STARTED`) -- these are
the exact commands to run once the fix lands, not yet-observed outcomes.**

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the gap before touching anything:
grep -n "content_sha256" tools/v26.8.1/src/bin/subsystem_verifier.rs
cargo build --manifest-path tools/v26.8.1/Cargo.toml --bin subsystem_verifier --locked
python3 -c "
import json, shutil
d = json.load(open('.ggen/v26.8.1/subsystem-evidence-manifest.json'))
d['verifier_identity']['content_sha256'] = 'deadbeef' * 8
json.dump(d, open('/tmp/gl-exp-031-corrupted-manifest.json', 'w'))
"
./tools/v26.8.1/target/debug/subsystem_verifier --root . \
  --manifest /tmp/gl-exp-031-corrupted-manifest.json --observe-only --no-cache
echo "exit before fix (expect 0 -- proves the gap): $?"

# After the fix, the same corrupted manifest must be refused:
cargo build --manifest-path tools/v26.8.1/Cargo.toml --bin subsystem_verifier --locked
./tools/v26.8.1/target/debug/subsystem_verifier --root . \
  --manifest /tmp/gl-exp-031-corrupted-manifest.json --observe-only --no-cache
echo "exit after fix (expect nonzero -- proves the fix): $?"

# The real, honest fixture must still pass:
./tools/v26.8.1/target/debug/subsystem_verifier --root . --observe-only --no-cache
echo "exit for real fixture after fix (expect 0): $?"

# Confirm the crate still builds and the black-box regression tests still pass:
cargo build --manifest-path tools/v26.8.1/Cargo.toml --locked
cargo test --manifest-path tools/v26.8.1/Cargo.toml --test verifier_boundary --locked

rm -f /tmp/gl-exp-031-corrupted-manifest.json
git diff --stat   # must show only subsystem_verifier.rs + tickets/GL-EXP-031.md + OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `git show HEAD:tools/v26.8.1/src/bin/subsystem_verifier.rs` (643 lines,
  saved to a scratch file this session) -- confirms `VerifierIdentity`
  struct at lines 58-63 with `content_sha256` at line 61 and
  `#[allow(dead_code)]` at line 60; `self_cert_ok` check at lines 430-441;
  `VerifierReport.self_cert_check_passed: bool` field declared at line
  141; `load_cache_hit()`'s use of `cached.self_cert_check_passed` at line
  232; report construction `self_cert_check_passed: self_cert_ok` at line
  626.
- `grep -n content_sha256
  <scratch-copy-of-HEAD:tools/v26.8.1/src/bin/subsystem_verifier.rs>` --
  real output this session: exactly one match (line 61, the struct-field
  declaration) -- confirms the field is never read anywhere else in the
  file.
- `python3 -c "import hashlib; print(hashlib.sha256(open('tools/v26.8.1/subsystem_evidence_manifest.py','rb').read()).hexdigest())"`
  -- real output this session:
  `d3738be844f93aa2bc9c1dbf26e753fc50fcf56c87dc395148b58922544087bc`,
  matching `.ggen/v26.8.1/subsystem-evidence-manifest.json`'s committed
  `verifier_identity.content_sha256` exactly (confirmed by direct
  `python3 -c "import json;print(json.load(open('.ggen/v26.8.1/subsystem-evidence-manifest.json'))['verifier_identity'])"`).
- Real adversarial run this session:
  `cargo build --manifest-path tools/v26.8.1/Cargo.toml --bin
  subsystem_verifier --locked` (succeeds), then a corrupted copy of the
  real manifest fixture with `content_sha256` overwritten to
  `"deadbeef"*8` (real `path`/`role` untouched) fed to the real compiled
  binary via `./tools/v26.8.1/target/debug/subsystem_verifier --root . \
  --manifest <corrupted copy> --observe-only --no-cache` -- real output
  this session: the binary ran to completion (`legacy standing=ALIVE`,
  `report=.../subsystem-verifier-report.json`), exit code `0`, no
  `SELF_CERTIFICATION_REFUSED` or any other bail. The written report's own
  `self_cert_check_passed` field, read back via
  `python3 -c "import json;print(json.load(open('.ggen/v26.8.1/subsystem-verifier-report.json'))['self_cert_check_passed'])"`,
  is `True`.
- `cargo test --manifest-path tools/v26.8.1/Cargo.toml --test
  verifier_boundary --locked` -- real output this session:
  `test result: ok. 2 passed; 0 failed`, establishing the current baseline
  this ticket's Hard Law 6 must preserve.
- `grep -il "content_sha256\|self_cert_ok" tickets/GL-*.md` -- real output
  this session: zero matches across all 51 tickets; no existing ticket
  covers this gap.
- `cat tickets/GL-EXP-001.md` and `cat tickets/GL-EXP-005.md` -- confirm
  both already claim disjoint parts of this same file
  (`resolve_root`/`fresh_git_head`, unrelated functions and line ranges,
  neither touching `VerifierIdentity`, `self_cert_ok`, or
  `content_sha256`); `GL-EXP-001`'s own on-disk Status is `EXECUTED`
  (fix already landed, currently uncommitted in this working tree per
  `git diff -- tools/v26.8.1/src/bin/subsystem_verifier.rs`, which shows
  only the `resolve_root` deletion/import-swap -- confirmed this session
  that this dirty change is unrelated to and does not touch the
  self-certification region cited above).
- `sed -n '498p' tools/v26.8.1/subsystem_evidence_manifest.py` -- real
  output this session: `"content_sha256": sha256_file(generator_path),`,
  confirming the generator side already computes this field correctly;
  the gap is verifier-side only.
- `git rev-parse HEAD` -- `bce7f6386c4203784beaae426e40804636c4151a`, the
  same base commit as `GL-EXP-001`/`GL-EXP-005`, confirming all three
  tickets are drafted against comparable working-tree state (this
  ticket's own line citations are taken from the committed `HEAD` copy via
  `git show`, not the currently-dirty working tree, so they remain valid
  regardless of `GL-EXP-001`'s uncommitted in-flight fix).

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
unverified-claim finding (including a real adversarial exploit of the
current gap); the actual re-hash-and-compare fix in
`subsystem_verifier.rs` has not been made.
