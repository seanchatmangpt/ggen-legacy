#!/usr/bin/env python3
"""Append a `## Dry run` section to each v26.11.9 ticket from the ggen-create probe table.

Usage: PYTHONPATH=~/ggen-create/src python3 scripts/add_dryrun_sections.py
Idempotent: a ticket that already has the section is replaced, never duplicated.
"""
from __future__ import annotations

from pathlib import Path
import re

from ggen_create.cutover_dryrun.tickets import PROBES

D = Path(__file__).resolve().parents[1] / "docs/jira/v26.11.9"
MARK = "## Dry run"


def section(p) -> str:
    lines = [MARK, "", f"Command: `{p.command}`",
             "Read-only; add `--selftest` to prove each deterministic clause flips.",
             f"Highest tier needed to fully decide: {p.tier}", "", "Clauses:"]
    for c in p.clauses:
        lines.append(f"- [{c.tier}/{c.kind}] {c.desc}")
        for key in ("paths", "path", "pattern", "n", "fields", "reason", "repos", "argv"):
            if key in c.args and c.args[key] not in (None, [], ""):
                val = c.args[key]
                if isinstance(val, list):
                    lines.append(f"  - {key}:")
                    lines.extend(f"    - `{v}`" for v in val)
                else:
                    lines.append(f"  - {key}: `{val}`")
    lines += ["", "PASS_PREDICTED only when every T0 clause passes; T1/T2 clauses stay UNVERIFIED",
              "until a scratch or shadow run is authorized.", ""]
    return "\n".join(lines)


for p in PROBES:
    n = int(p.id.split("-")[1])
    f = next(D.glob(f"tickets/T-{n:03d}-*.md"))
    text = f.read_text()
    text = re.sub(rf"\n{MARK}\n.*?(?=\n## See Also)", "", text, flags=re.S)
    text = text.replace("\n## See Also", "\n" + section(p) + "\n## See Also", 1)
    f.write_text(text)
print(f"{len(PROBES)} tickets updated")
