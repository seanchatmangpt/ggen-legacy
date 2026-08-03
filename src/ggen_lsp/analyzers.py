"""Deterministic diagnostics for ggen Turtle, TOML, and Tera surfaces."""
from __future__ import annotations

import os
import re
import tomllib
from urllib.parse import unquote, urlparse

from .core import JSON, SERVER_NAME, _diagnostic, _language

KNOWN_TTL_PREFIXES = {
    "rdf",
    "rdfs",
    "xsd",
    "owl",
    "sh",
    "dcterms",
    "prov",
    "skos",
    "foaf",
    "dcat",
    "odrl",
    "schema",
    "sosa",
    "qudt",
    "fibo",
}

def _balanced_delimiters(text: str) -> list[JSON]:
    pairs = {")": "(", "]": "[", "}": "{"}
    opening = set(pairs.values())
    stack: list[tuple[str, int]] = []
    diagnostics: list[JSON] = []
    quote: str | None = None
    escaped = False
    for index, char in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char in opening:
            stack.append((char, index))
        elif char in pairs:
            if not stack or stack[-1][0] != pairs[char]:
                diagnostics.append(
                    _diagnostic(
                        text,
                        "GGEN-SYNTAX-001",
                        f"Unmatched closing delimiter {char!r}.",
                        index,
                        index + 1,
                    )
                )
            else:
                stack.pop()
    if quote is not None:
        diagnostics.append(
            _diagnostic(
                text,
                "GGEN-SYNTAX-002",
                f"Unterminated {quote} string literal.",
                max(0, len(text) - 1),
                len(text),
            )
        )
    for char, index in stack:
        diagnostics.append(
            _diagnostic(
                text,
                "GGEN-SYNTAX-003",
                f"Unclosed delimiter {char!r}.",
                index,
                index + 1,
            )
        )
    return diagnostics


def _toml_diagnostics(uri: str, text: str) -> list[JSON]:
    diagnostics: list[JSON] = []
    try:
        document = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        match = re.search(r"at line (\d+), column (\d+)", str(error))
        if match:
            line = max(0, int(match.group(1)) - 1)
            column = max(0, int(match.group(2)) - 1)
            lines = text.splitlines(keepends=True)
            start = sum(len(item) for item in lines[:line]) + column
        else:
            start = 0
        diagnostics.append(
            _diagnostic(text, "GGEN-TOML-001", f"TOML parse refusal: {error}", start)
        )
        return diagnostics

    if os.path.basename(unquote(urlparse(uri).path)) == "ggen.toml":
        if "project" not in document:
            diagnostics.append(
                _diagnostic(
                    text,
                    "GGEN-MANIFEST-001",
                    "ggen.toml requires a [project] table.",
                    0,
                    1,
                )
            )
        project = document.get("project")
        if isinstance(project, dict) and not project.get("name"):
            location = text.find("[project]")
            diagnostics.append(
                _diagnostic(
                    text,
                    "GGEN-MANIFEST-002",
                    "[project] requires a non-empty name.",
                    max(0, location),
                    max(1, location + len("[project]")),
                )
            )
    return diagnostics


def _turtle_diagnostics(text: str) -> list[JSON]:
    diagnostics = _balanced_delimiters(text)
    declared = set(KNOWN_TTL_PREFIXES)
    for match in re.finditer(
        r"(?im)^\s*(?:@prefix|prefix)\s+([A-Za-z][\w-]*):\s*<[^>]+>\s*\.?",
        text,
    ):
        declared.add(match.group(1))

    ignored = {"http", "https", "urn", "file", "mailto"}
    seen: set[str] = set()
    for match in re.finditer(r"(?<![\w:/])([A-Za-z][\w-]*):([A-Za-z_][\w.-]*)", text):
        prefix = match.group(1)
        if prefix in ignored or prefix in declared or prefix in seen:
            continue
        seen.add(prefix)
        diagnostics.append(
            _diagnostic(
                text,
                "GGEN-TTL-001",
                f"Prefix {prefix!r} is used but not declared.",
                match.start(1),
                match.end(1),
            )
        )

    for match in re.finditer(r"(?m)^\s*@prefix\s+[^\n]+(?<!\.)\s*$", text):
        diagnostics.append(
            _diagnostic(
                text,
                "GGEN-TTL-002",
                "Turtle @prefix declaration must end with '.'.",
                match.start(),
                match.end(),
            )
        )
    return diagnostics


def _tera_diagnostics(text: str) -> list[JSON]:
    diagnostics: list[JSON] = []
    delimiters = [("{{", "}}", "expression"), ("{%", "%}", "statement"), ("{#", "#}", "comment")]
    for opening, closing, name in delimiters:
        cursor = 0
        while True:
            start = text.find(opening, cursor)
            if start < 0:
                break
            end = text.find(closing, start + len(opening))
            if end < 0:
                diagnostics.append(
                    _diagnostic(
                        text,
                        "GGEN-TERA-001",
                        f"Unclosed Tera {name}; expected {closing!r}.",
                        start,
                        start + len(opening),
                    )
                )
                break
            cursor = end + len(closing)

    stack: list[tuple[str, int]] = []
    for match in re.finditer(r"{%\s*(if|for|block|macro|endif|endfor|endblock|endmacro)\b", text):
        keyword = match.group(1)
        if keyword.startswith("end"):
            expected = keyword[3:]
            if not stack or stack[-1][0] != expected:
                diagnostics.append(
                    _diagnostic(
                        text,
                        "GGEN-TERA-002",
                        f"Unexpected Tera closing block {keyword!r}.",
                        match.start(1),
                        match.end(1),
                    )
                )
            else:
                stack.pop()
        else:
            stack.append((keyword, match.start(1)))
    for keyword, start in stack:
        diagnostics.append(
            _diagnostic(
                text,
                "GGEN-TERA-003",
                f"Tera block {keyword!r} is not closed.",
                start,
                start + len(keyword),
            )
        )
    return diagnostics


def analyze_document(uri: str, text: str, language_id: str | None = None) -> list[JSON]:
    """Return deterministic diagnostics for one in-memory document."""
    language = _language(uri, language_id)
    if language == "toml":
        diagnostics = _toml_diagnostics(uri, text)
    elif language == "turtle":
        diagnostics = _turtle_diagnostics(text)
    elif language == "tera":
        diagnostics = _tera_diagnostics(text)
    else:
        diagnostics = _balanced_delimiters(text)

    if text and not text.endswith("\n"):
        diagnostics.append(
            _diagnostic(
                text,
                "GGEN-TEXT-001",
                "File should end with a newline.",
                max(0, len(text) - 1),
                len(text),
                severity=3,
            )
        )
    return sorted(
        diagnostics,
        key=lambda item: (
            item["range"]["start"]["line"],
            item["range"]["start"]["character"],
            str(item["code"]),
        ),
    )


