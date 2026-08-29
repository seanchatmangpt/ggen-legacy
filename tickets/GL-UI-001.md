# GL-UI-001 — ggen dashboard contract reconstitution

## Outcome

Independently receive and reconstitute the language-neutral dashboard contract manufactured for `ggen-ui` by `ggen-marketplace/ggen-dashboard-pack` without parsing React code, modifying producer ontology, or certifying the ggen producer.

The receiver proves only the bounded received contract: schema identity, standing vocabulary presence, projection identity uniqueness, exclusive BRCE DO topology, deterministic receipt manufacture, and replay/tamper refusal.

## Exact starting subjects

- receiver base: `seanchatmangpt/ggen-legacy@93d2ecd18147acaff659bf1d9cc2d4313628305b`
- producer subject: `seanchatmangpt/ggen-ui@34bb80e9c02326b49a866b0d2fbf02f6ff25404c`
- manufacturer subject: `seanchatmangpt/ggen-marketplace@bba99ff12533b7c8da3d5eaa7e88e8d5fe0133c6`
- reusable pack: `ggen-dashboard-pack@26.8.27`
- ggen runtime: whatever exact runtime is admitted by the above marketplace subject through `marketplace.toml`; this receiver does not independently promote or repin it.

The workflow pins these producer/manufacturer SHAs. If either moves, this ticket and receiver workflow must move explicitly; no floating ref is admitted.

## Calculus

```text
producer ontology
  -> marketplace pack
  -> admitted ggen runtime
  -> received dashboard-contract.json
  -> independent receiver validation
  -> deterministic reconstitution witness
  -> receiver receipt
  -> replay | REFUSED:REPLAY_DIVERGENCE
```

The receiver has `RECONSTRUCT_ONLY` authority. It has no DO authority and cannot transform contract validity into ggen certification, application runtime ALIVE, external actuation standing, or release standing.

## Exclusions

- no React/Next/TypeScript parsing is required for semantic admission;
- no copied producer ontology becomes receiver authority;
- no network actuator or BRCE client is implemented here;
- no ggen self-certification;
- no inference that a successful generated-contract check proves browser behavior;
- no inference that browser behavior proves external DO;
- no floating producer/manufacturer refs;
- no timestamps in deterministic receiver receipts.

## Falsifiers

- any authority stage other than `BRCE` has `allowsDo=true`;
- any intent kind other than `ACTUATE_VIA_BRCE` has `allowsDo=true`;
- `brceRequired` is false or absent;
- required standing or projection identities are absent;
- projection IDs or routes are duplicated;
- two identical receives manufacture different receipt digests;
- receipt tampering survives replay/integrity verification;
- the receiver claims `self_certifying=true`, `ggen_certified=true`, or DO authority.

## Acceptance

```bash
python3 tools/v26.8.27/test_dashboard_reconstitution.py -v
python3 tools/v26.8.27/dashboard_reconstitution.py verify \
  --contract /exact/dashboard-contract.json \
  --source-repo seanchatmangpt/ggen-ui \
  --source-sha 34bb80e9c02326b49a866b0d2fbf02f6ff25404c \
  --out /tmp/ui-receipt-a.json
python3 tools/v26.8.27/dashboard_reconstitution.py verify \
  --contract /exact/dashboard-contract.json \
  --source-repo seanchatmangpt/ggen-ui \
  --source-sha 34bb80e9c02326b49a866b0d2fbf02f6ff25404c \
  --out /tmp/ui-receipt-b.json
python3 tools/v26.8.27/dashboard_reconstitution.py replay \
  --left /tmp/ui-receipt-a.json \
  --right /tmp/ui-receipt-b.json
```
