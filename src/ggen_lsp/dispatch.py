"""Admitted JSON-RPC method dispatcher and document state."""
from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from .analyzers import analyze_document
from .core import (
    Document, JSON, SERVER_NAME, SERVER_VERSION, Token, _all_occurrences,
    _language, _optional_int, _position, _range, _token_at, _whole_document_range,
)
from .features import (
    HOVER_DOCS, _completion_items, _document_symbols, _folding_ranges,
    _format_text, _semantic_tokens,
)

class GgenLanguageServer:
    """Stateful JSON-RPC dispatcher for the bounded LSP contract."""

    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}
        self.shutdown_requested = False
        self.exit_requested = False

    @staticmethod
    def capabilities() -> JSON:
        return {
            "textDocumentSync": {"openClose": True, "change": 1, "save": {"includeText": False}},
            "completionProvider": {"triggerCharacters": [":", "@", ".", "{", "[", '"', "|"]},
            "hoverProvider": True,
            "definitionProvider": True,
            "referencesProvider": True,
            "renameProvider": {"prepareProvider": True},
            "documentSymbolProvider": True,
            "workspaceSymbolProvider": True,
            "documentFormattingProvider": True,
            "documentRangeFormattingProvider": True,
            "codeActionProvider": {"codeActionKinds": ["quickfix"], "resolveProvider": False},
            "foldingRangeProvider": True,
            "semanticTokensProvider": {
                "legend": {
                    "tokenTypes": ["namespace", "class", "property", "variable", "keyword", "string", "number", "comment", "function"],
                    "tokenModifiers": [],
                },
                "full": True,
            },
            "inlayHintProvider": True,
            "codeLensProvider": {"resolveProvider": False},
        }

    def _document(self, params: Mapping[str, Any]) -> Document | None:
        text_document = params.get("textDocument", {})
        uri = text_document.get("uri") if isinstance(text_document, Mapping) else None
        return self.documents.get(str(uri)) if uri else None

    def _publish(self, document: Document, diagnostics: Sequence[JSON] | None = None) -> JSON:
        return {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": document.uri,
                "version": document.version,
                "diagnostics": list(diagnostics if diagnostics is not None else analyze_document(document.uri, document.text, document.language_id)),
            },
        }

    def dispatch(self, message: Any) -> tuple[JSON | None, list[JSON]]:
        if not isinstance(message, dict):
            return self._error(None, -32600, "Invalid Request: JSON-RPC message must be an object."), []
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params") or {}
        if message.get("jsonrpc") != "2.0" or not isinstance(method, str):
            return self._error(request_id, -32600, "Invalid Request: expected jsonrpc='2.0' and string method."), []
        if not isinstance(params, dict):
            return self._error(request_id, -32602, "Invalid params: expected object."), []

        notifications: list[JSON] = []
        try:
            if method == "initialize":
                result = {
                    "capabilities": self.capabilities(),
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                }
            elif method == "initialized":
                return None, []
            elif method == "shutdown":
                self.shutdown_requested = True
                result = None
            elif method == "exit":
                self.exit_requested = True
                return None, []
            elif method == "textDocument/didOpen":
                item = params["textDocument"]
                document = Document(str(item["uri"]), str(item.get("languageId", "")), _optional_int(item.get("version")), str(item.get("text", "")))
                self.documents[document.uri] = document
                notifications.append(self._publish(document))
                return None, notifications
            elif method == "textDocument/didChange":
                item = params["textDocument"]
                uri = str(item["uri"])
                changes = params.get("contentChanges")
                if not isinstance(changes, list) or not changes:
                    raise ValueError("contentChanges must contain at least one full document change")
                last = changes[-1]
                if not isinstance(last, dict) or "text" not in last:
                    raise ValueError("full-sync change requires a text field")
                if "range" in last:
                    raise ValueError("incremental ranges are refused because the server advertises full sync")
                previous = self.documents.get(uri, Document(uri, "", None, ""))
                document = Document(uri, previous.language_id, _optional_int(item.get("version")), str(last["text"]))
                self.documents[uri] = document
                notifications.append(self._publish(document))
                return None, notifications
            elif method == "textDocument/didSave":
                return None, []
            elif method == "textDocument/didClose":
                item = params["textDocument"]
                uri = str(item["uri"])
                document = self.documents.pop(uri, Document(uri, "", None, ""))
                notifications.append(self._publish(document, []))
                return None, notifications
            elif method == "textDocument/completion":
                document = self._require_document(params)
                result = {"isIncomplete": False, "items": _completion_items(_language(document.uri, document.language_id))}
            elif method == "textDocument/hover":
                document = self._require_document(params)
                token = _token_at(document.text, params.get("position", {}))
                detail = HOVER_DOCS.get(token.text if token else "")
                result = None if not token or not detail else {"contents": {"kind": "markdown", "value": detail}, "range": _range(document.text, token.start, token.end)}
            elif method == "textDocument/definition":
                document = self._require_document(params)
                token = _token_at(document.text, params.get("position", {}))
                result = self._definition(document, token)
            elif method == "textDocument/references":
                document = self._require_document(params)
                token = _token_at(document.text, params.get("position", {}))
                result = [] if token is None else [{"uri": document.uri, "range": _range(document.text, start, end)} for start, end in _all_occurrences(document.text, token)]
            elif method == "textDocument/prepareRename":
                document = self._require_document(params)
                token = _token_at(document.text, params.get("position", {}))
                result = None if token is None else {"range": _range(document.text, token.start, token.end), "placeholder": token.text}
            elif method == "textDocument/rename":
                document = self._require_document(params)
                token = _token_at(document.text, params.get("position", {}))
                new_name = str(params.get("newName", ""))
                if token is None or not re.fullmatch(r"[A-Za-z_][\w:.-]*", new_name):
                    result = None
                else:
                    edits = [{"range": _range(document.text, start, end), "newText": new_name} for start, end in _all_occurrences(document.text, token)]
                    result = {"changes": {document.uri: edits}}
            elif method == "textDocument/documentSymbol":
                result = _document_symbols(self._require_document(params))
            elif method == "workspace/symbol":
                query = str(params.get("query", "")).lower()
                result = []
                for document in self.documents.values():
                    for symbol in _document_symbols(document):
                        if not query or query in symbol["name"].lower():
                            result.append({"name": symbol["name"], "kind": symbol["kind"], "location": {"uri": document.uri, "range": symbol["range"]}})
            elif method in {"textDocument/formatting", "textDocument/rangeFormatting"}:
                document = self._require_document(params)
                formatted = _format_text(document)
                result = [] if formatted == document.text else [{"range": _whole_document_range(document.text), "newText": formatted}]
            elif method == "textDocument/codeAction":
                document = self._require_document(params)
                result = self._code_actions(document, params)
            elif method == "textDocument/foldingRange":
                result = _folding_ranges(self._require_document(params))
            elif method == "textDocument/semanticTokens/full":
                result = _semantic_tokens(self._require_document(params))
            elif method == "textDocument/inlayHint":
                document = self._require_document(params)
                result = self._inlay_hints(document)
            elif method == "textDocument/codeLens":
                document = self._require_document(params)
                count = len(analyze_document(document.uri, document.text, document.language_id))
                result = [{"range": _range(document.text, 0, 0), "command": {"title": f"ggen diagnostics: {count}", "command": "ggen.showDiagnostics", "arguments": [document.uri]}}]
            else:
                return self._error(request_id, -32601, f"Method not found: {method}"), []
        except (KeyError, TypeError, ValueError) as error:
            return self._error(request_id, -32602, f"Invalid params: {error}"), []

        if request_id is None:
            return None, notifications
        return {"jsonrpc": "2.0", "id": request_id, "result": result}, notifications

    def _require_document(self, params: Mapping[str, Any]) -> Document:
        document = self._document(params)
        if document is None:
            raise ValueError("document is not open")
        return document

    @staticmethod
    def _error(request_id: Any, code: int, message: str, data: Any = None) -> JSON:
        error: JSON = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return {"jsonrpc": "2.0", "id": request_id, "error": error}

    @staticmethod
    def _definition(document: Document, token: Token | None) -> JSON | None:
        if token is None:
            return None
        language = _language(document.uri, document.language_id)
        patterns: list[re.Pattern[str]] = []
        if language == "turtle" and ":" in token.text:
            patterns.append(re.compile(rf"(?m)^\s*{re.escape(token.text)}\s+"))
        if language == "toml":
            patterns.append(re.compile(rf"(?m)^\s*{re.escape(token.text)}\s*="))
        for pattern in patterns:
            match = pattern.search(document.text)
            if match:
                start = match.start() + len(match.group(0)) - len(match.group(0).lstrip())
                return {"uri": document.uri, "range": _range(document.text, start, start + len(token.text))}
        occurrence = next(_all_occurrences(document.text, token), None)
        return None if occurrence is None else {"uri": document.uri, "range": _range(document.text, *occurrence)}

    @staticmethod
    def _code_actions(document: Document, params: Mapping[str, Any]) -> list[JSON]:
        diagnostics = params.get("context", {}).get("diagnostics", []) if isinstance(params.get("context"), dict) else []
        actions: list[JSON] = []
        for diagnostic in diagnostics if isinstance(diagnostics, list) else []:
            if not isinstance(diagnostic, dict):
                continue
            code = diagnostic.get("code")
            if code == "GGEN-TEXT-001":
                actions.append({"title": "Add final newline", "kind": "quickfix", "diagnostics": [diagnostic], "edit": {"changes": {document.uri: [{"range": _range(document.text, len(document.text), len(document.text)), "newText": "\n"}]}}})
            elif code == "GGEN-TTL-001":
                prefix_match = re.search(r"Prefix '([^']+)'", str(diagnostic.get("message", "")))
                if prefix_match:
                    prefix = prefix_match.group(1)
                    actions.append({"title": f"Declare prefix {prefix}", "kind": "quickfix", "diagnostics": [diagnostic], "edit": {"changes": {document.uri: [{"range": _range(document.text, 0, 0), "newText": f"@prefix {prefix}: <urn:{prefix}:> .\n"}]}}})
        return actions

    @staticmethod
    def _inlay_hints(document: Document) -> list[JSON]:
        language = _language(document.uri, document.language_id)
        hints: list[JSON] = []
        if language == "turtle":
            for match in re.finditer(r"(?m)^\s*([A-Za-z][\w-]*:[A-Za-z_][\w.-]*)\s+a\s+", document.text):
                hints.append({"position": _position(document.text, match.end()), "label": "rdf:type", "kind": 2, "paddingLeft": True})
        elif language == "toml":
            for match in re.finditer(r"(?m)^\s*([A-Za-z_][\w.-]*)\s*=\s*", document.text):
                hints.append({"position": _position(document.text, match.end()), "label": "value", "kind": 2, "paddingLeft": True})
        return hints


