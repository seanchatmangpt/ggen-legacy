#!/usr/bin/env python3
"""
scripts/extract_stardf_arrow.py
Deterministic extractor compiling the AS-BUILT stardf/arrow C ABI surface into
authority/stardf/stardf-contract.json.

Ground truth inputs (generation over hand-editing):
  - stardf/arrow/crates/stardf-arrow-capi/src/*.rs   ([no_mangle] export scan)
  - stardf/arrow/crates/stardf-arrow-capi/include/stardf_arrow.h  (C signatures)
Cross-check: the Rust export set MUST equal the header export set; any drift
is a loud failure, never silently admitted.

Output:
  - authority/stardf/stardf-contract.json

The purrdf legacy projection (128 predecessor rows) is carried over verbatim
from the previous contract generation under `legacy_projection` so the
predecessor census survives the regeneration.
"""

import os
import re
import sys
import json
import hashlib
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPI_SRC = os.path.join(REPO, "stardf/arrow/crates/stardf-arrow-capi/src")
CAPI_HEADER = os.path.join(REPO, "stardf/arrow/crates/stardf-arrow-capi/include/stardf_arrow.h")
CONTRACT = os.path.join(REPO, "authority/stardf/stardf-contract.json")

RELEASE = "v26.10.31"
SCHEMA = f"urn:chatman:ggen-legacy:stardf-contract:{RELEASE}"

# Rust surface: #[no_mangle] fn name(args) -> ret
RUST_FN_RE = re.compile(
    r'#\[no_mangle\]\s*(?:pub\s+)?(?:unsafe\s+)?extern\s+"C"\s+fn\s+'
    r'(stardf_[a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*(?:->\s*([^{;]+?))?\s*\{',
    re.DOTALL,
)

# C surface: signature lines in the header ending in `name(...);`
C_FN_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_ \t\*]*[\s\*])(stardf_[a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*;', re.DOTALL)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def rust_exports():
    """Scan all capi .rs sources for #[no_mangle] extern "C" stardf_* fns."""
    out = {}
    for fname in sorted(os.listdir(CAPI_SRC)):
        if not fname.endswith(".rs"):
            continue
        text = open(os.path.join(CAPI_SRC, fname), encoding="utf-8").read()
        for m in RUST_FN_RE.finditer(text):
            name, args, ret = m.group(1), m.group(2), m.group(3)
            params = []
            for i, a in enumerate([a.strip() for a in args.split(",") if a.strip()]):
                parts = a.split()
                pname = parts[-1].lstrip("*&")
                ptype = " ".join(parts[:-1])
                params.append({"index": i, "name": pname, "type": ptype})
            out[name] = {
                "source_file": f"stardf/arrow/crates/stardf-arrow-capi/src/{fname}",
                "return_type": " ".join((ret or "()").split()),
                "parameters": params,
            }
    return out


def c_exports():
    """Scan stardf_arrow.h for stardf_* function declarations."""
    text = open(CAPI_HEADER, encoding="utf-8").read()
    code = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    code = re.sub(r'//.*', '', code)
    out = {}
    for m in C_FN_RE.finditer(code):
        ret, name, args = m.group(1).strip(), m.group(2), m.group(3)
        out[name] = {"return_type": " ".join(ret.split())}
    return out


def classify_subsystem(name):
    if "version" in name:
        return "Version"
    elif "arena" in name:
        return "Arena"
    elif "batch" in name and "export" not in name:
        return "Batch"
    elif "export" in name or "stream" in name:
        return "Arrow"
    elif "error" in name:
        return "Error"
    elif "release" in name or "pending" in name:
        return "Lifecycle"
    else:
        return "General"


def classify_substrate(name, subsystem):
    if "stream" in name or "array" in name or "batch" in name or "export" in name or "i32" in name:
        return "avec"
    elif subsystem in ("Batch", "Arrow"):
        batch = "batch" in name or "export" in name
        return "avec" if batch else "stardf-kernel"
    else:
        return "strd-kernel-placeholder" if False else "stardf-kernel"


def main():
    rust = rust_exports()
    c = c_exports()

    if len(rust) == 0:
        print("[FAIL] Vacuous census: 0 #[no_mangle] stardf_* exports found in capi src.", file=sys.stderr)
        sys.exit(1)
    if len(c) == 0:
        print(f"[FAIL] Vacuous census: 0 stardf_* declarations found in {CAPI_HEADER}.", file=sys.stderr)
        sys.exit(1)

    missing_in_c = sorted(set(rust) - set(c))
    missing_in_rust = sorted(set(c) - set(rust))
    if missing_in_c:
        print(f"[FAIL] Rust exports missing from stardf_arrow.h: {missing_in_c}", file=sys.stderr)
        sys.exit(1)
    if missing_in_rust:
        print(f"[FAIL] Header declarations missing from Rust #[no_mangle]: {missing_in_rust}", file=sys.stderr)
        sys.exit(1)

    print(f"[PASS] Rust/header census match: {len(rust)} stardf_* exports agree across src and header.")

    # Carried-over predecessor projection (read from prior generation, never
    # hand-written here).
    with open(CONTRACT, encoding="utf-8") as f:
        prior = json.load(f)
    legacy = prior.get("legacy_projection") or {
        "source": "purrdf.h",
        "predecessor": "purrdf",
        "functions_count": prior.get("functions_count"),
        "functions": prior.get("functions"),
    }

    src_digest = sha256_file(CAPI_HEADER)
    fn_rows = []
    for name in sorted(rust):
        info = rust[name]
        subsys = classify_subsystem(name)
        fn_rows.append({
            "target_symbol": name,
            "predecessor_symbol": "none",
            "return_type": c[name]["return_type"],
            "subsystem": subsys,
            "downstream_substrate": classify_substrate(name, subsys),
            "source_file": info["source_file"],
            "parameters": info["parameters"],
        })

    contract = {
        "schema": SCHEMA,
        "release": RELEASE,
        "standing": "PARTIAL_ALIVE",
        "equation": "A = mu(O*)",
        "generated_from": {
            "capi_src": "stardf/arrow/crates/stardf-arrow-capi/src",
            "capi_header": "stardf/arrow/crates/stardf-arrow-capi/include/stardf_arrow.h",
            "header_sha256": src_digest,
            "extractor": "scripts/extract_stardf_arrow.py",
        },
        "contract": prior.get("contract"),
        "invariants": prior.get("invariants"),
        "functions_count": len(fn_rows),
        "functions": fn_rows,
        "legacy_projection": legacy,
    }

    with open(CONTRACT, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=1)
        f.write("\n")
    print(f"Wrote {CONTRACT} ({len(fn_rows)} as-built functions, "
          f"{legacy['functions_count']} carried-over legacy projection rows).")


if __name__ == "__main__":
    main()
