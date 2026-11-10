#!/bin/bash
# usage: replay_migrations.sh <migrations_dir> <db> <workdir>
# Replays xaas Ecto migrations into a SCRATCH Postgres via ecto_sql_stub.exs (an approximation of
# the Ecto DSL, not xaas's own migrator). Requires PGHOST/PGPORT pointing at a scratch server.
# Never run against a real database.
set -u
M=${1:?migrations dir}; DB=${2:?scratch db}; W=${3:?workdir}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH=/opt/homebrew/opt/postgresql@15/bin:$PATH
mkdir -p "$W/sql"; : > "$W/status.tsv"
P="psql -q -v ON_ERROR_STOP=1 -d $DB"
for f in $(ls "$M"/*.exs | sort); do
  b=$(basename "$f")
  elixir "$HERE/ecto_sql_stub.exs" "$f" > "$W/sql/$b.sql" 2> "$W/sql/$b.err"; rc=$?
  if [ $rc -ne 0 ]; then printf "%s\tTRANSLATE_FAIL(%s)\t%s\n" "$b" $rc "$(grep -E 'UNSUPPORTED|TRANSLATE_ERROR' "$W/sql/$b.err" | head -1 | cut -c1-200)" >> "$W/status.tsv"; continue; fi
  if [ ! -s "$W/sql/$b.sql" ]; then printf "%s\tEMPTY\t\n" "$b" >> "$W/status.tsv"; continue; fi
  out=$( ($P -1 -f "$W/sql/$b.sql") 2>&1 ); rc=$?
  if [ $rc -eq 0 ]; then printf "%s\tAPPLIED\t\n" "$b" >> "$W/status.tsv"; else printf "%s\tAPPLY_FAIL\t%s\n" "$b" "$(echo "$out" | head -2 | tr '\n' ' ' | cut -c1-250)" >> "$W/status.tsv"; fi
done
cut -f2 "$W/status.tsv" | sed 's/(.*//' | sort | uniq -c
