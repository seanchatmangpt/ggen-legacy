set shell := ["bash", "-euo", "pipefail", "-c"]

# Root ggen-legacy-lsp workspace ladder — mirrors
# .github/workflows/gl-lsp-001-runtime.yml step for step (fmt, check,
# clippy, test), minus the receipt bookkeeping and toolchain install.
fmt:
    cargo fmt --all -- --check

check:
    cargo check --all-targets --locked

clippy:
    cargo clippy --all-targets --locked -- -D warnings

test:
    cargo test --all-targets --locked -- --test-threads=1

ci: fmt check clippy test

# tools/v26.8.1 is a separate Cargo workspace; delegate to its own justfile.
v26-fmt:
    just -f tools/v26.8.1/justfile fmt

v26-check:
    just -f tools/v26.8.1/justfile check

v26-clippy:
    just -f tools/v26.8.1/justfile clippy

v26-test:
    cargo test --manifest-path tools/v26.8.1/Cargo.toml --all-targets --locked -- --test-threads=1

v26-ci: v26-fmt v26-check v26-clippy v26-test

# Run the full ladder for both workspaces — the single local command a new
# engineer can run to reproduce what CI gates before opening a PR.
ci-all: ci v26-ci

# GL-PLAN-002 is a concurrent, dependency-free planning verifier. It is not added
# to ci-all because that target mirrors the pre-existing GL-LSP-001 workspace ladder.
planning-max:
    python3 planning/v26.8.7/verify.py --strict
