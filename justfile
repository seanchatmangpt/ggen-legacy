set shell := ["bash", "-euo", "pipefail", "-c"]

# Root ggen-legacy-lsp workspace ladder — mirrors
# .github/workflows/ci.yml step for step (fmt, check,
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

# GL-ERRC-022: optional, suggestion-only wiring for the real
# tools/dsrust-disposition-proposer crate's `propose-disposition` binary. Not part
# of `ci`/`ci-all`/`v26-ci` and not invoked from any workflow -- a human runs this
# by hand and reviews the proposal; it never writes to CATALOG, draft-candidates.json,
# or any admission-workflow state, and it does not change any existing recipe.
# Requires GROQ_API_KEY in the environment for a real proposal (not needed for --help).
propose-disposition *ARGS:
    cargo run --manifest-path tools/dsrust-disposition-proposer/Cargo.toml --bin propose-disposition -- {{ARGS}}

# GL-EXP-048: optional, suggestion-only self-check of this repo's own
# v26.8.3 PRD/ARD authority bundle. Not part of ci/ci-all/v26-ci.
verify-prd-ard:
    python3 verifiers/verify_ggen_v26_8_3.py --subject-root . \
      --expected-repository seanchatmangpt/ggen-legacy \
      --expected-role EXECUTABLE_ARCHITECTURE_CORPUS

# v26.11.9: structure and anti-overclaim check of the srve switch-over ticket set, with a
# non-vacuity selftest. Add --check-fresh to flag manifests older than their source repos.
# Not part of ci/ci-all/v26-ci.
verify-v26-11-9:
    python3 scripts/verify_v26_11_9.py --selftest
    python3 -m unittest scripts/tests/test_v26_11_9.py

# v26.11.9: refresh the SHA-pinned manifests and run the read-only cutover dry-run (needs the
# ggen-create entry point). Exit 0 only for a READY verdict.
v26-11-9-dryrun:
    scripts/dryrun/refresh_and_run.sh

# GL-EXP-044: optional, suggestion-only wiring for the real, already-passing
# Verifier Appliance reference regression harness. Not part of ci/ci-all/v26-ci
# and not invoked from any workflow -- a pure pass-through, no reimplementation
# of the script's own logic, and it does not change any existing recipe.
reference-e2e:
    bash appliance/bin/run-reference-e2e.sh
