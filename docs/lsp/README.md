# ggen-legacy language-server reference runtime

## Purpose

This directory documents the executable `GL-LSP-001` boundary admitted by the root constitution. It is a dependency-free LSP 3.17 reference server for ggen's Turtle, TOML/ggen-manifest, and Tera surfaces.

The server is intentionally smaller than the live Rust implementation in `seanchatmangpt/ggen/crates/ggen-lsp`. Its role is to preserve and execute the protocol contract inside `ggen-legacy` without importing the monorepo's path-dependent build graph.

## Run

```bash
python3 bin/ggen-lsp
# equivalent
python3 bin/ggen-lsp stdio
```

Standard output is reserved for Content-Length framed JSON-RPC. Logs and fatal transport refusals use standard error.

## Verify

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_lsp_*.py' -v
python3 scripts/verify_lsp.py
cp evidence/lsp-reference/verification-report.json /tmp/ggen-lsp-report-a.json
python3 scripts/verify_lsp.py
cmp /tmp/ggen-lsp-report-a.json evidence/lsp-reference/verification-report.json
```

The test suite launches the real `python3 bin/ggen-lsp` subprocess. It does not call handlers in place as a substitute for protocol evidence.

## Supported lifecycle

- `initialize`, `initialized`, `shutdown`, `exit`
- `textDocument/didOpen`, `didChange` (full sync), `didSave`, `didClose`
- deterministic `publishDiagnostics`

## Supported requests

- completion and hover
- definition and references
- prepare rename and rename
- document and workspace symbols
- document and range formatting
- quick-fix code actions
- folding ranges
- semantic tokens
- inlay hints
- code lenses

## Diagnostics

| Code | Meaning |
|---|---|
| `GGEN-TOML-001` | TOML parse refusal |
| `GGEN-MANIFEST-001` | missing `[project]` in `ggen.toml` |
| `GGEN-MANIFEST-002` | missing project name |
| `GGEN-TTL-001` | undeclared Turtle prefix |
| `GGEN-TTL-002` | malformed `@prefix` terminator |
| `GGEN-TERA-001` | unclosed delimiter |
| `GGEN-TERA-002` | unexpected closing block |
| `GGEN-TERA-003` | unclosed block |
| `GGEN-SYNTAX-*` | common delimiter/string refusal |
| `GGEN-TEXT-001` | missing final newline |

## Nonclaims

This runtime does not claim full RDF/Turtle, SPARQL, TOML, or Tera conformance. It does not replace the live Rust feature set, MCP/A2A bridges, persistent workspace indexing, or `ggen-engine` integration. It establishes an executable, replayable compatibility floor.
