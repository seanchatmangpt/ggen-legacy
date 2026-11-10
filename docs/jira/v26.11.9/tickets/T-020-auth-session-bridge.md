# T020 — Auth and session bridge

Standing: REGISTERED

Wave: W1 · Depends on: T-017
Owned paths: ~/srve/packs/srve-backend-pack
Research lanes: L03, L20

## Scope

xaas is token-based (AshAuthentication, bcrypt, magic-link, TokenResource revocation); legacy is
an opaque session-id in a DynamoDB row with codes
NO_SESSION_ID/INVALID_SESSION/SESSION_EXPIRED/SESSION_REVOKED. Decide shim vs move clients to
tokens, then implement. Cover the 21 parity cases: roleScope both and 403 SWITCH_REQUIRED, entity-
login permission rows, acting-entity cross-tenant 403 with super-admin scope all, fail-closed
money writes, 401-first for empty envelopes, impersonation write authority. Revoked/expired short-
circuit with no IdP call.

## Acceptance

- 21 cases replayed against the candidate with identical status and code.
- Revoked session rejected with network blocked.
- Rollback expires bridged sessions cleanly.

## Gates (verbatim, not yet run)

```bash
cd ~/srve && ./scripts/auth_parity_cases.sh
```

## Git law

commit -F file, never -m; explicit pathspec only; no git add -A, no stash, no worktrees.

## Test budget

At most 3 tests per ticket; Chicago style, real collaborators, no mocks.

## Receipt

Path: receipts/lanes/t020-auth-session-bridge.md (under docs/jira/v26.11.9/)
Falsifier: A servengine-only role gets 200 at an entity login, or switching forces a global
logout.

## Dry run

Command: `ggen-create cutover dryrun --ticket T-020`
Read-only; add `--selftest` to prove each deterministic clause flips.
Highest tier needed to fully decide: T2

Clauses:
- [T0/exists] auth decision record
  - paths:
    - `ggen-legacy:docs/jira/v26.11.9/manifests/auth-bridge-decision.md`
- [T2/unverified] 21 parity cases replayed
  - reason: `needs candidate running and legacy cases`

PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED
until a scratch or shadow run is authorized.

## See Also

CHARTER.md · INDEX.md · DEPENDENCY-GRAPH.md
