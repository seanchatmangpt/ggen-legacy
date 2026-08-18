#!/usr/bin/env python3
"""Deterministic external legacy observation. Emits OBSERVED evidence, never admission."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, sys, tomllib
from pathlib import Path
from typing import Any

VERSION = "1"

class ReconstitutionError(RuntimeError):
    def __init__(self, code: str, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message); self.code = code; self.detail = detail or {}
    def to_json(self): return {"status":"REFUSED","code":self.code,"message":str(self),"detail":self.detail}

def h(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def jb(v: Any) -> bytes: return (json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
def sh(argv: list[str], cwd: Path, code: str) -> tuple[str,str,dict[str,Any]]:
    p=subprocess.run(argv,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode:
        raise ReconstitutionError(code,f"command failed ({p.returncode}): {' '.join(argv)}",{"stderr":p.stderr[-4000:]})
    r={"argv":argv,"exit_code":0,"stdout_sha256":h(p.stdout.encode()),"stderr_sha256":h(p.stderr.encode())}
    return p.stdout,p.stderr,r

def rel(raw: str) -> str:
    p=Path(raw)
    if p.is_absolute() or ".." in p.parts: raise ReconstitutionError("CONTRACT_INVALID",f"unsafe relative path: {raw}")
    return p.as_posix()

def contract(path: Path) -> dict[str,Any]:
    try: v=json.loads(path.read_text())
    except Exception as e: raise ReconstitutionError("CONTRACT_INVALID",f"cannot load contract: {e}") from e
    for k in ("case_id","source","observation"):
        if k not in v: raise ReconstitutionError("CONTRACT_INVALID",f"missing field: {k}")
    for k in ("repo","ref","sha","license_expression","expected_files"):
        if k not in v["source"]: raise ReconstitutionError("CONTRACT_INVALID",f"missing source field: {k}")
    if not re.fullmatch(r"[0-9a-f]{40}",str(v["source"]["sha"])): raise ReconstitutionError("CONTRACT_INVALID","source.sha must be 40 lowercase hex")
    return v

def verify_source(src: Path, c: dict[str,Any]):
    cmds=[]; out,_,r=sh(["git","rev-parse","HEAD"],src,"SOURCE_GIT_UNAVAILABLE"); cmds.append(r)
    actual=out.strip(); expected=c["source"]["sha"]
    if actual != expected: raise ReconstitutionError("SOURCE_IDENTITY_MISMATCH","checked-out source differs from exact contract",{"expected":expected,"actual":actual})
    out,_,r=sh(["git","status","--porcelain=v1","--untracked-files=no"],src,"SOURCE_GIT_UNAVAILABLE"); cmds.append(r)
    if out.strip(): raise ReconstitutionError("SOURCE_TREE_DIRTY","tracked source tree contains local modifications",{"status":out.splitlines()})
    files=[]
    for raw in c["source"]["expected_files"]:
        rp=rel(raw); p=src/rp
        if not p.is_file(): raise ReconstitutionError("SOURCE_EXPECTED_FILE_MISSING",f"missing: {rp}")
        files.append({"path":rp,"sha256":h(p.read_bytes()),"bytes":p.stat().st_size})
    return actual,files,cmds

def inventory(src: Path):
    out,_,r=sh(["git","ls-files","-s","-z"],src,"SOURCE_GIT_UNAVAILABLE"); rows=[]
    for rec in out.split("\0"):
        if not rec: continue
        meta,path=rec.split("\t",1); mode,oid,stage=meta.split(" ",2)
        rows.append({"path":path,"mode":mode,"git_object":oid,"stage":int(stage)})
    return sorted(rows,key=lambda x:x["path"]),r

def cargo_root(src: Path):
    p=src/"Cargo.toml"
    if not p.is_file(): return {"present":False}
    try: d=tomllib.loads(p.read_text())
    except Exception as e: raise ReconstitutionError("CARGO_MANIFEST_INVALID",str(e)) from e
    w=d.get("workspace",{}); q=d.get("package",{})
    return {"present":True,"package":{k:q.get(k) for k in ("name","version","edition","rust-version","license")},
            "workspace":{"members":sorted(w.get("members",[])),"default-members":sorted(w.get("default-members",[])),"exclude":sorted(w.get("exclude",[]))},
            "features":sorted(d.get("features",{}))}

def under(v: Any, src: Path):
    if not isinstance(v,str): return v
    try: return Path(v).resolve().relative_to(src.resolve()).as_posix()
    except Exception: return v

def cargo_meta(src: Path, cargo: str):
    out,_,r=sh([cargo,"metadata","--format-version","1","--locked","--no-deps"],src,"CARGO_METADATA_FAILED")
    try: d=json.loads(out)
    except Exception as e: raise ReconstitutionError("CARGO_METADATA_INVALID",str(e)) from e
    ps=[]
    for p in d.get("packages",[]):
        ps.append({"name":p.get("name"),"version":p.get("version"),"edition":p.get("edition"),"rust_version":p.get("rust_version"),"license":p.get("license"),
                   "manifest_path":under(p.get("manifest_path"),src),"features":sorted(p.get("features",{})),
                   "targets":sorted([{"name":t.get("name"),"kind":sorted(t.get("kind",[])),"crate_types":sorted(t.get("crate_types",[])),"src_path":under(t.get("src_path"),src)} for t in p.get("targets",[])],key=lambda x:(x["name"] or "",x["src_path"] or "")),
                   "dependencies":sorted([{"name":x.get("name"),"req":x.get("req"),"kind":x.get("kind"),"optional":bool(x.get("optional")),"features":sorted(x.get("features",[]))} for x in p.get("dependencies",[])],key=lambda x:(x["name"] or "",x["kind"] or ""))})
    return {"workspace_members":sorted(d.get("workspace_members",[])),"packages":sorted(ps,key=lambda x:(x["name"] or "",x["manifest_path"] or ""))},r

ITEM=re.compile(r"^\s*pub(?:\([^)]*\))?\s+(?:(?:async|unsafe|const)\s+)*(struct|enum|trait|fn|type|mod|static|const)\s+([A-Za-z_][A-Za-z0-9_]*)\b")
IMPL=re.compile(r"^\s*impl(?:\s*<[^>{}]*>)?\s+([A-Za-z_][A-Za-z0-9_:<> ,&'\[\]]*)\s+for\s+([A-Za-z_][A-Za-z0-9_:<> ,&'\[\]]*)\s*(?:where\b.*)?\{?\s*$")
def rust_surface(src: Path, tracked, c):
    o=c["observation"]; inc=[rel(x) for x in o.get("include_prefixes",[])]; exc=[rel(x) for x in o.get("exclude_prefixes",[])]; found=[]
    for e in tracked:
        rp=e["path"]
        if not rp.endswith(".rs") or (inc and not any(rp==x or rp.startswith(x.rstrip("/")+"/") for x in inc)) or any(rp==x or rp.startswith(x.rstrip("/")+"/") for x in exc): continue
        try: lines=(src/rp).read_text().splitlines()
        except UnicodeDecodeError: continue
        for n,line in enumerate(lines,1):
            m=ITEM.match(line)
            if m: found.append({"evidence_kind":"lexical-public-item","path":rp,"line":n,"rust_kind":m.group(1),"name":m.group(2)}); continue
            m=IMPL.match(line)
            if m: found.append({"evidence_kind":"lexical-trait-impl","path":rp,"line":n,"trait":" ".join(m.group(1).split()),"for_type":" ".join(m.group(2).split())})
    return sorted(found,key=lambda x:(x["path"],x["line"],x["evidence_kind"],x.get("name","")))

def lit(v: str): return '"'+v.replace("\\","\\\\").replace('"','\\"').replace("\n","\\n")+'"'
def graph(case: str, sha: str, items):
    b=f"urn:ggen-legacy:reconstitution:{case}:"; lines=[f"<{b}source> <urn:ggen-legacy:vocab:exactCommit> {lit(sha)} .",f"<{b}source> <urn:ggen-legacy:vocab:status> \"OBSERVED\" ."]
    for i,x in enumerate(items):
        s=f"{b}rust-item:{i:06d}"
        for k in ("evidence_kind","path","name","rust_kind","trait","for_type"):
            if k in x: lines.append(f"<{s}> <urn:ggen-legacy:vocab:{k}> {lit(str(x[k]))} .")
        lines += [f"<{s}> <urn:ggen-legacy:vocab:line> {lit(str(x['line']))} .",f"<{s}> <urn:ggen-legacy:vocab:status> \"OBSERVED\" ."]
    return "\n".join(sorted(lines))+"\n"

def write(p: Path,v): p.write_bytes(jb(v))
def manufacture(source: Path, contract_path: Path, out: Path, *, cargo_bin: str, skip_cargo_metadata: bool):
    src=source.resolve(); out.mkdir(parents=True,exist_ok=True); c=contract(contract_path)
    sha,expected,cmds=verify_source(src,c); tracked,r=inventory(src); cmds.append(r); cr=cargo_root(src)
    if skip_cargo_metadata: cm={"status":"UNSUPPORTED","reason":"cargo metadata explicitly skipped"}
    else: cm,r=cargo_meta(src,cargo_bin); cmds.append(r)
    items=rust_surface(src,tracked,c)
    capsule={"schema_version":1,"case_id":c["case_id"],"standing":"OBSERVED","source":{"repo":c["source"]["repo"],"ref":c["source"]["ref"],"exact_sha":sha,"license_expression":c["source"]["license_expression"]},"expected_files":expected,"tracked_files":tracked}
    workspace={"schema_version":1,"case_id":c["case_id"],"standing":"OBSERVED","cargo_root":cr,"cargo_metadata":cm}
    surface={"schema_version":1,"case_id":c["case_id"],"standing":"OBSERVED","claim_boundary":"lexical Rust evidence only; no semantic admission implied","items":items}
    write(out/"source-capsule.json",capsule); write(out/"workspace-observations.json",workspace); write(out/"rust-surface-observations.json",surface); (out/"observations.nt").write_text(graph(c["case_id"],sha,items))
    names=["source-capsule.json","workspace-observations.json","rust-surface-observations.json","observations.nt"]; dig={n:h((out/n).read_bytes()) for n in names}
    core={"schema_version":1,"tool":"external_reconstitution.py","tool_version":VERSION,"case_id":c["case_id"],"standing":"PARTIAL_ALIVE" if skip_cargo_metadata else "ALIVE","source":capsule["source"],"observed":{"tracked_file_count":len(tracked),"rust_surface_count":len(items),"cargo_metadata_executed":not skip_cargo_metadata},"admitted":[],"executed":cmds,"changed":names,"verified":["exact source SHA","clean tracked source tree","expected files","deterministic artifact hashing"]+([] if skip_cargo_metadata else ["cargo metadata --locked --no-deps"]),"inferred":[],"refused":[],"blocked":[],"unsupported":["cargo metadata"] if skip_cargo_metadata else [],"artifacts_sha256":dig}
    receipt={**core,"receipt_sha256":h(jb(core))}; write(out/"reconstitution-receipt.json",receipt); return receipt

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--source",required=True,type=Path); p.add_argument("--contract",required=True,type=Path); p.add_argument("--out",required=True,type=Path); p.add_argument("--cargo-bin",default="cargo"); p.add_argument("--skip-cargo-metadata",action="store_true"); a=p.parse_args(argv)
    try: r=manufacture(a.source,a.contract,a.out,cargo_bin=a.cargo_bin,skip_cargo_metadata=a.skip_cargo_metadata)
    except ReconstitutionError as e: print(json.dumps(e.to_json(),sort_keys=True),file=sys.stderr); return 2
    print(json.dumps(r,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
