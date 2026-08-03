"""Shared immutable LSP types and text-coordinate helpers."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterator, Mapping
from urllib.parse import unquote, urlparse

JSON = dict[str, Any]
SERVER_NAME = "ggen-lsp-reference"
SERVER_VERSION = "26.8.1"

@dataclass(frozen=True)
class Document:
    uri: str
    language_id: str
    version: int | None
    text: str


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int


def _position(text: str, offset: int) -> JSON:
    offset = max(0, min(offset, len(text)))
    before = text[:offset]
    line = before.count("\n")
    last_newline = before.rfind("\n")
    character = offset if last_newline < 0 else offset - last_newline - 1
    return {"line": line, "character": character}


def _offset(text: str, position: Mapping[str, Any]) -> int:
    target_line = max(0, int(position.get("line", 0)))
    target_char = max(0, int(position.get("character", 0)))
    lines = text.splitlines(keepends=True)
    if target_line >= len(lines):
        return len(text)
    return min(sum(len(line) for line in lines[:target_line]) + target_char, len(text))


def _range(text: str, start: int, end: int | None = None) -> JSON:
    if end is None:
        end = start + 1
    return {"start": _position(text, start), "end": _position(text, max(start, end))}


def _diagnostic(
    text: str,
    code: str,
    message: str,
    start: int = 0,
    end: int | None = None,
    severity: int = 1,
    source: str = SERVER_NAME,
) -> JSON:
    return {
        "range": _range(text, start, end),
        "severity": severity,
        "code": code,
        "source": source,
        "message": message,
    }


def _language(uri: str, language_id: str | None = None) -> str:
    lang = (language_id or "").lower()
    if lang in {"toml", "turtle", "tera", "jinja", "jinja2"}:
        return "tera" if lang.startswith("jinja") else lang
    path = unquote(urlparse(uri).path).lower()
    if path.endswith((".ttl", ".rdf", ".n3")):
        return "turtle"
    if path.endswith(".toml"):
        return "toml"
    if path.endswith((".tera", ".tmpl", ".j2", ".jinja", ".jinja2")):
        return "tera"
    return "text"


def _token_at(text: str, position: Mapping[str, Any]) -> Token | None:
    offset = _offset(text, position)
    allowed = re.compile(r"[A-Za-z0-9_:@.\-\[\]]")
    start = offset
    while start > 0 and allowed.match(text[start - 1]):
        start -= 1
    end = offset
    while end < len(text) and allowed.match(text[end]):
        end += 1
    if start == end:
        return None
    return Token(text[start:end], start, end)


def _all_occurrences(text: str, token: Token) -> Iterator[tuple[int, int]]:
    pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(token.text)}(?![A-Za-z0-9_])")
    for match in pattern.finditer(text):
        yield match.start(), match.end()


def _whole_document_range(text: str) -> JSON:
    return {"start": {"line": 0, "character": 0}, "end": _position(text, len(text))}


def _optional_int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


