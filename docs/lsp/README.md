# ggen-legacy LSP on lsp-max

The executable language server is a Rust crate built directly on `lsp-max`.

## Exact runtime dependency

```text
repository: seanchatmangpt/lsp-max
commit:     220d3251e959f6a58ce0311e995b31a85f98240c
crate:      lsp-max 26.7.1
```

`lsp-max` owns JSON-RPC framing, the stdio server runtime, the `LanguageServer` contract, client notifications, and `lsp_types_max`. `ggen-legacy` owns domain diagnostics and feature behavior.

## Run

```bash
cargo run --bin ggen-lsp
```

Standard output is exclusively the LSP protocol channel. Tracing is directed to standard error.

## Verify locally

```bash
cargo fmt --all -- --check
cargo check --all-targets
cargo clippy --all-targets -- -D warnings
cargo test --all-targets
```

These commands must execute locally before the bounded runtime may be promoted to `ALIVE`.

## Implemented boundary

- full document synchronization
- diagnostics for Turtle, TOML/ggen manifests, and Tera
- completion
- hover
- document symbols
- document formatting
- quick-fix code actions
- clean diagnostic removal on close

## Exclusions

This change does not claim MCP/A2A, persistent graph indexing, the full feature surface of `ggen/crates/ggen-lsp`, release admission, or sunset admission.
