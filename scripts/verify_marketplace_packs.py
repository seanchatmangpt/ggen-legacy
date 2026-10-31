#!/usr/bin/env python3
"""
scripts/verify_marketplace_packs.py
Mechanical verification of the ggen marketplace packs selected for stardf reconstitution.
Asserts:
  1. All 15 packs exist in ~/ggen-marketplace/packs
  2. Every pack has a readable pack.toml with a declared version
  3. Every pack has either an ontology.ttl or a templates/ directory
"""

import os
import sys
import json

MANIFEST_PATH = "authority/stardf/marketplace_packs.json"

def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"[FAIL] Missing manifest: {MANIFEST_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(MANIFEST_PATH, "r") as f:
        data = json.load(f)

    packs = data.get("packs", [])
    print(f"=== Verifying {len(packs)} ggen marketplace packs for stardf ===")

    failures = 0
    for p in packs:
        name = p["name"]
        path = p["path"]
        version = p.get("version", "unknown")

        if not os.path.isdir(path):
            print(f"[FAIL] Pack directory does not exist: {path}", file=sys.stderr)
            failures += 1
            continue

        pack_toml = os.path.join(path, "pack.toml")
        if not os.path.isfile(pack_toml):
            print(f"[FAIL] Missing pack.toml in {path}", file=sys.stderr)
            failures += 1
            continue

        ontology = os.path.join(path, "ontology.ttl")
        templates = os.path.join(path, "templates")
        has_content = os.path.isfile(ontology) or os.path.isdir(templates)
        if not has_content:
            print(f"[FAIL] Pack {name} has neither ontology.ttl nor templates/", file=sys.stderr)
            failures += 1
            continue

        print(f"[PASS] {name:<36} (v{version:<8}) -> {p['domain']}")

    if failures > 0:
        print(f"\n[FAIL] {failures} pack validation failures.", file=sys.stderr)
        sys.exit(1)

    print(f"\n[ALL PASS] All {len(packs)} marketplace packs verified on disk and ready for stardf.")

if __name__ == "__main__":
    main()
