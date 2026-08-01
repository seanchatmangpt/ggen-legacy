#!/usr/bin/env python3
"""Verify and project the same-day multi-repository reconstitution corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
EXPECTED_REPOSITORIES = {
    "seanchatmangpt/ggen",
    "seanchatmangpt/mfw",
    "seanchatmangpt/ferroplan",
    "seanchatmangpt/wasm4pm",
    "seanchatmangpt/wasm4pm-compat",
    "seanchatmangpt/open-ontologies",
    "seanchatmangpt/ggen-legacy",
    "seanchatmangpt/chicago-tdd-tools",
    "seanchatmangpt/ostar",
    "seanchatmangpt/zoela",
    "seanchatmangpt/clap-noun-verb",
    "seanchatmangpt/lsp-max",
    "seanchatmangpt/dspygen",
    "seanchatmangpt/stpnt",
    "seanchatmangpt/truex",
    "seanchatmangpt/praxis",
    "seanchatmangpt/unrdf",
    "seanchatmangpt/agile-protocol-specification",
    "seanchatmangpt/clnrm",
}
DISPOSITIONS = {
    "INTEGRATED",
    "INTEGRATED_BRANCH",
    "ACTIVE_CANDIDATE",
    "PRESERVED_CANDIDATE",
    "TRANSPORT_ONLY",
}
STANDINGS = {
    "ALIVE",
    "PARTIAL_ALIVE",
    "UNKNOWN",
    "BLOCKED",
    "BUILD_BROKEN",
    "UNSUPPORTED",
}


class Refusal(RuntimeError):
    """Typed fail-closed contract refusal."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def payload(self) -> dict[str, str]:
        return {"schema": "ggen-legacy.refusal/v1", "code": self.code, "message": self.message}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_bytes(data: bytes, mode: str) -> tuple[str, str]:
    if mode == "sha256-observation":
        return "SHA-256", hashlib.sha256(data).hexdigest()
    try:
        import blake3  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise Refusal(
            "RECON-BLAKE3-001",
            "BLAKE3 provider unavailable; install blake3==1.0.9 or run the explicitly non-promoting observation mode",
        ) from exc
    return "BLAKE3", blake3.blake3(data).hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise Refusal("RECON-MANIFEST-001", f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise Refusal("RECON-MANIFEST-002", f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise Refusal("RECON-MANIFEST-003", "manifest root must be an object")
    return value


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    if manifest.get("schema") != "ggen-legacy.ecosystem-reconstitution/1":
        raise Refusal("RECON-SCHEMA-001", "unexpected manifest schema")
    if manifest.get("authority") != "AUTHORED_INPUT_ONLY":
        raise Refusal("RECON-AUTHORITY-001", "manifest must remain authored input, not generated standing")
    if manifest.get("direct_actuation") is not False:
        raise Refusal("RECON-ACTUATION-001", "direct actuation is forbidden")
    if manifest.get("final_admission_allowed") is not False:
        raise Refusal("RECON-PROMOTION-001", "authored manifest cannot grant final admission")
    if manifest.get("standing") != "UNKNOWN":
        raise Refusal("RECON-PROMOTION-002", "authored source standing must remain UNKNOWN")
    if manifest.get("required_broker") != "BRCE":
        raise Refusal("RECON-BROKER-001", "BRCE must remain the only consequential broker")
    if not SHA_RE.fullmatch(str(manifest.get("corpus_base_sha", ""))):
        raise Refusal("RECON-SHA-001", "corpus base SHA must be a full lowercase Git SHA")

    repositories = manifest.get("repositories")
    if not isinstance(repositories, list):
        raise Refusal("RECON-REPOSITORY-001", "repositories must be an array")
    if len(repositories) != manifest.get("expected_repository_count"):
        raise Refusal("RECON-REPOSITORY-002", "repository count differs from declared exact count")

    by_name: dict[str, dict[str, Any]] = {}
    source_ids: set[str] = set()
    source_coordinates: set[tuple[str, str, str]] = set()
    for item in repositories:
        if not isinstance(item, dict):
            raise Refusal("RECON-REPOSITORY-003", "repository entry must be an object")
        name = item.get("repository")
        if not isinstance(name, str) or not REPO_RE.fullmatch(name):
            raise Refusal("RECON-REPOSITORY-004", f"invalid repository identity: {name!r}")
        if name in by_name:
            raise Refusal("RECON-REPOSITORY-005", f"duplicate repository identity: {name}")
        by_name[name] = item

        canonical_sha = item.get("canonical_reconstruction_sha")
        if not isinstance(canonical_sha, str) or not SHA_RE.fullmatch(canonical_sha):
            raise Refusal("RECON-SHA-002", f"{name} has malformed canonical SHA")

        commands = item.get("validation_commands")
        if not isinstance(commands, list) or len(commands) < 3 or not all(isinstance(c, str) and c.strip() for c in commands):
            raise Refusal("RECON-VALIDATION-001", f"{name} must declare at least three concrete validation commands")

        sources = item.get("sources")
        if not isinstance(sources, list) or not sources:
            raise Refusal("RECON-SOURCE-001", f"{name} has no exact source objects")
        source_shas: set[str] = set()
        for source in sources:
            if not isinstance(source, dict):
                raise Refusal("RECON-SOURCE-002", f"{name} source must be an object")
            source_id = source.get("id")
            sha = source.get("sha")
            disposition = source.get("disposition")
            observed_standing = source.get("observed_standing")
            if not isinstance(source_id, str) or not source_id:
                raise Refusal("RECON-SOURCE-003", f"{name} has empty source identity")
            if source_id in source_ids:
                raise Refusal("RECON-SOURCE-004", f"duplicate source identity: {source_id}")
            source_ids.add(source_id)
            if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
                raise Refusal("RECON-SHA-003", f"{name}/{source_id} has malformed source SHA")
            coordinate = (name, sha, source_id)
            if coordinate in source_coordinates:
                raise Refusal("RECON-SOURCE-005", f"duplicate source coordinate: {coordinate}")
            source_coordinates.add(coordinate)
            source_shas.add(sha)
            if disposition not in DISPOSITIONS:
                raise Refusal("RECON-DISPOSITION-001", f"{name}/{source_id} has unknown disposition")
            if observed_standing not in STANDINGS:
                raise Refusal("RECON-STANDING-001", f"{name}/{source_id} has unknown observed standing")
            if disposition in {"INTEGRATED", "INTEGRATED_BRANCH"} and source.get("merged") is not True:
                raise Refusal("RECON-DISPOSITION-002", f"{name}/{source_id} integrated source is not marked merged")
            if disposition == "ACTIVE_CANDIDATE" and (source.get("pr_state") != "open" or source.get("merged") is not False):
                raise Refusal("RECON-DISPOSITION-003", f"{name}/{source_id} active candidate state is inconsistent")
            if disposition == "PRESERVED_CANDIDATE" and (source.get("pr_state") != "closed" or source.get("merged") is not False):
                raise Refusal("RECON-DISPOSITION-004", f"{name}/{source_id} preserved candidate state is inconsistent")
            if disposition == "TRANSPORT_ONLY" and item.get("product_reconstitution") is not False:
                raise Refusal("RECON-TRANSPORT-001", f"{name} transport-only source cannot become product authority")
        if canonical_sha not in source_shas:
            raise Refusal("RECON-SOURCE-006", f"{name} canonical reconstruction SHA is not among admitted source objects")

    actual = set(by_name)
    if actual != EXPECTED_REPOSITORIES:
        missing = sorted(EXPECTED_REPOSITORIES - actual)
        extra = sorted(actual - EXPECTED_REPOSITORIES)
        raise Refusal("RECON-EXACT-SET-001", f"repository set mismatch; missing={missing} extra={extra}")

    for name, item in by_name.items():
        dependencies = item.get("depends_on")
        if not isinstance(dependencies, list) or len(dependencies) != len(set(dependencies)):
            raise Refusal("RECON-DEPENDENCY-001", f"{name} dependencies must be a unique array")
        for dependency in dependencies:
            if dependency not in by_name:
                raise Refusal("RECON-DEPENDENCY-002", f"{name} references unknown dependency {dependency}")
            if dependency == name:
                raise Refusal("RECON-DEPENDENCY-003", f"{name} depends on itself")

    return topological_order(by_name)


def topological_order(by_name: dict[str, dict[str, Any]]) -> list[str]:
    indegree = {name: 0 for name in by_name}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for name, item in by_name.items():
        for dependency in item["depends_on"]:
            outgoing[dependency].append(name)
            indegree[name] += 1
    ready = deque(sorted(name for name, degree in indegree.items() if degree == 0))
    order: list[str] = []
    while ready:
        current = ready.popleft()
        order.append(current)
        for target in sorted(outgoing[current]):
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    if len(order) != len(by_name):
        cyclic = sorted(name for name, degree in indegree.items() if degree > 0)
        raise Refusal("RECON-DEPENDENCY-004", f"repository dependency graph contains a cycle: {cyclic}")
    return order


def source_matrix(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for repo in sorted(manifest["repositories"], key=lambda item: item["repository"]):
        for source in sorted(repo["sources"], key=lambda item: item["id"]):
            matrix.append(
                {
                    "repository": repo["repository"],
                    "source_id": source["id"],
                    "sha": source["sha"],
                    "disposition": source["disposition"],
                    "pull_request": source["pull_request"],
                    "merged": source["merged"],
                    "product_reconstitution": repo["product_reconstitution"],
                }
            )
    return matrix


def verify(manifest_path: Path, output: Path, digest_mode: str) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    order = validate_manifest(manifest)
    output.mkdir(parents=True, exist_ok=True)
    matrix = source_matrix(manifest)
    algorithm, subject_digest = digest_bytes(canonical_bytes(manifest), digest_mode)
    plan = {
        "schema": "ggen-legacy.ecosystem-reconstitution.plan/v1",
        "program_id": manifest["program_id"],
        "corpus_base_sha": manifest["corpus_base_sha"],
        "head_binding": manifest["head_binding"],
        "repository_order": order,
        "source_matrix": matrix,
        "direct_actuation": False,
        "required_broker": "BRCE",
        "final_admission_allowed": False,
    }
    _, plan_digest = digest_bytes(canonical_bytes(plan), digest_mode)
    receipt = {
        "schema": "ggen-legacy.ecosystem-reconstitution.receipt/v1",
        "algorithm": algorithm,
        "subject_digest": subject_digest,
        "plan_digest": plan_digest,
        "repository_count": len(manifest["repositories"]),
        "source_count": len(matrix),
        "product_repository_count": sum(1 for item in manifest["repositories"] if item["product_reconstitution"]),
        "transport_repository_count": sum(1 for item in manifest["repositories"] if not item["product_reconstitution"]),
        "standing": "PARTIAL_ALIVE",
        "promotion_eligible": False,
        "direct_actuation": False,
        "open_obligations": (
            ["exact source retrieval", "repository-owned validation ladders", "clean-room replay", "final foundry admission"]
            if digest_mode == "blake3"
            else ["BLAKE3 receipt", "exact source retrieval", "repository-owned validation ladders", "clean-room replay", "final foundry admission"]
        ),
    }
    report = {
        "schema": "ggen.verifier.report.v1",
        "program_id": manifest["program_id"],
        "standing": receipt["standing"],
        "exact_repository_set": True,
        "dependency_closed": True,
        "deterministic_plan": True,
        "source_objects_bound": len(matrix),
        "direct_actuation": False,
        "final_admission": False,
        "receipt": receipt,
        "exclusions": [
            "No repository source is copied into controller-owned foundry projections.",
            "No source branch is merged or retired by this verifier.",
            "Transport-only repositories remain lineage evidence and cannot become product authority.",
            "Repository-native validation commands are inventoried but not represented as executed.",
            "ALIVE is unavailable until exact source retrieval, validation, receipts, and clean-room replay close.",
        ],
    }
    for name, value in (("plan.json", plan), ("receipt.json", receipt), ("report.json", report)):
        (output / name).write_bytes(canonical_bytes(value) + b"\n")
    return report


def aggregate(manifest_path: Path, receipts_dir: Path, output: Path, digest_mode: str) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    validate_manifest(manifest)
    expected = {(row["repository"], row["source_id"], row["sha"]) for row in source_matrix(manifest)}
    receipts: list[dict[str, Any]] = []
    for path in sorted(receipts_dir.rglob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if value.get("schema") == "ggen-legacy.source-reconstitution.receipt/v1":
            receipts.append(value)
    observed = {(r.get("repository"), r.get("source_id"), r.get("sha")) for r in receipts}
    missing = sorted(expected - observed)
    if missing:
        raise Refusal("RECON-AGGREGATE-001", f"missing source receipts: {missing}")
    duplicate_count = len(receipts) - len(observed)
    if duplicate_count:
        raise Refusal("RECON-AGGREGATE-002", f"duplicate source receipts: {duplicate_count}")
    states = defaultdict(int)
    for receipt in receipts:
        states[str(receipt.get("standing"))] += 1
    algorithm, aggregate_digest = digest_bytes(canonical_bytes(sorted(receipts, key=lambda r: (r["repository"], r["source_id"]))), digest_mode)
    final = {
        "schema": "ggen-legacy.ecosystem-reconstitution.aggregate/v1",
        "algorithm": algorithm,
        "aggregate_digest": aggregate_digest,
        "source_receipt_count": len(receipts),
        "states": dict(sorted(states.items())),
        "standing": "PARTIAL_ALIVE" if states.get("ALIVE", 0) else "BLOCKED",
        "all_sources_retrieved": states.get("ALIVE", 0) == len(receipts),
        "final_admission": False,
        "direct_actuation": False,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "aggregate-report.json").write_bytes(canonical_bytes(final) + b"\n")
    return final


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.add_argument("--output", type=Path, required=True)
    verify_parser.add_argument("--digest-mode", choices=("blake3", "sha256-observation"), default="blake3")
    matrix_parser = sub.add_parser("matrix")
    matrix_parser.add_argument("--manifest", type=Path, required=True)
    aggregate_parser = sub.add_parser("aggregate")
    aggregate_parser.add_argument("--manifest", type=Path, required=True)
    aggregate_parser.add_argument("--receipts-dir", type=Path, required=True)
    aggregate_parser.add_argument("--output", type=Path, required=True)
    aggregate_parser.add_argument("--digest-mode", choices=("blake3", "sha256-observation"), default="blake3")
    args = parser.parse_args()
    try:
        if args.command == "verify":
            print(json.dumps(verify(args.manifest, args.output, args.digest_mode), indent=2, sort_keys=True))
        elif args.command == "matrix":
            manifest = load_manifest(args.manifest)
            validate_manifest(manifest)
            print(json.dumps({"include": source_matrix(manifest)}, separators=(",", ":")))
        else:
            print(json.dumps(aggregate(args.manifest, args.receipts_dir, args.output, args.digest_mode), indent=2, sort_keys=True))
        return 0
    except Refusal as refusal:
        print(json.dumps(refusal.payload(), indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
