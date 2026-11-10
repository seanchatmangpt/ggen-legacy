# T029 — Independent verifier with negative controls

Standing: REGISTERED

Wave: W2 · Depends on: T-025, T-028
Owned paths: ~/ggen-legacy/verifiers
Research lanes: L10

## Scope

A verifier distinct from the producer runs the same request set against xaas and the candidate
with equal results, and negative controls are refused. Generated output has no runtime dependency
on xaas source. There is no v26.9.28 verifier today (verifiers/ holds only
verify_ggen_v26_8_3.py).

## Acceptance

- Equal results on the request set; each negative control refused.
- Producer output is never its own verifier.

## Gates (verbatim, not yet run)

```bash
cd ~/ggen-legacy && python3 verifiers/verify_srve_cutover.py --subject $SHA
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t029-independent-verifier-and-negative-controls.md (under docs/jira/v26.11.9/)
Falsifier: The producer's own output is the only verifier, or a negative control is admitted.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-029`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T0

Clauses:
- [T0/exists] verifier present
  - paths:
    - `ggen-legacy:verifiers/verify_srve_cutover.py`
- [T0/cmd] python parses verifiers/verify_srve_cutover.py
  - argv:
    - `python3`
    - `-c`
    - `import ast,sys;ast.parse(open(sys.argv[1]).read())`
    - `@ggen-legacy:verifiers/verify_srve_cutover.py`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
