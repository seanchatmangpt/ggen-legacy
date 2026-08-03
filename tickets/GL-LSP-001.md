# GL-LSP-001 — Implement the ggen legacy LSP on lsp-max

## Identity

- repository: `seanchatmangpt/ggen-legacy`
- original base: `70e599a599fedb7c62c965377cc2f80df1fa01ec`
- lsp-max subject: `seanchatmangpt/lsp-max@220d3251e959f6a58ce0311e995b31a85f98240c`
- implementation: Rust 2021, minimum Rust 1.82

## Admission

The prior Python reference implementation is not an admitted final runtime. This ticket requires the executable server to use `lsp-max` for framing, transport, server lifecycle, client notifications, protocol types, and method dispatch.

## Observable contract

1. `ggen-lsp` starts `lsp_max::Server` over stdin/stdout.
2. stdout contains only LSP protocol frames.
3. initialize advertises only implemented features.
4. open/change publish deterministic diagnostics.
5. close clears diagnostics.
6. Turtle, TOML, and Tera are analyzed.
7. completion, hover, document symbols, formatting, and quick fixes execute through the `lsp-max::LanguageServer` implementation.
8. local fmt, check, clippy, and tests pass against the exact dependency revision.

## Falsifiers

- Python remains on the executable path.
- the server bypasses `LspService` or `Server`.
- logging writes to stdout.
- a capability is advertised without a corresponding handler.
- diagnostics survive document close.
- the `lsp-max` revision floats.
- local Rust verification does not execute.

## Acceptance

```bash
cargo fmt --all -- --check
cargo check --all-targets
cargo clippy --all-targets -- -D warnings
cargo test --all-targets
```

## Standing

Until those commands execute locally, the implementation is `BLOCKED:TOOLCHAIN_UNAVAILABLE`, not `ALIVE` and not `BUILD_BROKEN`.
