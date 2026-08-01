#!/usr/bin/env python3
"""Cross real subprocess and filesystem boundaries for the reconstitution contract."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifiers" / "verify_ecosystem_reconstitution.py"
MANIFEST = ROOT / "authority" / "ecosystem-reconstitution" / "2026-07-31.repositories.json"


def run_verify(manifest: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VERIFIER),
            "verify",
            "--manifest",
            str(manifest),
            "--output",
            str(output),
            "--digest-mode",
            "sha256-observation",
        ],
        text=True,
        capture_output=True,
    )


def require_refusal(base: dict, mutate, expected_code: str, temp: Path) -> None:
    specimen = json.loads(json.dumps(base))
    mutate(specimen)
    manifest = temp / f"{expected_code}.json"
    manifest.write_text(json.dumps(specimen), encoding="utf-8")
    result = run_verify(manifest, temp / f"{expected_code}-out")
    assert result.returncode == 2, (expected_code, result.stdout, result.stderr)
    payload = json.loads(result.stderr)
    assert payload["code"] == expected_code, payload


def main() -> int:
    base = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="ggen-legacy-reconstitution-") as directory:
        temp = Path(directory)
        first = temp / "first"
        second = temp / "second"
        one = run_verify(MANIFEST, first)
        two = run_verify(MANIFEST, second)
        assert one.returncode == 0, (one.stdout, one.stderr)
        assert two.returncode == 0, (two.stdout, two.stderr)
        first_files = sorted(path.relative_to(first) for path in first.rglob("*") if path.is_file())
        second_files = sorted(path.relative_to(second) for path in second.rglob("*") if path.is_file())
        assert first_files == second_files == [Path("plan.json"), Path("receipt.json"), Path("report.json")]
        for relative in first_files:
            assert (first / relative).read_bytes() == (second / relative).read_bytes(), relative

        require_refusal(
            base,
            lambda value: value["repositories"].append(json.loads(json.dumps(value["repositories"][0]))),
            "RECON-REPOSITORY-002",
            temp,
        )
        require_refusal(
            base,
            lambda value: value["repositories"][0].__setitem__("canonical_reconstruction_sha", "bad"),
            "RECON-SHA-002",
            temp,
        )
        require_refusal(
            base,
            lambda value: value["repositories"][0].__setitem__("depends_on", ["seanchatmangpt/ggen-legacy"]),
            "RECON-DEPENDENCY-004",
            temp,
        )
        require_refusal(
            base,
            lambda value: value.__setitem__("direct_actuation", True),
            "RECON-ACTUATION-001",
            temp,
        )
        require_refusal(
            base,
            lambda value: value["repositories"][-1].__setitem__("product_reconstitution", True),
            "RECON-TRANSPORT-001",
            temp,
        )
        require_refusal(
            base,
            lambda value: value["repositories"][1].__setitem__("canonical_reconstruction_sha", value["repositories"][0]["canonical_reconstruction_sha"]),
            "RECON-SOURCE-006",
            temp,
        )

        report = json.loads((first / "report.json").read_text())
        assert report["exact_repository_set"] is True
        assert report["dependency_closed"] is True
        assert report["source_objects_bound"] >= 19
        assert report["direct_actuation"] is False
        print(
            json.dumps(
                {
                    "schema": "ggen-legacy.ecosystem-reconstitution.test/v1",
                    "standing": "PARTIAL_ALIVE",
                    "deterministic_files": len(first_files),
                    "typed_refusals": 6,
                    "repositories": 19,
                    "source_objects": report["source_objects_bound"],
                    "direct_actuation": False,
                    "blake3_execution": "BLOCKED_IN_LOCAL_RUNTIME",
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
