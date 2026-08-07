//! `ggen-verifier-cli-verify` — committed, real cross-repo consumer of
//! `chicago-tdd-tools-pack` (from the separate `~/ggen` checkout).
//!
//! This consumer targets `ggen-legacy`'s own `tools/v26.8.1` real CLI
//! binary, `ggen-v26-8-1-verifier`: the ontology in `schema/domain.ttl`
//! describes `ctt:CliBoundaryTest` individuals whose `ctt:binary` is
//! `"ggen-v26-8-1-verifier"`. `ggen sync run` renders
//! `tests/chicago_tdd_tools_boundary.rs`, which spawns the real compiled
//! `ggen-v26-8-1-verifier` binary via
//! `chicago_tdd_tools::cli_proof::CliHarness` and asserts on its actual
//! exit codes and stdout/stderr. No mocks, no stubs.
//!
//! This crate carries no library logic of its own — it exists only to give
//! the generated tests a home and a dev-dependency on `chicago-tdd-tools`.
