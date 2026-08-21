#!/usr/bin/env python3
"""Shared helpers for appliance/bin/ scripts.

Consolidates the sha256_file() and read_json() implementations that were
previously duplicated (and, for sha256_file, had drifted into two
byte-identical but memory-behavior-different variants) across appliance/bin/'s
multi-function scripts. See tickets/GL-EXP-013.md.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def typed_canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest_sources(root: Path, sources: list[str]) -> tuple[str, list[str]]:
    digest = hashlib.sha256()
    missing: list[str] = []
    for rel in sorted(sources):
        path = root / rel
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        if path.is_file():
            digest.update(path.read_bytes())
        else:
            missing.append(rel)
            digest.update(b"MISSING")
        digest.update(b"\0")
    return digest.hexdigest(), missing


def check_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in report.get("checks", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
