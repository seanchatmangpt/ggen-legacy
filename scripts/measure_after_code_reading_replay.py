#!/usr/bin/env python3
"""Measure one clean replay of the After Code Reading strategic corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "ggen.legacy.after-code-reading.replay.v1"
SOURCE_FILES = (
    "AGENTS.md",
    "RELEASE_CONTROL.md",
    "README.md",
    "authority/after-code-reading.json",
    "product/AFTER_CODE_READING.md",
    "product/PRD.md",
    "architecture/AFTER_CODE_READING_ARCHITECTURE.md",
    "architecture/ARD.md",
    "governance/after-code-reading-review-standard.md",
    "governance/claims-register.md",
    "docs/src/15-after-code-reading.md",
    "docs/src/SUMMARY.md",
    "tickets/TICKET-012-after-code-reading-pivot.md",
)


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def digest_file_set(root: Path, relatives: list[str] | tuple[str, ...]) -> str:
    hasher = hashlib.sha256()
    for relative in sorted(relatives):
        data = (root / relative).read_bytes()
        path = relative.encode("utf-8")
        hasher.update(len(path).to_bytes(8, "little"))
        hasher.update(path)
        hasher.update(len(data).to_bytes(8, "little"))
        hasher.update(data)
    return hasher.hexdigest()


def canonical_digest(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    errors: list[str] = []
    revision = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    if revision != args.expected_revision:
        errors.append(f"EXACT_REVISION_MISMATCH:{revision}:{args.expected_revision}")

    missing = [relative for relative in SOURCE_FILES if not (root / relative).is_file()]
    errors.extend(f"SOURCE_FILE_MISSING:{relative}" for relative in missing)

    book_root = root / "docs/book"
    book_files = [
        path.relative_to(root).as_posix()
        for path in book_root.rglob("*")
        if path.is_file()
    ] if book_root.is_dir() else []
    if "docs/book/index.html" not in book_files:
        errors.append("MDBOOK_INDEX_MISSING")
    if "docs/book/print.html" not in book_files:
        errors.append("MDBOOK_PRINT_MISSING")

    verifier_path = root / "evidence/local-docs-verifier.json"
    if not verifier_path.is_file():
        errors.append("LOCAL_DOCS_VERIFIER_MISSING")
        verifier: dict[str, Any] = {}
    else:
        try:
            verifier = json.loads(verifier_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            verifier = {}
            errors.append(f"LOCAL_DOCS_VERIFIER_INVALID:{exc}")
    if verifier and verifier.get("errors"):
        errors.append("LOCAL_DOCS_VERIFIER_ERRORS")

    tracked_diff = git(root, "diff", "--name-only")
    if tracked_diff:
        errors.append(f"TRACKED_SOURCE_DRIFT:{tracked_diff}")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "subject": {
            "repository": "seanchatmangpt/ggen-legacy",
            "scope": "after-code-reading-strategic-corpus",
            "release": "v26.8.1",
            "revision": revision,
            "tree": tree,
        },
        "observer": "scripts/measure_after_code_reading_replay.py",
        "final_admission_allowed": False,
        "source_set_sha256": digest_file_set(root, SOURCE_FILES) if not missing else None,
        "authority_sha256": hashlib.sha256(
            (root / "authority/after-code-reading.json").read_bytes()
        ).hexdigest() if (root / "authority/after-code-reading.json").is_file() else None,
        "book_sha256": digest_file_set(root, book_files) if book_files else None,
        "book_file_count": len(book_files),
        "local_docs_verifier_sha256": hashlib.sha256(verifier_path.read_bytes()).hexdigest()
        if verifier_path.is_file()
        else None,
        "local_docs_verifier_standing": verifier.get("standing"),
        "local_docs_verifier_errors": verifier.get("errors", []),
        "tracked_source_clean": not bool(tracked_diff),
        "errors": errors,
        "standing": "PARTIAL_ALIVE" if not errors else "BLOCKED",
        "reason": "INDEPENDENT_CROWN_REQUIRED" if not errors else "REPLAY_NONCONFORMANCE",
    }
    report["receipt_sha256"] = canonical_digest(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"standing": report["standing"], "errors": errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
