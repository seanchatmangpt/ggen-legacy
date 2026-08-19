#!/usr/bin/env python3
"""Bounded implementation-extinction court; never a universal equivalence decider."""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

def invoke(command:list[str], request:dict)->dict:
    p=subprocess.run(command,input=json.dumps(request,sort_keys=True),text=True,capture_output=True,check=False,timeout=5)
    if p.returncode!=0: raise RuntimeError(f"BLOCKED:IMPLEMENTATION_EXIT:{p.returncode}:{p.stderr.strip()}")
    lines=[x for x in p.stdout.splitlines() if x.strip()]
    if len(lines)!=1: raise RuntimeError("REFUSED:NON_SINGLE_RESPONSE")
    out=json.loads(lines[0])
    if not isinstance(out,dict): raise RuntimeError("REFUSED:NON_OBJECT_RESPONSE")
    return out

def verify(vectors:list[dict], command:list[str])->list[dict]:
    results=[]
    for v in vectors:
        actual=invoke(command,v["request"]); expected=v["expect"]
        results.append({"id":v["id"],"ok":all(actual.get(k)==val for k,val in expected.items()),"actual":actual,"expect":expected})
    return results

def court(vectors_path:Path,replacement:list[str],original_absent:Path|None=None)->dict:
    if original_absent is not None and original_absent.exists(): return {"standing":"REFUSED:ORIGINAL_STILL_PRESENT","original_absent":False}
    results=verify(json.loads(vectors_path.read_text()),replacement); failures=[r for r in results if not r["ok"]]
    return {"standing":"PARTIAL_ALIVE" if not failures else "BUILD_BROKEN","scope":"finite-observable-vector-equivalence","rice_fence":"no universal semantic equivalence claim","original_absent":original_absent is None or not original_absent.exists(),"vectors":len(results),"failures":failures}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--vectors",required=True,type=Path); ap.add_argument("--original-absent",type=Path); ap.add_argument("implementation",nargs=argparse.REMAINDER); a=ap.parse_args()
    if not a.implementation: ap.error("implementation command required")
    report=court(a.vectors,a.implementation,a.original_absent); print(json.dumps(report,sort_keys=True,separators=(",",":"))); return 0 if report["standing"]=="PARTIAL_ALIVE" else 1
if __name__=="__main__": raise SystemExit(main())
