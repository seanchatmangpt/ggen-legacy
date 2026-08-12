set shell := ["bash", "-euo", "pipefail", "-c"]

# Root ggen-legacy-lsp workspace ladder.
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

# GL-PLAN-002: bounded combinatorial-max planning replay.
planning-max:
    python3 -m unittest discover -s planning/v26.8.7/tests -v
    python3 planning/v26.8.7/verify.py --strict
    planning/v26.8.7/skdecide_classical_engine.py --help | head -n 1 | grep '^skdecide-classical-engine/26.8.7$'

# GL-ERRC-003: self-reconstitute the complete Fortune-5 decision surface,
# replay it independently, and kill topology/cardinality mutants.
fortune5-reconstitute:
    rm -rf /tmp/ggen-legacy-fortune5-reconstitution
    python3 scripts/reconstitute_fortune5.py --root . --output /tmp/ggen-legacy-fortune5-reconstitution --strict
    python3 scripts/verify_fortune5_reconstitution.py --root .

# One local crown matching the single hosted exact-subject court.
ci-all: fortune5-reconstitute planning-max ci v26-ci
