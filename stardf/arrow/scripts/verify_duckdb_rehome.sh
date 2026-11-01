#!/bin/bash
# verify_duckdb_rehome.sh — fail-closed frozen-duckdb rehome court (W1 lane 9)
#
# Runs entirely in a /tmp sandbox. Renames NOTHING in any real tree.
# Falsifier under test: frozen-duckdb 2.0.3 resolves and compiles from crates.io
# WITHOUT any machine-local path (no [patch.crates-io], no /Users/sac/frozen-duckdb,
# no $HOME/.frozen-duckdb). Registry resolve proven = D13 acceptance datum.
#
# Fail-closed contract:
#   exit 0  — registry-only resolve + compile ALIVE, real-tree digests unchanged
#   exit 42 — VACUOUS (local path hit in sandbox manifests, or patch present)
#   exit 1  — cargo failed (recorded honestly, never passed)
#   exit 3  — restore-digest mismatch on the real frozen-duckdb tree
#   exit 4  — sandbox cleanup refused (loud, disclosed)
#   exit 5  — provenance assertion failed (resolved source is not the registry)
set -uo pipefail

FORK=/Users/sac/frozen-duckdb
FORK_CACHE="$HOME/.frozen-duckdb"
EXIT_VACUOUS=42

say() { printf '[rehome-court] %s\n' "$*"; }

# ---- (d) PRE digests of the real tree (Cargo.tomls only — read-only) ---------
PRE_FORK=$(find "$FORK" -maxdepth 3 -name Cargo.toml -exec shasum -a 256 {} + 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
say "PRE_FORK digest=$PRE_FORK"
if [ -z "$PRE_FORK" ]; then
  say "FAIL: cannot digest $FORK (missing or unreadable)"; exit 1
fi

# ---- (a) minimal sandbox project: registry-only, NO [patch] ------------------
SB=$(mktemp -d /tmp/rehome-court.XXXXXX) || { say "FAIL: no sandbox"; exit 1; }
cleanup() {
  rm -rf "$SB" 2>/dev/null
  if [ -d "$SB" ]; then say "FAIL: sandbox rm denied at $SB (disclose)"; exit 4; fi
}
trap cleanup EXIT

mkdir -p "$SB/src"
cat > "$SB/Cargo.toml" <<'EOF'
[package]
name = "rehome-court-subject"
version = "0.1.0"
edition = "2021"

[dependencies]
frozen-duckdb = { version = "=2.0.3" }
EOF
cat > "$SB/src/main.rs" <<'EOF'
fn main() {}
EOF
# Dependency-only court: `cargo check` type-checks frozen-duckdb itself; the
# subject binary intentionally exercises no symbols (linking is D13's follow-up,
# not this court's falsifier — the falsifier is RESOLVE provenance).

# ---- (b) rename-guard: grep sandbox manifests for machine-local paths --------
GUARD_HITS=$(grep -R -n -e "/Users/sac/frozen-duckdb" -e "$HOME/.frozen-duckdb" \
  "$SB/Cargo.toml" "$SB/Cargo.lock" 2>/dev/null || true)
if [ -n "$GUARD_HITS" ]; then
  say "VACUOUS: machine-local path present in sandbox manifests:"
  printf '%s\n' "$GUARD_HITS"
  exit $EXIT_VACUOUS
fi
if grep -q 'patch.crates-io' "$SB/Cargo.toml"; then
  say "VACUOUS: [patch.crates-io] present in sandbox manifest"; exit $EXIT_VACUOUS
fi
say "rename-guard: clean (no local paths, no patch section)"

# ---- (c) registry resolve from crates.io ------------------------------------
export CARGO_NET_OFFLINE=false
cd "$SB" || exit 1
say "running cargo generate-lockfile (registry resolve of frozen-duckdb =2.0.3)"
if ! cargo generate-lockfile 2>&1; then
  say "BLOCKED-not-resolved: cargo could not reach/fetch the registry — never a pass"
  exit 1
fi

# Provenance: the Cargo.lock `source` field is authoritative (cargo tree omits
# "registry" for default-registry deps). Source must be crates.io, version == pin.
LOCKBLOCK=$(grep -A3 '^name = "frozen-duckdb"$' "$SB/Cargo.lock" || true)
say "Cargo.lock block: $LOCKBLOCK"
LOCKVER=$(printf '%s' "$LOCKBLOCK" | grep '^version' | head -1 | cut -d'"' -f2)
LOCKSRC=$(printf '%s' "$LOCKBLOCK" | grep '^source' | head -1)
case "$LOCKSRC" in
  *registry*crates.io*) : ;;
  "") say "FAIL: no source line — frozen-duckdb is a path/git dep, not registry"; exit 5 ;;
  *) say "FAIL: provenance assertion — source is '$LOCKSRC', not crates.io"; exit 5 ;;
esac
if [ "$LOCKVER" != "2.0.3" ]; then
  say "FAIL: lockfile resolved frozen-duckdb $LOCKVER != pin 2.0.3"; exit 5
fi
# cargo tree provenance corroboration (§1 court precondition)
say "cargo tree -i frozen-duckdb-sys: $(cargo tree -i frozen-duckdb-sys 2>&1 | head -3 | tr '\n' ' ')"
say "provenance OK: registry source, lockfile version 2.0.3 == pin"

# Compile check (dependency-only compile; symbol-linking fallback tolerated)
say "running cargo check"
if ! cargo check 2>&1; then
  say "FAIL: cargo check exited non-zero against registry 2.0.3"
  exit 1
fi

# ---- (d) POST digests: real tree byte-identical ------------------------------
POST_FORK=$(find "$FORK" -maxdepth 3 -name Cargo.toml -exec shasum -a 256 {} + 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
if [ "$PRE_FORK" != "$POST_FORK" ]; then
  say "FAIL: restore-digest mismatch on $FORK (PRE=$PRE_FORK POST=$POST_FORK)"; exit 3
fi
say "POST_FORK digest=$POST_FORK (unchanged)"

say "COURT PASS: frozen-duckdb 2.0.3 resolves + compiles from crates.io with zero machine-local paths"
exit 0
