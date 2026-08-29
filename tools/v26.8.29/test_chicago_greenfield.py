#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("chicago_greenfield",HERE/"chicago_greenfield.py"); assert spec and spec.loader
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
SUBJECT="0123456789abcdef0123456789abcdef01234567"
def scenario():
 return {"schema":m.SCHEMA,"scenario_id":"fortune5-p2p-chicago-001","immutable_subject":True,"provenance":{"ggen_ecosystem":m.GGEN_ECOSYSTEM_SHA,"autofde_lab":m.AUTOFDE_LAB_SHA,"gymact":m.GYMACT_SHA},"capabilities":list(m.REQUIRED_CAPABILITIES),"strategies":list(m.REQUIRED_STRATEGIES),"failure_injections":list(m.REQUIRED_FAILURES),"owners":{c:f"owner:{n:02d}" for n,c in enumerate(m.REQUIRED_CAPABILITIES,1)},"architecture":{"linux_arm64":True,"linux_amd64":False}}
class GreenfieldChicagoTest(unittest.TestCase):
 def test_full_chain_deterministic_replayable(self):
  s=scenario(); a=m.execute(s,SUBJECT); b=m.execute(s,SUBJECT)
  self.assertEqual(a["artifact_sha256"],b["artifact_sha256"]); self.assertEqual(a["receipt"],b["receipt"]); self.assertEqual(a["option_count"],15); self.assertEqual(a["selected"]["strategy"],"canary"); self.assertEqual(a["planner_portfolio"]["selected"],"deterministic-dfcm"); self.assertEqual(a["receipt"]["authority"],"BRCE"); self.assertFalse(a["receipt"]["external_actuation"]); self.assertEqual(m.replay(s,SUBJECT,a["receipt"])["replay"],"MATCHED"); self.assertEqual(set(a["artifact"]["capabilities"]),set(m.REQUIRED_CAPABILITIES))
 def test_ppddl_has_business_and_failure_closure(self):
  r=m.execute(scenario(),SUBJECT)
  for x in (*m.REQUIRED_CAPABILITIES,*m.REQUIRED_FAILURES): self.assertIn(x,r["ppddl"])
 def test_refuses_stale_sha(self):
  s=scenario(); s["provenance"]["gymact"]="f"*40
  with self.assertRaisesRegex(m.Refusal,r"REFUSED\[STALE_SHA\]"): m.execute(s,SUBJECT)
 def test_refuses_mutable_identity(self):
  s=scenario(); s["immutable_subject"]=False
  with self.assertRaisesRegex(m.Refusal,r"REFUSED\[MUTABLE_IDENTITY\]"): m.execute(s,SUBJECT)
 def test_refuses_malformed_admission(self):
  s=scenario(); s["schema"]="wrong"
  with self.assertRaisesRegex(m.Refusal,r"REFUSED\[MALFORMED_ADMISSION\]"): m.execute(s,SUBJECT)
 def test_refuses_ownership_collision(self):
  s=scenario(); s["owners"]["payment"]=s["owners"]["invoice"]
  with self.assertRaisesRegex(m.Refusal,r"REFUSED\[OWNERSHIP_COLLISION\]"): m.execute(s,SUBJECT)
 def test_refuses_unauthorized_do(self):
  with self.assertRaisesRegex(m.Refusal,r"REFUSED\[UNAUTHORIZED_DO\]"): m.execute(scenario(),SUBJECT,authorized=False)
 def test_refuses_unbound_and_tampered_receipts(self):
  r=m.execute(scenario(),SUBJECT); artifact=m.canonical(r["artifact"]); bad=copy.deepcopy(r["receipt"]); bad["intent_sha256"]="0"*64
  with self.assertRaisesRegex(m.Refusal,r"REFUSED\[UNBOUND_RECEIPT\]"): m.verify_receipt(bad,r["intent"],artifact)
  bad=copy.deepcopy(r["receipt"]); bad["standing"]="UNKNOWN"
  with self.assertRaisesRegex(m.Refusal,r"REFUSED\[RECEIPT_TAMPER\]"): m.verify_receipt(bad,r["intent"],artifact)
 def test_amd64_is_explicitly_unsupported(self):
  r=m.execute(scenario(),SUBJECT)
  with self.assertRaisesRegex(m.Refusal,r"UNSUPPORTED\[ECOSYSTEM_CONTAINER_AMD64\]"): m.platform_support(r["admitted"],"linux/amd64")
if __name__=="__main__": unittest.main()
