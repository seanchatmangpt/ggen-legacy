#!/usr/bin/env python3
"""Execute historical extraction with process-local Git object caches."""
from __future__ import annotations

import functools
import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "verifiers" / "admit_historical_extraction.py"
spec = importlib.util.spec_from_file_location("historical_extraction_runtime", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

_original_tree_entries = module.tree_entries
_original_history_commits = module.history_commits
_original_resolve_revision = module.resolve_revision
_original_changed_paths = module.changed_paths


@functools.lru_cache(maxsize=2048)
def _tree_entries(repo: str, commit: str):
    return tuple(_original_tree_entries(Path(repo), commit))


@functools.lru_cache(maxsize=4096)
def _history_commits(repo: str, requested: str, limit: int = 64):
    return tuple(_original_history_commits(Path(repo), requested, limit))


@functools.lru_cache(maxsize=4096)
def _resolve_revision(repo: str, revision: str):
    return _original_resolve_revision(Path(repo), revision)


@functools.lru_cache(maxsize=4096)
def _changed_paths(repo: str, commit: str):
    return tuple(_original_changed_paths(Path(repo), commit))


module.tree_entries = lambda repo, commit: list(_tree_entries(str(Path(repo).resolve()), commit))
module.history_commits = lambda repo, requested, limit=64: list(_history_commits(str(Path(repo).resolve()), requested, limit))
module.resolve_revision = lambda repo, revision: _resolve_revision(str(Path(repo).resolve()), revision)
module.changed_paths = lambda repo, commit: list(_changed_paths(str(Path(repo).resolve()), commit))

if __name__ == "__main__":
    raise SystemExit(module.main())
