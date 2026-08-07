//! Chicago-TDD boundary tests for the three real, compiled v26.8.1 binaries:
//! `ggen-v26-8-1-verifier`, `subsystem_verifier`, `project_coverage`. Each
//! spawns the real subprocess via `CliHarness` and asserts on its actual
//! exit code/stderr — no mocks. Extends the existing pattern already proven
//! in the sibling `tools/ggen-verifier-cli-verify` crate (which exercises
//! `ggen-v26-8-1-verifier` against this repo's own real root) to also cover
//! `subsystem_verifier` and `project_coverage`, and to exercise root
//! resolution against a real, hermetic `TempWorkspace` rather than only the
//! live checkout.

use chicago_tdd_tools::cli_proof::{CliHarness, TempWorkspace};

/// All three binaries share the same `resolve_root` walk-up-for-AGENTS.md
/// logic (see `src/coverage_projection.rs::resolve_root` and the copies in
/// each `src/bin/*.rs`), and the same `eprintln!("<name> refused: {error:#}");
/// std::process::exit(2);` error wrapper in `main()`. A root with no
/// `AGENTS.md` anywhere in its ancestry must fail closed identically across
/// all three.
#[test]
fn all_three_binaries_fail_closed_on_missing_root() {
    for binary in [
        "ggen-v26-8-1-verifier",
        "subsystem_verifier",
        "project_coverage",
    ] {
        let output = CliHarness::cargo_bin(binary)
            .args([
                "--root",
                "/tmp/definitely-not-a-repo-for-chicago-tdd-boundary-test",
            ])
            .run()
            .unwrap_or_else(|e| panic!("{binary}: CliHarness run failed: {e}"));

        output
            .assert_exit_code(2)
            .assert_stderr_contains("repository root not found; pass --root <path>");
        assert!(
            output.stderr.starts_with(binary) || output.stderr.contains("refused:"),
            "{binary}: expected the real \"<name> refused: ...\" wrapper on stderr, got:\n{}",
            output.stderr
        );
    }
}

/// A real `TempWorkspace` with a real `AGENTS.md` file lets `resolve_root`
/// succeed — proving the real, positive branch of root resolution against
/// an actual file on disk, not just its negative-path sibling above. Each
/// binary then proceeds past root resolution into its own, later-failing
/// logic (this hermetic workspace has none of the manifest/coverage files
/// each binary goes on to require), which is a *different* real failure
/// than "repository root not found" — proving root resolution itself, not
/// merely that the whole binary always exits 2 regardless of input.
#[test]
fn all_three_binaries_get_past_root_resolution_with_real_agents_md() {
    for binary in [
        "ggen-v26-8-1-verifier",
        "subsystem_verifier",
        "project_coverage",
    ] {
        let ws = TempWorkspace::new().expect("temp workspace");
        ws.write_file("AGENTS.md", "# Chicago-TDD boundary test workspace\n")
            .expect("write real AGENTS.md to disk");

        let root = ws.path().to_str().expect("utf8 temp path").to_owned();
        let output = CliHarness::cargo_bin(binary)
            .args(["--root", &root])
            .run()
            .unwrap_or_else(|e| panic!("{binary}: CliHarness run failed: {e}"));

        output.assert_exit_code(2);
        assert!(
            !output.stderr.contains("repository root not found"),
            "{binary}: a real AGENTS.md on disk should get past root resolution, \
             but it still failed at that step:\n{}",
            output.stderr
        );
    }
}
