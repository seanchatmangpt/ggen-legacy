#!/usr/bin/env python3
"""T-008: classify xaas serv_engine AshPostgres resources + actions (generated vs custom-handler residue)."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _common import *
KINDS = ("create", "update", "read", "destroy", "action")
HDR = re.compile(r"^(\s*)(create|update|read|destroy|action)\(?\s*:([a-z_0-9?!]+)")
CUSTOM = re.compile(r"^\s*(change|validate|manual|run|prepare)\b\(?\s*(\{?\s*[A-Z][\w.]*|__MODULE__|fn\b|&)")
def parse(path):
    lines = open(path).read().split("\n"); out = []; i = 0
    in_actions = False; aind = 0
    while i < len(lines):
        l = lines[i]
        m = re.match(r"^(\s*)actions do\s*$", l)
        if m: in_actions, aind = True, len(m.group(1)); i += 1; continue
        if in_actions and l.strip() == "end" and len(l) - len(l.lstrip()) == aind: in_actions = False
        h = HDR.match(l) if in_actions else None
        if h and len(h.group(1)) == aind + 2:
            ind = len(h.group(1)); body = [l]; j = i + 1
            if re.search(r"\bdo\s*$", l):
                while j < len(lines) and not (lines[j].strip() == "end" and len(lines[j]) - len(lines[j].lstrip()) == ind):
                    body.append(lines[j]); j += 1
            cust = [b.strip() for b in body if CUSTOM.match(b)]
            out.append({"kind": h.group(2), "name": h.group(3), "line": i + 1,
                        "tag": "custom-handler" if cust else "generated", "custom_refs": cust})
            i = j
        i += 1
    return out
res = []
for p in walk(f"{XAAS}/lib/xaas/serv_engine", ".ex"):
    t = open(p).read()
    if "data_layer: AshPostgres" not in t: continue
    tb = re.search(r'table\(?\s*"([^"]+)"', t)
    acts = parse(p)
    res.append({"file": rel(p), "table": tb.group(1) if tb else None,
                "resource_tag": "custom-handler" if any(a["tag"] == "custom-handler" for a in acts) else "generated",
                "actions": acts})
totals = {k: sum(1 for r in res for a in r["actions"] if a["kind"] == k) for k in KINDS}
tags = {t: sum(1 for r in res for a in r["actions"] if a["tag"] == t) for t in ("generated", "custom-handler")}
emit("resource-classification.json", {
 "derivation": {"commands": [
   "cd ~/xaas && grep -rl 'data_layer: AshPostgres' lib/xaas/serv_engine | wc -l",
   "python3 scripts/dryrun/gen_resource_classification.py  (parses 'actions do' blocks; action tagged custom-handler iff body has change/validate/manual/run/prepare naming a module, fn or capture)",
   "cross-check: grep -rhE '^\\s+(create|update|read|destroy|action)[ (]' lib/xaas/serv_engine"],
   "counts": {"resources": len(res), "actions_by_kind": totals, "actions_total": sum(totals.values()), "by_tag": tags,
              "resources_tag_generated": sum(r["resource_tag"] == "generated" for r in res)}},
 "resources": res})
print(len(res), totals, tags)
