# GL-FED-003 — Federated capability ownership projection

## Exact subject

- repository: `seanchatmangpt/ggen-legacy`
- admitted base: `93d2ecd18147acaff659bf1d9cc2d4313628305b`
- control plane: `seanchatmangpt/chatman-ecosystem@475d36e9c716fbedb33db6b74b55b0edf6f73c71`
- canonical capability: `capability:reconstitute-project-protocol-suite`

## Authority

CONSTRUCT only. Maximum local authority is `persist_control_plane`. There is no broker and no ambient DO, shell, deployment, merge, delete, release, or production authority created by this ticket.

## Observable behavior

`ecosystem/capability-owner.toml` must project the exact canonical owner relationship, broker requirement, receipt requirement, authority ceiling, repository identity, and exact control-plane subject. The reusable federation court must refuse owner drift, stale control-plane identity, authority widening, unearned ALIVE standing, or ambient DO.

## Witnesses

- descriptor is admitted by the pinned federation verifier;
- exact PR head is checked out by CI;
- canonical capability owner coverage is complete;
- admission receipt states `capability_standing_promoted=false` and `ambient_do=false`.

## Falsifiers

- `REFUSED:CONTROL_PLANE_SUBJECT_DRIFT`
- `REFUSED:OWNER_CAPABILITY_COVERAGE`
- `REFUSED:CAPABILITY_OWNER_MISMATCH`
- `REFUSED:EXACT_AUTHORITY_MISSING`
- `REFUSED:AMBIENT_DO`
- `REFUSED:UNEARNED_FEDERATED_STANDING`

## Replay

The owning court is the reusable workflow at the exact control-plane SHA above. Its success proves federation correspondence only; it does not crown reconstitution runtime behavior.

## Exclusions

GL-LSP-001, GL-PLAN-002, and GL-OSTAR-001 behavior, generated contracts, runtime implementation, external authority contracts, predecessor equivalence, and consequential actuation are unchanged.
