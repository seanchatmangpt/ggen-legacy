#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class Refusal(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}:{detail}")
        self.code = code
        self.detail = detail


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

    source_repo = args.source_repo.resolve()
    contract = read_json(args.contract)
    source = contract["source"]
    pack = source_repo / source["pack"]
    base_output = args.output.with_name(args.output.stem + ".base.json")
    checks: list[dict[str, str]] = []

    base_command = [
        sys.executable,
        str(Path(__file__).with_name("verify_source.py")),
        "--source-repo", str(source_repo),
        "--contract", str(args.contract),
        "--output", str(base_output),
    ]
    if args.require_git_head:
        base_command.append("--require-git-head")
    base = subprocess.run(base_command, text=True, capture_output=True)
    if base.returncode != 0:
        if base_output.is_file():
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(base_output.read_text())
        sys.stderr.write(base.stderr)
        return base.returncode

    base_report = read_json(base_output)
    try:
        expected = contract["noCi"]
        receipt = read_json(pack / ".ggen/evidence/no-ci/no-ci-receipt.json")
        require(receipt.get("schema") == expected["schema"], "NO_CI_SCHEMA_MISMATCH", str(receipt.get("schema")))
        require(receipt.get("receipt", {}).get("digest") == expected["receiptDigest"], "NO_CI_RECEIPT_MISMATCH", str(receipt.get("receipt", {}).get("digest")))
        require(receipt.get("wasmSha256") == expected["wasmSha256"], "NO_CI_WASM_MISMATCH", str(receipt.get("wasmSha256")))
        require(receipt.get("browserScreenshotSha256") == expected["browserScreenshotSha256"], "NO_CI_BROWSER_SCREENSHOT_MISMATCH", str(receipt.get("browserScreenshotSha256")))
        require(receipt.get("rokuPackageSha256") == expected["rokuPackageSha256"], "NO_CI_ROKU_PACKAGE_MISMATCH", str(receipt.get("rokuPackageSha256")))
        require(receipt.get("exhaustiveWasmProfiles") == expected["exhaustiveWasmProfiles"], "NO_CI_PROFILE_COUNT_MISMATCH", str(receipt.get("exhaustiveWasmProfiles")))
        require(receipt.get("sourceAssertions") == expected["sourceAssertions"], "NO_CI_ASSERTION_COUNT_MISMATCH", str(receipt.get("sourceAssertions")))
        require(receipt.get("aggregate") == expected["aggregate"], "NO_CI_AGGREGATE_MISMATCH", str(receipt.get("aggregate")))
        require(receipt.get("releaseAdmission") is expected["releaseAdmission"], "NO_CI_RELEASE_ADMISSION_MISMATCH", str(receipt.get("releaseAdmission")))
        for key in expected["requiredAlive"]:
            require(receipt.get("localBoundaries", {}).get(key) == "ALIVE", "NO_CI_REQUIRED_BOUNDARY_NOT_ALIVE", f"{key}:{receipt.get('localBoundaries', {}).get(key)}")
        for key, standing in expected["requiredBlocked"].items():
            require(receipt.get("localBoundaries", {}).get(key) == standing, "NO_CI_BLOCK_CLASSIFICATION_MISMATCH", f"{key}:{receipt.get('localBoundaries', {}).get(key)}!={standing}")
        checks.append({"id": "no-ci-receipt", "state": "PASS", "detail": expected["receiptDigest"]})

        wasm = read_json(pack / ".ggen/evidence/no-ci/wasm-equivalence.json")
        require(wasm.get("standing") == "ALIVE" and wasm.get("mismatches") == 0, "WASM_EQUIVALENCE_NOT_ALIVE", str(wasm.get("standing")))
        require(wasm.get("exhaustiveProfiles") == expected["exhaustiveWasmProfiles"], "WASM_PROFILE_COUNT_MISMATCH", str(wasm.get("exhaustiveProfiles")))
        require(wasm.get("mutationControl", {}).get("standing") == "KILLED", "WASM_MUTATION_SURVIVED", str(wasm.get("mutationControl")))
        require(wasm.get("wasm", {}).get("sha256") == expected["wasmSha256"], "WASM_BODY_MISMATCH", str(wasm.get("wasm", {}).get("sha256")))
        checks.append({"id": "wasm-equivalence", "state": "PASS", "detail": f"{wasm['exhaustiveProfiles']} profiles"})

        browser = read_json(pack / ".ggen/evidence/no-ci/browser-webgl2.json")
        require(browser.get("standing") == "ALIVE" and browser.get("webgl2") is True, "BROWSER_WEBGL2_NOT_ALIVE", str(browser.get("standing")))
        require(browser.get("shaderMutationControl") == "KILLED", "BROWSER_SHADER_MUTATION_SURVIVED", str(browser.get("shaderMutationControl")))
        screenshot = pack / ".ggen/evidence/no-ci/browser-webgl2.png"
        require(screenshot.is_file(), "BROWSER_SCREENSHOT_MISSING", str(screenshot))
        screenshot_sha = hashlib.sha256(screenshot.read_bytes()).hexdigest()
        require(screenshot_sha == expected["browserScreenshotSha256"], "BROWSER_SCREENSHOT_BYTES_MISMATCH", screenshot_sha)
        checks.append({"id": "browser-webgl2", "state": "PASS", "detail": browser.get("renderer", "EXECUTED")})

        roku = read_json(pack / ".ggen/evidence/no-ci/roku-source-simulation.json")
        require(roku.get("standing") == "ALIVE", "ROKU_SOURCE_SIMULATION_NOT_ALIVE", str(roku.get("standing")))
        require(roku.get("mutationControl", {}).get("standing") == "KILLED", "ROKU_MUTATION_SURVIVED", str(roku.get("mutationControl")))
        require(roku.get("packageSha256") == expected["rokuPackageSha256"], "ROKU_PACKAGE_RECEIPT_MISMATCH", str(roku.get("packageSha256")))
        checks.append({"id": "roku-source-simulation", "state": "PASS", "detail": roku.get("finalReceipt", "EXECUTED")})

        report = {
            **base_report,
            "schema": "ggen-legacy.nasa-dark-mode.independent-no-ci-verifier.v1",
            "sourceHead": source["head"],
            "sourceObjectsVerified": len(contract["sourceObjects"]),
            "standings": {
                "exactSourceObjects": "ALIVE",
                "deterministicManufacture": "ALIVE",
                "sourceCapsule": "ALIVE",
                "wasmControlCore": "ALIVE",
                "browserDom": "ALIVE",
                "browserWebGL2": "ALIVE",
                "rokuSourceSimulation": "ALIVE",
                "rokuPackage": "ALIVE",
                "receiptReplay": "ALIVE",
                **expected["requiredBlocked"],
                "independentReplay": "ALIVE",
                "aggregate": "PARTIAL_ALIVE",
            },
            "noCiReceipt": receipt,
            "wasmEvidence": wasm,
            "browserEvidence": browser,
            "rokuSimulationEvidence": roku,
            "checks": base_report.get("checks", []) + checks,
            "releaseAdmission": False,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, sort_keys=True))
        return 0
    except Refusal as exc:
        refusal = {
            "schema": "ggen-legacy.nasa-dark-mode.no-ci-refusal.v1",
            "standing": "REFUSED",
            "code": exc.code,
            "detail": exc.detail,
            "sourceHead": source.get("head"),
            "checks": base_report.get("checks", []) + checks,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(refusal, indent=2, sort_keys=True) + "\n")
        print(json.dumps(refusal, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
