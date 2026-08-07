#!/usr/bin/env python3
"""Record exact-head CI command execution into a durable JSON receipt."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

TAIL_LIMIT = 8_000


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"REFUSED:RECEIPT_NOT_INITIALIZED path={path}")
    return json.loads(path.read_text(encoding="utf-8"))


def store(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def initialize(args: argparse.Namespace) -> int:
    report = {
        "schema": args.schema,
        "subject": {
            "repository": os.environ.get("GITHUB_REPOSITORY", "local/ggen-legacy"),
            "head": args.head,
            "workflow": os.environ.get("GITHUB_WORKFLOW"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
        },
        "claim_ceiling": args.claim_ceiling,
        "checks": [],
        "failures": [],
        "standing": "UNKNOWN",
        "replay": {"commands": []},
    }
    store(args.report, report)
    return 0


def execute(args: argparse.Namespace) -> int:
    report = load(args.report)
    if not args.command:
        raise SystemExit("REFUSED:EMPTY_COMMAND")
    started = time.monotonic()
    completed = subprocess.run(args.command, text=True, capture_output=True, check=False)
    elapsed_ms = round((time.monotonic() - started) * 1000)
    check: dict[str, Any] = {
        "id": args.id,
        "command": args.command,
        "exit_code": completed.returncode,
        "elapsed_ms": elapsed_ms,
        "passed": completed.returncode == 0,
    }
    if completed.stdout:
        check["stdout_tail"] = completed.stdout[-TAIL_LIMIT:]
        sys.stdout.write(completed.stdout)
    if completed.stderr:
        check["stderr_tail"] = completed.stderr[-TAIL_LIMIT:]
        sys.stderr.write(completed.stderr)
    if completed.returncode != 0:
        check["failure"] = "CHECK_FAILED"
        report["failures"].append(
            {"id": args.id, "failure": "CHECK_FAILED", "exit_code": completed.returncode}
        )
    report["checks"].append(check)
    report["replay"]["commands"].append(args.command)
    report["standing"] = "BUILD_BROKEN" if report["failures"] else "PARTIAL_ALIVE"
    store(args.report, report)
    return completed.returncode


def finalize(args: argparse.Namespace) -> int:
    report = load(args.report)
    report["standing"] = "BUILD_BROKEN" if report["failures"] else "ALIVE"
    store(args.report, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["standing"] == "ALIVE" else 1


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="operation", required=True)

    init = sub.add_parser("init")
    init.add_argument("--report", type=Path, required=True)
    init.add_argument("--schema", required=True)
    init.add_argument("--head", required=True)
    init.add_argument("--claim-ceiling", required=True)
    init.set_defaults(function=initialize)

    run = sub.add_parser("run")
    run.add_argument("--report", type=Path, required=True)
    run.add_argument("--id", required=True)
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(function=execute)

    finish = sub.add_parser("finalize")
    finish.add_argument("--report", type=Path, required=True)
    finish.set_defaults(function=finalize)
    return root


def main() -> int:
    args = parser().parse_args()
    if getattr(args, "command", None) and args.command[0] == "--":
        args.command = args.command[1:]
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
