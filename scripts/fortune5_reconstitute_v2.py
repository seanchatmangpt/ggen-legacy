#!/usr/bin/env python3
"""GL-ERRC-003 v2: explicit-evidence Fortune-5 reconstitution court."""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STANDINGS={"UNKNOWN","PARTIAL_ALIVE","ALIVE","BLOCKED","BUILD_BROKEN","UNSUPPORTED","REFUSED"}
ERRC={"ELIMINATE","REDUCE","RAISE","CREATE"}
PATH_FIELDS=("authority_paths","implementation_paths","test_paths","evidence_paths","verifier_paths")
GENERATED=("evidence/reconstitution/","foundry/generated/","foundry/reports/","foundry/receipts/")
class Refusal(RuntimeError): pass

def cj(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
def h(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def fh(p:Path)->str:return h(p.read_bytes())
def load(p:Path)->Any:
 try:return json.loads(p.read_text())
 except (OSError,json.JSONDecodeError) as e:raise Refusal(f"REFUSED:INVALID_JSON:{p}:{e}") from e
def rel(v:Any)->str:
 s=str(v)
 if not s or s.startswith("/") or ".." in Path(s).parts:raise Refusal(f"REFUSED:UNSAFE_RELATIVE_PATH:{s}")
 return Path(s).as_posix()
def head(root:Path)->str:
 o=os.getenv("GGEN_SUBJECT_HEAD","").strip()
 if re.fullmatch(r"[0-9a-f]{40}",o):return o
 try:p=subprocess.run(["git","rev-parse","HEAD"],cwd=root,text=True,capture_output=True,timeout=5)
 except (OSError,subprocess.TimeoutExpired):return "UNKNOWN"
 x=p.stdout.strip();return x if p.returncode==0 and re.fullmatch(r"[0-9a-f]{40}",x) else "UNKNOWN"
def field(v:Any,dot:str)->Any:
 for k in dot.split("."):
  if not isinstance(v,dict) or k not in v:raise KeyError(dot)
  v=v[k]
 return v

def write(root:Path,name:str,data:bytes)->None:
 root=root.resolve();p=(root/name).resolve()
 if p!=root and root not in p.parents:raise Refusal("REFUSED:OUTPUT_ESCAPE")
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+".tmp");t.write_bytes(data);os.replace(t,p)

@dataclass(frozen=True)
class Obj:
 id:str;kind:str;title:str;source:str;standing:str="UNKNOWN";external:bool=False

def objects(root:Path,external:set[str])->list[Obj]:
 out=[]
 txt=(root/"product/PRD.md").read_text()
 out += [Obj(m.group(1),"product_requirement",m.group(2),"product/PRD.md") for m in re.finditer(r"^###\s+(PRD-FR-\d+)\s+—\s+(.+?)\s*$",txt,re.M)]
 for line in (root/"governance/claims-register.md").read_text().splitlines():
  if not line.startswith("| CLM-"):continue
  c=[x.strip() for x in line.strip().strip("|").split("|")]
  if len(c)<4:continue
  s=c[3].strip("`");s="REFUSED" if s.startswith("REFUSED") else s
  out.append(Obj(c[0],"claim",c[1],"governance/claims-register.md",s if s in STANDINGS else "UNKNOWN",c[0] in external))
 txt=(root/"governance/enterprise-maturity-model.md").read_text()
 for m in re.finditer(r"^##\s+(EM-(\d{2}))\s+(.+?)\s*$",txt,re.M):
  for suf,label in (("P","Positive"),("N","Negative"),("R","Replay")):out.append(Obj(f"{m.group(1)}-{suf}","enterprise_obligation",f"{m.group(3)} — {label}","governance/enterprise-maturity-model.md"))
 b=load(root/"foundry/bootstrap.yaml")
 for w in b.get("workstreams",[]):
  wid=str(w.get("id",""))
  if not re.fullmatch(r"[A-K]",wid):raise Refusal(f"REFUSED:INVALID_WORKSTREAM:{wid}")
  s=str(w.get("status","UNKNOWN"));s="PARTIAL_ALIVE" if s in {"IN_PROGRESS","PARTIAL_ALIVE"} else s
  out.append(Obj(f"FOUNDRY-{wid}","foundry_workstream",f"Foundry workstream {wid}","foundry/bootstrap.yaml",s if s in STANDINGS or s=="NOT_STARTED" else "UNKNOWN"))
 return out

def invariants(root:Path,c:dict[str,Any],objs:list[Obj])->list[dict[str,Any]]:
 actual={"product_requirements":sum(o.kind=="product_requirement" for o in objs),"claims":sum(o.kind=="claim" for o in objs),"maturity_dimensions":len({o.id[:5] for o in objs if o.kind=="enterprise_obligation"}),"maturity_obligations":sum(o.kind=="enterprise_obligation" for o in objs),"workstreams":sum(o.kind=="foundry_workstream" for o in objs)}
 for k,v in c["expected_cardinality"].items():
  if actual.get(k)!=v:raise Refusal(f"REFUSED:CARDINALITY_DRIFT:{k}:expected={v}:observed={actual.get(k)}")
 ids=[o.id for o in objs]
 if len(ids)!=len(set(ids)):raise Refusal("REFUSED:DUPLICATE_OBJECT")
 wd=root/".github/workflows";n=len(list(wd.glob("*.yml")))+len(list(wd.glob("*.yaml")))
 if n!=int(c["expected_workflow_count"]):raise Refusal(f"REFUSED:WORKFLOW_TOPOLOGY_DRIFT:expected={c['expected_workflow_count']}:observed={n}")
 f=[{"code":"WORKFLOW_TOPOLOGY","state":"ALIVE","observed":n}]
 statuses=[str(x.get("status","UNKNOWN")) for x in load(root/"foundry/bootstrap.yaml").get("workstreams",[])]
 claims={o.id:o for o in objs if o.kind=="claim"}
 if statuses and all(x=="NOT_STARTED" for x in statuses) and claims.get("CLM-012") and claims["CLM-012"].standing=="PARTIAL_ALIVE":f.append({"code":"FOUNDRY_BOOTSTRAP_STATUS_LAG","state":"PARTIAL_ALIVE","operator":"RAISE","reason":"bounded evidence is not workstream admission"})
 gp=root/"governance/production-gaps.md";rp=root/"authority/ggen-create-receiving-contract.json"
 if gp.exists() and rp.exists():
  m=re.search(r"producer pin .*?commit `([0-9a-f]{7,40})`",gp.read_text(),re.I|re.S);cur=str(load(rp).get("producer",{}).get("commit",""))
  if m and cur and not cur.startswith(m.group(1)):f.append({"code":"STALE_PRODUCTION_GAP_ASSERTION","state":"PARTIAL_ALIVE","operator":"ELIMINATE","observed":m.group(1),"current":cur,"reason":"historical blocker text no longer matches admitted producer coordinate"})
 return f

def qualify(root:Path,c:dict[str,Any],objs:list[Obj],strict:bool,subject:str)->tuple[dict[str,Any],list[dict[str,Any]],set[str]]:
 mp=rel(c.get("evidence_map",""));data=load(root/mp)
 if data.get("schema")!="ggen.legacy.fortune5.evidence-map/1":raise Refusal("REFUSED:EVIDENCE_MAP_SCHEMA")
 by={o.id:o for o in objs};support={i:{"complete_bundles":[],"partial_bundles":[],"paths":{k:[] for k in PATH_FIELDS},"modes":[]} for i in by};reports=[];bound={mp};seen=set();excluded={rel(x) for x in c.get("evidence_exclusions",[])}
 for x in excluded:
  if not (root/x).is_file():raise Refusal(f"REFUSED:MISSING_EVIDENCE_EXCLUSION:{x}")
 for b in data.get("bundles",[]):
  bid=str(b.get("id",""));
  if not bid or bid in seen:raise Refusal(f"REFUSED:DUPLICATE_EVIDENCE_BUNDLE:{bid}")
  seen.add(bid);complete=[str(x) for x in b.get("complete_objects",[])];partial=[str(x) for x in b.get("partial_objects",[])];mapped=complete+partial
  if set(complete)&set(partial):raise Refusal(f"REFUSED:EVIDENCE_MAP_AMBIGUOUS_COVERAGE:{bid}")
  unknown=sorted(set(mapped)-set(by))
  if unknown:raise Refusal(f"REFUSED:EVIDENCE_MAP_UNKNOWN_OBJECT:{bid}:{','.join(unknown)}")
  ext=sorted(i for i in mapped if by[i].external)
  if ext:raise Refusal(f"REFUSED:EXTERNAL_EVIDENCE_MAPPING:{bid}:{','.join(ext)}")
  modes=sorted(set(map(str,b.get("modes",[]))))
  if not set(modes)<={"positive","negative","replay"}:raise Refusal(f"REFUSED:EVIDENCE_MAP_MODE:{bid}")
  paths={};missing=[]
  for k in PATH_FIELDS:
   vals=[rel(x) for x in b.get(k,[])]
   if len(vals)!=len(set(vals)):raise Refusal(f"REFUSED:EVIDENCE_MAP_DUPLICATE_PATH:{bid}:{k}")
   for p in vals:
    if p in excluded or p.startswith(GENERATED):raise Refusal(f"REFUSED:EVIDENCE_MAP_SELF_REFERENCE:{bid}:{p}")
    if not (root/p).is_file():missing.append(p)
   paths[k]=vals
   if k=="evidence_paths":bound.update(vals)
  ars=[];ok=True
  for a in b.get("assertions",[]):
   p=rel(a.get("path",""));exp=subject if a.get("equals")=="$SUBJECT_HEAD" else a.get("equals");passed=False;obs=None;why=None
   if not (root/p).is_file():why="missing"
   else:
    try:obs=field(load(root/p),str(a.get("field","")));passed=obs==exp
    except (Refusal,KeyError):why="field_missing"
   ok=ok and passed;ars.append({"path":p,"field":a.get("field"),"expected":exp,"observed":obs,"passed":passed,"reason":why})
  q=not missing and ok
  if strict and missing:raise Refusal(f"REFUSED:EVIDENCE_PATH_MISSING:{bid}:{','.join(sorted(missing))}")
  if strict and not ok:raise Refusal(f"REFUSED:EVIDENCE_ASSERTION_FAILED:{bid}")
  reports.append({"id":bid,"scope":str(b.get("scope","")),"standing_ceiling":str(b.get("standing_ceiling","PARTIAL_ALIVE")),"complete_objects":sorted(complete),"partial_objects":sorted(partial),"qualified":q,"missing_paths":sorted(missing),"assertions":ars,"modes":modes})
  if not q:continue
  for i in complete:support[i]["complete_bundles"].append(bid)
  for i in partial:support[i]["partial_bundles"].append(bid)
  for i in mapped:
   for k in PATH_FIELDS:support[i]["paths"][k]+=paths[k]
   support[i]["modes"]+=modes
 for s in support.values():
  for k in ("complete_bundles","partial_bundles","modes"):s[k]=sorted(set(s[k]))
  for k in PATH_FIELDS:s["paths"][k]=sorted(set(s["paths"][k]))
 return support,sorted(reports,key=lambda x:x["id"]),bound

def state(o:Obj,m:dict[str,Any])->tuple[str,str,int,list[str],str]:
 if o.external:return "EXTERNAL_GATE","RAISE",0,["independent external evidence"],"UNKNOWN"
 if m["complete_bundles"]:
  if o.kind=="foundry_workstream" and o.standing=="NOT_STARTED":return "ADMISSION_PENDING","RAISE",2,["workstream admission"],"UNKNOWN"
  ceiling=o.standing if o.kind=="claim" and o.standing in {"ALIVE","PARTIAL_ALIVE"} else "PARTIAL_ALIVE"
  return "BOUNDED_EVIDENCE_COMPLETE","REDUCE",3,[],ceiling
 if m["partial_bundles"]:
  miss={"enterprise_obligation":"enterprise-scope P/N/R qualification","foundry_workstream":"workstream admission","product_requirement":"product-wide terminal admission","claim":"claim terminal admission"}[o.kind]
  return "BOUNDED_EVIDENCE_PARTIAL","RAISE",2,[miss],"UNKNOWN" if o.kind=="foundry_workstream" and o.standing=="NOT_STARTED" else "PARTIAL_ALIVE"
 return "DOCUMENTED_ONLY","CREATE",1,["explicit executable evidence mapping"],"UNKNOWN"

def build(root:Path,cp:Path,strict:bool)->dict[str,Any]:
 c=load(cp)
 if c.get("ticket")!="GL-ERRC-003":raise Refusal("REFUSED:WRONG_RECONSTITUTION_TICKET")
 objs=objects(root,set(c.get("external_claims",[])));find=invariants(root,c,objs);subject=head(root);mapped,bundles,bound=qualify(root,c,objs,strict,subject);rows=[];queue=[]
 for o in sorted(objs,key=lambda x:x.id):
  st,op,lvl,miss,ceil=state(o,mapped[o.id]);rows.append({"id":o.id,"kind":o.kind,"title":o.title,"source_path":o.source,"source_standing":o.standing,"external_gate":o.external,"computed_state":st,"computed_level":lvl,"computed_standing_ceiling":ceil,"errc_operator":op,"missing":miss,"mapped_evidence":mapped[o.id]})
  if miss:queue.append({"priority":0 if o.external else 1,"object_id":o.id,"operator":op,"reason":"; ".join(miss),"auto_executable":False,"authority":"CONSTRUCT_ONLY","actuation":"REFUSED:AMBIENT_ACTUATION"})
 for f in find:
  if f.get("operator") in ERRC:queue.append({"priority":0 if f["operator"]=="ELIMINATE" else 1,"object_id":f["code"],"operator":f["operator"],"reason":f.get("reason","reconstitution finding"),"auto_executable":False,"authority":"CONSTRUCT_ONLY","actuation":"REFUSED:AMBIENT_ACTUATION"})
 queue.sort(key=lambda x:(x["priority"],x["operator"],x["object_id"]));counts={"objects":len(rows),"product_requirements":sum(r["kind"]=="product_requirement" for r in rows),"claims":sum(r["kind"]=="claim" for r in rows),"maturity_obligations":sum(r["kind"]=="enterprise_obligation" for r in rows),"workstreams":sum(r["kind"]=="foundry_workstream" for r in rows),"external_gates":sum(r["external_gate"] for r in rows),"documented_only":sum(r["computed_state"]=="DOCUMENTED_ONLY" for r in rows),"bounded_evidence_complete":sum(r["computed_state"]=="BOUNDED_EVIDENCE_COMPLETE" for r in rows),"bounded_evidence_partial":sum(r["computed_state"]=="BOUNDED_EVIDENCE_PARTIAL" for r in rows),"work_orders":len(queue),"qualified_evidence_bundles":sum(b["qualified"] for b in bundles)}
 return {"schema":"ggen.legacy.errc.reconstitution.matrix/2","ticket":"GL-ERRC-003","repository":"seanchatmangpt/ggen-legacy","subject_head":subject,"claim_ceiling":c["claim_ceiling"],"standing":"PARTIAL_ALIVE","counts":counts,"findings":find,"evidence_bundles":bundles,"matrix":rows,"work_queue":queue,"bound_evidence_paths":sorted(bound),"invariants":{"zero_unreceipted_actuation":True,"self_certification":False,"external_claims_auto_promoted":False,"explicit_evidence_mapping_required":True,"literal_identifier_mentions_are_evidence":False,"evidence_exclusions":sorted(map(rel,c.get("evidence_exclusions",[])))}}

def render(r:dict[str,Any])->str:
 c=r["counts"];lines=["# Fortune 5 ERRC Self-Reconstitution","",f"Subject: `{r['subject_head']}`",f"Standing: `{r['standing']}`",f"Claim ceiling: `{r['claim_ceiling']}`","","## Exact bounded inventory","",f"- Total objects: **{c['objects']}**",f"- Qualified evidence bundles: **{c['qualified_evidence_bundles']}**",f"- Bounded evidence complete: **{c['bounded_evidence_complete']}**",f"- Bounded evidence partial: **{c['bounded_evidence_partial']}**",f"- Documented only: **{c['documented_only']}**",f"- External gates: **{c['external_gates']}**",f"- Remaining work orders: **{c['work_orders']}**","","## Evidence bundles",""]
 lines += [f"- `{b['id']}` — `{'QUALIFIED' if b['qualified'] else 'UNQUALIFIED'}` — {b['scope']}" for b in r["evidence_bundles"]];lines += ["","## Findings",""]+[f"- `{f['code']}` — `{f['state']}`{': '+f.get('reason','') if f.get('reason') else ''}" for f in r["findings"]];lines += ["","## Highest-priority remaining work",""]+[f"- P{x['priority']} `{x['operator']}` `{x['object_id']}` — {x['reason']}" for x in r["work_queue"][:30]];return "\n".join(lines)+"\n"
def emit(root:Path,out:Path,cp:Path,strict:bool)->dict[str,Any]:
 r=build(root,cp,strict);m=dict(r);q=m.pop("work_queue");products={"matrix.json":cj(m),"work-queue.json":cj({"schema":"ggen.legacy.errc.work-queue/2","ticket":"GL-ERRC-003","items":q}),"report.md":render(r).encode()};c=load(cp);mp=rel(c["evidence_map"]);sources=["AGENTS.md","RELEASE_CONTROL.md","product/PRD.md","architecture/ARD.md","governance/claims-register.md","governance/enterprise-maturity-model.md","governance/production-gaps.md","foundry/bootstrap.yaml",cp.relative_to(root).as_posix(),mp,"scripts/reconstitute_fortune5.py","scripts/fortune5_reconstitute_v2.py","scripts/verify_fortune5_reconstitution.py","scripts/fortune5_verify_v2.py","tickets/GL-ERRC-003.md",".github/workflows/ci.yml"];sm={p:fh(root/p) for p in sources if (root/p).is_file()};em={p:fh(root/p) for p in r["bound_evidence_paths"] if (root/p).is_file() and p!=mp};om={p:h(d) for p,d in sorted(products.items())};receipt={"schema":"ggen.legacy.errc.reconstitution.receipt/2","ticket":"GL-ERRC-003","repository":"seanchatmangpt/ggen-legacy","subject_head":r["subject_head"],"claim_ceiling":r["claim_ceiling"],"source_manifest":sm,"evidence_manifest":em,"output_manifest":om,"replay_identity":h(cj({"sources":sm,"evidence":em,"outputs":om})),"standing":"PARTIAL_ALIVE","actuation":"ANALYSIS_OUTPUT_DIRECTORY_ONLY","external_production_standing":"UNKNOWN"};products["receipt.json"]=cj(receipt);out.mkdir(parents=True,exist_ok=True)
 for p,d in sorted(products.items()):write(out,p,d)
 return receipt
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument("--contract",type=Path);ap.add_argument("--output",type=Path,required=True);ap.add_argument("--strict",action="store_true");a=ap.parse_args();root=a.root.resolve();cp=(a.contract or root/"authority/fortune5-reconstitution.json").resolve()
 try:r=emit(root,a.output.resolve(),cp,a.strict)
 except (OSError,Refusal) as e:print(str(e),file=sys.stderr);return 2
 print(json.dumps(r,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
