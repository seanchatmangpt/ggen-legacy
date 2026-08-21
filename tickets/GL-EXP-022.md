# GL-EXP-022 — Reduce `ggen-verifier-cli-verify`'s remaining hardcoded `/Users/sac/ggen/...` absolute path (`ggen.toml`/`ggen.lock`)

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/ggen-verifier-cli-verify/ggen.toml`'s `[packs]` table pins its sole
pack dependency to a machine-local absolute path:

```toml
[packs]
chicago-tdd-tools-pack = { path = "/Users/sac/ggen/packs/chicago-tdd-tools-pack" }
```

and the committed, `ggen sync`-generated `ggen.lock` (read directly this
session, in full -- 5 lines) records the identical absolute source and a
`content_hash`:

```
[packs.chicago-tdd-tools-pack]
source = "path:/Users/sac/ggen/packs/chicago-tdd-tools-pack"
content_hash = "blake3:7af70669e92ae05a5d8eb217fbe059464a536f90284b89163b8edd6b239f539c"
```

This is the same class of defect `GL-EXP-002` (`EXECUTED`, `ALIVE`) already
fixed once in this exact crate -- a version-controlled manifest hardcoding
`/Users/sac/ggen/...`, unresolvable on any machine other than the one that
happens to have `~/ggen` checked out at that exact path -- but for a
second, independent manifest pair `GL-EXP-002`'s own Authored boundary
explicitly excludes. `GL-EXP-002.md` (read in full this session) states
verbatim: "No change to `tools/ggen-verifier-cli-verify/src/`, `tests/`,
`schema/domain.ttl`, `ggen.toml`, or `ggen.lock` -- this ticket repairs the
dependency declaration only" (referring to `Cargo.toml`/`Cargo.lock`'s own
`chicago-tdd-tools` dev-dependency, already relocked to the published
crates.io form per `GL-EXP-002`'s Standing section). `ggen.toml`/
`ggen.lock`'s own, separate pin into the sibling repo was left untouched
by design, and remains machine-local today.

**Confirmed this session: unlike the `Cargo.toml` case `GL-EXP-002` fixed,
this path currently resolves on this machine** --
`ls -la /Users/sac/ggen/packs/chicago-tdd-tools-pack` succeeds (a real
directory: `gates/`, `ontology.ttl`, `pack.toml`, `templates/`) -- so this
is not a currently-broken build the way the deleted
`crates/chicago-tdd-tools` path was. The defect is portability, not an
active failure: any developer, CI runner, or future session without
`~/ggen` checked out at exactly `/Users/sac/ggen` cannot run `ggen sync`
against this crate at all.

**This crate's own repo already establishes the portable convention this
manifest violates.** Confirmed by direct read this session, this repo's
*other* two `ggen.toml` files use repository-relative paths for their own
`[packs]` dependencies, not absolute ones:

- Root `ggen.toml`: `ggen-legacy-assurance-pack = { path =
  "packs/ggen-legacy-assurance-pack" }` -- a relative path to a pack
  vendored inside this same repo.
- `packs/legacy-equivalence-verifier-pack/ggen.toml` declares no `[packs]`
  section at all (it has no external pack dependency).

`tools/ggen-verifier-cli-verify/ggen.toml` is the sole `ggen.toml` in this
repo with an absolute, single-machine path.

**This is not dead configuration -- it is the one real, live path that
exercises this crate's cross-repo sync, confirmed this session.**
`scripts/ci/guard-verifier-proof.sh` (read in full this session, 3777
bytes) is the script whose own comment states it "re-syncs
tools/ggen-verifier-cli-verify (a real, cross-repo consumer of the
separate `~/ggen` repo's chicago-tdd-tools-pack)". Per
`governance/production-gaps.md`'s own "What an engineering pass can close"
section (read in full this session), that script was already fixed once
this milestone: it "silently assumed a single-machine absolute path
(`GGEN_REPO=/Users/sac/ggen`) -- now requires the env var explicitly and
fails loudly with setup instructions if unset." **That fix does not
actually make the sync portable**, confirmed by direct read of
`scripts/ci/guard-verifier-proof.sh` this session: the script builds
`CONSUMER="$REPO_ROOT/tools/ggen-verifier-cli-verify"` and (per its own
comment) invokes a real `ggen sync` against that consumer, but `ggen sync`
itself reads the pack source from `ggen.toml`'s `[packs]` table -- which
is not parameterized by `$GGEN_REPO` at all. Setting
`GGEN_REPO=/some/other/checkout` and running the (already-fixed) guard
script would still attempt to read
`path:/Users/sac/ggen/packs/chicago-tdd-tools-pack` literally, because
that string is baked into the committed manifest, not derived from the
environment. `governance/production-gaps.md`'s own prose attributes this
script's non-portability entirely to `guard-verifier-proof.sh`'s own
missing env-var check (now fixed) and does not name `ggen.toml`/
`ggen.lock`'s independent, still-hardcoded path as a second, additional
cause -- this ticket names that second cause.

**No existing ticket covers this.** `grep -l "ggen.toml\|ggen.lock"
tickets/GL-*.md` (run this session) returns `GL-CONTRACT-004.md`,
`GL-AUTO-001.md`, `GL-ERRC-018.md`, `GL-EXP-002.md`; direct inspection of
each: `GL-CONTRACT-004.md`'s hit is an unrelated string literal inside a
pilot `ggen:precondition` value ("Template + context data available
(ggen.toml + .specify/*.ttl loaded)"); `GL-ERRC-018.md`'s two hits are both
substring matches inside the unrelated CATALOG slug
`legacy_ggen_toml_dual_schema`; `GL-AUTO-001.md`'s hit is one bare filename
among 115 inside its `REFUSED:FORBIDDEN_DIFF:...` dump (same non-substantive
pattern already established elsewhere in this corpus); `GL-EXP-002.md`
names both files only to explicitly exclude them from its own scope, as
quoted above.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below. Confirmed
this session via `grep -n "ggen.toml\|ggen.lock" tickets/OVERLAPS.md`: no
existing entry for either path.)

```text
tools/ggen-verifier-cli-verify/ggen.toml   # [packs] table's chicago-tdd-tools-pack source only
tools/ggen-verifier-cli-verify/ggen.lock   # relocked to match, regenerated by a real `ggen sync`
tickets/GL-EXP-022.md
```

No change to `tools/ggen-verifier-cli-verify/Cargo.toml`/`Cargo.lock`
(already fixed by `GL-EXP-002`, `EXECUTED`), `src/`, `tests/`,
`schema/domain.ttl`, `templates/`, `docs/chicago_tdd_tools_boundary.md`, or
`scripts/ci/guard-verifier-proof.sh`'s own `$GGEN_REPO` handling (already
fixed per `governance/production-gaps.md`) -- this ticket touches only the
pack-dependency source declaration and its generated lockfile.

## Hard laws

1. The resolution is one of two, named explicitly here (this ticket does
   not silently pick a default): (a) **vendor** the pack into this repo
   (mirroring the root `ggen.toml`'s own precedent --
   `packs/ggen-legacy-assurance-pack` is vendored in-repo at a relative
   path) and re-point `ggen.toml` at a repo-relative `path = "packs/..."`;
   or (b) if `chicago-tdd-tools-pack` is meant to keep tracking the
   sibling `ggen` repo's evolving pack rather than a frozen vendored copy,
   parameterize the source via an environment variable (e.g.
   `${GGEN_REPO}/packs/chicago-tdd-tools-pack`) consistent with
   `guard-verifier-proof.sh`'s own already-established `$GGEN_REPO`
   convention, if and only if `ggen`'s own manifest format supports
   environment-variable interpolation in `[packs]` path values (verify
   this against the real `ggen` CLI's documented `ggen.toml` schema before
   choosing this branch -- do not assume support and silently produce a
   manifest `ggen sync` cannot parse).
2. Whichever resolution is chosen, a real `ggen sync` (or equivalent
   `guard-verifier-proof.sh` invocation with `$GGEN_REPO` set) must
   succeed against the new manifest and regenerate `ggen.lock` for real --
   this ticket does not hand-edit `ggen.lock`'s `content_hash` field.
3. No new dependency, generation rule, or template is introduced --
   this is a source-of-truth-path fix only, not a redesign of what this
   crate's `ggen.toml` generates.
4. `git diff --stat` after this ticket touches only
   `tools/ggen-verifier-cli-verify/ggen.toml`,
   `tools/ggen-verifier-cli-verify/ggen.lock`, and this ticket file.

## Falsifiers

- After the fix, `grep -n "/Users/sac" tools/ggen-verifier-cli-verify/ggen.toml
  tools/ggen-verifier-cli-verify/ggen.lock` still matches (the hardcoded
  absolute path was not actually removed).
- The chosen resolution's own `ggen sync` (or equivalent) does not
  actually succeed for real when re-run -- e.g. a vendored copy that was
  never actually created on disk at the new relative path, or an
  env-var-interpolated form `ggen`'s real CLI cannot parse.
- `ggen.lock`'s `content_hash` is edited by hand rather than regenerated
  by a real sync run (Hard Law 2).
- `git diff --stat` shows any file changed other than the two named
  manifests and this ticket file.
- `scripts/ci/guard-verifier-proof.sh`'s own `$GGEN_REPO` requirement or
  error-message text is modified by this ticket (that fix already landed
  per `governance/production-gaps.md`; this ticket's scope is the
  manifest files only).

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Reconfirm the hardcoded path before touching anything:
grep -n "packs\]\|chicago-tdd-tools-pack\|/Users/sac" \
  tools/ggen-verifier-cli-verify/ggen.toml tools/ggen-verifier-cli-verify/ggen.lock

# Confirm the other 2 ggen.toml files in this repo use a portable form:
grep -A2 '\[packs\]' ggen.toml
grep -c '\[packs\]' packs/legacy-equivalence-verifier-pack/ggen.toml   # expect 0

# After choosing and applying a resolution (Hard Law 1), regenerate the
# lockfile with a real sync and confirm the absolute path is gone:
grep -n "/Users/sac" tools/ggen-verifier-cli-verify/ggen.toml tools/ggen-verifier-cli-verify/ggen.lock
  # expect: no match

# Confirm the crate's own tests still pass unaffected (this ticket does
# not touch generated source, only the manifest driving generation):
cargo clippy --manifest-path tools/ggen-verifier-cli-verify/Cargo.toml --all-targets -- -D warnings

git diff --stat   # must show only the two manifests and tickets/GL-EXP-022.md
```

## Evidence this ticket is grounded in (verified this session)

- Direct `Read` of `tools/ggen-verifier-cli-verify/ggen.toml` this session
  -- confirms `[packs] chicago-tdd-tools-pack = { path =
  "/Users/sac/ggen/packs/chicago-tdd-tools-pack" }` verbatim.
- Direct `Read` of `tools/ggen-verifier-cli-verify/ggen.lock` this session
  (full file, 5 lines) -- confirms `source = "path:/Users/sac/ggen/packs/
  chicago-tdd-tools-pack"` and a `content_hash` value, matching the
  manifest above.
- `ls -la /Users/sac/ggen/packs/chicago-tdd-tools-pack` this session --
  real output: a real, existing directory (`gates/`, `ontology.ttl`,
  `pack.toml`, `templates/`) -- confirming the path currently resolves on
  this machine (unlike `GL-EXP-002`'s deleted-crate finding), so the
  defect is portability, not an active local build failure.
- Direct `Read` of `tickets/GL-EXP-002.md` in full this session -- its
  Authored boundary states verbatim: "No change to
  `tools/ggen-verifier-cli-verify/src/`, `tests/`, `schema/domain.ttl`,
  `ggen.toml`, or `ggen.lock` -- this ticket repairs the dependency
  declaration only", scoping that ticket exclusively to `Cargo.toml`/
  `Cargo.lock`.
- Direct `Read` of the root `ggen.toml` this session -- confirms
  `ggen-legacy-assurance-pack = { path = "packs/ggen-legacy-assurance-pack" }`,
  a repository-relative path to a pack vendored in this same repo, as the
  established local counter-example. Direct `Read` of
  `packs/legacy-equivalence-verifier-pack/ggen.toml` this session --
  confirms it declares no `[packs]` section at all.
- `find . -name "ggen.toml"` (excluding `.claude/worktrees/`) this
  session -- confirms exactly 3 `ggen.toml` files in the repo: the root
  one, `packs/legacy-equivalence-verifier-pack/ggen.toml`, and
  `tools/ggen-verifier-cli-verify/ggen.toml` -- the last is the sole one
  with an absolute, single-machine path.
- Direct `Read` of `scripts/ci/guard-verifier-proof.sh` in full this
  session (3777 bytes) -- confirms its comment describing itself as
  re-syncing `tools/ggen-verifier-cli-verify` against the sibling
  `chicago-tdd-tools-pack`, its `$GGEN_REPO` requirement (fails loudly
  with setup instructions if unset, per its own `if [[ -z
  "${GGEN_REPO:-}" ]]` check), and its `CONSUMER="$REPO_ROOT/
  tools/ggen-verifier-cli-verify"` variable -- confirming this is the one
  real, live path that exercises `ggen.toml`'s pack dependency, and that
  its `$GGEN_REPO` env var is never threaded into `ggen.toml`'s own
  `[packs]` table (which is a static, committed file, not templated at
  sync time).
- Direct `Read` of `governance/production-gaps.md` this session --
  confirms its "What an engineering pass can close" section attributes
  `guard-verifier-proof.sh`'s prior non-portability solely to the missing
  `$GGEN_REPO` check (now fixed), and its "What remains ... out of this
  pass's scope" section separately names `guard-verifier-proof.sh`'s
  continued reliance on "a sibling `~/ggen` checkout at a path only
  meaningful on this machine" as a known, deferred item -- but neither
  section names `ggen.toml`/`ggen.lock`'s own independently-hardcoded
  path as a distinct cause that survives the `$GGEN_REPO` fix.
- `grep -l "ggen.toml\|ggen.lock" tickets/GL-*.md` this session -- real
  output: `GL-CONTRACT-004.md`, `GL-AUTO-001.md`, `GL-ERRC-018.md`,
  `GL-EXP-002.md`. Per-file `grep -n` on each (this session) confirms
  three are unrelated substring matches (a prose string literal, and two
  hits inside the CATALOG slug `legacy_ggen_toml_dual_schema`) and the
  fourth (`GL-EXP-002.md`) explicitly excludes these two files from its
  own scope, as quoted in Outcome above.
- `grep -n "ggen.toml\|ggen.lock" tickets/OVERLAPS.md` this session --
  zero matches, no existing overlap-registry entry for either path.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
remaining-absolute-path finding and names the two candidate resolutions
(vendor vs. env-var-parameterize); which one is correct depends on whether
`ggen`'s own manifest format supports path interpolation (Hard Law 1) and
is left to implementation, not decided here. No manifest edit or `ggen
sync` re-run has been performed.
