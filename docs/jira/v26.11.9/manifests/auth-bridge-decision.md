# auth-bridge-decision

Standing: PARTIAL

Ticket T-020. Decision D3 is OPEN; the 21 parity cases are UNVERIFIED (T2).

## Facts (grounded)

- Legacy: opaque session id -> DynamoDB row; codes NO_SESSION_ID, INVALID_SESSION,
  SESSION_EXPIRED, SESSION_REVOKED (srve/docs/plan/16, docs/mine/infrastructure/
  dynamos-and-sessions.md). Revoked/expired fire before any Cognito call.
- xaas: AshAuthentication tokens, bcrypt, magic-link, TokenResource revocation.
- DynamoDB table in play: CognitoSessionsTable (template-topology.md:49).

## Options

| option | what | cost | risk |
|---|---|---|---|
| A shim | session-id to token actor | keeps DynamoDB | rollback expires sessions |
| B tokens | clients move to bearer tokens | FE auth store change | big-bang client change |

Recommendation (not a decision): B for steady state; A only as time-boxed
rollback bridge. Operator picks.

## 21 parity cases to replay (plan 16 auth chain)

roleScope both and 403 SWITCH_REQUIRED; entity-login permission rows;
cross-tenant acting-entity 403 vs super-admin scope all; fail-closed money
writes; 401-first for empty envelopes; impersonation write authority;
revoked/expired short-circuit with no IdP call. Replay: UNVERIFIED.

## Acceptance status

| acceptance | standing |
|---|---|
| 21 cases identical status and code | UNVERIFIED |
| revoked rejected, network blocked | UNVERIFIED |
| rollback expires bridged sessions | UNVERIFIED |

## See Also

scope-decisions.md · side-effects.md · ../tickets/T-020-auth-session-bridge.md
