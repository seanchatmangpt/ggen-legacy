#!/usr/bin/env python3
"""Independent GL-ERRC-003 v2 replay and mutation court."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

COMPLETE_PRDS={"PRD-FR-001","PRD-FR-002","PRD-FR-003","PRD-FR-004","PRD-FR-005","PRD-FR-009","PRD-FR-010","PRD-FR-011","PRD-FR-013"}
COMPLETE_CLAIMS={"CLM-001","CLM-002","CLM-004","CLM-009","CLM-010","CLM-011"}
BUNDLES={"migration-v26-8-1","verifier-appliance-reference","offline-verifier-transport","foundry-bootstrap-evidence","foundry-runtime-candidate","planning-combinatorial-max","lsp-enterprise-boundary","autonomic-projection-reference"}
EXCLUSIONS={"scripts/reconstitute_fortune5.py","scripts/fortune5_reconstitute_v2.py","scripts/verify_fortune5_reconstitution.py","scripts/fortune5_verify_v2.py"}
IGNORE=shutil.ignore_patterns(".git","target","__pycache__",".source-ggen",".foundry-ggen","book")
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def h(root:Path)->str:
 p=subprocess.run(["git","rev-parse","HEAD"],cwd=root,text=True,capture_output=True)
 if p.returncode or len(p.stdout.strip())!=40:raise RuntimeError("SUBJECT_HEAD_UNAVAILABLE")
 return p.stdout.strip()
def tree(root:Path)->dict[str,str]:return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob("*")) if p.is_file()}
def run(root:Path,out:Path,subject:str)->subprocess.CompletedProcess[str]:
 e=dict(os.environ);e["GGEN_SUBJECT_HEAD"]=subject
 return subprocess.run([sys.executable,str(root/"scripts/reconstitute_fortune5.py"),"--root",str(root),"--contract",str(root/"authority/fortune5-reconstitution.json"),"--output",str(out),"--strict"],cwd=root,text=True,capture_output=True,timeout=90,env=e)
def copy(src:Path,dst:Path)->None:shutil.copytree(src,dst,ignore=IGNORE)
def receipt(out:Path)->dict:
 r=json.loads((out/"receipt.json").read_text())
 if r.get("schema")!="ggen.legacy.errc.reconstitution.receipt/2" or r.get("standing")!="PARTIAL_ALIVE" or r.get("external_production_standing")!="UNKNOWN":raise RuntimeError("RECEIPT_CEILING_DRIFT")
 for p,x in r["output_manifest"].items():
  if sha(out/p)!=x:raise RuntimeError(f"OUTPUT_DIGEST_MISMATCH:{p}")
 sources={"authority/fortune5-reconstitution.json","authority/fortune5-evidence-map.json","scripts/reconstitute_fortune5.py","scripts/fortune5_reconstitute_v2.py","scripts/verify_fortune5_reconstitution.py","scripts/fortune5_verify_v2.py",".github/workflows/ci.yml"}
 if not sources<=set(r["source_manifest"]):raise RuntimeError("RECEIPT_SOURCE_BINDING_MISSING")
 evidence={"evidence/appliance/crown-report.json","migrations/ggen-v26.8.1/verifier-report.json","evidence/offline-bundle/replay-report.json","evidence/foundry-bootstrap-verifier.json","evidence/ci/gl-plan-002.json","evidence/ci/local-qualification.json"}
 if not evidence<=set(r["evidence_manifest"]):raise RuntimeError("RECEIPT_EVIDENCE_BINDING_MISSING")
 return r
def mutate(src:Path,dst:Path,kind:str)->None:
 copy(src,dst)
 if kind=="cardinality":
  p=dst/"product/PRD.md";s=p.read_text();a=s.index("### PRD-FR-014");b=s.find("\n### PRD-FR-",a+1);p.write_text(s[:a]+(s[b+1:] if b>=0 else ""))
 elif kind=="workflow":(dst/".github/workflows/rogue.yml").write_text("name: rogue\n")
 elif kind=="self":
  p=dst/"authority/fortune5-evidence-map.json";x=json.loads(p.read_text());x["bundles"][0]["evidence_paths"].append("scripts/fortune5_reconstitute_v2.py");p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
 elif kind=="external":
  p=dst/"authority/fortune5-evidence-map.json";x=json.loads(p.read_text());x["bundles"][0]["complete_objects"].append("CLM-005");p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
 elif kind=="assertion":
  p=dst/"authority/fortune5-evidence-map.json";x=json.loads(p.read_text());next(a for b in x["bundles"] if b["id"]=="verifier-appliance-reference" for a in b["assertions"] if a["field"]=="standing")["equals"]="BUILD_BROKEN";p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args();root=a.root.resolve();subject=h(root)
 with tempfile.TemporaryDirectory(prefix="gl-errc-003-v2-") as raw:
  td=Path(raw);one,two=td/"one",td/"two";r1,r2=run(root,one,subject),run(root,two,subject)
  if r1.returncode or r2.returncode:print(json.dumps({"standing":"BUILD_BROKEN","first":{"exit":r1.returncode,"stderr":r1.stderr},"second":{"exit":r2.returncode,"stderr":r2.stderr}},sort_keys=True));return 1
  if tree(one)!=tree(two):raise RuntimeError("REPLAY_DIVERGENCE")
  rec=receipt(one);m=json.loads((one/"matrix.json").read_text());q=json.loads((one/"work-queue.json").read_text());c=json.loads((root/"authority/fortune5-reconstitution.json").read_text());counts=m["counts"]
  for k in ("product_requirements","claims","maturity_obligations","workstreams"):
   if counts[k]!=c["expected_cardinality"][k]:raise RuntimeError(f"CARDINALITY_MISMATCH:{k}")
  if counts["qualified_evidence_bundles"]!=len(BUNDLES) or {x["id"] for x in m["evidence_bundles"] if x["qualified"]}!=BUNDLES:raise RuntimeError("EVIDENCE_BUNDLE_QUALIFICATION_GAP")
  rows={x["id"]:x for x in m["matrix"]}
  for oid in COMPLETE_PRDS:
   x=rows[oid]
   if x["computed_state"]!="BOUNDED_EVIDENCE_COMPLETE" or x["computed_standing_ceiling"]!="PARTIAL_ALIVE" or x["missing"]:raise RuntimeError(f"PRD_EVIDENCE_NOT_ADMITTED:{oid}")
  for oid in COMPLETE_CLAIMS:
   x=rows[oid]
   if x["computed_state"]!="BOUNDED_EVIDENCE_COMPLETE" or x["computed_standing_ceiling"]!="ALIVE" or x["missing"]:raise RuntimeError(f"CLAIM_EVIDENCE_NOT_ADMITTED:{oid}")
  if set(c.get("evidence_exclusions",[]))!=EXCLUSIONS or set(m["invariants"].get("evidence_exclusions",[]))!=EXCLUSIONS or m["invariants"].get("literal_identifier_mentions_are_evidence") is not False:raise RuntimeError("SELF_EVIDENCE_INVARIANT_DRIFT")
  for oid in c["external_claims"]:
   x=rows[oid]
   if not x["external_gate"] or x["computed_state"]!="EXTERNAL_GATE" or x["computed_standing_ceiling"]!="UNKNOWN" or x["mapped_evidence"]["complete_bundles"] or x["mapped_evidence"]["partial_bundles"]:raise RuntimeError(f"EXTERNAL_GATE_WIDENED:{oid}")
  if any(x["auto_executable"] or x["actuation"]!="REFUSED:AMBIENT_ACTUATION" for x in q["items"]):raise RuntimeError("AMBIENT_ACTUATION_ESCALATION")
  tests={"cardinality":("REFUSED:CARDINALITY_DRIFT",),"workflow":("REFUSED:WORKFLOW_TOPOLOGY_DRIFT",),"self":("REFUSED:EVIDENCE_MAP_SELF_REFERENCE",),"external":("REFUSED:EXTERNAL_EVIDENCE_MAPPING",),"assertion":("REFUSED:EVIDENCE_ASSERTION_FAILED",)};results={}
  for kind,codes in tests.items():
   d=td/f"bad-{kind}";mutate(root,d,kind);rr=run(d,td/f"out-{kind}",subject);results[kind]=rr.returncode==2 and any(code in rr.stderr for code in codes)
  bad=[k for k,v in results.items() if not v]
  if bad:raise RuntimeError("MUTANT_SURVIVED:"+",".join(bad))
  report={"schema":"ggen.legacy.errc.reconstitution.verifier/2","ticket":"GL-ERRC-003","subject_head":rec["subject_head"],"objects":counts["objects"],"work_orders":counts["work_orders"],"bounded_evidence_complete":counts["bounded_evidence_complete"],"bounded_evidence_partial":counts["bounded_evidence_partial"],"qualified_evidence_bundles":counts["qualified_evidence_bundles"],"replay":"REPLAY_MATCH","negative_controls":{k:"KILLED" for k in results},"claim_ceiling":"FORTUNE5_SELF_RECONSTITUTION_ANALYSIS_ONLY","standing":"PARTIAL_ALIVE"};print(json.dumps(report,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
