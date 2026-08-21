# GL-ERRC-011 — Stale EXPECTED_* SHA constants across 4 verify_*.py scripts

**Status:** EXECUTED
**Base:** `seanchatmangpt/ggen-legacy@f9b283e`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`scripts/verify_foundry_provenance.py`, `scripts/verify_foundry_bootstrap.py`,
`scripts/verify_docs.py`, and `scripts/verify_offline_transport.py` each
hardcode 40-character SHA constants (`EXPECTED_STABLE_GGEN`/
`EXPECTED_STABLE`/`EXPECTED_GGEN`, `EXPECTED_PLAN_HEAD`/`EXPECTED_PLAN`,
`EXPECTED_RUNTIME_HEAD`/`EXPECTED_CURRENT_RUNTIME`/`EXPECTED_RUNTIME`,
`EXPECTED_RECEIVING_RUNTIME`, `EXPECTED_HEAD`, `EXPECTED_WORKFLOW_RUN`) that
this session confirmed are all git objects unreachable in this worktree
(`git cat-file -t <hash>` fails on all 5 distinct hash values), and two of
the scripts (`verify_docs.py`, `verify_offline_transport.py`) additionally
compare live values (`ggen_source_revision`, `provenance.head`) against
these stale constants directly, meaning a clean checkout at current `HEAD`
fails those two scripts' checks today — not a hypothetical future
regression. This ticket does not silently update the constants to
whatever value passes today (that would launder an unverified claim into
a new hardcoded truth with the same staleness failure mode) — it (1) adds
a single documented `EXPECTED_*_SOURCE` comment above each constant citing
which producing repo/commit the value is supposed to represent (mirroring
`docs/v26.8.20/DECISIONS.md`'s existing finding that `CATALOG`'s hashes cite
a different producing repository's history), and (2) changes each
comparison's failure mode from a bare `False`/exit-nonzero to an explicit
`STALE_REFERENCE_UNVERIFIABLE` status distinguishable from a real
provenance mismatch, so a caller (human or CI) can tell "this script
cannot verify because its reference value predates this worktree's
reachable history" apart from "this script ran and found a real
discrepancy." Resolving *which* constants are actually correct (updating
them to real, currently-reachable values) requires the repo owner's
input on which producing-repo commits are canonical and is explicitly out
of scope — this ticket makes the staleness legible and non-silent, it does
not resolve it.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before assuming sole ownership of a path below.)

```text
scripts/verify_foundry_provenance.py   # EXPECTED_* comments + STALE_REFERENCE_UNVERIFIABLE status
scripts/verify_foundry_bootstrap.py    # EXPECTED_* comments + STALE_REFERENCE_UNVERIFIABLE status
scripts/verify_docs.py                 # EXPECTED_* comments + STALE_REFERENCE_UNVERIFIABLE status
scripts/verify_offline_transport.py    # EXPECTED_* comments + STALE_REFERENCE_UNVERIFIABLE status
tickets/GL-ERRC-011.md
```

No `EXPECTED_*` constant's literal value is changed by this ticket — only
its accompanying comment and its failure-path status string. No other
script (`verify_autonomic_finish.py`, `verify_ggen_create_bundle.py`,
`verify_lsp_contract.py`, `verify_ggen_v26_8_1_migration.py`, all already
confirmed to have no `EXPECTED_*` constants) is touched.

## Hard laws

1. No `EXPECTED_*` constant's hash value changes — this ticket makes
   staleness visible, it does not resolve which value is correct (that is
   a repo-owner provenance decision, matching `GL-ARCH-003`'s existing
   precedent of recording `UNKNOWN` over guessing).
2. A currently-passing comparison (if any exist after re-verification at
   execution time) must still pass identically after this ticket — only
   the *failure* path's status string changes, not the pass path's
   control flow.
3. `git diff --stat` after this ticket touches only the 4 named scripts
   and this ticket file — no `authority/`, `ontology/`, or `CATALOG`
   changes.

## Falsifiers

- Any `EXPECTED_*` constant's literal string value differs before/after
  this ticket.
- A script that passed before this ticket (against a real, current
  provenance JSON fixture) fails after this ticket, or vice versa, for a
  reason other than the new status-string distinction.
- `git cat-file -t <hash>` newly succeeds for a hash this ticket's comment
  claims is unverifiable (i.e., the comment asserts staleness the real
  repository state contradicts).

## Acceptance (executed this session)

```bash
cd /Users/sac/ggen-legacy/.claude/worktrees/wf_d45a38a1-7b7-3
# Reconfirm staleness before touching anything:
for h in 4bd2df69362c2708551f870c3dac36bce97898c2 \
         0f39227c102e0ac7519f0f27561356227a518653 \
         999db36647feeb2dfd0bd2250d2db2ef00b887c4 \
         f831e4d9fa80fe345349ce5d6e0fff41e6eb2a4a \
         0175ead9748a7f41018ec037828865ae11cfe267; do
  git cat-file -t "$h" >/dev/null 2>&1 && echo "$h: REACHABLE (ticket premise falsified)" || echo "$h: unreachable (confirms staleness)"
done
```

Real output (this session, this worktree, HEAD
`93d2ecd18147acaff659bf1d9cc2d4313628305b`):

```text
4bd2df69362c2708551f870c3dac36bce97898c2: unreachable (confirms staleness)
0f39227c102e0ac7519f0f27561356227a518653: unreachable (confirms staleness)
999db36647feeb2dfd0bd2250d2db2ef00b887c4: unreachable (confirms staleness)
f831e4d9fa80fe345349ce5d6e0fff41e6eb2a4a: unreachable (confirms staleness)
0175ead9748a7f41018ec037828865ae11cfe267: unreachable (confirms staleness)
```

All 5 confirmed unreachable — premise holds. Fix applied (comments +
`STALE_REFERENCE_UNVERIFIABLE` status wiring; no literal value changed).

```bash
python3 scripts/verify_docs.py --strict 2>&1 | grep -i "stale\|EXPECTED"
python3 scripts/verify_offline_transport.py 2>&1 | grep -i "stale\|EXPECTED"
git diff --stat
```

Real output:

- Both `grep` commands returned **no matches**. Correction to this
  ticket's own premise, discovered only by actually running the scripts
  this session rather than trusting the earlier session's note: in this
  worktree's current state, `authority/product-profile.json`'s
  `ggen_source_revision`, `authority/foundry-work-program.json`'s
  `runtime_provenance.head`, and `authority/offline-verifier-transport.json`'s
  `provenance.head` all already **equal** their respective stale
  `EXPECTED_*` constants (the fixture JSON was itself written to embed the
  same unreachable-object value the script expects). All 4 scripts
  therefore currently exit 0 with `errors: []` and never reach the new
  `STALE_REFERENCE_UNVERIFIABLE` branch — there is no live discrepancy in
  this worktree today, contra this ticket's original "meaning a clean
  checkout at current HEAD fails those two scripts' checks today" claim,
  which was accurate for the worktree state at the time it was drafted but
  is not reproducible in this session's worktree. The
  `STALE_REFERENCE_UNVERIFIABLE` code path is real and load-bearing (it
  fires the instant any of these live values diverges from its paired
  `EXPECTED_*` constant, which — given the constant is a confirmed-dead
  git object — is a "when," not an "if"), but is currently unexercised by
  this worktree's fixture data. Verified directly:
  ```
  $ python3 scripts/verify_foundry_provenance.py  -> standing: ALIVE, errors: []
  $ python3 scripts/verify_foundry_bootstrap.py   -> standing: ALIVE, errors: []
  $ python3 scripts/verify_docs.py --strict       -> standing: PARTIAL_ALIVE, errors: [], exit 0
  $ python3 scripts/verify_offline_transport.py   -> standing: ALIVE, errors: [], exit 0
  ```
- `git diff scripts/*.py | grep "EXPECTED_"` shows every `EXPECTED_*`
  assignment line unchanged (only `+`-added comment lines above each);
  no `-`-removed assignment line for any `EXPECTED_*` constant.
- `git diff --stat` (this session):
  ```
   scripts/verify_docs.py               | 28 +++++++++++++++++++++--
   scripts/verify_foundry_bootstrap.py  | 44 +++++++++++++++++++++++++++++++++++-
   scripts/verify_foundry_provenance.py | 38 +++++++++++++++++++++++++++----
   scripts/verify_offline_transport.py  | 17 +++++++++++++-
   4 files changed, 118 insertions(+), 9 deletions(-)
  ```
  plus this ticket file (new in this worktree) — matches Hard Law 3
  (only the 4 named scripts + this ticket touched; no `authority/`,
  `ontology/`, or `CATALOG` changes).

## Evidence this ticket is grounded in (verified this session)

- Direct `grep -n "EXPECTED_"` over all 4 scripts (run this session)
  confirms 5 distinct 40-character SHA-like constants:
  `EXPECTED_STABLE_GGEN`/`EXPECTED_STABLE`/`EXPECTED_GGEN` =
  `0f39227c102e0ac7519f0f27561356227a518653`;
  `EXPECTED_PLAN_HEAD`/`EXPECTED_PLAN` =
  `999db36647feeb2dfd0bd2250d2db2ef00b887c4`;
  `EXPECTED_RUNTIME_HEAD`/`EXPECTED_CURRENT_RUNTIME`/`EXPECTED_RUNTIME` =
  `f831e4d9fa80fe345349ce5d6e0fff41e6eb2a4a`;
  `EXPECTED_RECEIVING_RUNTIME` =
  `0175ead9748a7f41018ec037828865ae11cfe267`;
  `EXPECTED_HEAD` = `4bd2df69362c2708551f870c3dac36bce97898c2` (plus
  `EXPECTED_WORKFLOW_RUN = 30654755433`, a non-hash integer, in
  `verify_offline_transport.py`).
- `git cat-file -t <hash>` (run directly this session, all 5 hashes) fails
  with `fatal: git cat-file: could not get object info` for every one —
  none exist in this worktree, whose real current `HEAD` is
  `93d2ecd18147acaff659bf1d9cc2d4313628305b`.
- `docs/v26.8.20/ultracode-loop-progress.md:56` (item 9, this repo's own
  prior audit): "All 5 distinct 40-char SHA constants across
  verify_foundry_provenance.py/verify_foundry_bootstrap.py/verify_docs.py/
  verify_offline_transport.py are unreachable in this worktree ...
  verify_docs.py and verify_offline_transport.py also compare directly
  against live HEAD (f9b283e...) which matches none of them — stale." That
  entry ends "Documented, not fixed (outside GL-ARCH-003 boundary)" — this
  ticket is the follow-up it names.
- `docs/v26.8.20/DECISIONS.md`'s "Exhaustive cross-repo commit-hash
  finding" section documents the same class of problem for `CATALOG`'s
  `historical_source_commit` fields (all 79 hashes unreachable) and
  explicitly frames the resolution as "an open question for the repo
  owner," not a defect to silently fix — this ticket applies that same
  established, already-precedented framing to the `verify_*.py` scripts'
  `EXPECTED_*` constants rather than inventing a new resolution policy.

## Standing

`PARTIAL_ALIVE` — executed this session. The `EXPECTED_*_SOURCE` comments
and `STALE_REFERENCE_UNVERIFIABLE` status wiring are real and verified
(all 4 scripts run clean, `EXPECTED_*` literal values unchanged, diff
scope matches Hard Law 3). Determining the correct current values for
each `EXPECTED_*` constant remains a repo-owner provenance decision
explicitly out of scope, per Hard Law 1 — that portion of the underlying
staleness is legible now (via the comments and the dormant
`STALE_REFERENCE_UNVERIFIABLE` branch) but still unresolved.
