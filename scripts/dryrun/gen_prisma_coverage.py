#!/usr/bin/env python3
"""T-013: classify Prisma models against canonical.ttl classes; tenant-keyed vs global policy."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _common import *
sch = open(f"{BE}/prisma/schema.prisma").read().split("\n")
models = {}; cur = None
for n, l in enumerate(sch, 1):
    m = re.match(r"^model (\w+) \{", l)
    if m: cur = m.group(1); models[cur] = {"line": n, "tenant": False, "map": None}; continue
    if cur and l.startswith("}"): models[cur]["end"] = n; cur = None
    elif cur:
        if re.match(r"^\s+tenantId\s", l): models[cur]["tenant"] = True
        mm = re.search(r'@@map\("([^"]+)"\)', l)
        if mm: models[cur]["map"] = mm.group(1)
ttl = open(f"{SRVE}/ontology/canonical.ttl").read()
classes = {}
for m in re.finditer(r"^one:(\w+) a owl:Class ;(.*?)\.\s*$", ttl, re.S | re.M):
    name, body = m.groups()
    if "one:Aggregate" in name or "inAggregate" not in body: continue
    c = re.search(r'rdfs:comment "([^"]*)"', body); c = c.group(1) if c else ""
    sub = re.search(r"Subsumes ([^(]*)(?:\(([^)]*)\))?", c)
    named = set(re.findall(r"[A-Z]\w+", sub.group(1))) if sub else set()
    rng = [(int(a), int(b)) for a, b in re.findall(r"(\d{2,5})-(\d{2,5})", sub.group(2) or "")] if sub else []
    ag = re.search(r"inAggregate one:(\w+)", body)
    classes[name] = {"named": named, "ranges": rng, "aggregate": ag.group(1) if ag else None}
GLOBAL = {"Provider": "suppliers global after migration 20260715173000_procurement_suppliers_global"}
mig = os.path.isdir(f"{BE}/prisma/migrations/20260715173000_procurement_suppliers_global")
out = []
for name, m in models.items():
    hit = next((c for c, v in classes.items() if name in v["named"]), None); how = "named"
    if not hit:
        hit = next((c for c, v in classes.items() if any(a <= m["line"] <= b for a, b in v["ranges"])), None); how = "line-range"
    if hit: cls, basis = "canonical", {"class": hit, "by": how}
    elif re.search(r"legacy|deprecated|backup|_old$|_bak$|temp", name + (m["map"] or ""), re.I): cls, basis = "legacy", None
    elif m["tenant"]: cls, basis = "tenant-only", None
    else: cls, basis = "unmapped", None
    out.append({"model": name, "line": m["line"], "table": m["map"], "has_tenantId": m["tenant"], "classification": cls, "basis": basis})
pol = {}
for c, v in sorted(classes.items()):
    ms = [o for o in out if o["basis"] and o["basis"]["class"] == c]
    t = sum(o["has_tenantId"] for o in ms)
    pol[c] = {"aggregate": v["aggregate"], "backing_models": len(ms), "models_with_tenantId": t,
              "policy": "global" if c in GLOBAL else ("tenant-keyed" if ms and t * 2 >= len(ms) else ("tenant-keyed(unbacked)" if not ms else "global")),
              "note": GLOBAL.get(c)}
tot = {k: sum(o["classification"] == k for o in out) for k in ("canonical", "tenant-only", "legacy", "unmapped")}
emit("prisma-coverage.json", {"derivation": {"commands": [
  "cd ~/srve/onengine-backend && grep -c '^model ' prisma/schema.prisma",
  "python3 scripts/dryrun/gen_prisma_coverage.py (model->class: named in canonical.ttl 'Subsumes' comment, else inside its schema.prisma:A-B range; else legacy-name / tenantId / unmapped)"],
  "counts": {"models": len(out), "by_classification": tot, "canonical_classes": len(classes),
             "classes_without_backing_model": sorted(c for c, p in pol.items() if p["backing_models"] == 0),
             "global_supplier_migration_present": mig}},
  "models": out, "tenant_policy": pol})
print(len(out), tot, len(classes))
