# CLI Boundary Proofs (chicago-tdd-tools)

Generated from `ctt:CliBoundaryTest` individuals. Each row is one
Chicago-style `#[test]` in `tests/chicago_tdd_tools_boundary.rs` that
crosses a real binary boundary via `CliHarness` — no mocks.

## Prerequisites

`CliHarness::cargo_bin` resolves each binary below via `CARGO_BIN_EXE_*`,
then this workspace's own `target/{debug,release}/`, then a `PATH` search
(see `chicago_tdd_tools::cli_proof::CliHarness::cargo_bin`). If a binary
below is not a `[[bin]]` target of *this* consumer crate's own workspace,
it must be built and placed on `PATH` before `cargo test` will pass —
derived from `ctt:binary`, not hand-maintained:

- `ggen-v26-8-1-verifier`
- `receiptctl`


| Test | Binary | Args | Exit | Axiom covered |
|------|--------|------|------|---------------|
| `ggen_verifier_bad_root_fails_closed` | `ggen-v26-8-1-verifier` | `--root /tmp/definitely-not-a-repo` | 2 | an explicit --root with no AGENTS.md anywhere up its ancestry still fails closed with repository root not found |
| `ggen_verifier_good_root_gets_past_root_resolution` | `ggen-v26-8-1-verifier` | `--root /Users/sac/ggen-legacy` | 2 | with the resolve_root fix, an explicit correct --root gets past root resolution and fails later on a SEPARATE, still-unfixed bug: observe_workspace's unwrapped read of root/Cargo.toml, which does not exist at ggen-legacy's repo root |
| `receiptctl_help_lists_verbs` | `receiptctl` | `--help` | 0 | receiptctl --help exits 0 with usage text |
| `receiptctl_known_noun_unrecognized_verb_fails_closed` | `receiptctl` | `algorithm frobnicate` | 1 | a known noun with an unrecognized verb exits nonzero with a clap error on stderr, distinct from an entirely-unknown top-level noun |
| `receiptctl_unexpected_flag_fails_closed` | `receiptctl` | `algorithm list --bogus-flag` | 1 | an unrecognized flag on an otherwise-valid command exits nonzero with a clap error on stderr |
| `receiptctl_unknown_verb_fails_closed` | `receiptctl` | `frobnicate` | 1 | an unknown subcommand exits nonzero with a clap error on stderr |
| `receiptctl_version_emits_name` | `receiptctl` | `--version` | 0 | receiptctl --version exits 0 and prints a version string |

