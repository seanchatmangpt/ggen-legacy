#!/usr/bin/env python3
"""T-009: onengine route inventory: every router.<verb>( registration under src/modules."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _common import *
VERB = re.compile(r"router\.(get|post|put|patch|delete)\(")
def args_of(t, i):
    d = 1; j = i; q = None
    while j < len(t) and d:
        c = t[j]
        if q:
            if c == "\\": j += 1
            elif c == q: q = None
        elif c in "\"'`": q = c
        elif c == "(": d += 1
        elif c == ")": d -= 1
        j += 1
    return t[i:j - 1]
def split_top(s):
    out = []; d = 0; cur = ""; q = None
    for c in s:
        if q:
            cur += c
            if c == q: q = None
            continue
        if c in "\"'`": q = c; cur += c; continue
        if c in "([{": d += 1
        if c in ")]}": d -= 1
        if c == "," and d == 0: out.append(cur.strip()); cur = ""
        else: cur += c
    if cur.strip(): out.append(cur.strip())
    return out
AUTH = re.compile(r"auth|permission|role|guard|jwt|token|protect|scope", re.I)
routes = []
for p in walk(f"{BE}/src/modules", ".ts"):
    t = open(p).read()
    mod = os.path.relpath(p, f"{BE}/src/modules").split(os.sep)[0]
    uses = [a.strip() for m in re.finditer(r"router\.use\(", t) for a in [args_of(t, m.end())]]
    for m in VERB.finditer(t):
        a = split_top(args_of(t, m.end()))
        path = a[0].strip("\"'`") if a else None
        mids, handler = (a[1:-1], a[-1]) if len(a) > 1 else ([], None)
        routes.append({"method": m.group(1).upper(), "path": path, "module": mod, "file": rel(p),
            "line": t[:m.start()].count("\n") + 1, "handler": handler, "middleware": mids,
            "auth_middleware": [x for x in mids + uses if AUTH.search(x)], "router_use": uses})
routes.sort(key=lambda r: (r["file"], r["line"]))
oa = f"{BE}/swagger/output/openapi.yaml"
doc = set()
if os.path.exists(oa):
    cur = None
    for l in open(oa):
        m = re.match(r"^  (/\S*):\s*$", l)
        if m: cur = m.group(1)
        m = re.match(r"^    (get|post|put|patch|delete):", l)
        if m and cur: doc.add((m.group(1).upper(), cur))
norm = lambda p: re.sub(r":(\w+)|\{\w+\}", "{}", p or "")
docn = {(m, norm(p)) for m, p in doc}
for r in routes: r["documented_by_name_only"] = any(m == r["method"] and p.endswith(norm(r["path"])) and r["path"] not in ("/", "") for m, p in docn)
emit("route-inventory.json", {"derivation": {"commands": [
  "cd ~/srve/onengine-backend && grep -rEo 'router\\.(get|post|put|patch|delete)\\(' src/modules | wc -l",
  "python3 scripts/dryrun/gen_route_inventory.py (paren-balanced parse; module = first dir under src/modules; mount prefix not derivable: app.ts absent from archive)",
  "openapi reconcile: swagger/output/openapi.yaml %s" % ("present" if doc else "ABSENT from archive (undocumented flag = UNVERIFIED)")],
  "counts": {"routes": len(routes), "modules": len({r['module'] for r in routes}), "openapi_verbs": len(doc),
             "by_method": {m: sum(r['method'] == m for r in routes) for m in ("GET","POST","PUT","PATCH","DELETE")},
             "with_auth_middleware": sum(bool(r["auth_middleware"]) for r in routes)}}, "routes": routes})
print(len(routes), len(doc))
