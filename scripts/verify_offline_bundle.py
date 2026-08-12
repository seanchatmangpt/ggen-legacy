#!/usr/bin/env python3
"""Current-head replay and sabotage court for the portable verifier bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "ggen-legacy-verifier-v26.8.1"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False, timeout=120)


def head(root: Path) -> str:
    p = run(["git", "rev-parse", "HEAD"], root)
    if p.returncode or len(p.stdout.strip()) != 40:
        raise RuntimeError("SUBJECT_HEAD_UNAVAILABLE")
    return p.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--output", type=Path, default=Path("evidence/offline-bundle"))
    args = ap.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    build = root / "appliance/bin/build-offline-bundle.sh"
    subject = head(root)
    with tempfile.TemporaryDirectory(prefix="ggen-offline-replay-") as td_raw:
        td = Path(td_raw)
        second = td / "second"
        if output.exists():
            shutil.rmtree(output)
        a = run(["bash", str(build), str(output)], root)
        b = run(["bash", str(build), str(second)], root)
        if a.returncode or b.returncode:
            print(json.dumps({"standing": "BUILD_BROKEN", "first": a.stderr, "second": b.stderr}, sort_keys=True))
            return 1
        archive_a = output / f"{NAME}.tar.gz"
        archive_b = second / f"{NAME}.tar.gz"
        replay_match = archive_a.read_bytes() == archive_b.read_bytes()
        if not replay_match:
            raise RuntimeError("OFFLINE_BUNDLE_REPLAY_DIVERGENCE")
        receipt = json.loads((output / f"{NAME}.receipt.json").read_text())
        if receipt.get("source_head") != subject or receipt.get("archive_sha256") != digest(archive_a):
            raise RuntimeError("OFFLINE_BUNDLE_RECEIPT_MISMATCH")
        extracted = td / "extract"
        extracted.mkdir()
        with tarfile.open(archive_a, "r:gz") as tf:
            tf.extractall(extracted, filter="data")
        bundle = extracted / NAME
        verify = run(["bash", str(bundle / "verify-manifest.sh")], bundle)
        if verify.returncode:
            raise RuntimeError("OFFLINE_MANIFEST_VERIFY_FAILED:" + verify.stderr)
        tamper = bundle / "AGENTS.md"
        tamper.write_text(tamper.read_text() + "\nTAMPER\n")
        killed = run(["bash", str(bundle / "verify-manifest.sh")], bundle)
        if killed.returncode == 0:
            raise RuntimeError("OFFLINE_TAMPER_MUTANT_SURVIVED")
        report = {
            "schema": "ggen.legacy.offline.bundle.replay/1",
            "subject_head": subject,
            "archive_sha256": digest(archive_a),
            "replay": "REPLAY_MATCH",
            "manifest_verification": "ALIVE",
            "tamper_mutant": "KILLED",
            "network_required": False,
            "standing": "ALIVE",
            "claim_ceiling": "PORTABLE_APPLICATION_BUNDLE_ONLY",
        }
        output.mkdir(parents=True, exist_ok=True)
        (output / "replay-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
