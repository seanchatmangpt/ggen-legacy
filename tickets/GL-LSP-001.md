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

The independent source-contract rail is `ALIVE`: `scripts/verify_lsp_contract.py` executes with zero findings (`evidence/lsp-contract/receiver-report.json`).

The Rust runtime is `PARTIAL_ALIVE`, not `BLOCKED:TOOLCHAIN_UNAVAILABLE`. As of 2026-08-03:

- `rust-toolchain.toml` is pinned to `nightly-2026-06-22` (was `1.82.0`; that pin could not even parse the pinned `lsp-max` manifest, which declares `resolver = "3"`, gated behind Cargo's `edition2024` feature and requiring Cargo ≥1.85 -- see repair note below). `nightly-2026-06-22` is the same pin the producing `ggen` repository already uses for the same reason (`wasm4pm-compat`'s `#![feature(...)]` gates), so this keeps the two repositories consistent.
- `lsp-max` is pinned to `c1cab89bf54fcc9100b3ce75580b3cc3aa8eb852` on branch `fix/wasm4pm-lsp-example-crates-io-dep`, **not yet merged** (draft PR `seanchatmangpt/lsp-max#22`). The originally-admitted rev `220d3251e959f6a58ce0311e995b31a85f98240c` has three independent local-machine-path leaks (an example's dependency escaping the repo via `../../../wasm4pm/...`, a workspace `[patch.crates-io]` table pointing at sibling directories, and an orphaned unreferenced duplicate example with its own broken path) that make cargo unable to enumerate `lsp-max` as a package for any external consumer at all -- this is why `cargo check` previously failed with `no matching package named 'lsp-max' found` regardless of toolchain. This pin is provisional pending PR #22 review/merge; per this file's own "Generated contract ownership" and "No self-certification" invariants, merging is not self-authorized here.
- `cargo fmt --all -- --check`, `cargo check --all-targets`, `cargo clippy --all-targets -- -D warnings`, and `cargo test --all-targets` all exit 0 (3 real receiver-side bugs fixed along the way: two `fluent_uri::Path` API mismatches in `src/analysis.rs`/`src/backend.rs` where `.path()` needed `.as_str()` first; one invalid regex in `src/backend.rs`'s `symbols()` that would have panicked at runtime, `r"{%..."` missing the required `\{` escape; one broken `DocumentUri::parse` call in `tests/analysis.rs`, fixed to use `.parse()` via `FromStr`).
- A real stdio replay (`evidence/lsp-contract/stdio-replay-2026-08-03.json`) executed the full `initialize -> initialized -> didOpen -> didChange -> prepareTypeHierarchy -> didClose -> shutdown -> exit` sequence twice against the built binary. Diagnostics, capability advertisement, and hierarchy responses are correct and byte-identical across both runs. **Not yet proven:** the process did not exit on its own within 5s of the `exit` notification + stdin close in either run (observed SIGKILL, exit code -9) -- root cause not yet found; tracked separately. Until that's resolved, "compiles, executes, and replays locally" is satisfied for the request/response/notification surface but not for clean process termination, so this rail stops short of unqualified `ALIVE`.
