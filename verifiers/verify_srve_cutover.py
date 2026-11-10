#!/usr/bin/env python3
"""Independent verifier for the srve cutover identity law (T-029).

Judges *recorded* request/response fixtures; it never calls the producer's
scripts. Law re-derived here, not imported: a backend is admitted iff
GET /health == 200 AND unauthenticated GET /api/health == 401 whose body
contains "missing or invalid Bearer token".

Positive witnesses must be admitted; negative controls (stub serving
/api/health 200, dead /health, wrong 401 body, 403 instead of 401) must be
refused. A verifier that cannot refuse is vacuous -> exit 1.

Usage: verify_srve_cutover.py [--fixture FILE] [--producer PATH]
  FILE: JSON {"producer_id": str, "records": [{"name","kind":"positive|negative",
        "responses": {"/health": [status, body], "/api/health": [status, body]}}]}
  --producer: path of the producing script; refused if its sha256 equals this file's
        or if fixture producer_id == this verifier's id.
Exit: 0 all witnesses admitted and all controls refused; 1 verdict failure;
      2 producer==verifier refusal.
"""
import argparse, hashlib, json, sys

VERIFIER_ID = "verify_srve_cutover.py"
BEARER = "missing or invalid Bearer token"

BUILTIN = {
    "producer_id": "srve/scripts/dryrun/two_probe.sh",
    "records": [
        {"name": "xaas-shaped", "kind": "positive", "responses": {
            "/health": [200, "ok"], "/api/health": [401, '{"error":"missing or invalid Bearer token"}']}},
        {"name": "candidate-shaped", "kind": "positive", "responses": {
            "/health": [200, '{"status":"up"}'],
            "/api/health": [401, "Unauthorized: missing or invalid Bearer token."]}},
        {"name": "stub-api-health-200", "kind": "negative", "responses": {
            "/health": [200, "ok"], "/api/health": [200, '{"ok":true}']}},
        {"name": "dead-health", "kind": "negative", "responses": {
            "/health": [0, ""], "/api/health": [401, BEARER]}},
        {"name": "wrong-401-body", "kind": "negative", "responses": {
            "/health": [200, "ok"], "/api/health": [401, "nope"]}},
        {"name": "403-not-401", "kind": "negative", "responses": {
            "/health": [200, "ok"], "/api/health": [403, BEARER]}},
        {"name": "spa-fallback", "kind": "negative", "responses": {
            "/health": [200, "<html>"], "/api/health": [200, "<html>"]}},
    ],
}


def admitted(resp):
    h = resp.get("/health", [0, ""])
    a = resp.get("/api/health", [0, ""])
    return h[0] == 200 and a[0] == 401 and BEARER in a[1]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture")
    ap.add_argument("--producer")
    ns = ap.parse_args(argv)
    fx = json.load(open(ns.fixture)) if ns.fixture else BUILTIN

    if fx.get("producer_id") == VERIFIER_ID or (ns.producer and sha(ns.producer) == sha(__file__)):
        print("REFUSED(producer==verifier): independence violated", file=sys.stderr)
        return 2

    bad = []
    pos = neg = 0
    for r in fx["records"]:
        ok = admitted(r["responses"])
        if r["kind"] == "positive":
            pos += 1
            if not ok: bad.append(f"positive witness refused: {r['name']}")
        else:
            neg += 1
            if ok: bad.append(f"negative control admitted: {r['name']}")
    if pos == 0 or neg == 0:
        bad.append(f"vacuous fixture: {pos} positives, {neg} negatives")
    for b in bad: print("FAIL:", b, file=sys.stderr)
    if bad: return 1
    print(f"VERIFIED: {pos} positive witnesses admitted, {neg} negative controls refused")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
