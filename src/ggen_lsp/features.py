"""Pure in-memory LSP feature projections."""
from __future__ import annotations

import re

from .core import Document, JSON, _language, _position, _range

TTL_COMPLETIONS = [
    ("@prefix", "Prefix declaration", "@prefix ${1:prefix}: <${2:iri}> ."),
    ("a", "rdf:type shorthand", "a "),
    ("rdfs:label", "Human-readable label", 'rdfs:label "${1:label}" ;'),
    ("dcterms:title", "Dublin Core title", 'dcterms:title "${1:title}" ;'),
    ("prov:wasDerivedFrom", "PROV-O lineage", "prov:wasDerivedFrom ${1:source} ;"),
]
TOML_COMPLETIONS = [
    ("[project]", "ggen project table", '[project]\nname = "${1:name}"\nversion = "${2:0.1.0}"'),
    ("[ontology]", "ontology table", '[ontology]\nsource = "${1:ontology.ttl}"'),
    ("[templates]", "templates table", "[templates]"),
    ("[validation]", "validation gates", "[validation]"),
    ("[[generation.rules]]", "generation rule", '[[generation.rules]]\nname = "${1:rule}"'),
]
TERA_COMPLETIONS = [
    ("{{ }}", "Render expression", "{{ ${1:value} }}"),
    ("{% if %}", "Conditional block", "{% if ${1:condition} %}\n${2}\n{% endif %}"),
    ("{% for %}", "Loop block", "{% for ${1:item} in ${2:items} %}\n${3}\n{% endfor %}"),
    ("{# #}", "Template comment", "{# ${1:comment} #}"),
]

HOVER_DOCS = {
    "@prefix": "Declares a Turtle namespace prefix.",
    "a": "Turtle shorthand for `rdf:type`.",
    "rdfs:label": "Human-readable label from RDF Schema.",
    "prov:wasDerivedFrom": "PROV-O derivation relation used for lineage.",
    "[project]": "Top-level ggen project metadata table.",
    "[ontology]": "Declares ontology inputs consumed by ggen.",
    "[[generation.rules]]": "Declares a deterministic generation rule.",
    "if": "Tera conditional block keyword.",
    "for": "Tera iteration block keyword.",
}

def _completion_items(language: str) -> list[JSON]:
    source = TTL_COMPLETIONS if language == "turtle" else TOML_COMPLETIONS if language == "toml" else TERA_COMPLETIONS if language == "tera" else []
    return [
        {
            "label": label,
            "kind": 14,
            "detail": detail,
            "insertText": insert_text,
            "insertTextFormat": 2,
        }
        for label, detail, insert_text in source
    ]


def _document_symbols(document: Document) -> list[JSON]:
    text = document.text
    language = _language(document.uri, document.language_id)
    symbols: list[JSON] = []
    if language == "turtle":
        for match in re.finditer(r"(?im)^\s*(?:@prefix|prefix)\s+([A-Za-z][\w-]*):", text):
            symbols.append({"name": f"prefix {match.group(1)}", "kind": 3, "range": _range(text, match.start(1), match.end(1)), "selectionRange": _range(text, match.start(1), match.end(1))})
        for match in re.finditer(r"(?m)^\s*([A-Za-z][\w-]*:[A-Za-z_][\w.-]*)\s+", text):
            symbols.append({"name": match.group(1), "kind": 5, "range": _range(text, match.start(1), match.end(1)), "selectionRange": _range(text, match.start(1), match.end(1))})
    elif language == "toml":
        for match in re.finditer(r"(?m)^\s*(\[\[?[^\]\n]+\]\]?)\s*$", text):
            symbols.append({"name": match.group(1), "kind": 2, "range": _range(text, match.start(1), match.end(1)), "selectionRange": _range(text, match.start(1), match.end(1))})
    elif language == "tera":
        for match in re.finditer(r"{%\s*(block|macro)\s+([A-Za-z_][\w-]*)", text):
            symbols.append({"name": match.group(2), "detail": match.group(1), "kind": 12, "range": _range(text, match.start(2), match.end(2)), "selectionRange": _range(text, match.start(2), match.end(2))})
    return symbols


def _folding_ranges(document: Document) -> list[JSON]:
    text = document.text
    ranges: list[JSON] = []
    stack: list[tuple[str, int]] = []
    for line_number, line in enumerate(text.splitlines()):
        open_match = re.search(r"{%\s*(if|for|block|macro)\b", line)
        close_match = re.search(r"{%\s*end(if|for|block|macro)\b", line)
        if open_match:
            stack.append((open_match.group(1), line_number))
        if close_match:
            expected = close_match.group(1)
            for index in range(len(stack) - 1, -1, -1):
                if stack[index][0] == expected:
                    _, start_line = stack.pop(index)
                    if line_number > start_line:
                        ranges.append({"startLine": start_line, "endLine": line_number, "kind": "region"})
                    break
    return ranges


def _semantic_tokens(document: Document) -> JSON:
    text = document.text
    language = _language(document.uri, document.language_id)
    raw: list[tuple[int, int, int, int, int]] = []
    patterns: list[tuple[re.Pattern[str], int]] = []
    if language == "turtle":
        patterns = [
            (re.compile(r"(?m)#.*$"), 7),
            (re.compile(r"\b(?:@prefix|PREFIX|BASE|a)\b"), 4),
            (re.compile(r"[A-Za-z][\w-]*:[A-Za-z_][\w.-]*"), 2),
            (re.compile(r'"(?:\\.|[^"\\])*"'), 5),
        ]
    elif language == "toml":
        patterns = [
            (re.compile(r"(?m)#.*$"), 7),
            (re.compile(r"(?m)^\s*\[\[?[^\]\n]+\]\]?"), 1),
            (re.compile(r'"(?:\\.|[^"\\])*"'), 5),
            (re.compile(r"\b\d+(?:\.\d+)?\b"), 6),
        ]
    elif language == "tera":
        patterns = [
            (re.compile(r"{#.*?#}", re.DOTALL), 7),
            (re.compile(r"{%\s*(?:if|for|block|macro|endif|endfor|endblock|endmacro)\b"), 4),
            (re.compile(r"{{\s*[A-Za-z_][\w.]*"), 3),
            (re.compile(r'"(?:\\.|[^"\\])*"'), 5),
        ]
    occupied: list[tuple[int, int]] = []
    for pattern, token_type in patterns:
        for match in pattern.finditer(text):
            start, end = match.span()
            if any(not (end <= left or start >= right) for left, right in occupied):
                continue
            occupied.append((start, end))
            pos = _position(text, start)
            raw.append((pos["line"], pos["character"], max(1, end - start), token_type, 0))
    raw.sort()
    data: list[int] = []
    previous_line = 0
    previous_character = 0
    for line, character, length, token_type, modifiers in raw:
        delta_line = line - previous_line
        delta_character = character - previous_character if delta_line == 0 else character
        data.extend([delta_line, delta_character, length, token_type, modifiers])
        previous_line = line
        previous_character = character
    return {"data": data}


def _format_text(document: Document) -> str:
    lines = [line.rstrip(" \t") for line in document.text.splitlines()]
    return "\n".join(lines) + "\n" if lines else ""


