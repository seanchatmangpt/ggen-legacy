#!/bin/bash
# usage: refresh_manifests.sh [archive_dir]
# Extracts the exact HEAD of each source repo with `git archive` (never the live tree, never a
# worktree), records SOURCE_SHAS.json, and regenerates the four SHA-pinned manifests.
# ddl-census.json needs a scratch Postgres and is produced by replay_migrations.sh + gen_ddl_census.py.
set -eu
A=${1:-/tmp/ggen-legacy-sources}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rm -rf "$A"; mkdir -p "$A/xaas" "$A/srve/onengine-backend" "$A/srve/servengine-frontend"
sha() { (cd "$1" && git archive HEAD | tar -x -C "$2" 2>/dev/null; git rev-parse HEAD); }
X=$(sha "$HOME/xaas" "$A/xaas"); S=$(sha "$HOME/srve" "$A/srve")
B=$(sha "$HOME/srve/onengine-backend" "$A/srve/onengine-backend")
F=$(sha "$HOME/srve/servengine-frontend" "$A/srve/servengine-frontend")
find "$A" -type l -delete
printf '{"xaas":"%s","srve":"%s","srve/onengine-backend":"%s","srve/servengine-frontend":"%s"}\n' \
  "$X" "$S" "$B" "$F" > "$A/SOURCE_SHAS.json"
export GGEN_SRC_HOME="$A"
for g in gen_resource_classification gen_route_inventory gen_cutover_scope gen_prisma_coverage; do
  python3 "$HERE/$g.py"
done
cat "$A/SOURCE_SHAS.json"
