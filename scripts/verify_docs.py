#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, sys, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "AGENTS.md", "README.md", "RELEASE_CONTROL.md", "product/PRD.md",
    "architecture/ARD.md", "strategy/PRFAQ.md", "strategy/VISION_2030.md",
    "docs/book.toml", "docs/src/SUMMARY.md", "governance/claims-register.md",
    "governance/enterprise-maturity-model.md", "security/threat-model.md",
    "operations/enterprise-operations.md", "procurement/enterprise-due-diligence.md",
    "authority/product-profile.json", "authority/gall-checkpoints.json",
    "schemas/product-profile.schema.json", "schemas/verifier-report.schema.json",
    "schemas/receipt.schema.json", "fixtures/positive/product-profile.json",
    "fixtures/negative/premature-alive.json"
]
FORBIDDEN_DIRS = {"src","crates","packages","cmd","internal","app","lib","services","runtime"}
STATES = {"PARTIAL_ALIVE","ALIVE","BLOCKED","BUILD_BROKEN","UNKNOWN","UNSUPPORTED"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    errors: list[dict[str,str]] = []
    checks: list[dict[str,object]] = []

    def fail(code: str, message: str) -> None:
        errors.append({"code":code,"message":message})

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail("REQUIRED_FILE_MISSING", rel)
    checks.append({"id":"required-files","passed":not any(e["code"]=="REQUIRED_FILE_MISSING" for e in errors)})

    for name in FORBIDDEN_DIRS:
        if (ROOT / name).exists():
            fail("PRODUCTION_SOURCE_PREMATURE", name)
    checks.append({"id":"bootstrap-scope","passed":not any(e["code"]=="PRODUCTION_SOURCE_PREMATURE" for e in errors)})

    try:
        tomllib.loads((ROOT / "docs/book.toml").read_text())
    except Exception as exc:
        fail("BOOK_TOML_INVALID", str(exc))

    summary = (ROOT / "docs/src/SUMMARY.md").read_text()
    links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", summary)
    for link in links:
        if not (ROOT / "docs/src" / link).is_file():
            fail("BOOK_LINK_BROKEN", link)
    checks.append({"id":"book-links","passed":not any(e["code"]=="BOOK_LINK_BROKEN" for e in errors),"count":len(links)})

    json_paths = sorted((ROOT / "authority").glob("*.json")) + sorted((ROOT / "schemas").glob("*.json")) + sorted((ROOT / "fixtures").rglob("*.json"))
    parsed: dict[str,object] = {}
    for path in json_paths:
        try:
            parsed[path.relative_to(ROOT).as_posix()] = json.loads(path.read_text())
        except Exception as exc:
            fail("JSON_INVALID", f"{path}: {exc}")
    checks.append({"id":"json-parse","passed":not any(e["code"]=="JSON_INVALID" for e in errors),"count":len(json_paths)})

    profile = parsed.get("authority/product-profile.json", {})
    if isinstance(profile, dict):
        if profile.get("implementation_standing") == "ALIVE" and not profile.get("source_phase_admitted"):
            fail("PREMATURE_ALIVE_REFUSED", "authority claims ALIVE before source admission")
        if profile.get("direct_actuation_allowed") is not False:
            fail("DIRECT_ACTUATION_REFUSED", "direct_actuation_allowed must be false")
        for key in ("documentation_standing","implementation_standing","external_production_standing"):
            if profile.get(key) not in STATES:
                fail("STATE_INVALID", key)

    neg = parsed.get("fixtures/negative/premature-alive.json", {})
    neg_refused = isinstance(neg, dict) and neg.get("implementation_standing") == "ALIVE" and not neg.get("source_phase_admitted")
    if not neg_refused:
        fail("NEGATIVE_FIXTURE_INEFFECTIVE", "premature ALIVE fixture no longer violates law")
    checks.append({"id":"premature-alive-negative","passed":neg_refused})

    forbidden = [r"\bSOC 2-ready\b", r"\bSOC 2 compliant\b", r"\bguaranteed secure\b"]
    for path in sorted((ROOT / "docs/src").glob("*.md")):
        for line_no, line in enumerate(path.read_text().splitlines(), 1):
            lower = line.lower()
            if any(term in lower for term in ("does not claim","not claim","refused","forbidden","unproven","no guarantee")):
                continue
            for pattern in forbidden:
                if re.search(pattern, line, re.I):
                    fail("FORBIDDEN_OVERCLAIM", f"{path.relative_to(ROOT)}:{line_no}: {line.strip()}")
    checks.append({"id":"claim-discipline","passed":not any(e["code"]=="FORBIDDEN_OVERCLAIM" for e in errors)})

    inventory = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and ".git" not in path.parts and path.name != "local-docs-verifier.json":
            rel = path.relative_to(ROOT).as_posix()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            inventory.append({"path":rel,"sha256":digest,"bytes":path.stat().st_size})
    tree_digest = hashlib.sha256("\n".join(f"{x['path']}:{x['sha256']}" for x in inventory).encode()).hexdigest()
    standing = "PARTIAL_ALIVE" if not errors else "BUILD_BROKEN"
    report = {
        "schema":"ggen.legacy.docs.verifier.v1",
        "subject":{"revision":"WORKTREE_OR_EXACT_HEAD","tree_digest":tree_digest},
        "checks":checks,
        "errors":errors,
        "files":len(inventory),
        "replay":{"status":"SOURCE_SET_DIGEST_COMPUTED"},
        "standing":standing,
        "nonclaims":["product implementation ALIVE","external production standing","Sunset Admission"]
    }
    out = ROOT / "evidence" / "local-docs-verifier.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 1 if errors and args.strict else 0

if __name__ == "__main__":
    raise SystemExit(main())
