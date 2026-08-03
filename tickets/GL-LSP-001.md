# GL-LSP-001 — Admit and finish the bounded ggen language-server reference runtime

## Identity

- **Ticket:** `GL-LSP-001`
- **Repository:** `seanchatmangpt/ggen-legacy`
- **Exact base:** `70e599a599fedb7c62c965377cc2f80df1fa01ec`
- **Owner:** `ggen-legacy` reconstruction program
- **Expected transition:** `UNKNOWN → ALIVE` for the bounded reference LSP only

## Authority

`AGENTS.md` admits this ticket as the first executable source boundary. `RELEASE_CONTROL.md` continues to govern claim ceilings and prevents this ticket from promoting repository, production, release, or sunset standing.

## Problem

The receiving repository contains the v26.8.1 legacy corpus but no executable workspace. Its previous constitution permanently prohibited implementation directories even after the corpus identified `ggen-lsp` as a live subsystem. The live Rust implementation remains coupled to the `ggen` monorepo and external/path dependency closure. This ticket admits a dependency-free executable reference boundary that can be run and independently verified in a clean Python 3.11+ environment.

## Bounded scope

- Content-Length framed JSON-RPC over stdio, launched as `python3 bin/ggen-lsp`.
- In-memory full document synchronization.
- Deterministic diagnostics for Turtle, TOML/ggen manifests, and Tera.
- Implemented LSP requests: initialize, completion, hover, definition, references, prepareRename, rename, documentSymbol, workspace/symbol, formatting, rangeFormatting, codeAction, foldingRange, semanticTokens/full, inlayHint, codeLens, shutdown.
- Notifications: initialized, didOpen, didChange, didSave, didClose, exit.
- Recoverable malformed-JSON and unknown-method errors.
- Independent real-subprocess protocol verifier and deterministic evidence report.

## Inputs

- JSON-RPC request/notification bytes received over stdin.
- Document URI, language identifier, version, content, and positions.
- Exact authored source files bound by the verifier manifest.

## Outputs

- Framed JSON-RPC responses and notifications on stdout.
- Diagnostic and refusal details on stderr where protocol framing cannot carry them.
- Deterministic `evidence/lsp-reference/verification-report.json`.

## Implementation boundary

```text
bin/ggen-lsp
src/ggen_lsp/**
tests/test_lsp_*.py
scripts/verify_lsp.py
docs/lsp/**
evidence/lsp-reference/**
```

No handler may invoke a shell, access the network, install packages, modify Git, or write governed project files.

## Toolchain and dependency closure

- Python `>=3.11`.
- Standard library only.
- No package installation and no network dependency.

The historical Rust implementation and its path-dependent monorepo are observed context, not a dependency of this bounded runtime.

## Positive witnesses

1. Initialize response advertises only implemented capabilities.
2. Invalid TOML produces `GGEN-TOML-001` through a real `publishDiagnostics` notification.
3. A valid full-content change clears prior parse diagnostics.
4. Closing a document publishes an empty diagnostic list.
5. Completion, navigation, symbols, formatting, code actions, folding, semantic tokens, hints, and lenses return valid result shapes.
6. Shutdown and exit terminate with process status 0.
7. Two verifier executions produce byte-identical reports.

## Negative falsifiers

1. Any unframed stdout byte.
2. Malformed JSON terminates the server or prevents a later valid request.
3. Unknown request methods return success rather than `-32601`.
4. A partial incremental change is silently treated as full content.
5. `didClose` leaves stale diagnostics.
6. A handler imports a non-standard package or performs shell/network actuation.
7. The verifier report changes without an authored-source change.

## Acceptance commands

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_lsp_*.py' -v
python3 scripts/verify_lsp.py
cp evidence/lsp-reference/verification-report.json /tmp/ggen-lsp-report-a.json
python3 scripts/verify_lsp.py
cmp /tmp/ggen-lsp-report-a.json evidence/lsp-reference/verification-report.json
```

## Receipt and replay

- **Verifier:** `scripts/verify_lsp.py`
- **Evidence:** `evidence/lsp-reference/verification-report.json`
- **Replay:** execute the verifier twice and require byte identity.

## Exclusions

- Rust build compatibility.
- MCP and A2A transports.
- Workspace-wide semantic indexing beyond open documents.
- Full RDF 1.2, SPARQL, Tera, or TOML language conformance.
- Filesystem edits, command execution, network calls, deployment, release, production, certification, or sunset admission.
- Aggregate `ggen-legacy` repository crown.

## Acceptance

`ALIVE` applies only when every positive witness and negative falsifier above executes against the exact authored source manifest and deterministic replay matches.
