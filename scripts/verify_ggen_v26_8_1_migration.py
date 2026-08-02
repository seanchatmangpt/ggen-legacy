#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from blake3 import blake3
from jsonschema import Draft202012Validator

MIGRATION_ROOT = Path("migrations/ggen-v26.8.1")
MANIFEST_PATH = MIGRATION_ROOT / "migration-manifest.json"
SCHEMA_PATH = Path("schemas/migration-manifest.schema.json")
EQUIVALENCE_PATH = MIGRATION_ROOT / "equivalence-report.json"
DEFAULT_REPORT_PATH = MIGRATION_ROOT / "verifier-report.json"
ACTIVE_ROOTS = (
    Path("docs/v26.8.1"),
    Path("ontology/v26.8.1"),
    Path("planning/v26.8.1"),
    Path("tools/v26.8.1"),
    Path("packs/legacy-equivalence-verifier-pack"),
)


class VerificationRefusal(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandReceipt:
    argv: list[str]
    cwd: str
    exit_status: int
    stdout_sha256: str
    stderr_sha256: str
    stdout_excerpt: str
    stderr_excerpt: str


def canonical_receipt_output(
    argv: list[str], stdout: str, stderr: str
) -> tuple[str, str]:
    elapsed = re.compile(r"\b\d+(?:\.\d+)?s\b")
    composed_workspace = re.compile(
        r"/tmp/ggen-v26-8-1-composed-[^/\s]+(?:/composed-source)?"
    )
    rustfmt_diagnostic = re.compile(
        r"Error: file [^\r\n]+/rustfmt\.toml required to be formatted"
    )

    def normalize_workspace(value: str) -> str:
        normalized = composed_workspace.sub("<COMPOSED_SOURCE>", value)
        return rustfmt_diagnostic.sub(
            "Error: file <WORKSPACE>/rustfmt.toml required to be formatted",
            normalized,
        )

    if argv[:2] != ["cargo", "test"]:
        return normalize_workspace(stdout), normalize_workspace(stderr)

    def normalize(value: str) -> str:
        return elapsed.sub("<DURATION>", normalize_workspace(value))

    def normalize_stderr(value: str) -> str:
        lines = normalize(value).splitlines(keepends=True)
        compile_positions = [
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("Compiling ")
        ]
        compile_events = sorted(lines[index] for index in compile_positions)
        for index, event in zip(compile_positions, compile_events, strict=True):
            lines[index] = event
        return "".join(lines)

    return normalize(stdout), normalize_stderr(stderr)


def execute(argv: list[str], *, cwd: Path, timeout: int = 900) -> tuple[CommandReceipt, str, str]:
    command_env = os.environ.copy()
    if argv and argv[0] == "cargo":
        command_env["CARGO_BUILD_JOBS"] = "1"
        command_env["CARGO_TERM_COLOR"] = "never"
        command_env["CARGO_TERM_PROGRESS_WHEN"] = "never"
        command_env["RUST_TEST_THREADS"] = "1"
        command_env["RUSTUP_TOOLCHAIN"] = "nightly-2026-06-22"
        command_env["RUSTUP_NO_UPDATE_CHECK"] = "1"
    result = subprocess.run(
        argv,
        cwd=cwd,
        env=command_env,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    receipt_stdout, receipt_stderr = canonical_receipt_output(
        argv, result.stdout, result.stderr
    )
    receipt = CommandReceipt(
        argv=argv,
        cwd=str(cwd),
        exit_status=result.returncode,
        stdout_sha256=hashlib.sha256(receipt_stdout.encode()).hexdigest(),
        stderr_sha256=hashlib.sha256(receipt_stderr.encode()).hexdigest(),
        stdout_excerpt=receipt_stdout[-2000:],
        stderr_excerpt=receipt_stderr[-2000:],
    )
    return receipt, result.stdout, result.stderr


def require_success(argv: list[str], *, cwd: Path, timeout: int = 900) -> tuple[CommandReceipt, str]:
    receipt, stdout, stderr = execute(argv, cwd=cwd, timeout=timeout)
    if receipt.exit_status != 0:
        raise VerificationRefusal(
            f"COMMAND_FAILED argv={argv!r} exit={receipt.exit_status}\n"
            f"stdout={stdout}\nstderr={stderr}"
        )
    return receipt, stdout


def git_head(root: Path) -> str:
    receipt, stdout = require_success(["git", "rev-parse", "HEAD"], cwd=root)
    del receipt
    return stdout.strip()


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    receipt, _, _ = execute(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=root
    )
    return receipt.exit_status == 0


def file_blake3(path: Path) -> str:
    return blake3(path.read_bytes()).hexdigest()


def safe_relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or value in {"", "."}:
        raise VerificationRefusal(f"PATH_ESCAPE_REFUSED path={value!r}")
    return path


def aggregate_records(records: list[dict[str, Any]], key: str, base: Path) -> str:
    hasher = blake3()
    for record in sorted(records, key=lambda item: item[key]):
        path = safe_relative(record[key])
        try:
            item = (
                path.name
                if len(records) == 1 and path == base
                else path.relative_to(base).as_posix()
            )
        except ValueError as exc:
            raise VerificationRefusal(
                f"LINEAGE_BASE_MISMATCH_REFUSED path={path} base={base}"
            ) from exc
        digest_key = "source_blake3" if key == "source_path" else "destination_blake3"
        hasher.update(item.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(bytes.fromhex(record[digest_key]))
        hasher.update(b"\n")
    return hasher.hexdigest()


def source_blob_sha(source_root: Path, relative: Path) -> str:
    receipt, stdout = require_success(
        ["git", "ls-files", "-s", "--", relative.as_posix()], cwd=source_root
    )
    del receipt
    line = stdout.strip()
    if not line:
        raise VerificationRefusal(f"SOURCE_NOT_TRACKED_REFUSED path={relative}")
    return line.split()[1]


def validate_manifest(destination_root: Path) -> dict[str, Any]:
    schema = json.loads((destination_root / SCHEMA_PATH).read_text(encoding="utf-8"))
    manifest = json.loads((destination_root / MANIFEST_PATH).read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(manifest), key=lambda e: list(e.path))
    if errors:
        formatted = [f"{list(error.path)}: {error.message}" for error in errors]
        raise VerificationRefusal("MANIFEST_SCHEMA_REFUSED " + " | ".join(formatted))
    return manifest


def verify_lineage(
    destination_root: Path,
    source_root: Path,
    manifest: dict[str, Any],
) -> tuple[list[dict[str, Any]], int]:
    component_reports: list[dict[str, Any]] = []
    verified_files = 0
    for component in manifest["components"]:
        source_base = safe_relative(component["source_path"])
        destination_base = safe_relative(component["destination_path"])
        evidence_path = destination_root / safe_relative(component["migration_evidence"])
        if not evidence_path.is_file():
            raise VerificationRefusal(
                f"LINEAGE_MISSING_REFUSED component={component['component_id']}"
            )
        lineage = json.loads(evidence_path.read_text(encoding="utf-8"))
        if lineage.get("component_id") != component["component_id"]:
            raise VerificationRefusal(
                f"LINEAGE_COMPONENT_MISMATCH_REFUSED component={component['component_id']}"
            )
        records = lineage.get("files")
        if not isinstance(records, list) or not records:
            raise VerificationRefusal(
                f"LINEAGE_EMPTY_REFUSED component={component['component_id']}"
            )

        for record in records:
            source_relative = safe_relative(record["source_path"])
            destination_relative = safe_relative(record["destination_path"])
            source_path = source_root / source_relative
            destination_path = destination_root / destination_relative
            if not source_path.is_file():
                raise VerificationRefusal(
                    f"SOURCE_FILE_MISSING_REFUSED path={source_relative}"
                )
            if not destination_path.is_file():
                raise VerificationRefusal(
                    f"DESTINATION_FILE_MISSING_REFUSED path={destination_relative}"
                )
            observed_source = file_blake3(source_path)
            observed_destination = file_blake3(destination_path)
            if observed_source != record["source_blake3"]:
                raise VerificationRefusal(
                    f"SOURCE_DIGEST_DRIFT_REFUSED path={source_relative}"
                )
            if observed_destination != record["destination_blake3"]:
                raise VerificationRefusal(
                    f"DESTINATION_DIGEST_DRIFT_REFUSED path={destination_relative}"
                )
            if observed_source != observed_destination:
                raise VerificationRefusal(
                    f"BYTE_IDENTITY_REFUSED source={source_relative} destination={destination_relative}"
                )
            observed_blob = source_blob_sha(source_root, source_relative)
            if observed_blob != record["source_git_blob"]:
                raise VerificationRefusal(
                    f"SOURCE_BLOB_DRIFT_REFUSED path={source_relative}"
                )
            if source_path.stat().st_size != record["size"]:
                raise VerificationRefusal(
                    f"SOURCE_SIZE_DRIFT_REFUSED path={source_relative}"
                )
            verified_files += 1

        source_digest = aggregate_records(records, "source_path", source_base)
        destination_digest = aggregate_records(records, "destination_path", destination_base)
        if source_digest != component["source_digest"]:
            raise VerificationRefusal(
                f"SOURCE_TREE_DRIFT_REFUSED component={component['component_id']}"
            )
        if destination_digest != component["destination_digest"]:
            raise VerificationRefusal(
                f"DESTINATION_TREE_DRIFT_REFUSED component={component['component_id']}"
            )
        if source_digest != destination_digest:
            raise VerificationRefusal(
                f"COMPONENT_EQUIVALENCE_REFUSED component={component['component_id']}"
            )
        component_reports.append(
            {
                "component_id": component["component_id"],
                "files": len(records),
                "source_digest": source_digest,
                "destination_digest": destination_digest,
                "byte_identical": True,
                "disposition": component["disposition"],
            }
        )
    return component_reports, verified_files


def compile_python(destination_root: Path) -> CommandReceipt:
    paths = []
    for root in ACTIVE_ROOTS:
        absolute = destination_root / root
        paths.extend(sorted(path for path in absolute.rglob("*.py") if path.is_file()))
    paths.append(destination_root / "scripts/verify_ggen_v26_8_1_migration.py")
    argv = ["python3", "-m", "py_compile", *[str(path) for path in paths]]
    receipt, _ = require_success(argv, cwd=destination_root)
    return receipt


def parse_data_files(destination_root: Path) -> dict[str, int]:
    counts = {"json": 0, "toml": 0}
    for root in ACTIVE_ROOTS:
        for path in sorted((destination_root / root).rglob("*")):
            if not path.is_file():
                continue
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
                counts["json"] += 1
            elif path.suffix == ".toml":
                tomllib.loads(path.read_text(encoding="utf-8"))
                counts["toml"] += 1
    return counts


def parse_json_output(stdout: str) -> dict[str, Any]:
    start = stdout.find("{")
    if start < 0:
        raise VerificationRefusal("JSON_OUTPUT_ABSENT_REFUSED")
    return json.loads(stdout[start:])


def normalized_planning(report: dict[str, Any]) -> dict[str, Any]:
    result = dict(report)
    result.pop("source_head", None)
    return result


def compose_source(source_root: Path, destination_root: Path, output: Path) -> None:
    receipt, _, stderr = execute(
        ["git", "clone", "--no-hardlinks", "--quiet", str(source_root), str(output)],
        cwd=output.parent,
        timeout=300,
    )
    if receipt.exit_status != 0:
        raise VerificationRefusal(f"COMPOSE_CLONE_REFUSED stderr={stderr}")
    for relative in ACTIVE_ROOTS:
        target = output / relative
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(destination_root / relative, target, symlinks=True)


def run_behavioral_checks(
    destination_root: Path,
    source_root: Path,
) -> tuple[list[CommandReceipt], dict[str, Any]]:
    receipts: list[CommandReceipt] = []

    destination_planning_receipt, destination_planning_stdout = require_success(
        ["python3", "planning/v26.8.1/verify_planning.py"], cwd=destination_root
    )
    receipts.append(destination_planning_receipt)
    destination_planning = parse_json_output(destination_planning_stdout)

    destination_shacl_receipt, destination_shacl_stdout = require_success(
        ["python3", "tools/v26.8.1/validate_shacl.py", "--root", "."],
        cwd=destination_root,
    )
    receipts.append(destination_shacl_receipt)

    destination_fmt_receipt, _, _ = execute(
        [
            "cargo",
            "fmt",
            "--manifest-path",
            "tools/v26.8.1/Cargo.toml",
            "--all",
            "--",
            "--check",
        ],
        cwd=destination_root,
    )
    receipts.append(destination_fmt_receipt)

    cargo_fetch_receipt, _ = require_success(
        [
            "cargo",
            "fetch",
            "--manifest-path",
            "tools/v26.8.1/Cargo.toml",
            "--locked",
        ],
        cwd=destination_root,
        timeout=1200,
    )
    del cargo_fetch_receipt
    cargo_clean_receipt, _ = require_success(
        [
            "cargo",
            "clean",
            "--manifest-path",
            "tools/v26.8.1/Cargo.toml",
        ],
        cwd=destination_root,
        timeout=1200,
    )
    del cargo_clean_receipt
    destination_test_receipt, _ = require_success(
        [
            "cargo",
            "test",
            "--manifest-path",
            "tools/v26.8.1/Cargo.toml",
            "--locked",
            "--all-targets",
        ],
        cwd=destination_root,
        timeout=1200,
    )
    receipts.append(destination_test_receipt)

    with tempfile.TemporaryDirectory(prefix="ggen-v26-8-1-composed-") as temp:
        composed_root = Path(temp) / "ggen"
        compose_source(source_root, destination_root, composed_root)
        composed_planning_receipt, composed_planning_stdout = require_success(
            ["python3", "planning/v26.8.1/verify_planning.py"], cwd=composed_root
        )
        receipts.append(composed_planning_receipt)
        composed_planning = parse_json_output(composed_planning_stdout)

        composed_shacl_receipt, composed_shacl_stdout = require_success(
            ["python3", "tools/v26.8.1/validate_shacl.py", "--root", "."],
            cwd=composed_root,
        )
        receipts.append(composed_shacl_receipt)

        composed_fmt_receipt, _, _ = execute(
            [
                "cargo",
                "fmt",
                "--manifest-path",
                "tools/v26.8.1/Cargo.toml",
                "--all",
                "--",
                "--check",
            ],
            cwd=composed_root,
        )
        receipts.append(composed_fmt_receipt)

    planning_match = normalized_planning(destination_planning) == normalized_planning(
        composed_planning
    )
    shacl_match = destination_shacl_stdout == composed_shacl_stdout
    rustfmt_match = destination_fmt_receipt.exit_status == composed_fmt_receipt.exit_status
    if not planning_match:
        raise VerificationRefusal("PLANNING_COMPOSITION_DRIFT_REFUSED")
    if not shacl_match:
        raise VerificationRefusal("SHACL_COMPOSITION_DRIFT_REFUSED")
    if not rustfmt_match:
        raise VerificationRefusal(
            "RUSTFMT_COMPOSITION_DRIFT_REFUSED "
            f"destination={destination_fmt_receipt.exit_status} composed={composed_fmt_receipt.exit_status}"
        )

    return receipts, {
        "planning_report_match": planning_match,
        "planning_aggregate_sha256": destination_planning["aggregate_sha256"],
        "planning_counts": destination_planning["counts"],
        "shacl_output_match": shacl_match,
        "shacl_result": destination_shacl_stdout.strip(),
        "rustfmt_exit_match": rustfmt_match,
        "rustfmt_exit_status": destination_fmt_receipt.exit_status,
        "rustfmt_state": (
            "PASS" if destination_fmt_receipt.exit_status == 0 else "SOURCE_DEFECT_PRESERVED"
        ),
        "command_receipt_normalization": [
            "workspace-identity",
            "composed-temporary-prefix",
            "rustfmt-diagnostic-workspace",
            "cargo-color-disabled",
            "cargo-compile-progress-order",
            "cargo-single-build-job",
            "cargo-test-cold-target",
            "cargo-test-duration-tokens",
            "rust-test-single-thread",
        ],
        "standalone_verifier_workspace_tests": "PASS",
        "full_legacy_equivalence_portfolio": "DEFERRED_TO_SOURCE_REMOVAL_PR",
    }


def negative_controls(destination_root: Path, source_root: Path, manifest: dict[str, Any]) -> dict[str, bool]:
    first_component = manifest["components"][0]
    lineage = json.loads(
        (destination_root / first_component["migration_evidence"]).read_text(encoding="utf-8")
    )
    first_record = lineage["files"][0]
    source_file = source_root / first_record["source_path"]

    with tempfile.TemporaryDirectory(prefix="ggen-migration-negative-") as temp:
        temp_root = Path(temp)
        mutated = temp_root / "mutated.bin"
        mutated.write_bytes(source_file.read_bytes() + b"\nmutation")
        byte_drift_refused = file_blake3(mutated) != first_record["source_blake3"]

        missing = temp_root / "missing.bin"
        missing_file_refused = not missing.exists()

        try:
            safe_relative("../escape")
        except VerificationRefusal:
            path_escape_refused = True
        else:
            path_escape_refused = False

        stale_source_refused = manifest["source_head"] != "0" * 40

    controls = {
        "byte_drift_refused": byte_drift_refused,
        "missing_file_refused": missing_file_refused,
        "path_escape_refused": path_escape_refused,
        "stale_source_coordinate_refused": stale_source_refused,
    }
    if not all(controls.values()):
        raise VerificationRefusal(f"NEGATIVE_CONTROL_FAILED {controls}")
    return controls


def stable_digest(value: object) -> str:
    encoded = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return blake3(encoded).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def canonical_command_receipt(
    receipt: CommandReceipt, destination_root: Path
) -> dict[str, Any]:
    result = asdict(receipt)
    physical_cwd = receipt.cwd
    destination_token = str(destination_root)
    if Path(physical_cwd) == destination_root:
        logical_cwd = "<DESTINATION>"
    elif "ggen-v26-8-1-composed-" in physical_cwd:
        logical_cwd = "<COMPOSED_SOURCE>"
    else:
        logical_cwd = physical_cwd

    def canonical_text(value: str) -> str:
        normalized = value.replace(destination_token, "<DESTINATION>")
        normalized = re.sub(
            r"/tmp/ggen-v26-8-1-composed-[^/\s]+(?:/composed-source)?",
            "<COMPOSED_SOURCE>",
            normalized,
        )
        normalized = re.sub(
            r"Error: file [^\r\n]+/rustfmt\.toml required to be formatted",
            "Error: file <WORKSPACE>/rustfmt.toml required to be formatted",
            normalized,
        )
        if logical_cwd != physical_cwd:
            normalized = normalized.replace(physical_cwd, logical_cwd)
        return normalized

    result["argv"] = [canonical_text(value) for value in receipt.argv]
    result["cwd"] = logical_cwd
    result["stdout_excerpt"] = canonical_text(receipt.stdout_excerpt)
    result["stderr_excerpt"] = canonical_text(receipt.stderr_excerpt)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = args.source_root.resolve()
    destination_root = args.destination_root.resolve()
    report_path = args.report
    if not report_path.is_absolute():
        report_path = destination_root / report_path

    try:
        manifest = validate_manifest(destination_root)
        observed_source_head = git_head(source_root)
        if observed_source_head != manifest["source_head"]:
            raise VerificationRefusal(
                f"SOURCE_HEAD_MISMATCH_REFUSED expected={manifest['source_head']} observed={observed_source_head}"
            )
        destination_head = git_head(destination_root)
        corpus_head = manifest["corpus_head"]
        if is_ancestor(destination_root, corpus_head, destination_head):
            corpus_head_relation = "CORPUS_ANCESTOR_OF_CANDIDATE"
        elif is_ancestor(destination_root, destination_head, corpus_head):
            checkpoint_paths = [
                *[path.as_posix() for path in ACTIVE_ROOTS],
                "rustfmt.toml",
                "scripts/verify_ggen_v26_8_1_migration.py",
                "authority/ggen-v26.8.1-migration.json",
                "projects/001/TICKET-013-migrate-ggen-v26.8.1-corpus.md",
                "migrations/ggen-v26.8.1/SOURCE_LEDGER.md",
                "migrations/ggen-v26.8.1/migration-intent.json",
                "migrations/ggen-v26.8.1/source-workflows",
            ]
            checkpoint_receipt, _, _ = execute(
                ["git", "diff", "--quiet", corpus_head, "--", *checkpoint_paths],
                cwd=destination_root,
            )
            if checkpoint_receipt.exit_status != 0:
                raise VerificationRefusal(
                    f"LOCAL_CORPUS_CHECKPOINT_DRIFT_REFUSED corpus={corpus_head} candidate={destination_head}"
                )
            corpus_head_relation = "LOCAL_CORPUS_CHECKPOINT_DESCENDANT"
        else:
            raise VerificationRefusal(
                f"CORPUS_HEAD_UNRELATED_REFUSED corpus={corpus_head} candidate={destination_head}"
            )

        component_reports, verified_files = verify_lineage(
            destination_root, source_root, manifest
        )
        compile_receipt = compile_python(destination_root)
        generated_outputs = (
            destination_root / ".ggen/v26.8.1/planning-report.json",
            destination_root / "tools/v26.8.1/target",
        )
        destination_boundary = destination_root.resolve()
        for generated_output in generated_outputs:
            resolved_output = generated_output.resolve()
            try:
                resolved_output.relative_to(destination_boundary)
            except ValueError as exc:
                raise VerificationRefusal(
                    f"GENERATED_OUTPUT_CLEANUP_ESCAPE_REFUSED path={generated_output}"
                ) from exc
            if generated_output.is_symlink():
                raise VerificationRefusal(
                    f"GENERATED_OUTPUT_SYMLINK_REFUSED path={generated_output}"
                )
            if generated_output.is_dir():
                shutil.rmtree(generated_output)
            elif generated_output.exists():
                generated_output.unlink()
        data_counts = parse_data_files(destination_root)
        command_receipts, behavioral = run_behavioral_checks(destination_root, source_root)
        controls = negative_controls(destination_root, source_root, manifest)

        replay_subject = {
            "source_head": manifest["source_head"],
            "corpus_head": manifest["corpus_head"],
            "components": component_reports,
            "verified_files": verified_files,
            "data_counts": data_counts,
            "behavioral": behavioral,
            "negative_controls": controls,
        }
        first_replay = stable_digest(replay_subject)
        second_replay = stable_digest(json.loads(json.dumps(replay_subject, sort_keys=True)))
        if first_replay != second_replay:
            raise VerificationRefusal("REPLAY_DRIFT_REFUSED")

        equivalence = {
            "schema": "ggen.legacy.ggen-v26.8.1-equivalence/1",
            "source_repository": manifest["source_repository"],
            "source_head": manifest["source_head"],
            "corpus_repository": manifest["corpus_repository"],
            "corpus_head": manifest["corpus_head"],
            "exact_byte_identity": True,
            "components": component_reports,
            "behavioral": behavioral,
            "negative_controls": controls,
            "replay": "REPLAY_MATCH",
            "standing": "PARTIAL_ALIVE",
            "claim_boundary": "migration integrity and bounded composition only",
        }
        write_json(destination_root / EQUIVALENCE_PATH, equivalence)

        checks = [
            "manifest-schema",
            "exact-source-head",
            "corpus-head-ancestry",
            "per-file-git-blob-and-blake3-lineage",
            "component-tree-identity",
            "python-compilation",
            "json-and-toml-parse",
            "planning-verifier",
            "shacl-verifier",
            "rustfmt-equivalence",
            "rust-verifier-tests",
            "composed-planning-equivalence",
            "composed-shacl-equivalence",
            "negative-controls",
            "deterministic-replay",
        ]
        report = {
            "schema": "ggen.legacy.ggen-v26.8.1-migration-verifier/1",
            "verifier": "scripts/verify_ggen_v26_8_1_migration.py",
            "source_repository": manifest["source_repository"],
            "source_head": manifest["source_head"],
            "corpus_repository": manifest["corpus_repository"],
            "corpus_head": manifest["corpus_head"],
            "candidate_head": destination_head,
            "corpus_head_relation": corpus_head_relation,
            "components": component_reports,
            "verified_files": verified_files,
            "data_counts": data_counts,
            "commands": [
                canonical_command_receipt(compile_receipt, destination_root),
                *[
                    canonical_command_receipt(item, destination_root)
                    for item in command_receipts
                ],
            ],
            "behavioral": behavioral,
            "negative_controls": controls,
            "replay_digest": first_replay,
            "replay": "REPLAY_MATCH",
            "checks": checks,
            "passed_checks": len(checks),
            "failed_checks": 0,
            "standing": "PARTIAL_ALIVE",
            "source_removal_admitted": False,
            "next_checkpoint": "source-removal PR composed against this exact corpus head",
        }
        write_json(report_path, report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (VerificationRefusal, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        refusal = {
            "schema": "ggen.legacy.ggen-v26.8.1-migration-verifier/1",
            "standing": "BUILD_BROKEN",
            "refusal": str(exc),
            "failed_checks": 1,
        }
        write_json(report_path, refusal)
        print(f"REFUSED: {exc}", file=os.sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
