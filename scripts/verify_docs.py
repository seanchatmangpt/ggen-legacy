#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "AGENTS.md", "README.md", "RELEASE_CONTROL.md", "product/PRD.md",
    "architecture/ARD.md", "strategy/PRFAQ.md", "strategy/VISION_2030.md",
    "docs/book.toml", "docs/src/SUMMARY.md", "docs/src/12-verifier-appliance.md",
    "governance/claims-register.md", "governance/enterprise-maturity-model.md",
    "security/threat-model.md", "operations/enterprise-operations.md",
    "procurement/enterprise-due-diligence.md", "authority/product-profile.json",
    "authority/verifier-appliance-profile.json", "authority/gall-checkpoints.json",
    "ggen.toml", "ontology/assurance-program.ttl",
    "packs/ggen-legacy-assurance-pack/pack.toml",
    "packs/ggen-legacy-assurance-pack/ontology.ttl",
    "appliance/manifest.json", "appliance/bin/build-standing-portfolio.py",
    "appliance/bin/verify-standing-portfolio.py", "appliance/bin/cross-check-portfolio.py",
    "appliance/bin/transparency-log.py", "appliance/bin/replay-standing-portfolio.py",
    "appliance/bin/decision-engine.py", "appliance/bin/run-reference-e2e.sh",
    "projects/001/TICKET-011-admit-verifier-appliance-pack.md",
    "schemas/product-profile.schema.json", "schemas/verifier-report.schema.json",
    "schemas/receipt.schema.json", "schemas/engagement.schema.json",
    "schemas/claim-manifest.schema.json", "schemas/replay-report.schema.json",
    "schemas/release-admission.schema.json", "schemas/sunset-admission.schema.json",
    "schemas/transparency-entry.schema.json", "fixtures/positive/product-profile.json",
    "fixtures/negative/premature-alive.json", "tests/fixtures/engagement.reference.json"
]
FORBIDDEN_DIRS = {"src","crates","packages","cmd","internal","app","lib","services","runtime"}
STATES = {"PARTIAL_ALIVE","ALIVE","BLOCKED","BUILD_BROKEN","UNKNOWN","UNSUPPORTED"}
EXPECTED_GGEN = "0f39227c102e0ac7519f0f27561356227a518653"

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--strict",action="store_true"); args=ap.parse_args()
    errors=[]; checks=[]
    def fail(code,message): errors.append({"code":code,"message":message})
    for rel in REQUIRED:
        if not (ROOT/rel).is_file(): fail("REQUIRED_FILE_MISSING",rel)
    checks.append({"id":"required-files","passed":not any(e["code"]=="REQUIRED_FILE_MISSING" for e in errors),"count":len(REQUIRED)})
    for name in FORBIDDEN_DIRS:
        if (ROOT/name).exists(): fail("UNADMITTED_TOP_LEVEL_SOURCE",name)
    checks.append({"id":"source-boundary","passed":not any(e["code"]=="UNADMITTED_TOP_LEVEL_SOURCE" for e in errors)})
    try: tomllib.loads((ROOT/"docs/book.toml").read_text()); tomllib.loads((ROOT/"ggen.toml").read_text()); tomllib.loads((ROOT/"packs/ggen-legacy-assurance-pack/pack.toml").read_text())
    except Exception as exc: fail("TOML_INVALID",str(exc))
    summary=(ROOT/"docs/src/SUMMARY.md").read_text(); links=re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)",summary)
    for link in links:
        if not (ROOT/"docs/src"/link).is_file(): fail("BOOK_LINK_BROKEN",link)
    checks.append({"id":"book-links","passed":not any(e["code"]=="BOOK_LINK_BROKEN" for e in errors),"count":len(links)})
    json_paths=sorted((ROOT/"authority").glob("*.json"))+sorted((ROOT/"schemas").glob("*.json"))+sorted((ROOT/"fixtures").rglob("*.json"))+sorted((ROOT/"tests/fixtures").rglob("*.json"))+sorted((ROOT/"appliance").rglob("*.json"))
    parsed={}
    for path in json_paths:
        try: parsed[path.relative_to(ROOT).as_posix()]=json.loads(path.read_text())
        except Exception as exc: fail("JSON_INVALID",f"{path}: {exc}")
    checks.append({"id":"json-parse","passed":not any(e["code"]=="JSON_INVALID" for e in errors),"count":len(json_paths)})
    profile=parsed.get("authority/product-profile.json",{})
    if isinstance(profile,dict):
        if profile.get("direct_actuation_allowed") is not False: fail("DIRECT_ACTUATION_REFUSED","direct_actuation_allowed must be false")
        if profile.get("source_phase_admitted") is not True: fail("SOURCE_PHASE_NOT_ADMITTED","TICKET-011 must admit source phase")
        if profile.get("ggen_source_revision")!=EXPECTED_GGEN: fail("GGEN_COORDINATE_DRIFT",str(profile.get("ggen_source_revision")))
        for key in ("documentation_standing","implementation_standing","external_production_standing","verifier_appliance_standing"):
            if profile.get(key) not in STATES: fail("STATE_INVALID",key)
        if profile.get("implementation_standing")=="ALIVE": fail("PRODUCT_ALIVE_PREMATURE","complete product cannot be ALIVE in Project 001")
    neg=parsed.get("fixtures/negative/premature-alive.json",{})
    if not (isinstance(neg,dict) and neg.get("implementation_standing")=="ALIVE" and not neg.get("source_phase_admitted")):
        fail("NEGATIVE_FIXTURE_INEFFECTIVE","premature ALIVE fixture no longer violates law")
    templates=sorted((ROOT/"packs/ggen-legacy-assurance-pack/templates").glob("*.tmpl")); projection_fail=[]
    for path in templates:
        text=path.read_text()
        m=re.match(r"---\n(?:.|\n)*?to:\s*([^\n]+)\n(?:.|\n)*?---\n\{% raw %\}(.*)\{% endraw %\}\Z",text,re.S)
        if not m: projection_fail.append(f"frontmatter:{path.name}"); continue
        target=ROOT/m.group(1).strip(); body=m.group(2)
        if not target.is_file() or target.read_text()!=body: projection_fail.append(m.group(1).strip())
    if projection_fail: fail("GENERATED_PROJECTION_DRIFT",",".join(projection_fail))
    checks.append({"id":"ggen-projection-identity","passed":not projection_fail,"templates":len(templates)})
    gates=sorted((ROOT/"packs/ggen-legacy-assurance-pack/gates").glob("*.rq"))
    if len(gates)!=10: fail("GATE_CARDINALITY",f"expected 10, observed {len(gates)}")
    checks.append({"id":"assurance-gates","passed":len(gates)==10,"count":len(gates)})
    forbidden=[r"\bSOC 2-ready\b",r"\bSOC 2 compliant\b",r"\bguaranteed secure\b"]
    for path in sorted((ROOT/"docs/src").glob("*.md")):
        for line_no,line in enumerate(path.read_text().splitlines(),1):
            lower=line.lower()
            if any(term in lower for term in ("does not claim","not claim","refused","forbidden","unproven","no guarantee")): continue
            for pattern in forbidden:
                if re.search(pattern,line,re.I): fail("FORBIDDEN_OVERCLAIM",f"{path.relative_to(ROOT)}:{line_no}: {line.strip()}")
    checks.append({"id":"claim-discipline","passed":not any(e["code"]=="FORBIDDEN_OVERCLAIM" for e in errors)})
    inventory=[]
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and ".git" not in path.parts and "docs/book" not in path.as_posix() and not path.as_posix().endswith("evidence/local-docs-verifier.json") and "/evidence/appliance/" not in path.as_posix():
            rel=path.relative_to(ROOT).as_posix(); digest=hashlib.sha256(path.read_bytes()).hexdigest(); inventory.append({"path":rel,"sha256":digest,"bytes":path.stat().st_size})
    tree_digest=hashlib.sha256("\n".join(f"{x['path']}:{x['sha256']}" for x in inventory).encode()).hexdigest()
    standing="PARTIAL_ALIVE" if not errors else "BUILD_BROKEN"
    report={"schema":"ggen.legacy.docs.verifier.v1","subject":{"revision":"WORKTREE_OR_EXACT_HEAD","tree_digest":tree_digest},"checks":checks,"errors":errors,"files":len(inventory),"replay":{"status":"SOURCE_SET_DIGEST_COMPUTED"},"standing":standing,"nonclaims":["complete product ALIVE","external production standing","real Sunset Admission"]}
    out=ROOT/"evidence/local-docs-verifier.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2)); return 1 if errors and args.strict else 0
if __name__=="__main__": raise SystemExit(main())
