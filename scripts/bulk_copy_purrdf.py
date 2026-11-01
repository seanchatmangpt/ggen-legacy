#!/usr/bin/env python3
"""80/20 Phase-1 bulk copy: git-archive remaining purrdf crates into stardf/arrow/crates/ as stardf-*.
One package. Package-name + dep renames in Cargo.toml only; everything else verbatim.
Excluded from workspace members (copied to disk, registered): binary/tooling/bindings crates.
"""
import subprocess, shutil, sys, os
from pathlib import Path

REV = "0da0578306983da851a9073337d57e2e2c41ab3a"
PURRDF = Path("/Users/sac/purrdf")
DEST_ROOT = Path("/Users/sac/ggen-legacy/stardf/arrow/crates")
TMP = Path("/tmp/stardf-bulk-copy")

COPY = ["arrow", "bench", "cli", "duckdb", "entail", "envelope-probe", "geo", "geo-kernel",
        "glob", "gts", "hash-conformance", "helper-census", "hnsw", "hooks", "json",
        "markdown", "mime", "process", "purrdf", "rdf", "rdf-capi", "rdf-events", "rdf-wasm",
        "retrieval", "shex", "sparql-conformance", "sparql-eval", "sparql-results", "sql",
        "text", "toml", "validate", "wasm-link"]
NO_MEMBER = {"cli", "rdf-capi", "rdf-wasm", "wasm-link", "bench", "helper-census",
             "envelope-probe", "hash-conformance"}

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def main():
    copied, failed, skipped = [], [], []
    for c in COPY:
        dest = DEST_ROOT / f"stardf-{c}"
        if dest.exists():
            skipped.append(c)
            continue
        if TMP.exists():
            shutil.rmtree(TMP)
        TMP.mkdir(parents=True)
        # git archive writes a binary tar to stdout — never text mode
        p1 = subprocess.run(["git", "-C", str(PURRDF), "archive", REV, f"crates/{c}"],
                            capture_output=True)
        if p1.returncode != 0:
            failed.append((c, "archive2", p1.stderr.decode()[:120]))
            continue
        p2 = subprocess.run(["tar", "-x", "-C", str(TMP)], input=p1.stdout)
        if p2.returncode != 0:
            failed.append((c, "tar", ""))
            continue
        src = TMP / "crates" / c
        if not src.is_dir():
            failed.append((c, "no-src", ""))
            continue
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest, dirs_exist_ok=True)
        # rename package + deps in Cargo.toml (the only file we touch)
        cm = dest / "Cargo.toml"
        if cm.is_file():
            text = cm.read_text()
            text = text.replace('name = "purrdf-', 'name = "stardf-')
            text = text.replace('name = "purdff-', 'name = "stardf-')
            text = text.replace("purrdf-", "stardf-").replace("purdff-", "stardf-")
            cm.write_text(text)
        copied.append(c)
    if TMP.exists():
        shutil.rmtree(TMP, ignore_errors=True)
    members = [f"stardf-{c}" for c in copied if c not in NO_MEMBER]
    print("COPIED:", len(copied), copied)
    print("SKIPPED(already-present):", len(skipped), skipped)
    print("FAILED:", failed if failed else "none")
    print("MEMBER_CRATES:", members)

if __name__ == "__main__":
    main()
