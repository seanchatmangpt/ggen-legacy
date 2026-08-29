# GL-EXP-012 — Wire `tools/v26.8.20/observe_contract.py` into `justfile` as an optional, suggestion-only recipe

**Status:** admitted, NOT_STARTED — drafted by standing ultracode exploration cron

**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.20/observe_contract.py` is a real, working, read-only characterization tool
(confirmed this session, not merely read): `python3 tools/v26.8.20/observe_contract.py --help`
exits 0 with a real `argparse` usage line (`--repo REPO`, `--target TARGET`,
`--command COMMAND`, `--out OUT`). Running it for real this session —

```console
$ python3 tools/v26.8.20/observe_contract.py --repo . --target AGENTS.md --out <scratch-dir>
wrote <scratch-dir>/47ab4ebe02b6900e4e6a4a16c297316f957280e17240e0a2310b592b3fa71fa6.json
```

— produced a genuine `ggen.legacy.observe.v1` contract JSON:

```json
{
  "schema": "ggen.legacy.observe.v1",
  "target": "AGENTS.md",
  "target_exists": true,
  "target_b3": "ef0683d0e458c2f811ac14348ab1641bea113cf66b30d8ef59e861b2d9db660f",
  "target_size_bytes": 10801,
  "git_head": "bce7f6386c4203784beaae426e40804636c4151a",
  "nonclaims": [
    "correctness of the observed behavior",
    "that this baseline is complete coverage of the target's real behavior",
    "any standing (ALIVE/PARTIAL_ALIVE/UNKNOWN/REFUSED) for the target"
  ]
}
```

Independently cross-checked this session, not taken on faith: `which b3sum` resolves to a
real binary (`/opt/homebrew/bin/b3sum`); running that same binary directly against
`AGENTS.md` (`b3sum AGENTS.md`) reproduces the exact digest
`ef0683d0e458c2f811ac14348ab1641bea113cf66b30d8ef59e861b2d9db660f`; `wc -c AGENTS.md` reports
exactly `10801`, matching `target_size_bytes`; `git_head` matches the real current `HEAD`
(`bce7f6386c4203784beaae426e40804636c4151a`, this session's own `gitStatus`). The script's own
docstring (`tools/v26.8.20/observe_contract.py`, read this session, 132 lines total) states it
is "the first (read-only) tool of the ggen-legacy-mcp 7-tool surface proposed in
`planning/v26.8.20/README.md`" and is "Read-only w.r.t. the observed target: never writes into
`--repo`, only into `--out`." Reading `planning/v26.8.20/README.md` (this session) confirms
that surrounding design is explicitly **not admitted** ("Standing: candidate proposal, not
admitted... Nothing here is executable source") — this ticket does not admit that design; it
wires only the one already-real, already-standalone script that exists on disk today, exactly
as `GL-ERRC-022` wired `propose-disposition` without admitting the rest of
`dsrust-disposition-proposer`'s roadmap.

But nothing wires this script into this repo's admission workflow:
`grep -rn "observe_contract" justfile tools/v26.8.1/justfile .github/workflows/*.yml` (run this
session) returns zero matches (exit code 1, no output), and `grep -n
"observe_contract\|tools/v26\.8\.20" tickets/*.md` (run this session, across all `GL-*.md`
tickets present at drafting time) also returns zero matches — no ticket currently claims this
file. This is the identical shape already admitted/executed three times in this corpus for
sibling candidates: `GL-ERRC-022` (`tools/dsrust-disposition-proposer`, `EXECUTED`),
`GL-EXP-004` (`planning/v26.8.7/cli.py`, `NOT_STARTED`), and `GL-EXP-008`
(`scripts/verify_ggen_v26_8_1_migration.py`, `NOT_STARTED`) — all read/confirmed directly this
session. This ticket applies the same already-precedented pattern (an additive,
suggestion-only `justfile` pass-through recipe, no change to the wrapped script's own logic,
no CI gate) to a fourth sibling candidate.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` — check there before
assuming sole ownership of a path below.)

```text
justfile                          # new recipe only, additive
tools/v26.8.20/observe_contract.py  # no source change — wiring only, not modifying the script's own logic
tickets/GL-EXP-012.md
```

No change to `planning/v26.8.20/README.md` or any of the other 6 proposed (not-yet-existing)
tools in that design — this ticket wires only the one script that is real and on disk today.
No change to `GL-ERRC-022`'s `propose-disposition` recipe, `GL-EXP-004`'s proposed
`planning-cli` recipe, or `GL-EXP-008`'s proposed `verify-migration` recipe — this ticket adds
a fifth, distinct `justfile` recipe alongside `planning-max`, `propose-disposition`, and the
two not-yet-executed proposals. This `justfile` overlap should be disclosed in
`tickets/OVERLAPS.md`'s existing `## \`justfile\`` section at execution time.

## Hard laws

1. The new recipe is a pure pass-through to `python3 tools/v26.8.20/observe_contract.py` — it
   must not reimplement, swallow, or reinterpret the script's own output, exit codes, or
   `nonclaims`.
2. The new `justfile` recipe is additive; it does not change any existing recipe's behavior,
   including `planning-max`, `propose-disposition`, `ci`, `ci-all`, and `v26-ci`.
3. No new CI step is added by this ticket — CLI wiring only, mirroring `GL-ERRC-022`'s and
   `GL-EXP-008`'s existing discipline. A characterization tool that writes a fresh contract
   JSON on every invocation is not a stable gate and must not be treated as one.
4. `--repo`, `--target`, and `--out` must remain required, caller-supplied arguments (mirrors
   the script's own `argparse` definition) — the new recipe must not hardcode a default
   `--repo`/`--target`/`--out` that papers over the caller's actual intent.
5. This ticket does not admit `planning/v26.8.20/README.md`'s broader 7-tool `ggen-legacy-mcp`
   proposal (skills, subagents, RDF ontology, `ggen sync` construction, strangler-fig verify
   loop) — that design remains an unadmitted candidate proposal per its own stated standing.
   Only the one already-real script is wired.

## Falsifiers

- The new recipe does not exist / fails to invoke the real
  `tools/v26.8.20/observe_contract.py`.
- `just --list` no longer shows `planning-max` or `propose-disposition` unchanged after this
  ticket's diff.
- The new recipe is reachable from `ci`, `ci-all`, or `v26-ci`.
- `git diff --stat` shows any file changed other than `justfile` and `tickets/GL-EXP-012.md`.
- `git diff --stat -- tools/v26.8.20/observe_contract.py` shows any output (would mean this
  ticket strayed into the script's own logic).
- The recipe's output is silently treated as admitted RDF fact or auto-merged into any
  `CATALOG`/`draft-candidates.json`/ontology file without a human step.

## Acceptance (not yet run — ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Confirm the gap before fixing:
grep -rn "observe_contract" justfile tools/v26.8.1/justfile .github/workflows/*.yml
  # expect: no output (zero matches)
just --list | grep -i observe   # expect no output (recipe doesn't exist yet)

# After adding the recipe (proposed name: observe-contract, mirroring
# GL-ERRC-022's `propose-disposition *ARGS:` pass-through shape):
just --list | grep -i observe-contract        # expect the new recipe listed
just observe-contract --help                  # expect the real script's argparse usage line
just observe-contract --repo . --target AGENTS.md --out /tmp/observe-check
  # expect a real ggen.legacy.observe.v1 JSON written and printed, exit 0

# Confirm existing recipes untouched:
just planning-max               # expect unchanged verify.py --strict behavior
just --list | grep -i propose-disposition   # expect unchanged

git diff --stat   # must show only justfile and tickets/GL-EXP-012.md
git diff --stat -- tools/v26.8.20/observe_contract.py   # must show no output
```

## Evidence this ticket is grounded in (verified this session)

- `python3 tools/v26.8.20/observe_contract.py --help` (run directly this session): exit 0,
  real `argparse` usage line listing `--repo`, `--target`, `--command`, `--out`.
- `python3 tools/v26.8.20/observe_contract.py --repo . --target AGENTS.md --out <scratch-dir>`
  (run directly this session, real command, not simulated): exit 0, wrote a real
  `ggen.legacy.observe.v1` JSON contract with `target_b3` matching a directly-run `b3sum
  AGENTS.md` (`ef0683d0e458c2f811ac14348ab1641bea113cf66b30d8ef59e861b2d9db660f`),
  `target_size_bytes` (`10801`) matching a directly-run `wc -c AGENTS.md`, and `git_head`
  matching this session's real current `HEAD` (`bce7f6386c4203784beaae426e40804636c4151a`).
- `which b3sum` (run directly this session): `/opt/homebrew/bin/b3sum` — the hashing is a real
  subprocess call to a real binary, not a stub.
- `wc -l tools/v26.8.20/observe_contract.py` (run directly this session): `132
  tools/v26.8.20/observe_contract.py` — read in full this session; confirms real `subprocess`
  calls to `git rev-parse HEAD` and `b3sum`, and a real `contract_id` computed as the BLAKE3 of
  the canonical (sorted-key, whitespace-stripped) JSON excluding `observed_at`.
- `grep -rn "observe_contract" justfile tools/v26.8.1/justfile .github/workflows/*.yml` (run
  directly this session): zero matches (exit code 1, no output).
- `grep -n "observe_contract\|tools/v26\.8\.20" tickets/*.md` (run directly this session,
  across all `GL-*.md` tickets present at drafting time): zero matches — no ticket claims this
  file.
- `planning/v26.8.20/README.md` (read directly this session): confirms `observe_contract.py`
  is the first of 7 proposed tools in a design explicitly marked "candidate proposal, not
  admitted" — this ticket wires only the one script that already exists on disk, not the
  surrounding unadmitted design.
- `tools/v26.8.20/observed/4cf7ed2596d66358f720027a96b2f9ae1f473bda49553104f19760bcefe67b5f.json`
  (read directly this session): a prior real invocation of this same script exists on disk
  (against a sibling repo, `~/chatman-ecosystem/.../wasm4pm-drift-reconciliation-pack`,
  `observed_at` earlier the same day) — independent confirmation the tool has already been run
  for real more than once, by more than one invocation, before this ticket.
- `tickets/GL-ERRC-022.md` (read directly this session, `EXECUTED`), `tickets/GL-EXP-004.md`
  (read directly this session, `NOT_STARTED`), and `tickets/GL-EXP-008.md` (read directly this
  session, `NOT_STARTED`) are the three directly analogous, already-drafted/landed precedents
  for this exact "real tool, zero wiring" pattern — same additive, suggestion-only `justfile`
  recipe shape, same "no CI gate" discipline, same corpus.
- `tickets/OVERLAPS.md`'s `## \`justfile\`` section (read directly this session) already
  tracks three tickets sharing this file (`GL-PLAN-002`'s `planning-max`, `GL-ERRC-022`'s
  `propose-disposition`, `GL-EXP-004`'s proposed `planning-cli`); `GL-EXP-008` adds a fourth
  (`verify-migration`) not yet reflected there at drafting time. This ticket's
  `observe-contract` recipe follows the same non-overlapping-target convention and should be
  added as a fifth entry at execution time.

## Standing

`PARTIAL_ALIVE` ceiling only — this ticket is drafted and admitted, `NOT_STARTED`. No code has
been written or run beyond the read-only verification commands captured above (confirming the
script's real internals, one real successful invocation producing a verified-correct contract
JSON, its absence from `justfile`/CI, and its absence from every other ticket's claimed
boundary). Executing this ticket (adding the recipe, re-running the "Acceptance" commands, and
recording their real output) is required before any higher standing can be claimed.
