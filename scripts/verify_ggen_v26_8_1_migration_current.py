#!/usr/bin/env python3
"""Verify the original v26.8.1 migration without freezing its successor forever.

The original migration is replayed against the exact historical corpus head.
Any later mutation of a file inherited through that migration must then be
listed in authority/ggen-v26.8.1-successor.json and remain byte-identical to
the admitted origin commit.  This preserves the migration proof while making
post-migration hardening explicit instead of weakening lineage verification.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("migrations/ggen-v26.8.1/migration-manifest.json")
SUCCESSOR = Path("authority/ggen-v26.8.1-successor.json")
ORIGINAL_VERIFIER = Path("scripts/verify_ggen_v26_8_1_migration.py")
ACTIVE_ROOTS = (
    Path("docs/v26.8.1"),
    Path("ontology/v26.8.1"),
    Path("planning/v26.8.1"),
    Path("tools/v26.8.1"),
    Path("packs/legacy-equivalence-verifier-pack"),
)


class Refusal(RuntimeError):
    pass


def run(argv: list[str], cwd: Path, timeout: int = 1200) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout)


def require(argv: list[str], cwd: Path, timeout: int = 1200) -> str:
    p = run(argv, cwd, timeout)
    if p.returncode:
        raise Refusal(
            "REFUSED:COMMAND_FAILED argv=" + json.dumps(argv) +
            f" exit={p.returncode} stdout={p.stdout[-4000:]} stderr={p.stderr[-4000:]}"
        )
    return p.stdout


def git_head(root: Path) -> str:
    value = require(["git", "rev-parse", "HEAD"], root).strip()
    if len(value) != 40:
        raise Refusal("REFUSED:CANDIDATE_HEAD_UNAVAILABLE")
    return value


def safe_path(value: Any) -> str:
    text = str(value)
    path = Path(text)
    if not text or path.is_absolute() or ".." in path.parts:
        raise Refusal(f"REFUSED:UNSAFE_SUCCESSOR_PATH:{text}")
    return path.as_posix()


def tracked_worktree_blob(root: Path, rel: str) -> str | None:
    path = root / rel
    if not path.is_file():
        return None
    value = require(["git", "hash-object", "--", rel], root).strip()
    return value or None


def tree_blob(root: Path, commit: str, rel: str) -> str | None:
    p = run(["git", "ls-tree", commit, "--", rel], root, 30)
    if p.returncode:
        raise Refusal(f"REFUSED:GIT_TREE_QUERY_FAILED:{commit}:{rel}:{p.stderr.strip()}")
    line = p.stdout.strip()
    if not line:
        return None
    parts = line.split()
    if len(parts) < 3 or parts[1] != "blob":
        raise Refusal(f"REFUSED:NON_BLOB_SUCCESSOR_PATH:{commit}:{rel}")
    return parts[2]


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return run(["git", "merge-base", "--is-ancestor", ancestor, descendant], root, 30).returncode == 0


def lineage_paths(root: Path, manifest: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for component in manifest["components"]:
        evidence = root / safe_path(component["migration_evidence"])
        lineage = json.loads(evidence.read_text())
        for record in lineage.get("files", []):
            paths.add(safe_path(record["destination_path"]))
    return paths


def verify_successor(root: Path, candidate: str) -> dict[str, Any]:
    manifest = json.loads((root / MANIFEST).read_text())
    authority = json.loads((root / SUCCESSOR).read_text())
    if authority.get("schema") != "ggen.legacy.migration-successor/1":
        raise Refusal("REFUSED:SUCCESSOR_SCHEMA")
    corpus = str(manifest["corpus_head"])
    if authority.get("corpus_head") != corpus:
        raise Refusal("REFUSED:SUCCESSOR_CORPUS_HEAD_MISMATCH")
    if not is_ancestor(root, corpus, candidate):
        raise Refusal(f"REFUSED:CORPUS_HEAD_UNRELATED corpus={corpus} candidate={candidate}")

    inherited = lineage_paths(root, manifest)
    entries: dict[str, dict[str, Any]] = {}
    for raw in authority.get("entries", []):
        rel = safe_path(raw.get("path"))
        if rel in entries:
            raise Refusal(f"REFUSED:DUPLICATE_SUCCESSOR_PATH:{rel}")
        kind = str(raw.get("kind"))
        if kind not in {"MODIFIED", "ADDED"}:
            raise Refusal(f"REFUSED:SUCCESSOR_KIND:{rel}:{kind}")
        origin = str(raw.get("origin_commit", ""))
        expected = str(raw.get("git_blob", ""))
        if len(origin) != 40 or len(expected) != 40:
            raise Refusal(f"REFUSED:SUCCESSOR_IDENTITY:{rel}")
        if not is_ancestor(root, corpus, origin) or not is_ancestor(root, origin, candidate):
            raise Refusal(f"REFUSED:SUCCESSOR_ORIGIN_UNRELATED:{rel}:{origin}")
        origin_blob = tree_blob(root, origin, rel)
        current_blob = tracked_worktree_blob(root, rel)
        corpus_blob = tree_blob(root, corpus, rel)
        if origin_blob != expected:
            raise Refusal(f"REFUSED:SUCCESSOR_ORIGIN_BLOB_DRIFT:{rel}:expected={expected}:observed={origin_blob}")
        if current_blob != expected:
            raise Refusal(f"REFUSED:SUCCESSOR_CURRENT_BLOB_DRIFT:{rel}:expected={expected}:observed={current_blob}")
        if kind == "MODIFIED":
            if rel not in inherited or corpus_blob is None or corpus_blob == expected:
                raise Refusal(f"REFUSED:SUCCESSOR_MODIFICATION_NOT_PROVEN:{rel}")
        else:
            if rel in inherited or corpus_blob is not None:
                raise Refusal(f"REFUSED:SUCCESSOR_ADDITION_NOT_PROVEN:{rel}")
        entries[rel] = dict(raw)

    drifted: list[str] = []
    for rel in sorted(inherited):
        historical = tree_blob(root, corpus, rel)
        current = tracked_worktree_blob(root, rel)
        if current != historical:
            drifted.append(rel)
            entry = entries.get(rel)
            if entry is None or entry.get("kind") != "MODIFIED":
                raise Refusal(f"REFUSED:UNMAPPED_INHERITED_DRIFT:{rel}")

    admitted_modified = sorted(rel for rel, entry in entries.items() if entry["kind"] == "MODIFIED")
    if drifted != admitted_modified:
        raise Refusal(
            "REFUSED:SUCCESSOR_MODIFICATION_SET_MISMATCH observed=" +
            json.dumps(drifted) + " admitted=" + json.dumps(admitted_modified)
        )
    return {
        "schema": "ggen.legacy.migration-successor.verification/1",
        "corpus_head": corpus,
        "candidate_head": candidate,
        "admitted_origin_commits": sorted({str(x["origin_commit"]) for x in entries.values()}),
        "modified_inherited_files": admitted_modified,
        "added_successor_files": sorted(rel for rel, entry in entries.items() if entry["kind"] == "ADDED"),
        "standing": "ALIVE",
        "claim_ceiling": "POST_MIGRATION_EVOLUTION_ONLY",
    }


def historical_checkout(root: Path, target: Path, candidate: str, corpus: str) -> None:
    require(["git", "clone", "--no-hardlinks", "--no-checkout", "--quiet", str(root), str(target)], target.parent, 300)
    require(["git", "checkout", "--detach", candidate], target, 60)
    for rel in ACTIVE_ROOTS:
        absolute = target / rel
        if absolute.is_dir():
            shutil.rmtree(absolute)
        elif absolute.exists():
            absolute.unlink()
    require(["git", "checkout", corpus, "--", *[x.as_posix() for x in ACTIVE_ROOTS]], target, 60)


def verify_current_successor_behavior(root: Path) -> list[dict[str, Any]]:
    commands = [
        ["cargo", "fmt", "--manifest-path", "tools/v26.8.1/Cargo.toml", "--all", "--", "--check"],
        ["cargo", "test", "--manifest-path", "tools/v26.8.1/Cargo.toml", "--locked", "--all-targets"],
    ]
    receipts = []
    for argv in commands:
        p = run(argv, root, 1200)
        receipts.append({"argv": argv, "exit_status": p.returncode})
        if p.returncode:
            raise Refusal(
                "REFUSED:SUCCESSOR_BEHAVIOR_FAILED argv=" + json.dumps(argv) +
                f" stdout={p.stdout[-4000:]} stderr={p.stderr[-4000:]}"
            )
    return receipts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--destination-root", type=Path, default=ROOT)
    ap.add_argument("--report", type=Path, default=Path("migrations/ggen-v26.8.1/verifier-report.json"))
    args = ap.parse_args()
    root = args.destination_root.resolve()
    source = args.source_root.resolve()
    report_path = args.report if args.report.is_absolute() else root / args.report
    try:
        candidate = git_head(root)
        manifest = json.loads((root / MANIFEST).read_text())
        successor = verify_successor(root, candidate)
        corpus = str(manifest["corpus_head"])
        with tempfile.TemporaryDirectory(prefix="ggen-v26-8-1-historical-") as raw:
            historical = Path(raw) / "corpus"
            historical_checkout(root, historical, candidate, corpus)
            historical_report = historical / "migrations/ggen-v26.8.1/verifier-report.json"
            p = run(
                [
                    sys.executable,
                    str(root / ORIGINAL_VERIFIER),
                    "--source-root", str(source),
                    "--destination-root", str(historical),
                    "--report", str(historical_report),
                ],
                root,
                1800,
            )
            if p.returncode:
                sys.stdout.write(p.stdout)
                sys.stderr.write(p.stderr)
                return p.returncode
            base_report = json.loads(historical_report.read_text())
        behavior = verify_current_successor_behavior(root)
        base_report["historical_corpus_replay"] = {
            "corpus_head": corpus,
            "standing": "ALIVE",
            "byte_identity": "SOURCE_EQUALS_HISTORICAL_CORPUS",
        }
        base_report["successor_admission"] = successor
        base_report["successor_behavior_receipts"] = behavior
        base_report["candidate_head"] = candidate
        base_report["standing"] = "PARTIAL_ALIVE"
        base_report["claim_ceiling"] = "HISTORICAL_MIGRATION_PLUS_EXPLICIT_SUCCESSOR_EVOLUTION"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(base_report, indent=2, sort_keys=True) + "\n")
        print(json.dumps({
            "candidate_head": candidate,
            "historical_corpus": "ALIVE",
            "successor_admission": "ALIVE",
            "modified_inherited_files": len(successor["modified_inherited_files"]),
            "added_successor_files": len(successor["added_successor_files"]),
            "standing": "PARTIAL_ALIVE",
        }, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, Refusal, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
