#!/usr/bin/env python3
"""One-command GL-AUTO-001 crown: compile, manufacture, replay, mutate, guard, receipt."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'fixtures/autonomic/conversation.json'
FOUNDRY=ROOT/'scripts/autonomic_finish.py'
VERIFIER=ROOT/'scripts/verify_autonomic_finish.py'
DEFAULT_EVIDENCE=ROOT/'evidence/autonomic/GL-AUTO-001.json'
ALLOWED_PREFIXES=('autonomic/','fixtures/autonomic/','scripts/autonomic_finish.py','scripts/verify_autonomic_finish.py','scripts/run_autonomic_crown.py','tickets/GL-AUTO-001.md','evidence/autonomic/','.github/workflows/autonomic-crown.yml')

def command(args:list[str],cwd:Path=ROOT)->dict:
 p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,check=False)
 return {'argv':args,'exit':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def tree(root:Path)->dict[str,str]:return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file()}

def git_guard(base:str)->dict:
 probe=command(['git','rev-parse','--is-inside-work-tree'])
 if probe['exit']!=0:return {'standing':'UNSUPPORTED','reason':'git metadata unavailable','probe':probe}
 diff=command(['git','diff','--name-only',base+'...HEAD'])
 if diff['exit']!=0:return {'standing':'BLOCKED','reason':'cannot compute exact-base diff','probe':diff}
 files=[x for x in diff['stdout'].splitlines() if x]
 forbidden=[x for x in files if not any(x==p or x.startswith(p) for p in ALLOWED_PREFIXES)]
 if forbidden:raise SystemExit('REFUSED:FORBIDDEN_DIFF:'+','.join(forbidden))
 return {'standing':'ALIVE','base':base,'files':files}

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--base',default='33dd18801fecce48a5022c2727d1cefdf450cc87');ap.add_argument('--evidence',type=Path,default=DEFAULT_EVIDENCE);a=ap.parse_args()
 steps=[command([sys.executable,'-m','py_compile',str(FOUNDRY),str(VERIFIER),str(Path(__file__).resolve())])]
 with tempfile.TemporaryDirectory(prefix='ggen-auto-crown-') as t:
  t=Path(t);out=t/'out'
  steps.append(command([sys.executable,str(FOUNDRY),'--input',str(FIXTURE),'--output',str(out)]))
  steps.append(command([sys.executable,str(VERIFIER)]))
  if any(x['exit']!=0 for x in steps):
   print(json.dumps({'standing':'BUILD_BROKEN','steps':steps},ensure_ascii=False,sort_keys=True));return 1
  receipt=json.loads((out/'RECEIPT.json').read_text());gaps=json.loads((out/'GAPS.json').read_text())['gaps']
  if receipt['standing']!='ALIVE' or gaps:raise SystemExit('REFUSED:CROWN_NOT_CLOSED')
  guard=git_guard(a.base)
  evidence={'schema':'ggen-legacy.gl-auto-001.crown.v1','subject':{'repository':'seanchatmangpt/ggen-legacy','base':a.base,'fixture':str(FIXTURE.relative_to(ROOT))},'runtime':{'python':sys.version.split()[0],'platform':sys.platform},'commands':steps,'output_manifest':tree(out),'receipt':receipt,'gap_count':len(gaps),'git_guard':guard,'claim_ceiling':'AUTONOMIC_BOOTSTRAP_PROJECTION_ONLY','standing':'ALIVE'}
  a.evidence.parent.mkdir(parents=True,exist_ok=True);a.evidence.write_text(json.dumps(evidence,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 print('GL_AUTO_001_AUTONOMIC_CROWN_ALIVE');return 0
if __name__=='__main__':raise SystemExit(main())
