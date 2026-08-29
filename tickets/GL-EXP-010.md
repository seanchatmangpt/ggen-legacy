# GL-EXP-010 — Reduce `migrations/ggen-v26.8.1/migration-manifest.json`'s stale pinned `source_head` to a real re-verification decision

**Status:** admitted, `NOT_STARTED` — drafted by standing ultracode exploration cron
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE` (decision/doc-level only — no re-pin performed by this drafting pass)
**Publication:** draft pull request; no merge authority

## Outcome

`migrations/ggen-v26.8.1/migration-manifest.json:138` pins:

```json
"source_head": "8351af4c5bbbf60bd99ab8417752a1762c6ea4e3",
```

I re-ran the manifest's own verifier against the real sibling `~/ggen` repo
this session:

```text
$ python3 scripts/verify_ggen_v26_8_1_migration.py --source-root ~/ggen --destination-root .
REFUSED: SOURCE_HEAD_MISMATCH_REFUSED expected=8351af4c5bbbf60bd99ab8417752a1762c6ea4e3 observed=a6403d99c24f2372d2ec496f390536900bdefc74
```

Independently confirmed the observed value directly against the sibling
repo (`git -C ~/ggen rev-parse HEAD` → `a6403d99c24f2372d2ec496f390536900bdefc74`).
This is not a rewrite/force-push: `git -C ~/ggen merge-base --is-ancestor
8351af4c5bbbf60bd99ab8417752a1762c6ea4e3 a6403d99c24f2372d2ec496f390536900bdefc74`
exits `0` (true — ordinary ancestor), and `git -C ~/ggen rev-list --count
8351af4c..a6403d99c` reports `297` real commits between them. Their commit
dates (`git -C ~/ggen log -1 --format='%H %ci'` for each): the pinned
`source_head` is `2026-08-01 22:49:59 +0000`; the sibling repo's actual
current HEAD is `2026-08-19 22:25:10 -0700` — roughly 18 days of ordinary
forward drift in the upstream `seanchatmangpt/ggen` repo the manifest
pins against.

Reading `scripts/verify_ggen_v26_8_1_migration.py:586-620` (`main()`), the
`source_head` check (`observed_source_head != manifest["source_head"]`) is
a **hard exact-match refusal** with no ancestor tolerance — unlike the
adjacent `corpus_head` check three lines below it, which explicitly
tolerates the destination being ahead of `corpus_head` via an
`is_ancestor()`/`CORPUS_ANCESTOR_OF_CANDIDATE` path. So this manifest's
`source_head` field is designed to demand a live, current pin — not a
one-time historical snapshot — yet nothing currently re-pins it as the
sibling repo moves forward, which means the verifier live-refuses today
and will keep refusing indefinitely as `~/ggen` continues to advance.

Separately, `migration-manifest.json:135`'s `corpus_head` field
(`07928bde9d9eaba2e2e2fd8f78fcdc3f7b0b63ff`, dated `2026-08-02 04:01:29
+0000`) is also behind this repo's actual current HEAD
(`bce7f6386c4203784beaae426e40804636c4151a`, dated `2026-08-20 20:44:18
-0700`) — confirmed by direct `git log -1 --format='%H %ci'` lookups this
session. Per the script's own logic this field tolerates drift (the
`CORPUS_ANCESTOR_OF_CANDIDATE` branch), so it is not independently
refusing anything today, but it is further evidence the whole manifest is
a point-in-time artifact nobody has revisited since early August.

**This exact `source_head` mismatch was already surfaced once, in
passing, and explicitly left unticketed.** `tickets/GL-EXP-008.md:52`
(read in full this session) states: "the manifest's recorded `source_head`
(`8351af4c...`) no longer matches" the sibling repo, and
`GL-EXP-008.md:160-165` independently quotes the identical
`SOURCE_HEAD_MISMATCH_REFUSED` line reproduced above. But `GL-EXP-008`'s
own scope (its Outcome, Hard Laws, and Authored boundary sections, all
read in full this session) is narrowly about adding a `justfile` recipe
that pass-through-wraps `verify_ggen_v26_8_1_migration.py` — Hard Law 3
there explicitly forbids adding this new recipe to any CI target
"because this script currently `REFUSED`s ... gating CI on it today would
make every run fail for a reason unrelated to the change under review,"
and its Authored boundary states verbatim "No change to
`scripts/verify_ggen_v26_8_1_migration.py`." Nowhere in `GL-EXP-008` is
the manifest itself touched, re-pinned, or decided upon — the staleness
is named as a caveat to justify not wiring the script into CI, not as a
problem this ticket's execution will resolve.

I confirmed no other ticket owns this decision either.
`grep -n "source_head" tickets/*.md` (real output this session) hits only
`GL-EXP-008.md:52` (the passing note above), `GL-ERRC-015.md` and
`GL-ERRC-019.md` (both referencing an unrelated Rust local variable named
`source_head` inside `tools/v26.8.1/src/{main,project_coverage}.rs`, not
this manifest field), and `GL-EXP-005.md` (referencing an unrelated
`manifest.exact_source_head` field inside a different verifier's report
struct in `tools/v26.8.1/src/bin/subsystem_verifier.rs`, not this file).
`grep -ln "migration-manifest" tickets/*.md` hits only
`tickets/AUDIT-REPORT.md` (a historical audit note, not a live ticket) and
`tickets/GL-MANUFACTURE-005.md`, whose own hits (confirmed by direct
`grep -n "migration-manifest" tickets/GL-MANUFACTURE-005.md`) are all
about the unrelated `schemas/migration-manifest.schema.json`'s
`component.disposition` enum, not this file's `source_head`/`corpus_head`
pins.

This is the same shape of finding `GL-ERRC-020` already converted into a
trackable ticket for a different pair of stale-pinned files
(`authority/foundry-work-program.json` / `foundry/bootstrap.yaml`'s
thrice-flagged `runtime_dependency_admitted:false` claim): a real,
reproducible, currently-live discrepancy between a checked-in pin and the
actual state of the repo it references, named more than once but never
turned into a decision anyone can execute or explicitly decline. This
ticket applies that identical pattern to
`migrations/ggen-v26.8.1/migration-manifest.json`'s `source_head` (and,
secondarily, `corpus_head`).

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before assuming sole ownership of a path below.)

```text
migrations/ggen-v26.8.1/migration-manifest.json   # source_head / corpus_head fields only
tickets/GL-EXP-010.md
```

No change to `scripts/verify_ggen_v26_8_1_migration.py`, `schemas/migration-manifest.schema.json`,
`migrations/ggen-v26.8.1/migration-intent.json`, `migrations/ggen-v26.8.1/SOURCE_LEDGER.md`,
`migrations/ggen-v26.8.1/equivalence-report.json`, or any `justfile` recipe —
this ticket is scoped to the manifest's two head-pin fields and the
re-verification decision around them, not to wiring, schema, or ledger
changes. No change to `tickets/GL-EXP-008.md`'s own scope or its
`justfile` recipe addition; that ticket's caveat about this exact
refusal stands independently and is not superseded by this one.

## Hard laws

1. This ticket may update `migration-manifest.json`'s `source_head`
   and/or `corpus_head` fields to a current, real commit SHA **only if**
   that re-verification is re-run at execution time (`git -C ~/ggen
   rev-parse HEAD`, or the equivalent for whatever sibling checkout is
   available then) and its real output is quoted in this ticket's
   evidence — never carry forward this drafting session's SHAs
   (`a6403d99c24f2372d2ec496f390536900bdefc74` for `source_head`,
   `bce7f6386c4203784beaae426e40804636c4151a` for the destination HEAD
   informing `corpus_head`) as sufficient at execution time, since both
   repos will have moved further by then.
2. If re-pinning `source_head`, the full verifier
   (`python3 scripts/verify_ggen_v26_8_1_migration.py --source-root
   <sibling> --destination-root .`) must be re-run against the new pin
   and its real pass/fail output (not just the `source_head` check
   in isolation) quoted in evidence — a manifest whose `source_head`
   matches but whose downstream per-file `blake3`/git-blob lineage or
   replay checks now fail is not an acceptable resolution; that
   discrepancy must be recorded and left for a human, not silently
   patched over.
3. Alternatively, this ticket may resolve the decision by explicitly
   documenting `migration-manifest.json` as a fixed point-in-time
   receipt (e.g. a comment/companion doc stating the pin is deliberately
   frozen at the original migration's source commit and is not intended
   to track live upstream `~/ggen` HEAD) rather than re-pinning it — but
   only one of these two resolutions (re-pin-and-reverify, or
   explicitly-frozen-receipt) may be chosen, and the choice must be
   stated in this ticket's evidence, not left implicit.
4. This ticket must not add any new CI wiring, and must not modify
   `GL-EXP-008`'s proposed `justfile` recipe or its own file scope.
5. `git diff --stat` after this ticket touches only
   `migrations/ggen-v26.8.1/migration-manifest.json` and
   `tickets/GL-EXP-010.md` (or, under Hard Law 3's frozen-receipt
   resolution, only a companion doc plus `tickets/GL-EXP-010.md`, with
   `migration-manifest.json` left untouched).

## Falsifiers

- `source_head` is changed without a fresh, quoted `git rev-parse
  HEAD` (or equivalent) re-verification run against the sibling repo at
  execution time.
- `source_head` is re-pinned but the full verifier script is not re-run
  against the new pin, or its real output is not quoted.
- Both resolutions (re-pin-and-reverify vs. explicitly-frozen-receipt)
  are attempted at once, or neither is — leaving the decision as
  ambiguous as it was before this ticket.
- Any file outside the authored boundary above is modified, including
  `scripts/verify_ggen_v26_8_1_migration.py`, `GL-EXP-008.md`, or its
  proposed `justfile` recipe.
- A fourth passing mention of this exact staleness is added anywhere in
  the repo instead of this ticket being executed or explicitly rejected
  by the repo owner.

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the stale claim before touching anything:
grep -n '"source_head"\|"corpus_head"' migrations/ggen-v26.8.1/migration-manifest.json
python3 scripts/verify_ggen_v26_8_1_migration.py --source-root ~/ggen --destination-root .

# Re-verify sibling-repo HEAD at execution time (not drafting time):
git -C ~/ggen rev-parse HEAD
git -C ~/ggen merge-base --is-ancestor 8351af4c5bbbf60bd99ab8417752a1762c6ea4e3 "$(git -C ~/ggen rev-parse HEAD)" && echo ancestor-confirmed

# If re-pinning: update source_head/corpus_head, then re-run the full
# verifier and quote its real pass/fail output. If instead documenting
# the manifest as a frozen point-in-time receipt, leave the JSON
# untouched and add the companion doc/comment instead.

git diff --stat   # must show only migration-manifest.json (or a companion
                   # doc under the frozen-receipt resolution) and this ticket
```

## Standing

`UNKNOWN` — not started. This ticket only establishes the re-verification
and decision as a real trackable unit of work; whether
`migration-manifest.json`'s `source_head`/`corpus_head` should ultimately
be re-pinned to current upstream state, or explicitly documented as a
frozen point-in-time receipt, is left to execution-time re-verification
and the repo owner, not decided here.
