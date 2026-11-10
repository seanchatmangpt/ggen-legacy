# T030 — kind scripts parametrized (dry-run receipt)

Standing: BLOCKED

## Subject

Dry-run: `ggen-create cutover dryrun --ticket T-030` at 2026-11-10T05:19:20.797518+00:00
Report verdict: NOT_READY; tier needed to decide fully: T0
Source heads:
- ggen-create: 09a197ba32369bcec632dcc9b7919e633a6e08fb
- ggen-ecosystem: ab2a850488c0f49dc1f7754c6236a4f5d8d6d18f
- ggen-legacy: 46416e7464c7d51411ebd10cafc3ae15760e2a93
- srve: 29267a4453c2ea7536127047aadd8328ef63ca59
- xaas: d7e38a376450f7ae680fb580082577b24d9c31c6

## Clauses

- [FAIL] (T0/absent) no xaas:local / deployment/xaas in kind scripts
  8 matches
- [FAIL] (T0/absent) no hashed asset names in smoke test
  4 matches
- [PASS_PREDICTED] (T0/cmd) bash -n scripts/kind-bootstrap.sh
  rc 0, need 0
- [PASS_PREDICTED] (T0/cmd) bash -n scripts/kind-smoke-test.sh
  rc 0, need 0
- [PASS_PREDICTED] (T0/cmd) bash -n scripts/kind_doctor.sh
  rc 0, need 0

## Not claimed

This is a file-level prediction. No cutover, migration, generation or backend run
is evidenced here, and T1/T2 clauses stay UNVERIFIED until a scratch or shadow run.

## See Also

../../tickets/ · ../dry-run-latest.json · ../../INDEX.md
