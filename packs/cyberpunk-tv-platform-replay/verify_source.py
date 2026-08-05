#!/usr/bin/env python3
"""Read-only verifier for the admitted cyberpunk television source corpus."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_DISPOSITIONS = {"PRESERVED", "SUBSUMED", "REPLACED", "ARCHIVED", "REFUSED"}


@dataclass(frozen=True)
class Check:
    check_id: str
    state: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"id": self.check_id, "state": self.state, "detail": self.detail}


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def b3sum(path: Path) -> str:
    executable = shutil.which("b3sum")
    if executable is None:
        raise RuntimeError("BLAKE3_TOOL_BLOCKED:b3sum")
    result = run([executable, str(path)])
    if result.returncode != 0:
        raise RuntimeError(f"BLAKE3_FAILED:{path}:{result.stderr.strip()}")
    return result.stdout.split()[0]


def source_repo_root(source: Path) -> Path:
    for candidate in (source, *source.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("SOURCE_GIT_ROOT_BLOCKED")


def resolve_required(source: Path, repo_root: Path, relative: str) -> Path:
    return repo_root / relative if relative.startswith(".github/") else source / relative


def query_contract(path: Path) -> list[str]:
    upper = path.read_text(encoding="utf-8").upper()
    failures: list[str] = []
    if "SELECT *" in upper:
        failures.append("implicit_projection")
    if ("SELECT" in upper or "CONSTRUCT" in upper) and "ORDER BY" not in upper:
        failures.append("missing_order")
    return failures


def canonical_root(entries: list[dict[str, Any]]) -> str:
    payload = "".join(f"{entry['path']}\0{entry['blake3']}\0{entry['bytes']}\n" for entry in entries).encode("utf-8")
    with tempfile.NamedTemporaryFile(prefix="cyberpunk-tv-source-", delete=True) as handle:
        handle.write(payload)
        handle.flush()
        return b3sum(Path(handle.name))


def write_early_report(output: Path, checks: list[Check], standing: str) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({
        "schema": "ggen-legacy.source-verification.v2",
        "source_authority_standing": standing,
        "implementation_standing": "UNKNOWN",
        "aggregate_standing": "UNKNOWN",
        "checks": [check.as_dict() for check in checks],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 2 if standing == "BLOCKED" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    checks: list[Check] = []
    if not source.is_dir():
        checks.append(Check("source-directory", "BLOCKED", str(source)))
        return write_early_report(output, checks, "BLOCKED")

    try:
        repo_root = source_repo_root(source)
    except RuntimeError as error:
        checks.append(Check("source-git-root", "BLOCKED", str(error)))
        return write_early_report(output, checks, "BLOCKED")

    contract = json.loads(args.contract.resolve().read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.resolve().read_text(encoding="utf-8"))
    expected_head = contract["source"]["head_sha"]

    head_result = run(["git", "rev-parse", "HEAD"], cwd=repo_root)
    observed_head = head_result.stdout.strip() if head_result.returncode == 0 else "UNKNOWN"
    head_state = "PASS" if observed_head == expected_head else ("BLOCKED" if observed_head == "UNKNOWN" else "FAIL")
    checks.append(Check("exact-source-head", head_state, f"observed={observed_head};expected={expected_head}"))

    ledger_head = ledger.get("source_head")
    checks.append(Check("ledger-source-head", "PASS" if ledger_head == expected_head else "FAIL", f"ledger={ledger_head};expected={expected_head}"))

    resolved_paths: list[tuple[str, Path]] = []
    missing: list[str] = []
    for relative in contract["required_paths"]:
        path = resolve_required(source, repo_root, relative)
        if path.exists():
            resolved_paths.append((relative, path))
        else:
            missing.append(relative)
    checks.append(Check("required-paths", "PASS" if not missing else "FAIL", f"present={len(resolved_paths)};missing={missing}"))

    try:
        with (source / "ggen.toml").open("rb") as handle:
            manifest = tomllib.load(handle)
        current_schema = all(key in manifest for key in ("project", "ontology", "generation", "validation"))
        validation = manifest.get("validation", {})
        valid_manifest = current_schema and validation.get("strict_mode") is True and bool(validation.get("shacl"))
        checks.append(Check("manifest-admission", "PASS" if valid_manifest else "FAIL", f"current_schema={current_schema};strict={validation.get('strict_mode')};shacl={validation.get('shacl')}"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        checks.append(Check("manifest-admission", "FAIL", str(error)))

    query_failures: dict[str, list[str]] = {}
    for path in sorted((source / "queries").glob("*.rq")):
        failures = query_contract(path)
        if failures:
            query_failures[path.name] = failures
    checks.append(Check("query-contract", "PASS" if not query_failures else "FAIL", json.dumps(query_failures, sort_keys=True)))

    capabilities = ledger.get("capabilities", [])
    defaults = ledger.get("defaults", {})
    identities = [item.get("id") for item in capabilities]
    dispositions = [item.get("disposition", defaults.get("disposition")) for item in capabilities]
    required_fields = ("id", "provenance", "contract", "equivalence", "verifier", "rationale")
    complete = all(all(item.get(field) for field in required_fields) for item in capabilities)
    ledger_valid = (
        len(capabilities) == ledger.get("summary", {}).get("count")
        and len(set(identities)) == len(identities)
        and all(disposition in ALLOWED_DISPOSITIONS for disposition in dispositions)
        and ledger.get("summary", {}).get("unknown_dispositions") == 0
        and complete
    )
    checks.append(Check("capability-ledger", "PASS" if ledger_valid else "FAIL", f"count={len(capabilities)};unique={len(set(identities))};complete={complete};unknown_dispositions={ledger.get('summary', {}).get('unknown_dispositions')}"))

    generated_authority = contract.get("generated_outputs_are_authority")
    checks.append(Check("generated-authority", "PASS" if generated_authority is False else "FAIL", f"generated_outputs_are_authority={generated_authority}"))

    entries: list[dict[str, Any]] = []
    root = "UNKNOWN"
    try:
        for relative, path in sorted(resolved_paths):
            if path.is_file():
                entries.append({"path": relative, "bytes": path.stat().st_size, "blake3": b3sum(path)})
        root = canonical_root(entries)
        checks.append(Check("source-content-address", "PASS", f"root={root};artifacts={len(entries)}"))
    except RuntimeError as error:
        checks.append(Check("source-content-address", "BLOCKED", str(error)))

    failed = [check for check in checks if check.state == "FAIL"]
    blocked = [check for check in checks if check.state == "BLOCKED"]
    source_standing = "PARTIAL_ALIVE" if not failed and not blocked else ("BLOCKED" if blocked and not failed else "BUILD_BROKEN")
    report = {
        "schema": "ggen-legacy.source-verification.v2",
        "subject": contract["subject"],
        "source": {
            "repository": contract["source"]["repository"],
            "base_sha": contract["source"]["base_sha"],
            "expected_head_sha": expected_head,
            "observed_head_sha": observed_head,
            "path": str(source),
            "content_root": root,
            "artifacts": entries,
        },
        "source_authority_standing": source_standing,
        "implementation_standing": "UNKNOWN",
        "aggregate_standing": "UNKNOWN",
        "checks": [check.as_dict() for check in checks],
        "unexecuted": [
            "double-manufacture", "rust-tests", "wasm-build", "browser-build", "browser-e2e",
            "escrow-positive-negative", "tree-receipt", "replay", "independent-crown"
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(output), "source_authority_standing": source_standing, "aggregate_standing": "UNKNOWN", "failed": len(failed), "blocked": len(blocked)}))
    return 0 if source_standing == "PARTIAL_ALIVE" else (2 if blocked and not failed else 1)


if __name__ == "__main__":
    sys.exit(main())
