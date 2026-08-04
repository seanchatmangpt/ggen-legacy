#!/usr/bin/env python3
from __future__ import annotations
import filecmp,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SCRIPT=ROOT/'scripts/autonomic_finish.py'; FIXTURE=ROOT/'fixtures/autonomic/conversation.json'
def run(inp,out): return subprocess.run([sys.executable,str(SCRIPT),'--input',str(inp),'--output',str(out)],text=True,capture_output=True)
def cmp(a,b):
 d=filecmp.dircmp(a,b); assert not(d.left_only or d.right_only or d.funny_files)
 for f in d.common_files: assert (a/f).read_bytes()==(b/f).read_bytes(),f
 for x in d.common_dirs: cmp(a/x,b/x)
def case(root,p,n): q=root/f'{n}.json';q.write_text(json.dumps(p,ensure_ascii=False));return q
def main():
 with tempfile.TemporaryDirectory() as t:
  t=Path(t);a=t/'a';b=t/'b';ra=run(FIXTURE,a);rb=run(FIXTURE,b);assert ra.returncode==rb.returncode==0,(ra.stderr,rb.stderr);cmp(a,b)
  r=json.loads((a/'RECEIPT.json').read_text());assert r['standing']=='ALIVE' and r['gap_count']==0
  required=['.claude/settings.json','.claude/hooks/protocol_andon.py','.claude/agents/strategist.md','.claude/skills/close-capability/SKILL.md','production/KANBAN.json','genesis/NAMING.json','schemas/admitted-decision.schema.json','ppddl/domain.pddl','ppddl/problem.pddl']
  for p in required: assert (a/p).exists(),p
  base=json.loads(FIXTURE.read_text())
  muts=[]
  x=json.loads(json.dumps(base));x['concepts'].append(dict(x['concepts'][0]));muts.append((x,'DUPLICATE_CONCEPT'))
  x=json.loads(json.dumps(base));x['concepts'][0]['standing']='DONE';muts.append((x,'UNKNOWN_STANDING'))
  x=json.loads(json.dumps(base));x['projections']=['execute'];muts.append((x,'UNKNOWN_PROJECTION'))
  x=json.loads(json.dumps(base));x['system']['production_lane']['wip_limit']=2;muts.append((x,'WIP_LIMIT_NOT_ONE'))
  x=json.loads(json.dumps(base));x['system']['naming']['pairs'][1]['token']=x['system']['naming']['pairs'][0]['token'];muts.append((x,'INVALID_CLI_TOKEN'))
  x=json.loads(json.dumps(base));del x['concepts'][0]['decision']['acceptance'];muts.append((x,'DECISION_MISSING_ACCEPTANCE'))
  for i,(p,needle) in enumerate(muts):
   z=run(case(t,p,str(i)),t/f'm{i}');assert z.returncode==2 and needle in z.stderr,(needle,z.stderr)
 print('GL_AUTO_001_CROWN_ALIVE');return 0
if __name__=='__main__':raise SystemExit(main())
