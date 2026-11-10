"""Shared helpers for v26.11.9 manifest generators (deterministic, read-only on sources).

GGEN_SRC_HOME  root holding xaas/ and srve/ source trees (default: ~). Point it at an exact-SHA
               `git archive` extraction (with SOURCE_SHAS.json) for reproducible manifests.
GGEN_LEGACY_OUT  manifest output dir (default: this repo's docs/jira/v26.11.9/manifests).
"""
import json, os, re, sys
from pathlib import Path

HOME = os.environ.get("GGEN_SRC_HOME", str(Path.home()))
XAAS = f"{HOME}/xaas"; SRVE = f"{HOME}/srve"; BE = f"{SRVE}/onengine-backend"
MAN = os.environ.get(
    "GGEN_LEGACY_OUT",
    str(Path(__file__).resolve().parents[2] / "docs/jira/v26.11.9/manifests"))


def source_shas():
    """Exact source identity: SOURCE_SHAS.json if present, else git HEAD per tree, else UNKNOWN."""
    f = Path(HOME) / "SOURCE_SHAS.json"
    if f.is_file():
        return json.loads(f.read_text())
    import subprocess
    out = {}
    for name, path in (("xaas", XAAS), ("srve", SRVE), ("srve/onengine-backend", BE),
                       ("srve/servengine-frontend", f"{SRVE}/servengine-frontend")):
        try:
            out[name] = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True,
                                       text=True, timeout=30, check=False).stdout.strip() or "UNKNOWN"
        except (OSError, subprocess.SubprocessError):
            out[name] = "UNKNOWN"
    return out


def walk(root, exts):
    for d, ds, fs in os.walk(root):
        ds.sort()
        for f in sorted(fs):
            if f.endswith(exts): yield os.path.join(d, f)


def rel(p): return os.path.relpath(p, HOME)


def emit(name, doc):
    os.makedirs(MAN, exist_ok=True)
    doc.setdefault("source_shas", source_shas())
    with open(f"{MAN}/{name}", "w") as f: json.dump(doc, f, indent=2, sort_keys=True); f.write("\n")
    print(f"wrote {name}")
