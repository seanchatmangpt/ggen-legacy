#!/usr/bin/env python3
"""Fast exact-head CI admission and heavy-lane routing for ggen-legacy."""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

LANE_RULES: dict[str, dict[str, tuple[str, ...]]] = {
    "assurance_deep": {
        "include": (
            "AGENTS.md",
            "README.md",
            "RELEASE_CONTROL.md",
            "ggen.toml",
            "product/**",
            "architecture/**",
            "strategy/**",
            "docs/**",
            "governance/**",
            "security/**",
            "operations/**",
            "procurement/**",
            "authority/**",
            "foundry/**",
            "ontology/**",
            "templates/**",
            "packs/ggen-legacy-assurance-pack/**",
            "appliance/**",
            "schemas/**",
            "fixtures/**",
            "projects/001/**",
            "scripts/verify_docs.py",
            "scripts/verify_foundry_provenance.py",
            "scripts/verify_foundry_bootstrap.py",
            "scripts/verify_offline_transport.py",
            ".github/workflows/verify-docs.yml",
        ),
        "exclude": (
            "authority/lsp-contract.json",
            "docs/lsp/**",
            "schemas/migration-manifest.schema.json",
        ),
    },
    "migration_deep": {
        "include": (
            "migrations/ggen-v26.8.1/**",
            "scripts/verify_ggen_v26_8_1_migration.py",
            "schemas/migration-manifest.schema.json",
        ),
        "exclude": (),
    },
    "lsp_runtime": {
        "include": (
            "Cargo.toml",
            "Cargo.lock",
            "rust-toolchain.toml",
            "src/**",
            "tests/**",
            "authority/lsp-contract.json",
            "docs/lsp/**",
            "tickets/GL-LSP-001.md",
            "scripts/verify_lsp_contract.py",
            ".github/workflows/gl-lsp-001-runtime.yml",
        ),
        "exclude": ("scripts/tests/test_ci_errc.py",),
    },
    "autonomic_crown": {
        "include": (
            "autonomic/**",
            "fixtures/autonomic/**",
            "scripts/autonomic_finish.py",
            "scripts/verify_autonomic_finish.py",
            "scripts/run_autonomic_crown.py",
            "tickets/GL-AUTO-001.md",
            "evidence/autonomic/**",
            ".github/workflows/autonomic-crown.yml",
        ),
        "exclude": (),
    },
    "cyberpunk_replay": {
        "include": (
            "packs/cyberpunk-tv-platform-replay/**",
            "tickets/TV-001-cyberpunk-platform-source-admission.md",
            ".github/workflows/cyberpunk-tv-replay.yml",
        ),
        "exclude": (),
    },
    "nasa_replay": {
        "include": (
            "packs/nasa-dark-mode-replay/**",
            "tickets/TV-002-nasa-dark-mode-source-admission.md",
            ".github/workflows/nasa-dark-mode-replay.yml",
        ),
        "exclude": (),
    },
}

ERRC = {
    "eliminate": [
        "deep cross-repository assurance on unrelated pull requests",
        "migration reconstruction on unrelated pull requests",
    ],
    "reduce": [
        "heavy execution frequency to changes owned by each evidence lane",
        "unbounded time-to-first-falsifier",
    ],
    "raise": [
        "universal exact-head authority validation",
        "typed failure visibility and deterministic routing evidence",
    ],
    "create": [
        "machine-readable fast-gate receipt",
        "replayable changed-file to evidence-lane classification",
    ],
}


def _matches(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def classify_path(path: str) -> list[str]:
    lanes: list[str] = []
    for lane, rules in LANE_RULES.items():
        if _matches(path, rules["include"]) and not _matches(path, rules["exclude"]):
            lanes.append(lane)
    return lanes


def classify_paths(paths: Iterable[str]) -> dict[str, list[str]]:
    result = {lane: [] for lane in LANE_RULES}
    result["fast_only"] = []
    for path in sorted(set(paths)):
        lanes = classify_path(path)
        if not lanes:
            result["fast_only"].append(path)
        for lane in lanes:
            result[lane].append(path)
    return result


def git_changed_files(root: Path, base: str, head: str) -> list[str]:
    if base and base != head:
        command = ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base}...{head}"]
    else:
        command = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", head]
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "CHANGED_FILE_DISCOVERY_FAILED: "
            + (completed.stderr.strip() or completed.stdout.strip() or str(command))
        )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def validate_structured_files(root: Path, changed: Iterable[str]) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for rel in sorted(set(changed)):
        path = root / rel
        if not path.is_file():
            continue
        try:
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif path.suffix == ".toml":
                tomllib.loads(path.read_text(encoding="utf-8"))
            elif rel == "foundry/bootstrap.yaml":
                # This repository's admitted bootstrap carrier is JSON encoded in .yaml.
                json.loads(path.read_text(encoding="utf-8"))
            else:
                continue
            checks.append({"id": f"parse:{rel}", "passed": True})
        except Exception as exc:  # exact parse failure is preserved in the receipt
            checks.append(
                {
                    "id": f"parse:{rel}",
                    "passed": False,
                    "failure": "STRUCTURED_FILE_INVALID",
                    "detail": str(exc),
                }
            )
    return checks


def run_check(root: Path, check_id: str, command: list[str]) -> dict[str, object]:
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed_ms = round((time.monotonic() - started) * 1000)
    result: dict[str, object] = {
        "id": check_id,
        "command": command,
        "exit_code": completed.returncode,
        "elapsed_ms": elapsed_ms,
        "passed": completed.returncode == 0,
    }
    if completed.stdout:
        result["stdout_tail"] = completed.stdout[-4000:]
    if completed.stderr:
        result["stderr_tail"] = completed.stderr[-4000:]
    if completed.returncode != 0:
        result["failure"] = "CHECK_FAILED"
    return result


def write_github_outputs(path: Path, lanes: dict[str, list[str]], standing: str) -> None:
    lines = [f"standing={standing}"]
    for lane in LANE_RULES:
        lines.append(f"{lane}={'true' if lanes[lane] else 'false'}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary(report: dict[str, object]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    lanes = report["routing"]
    checks = report["checks"]
    with Path(summary_path).open("a", encoding="utf-8") as handle:
        handle.write("## ggen-legacy ERRC 80/20 receipt\n\n")
        handle.write(f"**Standing:** `{report['standing']}`  \n")
        handle.write(f"**Changed files:** `{len(report['changed_files'])}`  \n")
        handle.write(
            "**Deep lanes:** "
            + ", ".join(
                f"`{lane}`" for lane in LANE_RULES if lanes.get(lane)
            )
            + "\n\n"
        )
        handle.write("| Check | Exit | Elapsed |\n|---|---:|---:|\n")
        for check in checks:
            handle.write(
                f"| `{check['id']}` | {check.get('exit_code', 0)} | "
                f"{check.get('elapsed_ms', 0)} ms |\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base", default="")
    parser.add_argument("--head", required=True)
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--skip-verifiers", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        changed = args.changed_file or git_changed_files(root, args.base, args.head)
        discovery_error = None
    except RuntimeError as exc:
        changed = []
        discovery_error = str(exc)

    routing = classify_paths(changed)
    checks = validate_structured_files(root, changed)
    if discovery_error:
        checks.append(
            {
                "id": "changed-file-discovery",
                "passed": False,
                "failure": "CHANGED_FILE_DISCOVERY_FAILED",
                "detail": discovery_error,
            }
        )

    if not args.skip_verifiers:
        checks.append(
            run_check(
                root,
                "document-authority",
                [sys.executable, "scripts/verify_docs.py", "--strict"],
            )
        )
        if routing["lsp_runtime"]:
            checks.append(
                run_check(
                    root,
                    "lsp-contract",
                    [
                        sys.executable,
                        "scripts/verify_lsp_contract.py",
                        "--root",
                        ".",
                        "--report",
                        "/tmp/ggen-legacy-lsp-contract-fast.json",
                    ],
                )
            )

    failed = [check for check in checks if not check.get("passed", False)]
    standing = "ALIVE" if not failed else "BUILD_BROKEN"
    report: dict[str, object] = {
        "schema": "ggen.legacy.ci.errc.receipt.v1",
        "subject": {
            "repository": os.environ.get("GITHUB_REPOSITORY", "local/ggen-legacy"),
            "base": args.base or None,
            "head": args.head,
            "workflow": os.environ.get("GITHUB_WORKFLOW"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
        },
        "errc": ERRC,
        "changed_files": sorted(set(changed)),
        "routing": routing,
        "checks": checks,
        "failures": failed,
        "standing": standing,
        "claim_ceiling": "EXACT_HEAD_FAST_AUTHORITY_AND_ROUTING_ONLY",
        "replay": {
            "command": (
                f"python3 scripts/ci_errc.py --base {args.base or '<base>'} "
                f"--head {args.head} --report evidence/ci/errc-fast.json"
            )
        },
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.github_output:
        write_github_outputs(args.github_output, routing, standing)
    write_summary(report)
    return 0 if standing == "ALIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
