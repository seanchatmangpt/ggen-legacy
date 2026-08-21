# GL-ERRC-008 — Automated pre-filter for draft-candidates.json disposition triage

**Status:** admitted, `NOT_STARTED` — drafted by ultracode ERRC pass
**Base:** `seanchatmangpt/ggen-legacy@bce7f63`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

Add a `pre_filter_candidates()` pass to `tools/v26.8.1/legacy_archaeology.py`,
run after `draft_candidates()` and before a human ever opens
`draft-candidates.json`, that computes a machine-checkable
`pre_filter_signal` field for every `"disposition": "UNKNOWN"` entry —
`path_exists_at_head` (does any of `legacy_source_path`'s comma-separated
paths exist in the current working tree, per-path boolean list),
`is_merge_of_reverted_workflow` (heuristic: `is_merge=true` and every deleted
path matches `.github/workflows/*` — this repo's own data shows this pattern
dominates the current 22 entries), and `insertions_deletions_ratio` (flags
`insertions == 0` — pure deletions — as the cheapest-to-verify class). This
does **not** set `disposition` to anything but `UNKNOWN` — Hard Law 2 of
`tickets/GL-ARCH-003.md` (no draft auto-merges into `CATALOG`) is unchanged.
It adds a sort/annotation layer a human reviewer consumes to triage 22
entries in priority order instead of file order, and gives a future session
a machine-checkable reason to *fast-track* (not auto-approve) the entries
most likely to be trivially real.

## Authored boundary

```text
tools/v26.8.1/legacy_archaeology.py   # pre_filter_candidates(), additive function + CLI mode
tools/v26.8.1/draft-candidates.json   # regenerated with pre_filter_signal field added, disposition untouched
tickets/GL-ERRC-008.md
```

`draft_candidates()`'s existing emission logic (slug, disposition, standing,
notes) and `_catalog_covered_hashes()`'s short-hash matching are unchanged —
this ticket adds one new annotation pass downstream of them, it does not
alter what counts as covered or what gets emitted as a draft.

## Hard laws

1. `pre_filter_signal` never sets or implies `disposition` != `"UNKNOWN"` —
   inherits `tickets/GL-ARCH-003.md` Hard Law 2 verbatim: no draft is
   auto-merged or auto-promoted into `CATALOG` by this ticket.
2. `pre_filter_candidates()` is read-only with respect to the working tree —
   it inspects `Path.exists()` against the current checkout, it does not
   fetch, checkout, or diff any other commit.
3. `legacy-capabilities.ttl` byte-identity invariant (`GL-ARCH-003.md` Hard
   Law 3) is preserved — this ticket touches only `draft-candidates.json`
   and `legacy_archaeology.py`.
4. A `pre_filter_signal` that is wrong (a false "safe to fast-track") must
   fail visibly at the next human-verification step, not silently promote —
   this ticket adds no promotion path, so there is no silent-promotion
   surface to introduce.

## Falsifiers

- Any of the 22 current `draft-candidates.json` entries end up with
  `disposition` != `"UNKNOWN"` after running `pre_filter_candidates()`.
- `path_exists_at_head` reports `true` for a path that
  `git cat-file -e HEAD:<path>` (or `Path.exists()` against a clean
  checkout) disagrees with, for any of the 22 entries.
- `ontology/v26.8.1/legacy-capabilities.ttl` differs (checksum) before/after
  running the new pass.
- `is_merge_of_reverted_workflow` is `true` for an entry whose
  `legacy_source_path` contains any path outside `.github/workflows/`.

## Acceptance (not yet run — ticket not started)

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools/v26.8.1')
from legacy_archaeology import pre_filter_candidates
pre_filter_candidates()
"
python3 -c "
import json
d = json.load(open('tools/v26.8.1/draft-candidates.json'))
assert len(d) == 22, len(d)
assert all(e['disposition'] == 'UNKNOWN' for e in d), 'Hard Law 1 violated'
assert all('pre_filter_signal' in e for e in d), 'pre_filter_signal missing'
print('OK:', sum(1 for e in d if e['pre_filter_signal']['is_merge_of_reverted_workflow']), 'of 22 flagged as workflow-revert class')
"
git diff --stat ontology/v26.8.1/legacy-capabilities.ttl  # must be empty
```

## Evidence this ticket is grounded in (verified this session)

- `tools/v26.8.1/draft-candidates.json` contains exactly 22 entries; `grep
  -c '"disposition": "UNKNOWN"'` matches 22/22 (100%) — confirmed by direct
  read of the file.
- `tickets/GL-ARCH-003.md` line 40 states promotion/review is explicitly
  `(out of scope) human/session reviews drafts, re-verifies each commit`;
  line ~145 confirms "the 20 drafts are unreviewed by design (Hard Law 2)"
  (the file has grown from 20 to 22 entries since that ticket was written —
  the backlog is actively growing, not static).
- `tools/v26.8.1/legacy_archaeology.py:1153-1199` (`draft_candidates()`) is
  the exact, real function that emits these entries; its only existing
  machine gate before human review is `_catalog_covered_hashes()`'s
  short-hash cross-reference against `CATALOG` (line 1170,
  `if c.short_hash in covered_hashes: continue`) — no other automated
  pre-filtering exists downstream of that check today.
- Direct inspection of all 22 current entries shows a real, exploitable
  pattern: the majority are `is_merge=true` merges whose `legacy_source_path`
  is entirely `.github/workflows/*.yml` files, and several (e.g.
  `draft_c273f02f2`, deletions=78/insertions=0) are pure-deletion commits —
  exactly the classes `pre_filter_signal` targets.

## Standing

`UNKNOWN` — not started. This ticket only drafts the pre-filter; running it
against the live 22-entry backlog and having a human/session act on the
resulting priority ordering remains explicitly out of scope, per
`GL-ARCH-003.md`'s existing promotion boundary.
