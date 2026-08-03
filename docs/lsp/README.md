# ggen-legacy LSP contract receiver

This repository is the independent executable receiver for the LSP contract manufactured by ggen from `self-host/lsp-contract/ontology.ttl`.

## Authority chain

```text
ggen ontology
→ self-host/lsp-contract/ggen.toml
→ ggen-generated JSON, Rust, and Markdown projections
→ ggen-legacy received contract
→ Rust runtime on lsp-max
→ independent receiver verifier
→ local runtime replay
```

The received projections are:

- `authority/lsp-contract.json`
- `src/generated_contract.rs`
- `docs/lsp/CONTRACT.md`

They are generated surfaces. Edit the ggen ontology/templates, not these files.

## Exact protocol dependency

```text
repository: seanchatmangpt/lsp-max
commit:     220d3251e959f6a58ce0311e995b31a85f98240c
```

## Implemented source contract

- 29 required LSP methods;
- full synchronization;
- completion, hover, navigation, rename, symbols, formatting, quick fixes, folding, semantic tokens, inlay hints, and code lenses;
- call and type hierarchy prepare/follow-up requests;
- `.ttl`, `.nt`, `.nq`, `.rq`, `.sparql`, `.tera`, `.toml`, and generated `.rs` analysis;
- generated Rust module-ownership law `GGEN-SRC-004`;
- frame-pure stdout and no ambient actuation.

Type hierarchy is dynamically registered because the pinned protocol types do not expose a static server-capability field.

## Verify

```bash
python3 scripts/verify_lsp_contract.py --report evidence/lsp-contract/receiver-report.json
cargo fmt --all -- --check
cargo check --all-targets
cargo clippy --all-targets -- -D warnings
cargo test --all-targets
cargo run --bin ggen-lsp
```

The Python verifier proves received representation and source-contract alignment only. Runtime `ALIVE` requires the Rust commands and real stdio replay to execute locally.
