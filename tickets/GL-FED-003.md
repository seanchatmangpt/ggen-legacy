# GL-FED-003 — Federated capability ownership projection

## Exact subject

- repository: `seanchatmangpt/ggen-legacy`
- admitted base: `93d2ecd18147acaff659bf1d9cc2d4313628305b`
- control plane: `seanchatmangpt/chatman-ecosystem@7430dfc9b3ca138e703430d25de7c6f48a8d6ade`
- canonical capability: `capability:reconstitute-project-protocol-suite`

## Authority

CONSTRUCT only. Maximum local authority is `persist_control_plane`. There is no broker and no ambient or automatic irreversible DO, shell, deployment, merge, delete, release, or production authority created by this ticket.

## Observable behavior

`ecosystem/capability-owner.toml` must project the exact canonical owner relationship, broker requirement, receipt requirement, authority ceiling, repository identity, admitted base ancestry, and exact control-plane subject. The reusable DfCM federation court must refuse owner drift, stale control-plane identity, authority widening, unearned ALIVE standing, or ambient/automatic irreversible DO.

## Witnesses

- descriptor is admitted by the pinned federation verifier;
- exact PR head is checked out with ancestry by CI;
- admitted base is proven an ancestor of the exact PR head;
- canonical capability owner coverage is complete;
- admission receipt states `capability_standing_promoted=false`, `ambient_do=false`, `automatic_irreversible_do=false`, and `base_ancestry_verified=true`.

## Falsifiers

- `REFUSED:CONTROL_PLANE_SUBJECT_DRIFT`
- `REFUSED:FEDERATED_BASE_NOT_ANCESTOR`
- `REFUSED:OWNER_CAPABILITY_COVERAGE`
- `REFUSED:CAPABILITY_OWNER_MISMATCH`
- `REFUSED:EXACT_AUTHORITY_MISSING`
- `REFUSED:AMBIENT_DO`
- `REFUSED:AUTOMATIC_IRREVERSIBLE_DO`
- `REFUSED:UNEARNED_FEDERATED_STANDING`

## Replay

The owning court is the reusable workflow at the exact control-plane SHA above. Its success proves federation correspondence only; it does not crown reconstitution runtime behavior.

## Exclusions

GL-LSP-001, GL-PLAN-002, and GL-OSTAR-001 behavior, generated contracts, runtime implementation, external authority contracts, predecessor equivalence, and consequential actuation are unchanged.
