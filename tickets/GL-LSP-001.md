# GL-LSP-001 — Execute the ggen-manufactured LSP contract on lsp-max

## Identity

- repository: `seanchatmangpt/ggen-legacy`
- original base: `70e599a599fedb7c62c965377cc2f80df1fa01ec`
- producing repository: `seanchatmangpt/ggen`
- producing authority: `self-host/lsp-contract/ontology.ttl`
- received authority: `authority/lsp-contract.json`
- contract: `ggen.lsp.contract/1`, version `26.8.5`
- lsp-max: `220d3251e959f6a58ce0311e995b31a85f98240c`
- implementation: Rust 2021, minimum Rust 1.82

## Admission

The final reference runtime is Rust on lsp-max. The prior Python candidate is superseded. ggen owns generalized manufacturing law and generates the portable contract. ggen-legacy independently receives, implements, verifies, and replays it.

## Observable contract

1. Start `lsp_max::Server` over stdin/stdout.
2. Keep stdout frame-pure.
3. Implement the 29 received protocol methods.
4. Advertise every implemented capability truthfully; register type hierarchy dynamically when supported.
5. Use full document synchronization and refuse incremental ranges.
6. Analyze `.ttl`, `.nt`, `.nq`, `.rq`, `.sparql`, `.tera`, `.toml`, and generated `.rs`.
7. Emit receiver-owned typed diagnostics, including generated module ownership.
8. Clear diagnostics on close.
9. Keep the received JSON and generated Rust contract byte/semantic aligned.
10. Refuse ambient shell, network, and external-actuation authority.

## Positive witnesses

- independent source-contract verifier exits 0;
- JSON and generated Rust arrays agree exactly;
- every non-framework received method has a `LanguageServer` handler;
- every received surface is dispatched;
- generated Rust without a generation-rule owner emits `GGEN-SRC-004`;
- real stdio initialize/open/change/close and hierarchy requests return lawful responses.

## Falsifiers

- received projection differs from ggen output;
- capability without handler;
- missing surface or receiver-owned diagnostic;
- Python or custom JSON-RPC runtime on the final path;
- logging on stdout;
- incremental change silently accepted;
- generated module accepted without generation authority;
- floating lsp-max revision;
- source verification promoted to runtime `ALIVE`.

## Acceptance

```bash
python3 scripts/verify_lsp_contract.py --report evidence/lsp-contract/receiver-report.json
cargo fmt --all -- --check
cargo check --all-targets
cargo clippy --all-targets -- -D warnings
cargo test --all-targets
```

Then execute a real stdio replay covering lifecycle, diagnostics, hierarchy, and close cleanup twice and compare semantic receipts.

## Standing

The independent source-contract rail may be `ALIVE` when its verifier executes with zero findings. The Rust runtime remains `BLOCKED:TOOLCHAIN_UNAVAILABLE` until the exact candidate compiles, executes, and replays locally.
