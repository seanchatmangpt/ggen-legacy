#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("protocol_extinction",HERE/"protocol_extinction.py"); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
class ExtinctionCourtTest(unittest.TestCase):
  def test_absent_original_replacement_survives_exact_vectors(self):
    with tempfile.TemporaryDirectory() as td:
      root=Path(td); original=root/"original.py"; replacement=root/"replacement.py"; vectors=root/"vectors.json"
      replacement.write_text('import json,sys\nr=json.load(sys.stdin)\nout={"disposition":"ADMITTED","code":"ALLOWED"} if r.get("authority")=="exact" and r.get("receipt_capable") is True else {"disposition":"REFUSED","code":"REFUSED:AUTHORITY_OR_RECEIPT"}\nprint(json.dumps(out,sort_keys=True,separators=(",",":")))\n')
      vectors.write_text(json.dumps([{"id":"yes","request":{"authority":"exact","receipt_capable":True},"expect":{"disposition":"ADMITTED","code":"ALLOWED"}},{"id":"no","request":{"authority":None,"receipt_capable":True},"expect":{"disposition":"REFUSED","code":"REFUSED:AUTHORITY_OR_RECEIPT"}}]))
      self.assertFalse(original.exists()); report=mod.court(vectors,[sys.executable,str(replacement)],original)
      self.assertEqual(report["standing"],"PARTIAL_ALIVE"); self.assertTrue(report["original_absent"]); self.assertEqual(report["failures"],[])
  def test_original_presence_refuses_extinction_claim(self):
    with tempfile.TemporaryDirectory() as td:
      root=Path(td); original=root/"original.py"; original.write_text("x=1\n"); vectors=root/"vectors.json"; vectors.write_text("[]")
      self.assertEqual(mod.court(vectors,[sys.executable,"-c","pass"],original)["standing"],"REFUSED:ORIGINAL_STILL_PRESENT")
if __name__=="__main__": unittest.main()
