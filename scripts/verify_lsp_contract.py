#!/usr/bin/env python3
"""Independent receiver verifier for the ggen-manufactured LSP contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

SCHEMA = "ggen.lsp.receiver-report/1"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rust_constants(source: str, name: str) -> list[str]:
    match = re.search(rf"pub const {re.escape(name)}: &\[&str\] = &\[(.*?)\];", source, re.S)
    if match is None:
        return []
    return re.findall(r'"((?:[^"\\]|\\.)*)"', match.group(1))


def snake(capability: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", capability).lower()


def verify(root: pathlib.Path) -> dict[str, Any]:
    authority = root / "authority/lsp-contract.json"
    generated = root / "src/generated_contract.rs"
    backend_path = root / "src/backend.rs"
    capabilities_path = root / "src/capabilities.rs"
    analysis_path = root / "src/analysis.rs"
    required = [authority, generated, backend_path, capabilities_path, analysis_path]
    findings = [f"MISSING:{path.relative_to(root)}" for path in required if not path.is_file()]
    if findings:
        return {"schema": SCHEMA, "standing": "BUILD_BROKEN", "findings": findings}

    contract = json.loads(authority.read_text(encoding="utf-8"))
    generated_source = generated.read_text(encoding="utf-8")
    backend = backend_path.read_text(encoding="utf-8")
    capabilities = capabilities_path.read_text(encoding="utf-8")
    analysis = analysis_path.read_text(encoding="utf-8")

    if contract.get("schema") != "ggen.lsp.contract/1":
        findings.append("CONTRACT_SCHEMA_MISMATCH")
    if contract.get("legacy", {}).get("repository") != "seanchatmangpt/ggen-legacy":
        findings.append("RECEIVER_IDENTITY_MISMATCH")

    methods = [row["method"] for row in contract.get("methods", [])]
    surfaces = [row["extension"] for row in contract.get("surfaces", [])]
    diagnostics = [row["code"] for row in contract.get("diagnostics", [])]
    if methods != rust_constants(generated_source, "REQUIRED_METHODS"):
        findings.append("GENERATED_METHOD_DRIFT")
    if surfaces != rust_constants(generated_source, "REQUIRED_SURFACES"):
        findings.append("GENERATED_SURFACE_DRIFT")
    if diagnostics != rust_constants(generated_source, "DECLARED_DIAGNOSTICS"):
        findings.append("GENERATED_DIAGNOSTIC_DRIFT")

    for row in contract.get("methods", []):
        handler = row.get("legacy_handler")
        if handler != "framework" and not re.search(
            rf"\basync\s+fn\s+{re.escape(handler)}\b", backend
        ):
            findings.append(f"HANDLER_ABSENT:{row['method']}:{handler}")

    for capability in sorted(
        {row.get("capability") for row in contract.get("methods", []) if row.get("capability")}
    ):
        capability_sources = capabilities + backend
        dynamic_type_hierarchy = (
            capability == "typeHierarchyProvider"
            and "textDocument/prepareTypeHierarchy" in backend
            and "register_capability" in backend
        )
        if (
            capability not in capability_sources
            and snake(capability) not in capability_sources
            and not dynamic_type_hierarchy
        ):
            findings.append(f"CAPABILITY_ABSENT:{capability}")

    for extension in surfaces:
        quoted = f'"{extension}"'
        if quoted not in analysis and quoted not in backend:
            findings.append(f"SURFACE_ABSENT:{extension}")

    for row in contract.get("diagnostics", []):
        diagnostic_sources = analysis + generated_source
        if row.get("owner") in {"legacy", "both"} and row["code"] not in diagnostic_sources:
            findings.append(f"DIAGNOSTIC_ABSENT:{row['code']}")

    forbidden = ["std::process::Command", "reqwest::", "TcpStream", "UdpSocket"]
    combined = backend + analysis + capabilities
    for marker in forbidden:
        if marker in combined:
            findings.append(f"AMBIENT_ACTUATION:{marker}")

    source_manifest = {
        str(path.relative_to(root)): sha256(path)
        for path in required
    }
    return {
        "schema": SCHEMA,
        "contract_schema": contract.get("schema"),
        "contract_version": contract.get("version"),
        "method_count": len(methods),
        "surface_count": len(surfaces),
        "diagnostic_count": len(diagnostics),
        "source_manifest": source_manifest,
        "findings": sorted(set(findings)),
        "standing": "ALIVE" if not findings else "BUILD_BROKEN",
        "claim_ceiling": "INDEPENDENT_RECEIVER_SOURCE_CONTRACT_ONLY",
        "rust_execution": "BLOCKED_TOOLCHAIN_UNAVAILABLE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=pathlib.Path)
    args = parser.parse_args()
    report = verify(args.root.resolve())
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8")
    sys.stdout.write(encoded)
    return 0 if report["standing"] == "ALIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
