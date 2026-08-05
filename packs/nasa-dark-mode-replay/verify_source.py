#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


class Refusal(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}:{detail}")
        self.code = code
        self.detail = detail


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise Refusal(code, detail)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise Refusal("REQUIRED_EVIDENCE_MISSING", str(path)) from exc
    except json.JSONDecodeError as exc:
        raise Refusal("EVIDENCE_JSON_INVALID", f"{path}:{exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--require-git-head", action="store_true")
    args = parser.parse_args()

    contract = read_json(args.contract)
    source_repo = args.source_repo.resolve()
    source = contract["source"]
    checks: list[dict[str, str]] = []

    try:
        if args.require_git_head:
            try:
                head = subprocess.check_output(
                    ["git", "-C", str(source_repo), "rev-parse", "HEAD"],
                    text=True,
                    stderr=subprocess.STDOUT,
                ).strip()
            except (subprocess.CalledProcessError, FileNotFoundError) as exc:
                raise Refusal("SOURCE_GIT_UNAVAILABLE", str(exc)) from exc
            require(head == source["head"], "SOURCE_HEAD_MISMATCH", f"{head}!={source['head']}")
            checks.append({"id": "source-head", "state": "PASS", "detail": head})
        else:
            checks.append({"id": "source-head", "state": "PARTIAL", "detail": "object-identity mode"})

        for relative, expected in sorted(contract["sourceObjects"].items()):
            path = source_repo / relative
            require(path.is_file(), "SOURCE_SURFACE_MISSING", relative)
            observed = git_blob_sha(path)
            require(observed == expected, "SOURCE_OBJECT_ID_MISMATCH", f"{relative}:{observed}!={expected}")
            checks.append({"id": f"object:{relative}", "state": "PASS", "detail": observed})

        pack = source_repo / source["pack"]
        manufacture = read_json(pack / ".ggen/evidence/manufacture.json")
        expected_manufacture = contract["manufacture"]
        require(manufacture.get("schema") == expected_manufacture["schema"], "MANUFACTURE_SCHEMA_MISMATCH", str(manufacture.get("schema")))
        require(manufacture.get("standing") == "ALIVE", "MANUFACTURE_NOT_ALIVE", str(manufacture.get("standing")))
        require(manufacture.get("generatedRoot") == expected_manufacture["generatedRoot"], "GENERATED_ROOT_MISMATCH", str(manufacture.get("generatedRoot")))
        require(manufacture.get("artifactCount") == expected_manufacture["artifactCount"], "ARTIFACT_COUNT_MISMATCH", str(manufacture.get("artifactCount")))
        require(manufacture.get("replay") == expected_manufacture["replay"], "MANUFACTURE_REPLAY_MISMATCH", str(manufacture.get("replay")))
        checks.append({"id": "manufacture", "state": "PASS", "detail": manufacture["generatedRoot"]})

        runtime = read_json(pack / "generated/.ggen/evidence/nasa-dark-mode.json")
        expected_runtime = contract["runtime"]
        require(runtime.get("schema") == expected_runtime["verifierSchema"], "RUNTIME_SCHEMA_MISMATCH", str(runtime.get("schema")))
        require(runtime.get("failed") == expected_runtime["failed"], "RUNTIME_FAILURES_PRESENT", str(runtime.get("failed")))
        require(runtime.get("assertions", 0) >= expected_runtime["assertionsAtLeast"], "ASSERTION_FLOOR_NOT_MET", str(runtime.get("assertions")))
        for key in expected_runtime["requiredAlive"]:
            require(runtime["standings"].get(key) == "ALIVE", "REQUIRED_STANDING_NOT_ALIVE", f"{key}:{runtime['standings'].get(key)}")
        digest = runtime.get("missionFeedReceipt", {}).get("digest")
        require(digest == expected_runtime["missionFeedDigest"], "MISSION_FEED_DIGEST_MISMATCH", str(digest))
        checks.append({"id": "runtime-source-capsule", "state": "PASS", "detail": f"{runtime['assertions']} assertions"})

        roku_zip = pack / "generated/.ggen/evidence/nasa-dark-mode-roku.zip"
        require(roku_zip.is_file(), "ROKU_PACKAGE_MISSING", str(roku_zip))
        with zipfile.ZipFile(roku_zip) as archive:
            names = set(archive.namelist())
        required_zip = {
            "manifest",
            "source/main.brs",
            "components/NasaDarkModeScene.xml",
            "components/NasaDarkModeScene.brs",
            "components/MissionFeedTask.xml",
            "components/MissionFeedTask.brs",
            "data/mission-feed.json",
        }
        missing = sorted(required_zip - names)
        require(not missing, "ROKU_PACKAGE_INCOMPLETE", ",".join(missing))
        checks.append({"id": "roku-package", "state": "PASS", "detail": f"{len(names)} entries"})

        browser_path = pack / "generated/.ggen/evidence/browser-e2e.json"
        if browser_path.is_file():
            browser = read_json(browser_path)
            require(browser.get("schema") == "ggen.nasa-dark-mode.browser-evidence.v1", "BROWSER_SCHEMA_MISMATCH", str(browser.get("schema")))
            browser_standing = "ALIVE"
            checks.append({"id": "browser-webgl", "state": "PASS", "detail": "EXECUTED"})
        else:
            browser = None
            browser_standing = "BLOCKED_DEPENDENCY_INSTALL"
            checks.append({"id": "browser-webgl", "state": "BLOCKED", "detail": "browser evidence absent"})

        report = {
            "schema": "ggen-legacy.nasa-dark-mode.independent-verifier.v1",
            "sourceRepository": source["repository"],
            "sourceHead": source["head"],
            "sourceObjectsVerified": len(contract["sourceObjects"]),
            "manufactureRoot": manufacture["generatedRoot"],
            "missionFeedDigest": digest,
            "assertionsObserved": runtime["assertions"],
            "standings": {
                "exactSourceObjects": "ALIVE",
                "deterministicManufacture": "ALIVE",
                "sourceCapsule": "ALIVE",
                "rokuPackage": "ALIVE",
                "browserWebGL": browser_standing,
                "rokuPhysicalDevice": "BLOCKED_DEVICE_REQUIRED",
                "independentReplay": "ALIVE",
                "aggregate": "PARTIAL_ALIVE",
            },
            "browserEvidence": browser,
            "releaseAdmission": False,
            "checks": checks,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 0
    except Refusal as exc:
        refusal = {
            "schema": "ggen-legacy.nasa-dark-mode.refusal.v1",
            "standing": "REFUSED",
            "code": exc.code,
            "detail": exc.detail,
            "sourceHead": source.get("head"),
            "checks": checks,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(refusal, indent=2, sort_keys=True) + "\n")
        print(json.dumps(refusal, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
