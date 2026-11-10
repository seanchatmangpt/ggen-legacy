#!/usr/bin/env python3
"""Write one dry-run receipt per v26.11.9 ticket from a `ggen-create cutover dryrun` report.

usage: gen_v26_11_9_receipts.py <report.json>
Standing maps PASS_PREDICTED->PARTIAL (predicted, not executed), FAIL/BLOCKED->BLOCKED,
UNVERIFIED->UNVERIFIED. These receipts describe dry-run results only; nothing was executed.
"""
import json, re, sys, textwrap
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "docs/jira/v26.11.9"
MAP = {"PASS_PREDICTED": "PARTIAL", "FAIL": "BLOCKED", "BLOCKED": "BLOCKED", "UNVERIFIED": "UNVERIFIED"}


def wrap(text, indent="  "):
    return "\n".join(textwrap.wrap(text, 96, initial_indent=indent, subsequent_indent=indent + "  "))


report = json.loads(Path(sys.argv[1]).read_text())
(D / "receipts/lanes").mkdir(parents=True, exist_ok=True)
for t in report["tickets"]:
    n = int(t["ticket"].split("-")[1])
    slug = next((D / "tickets").glob(f"T-{n:03d}-*.md")).stem.split("-", 2)[2]
    lines = [f"# T{n:03d} — {t['title']} (dry-run receipt)", "", f"Standing: {MAP[t['standing']]}", "",
             "## Subject", "",
             f"Dry-run: `ggen-create cutover dryrun --ticket {t['ticket']}` at {report['generated_at']}",
             f"Report verdict: {report['verdict']}; tier needed to decide fully: {t['tier']}",
             "Source heads:"]
    lines += [f"- {name}: {sha}" for name, sha in sorted(report["identity"].items())]
    lines += ["", "## Clauses", ""]
    for c in t["clauses"]:
        lines.append(f"- [{c['status']}] ({c['tier']}/{c['kind']}) {c['desc']}")
        lines.append(wrap(c["detail"]))
    lines += ["", "## Not claimed", "",
              "This is a file-level prediction. No cutover, migration, generation or backend run",
              "is evidenced here, and T1/T2 clauses stay UNVERIFIED until a scratch or shadow run.",
              "", "## See Also", "", "../../tickets/ · ../dry-run-latest.json · ../../INDEX.md", ""]
    (D / "receipts/lanes" / f"t{n:03d}-{slug}.md").write_text("\n".join(lines))
print(f"{len(report['tickets'])} receipts")
