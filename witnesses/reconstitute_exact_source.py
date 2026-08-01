#!/usr/bin/env python3
"""Reconstitute one exact Git source object and emit a non-promoting receipt."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def blake3_hex(data: bytes) -> str:
    try:
        import blake3  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError("blake3==1.0.9 is required") from exc
    return blake3.blake3(data).hexdigest()


def run(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def remote_url(repository: str) -> str:
    token = os.environ.get("RECONSTITUTION_READER_TOKEN", "").strip()
    if token:
        return f"https://x-access-token:{token}@github.com/{repository}.git"
    return f"https://github.com/{repository}.git"


def doctrine_inventory(checkout: Path) -> list[str]:
    candidates = [
        "AGENTS.md",
        "CLAUDE.md",
        "CONSTITUTION.md",
        ".claude/rules/_core/absolute.md",
        ".claude/rules/cognition-contracts.md",
    ]
    return [path for path in candidates if (checkout / path).is_file()]


def emit_blocked(args: argparse.Namespace, output: Path, reason: str, stderr_tail: str) -> int:
    core = {
        "schema": "ggen-legacy.source-reconstitution.receipt/v1",
        "repository": args.repository,
        "source_id": args.source_id,
        "sha": args.sha,
        "disposition": args.disposition,
        "product_reconstitution": args.product_reconstitution == "true",
        "standing": "BLOCKED",
        "reason": reason,
        "stderr_tail": stderr_tail[-2000:],
        "direct_actuation": False,
        "source_tree": None,
        "tracked_paths": None,
        "doctrine_files": [],
    }
    core["receipt_digest"] = f"blake3:{blake3_hex(canonical_bytes(core))}"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_bytes(core) + b"\n")
    print(json.dumps(core, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--disposition", required=True)
    parser.add_argument("--pull-request", type=int, required=True)
    parser.add_argument("--product-reconstitution", choices=("true", "false"), required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    checkout = args.workspace / args.source_id
    if checkout.exists():
        shutil.rmtree(checkout)
    checkout.mkdir(parents=True)
    run(["git", "init", "--quiet"], cwd=checkout)
    run(["git", "remote", "add", "origin", remote_url(args.repository)], cwd=checkout)
    fetched = run(["git", "fetch", "--quiet", "--depth=1", "origin", args.sha], cwd=checkout, check=False)
    if fetched.returncode != 0 and args.disposition in {"ACTIVE_CANDIDATE", "PRESERVED_CANDIDATE"}:
        fetched = run(
            ["git", "fetch", "--quiet", "--depth=1", "origin", f"refs/pull/{args.pull_request}/head"],
            cwd=checkout,
            check=False,
        )
    if fetched.returncode != 0:
        return emit_blocked(args, args.output, "EXACT_SOURCE_FETCH_BLOCKED", fetched.stderr)

    run(["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=checkout)
    observed_sha = run(["git", "rev-parse", "HEAD"], cwd=checkout).stdout.strip()
    if observed_sha != args.sha:
        return emit_blocked(args, args.output, "EXACT_SOURCE_IDENTITY_MISMATCH", observed_sha)

    tree = run(["git", "rev-parse", "HEAD^{tree}"], cwd=checkout).stdout.strip()
    raw_paths = subprocess.check_output(["git", "ls-tree", "-r", "-z", "--name-only", "HEAD"], cwd=checkout)
    tracked_paths = sum(1 for item in raw_paths.split(b"\0") if item)
    status = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=checkout).stdout
    if status:
        return emit_blocked(args, args.output, "RECONSTITUTED_TREE_DIRTY", status)

    core = {
        "schema": "ggen-legacy.source-reconstitution.receipt/v1",
        "repository": args.repository,
        "source_id": args.source_id,
        "sha": observed_sha,
        "disposition": args.disposition,
        "product_reconstitution": args.product_reconstitution == "true",
        "standing": "ALIVE",
        "reason": None,
        "stderr_tail": "",
        "direct_actuation": False,
        "source_tree": tree,
        "tracked_paths": tracked_paths,
        "doctrine_files": doctrine_inventory(checkout),
        "validation_executed": False,
        "open_obligations": [
            "repository-owned validation ladder",
            "generated-output replay",
            "negative falsifier execution",
            "ggen receipt verification",
            "clean-room consequence replay",
        ],
    }
    core["receipt_digest"] = f"blake3:{blake3_hex(canonical_bytes(core))}"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(core) + b"\n")
    print(json.dumps(core, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
