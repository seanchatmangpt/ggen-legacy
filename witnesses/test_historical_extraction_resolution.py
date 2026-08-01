#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "verifiers" / "admit_historical_extraction.py"
spec = importlib.util.spec_from_file_location("historical_extraction", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def commit(repo: Path, message: str) -> str:
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-m", message],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return git(repo, "rev-parse", "HEAD")


def capability(identifier: str, historical: str, path: str, disposition: str = "REPLACED") -> dict:
    return {
        "capability_id": identifier,
        "historical_source_commit": historical,
        "legacy_source_path": path,
        "archive_path": "",
        "rollback_path": "",
        "migration_path": "",
        "evidence_fixtures": "",
        "disposition": disposition,
    }


def classification(identifier: str) -> dict:
    return {"capability_id": identifier, "classification": "CORPUS", "kernel_owner": "ggen-legacy", "corpus_destination": f"foundry/corpus/components/{identifier}"}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="historical-extraction-") as directory:
        repo = Path(directory) / "source"
        repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(repo)], check=True)

        deleted = repo / "crates/deleted/src"
        deleted.mkdir(parents=True)
        (deleted / "lib.rs").write_text("pub fn alive() {}\n")
        (repo / "justfile").write_text("sync-dry:\n    ggen sync --dry_run true\n")
        live = repo / "crates/engine/src/verbs"
        live.mkdir(parents=True)
        (live / "sync.rs").write_text("pub fn sync_run(dry_run: bool) {}\n")
        add_commit = commit(repo, "add historical source")

        subprocess.run(["git", "-C", str(repo), "rm", "-r", "crates/deleted"], check=True, stdout=subprocess.DEVNULL)
        delete_commit = commit(repo, "delete historical source")
        source_head = git(repo, "rev-parse", "HEAD")

        deleted_capability = capability("deleted", delete_commit[:12] + " (deleted)", "crates/deleted/ (deleted whole crate)")
        deleted_recovery = {"recovery_command": f"git show {delete_commit[:12]}^:crates/deleted/"}
        resolved = module.resolve_component(repo, deleted_capability, classification("deleted"), deleted_recovery, source_head)
        assert resolved.resolution == "GIT_OBJECTS_RECOVERED"
        assert any(commit_id == add_commit and entry.path == "crates/deleted/src/lib.rs" for commit_id, entry in resolved.entries)

        alternative = capability(
            "alternative",
            "UNKNOWN",
            "justfile (`sync-dry:` recipe) vs. crates/engine/src/verbs/sync.rs (--dry-run is a bare switch)",
        )
        alternative_resolved = module.resolve_component(repo, alternative, classification("alternative"), {}, source_head)
        paths = {entry.path for _, entry in alternative_resolved.entries}
        assert "justfile" in paths
        assert "crates/engine/src/verbs/sync.rs" in paths

        history = capability("history", "UNKNOWN", "crates/deleted/")
        history_resolved = module.resolve_component(repo, history, classification("history"), {}, source_head)
        assert any(entry.path == "crates/deleted/src/lib.rs" for _, entry in history_resolved.entries)

        missing = capability("missing", "UNKNOWN", "crates/never-existed/")
        try:
            module.resolve_component(repo, missing, classification("missing"), {}, source_head)
        except module.Refusal as refusal:
            assert refusal.code == "REQUIRED_SOURCE_OBJECT_UNRESOLVED"
        else:
            raise AssertionError("missing required source was admitted")

        print(json.dumps({
            "schema": "ggen.enterprise-architecture-foundry.historical-resolution-test/1",
            "standing": "ALIVE",
            "deletion_parent_recovered": True,
            "alternative_paths_recovered": True,
            "path_history_recovered": True,
            "missing_required_source_refused": True,
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
