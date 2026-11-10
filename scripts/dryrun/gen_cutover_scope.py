#!/usr/bin/env python3
"""T-010: cutover scope from FE call-register.json (rows) + legacy prefix census."""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _common import *
reg = json.load(open(f"{SRVE}/servengine-frontend/src/lib/xaas/__register__/call-register.json"))
rows = reg["rows"]; legacy = reg["summary"]["legacyPrefixes"]
def domain(r): return r["key"].split("::")[0]
actions, prefixes = {}, {}
for r in rows:
    d = domain(r)
    if r["kind"] == "http":
        pre = "/" + r["pathOrAction"].lstrip("/").split("/")[0]
        e = prefixes.setdefault(pre, {"prefix": pre, "legacy": pre in legacy, "domains": set(), "rows": 0, "classes": {}})
        e["domains"].add(d); e["rows"] += 1; e["classes"][r["class"]] = e["classes"].get(r["class"], 0) + 1
    else:
        e = actions.setdefault(r["pathOrAction"], {"action": r["pathOrAction"], "domains": set(), "rows": 0, "kind": r["kind"], "generatedClient": r["generatedClient"]})
        e["domains"].add(d); e["rows"] += 1
fin = lambda m: sorted(({**v, "domains": sorted(v["domains"])} for v in m.values()), key=lambda v: v.get("prefix") or v["action"])
src_prefixes = set()
for p in walk(f"{SRVE}/servengine-frontend/src/api", (".ts", ".tsx")):
    for m in re.finditer(r"""["'`](/(?:%s))\b""" % "|".join(x.strip("/") for x in legacy), open(p).read()):
        src_prefixes.add(m.group(1))
kinds = {}
for r in rows: kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
emit("cutover-scope.json", {"derivation": {"commands": [
  "python3 -c \"import json;print(len(json.load(open('src/lib/xaas/__register__/call-register.json'))['rows']))\"  (file is {summary,rows}; top-level len is 2)",
  "python3 scripts/dryrun/gen_cutover_scope.py (domain = key prefix; prefix = first path segment of http rows; legacy per summary.legacyPrefixes)"],
  "counts": {"rows": len(rows), "rows_by_kind": kinds, "generatedActionCount_summary": reg["summary"]["generatedActionCount"],
             "distinct_rpc_actions": len(actions), "distinct_http_prefixes": len(prefixes),
             "legacy_prefixes_in_register": sum(v["legacy"] for v in prefixes.values()),
             "legacy_prefixes_found_in_src_api_not_in_register": sorted(src_prefixes - set(prefixes)),
             "class_totals": reg["summary"]["countsByClass"]}},
  "rpc_actions": fin(actions), "rest_prefixes": fin(prefixes)})
print(len(rows), kinds, len(actions), len(prefixes))
