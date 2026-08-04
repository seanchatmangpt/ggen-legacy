#!/usr/bin/env python3
"""Dependency-free verifier for GL-AUTO-001."""

from __future__ import annotations

import filecmp
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "autonomic_finish.py"
FIXTURE = ROOT / "fixtures" / "autonomic" / "conversation.json"


def run(input_path: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(input_path), "--output", str(output)],
        text=True,
        capture_output=True,
        check=False,
    )


def compare_trees(left: Path, right: Path) -> None:
    comparison = filecmp.dircmp(left, right)
    if comparison.left_only or comparison.right_only or comparison.funny_files:
        raise AssertionError("REPLAY_FILE_SET_MISMATCH")
    for filename in comparison.common_files:
        if (left / filename).read_bytes() != (right / filename).read_bytes():
            raise AssertionError(f"REPLAY_BYTES_MISMATCH:{filename}")
    for dirname in comparison.common_dirs:
        compare_trees(left / dirname, right / dirname)


def write_case(root: Path, payload: dict) -> Path:
    path = root / "case.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ggen-auto-") as temp:
        temp_root = Path(temp)
        first = temp_root / "first"
        second = temp_root / "second"
        a = run(FIXTURE, first)
        b = run(FIXTURE, second)
        assert a.returncode == 0, a.stderr
        assert b.returncode == 0, b.stderr
        compare_trees(first, second)

        receipt = json.loads((first / "RECEIPT.json").read_text(encoding="utf-8"))
        assert receipt["claim_ceiling"] == "DETERMINISTIC_CONVERSATION_PROJECTION_ONLY"
        assert receipt["gap_count"] > 0
        assert receipt["standing"] == "PARTIAL_ALIVE"
        assert (first / "CLAUDE.md").exists()
        assert (first / "ppddl" / "problem.pddl").exists()

        base = json.loads(FIXTURE.read_text(encoding="utf-8"))

        duplicate = json.loads(json.dumps(base))
        duplicate["concepts"].append(dict(duplicate["concepts"][0]))
        result = run(write_case(temp_root, duplicate), temp_root / "duplicate")
        assert result.returncode == 2
        assert "REFUSED:DUPLICATE_CONCEPT" in result.stderr

        unknown = json.loads(json.dumps(base))
        unknown["concepts"][0]["standing"] = "DONE"
        result = run(write_case(temp_root, unknown), temp_root / "unknown")
        assert result.returncode == 2
        assert "REFUSED:UNKNOWN_STANDING" in result.stderr

        bad_projection = json.loads(json.dumps(base))
        bad_projection["projections"] = ["execute"]
        result = run(write_case(temp_root, bad_projection), temp_root / "projection")
        assert result.returncode == 2
        assert "REFUSED:UNKNOWN_PROJECTION" in result.stderr

        shutil.rmtree(first)
        shutil.rmtree(second)

    print("GL_AUTO_001_VERIFIER_ALIVE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
