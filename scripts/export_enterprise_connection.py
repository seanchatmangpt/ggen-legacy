#!/usr/bin/env python3
"""Export the admitted ggen-legacy foundry state as ConnectionEnvelope v1.

This is a CONSTRUCT-only transport projection. It does not advance A-K,
manufacture a repository, grant cloud authority, or transfer standing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
from typing import Any

SCHEMA = "urn:ggen:enterprise-connection:v1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")

class Refusal(ValueError):
    pass

def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()

def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _safe_rel(value: str) -> bool:
    normalized = value.replace("\\", "/"); p = PurePosixPath(normalized); w = PureWindowsPath(value)
    return bool(value) and not p.is_absolute() and not w.is_absolute() and not w.drive and ".." not in p.parts

def _read_object(path: Path) -> dict[str, Any]:
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise Refusal(f"REFUSED:INPUT:{path}:{exc}") from exc
    if not isinstance(value, dict): raise Refusal(f"REFUSED:INPUT:{path}:expected object")
    return value

def _artifact(root: Path, relative: str, role: str, media_type: str) -> dict[str, str]:
    if not _safe_rel(relative): raise Refusal(f"REFUSED:UNSAFE_PATH:{relative}")
    path = root / relative
    if not path.is_file(): raise Refusal(f"REFUSED:EVIDENCE_MISSING:{relative}")
    return {"path":relative,"role":role,"media_type":media_type,"digest":_digest(path.read_bytes())}

def export_connection(root: Path, revision: str, out: Path, connection_id: str | None = None) -> dict[str, Any]:
    root=root.resolve()
    if not HEX40.fullmatch(revision): raise Refusal(f"REFUSED:REVISION:{revision}")
    program_path=root/"authority/foundry-work-program.json"; state_path=root/"foundry/workstreams/state.json"
    program=_read_object(program_path); state=_read_object(state_path)
    if program.get("schema_version") != "ggen.enterprise-architecture-foundry.work-program/1": raise Refusal("REFUSED:PROGRAM_SCHEMA")
    if state.get("schema_version") != "ggen.enterprise-architecture-foundry.corpus/1": raise Refusal("REFUSED:STATE_SCHEMA")
    if program.get("program_id") != state.get("program_id"): raise Refusal("REFUSED:PROGRAM_ID_DRIFT")
    workstreams=state.get("workstreams")
    if not isinstance(workstreams,dict) or not workstreams: raise Refusal("REFUSED:WORKSTREAM_STATE")
    admitted=sorted(str(name) for name,item in workstreams.items() if isinstance(item,dict) and item.get("status")=="ADMITTED")
    graph_rel="foundry/evidence/B/legacy-capabilities.ttl"; graph_artifact=_artifact(root,graph_rel,"ggen-legacy:admitted-capability-graph","text/turtle")
    artifacts=[_artifact(root,"authority/foundry-work-program.json","ggen-legacy:work-program","application/json"),_artifact(root,"foundry/workstreams/state.json","ggen-legacy:workstream-state","application/json"),graph_artifact]
    evidence=[]
    for name in admitted:
        item=workstreams[name]; receipt=item.get("receipt_path")
        if not isinstance(receipt,str): raise Refusal(f"REFUSED:ADMITTED_WITHOUT_RECEIPT:{name}")
        artifact=_artifact(root,receipt,f"ggen-legacy:workstream-{name}-receipt","application/json"); artifacts.append(artifact)
        evidence.append({"kind":"foundry-workstream-admission","identity":f"{name}:ADMITTED","digest":artifact["digest"]})
    capabilities=program.get("initial_solution_packs"); invariants=program.get("invariants")
    if not isinstance(capabilities,list) or any(not isinstance(x,str) or not x for x in capabilities): raise Refusal("REFUSED:CAPABILITY_SET")
    if not isinstance(invariants,list) or any(not isinstance(x,str) or not x for x in invariants): raise Refusal("REFUSED:INVARIANT_SET")
    program_digest=_digest(program_path.read_bytes()); state_digest=_digest(state_path.read_bytes())
    env={"schema":SCHEMA,"connection_id":connection_id or f"urn:ggen:connection:{program['program_id']}","stage":"RECONSTITUTE","producer":{"repository":"seanchatmangpt/ggen-legacy","revision":revision,"component":"GL-CONN-001"},"subject":{"id":str(program["program_id"]),"kind":"enterprise-architecture-reconstitution","revision":program_digest},"architecture":{"graph":{"path":graph_rel,"media_type":"text/turtle","digest":graph_artifact["digest"]},"capabilities":sorted(set(capabilities)),"constraints":sorted(set(invariants))},"packs":[],"artifacts":sorted(artifacts,key=lambda x:x["path"]),"authority":{"ceiling":"CONSTRUCT_ONLY","do_authority":False},"standing":{"state":"PARTIAL_ALIVE" if admitted else "UNKNOWN","claim":f"FOUNDRY_WORKSTREAMS_ADMITTED={','.join(admitted) or 'NONE'}; CONNECTION_EXPORT_EXECUTED; COMPLETE_A_K_AND_EXTERNAL_PRODUCTION_NOT_INFERRED"},"parent":None,"evidence":sorted(evidence,key=lambda x:x["identity"]),"next":[{"consumer":"seanchatmangpt/ggen-create","operation":"generalize"}],"labels":{"program_status":str(program.get("status","UNKNOWN")),"admitted_workstreams":",".join(admitted),"workstream_count":str(len(workstreams)),"program_digest":program_digest,"state_digest":state_digest}}
    data=_canonical(env); out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(data); return env

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,default=Path(".")); parser.add_argument("--revision",required=True); parser.add_argument("--connection-id"); parser.add_argument("--out",type=Path,required=True); args=parser.parse_args()
    try: env=export_connection(args.root,args.revision,args.out,args.connection_id)
    except (Refusal,OSError) as exc: print(json.dumps({"standing":"REFUSED","error":str(exc)},sort_keys=True)); return 2
    print(json.dumps({"standing":env["standing"]["state"],"stage":env["stage"],"out":str(args.out),"digest":_digest(args.out.read_bytes()),"do_authority":False},sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
