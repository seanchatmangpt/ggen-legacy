from __future__ import annotations

import json
import os
import pathlib
import select
import subprocess
import sys
import time
import unittest
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ggen_lsp.server import GgenLanguageServer, analyze_document  # noqa: E402


class LspProcess:
    def __init__(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        self.process = subprocess.Popen(
            [sys.executable, str(ROOT / "bin" / "ggen-lsp")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            bufsize=0,
        )
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        assert self.process.stderr is not None

    def send(self, message: Any) -> None:
        body = json.dumps(message, separators=(",", ":")).encode()
        self.process.stdin.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
        self.process.stdin.flush()

    def send_raw_body(self, body: bytes) -> None:
        self.process.stdin.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
        self.process.stdin.flush()

    def read(self, timeout: float = 3.0) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        headers: dict[str, str] = {}
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("timed out waiting for LSP header")
            ready, _, _ = select.select([self.process.stdout], [], [], remaining)
            if not ready:
                raise TimeoutError("timed out waiting for LSP header")
            line = self.process.stdout.readline()
            if line == b"":
                stderr = self.process.stderr.read().decode(errors="replace")
                raise EOFError(f"server closed stdout; stderr={stderr!r}")
            if line in {b"\r\n", b"\n"}:
                break
            name, value = line.decode("ascii").split(":", 1)
            headers[name.lower()] = value.strip()
        length = int(headers["content-length"])
        body = self.process.stdout.read(length)
        return json.loads(body)

    def initialize(self) -> dict[str, Any]:
        self.send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"rootUri": "file:///tmp/ggen"}})
        return self.read()

    def stop(self) -> None:
        if self.process.poll() is None:
            try:
                self.send({"jsonrpc": "2.0", "id": 900, "method": "shutdown", "params": {}})
                self.read()
                self.send({"jsonrpc": "2.0", "method": "exit", "params": {}})
                self.process.wait(timeout=3)
            except Exception:
                self.process.kill()
                self.process.wait(timeout=3)
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            if stream is not None and not stream.closed:
                stream.close()


class AnalyzerTests(unittest.TestCase):
    def test_toml_turtle_and_tera_diagnostics_are_deterministic(self) -> None:
        toml = analyze_document("file:///tmp/ggen.toml", "[project\nname = 'x'")
        self.assertIn("GGEN-TOML-001", {item["code"] for item in toml})

        turtle = analyze_document("file:///tmp/model.ttl", "ex:thing a missing:Type .\n")
        codes = [item["code"] for item in turtle]
        self.assertEqual(codes.count("GGEN-TTL-001"), 2)
        self.assertEqual(turtle, analyze_document("file:///tmp/model.ttl", "ex:thing a missing:Type .\n"))

        tera = analyze_document("file:///tmp/view.tera", "{% if ready %}\n{{ value }}\n")
        self.assertIn("GGEN-TERA-003", {item["code"] for item in tera})

    def test_advertised_capabilities_have_dispatch_paths(self) -> None:
        capabilities = GgenLanguageServer.capabilities()
        expected = {
            "completionProvider",
            "hoverProvider",
            "definitionProvider",
            "referencesProvider",
            "renameProvider",
            "documentSymbolProvider",
            "workspaceSymbolProvider",
            "documentFormattingProvider",
            "documentRangeFormattingProvider",
            "codeActionProvider",
            "foldingRangeProvider",
            "semanticTokensProvider",
            "inlayHintProvider",
            "codeLensProvider",
        }
        self.assertTrue(expected.issubset(capabilities))


class ProtocolLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lsp = LspProcess()

    def tearDown(self) -> None:
        self.lsp.stop()

    def test_initialize_open_change_features_close_shutdown(self) -> None:
        initialized = self.lsp.initialize()
        self.assertEqual(initialized["id"], 1)
        self.assertEqual(initialized["result"]["serverInfo"]["name"], "ggen-lsp-reference")
        capabilities = initialized["result"]["capabilities"]
        self.assertEqual(capabilities["textDocumentSync"]["change"], 1)

        uri = "file:///tmp/ggen.toml"
        invalid = "[project\nname = 'demo'"
        self.lsp.send({"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {"textDocument": {"uri": uri, "languageId": "toml", "version": 1, "text": invalid}}})
        published = self.lsp.read()
        self.assertEqual(published["method"], "textDocument/publishDiagnostics")
        self.assertIn("GGEN-TOML-001", {item["code"] for item in published["params"]["diagnostics"]})

        valid = '[project]\nname = "demo"\n\n[ontology]\nsource = "ontology.ttl"\n'
        self.lsp.send({"jsonrpc": "2.0", "method": "textDocument/didChange", "params": {"textDocument": {"uri": uri, "version": 2}, "contentChanges": [{"text": valid}]}})
        cleared = self.lsp.read()
        self.assertEqual(cleared["params"]["diagnostics"], [])

        requests = [
            (2, "textDocument/completion", {"textDocument": {"uri": uri}, "position": {"line": 0, "character": 1}}),
            (3, "textDocument/hover", {"textDocument": {"uri": uri}, "position": {"line": 0, "character": 4}}),
            (4, "textDocument/documentSymbol", {"textDocument": {"uri": uri}}),
            (5, "workspace/symbol", {"query": "project"}),
            (6, "textDocument/formatting", {"textDocument": {"uri": uri}, "options": {"tabSize": 2, "insertSpaces": True}}),
            (7, "textDocument/foldingRange", {"textDocument": {"uri": uri}}),
            (8, "textDocument/semanticTokens/full", {"textDocument": {"uri": uri}}),
            (9, "textDocument/inlayHint", {"textDocument": {"uri": uri}, "range": {"start": {"line": 0, "character": 0}, "end": {"line": 10, "character": 0}}}),
            (10, "textDocument/codeLens", {"textDocument": {"uri": uri}}),
            (11, "textDocument/references", {"textDocument": {"uri": uri}, "position": {"line": 1, "character": 2}, "context": {"includeDeclaration": True}}),
            (12, "textDocument/prepareRename", {"textDocument": {"uri": uri}, "position": {"line": 1, "character": 2}}),
            (13, "textDocument/rename", {"textDocument": {"uri": uri}, "position": {"line": 1, "character": 2}, "newName": "project_name"}),
            (14, "textDocument/definition", {"textDocument": {"uri": uri}, "position": {"line": 1, "character": 2}}),
        ]
        results: dict[int, Any] = {}
        for request_id, method, params in requests:
            self.lsp.send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
            response = self.lsp.read()
            self.assertNotIn("error", response, method)
            results[request_id] = response["result"]
        self.assertGreater(len(results[2]["items"]), 0)
        self.assertGreater(len(results[4]), 0)
        self.assertIn("data", results[8])
        self.assertGreater(len(results[10]), 0)

        diagnostic = {"range": {"start": {"line": 4, "character": 22}, "end": {"line": 4, "character": 23}}, "code": "GGEN-TEXT-001", "message": "File should end with a newline."}
        self.lsp.send({"jsonrpc": "2.0", "id": 15, "method": "textDocument/codeAction", "params": {"textDocument": {"uri": uri}, "range": diagnostic["range"], "context": {"diagnostics": [diagnostic]}}})
        actions = self.lsp.read()["result"]
        self.assertEqual(actions[0]["title"], "Add final newline")

        self.lsp.send({"jsonrpc": "2.0", "method": "textDocument/didClose", "params": {"textDocument": {"uri": uri}}})
        closed = self.lsp.read()
        self.assertEqual(closed["params"]["diagnostics"], [])

        self.lsp.send({"jsonrpc": "2.0", "id": 16, "method": "shutdown", "params": {}})
        self.assertIsNone(self.lsp.read()["result"])
        self.lsp.send({"jsonrpc": "2.0", "method": "exit", "params": {}})
        self.assertEqual(self.lsp.process.wait(timeout=3), 0)
        stdout_tail = self.lsp.process.stdout.read()
        self.assertEqual(stdout_tail, b"")

    def test_malformed_json_recovers_and_unknown_method_refuses(self) -> None:
        self.lsp.send_raw_body(b"{not-json")
        parse_error = self.lsp.read()
        self.assertEqual(parse_error["error"]["code"], -32700)

        initialized = self.lsp.initialize()
        self.assertEqual(initialized["id"], 1)

        self.lsp.send({"jsonrpc": "2.0", "id": 40, "method": "ggen/ambientShell", "params": {"command": "rm -rf /"}})
        refused = self.lsp.read()
        self.assertEqual(refused["error"]["code"], -32601)
        self.assertIn("Method not found", refused["error"]["message"])

    def test_turtle_and_tera_protocol_surfaces(self) -> None:
        self.lsp.initialize()

        ttl_uri = "file:///tmp/model.ttl"
        ttl_text = "@prefix ex: <urn:ex:> .\nex:x a missing:Thing .\n"
        self.lsp.send({"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {"textDocument": {"uri": ttl_uri, "languageId": "turtle", "version": 1, "text": ttl_text}}})
        ttl_diagnostics = self.lsp.read()["params"]["diagnostics"]
        missing = next(item for item in ttl_diagnostics if item["code"] == "GGEN-TTL-001")
        self.assertIn("missing", missing["message"])

        self.lsp.send({"jsonrpc": "2.0", "id": 60, "method": "textDocument/completion", "params": {"textDocument": {"uri": ttl_uri}, "position": {"line": 1, "character": 7}}})
        labels = {item["label"] for item in self.lsp.read()["result"]["items"]}
        self.assertIn("@prefix", labels)

        self.lsp.send({"jsonrpc": "2.0", "id": 61, "method": "textDocument/codeAction", "params": {"textDocument": {"uri": ttl_uri}, "range": missing["range"], "context": {"diagnostics": [missing]}}})
        actions = self.lsp.read()["result"]
        self.assertEqual(actions[0]["title"], "Declare prefix missing")

        self.lsp.send({"jsonrpc": "2.0", "id": 62, "method": "textDocument/semanticTokens/full", "params": {"textDocument": {"uri": ttl_uri}}})
        self.assertGreater(len(self.lsp.read()["result"]["data"]), 0)

        tera_uri = "file:///tmp/view.tera"
        tera_invalid = "{% if ready %}\n{{ value }}\n"
        self.lsp.send({"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {"textDocument": {"uri": tera_uri, "languageId": "tera", "version": 1, "text": tera_invalid}}})
        tera_diagnostics = self.lsp.read()["params"]["diagnostics"]
        self.assertIn("GGEN-TERA-003", {item["code"] for item in tera_diagnostics})

        tera_valid = "{% if ready %}\n{{ value }}\n{% endif %}\n"
        self.lsp.send({"jsonrpc": "2.0", "method": "textDocument/didChange", "params": {"textDocument": {"uri": tera_uri, "version": 2}, "contentChanges": [{"text": tera_valid}]}})
        self.assertEqual(self.lsp.read()["params"]["diagnostics"], [])

        self.lsp.send({"jsonrpc": "2.0", "id": 63, "method": "textDocument/foldingRange", "params": {"textDocument": {"uri": tera_uri}}})
        folding = self.lsp.read()["result"]
        self.assertEqual(folding[0]["startLine"], 0)
        self.assertEqual(folding[0]["endLine"], 2)

        self.lsp.send({"jsonrpc": "2.0", "id": 64, "method": "textDocument/completion", "params": {"textDocument": {"uri": tera_uri}, "position": {"line": 1, "character": 2}}})
        tera_labels = {item["label"] for item in self.lsp.read()["result"]["items"]}
        self.assertIn("{% if %}", tera_labels)

    def test_non_object_json_rpc_message_is_invalid_request(self) -> None:
        self.lsp.send([])
        response = self.lsp.read()
        self.assertEqual(response["error"]["code"], -32600)

    def test_incremental_change_is_refused_not_silently_applied(self) -> None:
        self.lsp.initialize()
        uri = "file:///tmp/model.ttl"
        self.lsp.send({"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {"textDocument": {"uri": uri, "languageId": "turtle", "version": 1, "text": "@prefix ex: <urn:ex:> .\nex:x a ex:Thing .\n"}}})
        self.lsp.read()
        self.lsp.send({"jsonrpc": "2.0", "id": 50, "method": "textDocument/didChange", "params": {"textDocument": {"uri": uri, "version": 2}, "contentChanges": [{"range": {"start": {"line": 1, "character": 0}, "end": {"line": 1, "character": 2}}, "text": "ex"}]}})
        refusal = self.lsp.read()
        self.assertEqual(refusal["error"]["code"], -32602)
        self.assertIn("incremental ranges are refused", refusal["error"]["message"])


class TransportRefusalTests(unittest.TestCase):
    def test_missing_content_length_is_typed_fatal_refusal(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        result = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "ggen-lsp")],
            input=b"X-Test: 1\r\n\r\n{}",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            timeout=3,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"GGEN-LSP-TRANSPORT-004", result.stderr)


if __name__ == "__main__":
    unittest.main()
