#!/usr/bin/env bash
# guard-verifier-proof.sh — the ggen-legacy pack-proof gate.
#
# Makes "the generated proof suite for tools/v26.8.1's own binary passes" a
# checkable fact from repo state, not a claim about a session that once ran
# it: re-syncs tools/ggen-verifier-cli-verify (a real, cross-repo consumer of
# the separate ~/ggen repo's chicago-tdd-tools-pack), verifies the sync's own
# cryptographic receipt (BLAKE3 chain hash + signature, `ggen receipt
# verify`), verifies the re-sync was idempotent (byte-identical generated
# tests/ and docs/), and runs its full test suite (the generated CliHarness
# proofs against the real, just-fixed ggen-v26-8-1-verifier binary, plus
# chicago-tdd-tools-pack's own 9 bundled receiptctl-targeted demo facts
# shared by every consumer of the pack -- a known quirk, not something this
# script works around beyond putting receiptctl on PATH).
#
# Uses ~/ggen's release ggen binary if present (fast path), else its debug
# one, else builds it. Any sync refusal, any test failure, or any
# regeneration diff fails this script.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -z "${GGEN_REPO:-}" ]]; then
    echo "guard-verifier-proof: FAIL — GGEN_REPO is not set." >&2
    echo "  This gate cross-verifies against a sibling checkout of seanchatmangpt/ggen" >&2
    echo "  (for chicago-tdd-tools-pack and the ggen/receiptctl binaries)." >&2
    echo "  Set it to that checkout's path, e.g.:" >&2
    echo "    GGEN_REPO=/path/to/ggen $0" >&2
    exit 1
fi
if [[ ! -d "$GGEN_REPO" ]]; then
    echo "guard-verifier-proof: FAIL — GGEN_REPO=$GGEN_REPO does not exist." >&2
    exit 1
fi
CONSUMER="$REPO_ROOT/tools/ggen-verifier-cli-verify"
V26_DIR="$REPO_ROOT/tools/v26.8.1"

echo "guard-verifier-proof: building tools/v26.8.1 binaries..."
(cd "$V26_DIR" && cargo build -q --bin ggen-v26-8-1-verifier --bin subsystem_verifier --bin project_coverage)

echo "guard-verifier-proof: building receiptctl example binary (for the pack's shared demo facts)..."
(cd "$GGEN_REPO/examples/receiptctl" && cargo build -q --bin receiptctl)

GGEN_BIN="$GGEN_REPO/target/release/ggen"
if [[ ! -x "$GGEN_BIN" ]]; then
    GGEN_BIN="$GGEN_REPO/target/debug/ggen"
fi
if [[ ! -x "$GGEN_BIN" ]]; then
    echo "guard-verifier-proof: building ggen binary (debug) in $GGEN_REPO..."
    (cd "$GGEN_REPO" && cargo build -q -p ggen-cli-lib --bin ggen)
    GGEN_BIN="$GGEN_REPO/target/debug/ggen"
fi

export PATH="$V26_DIR/target/debug:$GGEN_REPO/examples/receiptctl/target/debug:$PATH"

echo "guard-verifier-proof: sync ${CONSUMER} (binary: ${GGEN_BIN})"
(cd "$CONSUMER" && "$GGEN_BIN" sync run >/dev/null)

echo "guard-verifier-proof: verifying sync receipt (chain hash + signature)"
receipt_out="$(cd "$CONSUMER" && "$GGEN_BIN" receipt verify 2>/dev/null)"
receipt_valid="$(jq -r '.valid' <<<"$receipt_out")"
receipt_signed="$(jq -r '.signed' <<<"$receipt_out")"
receipt_sig_valid="$(jq -r '.signature_valid' <<<"$receipt_out")"
if [[ "$receipt_valid" != "true" || "$receipt_signed" != "true" || "$receipt_sig_valid" != "true" ]]; then
    echo "guard-verifier-proof: FAIL — receipt not valid/signed: ${receipt_out}" >&2
    exit 1
fi

echo "guard-verifier-proof: verifying idempotent regeneration"
snapshot="$(mktemp -d)"
trap 'rm -rf "$snapshot"' EXIT
cp -R "$CONSUMER/tests" "$snapshot/tests"
cp -R "$CONSUMER/docs" "$snapshot/docs"
(cd "$CONSUMER" && "$GGEN_BIN" sync run >/dev/null)
diff -rq "$snapshot/tests" "$CONSUMER/tests"
diff -rq "$snapshot/docs" "$CONSUMER/docs"
rm -rf "$snapshot"
trap - EXIT

echo "guard-verifier-proof: running ${CONSUMER} test suite"
(cd "$CONSUMER" && cargo test -q)

echo "guard-verifier-proof: OK (sync clean, idempotent, receipt valid+signed, all generated proofs pass)"
