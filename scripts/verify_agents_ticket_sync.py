#!/usr/bin/env python3
"""GL-EXP-052: verify AGENTS.md's `drafted tickets` field stays in sync with
the real `tickets/GL-*.md` files on disk.

Read-only in every code path, including error paths: this script never
writes to AGENTS.md or any ticket file. stdlib only (argparse, re, pathlib).

`AGENTS.md`'s `- drafted tickets (see tickets/):` field enumerates ticket
slugs by hand. GL-ERRC-013's own Hard law 4 says that field "must be
re-run at execution time ... since new tickets will keep being drafted" --
this script mechanically checks that claim in both directions:

- missing-from-field: a `tickets/GL-*.md` file on disk with no matching
  slug inside the field's bulleted block.
- stale-in-field: a slug inside the field's block with no corresponding
  `tickets/<slug>.md` file on disk.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The field starts at this exact bullet line (leading "- ", no indent).
FIELD_START_RE = re.compile(r"^- drafted tickets \(see tickets/\):\s*$")
# The field ends at the next top-level bullet ("^- ", no indent) --
# indented sub-bullets like "  - `GL-EXP-001`: ..." do not match this.
FIELD_END_RE = re.compile(r"^- ")
SLUG_RE = re.compile(r"GL-[A-Z]+-[0-9]+")


class ParseError(Exception):
    """Raised when AGENTS.md does not contain the expected field header."""


def extract_field_block(agents_text: str) -> str:
    """Return the exact bulleted block bounded by the `drafted tickets`
    header line through (but not including) the next top-level `- ` line.

    Never a whole-file substring search -- ticket slugs appear elsewhere in
    AGENTS.md (header lines, prose) that must not be double-counted.
    """
    lines = agents_text.splitlines()

    start_idx = None
    for i, line in enumerate(lines):
        if FIELD_START_RE.match(line):
            start_idx = i
            break
    if start_idx is None:
        raise ParseError(
            "could not find a line matching "
            "'- drafted tickets (see tickets/):' in the supplied AGENTS.md text"
        )

    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if FIELD_END_RE.match(lines[j]):
            end_idx = j
            break

    return "\n".join(lines[start_idx:end_idx])


def slugs_in_block(block: str) -> set[str]:
    return set(SLUG_RE.findall(block))


def ticket_stems(tickets_dir: Path) -> set[str]:
    return {p.stem for p in tickets_dir.glob("GL-*.md")}


def diff_sync(field_slugs: set[str], disk_stems: set[str]) -> tuple[list[str], list[str]]:
    missing_from_field = sorted(disk_stems - field_slugs)
    stale_in_field = sorted(field_slugs - disk_stems)
    return missing_from_field, stale_in_field


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify AGENTS.md's 'drafted tickets' field is in sync with "
            "tickets/GL-*.md on disk. Read-only; exits non-zero on any drift."
        )
    )
    parser.add_argument(
        "--agents-file",
        type=Path,
        default=ROOT / "AGENTS.md",
        help="path to AGENTS.md (default: repo-root AGENTS.md)",
    )
    parser.add_argument(
        "--tickets-dir",
        type=Path,
        default=ROOT / "tickets",
        help="path to the tickets/ directory (default: repo-root tickets/)",
    )
    args = parser.parse_args(argv)

    try:
        agents_text = args.agents_file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: could not read {args.agents_file}: {exc}", file=sys.stderr)
        return 2

    try:
        block = extract_field_block(agents_text)
    except ParseError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return 2

    field_slugs = slugs_in_block(block)
    disk_stems = ticket_stems(args.tickets_dir)

    missing_from_field, stale_in_field = diff_sync(field_slugs, disk_stems)

    for slug in missing_from_field:
        print(f"missing-from-field: {slug}")
    for slug in stale_in_field:
        print(f"stale-in-field: {slug}")

    if missing_from_field or stale_in_field:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
