#!/usr/bin/env python3
"""Verify the original v26.8.1 migration and every admitted successor edge.

The original migration is replayed against the exact historical corpus head.
Later changes require explicit successor admission.  A special MATERIALIZED
kind exists only for files that the migration lineage proves were source
artifacts but the corpus commit omitted because they were ignored; their
current blob must equal both the lineage source blob and the exact blob first
committed by the corpus-retention repair.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("migrations/ggen-v26.8.1/migration-manifest.json")
SUCCESSOR = Path("authority/ggen-v26.8.1-successor.json")
ORIGINAL_VERIFIER = Path("scripts/verify_ggen_v26_8_1_migration.py")
ACTIVE_ROOTS = (
    Path("docs/v26.8.1"), Path("ontology/v26.8.1"), Path("planning/v26.8.1"),
    Path("tools/v26.8.1"), Path("packs/legacy-equivalence-verifier-pack"),
)

class Refusal(RuntimeError): pass

def run(argv:list[str],cwd:Path,timeout:int=1200)->subprocess.CompletedProcess[str]:
    return subprocess.run(argv,cwd=cwd,text=True,capture_output=True,check=False,timeout=timeout)
def require(argv:list[str],cwd:Path,timeout:int=1200)->str:
    p=run(argv,cwd,timeout)
    if p.returncode: raise Refusal("REFUSED:COMMAND_FAILED argv="+json.dumps(argv)+f" exit={p.returncode} stdout={p.stdout[-4000:]} stderr={p.stderr[-4000:]}")
    return p.stdout
def git_head(root:Path)->str:
    v=require(["git","rev-parse","HEAD"],root).strip()
    if len(v)!=40: raise Refusal("REFUSED:CANDIDATE_HEAD_UNAVAILABLE")
    return v
def safe_path(v:Any)->str:
    s=str(v);p=Path(s)
    if not s or p.is_absolute() or ".." in p.parts: raise Refusal(f"REFUSED:UNSAFE_SUCCESSOR_PATH:{s}")
    return p.as_posix()
def worktree_blob(root:Path,rel:str)->str|None:
    if not (root/rel).is_file(): return None
    return require(["git","hash-object","--",rel],root).strip() or None
def tree_blob(root:Path,commit:str,rel:str)->str|None:
    p=run(["git","ls-tree",commit,"--",rel],root,30)
    if p.returncode: raise Refusal(f"REFUSED:GIT_TREE_QUERY_FAILED:{commit}:{rel}:{p.stderr.strip()}")
    line=p.stdout.strip()
    if not line:return None
    parts=line.split()
    if len(parts)<3 or parts[1]!="blob":raise Refusal(f"REFUSED:NON_BLOB_SUCCESSOR_PATH:{commit}:{rel}")
    return parts[2]
def ancestor(root:Path,a:str,b:str)->bool:return run(["git","merge-base","--is-ancestor",a,b],root,30).returncode==0

def lineage(root:Path,manifest:dict[str,Any])->dict[str,str]:
    out:dict[str,str]={}
    for component in manifest["components"]:
        data=json.loads((root/safe_path(component["migration_evidence"])).read_text())
        for record in data.get("files",[]):
            rel=safe_path(record["destination_path"]);blob=str(record.get("source_git_blob", ""))
            if rel in out and out[rel]!=blob:raise Refusal(f"REFUSED:LINEAGE_COLLISION:{rel}")
            if len(blob)!=40:raise Refusal(f"REFUSED:LINEAGE_BLOB_MISSING:{rel}")
            out[rel]=blob
    return out

def verify_successor(root:Path,candidate:str)->dict[str,Any]:
    manifest=json.loads((root/MANIFEST).read_text());auth=json.loads((root/SUCCESSOR).read_text())
    if auth.get("schema")!="ggen.legacy.migration-successor/2":raise Refusal("REFUSED:SUCCESSOR_SCHEMA")
    corpus=str(manifest["corpus_head"])
    if auth.get("corpus_head")!=corpus:raise Refusal("REFUSED:SUCCESSOR_CORPUS_HEAD_MISMATCH")
    if not ancestor(root,corpus,candidate):raise Refusal(f"REFUSED:CORPUS_HEAD_UNRELATED corpus={corpus} candidate={candidate}")
    inherited=lineage(root,manifest);entries:dict[str,dict[str,Any]]={}
    for raw in auth.get("entries",[]):
        rel=safe_path(raw.get("path"));kind=str(raw.get("kind"));origin=str(raw.get("origin_commit",""));expected=str(raw.get("git_blob",""))
        if rel in entries:raise Refusal(f"REFUSED:DUPLICATE_SUCCESSOR_PATH:{rel}")
        if kind not in {"MODIFIED","ADDED","MATERIALIZED"}:raise Refusal(f"REFUSED:SUCCESSOR_KIND:{rel}:{kind}")
        if len(origin)!=40 or len(expected)!=40:raise Refusal(f"REFUSED:SUCCESSOR_IDENTITY:{rel}")
        if not ancestor(root,corpus,origin) or not ancestor(root,origin,candidate):raise Refusal(f"REFUSED:SUCCESSOR_ORIGIN_UNRELATED:{rel}:{origin}")
        origin_blob=tree_blob(root,origin,rel);current=worktree_blob(root,rel);historical=tree_blob(root,corpus,rel)
        if origin_blob!=expected:raise Refusal(f"REFUSED:SUCCESSOR_ORIGIN_BLOB_DRIFT:{rel}:expected={expected}:observed={origin_blob}")
        if current!=expected:raise Refusal(f"REFUSED:SUCCESSOR_CURRENT_BLOB_DRIFT:{rel}:expected={expected}:observed={current}")
        if kind=="MODIFIED":
            if rel not in inherited or historical is None or historical==expected:raise Refusal(f"REFUSED:SUCCESSOR_MODIFICATION_NOT_PROVEN:{rel}")
        elif kind=="ADDED":
            if rel in inherited or historical is not None:raise Refusal(f"REFUSED:SUCCESSOR_ADDITION_NOT_PROVEN:{rel}")
        else:
            if rel not in inherited or historical is not None:raise Refusal(f"REFUSED:SUCCESSOR_MATERIALIZATION_NOT_PROVEN:{rel}")
            if inherited[rel]!=expected:raise Refusal(f"REFUSED:MATERIALIZED_BLOB_DIFFERS_FROM_LINEAGE:{rel}:lineage={inherited[rel]}:observed={expected}")
        entries[rel]=dict(raw)
    changed_inherited=[]
    for rel in sorted(inherited):
        historical=tree_blob(root,corpus,rel);current=worktree_blob(root,rel)
        if current!=historical:
            changed_inherited.append(rel);entry=entries.get(rel);expected_kind="MATERIALIZED" if historical is None else "MODIFIED"
            if entry is None or entry.get("kind")!=expected_kind:raise Refusal(f"REFUSED:UNMAPPED_INHERITED_DRIFT:{rel}:expected_kind={expected_kind}")
    admitted_inherited=sorted(rel for rel,e in entries.items() if e["kind"] in {"MODIFIED","MATERIALIZED"})
    if changed_inherited!=admitted_inherited:raise Refusal("REFUSED:SUCCESSOR_INHERITED_SET_MISMATCH observed="+json.dumps(changed_inherited)+" admitted="+json.dumps(admitted_inherited))
    return {"schema":"ggen.legacy.migration-successor.verification/2","corpus_head":corpus,"candidate_head":candidate,"admitted_origin_commits":sorted({str(e["origin_commit"]) for e in entries.values()}),"modified_inherited_files":sorted(rel for rel,e in entries.items() if e["kind"]=="MODIFIED"),"materialized_lineage_files":sorted(rel for rel,e in entries.items() if e["kind"]=="MATERIALIZED"),"added_successor_files":sorted(rel for rel,e in entries.items() if e["kind"]=="ADDED"),"standing":"ALIVE","claim_ceiling":"POST_MIGRATION_EVOLUTION_ONLY"}

def historical_checkout(root:Path,target:Path,candidate:str,corpus:str)->None:
    require(["git","clone","--no-hardlinks","--no-checkout","--quiet",str(root),str(target)],target.parent,300)
    require(["git","checkout","--detach",candidate],target,60)
    for rel in ACTIVE_ROOTS:
        p=target/rel
        if p.is_dir():shutil.rmtree(p)
        elif p.exists():p.unlink()
    require(["git","checkout",corpus,"--",*[x.as_posix() for x in ACTIVE_ROOTS]],target,60)

def behavior(root:Path)->list[dict[str,Any]]:
    cmds=[["cargo","fmt","--manifest-path","tools/v26.8.1/Cargo.toml","--all","--","--check"],["cargo","test","--manifest-path","tools/v26.8.1/Cargo.toml","--locked","--all-targets"]];out=[]
    for argv in cmds:
        p=run(argv,root,1200);out.append({"argv":argv,"exit_status":p.returncode})
        if p.returncode:raise Refusal("REFUSED:SUCCESSOR_BEHAVIOR_FAILED argv="+json.dumps(argv)+f" stdout={p.stdout[-4000:]} stderr={p.stderr[-4000:]}")
    return out

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--source-root",type=Path,required=True);ap.add_argument("--destination-root",type=Path,default=ROOT);ap.add_argument("--report",type=Path,default=Path("migrations/ggen-v26.8.1/verifier-report.json"));a=ap.parse_args();root=a.destination_root.resolve();source=a.source_root.resolve();report=a.report if a.report.is_absolute() else root/a.report
    try:
        candidate=git_head(root);manifest=json.loads((root/MANIFEST).read_text());succ=verify_successor(root,candidate);corpus=str(manifest["corpus_head"])
        with tempfile.TemporaryDirectory(prefix="ggen-v26-8-1-historical-") as raw:
            hist=Path(raw)/"corpus";historical_checkout(root,hist,candidate,corpus);hr=hist/"migrations/ggen-v26.8.1/verifier-report.json"
            p=run([sys.executable,str(root/ORIGINAL_VERIFIER),"--source-root",str(source),"--destination-root",str(hist),"--report",str(hr)],root,1800)
            if p.returncode:sys.stdout.write(p.stdout);sys.stderr.write(p.stderr);return p.returncode
            base=json.loads(hr.read_text())
        br=behavior(root);base["historical_corpus_replay"]={"corpus_head":corpus,"standing":"ALIVE","byte_identity":"SOURCE_EQUALS_HISTORICAL_CORPUS"};base["successor_admission"]=succ;base["successor_behavior_receipts"]=br;base["candidate_head"]=candidate;base["standing"]="PARTIAL_ALIVE";base["claim_ceiling"]="HISTORICAL_MIGRATION_PLUS_EXPLICIT_SUCCESSOR_EVOLUTION";report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(base,indent=2,sort_keys=True)+"\n")
        print(json.dumps({"candidate_head":candidate,"historical_corpus":"ALIVE","successor_admission":"ALIVE","modified_inherited_files":len(succ["modified_inherited_files"]),"materialized_lineage_files":len(succ["materialized_lineage_files"]),"added_successor_files":len(succ["added_successor_files"]),"standing":"PARTIAL_ALIVE"},sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,Refusal,subprocess.TimeoutExpired) as e:print(str(e),file=sys.stderr);return 3
if __name__=="__main__":raise SystemExit(main())
