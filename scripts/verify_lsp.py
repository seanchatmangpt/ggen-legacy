#!/usr/bin/env python3
"""Independent deterministic verifier for the GL-LSP-001 bounded runtime."""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import os
import pathlib
import re
import sys
import unittest
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "evidence" / "lsp-reference" / "verification-report.json"
BASE_SHA = "70e599a599fedb7c62c965377cc2f80df1fa01ec"
SOURCE_GLOBS = (
    ".gitignore",
    "AGENTS.md",
    "pyproject.toml",
    "bin/ggen-lsp",
    "src/ggen_lsp/*.py",
    "tests/test_lsp_*.py",
    "scripts/verify_lsp.py",
    "tickets/GL-LSP-001.md",
    "docs/lsp/*.md",
)


def source_files() -> list[pathlib.Path]:
    files: set[pathlib.Path] = set()
    for pattern in SOURCE_GLOBS:
        files.update(path for path in ROOT.glob(pattern) if path.is_file())
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def verify_runtime_authority(paths: list[pathlib.Path]) -> dict[str, Any]:
    runtime_paths = [path for path in paths if path.as_posix().endswith("src/ggen_lsp/server.py") or path.as_posix().endswith("bin/ggen-lsp")]
    imports: set[str] = set()
    banned_calls: list[str] = []
    for path in runtime_paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.level == 0:
                    imports.add(node.module.split(".", 1)[0])
                else:
                    imports.add("ggen_lsp")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and (node.func.value.id, node.func.attr) in {
                    ("os", "system"),
                    ("os", "popen"),
                    ("subprocess", "run"),
                    ("subprocess", "Popen"),
                    ("socket", "socket"),
                }:
                    banned_calls.append(f"{path.relative_to(ROOT)}:{node.lineno}:{node.func.value.id}.{node.func.attr}")
    allowed_internal = {"ggen_lsp"}
    third_party = sorted(name for name in imports if name not in sys.stdlib_module_names and name not in allowed_internal)
    if third_party or banned_calls:
        raise RuntimeError(f"runtime authority violation: third_party={third_party}, banned_calls={banned_calls}")
    return {
        "status": "PASS",
        "stdlib_import_roots": sorted(imports - allowed_internal),
        "third_party_imports": third_party,
        "banned_actuation_calls": banned_calls,
    }


def compile_sources(paths: list[pathlib.Path]) -> list[str]:
    compiled: list[str] = []
    for path in paths:
        if path.suffix == ".py" or path == ROOT / "bin" / "ggen-lsp":
            compile(path.read_text(encoding="utf-8"), path.as_posix(), "exec")
            compiled.append(path.relative_to(ROOT).as_posix())
    return compiled


def run_suite() -> dict[str, Any]:
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"), pattern="test_lsp_*.py")
    names: list[str] = []

    def walk(node: unittest.TestSuite) -> None:
        for item in node:
            if isinstance(item, unittest.TestSuite):
                walk(item)
            else:
                names.append(item.id())

    walk(suite)
    stream = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    normalized = re.sub(r"Ran (\d+) tests? in [0-9.]+s", r"Ran \1 tests in <DURATION>", stream.getvalue())
    return {
        "tests": sorted(names),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "successful": result.wasSuccessful(),
        "normalized_output_sha256": hashlib.sha256(normalized.encode()).hexdigest(),
    }


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    authored = source_files()
    manifest = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size}
        for path in authored
    ]
    source_manifest_sha256 = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    authority = verify_runtime_authority(authored)
    compiled = compile_sources(authored)
    first = run_suite()
    second = run_suite()
    replay_match = first == second
    successful = first["successful"] and second["successful"] and replay_match

    report = {
        "schema": "ggen.legacy.lsp-verification-report/1",
        "ticket": "GL-LSP-001",
        "repository": "seanchatmangpt/ggen-legacy",
        "base_sha": BASE_SHA,
        "subject": {
            "source_manifest_sha256": source_manifest_sha256,
            "files": manifest,
        },
        "toolchain": {
            "implementation": "python-standard-library-only",
            "python": ".".join(map(str, sys.version_info[:3])),
            "third_party_dependencies": 0,
        },
        "authority_boundary": authority,
        "compile": {"status": "PASS", "compiled_paths": compiled},
        "execution": {
            "boundary": "real subprocess + stdin/stdout Content-Length framed JSON-RPC",
            "first": first,
            "second": second,
        },
        "negative_controls": [
            "malformed JSON recovers with -32700",
            "unknown method refuses with -32601",
            "incremental change refuses with -32602",
            "missing Content-Length exits 2 with typed transport refusal",
            "stdout remains frame-only",
        ],
        "replay": "REPLAY_MATCH" if replay_match else "REPLAY_DIFFERENCE",
        "claim_ceiling": "REFERENCE_CONFORMANT",
        "standing": "ALIVE" if successful else "BUILD_BROKEN",
        "exclusions": [
            "aggregate ggen-legacy repository crown",
            "Rust build compatibility",
            "MCP or A2A transports",
            "full language-spec conformance",
            "filesystem or network actuation",
            "release, production, certification, or sunset admission",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    REPORT.write_text(encoded, encoding="utf-8")
    print(f"standing={report['standing']}")
    print(f"tests={first['tests_run']}")
    print(f"replay={report['replay']}")
    print(f"source_manifest_sha256={source_manifest_sha256}")
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
