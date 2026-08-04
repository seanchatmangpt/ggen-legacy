#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, re, tempfile
from pathlib import Path
from typing import Any

PROCESS_STATES={"observed","admitted","inferred","proposed","decided","executed","verified","blocked","unsupported","refused"}
STANDINGS={"UNKNOWN","PARTIAL_ALIVE","ALIVE","BLOCKED","BUILD_BROKEN","UNSUPPORTED"}
PROJECTIONS={"architecture","working_backwards","claude","ppddl","gaps","toyota","genesis","hygen","schemas"}
REQUIRED_DECISION_FIELDS=("authority","acceptance","falsifier","evidence")
TOKEN_RE=re.compile(r"^[a-z][a-z0-9]{3}$")

class Refusal(ValueError): pass

def cj(v:Any)->bytes:return (json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
def dg(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def token_13(subject:str,operation:str)->str:
    s="".join(c for c in subject.lower() if c.isalnum()); o="".join(c for c in operation.lower() if c.isalnum())
    if not s or len(o)<3: raise Refusal("REFUSED:INVALID_IDENTITY_PAIR")
    return s[0]+o[:3]

def validate(bundle:dict[str,Any])->dict[str,Any]:
    subject=bundle.get("subject")
    if not isinstance(subject,dict) or not subject.get("id"): raise Refusal("REFUSED:MISSING_SUBJECT_ID")
    concepts=bundle.get("concepts")
    if not isinstance(concepts,list) or not concepts: raise Refusal("REFUSED:MISSING_CONCEPTS")
    seen=set(); norm=[]
    for raw in concepts:
        if not isinstance(raw,dict) or not raw.get("id"): raise Refusal("REFUSED:INVALID_CONCEPT")
        cid=str(raw["id"])
        if cid in seen: raise Refusal(f"REFUSED:DUPLICATE_CONCEPT:{cid}")
        seen.add(cid)
        state=raw.get("state","observed"); standing=raw.get("standing","UNKNOWN")
        if state not in PROCESS_STATES: raise Refusal(f"REFUSED:UNKNOWN_PROCESS_STATE:{state}")
        if standing not in STANDINGS and not str(standing).startswith("REFUSED:"): raise Refusal(f"REFUSED:UNKNOWN_STANDING:{standing}")
        decision=raw.get("decision")
        if state in {"decided","admitted","executed","verified"}:
            if not isinstance(decision,dict): raise Refusal(f"REFUSED:UNBOUND_DECISION:{cid}")
            for f in REQUIRED_DECISION_FIELDS:
                if not decision.get(f): raise Refusal(f"REFUSED:DECISION_MISSING_{f.upper()}:{cid}")
        norm.append({"id":cid,"label":str(raw.get("label",cid)),"kind":str(raw.get("kind","concept")),"state":state,"standing":standing,"summary":str(raw.get("summary","")),"evidence":sorted(str(x) for x in raw.get("evidence",[])),"depends_on":sorted({str(x) for x in raw.get("depends_on",[])}),"authority":str(raw.get("authority","SELECT_ONLY")),"decision":decision})
    unknown=sorted({d for c in norm for d in c["depends_on"] if d not in seen})
    if unknown: raise Refusal("REFUSED:UNKNOWN_DEPENDENCY:"+",".join(unknown))
    requested=bundle.get("projections",sorted(PROJECTIONS))
    if not isinstance(requested,list) or not set(requested).issubset(PROJECTIONS): raise Refusal("REFUSED:UNKNOWN_PROJECTION")
    system=bundle.get("system")
    if not isinstance(system,dict): raise Refusal("REFUSED:MISSING_SYSTEM")
    calc=system.get("calculus",{})
    required_calc={"Observation","AdmittedObservation","Capability","Construction","Actuation","Consequence","Receipt","Replay","Standing"}
    if set(calc)!=required_calc: raise Refusal("REFUSED:INCOMPLETE_CALCULUS")
    lane=system.get("production_lane",{})
    for f in ("wip_limit","takt","kanban","andon","brce","completion"):
        if not lane.get(f): raise Refusal(f"REFUSED:LANE_MISSING_{f.upper()}")
    if lane["wip_limit"]!=1: raise Refusal("REFUSED:WIP_LIMIT_NOT_ONE")
    prot=system.get("protocols",{})
    for symbol in ("策","標準作業","실행","証","止"):
        if symbol not in prot: raise Refusal(f"REFUSED:MISSING_PROTOCOL:{symbol}")
    naming=system.get("naming",{})
    pairs=naming.get("pairs",[]); tokens={}
    for pair in pairs:
        t=token_13(pair["subject"],pair["operation"])
        if pair.get("token")!=t or not TOKEN_RE.match(t): raise Refusal("REFUSED:INVALID_CLI_TOKEN")
        if t in tokens: raise Refusal(f"REFUSED:CLI_COLLISION:{t}")
        tokens[t]=pair
    crown=system.get("first_crown",{})
    for f in ("customer","demand","capability","initial_state","consequence","verifier","terminal_standing"):
        if not crown.get(f): raise Refusal(f"REFUSED:CROWN_MISSING_{f.upper()}")
    bootstrap=system.get("hygen_bootstrap",{})
    if not bootstrap.get("files") or not bootstrap.get("retirement_predicates"): raise Refusal("REFUSED:INCOMPLETE_HYGEN_BOOTSTRAP")
    return {"schema":"ggen-legacy.autonomic.v2","subject":{"id":str(subject["id"]),"source":str(subject.get("source","conversation")),"base":str(subject.get("base","UNKNOWN"))},"concepts":sorted(norm,key=lambda c:c["id"]),"projections":sorted(set(requested)),"constraints":sorted(str(x) for x in bundle.get("constraints",[])),"system":system,"cli_tokens":tokens}

def gaps(graph):
    out=[]
    for c in graph["concepts"]:
        if c["state"] not in {"decided","admitted","executed","verified"} or not isinstance(c["decision"],dict):
            out.append({"concept":c["id"],"state":c["state"],"standing":c["standing"],"required_decision":"admit, reject, or refine"})
    return out

def architecture(g):
    lines=["# Canonical Autonomic Architecture","",f"Subject: `{g['subject']['id']}`","","## Constitutional calculus",""]
    for k,v in g["system"]["calculus"].items(): lines.append(f"- **{k}** — {v}")
    lines += ["","## Concepts",""]
    for c in g["concepts"]:
        lines += [f"### {c['label']} (`{c['id']}`)","",c["summary"],"",f"- State: `{c['state']}`",f"- Standing: `{c['standing']}`",f"- Authority: `{c['authority']}`",f"- Acceptance: `{c['decision']['acceptance']}`"," "]
    return "\n".join(lines)

def working(g):
    c=g["system"]["first_crown"]
    return f"# Working Backwards\n\n## Press release\n\n{c['customer']} can now request `{c['capability']}` and receive `{c['consequence']}` through one WIP-limited, receipt-bearing, replayable production lane.\n\n## Customer demand\n\n{c['demand']}\n\n## Acceptance\n\n`{c['verifier']}` establishes `{c['terminal_standing']}`.\n"

def claude_root(g):
    return "# Claude Production Operator\n\nCanonical sequence: 策 → 標準作業 → 실행 → 証. 止 is mandatory on abnormality.\n\nLoad `.claude/agents/`, `.claude/skills/`, and `.claude/settings.json`. No role may self-certify or bypass BRCE.\n"

def agent(name,symbol,authority): return f"---\nname: {name}\n---\n# {symbol} {name}\n\nAuthority: `{authority}`. Emit machine-readable output only. Stop on scope drift, missing evidence, missing authority, or WIP > 1.\n"
def skill(name,sequence): return f"# Skill: {name}\n\nSequence: `{sequence}`. Required output: subject, authority, acceptance, falsifier, receipt destination, standing.\n"
def settings(g):
    return cj({"permissions":{"defaultMode":"plan","allow":["Read","Glob","Grep"],"deny":["Bash(git push:*)","Bash(git reset --hard:*)","Bash(rm -rf:*)"]},"hooks":{"PreToolUse":[{"matcher":"Edit|Write|Bash","hooks":[{"type":"command","command":"python3 .claude/hooks/protocol_andon.py"}]}]}})
def hook():
    return '''#!/usr/bin/env python3\nimport json,os,sys\nphase=os.environ.get("GGEN_PROTOCOL","策")\ntool=os.environ.get("CLAUDE_TOOL_NAME","")\nif phase=="策" and tool in {"Edit","Write","Bash"}:\n print(json.dumps({"decision":"deny","reason":"ANDON_策_ACTUATION_REFUSED"}));sys.exit(2)\nif phase=="실행" and not os.environ.get("BRCE_GRANT"):\n print(json.dumps({"decision":"deny","reason":"ANDON_실행_MISSING_BRCE_GRANT"}));sys.exit(2)\nprint(json.dumps({"decision":"allow"}))\n'''.encode()
def ppddl_domain(g):
    return """(define (domain autonomic-foundry)\n (:requirements :strips :typing :negative-preconditions :action-costs)\n (:types concept)\n (:predicates (observed ?c - concept)(admitted ?c - concept)(resolved ?c - concept)(projected ?c - concept)(receipted ?c - concept)(wip-free)(wip-active)(andon))\n (:functions (total-cost))\n (:action admit :parameters (?c - concept) :precondition (and (observed ?c)(wip-free)(not (andon))) :effect (and (admitted ?c)(wip-active)(not (wip-free))(increase (total-cost) 1)))\n (:action resolve :parameters (?c - concept) :precondition (and (admitted ?c)(wip-active)(not (andon))) :effect (and (resolved ?c)(increase (total-cost) 1)))\n (:action project :parameters (?c - concept) :precondition (and (resolved ?c)(wip-active)(not (andon))) :effect (and (projected ?c)(increase (total-cost) 1)))\n (:action receipt :parameters (?c - concept) :precondition (and (projected ?c)(wip-active)) :effect (and (receipted ?c)(wip-free)(not (wip-active))(increase (total-cost) 1)))\n)\n"""
def ppddl_problem(g):
    objs=" ".join(c["id"].replace(".","-") for c in g["concepts"]); init="\n".join(f"  (observed {c['id'].replace('.', '-')})" for c in g["concepts"]); goals="\n".join(f"  (receipted {c['id'].replace('.', '-')})" for c in g["concepts"])
    return f"(define (problem close-conversation) (:domain autonomic-foundry) (:objects {objs} - concept) (:init\n{init}\n  (wip-free)(= (total-cost) 0)) (:goal (and\n{goals}\n  (wip-free))) (:metric minimize (total-cost)))\n"
def kanban(g): return cj({"schema":"ggen.kanban.v1","quantity":1,"lane":g["system"]["production_lane"],"crown":g["system"]["first_crown"]})
def naming(g): return cj({"schema":"ggen.genesis-naming.v1","law":"first(subject)+first3(operation)","tokens":g["cli_tokens"]})
def schema(): return cj({"$schema":"https://json-schema.org/draft/2020-12/schema","title":"AdmittedDecision","type":"object","required":["authority","acceptance","falsifier","evidence"],"properties":{"authority":{"type":"string"},"acceptance":{"type":"string"},"falsifier":{"type":"string"},"evidence":{"type":"array","minItems":1,"items":{"type":"string"}}},"additionalProperties":True})
def hygen_files(g):
    products={}
    for path in g["system"]["hygen_bootstrap"]["files"]:
        products[f"hygen/_templates/ggen/bootstrap/{path}.ejs.t"]=(f"---\nto: <%= projectName %>/{path}\n---\n# Bootstrap projection: {path}\n").encode()
    return products

def atomic(root,rel,data):
    target=(root/rel).resolve(); rr=root.resolve()
    if target!=rr and rr not in target.parents: raise Refusal("REFUSED:OUTPUT_ESCAPE")
    target.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=".foundry-",dir=str(target.parent))
    try:
        with os.fdopen(fd,"wb") as h:h.write(data)
        os.replace(tmp,target)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def manufacture(bundle,output):
    g=validate(bundle); unresolved=gaps(g)
    products={"canonical-graph.json":cj(g),"ARCHITECTURE.md":(architecture(g)+"\n").encode(),"WORKING_BACKWARDS.md":working(g).encode(),"CLAUDE.md":claude_root(g).encode(),"GAPS.json":cj({"gaps":unresolved}),"ppddl/domain.pddl":ppddl_domain(g).encode(),"ppddl/problem.pddl":ppddl_problem(g).encode(),"production/KANBAN.json":kanban(g),"genesis/NAMING.json":naming(g),"schemas/admitted-decision.schema.json":schema(),".claude/settings.json":settings(g),".claude/hooks/protocol_andon.py":hook(),".claude/agents/strategist.md":agent("strategist","策","SELECT_ONLY").encode(),".claude/agents/production-engineer.md":agent("production-engineer","標準作業","CONSTRUCT_ONLY").encode(),".claude/agents/operator.md":agent("operator","실행","BRCE_ONLY").encode(),".claude/agents/inspector.md":agent("inspector","証","VERIFY_ONLY").encode(),".claude/skills/close-capability/SKILL.md":skill("close-capability","demand→admit→construct→BRCE→receipt→replay→standing").encode()}
    products.update(hygen_files(g))
    manifest={p:dg(d) for p,d in sorted(products.items())}
    standing="ALIVE" if not unresolved else "PARTIAL_ALIVE"
    receipt={"schema":"ggen-legacy.autonomic.receipt.v2","subject":g["subject"],"claim_ceiling":"AUTONOMIC_BOOTSTRAP_PROJECTION_ONLY","input_sha256":dg(cj(bundle)),"canonical_graph_sha256":manifest["canonical-graph.json"],"outputs":manifest,"gap_count":len(unresolved),"standing":standing,"actuation":"OUTPUT_DIRECTORY_ONLY","replay_identity":dg(cj(manifest))}
    products["RECEIPT.json"]=cj(receipt)
    output.mkdir(parents=True,exist_ok=True)
    for p,d in sorted(products.items()):atomic(output,p,d)
    return receipt

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",required=True,type=Path);ap.add_argument("--output",required=True,type=Path);a=ap.parse_args()
    try:r=manufacture(json.loads(a.input.read_text()),a.output)
    except (OSError,json.JSONDecodeError,Refusal) as e: print(str(e),file=os.sys.stderr);return 2
    print(json.dumps(r,ensure_ascii=False,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
