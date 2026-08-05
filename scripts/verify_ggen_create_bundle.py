#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Any

MANIFEST_SCHEMA = "ggen-create-legacy-manifest/1"
CONTRACT_SCHEMA = "ggen-create-to-ggen-legacy-contract/1"
RECEIPT_SCHEMA = "ggen-create-legacy-receipt/1"
RECEIVER_SCHEMA = "ggen-legacy-ggen-create-receiver/1"
REQUIRED_UNKNOWN = (
    "ggen_execution",
    "behavioral_equivalence",
    "release",
    "sunset",
)
EXCLUDED_DIRS = {
    ".git",
    ".ggen-create",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "node_modules",
    "target",
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def digest_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def digest_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return "sha256:" + hasher.hexdigest()


def file_mode(path: Path) -> str:
    return f"{stat.S_IMODE(path.stat().st_mode):04o}"


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def bundle_outputs(root: Path) -> tuple[dict[str, str], dict[str, str], list[dict[str, str]]]:
    digests: dict[str, str] = {}
    modes: dict[str, str] = {}
    problems: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        if path.name == "receipt.json":
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            problems.append({"path": relative, "reason": "symlink"})
            continue
        try:
            metadata = path.lstat()
        except OSError:
            problems.append({"path": relative, "reason": "stat"})
            continue
        if stat.S_ISDIR(metadata.st_mode):
            continue
        if not stat.S_ISREG(metadata.st_mode):
            problems.append({"path": relative, "reason": "special"})
            continue
        digests[relative] = digest_file(path)
        modes[relative] = f"{stat.S_IMODE(metadata.st_mode):04o}"
    return digests, modes, problems


def observed_subject_paths(
    subject: Path,
    bundle: Path,
) -> tuple[set[str], list[dict[str, str]]]:
    bundle = bundle.resolve()
    result: set[str] = set()
    problems: list[dict[str, str]] = []
    for current, dirs, files in os.walk(subject, topdown=True, followlinks=False):
        current_path = Path(current)
        kept: list[str] = []
        for name in sorted(dirs):
            candidate = current_path / name
            relative = candidate.relative_to(subject).as_posix()
            if name in EXCLUDED_DIRS:
                continue
            if candidate.is_symlink():
                problems.append({"path": relative, "reason": "symlink"})
                continue
            resolved = candidate.resolve()
            if resolved == bundle or resolved.is_relative_to(bundle):
                continue
            kept.append(name)
        dirs[:] = kept
        for name in sorted(files):
            path = current_path / name
            relative = path.relative_to(subject).as_posix()
            if path.resolve().is_relative_to(bundle):
                continue
            if path.is_symlink():
                problems.append({"path": relative, "reason": "symlink"})
                continue
            try:
                mode = path.lstat().st_mode
            except OSError:
                problems.append({"path": relative, "reason": "stat"})
                continue
            if not stat.S_ISREG(mode):
                problems.append({"path": relative, "reason": "special"})
                continue
            result.add(relative)
    return result, problems


def verify(
    bundle_root: Path,
    *,
    authority_path: Path,
    subject_root: Path | None = None,
) -> dict[str, Any]:
    bundle = bundle_root.resolve()
    authority = read_object(authority_path.resolve())
    manifest = read_object(bundle / "manifest.json")
    contract = read_object(bundle / "receiving-contract.json")
    receipt = read_object(bundle / "receipt.json")

    expected_outputs = receipt.get("outputs")
    expected_modes = receipt.get("output_modes")
    actual_outputs, actual_modes, output_problems = bundle_outputs(bundle)
    receipt_payload = {
        key: value
        for key, value in receipt.items()
        if key != "receipt_digest"
    }
    manifest_subject = manifest.get("subject", {})
    manifest_files = manifest.get("files", [])
    subject_body = {
        "program_id": manifest.get("program_id"),
        "identity": manifest_subject.get("identity"),
        "files": manifest_files,
    }
    producer = authority.get("producer", {})
    producer_identity = manifest.get("producer_identity")
    claims = receipt.get("claims", {})

    checks: dict[str, bool] = {
        "receiver_schema": authority.get("schema") == RECEIVER_SCHEMA,
        "manifest_schema": manifest.get("schema") == MANIFEST_SCHEMA,
        "contract_schema": contract.get("schema") == CONTRACT_SCHEMA,
        "receipt_schema": receipt.get("schema") == RECEIPT_SCHEMA,
        "producer_contract": (
            contract.get("producer") == "ggen-create"
            and contract.get("receiver") == "ggen-legacy"
        ),
        "authority_schema_binding": (
            producer.get("accepted_manifest_schema") == MANIFEST_SCHEMA
            and producer.get("accepted_contract_schema") == CONTRACT_SCHEMA
            and producer.get("accepted_receipt_schema") == RECEIPT_SCHEMA
        ),
        "producer_identity": (
            isinstance(producer_identity, dict)
            and producer_identity == contract.get("producer_identity")
            and producer_identity == receipt.get("producer_identity")
            and producer_identity.get("name") == "ggen-create"
            and producer_identity.get("repository") == producer.get("repository")
            and producer_identity.get("commit") == producer.get("commit")
            and producer_identity.get("version") == producer.get("version")
        ),
        "output_regular_files": not output_problems,
        "output_set": (
            isinstance(expected_outputs, dict)
            and set(actual_outputs) == set(expected_outputs)
        ),
        "output_digests": (
            isinstance(expected_outputs, dict)
            and actual_outputs == expected_outputs
        ),
        "output_modes": (
            isinstance(expected_modes, dict)
            and actual_modes == expected_modes
        ),
        "bundle_digest": (
            digest_json({
                "outputs": actual_outputs,
                "output_modes": actual_modes,
            })
            == receipt.get("bundle_digest")
        ),
        "receipt_digest": (
            digest_json(receipt_payload) == receipt.get("receipt_digest")
        ),
        "subject_digest": (
            digest_json(subject_body) == manifest_subject.get("digest")
            and receipt.get("subject_digest") == manifest_subject.get("digest")
            and contract.get("subject_digest") == manifest_subject.get("digest")
        ),
        "workstream_boundary": (
            contract.get("provided_workstreams")
            == {"A": "ALIVE", "B": "PARTIAL_ALIVE", "C": "ALIVE", "D": "ALIVE"}
            and contract.get("receiver_owned_workstreams")
            == ["E", "F", "G", "H", "I", "J", "K"]
        ),
        "self_certification_refused": (
            contract.get("standing") == "PARTIAL_ALIVE"
            and receipt.get("state") == "PARTIAL_ALIVE"
            and all(claims.get(name) == "UNKNOWN" for name in REQUIRED_UNKNOWN)
        ),
    }

    drift: list[dict[str, str]] = list(output_problems)
    if subject_root is not None:
        subject = subject_root.resolve()
        subject_drift: list[dict[str, str]] = []
        admitted_paths = {
            item.get("path")
            for item in manifest_files
            if isinstance(item, dict) and isinstance(item.get("path"), str)
        }
        observed_paths, subject_problems = observed_subject_paths(subject, bundle)
        subject_drift.extend(subject_problems)
        for item in manifest_files:
            path = subject / item["path"]
            if item["path"] not in observed_paths:
                subject_drift.append({"path": item["path"], "reason": "missing"})
            elif digest_file(path) != item.get("sha256"):
                subject_drift.append({"path": item["path"], "reason": "digest"})
            elif file_mode(path) != item.get("mode"):
                subject_drift.append({"path": item["path"], "reason": "mode"})
            elif path.stat().st_size != item.get("size"):
                subject_drift.append({"path": item["path"], "reason": "size"})
        for path in sorted(observed_paths - admitted_paths):
            subject_drift.append({"path": path, "reason": "unadmitted"})
        drift.extend(subject_drift)
        checks["subject_replay"] = not subject_drift

    valid = all(checks.values())
    return {
        "schema": "ggen-legacy-ggen-create-verification/1",
        "producer": producer_identity,
        "bundle": str(bundle),
        "subject": str(subject_root.resolve()) if subject_root else None,
        "checks": checks,
        "drift": drift,
        "subject_digest": receipt.get("subject_digest"),
        "bundle_digest": receipt.get("bundle_digest"),
        "state": "ALIVE" if valid else "BUILD_BROKEN",
        "valid": valid,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independently verify a ggen-create receiving bundle",
    )
    parser.add_argument("bundle")
    parser.add_argument("--authority", required=True)
    parser.add_argument("--subject")
    args = parser.parse_args()
    try:
        report = verify(
            Path(args.bundle),
            authority_path=Path(args.authority),
            subject_root=Path(args.subject) if args.subject else None,
        )
    except ValueError as exc:
        print(json.dumps({
            "state": "BLOCKED",
            "refusal": "RECEIVING_BUNDLE_PARSE_REFUSED",
            "detail": str(exc),
        }, indent=2, sort_keys=True))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
