"""Census of srve_* tables from a scratch Postgres that replayed xaas migrations.

usage: gen_ddl_census.py <db> <workdir>   (PGHOST/PGPORT select the scratch server)
Writes manifests/ddl-census.json with the exact source SHA of the replayed tree.
"""
import hashlib, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from _common import emit, source_shas

DB, W = sys.argv[1], sys.argv[2]
BIN = "/opt/homebrew/opt/postgresql@15/bin"


def q(sql):
    return subprocess.check_output([f"{BIN}/psql", "-d", DB, "-Atc", sql]).decode().strip()


def j(sql):
    return json.loads(q(f"select coalesce(json_agg(t),'[]') from ({sql}) t"))


L = "like 'srve\\_%'"
tables = [r["table_name"] for r in j(f"select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE' and table_name {L} order by 1")]
cols = j(f"select table_name,column_name,ordinal_position pos,data_type,udt_name,character_maximum_length len,numeric_precision prec,numeric_scale scale,is_nullable='NO' not_null,column_default \"default\" from information_schema.columns where table_schema='public' and table_name {L} order by 1,3")
fks = j(f"select c.conrelid::regclass::text tbl,c.conname name,pg_get_constraintdef(c.oid) def from pg_constraint c join pg_namespace n on n.oid=c.connamespace where n.nspname='public' and c.contype='f' and c.conrelid::regclass::text {L} order by 1,2")
cons = j(f"select c.conrelid::regclass::text tbl,c.conname name,c.contype,pg_get_constraintdef(c.oid) def from pg_constraint c join pg_namespace n on n.oid=c.connamespace where n.nspname='public' and c.contype in ('p','u','c') and c.conrelid::regclass::text {L} order by 1,2")
idx = j(f"select tablename tbl,indexname name,indexdef def from pg_indexes where schemaname='public' and tablename {L} order by 1,2")
status = [l.rstrip("\n").split("\t") for l in open(f"{W}/status.tsv")]
dump = subprocess.check_output([f"{BIN}/pg_dump", "--schema-only", "-d", DB])
open(f"{W}/schema.sql", "wb").write(dump)
out = {
    "source": "replay of xaas priv/repo/migrations via scripts/dryrun/ecto_sql_stub.exs into a scratch Postgres",
    "method_limits": "stub approximates the Ecto DSL (column_exists? answers false; types via own table); "
                     "not xaas's own migrator, so reproducibility against a real xaas DB is UNVERIFIED",
    "migration_files": len(status),
    "migration_status": {s: sum(1 for r in status if r[1].split("(")[0] == s)
                         for s in sorted({r[1].split("(")[0] for r in status})},
    "unreplayed": [{"file": r[0], "status": r[1], "detail": r[2] if len(r) > 2 else ""}
                   for r in status if r[1].split("(")[0] in ("TRANSLATE_FAIL", "APPLY_FAIL")],
    "table_count": len(tables),
    "tables": {t: {"columns": [c for c in cols if c["table_name"] == t],
                   "foreign_keys": [f for f in fks if f["tbl"] == t],
                   "constraints": [c for c in cons if c["tbl"] == t],
                   "indexes": [i for i in idx if i["tbl"] == t]} for t in tables},
    "column_count": len(cols), "fk_count": len(fks), "index_count": len(idx),
    "schema_dump_sha256": hashlib.sha256(dump).hexdigest(),
}
emit("ddl-census.json", out)
print(len(tables), len(cols), len(fks), len(idx))
