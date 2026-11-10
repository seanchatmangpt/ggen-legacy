#!/usr/bin/env python3
"""Independent v26.11.9 verifier: the srve switch-over ticket set and its admission artifacts.

It checks structure and refuses overclaiming; it does not run the cutover. Exit 1 on any error.
Claim ceiling for this release is DOCUMENTED (tooling: TESTED). `release_admitted` and
`sunset_admitted` must stay false, and no artifact may carry ALIVE or PRODUCTION_PROVEN.

usage: verify_v26_11_9.py [--root DIR] [--check-fresh] [--selftest]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REL = "docs/jira/v26.11.9"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
STANDING = {"ALIVE", "PARTIAL_ALIVE", "PASS", "BLOCKED", "UNVERIFIED", "PARTIAL", "REGISTERED"}
OVERCLAIM = re.compile(r"PRODUCTION_PROVEN|\bALIVE\b")
TICKETS = 36
MANIFESTS = {
    "resource-classification.json": ["xaas"],
    "route-inventory.json": ["srve/onengine-backend"],
    "cutover-scope.json": ["srve/servengine-frontend"],
    "prisma-coverage.json": ["srve/onengine-backend"],
    "ddl-census.json": ["xaas"],
}
REQUIRED = [
    f"{REL}/CHARTER.md", f"{REL}/INDEX.md", f"{REL}/DEPENDENCY-GRAPH.md",
    "authority/v26.11.9/promotion.json", "authority/v26.11.9/release-admission.json",
    "authority/v26.11.9/sunset-admission.json", "schemas/sunset-admission.schema.json",
    "schemas/release-admission.schema.json",
]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify(root: Path, check_fresh: bool = False) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED:
        if not (root / rel).is_file():
            errors.append(f"MISSING {rel}")
    if errors:
        return errors

    # admission artifacts: schema-valid and never admitted
    try:
        import jsonschema
    except ImportError:
        jsonschema = None
    for kind in ("release", "sunset"):
        art = _load(root / f"authority/v26.11.9/{kind}-admission.json")
        if art.get("admitted") is not False:
            errors.append(f"OVERCLAIM {kind}-admission admitted != false")
        if jsonschema is not None:
            try:
                jsonschema.validate(art, _load(root / f"schemas/{kind}-admission.schema.json"))
            except jsonschema.ValidationError as exc:
                errors.append(f"SCHEMA {kind}-admission: {exc.message}")
    sunset = _load(root / "authority/v26.11.9/sunset-admission.json")
    if not SHA_RE.match(str(sunset.get("predecessor_sha", ""))):
        errors.append("SUNSET predecessor_sha is not a 40-hex commit")
    promo = _load(root / "authority/v26.11.9/promotion.json")
    success = promo.get("success", {})
    if success.get("release_admitted") is not False or success.get("sunset_admitted") is not False:
        errors.append("OVERCLAIM promotion success admits release or sunset")
    for key in ("source_state", "source_claim_ceiling", "tooling_claim_ceiling"):
        if OVERCLAIM.search(str(promo.get(key, ""))):
            errors.append(f"OVERCLAIM promotion {key}={promo.get(key)}")
    if OVERCLAIM.search(str(success.get("standing", ""))):
        errors.append("OVERCLAIM promotion success.standing")

    # manifests carry exact source identity
    for name, repos in MANIFESTS.items():
        path = root / REL / "manifests" / name
        if not path.is_file():
            errors.append(f"MISSING manifest {name}")
            continue
        shas = _load(path).get("source_shas", {})
        for repo in repos:
            if not SHA_RE.match(str(shas.get(repo, ""))):
                errors.append(f"MANIFEST {name} lacks exact source sha for {repo}")
            elif check_fresh:
                head = subprocess.run(["git", "-C", str(Path.home() / repo), "rev-parse", "HEAD"],
                                      capture_output=True, text=True, check=False).stdout.strip()
                if head and head != shas[repo]:
                    errors.append(f"STALE {name}: {repo} manifest {shas[repo][:8]} != HEAD {head[:8]}")

    # tickets: count, standing line, dry-run section, line length
    tickets = sorted((root / REL / "tickets").glob("T-*.md"))
    if len(tickets) != TICKETS:
        errors.append(f"TICKETS {len(tickets)} != {TICKETS}")
    for path in tickets:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or not lines[0].startswith("# "):
            errors.append(f"{path.name}: first line is not an H1")
        standing = [ln for ln in lines[:4] if ln.startswith("Standing:")]
        if len(standing) != 1 or standing[0].split(":", 1)[1].strip() not in STANDING:
            errors.append(f"{path.name}: Standing line missing or outside vocabulary")
        if "## Dry run" not in lines:
            errors.append(f"{path.name}: no Dry run section")
    md = [*tickets, *(root / REL).glob("*.md"), *(root / REL / "manifests").glob("*.md")]
    for path in md:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if len(line) > 100:
                errors.append(f"{path.relative_to(root)}:{n}: line over 100 characters")
                break
    index = (root / REL / "INDEX.md").read_text(encoding="utf-8")
    for n in range(1, TICKETS + 1):
        if f"- T-{n:03d} [" not in index:
            errors.append(f"INDEX lacks T-{n:03d}")
    return errors


def selftest(root: Path) -> list[str]:
    """Non-vacuity: each mutation of a copy must be refused."""
    failures = []
    with tempfile.TemporaryDirectory() as raw:
        work = Path(raw) / "r"
        for rel in ("authority/v26.11.9", "schemas", REL):
            shutil.copytree(root / rel, work / rel)
        if verify(work):
            return ["baseline copy does not verify; selftest cannot run"]
        mutations = {
            "release admitted": lambda w: _patch(w / "authority/v26.11.9/release-admission.json",
                                                 lambda d: d.update(admitted=True)),
            "sunset admitted": lambda w: _patch(w / "authority/v26.11.9/sunset-admission.json",
                                                lambda d: d.update(admitted=True)),
            "promotion overclaim": lambda w: _patch(w / "authority/v26.11.9/promotion.json",
                                                    lambda d: d.update(source_state="ALIVE")),
            "unpinned manifest": lambda w: _patch(w / REL / "manifests/route-inventory.json",
                                                  lambda d: d.update(source_shas={})),
            "ticket lost standing": lambda w: _strip_standing(next((w / REL / "tickets").glob("T-001-*.md"))),
        }
        for name, mutate in mutations.items():
            probe = Path(raw) / name.replace(" ", "_")
            shutil.copytree(work, probe)
            mutate(probe)
            if not verify(probe):
                failures.append(f"VACUOUS: '{name}' was accepted")
    return failures


def _patch(path: Path, fn) -> None:
    data = _load(path)
    fn(data)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _strip_standing(path: Path) -> None:
    path.write_text("\n".join(ln for ln in path.read_text().splitlines()
                              if not ln.startswith("Standing:")) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--check-fresh", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    root = Path(args.root)
    errors = verify(root, args.check_fresh)
    if args.selftest and not errors:
        errors += selftest(root)
    for e in errors:
        print(e, file=sys.stderr)
    print(f"v26.11.9 verify: {'FAIL' if errors else 'OK'} ({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
