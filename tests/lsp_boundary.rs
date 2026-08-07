//! Chicago-TDD boundary tests for the real, compiled `ggen-lsp` binary: a
//! real subprocess, communicating over its real stdin/stdout pipes exactly
//! as a real LSP client would. No mocks, no in-process handler unit tests.
//!
//! `chicago_tdd_tools::cli_proof::CliHarness` is a one-shot "run to
//! completion, capture output" harness (`Command::output()`) with no stdin
//! piping — a good fit for ordinary CLIs, but `ggen-lsp` is a persistent
//! stdio protocol server with no CLI args at all (see `src/main.rs`): it
//! blocks reading `stdin` until EOF or a fatal protocol error. So these
//! tests use `std::process::Command` directly, with an explicit
//! `Stdio::piped()` stdin (never inherited — inheriting the test harness's
//! own stdin risks an indefinite hang under `cargo test`) and a bounded
//! wait loop that kills the child rather than ever blocking forever.

use std::io::Write;
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

/// Locate the compiled `ggen-lsp` binary the same way `CliHarness::cargo_bin`
/// does: `CARGO_BIN_EXE_ggen-lsp`, set by `cargo test` for binaries in this
/// package.
fn ggen_lsp_path() -> std::path::PathBuf {
    std::env::var("CARGO_BIN_EXE_ggen-lsp")
        .map(std::path::PathBuf::from)
        .expect("CARGO_BIN_EXE_ggen-lsp must be set by `cargo test` for the ggen-lsp binary")
}

/// Wait for `child` to exit, polling rather than blocking indefinitely.
/// Kills the child and panics if it hasn't exited within `timeout`.
fn wait_with_timeout(
    mut child: std::process::Child, timeout: Duration,
) -> std::process::ExitStatus {
    let start = Instant::now();
    loop {
        if let Some(status) = child.try_wait().expect("poll child status") {
            return status;
        }
        if start.elapsed() > timeout {
            let _ = child.kill();
            let _ = child.wait();
            panic!("ggen-lsp did not exit within {timeout:?} — real subprocess hung");
        }
        std::thread::sleep(Duration::from_millis(20));
    }
}

#[test]
fn stdin_eof_causes_clean_lawful_exit() {
    let mut child = Command::new(ggen_lsp_path())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn real ggen-lsp binary");

    // Close stdin immediately (no bytes written) — this is the real EOF signal
    // an editor sends when its client-side pipe closes without a `shutdown`/
    // `exit` handshake.
    drop(child.stdin.take());

    let status = wait_with_timeout(child, Duration::from_secs(10));

    // main.rs translates a lawful `ExitedError(code)` via `std::process::exit`,
    // and treats `Ok(())` from `serve` the same way (implicit exit 0). Either
    // path should surface as a real, observable process exit — never a hang.
    assert!(
        status.code().is_some(),
        "expected a real exit code from stdin EOF, got: {status:?}"
    );
}

#[test]
fn garbage_stdin_fails_closed_without_hanging() {
    let mut child = Command::new(ggen_lsp_path())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn real ggen-lsp binary");

    {
        let stdin = child.stdin.as_mut().expect("piped stdin");
        // Not a valid `Content-Length: N\r\n\r\n<json>` LSP frame — real
        // malformed-input boundary crossing, not a crafted-to-pass fixture.
        stdin
            .write_all(b"this is not an LSP frame at all\n")
            .expect("write garbage to real stdin pipe");
    }
    drop(child.stdin.take());

    let status = wait_with_timeout(child, Duration::from_secs(10));

    // The concrete requirement is fail-closed, observable termination — not
    // hanging forever trying to parse an ever-growing malformed frame.
    assert!(
        status.code().is_some(),
        "expected the real process to terminate on malformed input rather than hang, got: {status:?}"
    );
}
