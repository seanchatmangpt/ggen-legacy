#!/usr/bin/env python3
"""observe_contract -- first (read-only) tool of the ggen-legacy-mcp 7-tool surface
proposed in planning/v26.8.20/README.md.

Captures a real, current-behavior baseline (Feathers-style characterization, not a
spec of intended behavior) for one file or one command against a target repo, and
writes a `ggen.legacy.observe.v1` contract JSON -- the schema-naming convention
already used by this repo's real receipts (see evidence/foundry-provenance-verifier.json:
"schema": "ggen.legacy.foundry.provenance.verifier.v1").

Read-only w.r.t. the observed target: never writes into --repo, only into --out.
Hashing uses the real `b3sum` binary on disk (BLAKE3, this repo's own convention per
docs/src/07-verification.md) via subprocess -- no mocked/stubbed hash function.

Usage:
  python3 observe_contract.py --repo <path> --target <relpath-under-repo> \
      [--command "<shell command run with cwd=repo>"] --out <dir>

Exit 0 on a successful (possibly-negative, e.g. file absent) observation captured;
exit 1 on an operational error (repo missing, b3sum missing, command timeout).
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def git_head(repo: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True,
            timeout=10, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return None


def b3sum_file(path: Path) -> str:
    out = subprocess.run(
        ["b3sum", "--no-names", str(path)], capture_output=True, text=True,
        timeout=30, check=True,
    )
    return out.stdout.strip()


def b3sum_bytes(data: bytes) -> str:
    out = subprocess.run(
        ["b3sum", "--no-names"], input=data, capture_output=True,
        timeout=30, check=True,
    )
    return out.stdout.decode().strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="target repo root (read-only)")
    ap.add_argument("--target", required=True, help="path under --repo to observe")
    ap.add_argument("--command", default=None, help="optional shell command, cwd=repo, captured as behavior")
    ap.add_argument("--out", required=True, help="directory to write the contract JSON into")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"ERROR: --repo {repo} is not a directory", file=sys.stderr)
        return 1
    try:
        subprocess.run(["b3sum", "--version"], capture_output=True, timeout=5, check=True)
    except Exception as e:
        print(f"ERROR: b3sum not usable: {e}", file=sys.stderr)
        return 1

    target_path = repo / args.target
    file_exists = target_path.exists()
    file_hash = b3sum_file(target_path) if file_exists and target_path.is_file() else None
    file_size = target_path.stat().st_size if file_exists and target_path.is_file() else None

    command_result = None
    if args.command:
        try:
            proc = subprocess.run(
                args.command, shell=True, cwd=repo, capture_output=True,
                text=True, timeout=180,
            )
            combined = (proc.stdout + proc.stderr).encode()
            command_result = {
                "command": args.command,
                "exit_code": proc.returncode,
                "stdout_stderr_b3": b3sum_bytes(combined),
                "stdout_stderr_bytes": len(combined),
            }
        except subprocess.TimeoutExpired:
            print("ERROR: command timed out after 180s", file=sys.stderr)
            return 1

    contract = {
        "schema": "ggen.legacy.observe.v1",
        "repo": str(repo),
        "target": args.target,
        "target_exists": file_exists,
        "target_b3": file_hash,
        "target_size_bytes": file_size,
        "git_head": git_head(repo),
        "command_result": command_result,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "nonclaims": [
            "correctness of the observed behavior",
            "that this baseline is complete coverage of the target's real behavior",
            "any standing (ALIVE/PARTIAL_ALIVE/UNKNOWN/REFUSED) for the target",
        ],
    }
    # contract_id: BLAKE3 of the canonical JSON (sorted keys, no whitespace ambiguity),
    # excluding observed_at so re-running against unchanged state reproduces the same id
    # modulo the timestamp -- included separately so callers can dedupe by content.
    id_basis = {k: v for k, v in contract.items() if k != "observed_at"}
    canonical = json.dumps(id_basis, sort_keys=True, separators=(",", ":")).encode()
    contract["contract_id"] = b3sum_bytes(canonical)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{contract['contract_id']}.json"
    out_file.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")

    print(json.dumps(contract, indent=2, sort_keys=True))
    print(f"\nwrote {out_file}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
