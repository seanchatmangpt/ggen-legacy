# v26.10.1 — beam4pm + XaaS engine contract

ggen-legacy does not grow a second process miner or a second autonomous worker
fabric.

The engine boundary is:

- **beam4pm** owns observed behavior and bounded legacy/candidate equivalence.
- **ggen-legacy** owns semantic admission, authority, manufacture eligibility,
  and predecessor sunset eligibility.
- **XaaS** owns unattended repair campaigns over concrete counterexamples.
- **ggen** owns projection of admitted semantic authority into artifacts.

The first wire contract is `beam4pm-legacy-equivalence/1`. ggen-legacy accepts
that evidence through `compile_engine_handoff` and emits
`ggen-legacy-engine-handoff/1`.

A beam4pm EQUIVALENT verdict never self-promotes into manufacture or sunset
authority. The handoff remains `manufacture_allowed=false` and
`retirement_allowed=false` until the existing independent ggen-legacy
admission controls grant those consequences.

A COUNTEREXAMPLE verdict preserves the exact subject and court receipt and
routes the next edge to an XaaS repair campaign. XaaS repairs the candidate;
beam4pm reruns the same court; ggen-legacy then reevaluates admission.

```text
legacy + candidate
      |
      v
   beam4pm
      |
      | beam4pm-legacy-equivalence/1
      v
 ggen-legacy
   /       \
repair    review
  |          |
 XaaS     admission
  |          |
  +-> ggen <-+
```

This contract deliberately keeps selection/construction separate from DO and
sunset authority.
