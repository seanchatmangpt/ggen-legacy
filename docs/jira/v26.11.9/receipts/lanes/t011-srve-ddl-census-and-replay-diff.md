# T011 — srve DDL census and replay diff (dry-run receipt)

Standing: UNVERIFIED

## Subject

Dry-run: `ggen-create cutover dryrun --ticket T-011` at 2026-11-10T05:19:20.797518+00:00
Report verdict: NOT_READY; tier needed to decide fully: T1
Source heads:
- ggen-create: 09a197ba32369bcec632dcc9b7919e633a6e08fb
- ggen-ecosystem: ab2a850488c0f49dc1f7754c6236a4f5d8d6d18f
- ggen-legacy: 46416e7464c7d51411ebd10cafc3ae15760e2a93
- srve: 29267a4453c2ea7536127047aadd8328ef63ca59
- xaas: d7e38a376450f7ae680fb580082577b24d9c31c6

## Clauses

- [PASS_PREDICTED] (T0/distinct) distinct srve_* tables in migrations
  got 73, need eq 73
- [PASS_PREDICTED] (T0/exists) ddl census
  present
- [UNVERIFIED] (T1/unverified) pg_dump replay diff
  T1: needs scratch Postgres replay of 166 migrations

## Not claimed

This is a file-level prediction. No cutover, migration, generation or backend run
is evidenced here, and T1/T2 clauses stay UNVERIFIED until a scratch or shadow run.

## See Also

../../tickets/ · ../dry-run-latest.json · ../../INDEX.md
