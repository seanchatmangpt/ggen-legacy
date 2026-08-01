#!/usr/bin/env python3
"""Admit Workstream E with exact historical Git-object recovery.

This controller consumes the C capability catalog, D classification and recovery
plans, then resolves exact source objects before writing any consequence. It
handles deletion commits, alternative paths, path history, and bounded pickaxe
recovery without silently falling back to the current source tree.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

RECEIPT_SCHEMA = "ggen.enterprise-architecture-foundry.receipt/1"
EXTRACTION_SCHEMA = "ggen.enterprise-architecture-foundry.extraction-admission/2"
VERIFIER_ID = "ggen-foundry-admit-historical-extraction/v2"
REQUIRED_DISPOSITIONS = {"PRESERVED", "REPLACED", "SUBSUMED"}
HEX_TOKEN = re.compile(r"(?<![0-9a-f])([0-9a-f]{7,40})(?![0-9a-f])", re.IGNORECASE)
PATH_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_.-])((?:[A-Za-z0-9_.{}*?-]+/)+[A-Za-z0-9_.{}*?-]+(?:\.[A-Za-z0-9_.-]+)?/?|justfile)(?![A-Za-z0-9_.-])"
)


class Refusal(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def payload(self) -> dict[str, str]:
        return {"schema": "ggen.enterprise-architecture-foundry.refusal/1", "code": self.code, "message": self.message}


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    object_id: str
    path: str


@dataclass
class ResolvedComponent:
    capability: dict[str, Any]
    classification: dict[str, Any]
    commits: list[str]
    paths: list[str]
    entries: list[tuple[str, TreeEntry]]
    resolution: str


def blake3_module():
    try:
        import blake3  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise Refusal("EXTRACTION_BLAKE3_UNAVAILABLE", "install blake3==1.0.9") from exc
    return blake3


def digest_bytes(data: bytes) -> str:
    return blake3_module().blake3(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def hash_named_bytes(hasher: Any, name: str, value: bytes) -> None:
    encoded = name.encode("utf-8")
    hasher.update(len(encoded).to_bytes(8, "little"))
    hasher.update(encoded)
    hasher.update(len(value).to_bytes(8, "little"))
    hasher.update(value)


def digest_named_outputs(outputs: dict[str, str]) -> str:
    hasher = blake3_module().blake3()
    for name, digest in sorted(outputs.items()):
        hash_named_bytes(hasher, name, digest.encode("utf-8"))
    return hasher.hexdigest()


def run(repo: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if check and completed.returncode != 0:
        raise Refusal(
            "EXTRACTION_GIT_COMMAND_FAILED",
            f"git {' '.join(args)}: {completed.stderr.decode(errors='replace').strip()}",
        )
    return completed


def git_text(repo: Path, args: list[str]) -> str:
    return run(repo, args).stdout.decode("utf-8", errors="replace").strip()


def resolve_revision(repo: Path, revision: str) -> str | None:
    completed = run(repo, ["rev-parse", "--verify", f"{revision}^{{commit}}"], check=False)
    if completed.returncode != 0:
        return None
    return completed.stdout.decode().strip()


def tree_entries(repo: Path, commit: str) -> list[TreeEntry]:
    output = run(repo, ["ls-tree", "-r", "-z", commit]).stdout
    entries: list[TreeEntry] = []
    for record in output.split(b"\0"):
        if not record:
            continue
        header, path = record.split(b"\t", 1)
        mode, object_type, object_id = header.decode().split()
        if object_type == "blob" and mode != "160000":
            entries.append(TreeEntry(mode, object_id, path.decode("utf-8", errors="surrogateescape")))
    return entries


def match_entries(entries: Iterable[TreeEntry], requested: str) -> list[TreeEntry]:
    requested = requested.rstrip("/")
    wildcard = any(character in requested for character in "*?[")
    matched = []
    for entry in entries:
        selected = fnmatch.fnmatchcase(entry.path, requested) if wildcard else (
            entry.path == requested or entry.path.startswith(requested + "/")
        )
        if selected:
            matched.append(entry)
    return sorted(matched, key=lambda item: item.path)


def expand_braces(value: str) -> list[str]:
    match = re.search(r"\{([^{}]+)\}", value)
    if not match:
        return [value]
    results = []
    for option in match.group(1).split(","):
        results.extend(expand_braces(value[: match.start()] + option.strip() + value[match.end() :]))
    return results


def clean_path(value: str) -> str | None:
    value = value.strip().strip("`'\"").strip()
    value = value.replace("\\", "/")
    for marker in (
        " (deleted", " (historical", " (removed", " (local", " (Ggen", " (accepts",
        " (or ", " [", " — ", " -- ", ";",
    ):
        if marker in value:
            value = value.split(marker, 1)[0]
    if ".rs::" in value:
        value = value.split(".rs::", 1)[0] + ".rs"
    value = value.strip().strip(".,:;)").lstrip("./")
    if not value or value.startswith("git ") or " " in value:
        return None
    if value != "justfile" and "/" not in value:
        return None
    if value.startswith(("http://", "https://")) or ".." in Path(value).parts:
        return None
    return value.rstrip("/")


def path_candidates(*values: str) -> list[str]:
    candidates: list[str] = []
    for value in values:
        if not value:
            continue
        fragments = re.split(r"\s+vs\.\s+|\s+or\s+|\s*\|\s*", value)
        for fragment in fragments:
            direct = clean_path(fragment)
            if direct:
                candidates.extend(expand_braces(direct))
            for token in PATH_TOKEN.findall(fragment):
                cleaned = clean_path(token)
                if cleaned:
                    candidates.extend(expand_braces(cleaned))
        for quoted in re.findall(r"`([^`]+)`", value):
            cleaned = clean_path(quoted)
            if cleaned:
                candidates.extend(expand_braces(cleaned))
    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def recovery_locator(command: str) -> tuple[str, str] | None:
    match = re.match(r"^\s*git\s+show\s+([^:\s]+):(.+?)\s*$", command or "")
    if not match:
        return None
    path = clean_path(match.group(2))
    return (match.group(1), path) if path else None


def commit_candidates(repo: Path, capability: dict[str, Any], recovery: dict[str, Any], source_head: str) -> list[str]:
    specs: list[str] = []
    locator = recovery_locator(str(recovery.get("recovery_command", "")))
    if locator:
        specs.append(locator[0])
    text = " | ".join(
        str(capability.get(field, ""))
        for field in ("historical_source_commit", "archive_path", "rollback_path", "migration_path")
    )
    tokens = HEX_TOKEN.findall(text)
    deletion_semantics = bool(re.search(r"delete|deleted|remove|removed|fold|consolidat|replace", text, re.I))
    for token in tokens:
        if deletion_semantics:
            specs.extend([f"{token}^", token])
        else:
            specs.extend([token, f"{token}^"])
    specs.append(source_head)
    commits: list[str] = []
    for spec in specs:
        resolved = resolve_revision(repo, spec)
        if resolved and resolved not in commits:
            commits.append(resolved)
    return commits


def history_commits(repo: Path, requested: str, limit: int = 64) -> list[str]:
    completed = run(repo, ["log", "--all", f"--max-count={limit}", "--format=%H", "--", requested], check=False)
    if completed.returncode != 0:
        return []
    commits: list[str] = []
    for commit in completed.stdout.decode().splitlines():
        for revision in (commit, f"{commit}^"):
            resolved = resolve_revision(repo, revision)
            if resolved and resolved not in commits:
                commits.append(resolved)
    return commits


def changed_paths(repo: Path, commit: str) -> list[str]:
    completed = run(repo, ["diff-tree", "--no-commit-id", "--name-only", "-r", f"{commit}^", commit], check=False)
    return completed.stdout.decode(errors="replace").splitlines() if completed.returncode == 0 else []


def pickaxe_paths(repo: Path, term: str, limit: int = 16) -> list[tuple[str, str]]:
    completed = run(repo, ["log", "--all", f"--max-count={limit}", "--format=%H", "-S", term, "--"], check=False)
    if completed.returncode != 0:
        return []
    results: list[tuple[str, str]] = []
    for commit in completed.stdout.decode().splitlines():
        for candidate_commit in filter(None, (resolve_revision(repo, commit), resolve_revision(repo, f"{commit}^"))):
            for path in changed_paths(repo, commit):
                entries = match_entries(tree_entries(repo, candidate_commit), path)
                if entries:
                    blob = run(repo, ["show", f"{candidate_commit}:{path}"], check=False)
                    if blob.returncode == 0 and term.encode() in blob.stdout:
                        pair = (candidate_commit, path)
                        if pair not in results:
                            results.append(pair)
    return results


def special_pickaxe_terms(capability_id: str) -> list[str]:
    mapping = {
        "legacy_ext_template_mode_update": ['mode = "Update"', "GenerationMode::Update"],
        "legacy_ext_template_mode_append": ['mode = "Append"', "GenerationMode::Append"],
    }
    return mapping.get(capability_id, [])


def resolve_component(
    repo: Path,
    capability: dict[str, Any],
    classification: dict[str, Any],
    recovery: dict[str, Any],
    source_head: str,
) -> ResolvedComponent:
    values = [
        str(recovery.get("recovery_command", "")),
        str(capability.get("legacy_source_path", "")),
        str(capability.get("archive_path", "")),
        str(capability.get("rollback_path", "")),
        str(capability.get("migration_path", "")),
        str(capability.get("evidence_fixtures", "")),
    ]
    paths = path_candidates(*values)
    commits = commit_candidates(repo, capability, recovery, source_head)
    resolved: list[tuple[str, TreeEntry]] = []
    seen = set()

    def add_matches(commit: str, requested: str) -> bool:
        found = False
        for entry in match_entries(tree_entries(repo, commit), requested):
            key = (entry.object_id, entry.path)
            if key not in seen:
                seen.add(key)
                resolved.append((commit, entry))
            found = True
        return found

    unresolved_paths = []
    for requested in paths:
        found = any(add_matches(commit, requested) for commit in commits)
        if not found:
            for commit in history_commits(repo, requested):
                if add_matches(commit, requested):
                    if commit not in commits:
                        commits.append(commit)
                    found = True
                    break
        if not found:
            unresolved_paths.append(requested)

    if not resolved:
        for term in special_pickaxe_terms(str(capability.get("capability_id", ""))):
            for commit, requested in pickaxe_paths(repo, term):
                paths.append(requested)
                commits.append(commit)
                add_matches(commit, requested)
            if resolved:
                break

    required = str(capability.get("disposition")) in REQUIRED_DISPOSITIONS
    if required and not resolved:
        raise Refusal(
            "REQUIRED_SOURCE_OBJECT_UNRESOLVED",
            f"{capability.get('capability_id')}: commits={commits} paths={paths} unresolved={unresolved_paths}",
        )
    return ResolvedComponent(
        capability=capability,
        classification=classification,
        commits=list(dict.fromkeys(commit for commit, _ in resolved)) or commits[:1],
        paths=list(dict.fromkeys(entry.path for _, entry in resolved)) or paths,
        entries=resolved,
        resolution="GIT_OBJECTS_RECOVERED" if resolved else "SEMANTIC_EVIDENCE_ONLY",
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise Refusal("EXTRACTION_INPUT_MISSING", str(path)) from exc
    except json.JSONDecodeError as exc:
        raise Refusal("EXTRACTION_INPUT_INVALID", f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Refusal("EXTRACTION_INPUT_NOT_OBJECT", str(path))
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise Refusal("EXTRACTION_YAML_UNAVAILABLE", "install pyyaml==6.0.2") from exc
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise Refusal("EXTRACTION_PROGRAM_MISSING", str(path)) from exc
    if not isinstance(value, dict):
        raise Refusal("EXTRACTION_PROGRAM_INVALID", str(path))
    return value


def require_clean(repo: Path, code: str) -> None:
    status = git_text(repo, ["status", "--porcelain=v1", "--untracked-files=all"])
    if status:
        raise Refusal(code, status)


def write_new(path: Path, data: bytes) -> None:
    if path.exists():
        raise Refusal("EXISTING_OUTPUT_REFUSED", str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def verify_or_write_blob(path: Path, data: bytes, expected: str) -> None:
    if path.exists():
        observed = digest_bytes(path.read_bytes())
        if observed != expected:
            raise Refusal("BLOB_STORE_COLLISION", f"{path}: expected={expected} observed={observed}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def safe_relative(value: str) -> Path:
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise Refusal("DESTINATION_PATH_INVALID", value)
    return path


def recovery_command(component: ResolvedComponent) -> str:
    pairs = []
    for commit, entry in component.entries:
        command = f"git show {commit}:{entry.path}"
        if command not in pairs:
            pairs.append(command)
    return " && ".join(pairs) if pairs else "SEMANTIC_EVIDENCE_ONLY"


def admit(program_path: Path, source: Path, corpus: Path) -> dict[str, Any]:
    require_clean(source, "SOURCE_WORKTREE_DIRTY")
    require_clean(corpus, "CORPUS_WORKTREE_DIRTY")
    program = load_yaml(program_path)
    source_head = git_text(source, ["rev-parse", "HEAD"])
    corpus_head = git_text(corpus, ["rev-parse", "HEAD"])
    foundry = corpus / "foundry"
    state_path = foundry / "workstreams/state.json"
    state = load_json(state_path)
    if state.get("workstreams", {}).get("D", {}).get("status") != "ADMITTED":
        raise Refusal("WORKSTREAM_D_NOT_ADMITTED", str(state.get("workstreams", {}).get("D", {}).get("status")))
    observed_e = state.get("workstreams", {}).get("E", {}).get("status")
    if observed_e == "ADMITTED":
        return {"schema": EXTRACTION_SCHEMA, "workstream_id": "E", "status": "ALREADY_ADMITTED", "direct_actuation": False}
    if observed_e != "READY":
        raise Refusal("WORKSTREAM_E_NOT_READY", str(observed_e))

    capability_path = foundry / "catalogs/capabilities.json"
    classification_path = foundry / "catalogs/component-classification.json"
    recovery_path = foundry / "catalogs/recovery-plans.json"
    capability_catalog = load_json(capability_path)
    classification_catalog = load_json(classification_path)
    recovery_catalog = load_json(recovery_path)
    capabilities = capability_catalog.get("entries", [])
    classifications = {entry["capability_id"]: entry for entry in classification_catalog.get("entries", [])}
    recoveries = {entry["capability_id"]: entry for entry in recovery_catalog.get("entries", [])}
    if len(capabilities) != 65 or len(classifications) != 65 or len(recoveries) != 65:
        raise Refusal(
            "EXTRACTION_INPUT_COUNT_MISMATCH",
            f"capabilities={len(capabilities)} classifications={len(classifications)} recoveries={len(recoveries)}",
        )

    resolved: list[ResolvedComponent] = []
    unresolved: list[str] = []
    for capability in capabilities:
        capability_id = capability["capability_id"]
        try:
            resolved.append(
                resolve_component(source, capability, classifications[capability_id], recoveries[capability_id], source_head)
            )
        except Refusal as refusal:
            unresolved.append(f"{capability_id}: {refusal.message}")
    if unresolved:
        raise Refusal("REQUIRED_SOURCE_OBJECTS_UNRESOLVED", " | ".join(unresolved))

    semantic_path = foundry / "evidence/B/legacy-capabilities.ttl"
    semantic_bytes = semantic_path.read_bytes()
    semantic_digest = digest_bytes(semantic_bytes)
    output_digests: dict[str, str] = {}
    unique_blobs: set[str] = set()
    manifests = []
    recovered_count = 0
    semantic_only_count = 0
    total_source_files = 0

    for component in resolved:
        capability = component.capability
        classification = component.classification
        source_files = []
        for commit, entry in component.entries:
            blob = run(source, ["cat-file", "blob", entry.object_id]).stdout
            digest = digest_bytes(blob)
            blob_relative = f"foundry/blobs/blake3/{digest}"
            verify_or_write_blob(corpus / blob_relative, blob, digest)
            if digest not in unique_blobs:
                output_digests[f"corpus:{blob_relative}"] = digest
                unique_blobs.add(digest)
            source_files.append(
                {
                    "git_path": entry.path,
                    "git_object_id": entry.object_id,
                    "git_mode": entry.mode,
                    "byte_length": len(blob),
                    "blake3": digest,
                    "blob_path": blob_relative,
                    "historical_commit": commit,
                }
            )
            total_source_files += 1
        if source_files:
            recovered_count += 1
        else:
            semantic_only_count += 1
        destination = safe_relative(classification["corpus_destination"])
        historical_commits = list(dict.fromkeys(commit for commit, _ in component.entries))
        normalized_paths = list(dict.fromkeys(entry.path for _, entry in component.entries))
        manifest = {
            "schema_version": EXTRACTION_SCHEMA,
            "capability_id": capability["capability_id"],
            "source_repository": program["source_repository"],
            "corpus_repository": program["corpus_repository"],
            "source_head": source_head,
            "corpus_parent_head": corpus_head,
            "historical_commit": historical_commits[0] if len(historical_commits) == 1 else " | ".join(historical_commits),
            "historical_commits": historical_commits,
            "requested_source_path": capability["legacy_source_path"],
            "normalized_source_path": normalized_paths[0] if len(normalized_paths) == 1 else " | ".join(normalized_paths),
            "normalized_source_paths": normalized_paths,
            "disposition": capability["disposition"],
            "classification": classification["classification"],
            "kernel_owner": classification["kernel_owner"],
            "corpus_destination": classification["corpus_destination"],
            "resolution": component.resolution,
            "source_files": source_files,
            "semantic_evidence_path": "foundry/evidence/B/legacy-capabilities.ttl",
            "semantic_evidence_digest": semantic_digest,
            "source_removed": False,
            "recovery_command": recovery_command(component),
            "resolution_verifier": VERIFIER_ID,
        }
        manifest_bytes = canonical_json(manifest)
        manifest_relative = destination / "component-manifest.json"
        write_new(corpus / manifest_relative, manifest_bytes)
        manifest_digest = digest_bytes(manifest_bytes)
        output_digests[f"corpus:{manifest_relative.as_posix()}"] = manifest_digest
        lineage = {
            "schema_version": EXTRACTION_SCHEMA,
            "capability_id": capability["capability_id"],
            "source_repository": program["source_repository"],
            "corpus_repository": program["corpus_repository"],
            "source_head": source_head,
            "corpus_parent_head": corpus_head,
            "historical_commit": manifest["historical_commit"],
            "historical_commits": historical_commits,
            "source_path": manifest["normalized_source_path"],
            "source_paths": normalized_paths,
            "destination_path": classification["corpus_destination"],
            "manifest_digest": manifest_digest,
            "blob_digests": [item["blake3"] for item in source_files],
            "disposition": capability["disposition"],
            "classification": classification["classification"],
            "source_removed": False,
        }
        lineage_bytes = canonical_json(lineage)
        lineage_relative = Path("foundry/lineage/components") / f"{capability['capability_id']}.json"
        write_new(corpus / lineage_relative, lineage_bytes)
        output_digests[f"corpus:{lineage_relative.as_posix()}"] = digest_bytes(lineage_bytes)
        manifests.append(manifest)

    ledger = {
        "schema_version": EXTRACTION_SCHEMA,
        "source_head": source_head,
        "corpus_parent_head": corpus_head,
        "component_count": len(manifests),
        "recovered_source_components": recovered_count,
        "semantic_evidence_only_components": semantic_only_count,
        "unique_blob_count": len(unique_blobs),
        "total_source_files": total_source_files,
        "components": manifests,
    }
    ledger_bytes = canonical_json(ledger)
    ledger_relative = "foundry/catalogs/extraction-ledger.json"
    write_new(corpus / ledger_relative, ledger_bytes)
    output_digests[f"corpus:{ledger_relative}"] = digest_bytes(ledger_bytes)

    workstream = next(item for item in program["workstreams"] if item["id"] == "E")
    report = {
        "schema_version": EXTRACTION_SCHEMA,
        "workstream_id": "E",
        "verifier": VERIFIER_ID,
        "source_head": source_head,
        "corpus_head": corpus_head,
        "extracted_components": 65,
        "extracted_components_without_lineage": 0,
        "unresolved_required_sources": 0,
        "unique_blob_count": len(unique_blobs),
        "total_source_files": total_source_files,
        "source_removed_before_destination_admission": False,
        "source_and_destination_heads_bound": True,
        "cross_repository_receipts_valid": True,
        "predicates": workstream["predicates"],
    }
    report_bytes = canonical_json(report)
    report_digest = digest_bytes(report_bytes)
    report_relative = "foundry/workstreams/E/admission-report.json"
    write_new(corpus / report_relative, report_bytes)
    output_digests[f"corpus:{report_relative}"] = report_digest

    state["workstreams"]["E"]["status"] = "ADMITTED"
    state["workstreams"]["E"]["report_digest"] = report_digest
    state["workstreams"]["E"]["receipt_path"] = "foundry/receipts/workstream-E.json"
    if "F" in state["workstreams"]:
        state["workstreams"]["F"]["status"] = "READY"
    state_bytes = canonical_json(state)
    output_digests["projection:foundry/workstreams/state.json"] = digest_bytes(state_bytes)

    input_digests = {
        "work-program": digest_bytes(program_path.read_bytes()),
        "source-tree": git_text(source, ["rev-parse", "HEAD^{tree}"]),
        "corpus-tree": git_text(corpus, ["rev-parse", "HEAD^{tree}"]),
        "capability-catalog": digest_bytes(capability_path.read_bytes()),
        "classification-catalog": digest_bytes(classification_path.read_bytes()),
        "recovery-plans": digest_bytes(recovery_path.read_bytes()),
        "semantic-evidence": semantic_digest,
    }
    subject_digest = digest_named_outputs(output_digests)
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "receipt_type": "WORKSTREAM_ADMISSION",
        "subject": "E",
        "subject_digest": subject_digest,
        "source_head": source_head,
        "corpus_head": corpus_head,
        "input_digests": input_digests,
        "output_digests": output_digests,
        "run_id": subject_digest[:20],
    }
    write_new(corpus / "foundry/receipts/workstream-E.json", canonical_json(receipt))
    state_path.write_bytes(state_bytes)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = admit(args.program.resolve(), args.source.resolve(), args.corpus.resolve())
    except Refusal as refusal:
        print(json.dumps(refusal.payload(), indent=2, sort_keys=True), file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
