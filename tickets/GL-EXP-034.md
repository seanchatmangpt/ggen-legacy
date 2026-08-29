# GL-EXP-034 — Reduce `authority/ggen-create-receiving-contract.json`'s stale producer commit pin to a real re-verification decision

**Status:** admitted, `NOT_STARTED` -- drafted by standing ultracode exploration cron
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE` (decision/doc-level only -- no re-pin performed by this drafting pass)
**Publication:** draft pull request; no merge authority

## Outcome

`authority/ggen-create-receiving-contract.json:5` pins the producer side of
this repo's ggen-create bundle-receiving pipeline to:

```json
"commit": "8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4",
"version": "0.4.0"
```

I re-checked this against the real, local `~/ggen-create` sibling checkout
this session: `git -C ~/ggen-create log -1 --format='%H %ci'` reports the
real, current HEAD is `09a197ba32369bcec632dcc9b7919e633a6e08fb`, dated
`2026-08-18 22:16:05` -- a real commit,
`09a197b fix: prevent gc:subject IRI collisions across generators, add
--merge`. `git -C ~/ggen-create cat-file -t 8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4`
confirms the pinned commit is a real, reachable object (dated
`2026-08-07 13:39:23`), and `git -C ~/ggen-create merge-base --is-ancestor
8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4 09a197ba32369bcec632dcc9b7919e633a6e08fb`
exits `0` (true) -- this is ordinary forward drift, not a rewrite or
force-push. `git -C ~/ggen-create rev-list --count
8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4..09a197ba32369bcec632dcc9b7919e633a6e08fb`
reports **29** real commits between the pinned producer revision and the
sibling repo's real current HEAD -- roughly 11 days of ordinary upstream
movement in `seanchatmangpt/ggen-create`.

This is the exact same class of finding `GL-ERRC-020` already converted
into a trackable ticket for `authority/foundry-work-program.json`/
`foundry/bootstrap.yaml`, and that `GL-EXP-010` already converted into a
trackable ticket for
`migrations/ggen-v26.8.1/migration-manifest.json`'s `source_head` pin --
both real, reproducible, currently-live discrepancies between a checked-in
pin and the actual state of the repo it references, named and turned into
a decision rather than silently ignored or silently re-pinned. This
ticket applies the identical, already-precedented pattern to a third,
materially different subsystem: the cross-repo **ggen-create bundle
receiver** (the PR #19 pipeline `governance/production-gaps.md`'s own
"What remains -- and is code-shaped, but out of this pass's scope" section
already names as carrying a stale producer pin, without turning it into a
trackable ticket). Read in full this session, that section states
verbatim: "the producer pin (`ggen-create` commit `a0a9133`, v0.4.0) is
stale against `ggen-create`'s current main (v26.8.6) -- closing this means
re-pinning to a current commit once both branches merge, not a gap in this
repo alone." (Note: that document's own cited short-hash, `a0a9133`, does
not match the full pin actually stored in
`authority/ggen-create-receiving-contract.json`, `8a092c13...` -- both are
real, reachable git objects in `~/ggen-create`, per `git cat-file -t`
checked this session, but they are two different commits; this ticket
re-verifies against the real, current on-disk pin,
`8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4`, not the narrative document's
possibly-stale-itself short-hash citation.)

`grep -il "ggen-create" tickets/GL-*.md` (re-run this session, all 59
tickets currently on disk) matches only `GL-AUTO-001.md` and
`GL-EXP-006.md` as real, pre-existing hits (this ticket's own file,
`GL-EXP-034.md`, trivially self-matches once written and is excluded);
per-file inspection this session confirms both are incidental
(`GL-AUTO-001.md`'s hit is a bare filename inside its
`REFUSED:FORBIDDEN_DIFF:` dump, not its Authored boundary --
independently re-checked this session: that ticket's actual Authored
boundary section lists only `autonomic/`-scoped files, none of them this
authority file; `GL-EXP-006.md`'s hit is unrelated context). Two other
tickets, `GL-ERRC-011.md` and `GL-EXP-028.md`, name the *script*
`verify_ggen_create_bundle.py` (underscore-separated, not the hyphenated
`ggen-create` string this authority file's path uses) as one of several
scripts audited for unrelated properties (missing `EXPECTED_*` constants,
respectively a naming-convention sweep) -- re-checked this session with
`grep -ni "ggen-create" tickets/GL-ERRC-011.md tickets/GL-EXP-028.md`,
which returns zero matches for the literal hyphenated string in either
file, so they are not actually hits for this grep pattern. None of the
tickets found proposes re-verifying or re-pinning
`authority/ggen-create-receiving-contract.json`'s own producer commit. `verify_ggen_create_bundle.py`'s own `checks` dict
(read in full this session) cross-validates internal self-consistency
between `manifest.json`/`receiving-contract.json`/`receipt.json`/this
authority file -- it does not compare the pinned `producer.commit` against
the real, current state of a `~/ggen-create` checkout the way
`verify_ggen_v26_8_1_migration.py` does for the `tools/v26.8.1` migration
pin (`GL-EXP-010`'s subject) -- so this specific staleness is invisible to
that script too, not just to human review.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- checked this session, `grep -n "ggen-create-receiving-contract"
tickets/OVERLAPS.md` returns zero matches, no existing entry.)

```text
authority/ggen-create-receiving-contract.json   # producer.commit / producer.version fields only
tickets/GL-EXP-034.md
```

No change to `scripts/verify_ggen_create_bundle.py`,
`tests/test_ggen_create_receiver.py`, `tests/fixtures/ggen_create_fortune5.json`,
or any file under `docs/case-studies/`. No change to the `receiver` block
(`base_commit`) or `provided_workstreams`/`receiver_owned_workstreams`
fields -- this ticket is scoped to the producer identity pin only.

## Hard laws

1. This ticket may update `authority/ggen-create-receiving-contract.json`'s
   `producer.commit`/`producer.version` fields to a current, real value
   **only if** that re-verification is re-run at execution time
   (`git -C <real ggen-create checkout> rev-parse HEAD`, or equivalent)
   and its real output is quoted in this ticket's evidence -- never carry
   forward this drafting session's `09a197ba32369bcec632dcc9b7919e633a6e08fb`
   as sufficient at execution time, since the sibling repo will have moved
   further by then.
2. If re-pinning, `scripts/verify_ggen_create_bundle.py` must be re-run
   against a real bundle produced from the new pin and its real pass/fail
   output quoted -- a manifest whose `producer.commit` matches but whose
   `producer_identity`/schema-binding checks then fail is not an
   acceptable silent resolution; that discrepancy must be recorded and
   left for a human, not silently patched.
3. Alternatively, this ticket may resolve the decision by explicitly
   documenting the pin as a deliberately frozen point-in-time receipt
   (matching `GL-EXP-010`'s own Hard Law 3 precedent) rather than
   re-pinning -- but only one of the two resolutions (re-pin-and-reverify,
   or explicitly-frozen-receipt) may be chosen, and the choice must be
   stated in this ticket's evidence, not left implicit.
4. This ticket must not add any new CI wiring and must not modify
   `scripts/verify_ggen_create_bundle.py`'s own logic.
5. `git diff --stat` after this ticket touches only
   `authority/ggen-create-receiving-contract.json` and
   `tickets/GL-EXP-034.md` (or, under Hard Law 3's frozen-receipt
   resolution, only a companion note plus `tickets/GL-EXP-034.md`, with
   the JSON file left untouched).

## Falsifiers

- `producer.commit` is changed without a fresh, quoted `git rev-parse
  HEAD` (or equivalent) re-verification run against the real sibling
  repo at execution time.
- `producer.commit` is re-pinned but `verify_ggen_create_bundle.py` is not
  re-run against a bundle from the new pin, or its real output is not
  quoted.
- Both resolutions (re-pin-and-reverify vs. explicitly-frozen-receipt) are
  attempted at once, or neither is.
- Any file outside the authored boundary above is modified, including
  `scripts/verify_ggen_create_bundle.py` or any test fixture.
- A second passing mention of this exact staleness (beyond
  `governance/production-gaps.md`'s existing one) is added anywhere in the
  repo instead of this ticket being executed or explicitly rejected by the
  repo owner.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the stale pin before touching anything:
grep -n '"commit"\|"version"' authority/ggen-create-receiving-contract.json

# Re-verify sibling-repo HEAD at execution time (not drafting time):
git -C ~/ggen-create rev-parse HEAD
git -C ~/ggen-create merge-base --is-ancestor \
  8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4 "$(git -C ~/ggen-create rev-parse HEAD)" \
  && echo ancestor-confirmed
git -C ~/ggen-create rev-list --count \
  8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4.."$(git -C ~/ggen-create rev-parse HEAD)"

# If re-pinning: update producer.commit/producer.version, then re-run
# scripts/verify_ggen_create_bundle.py against a real bundle and quote its
# real pass/fail output. If instead documenting the pin as a frozen
# point-in-time receipt, leave the JSON untouched and add the companion
# note instead.

git diff --stat   # must show only authority/ggen-create-receiving-contract.json
                   # (or a companion note under the frozen-receipt
                   # resolution) and this ticket
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- Direct `Read` of `authority/ggen-create-receiving-contract.json` in full
  (34 lines) this session: confirms `producer.commit =
  "8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4"`, `producer.version = "0.4.0"`
  verbatim.
- `ls ~/ggen-create` this session: confirms a real, local sibling checkout
  exists (`architecture`, `BOOTSTRAP.md`, `Cargo.lock`, `Cargo.toml`,
  `crates`, ...).
- `git -C ~/ggen-create log -1 --format='%H %ci'` this session:
  `09a197ba32369bcec632dcc9b7919e633a6e08fb 2026-08-18 22:16:05 -0700`.
- `git -C ~/ggen-create cat-file -t 8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4`
  this session: `commit` (real, reachable object) --
  `git -C ~/ggen-create log -1 --format='%H %ci'
  8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4` confirms
  `2026-08-07 13:39:23 -0700`.
- `git -C ~/ggen-create merge-base --is-ancestor
  8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4
  09a197ba32369bcec632dcc9b7919e633a6e08fb` this session: exits `0` (real
  ancestor -- ordinary forward drift, not a force-push or rewrite).
- `git -C ~/ggen-create rev-list --count
  8a092c13538dc4ac91abfcfc46bcc6eaae6ceec4..09a197ba32369bcec632dcc9b7919e633a6e08fb`
  this session: `29` -- 29 real commits of drift.
- Direct `Read` of `governance/production-gaps.md` in full this session:
  its "What remains -- and *is* code-shaped, but out of this pass's scope"
  section states verbatim the pin is "stale against `ggen-create`'s
  current main (v26.8.6)" and names re-pinning as the real unblock,
  citing a different short-hash (`a0a9133`) than the one actually stored
  in the JSON file today (`8a092c1...`) -- both confirmed real, reachable,
  distinct commits via `git cat-file -t` this session; this ticket
  re-verifies against the real current on-disk pin, not the narrative
  document's own citation.
- `grep -il "ggen-create" tickets/GL-*.md` this session (59 tickets on
  disk, excluding this ticket's own self-match): real hits are
  `GL-AUTO-001.md` and `GL-EXP-006.md` only, both incidental (a bare
  filename in a `FORBIDDEN_DIFF` dump outside `GL-AUTO-001.md`'s actual
  Authored boundary; an unrelated mention in `GL-EXP-006.md`).
  `GL-ERRC-011.md` and `GL-EXP-028.md` reference the differently-spelled
  script name `verify_ggen_create_bundle.py` (underscore, not this
  authority file's hyphenated `ggen-create` path segment) for unrelated
  purposes -- confirmed this session with `grep -ni "ggen-create"
  tickets/GL-ERRC-011.md tickets/GL-EXP-028.md`, zero matches in either.
  None of the real hits proposes re-verifying or re-pinning this
  authority file's own producer commit.
- Direct `Read` of `scripts/verify_ggen_create_bundle.py`'s `verify()`
  function (lines 142-266) this session: confirms its `checks` dict
  cross-validates `producer_identity` fields for internal
  manifest/contract/receipt/authority consistency, but contains no branch
  that re-derives the producer's real, current git HEAD the way
  `verify_ggen_v26_8_1_migration.py` does for its own subject -- this
  staleness class is invisible to the script's own admission logic, not
  just to human review.
- `grep -n "ggen-create-receiving-contract" tickets/OVERLAPS.md` this
  session: zero matches -- no existing registry entry for this path.

## Standing

`UNKNOWN` -- not started. This ticket only establishes the re-verification
and decision as a real trackable unit of work; whether
`authority/ggen-create-receiving-contract.json`'s `producer.commit` should
ultimately be re-pinned to current upstream state, or explicitly
documented as a frozen point-in-time receipt, is left to execution-time
re-verification and the repo owner, not decided here.
