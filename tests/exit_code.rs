//! Asserts the compiled `ggen-lsp` binary exits with a lawful status code
//! after a real `initialize -> initialized -> shutdown -> exit` sequence.
//!
//! `lsp-max`'s `Server::serve` signals a *lawful* shutdown via
//! `Err(ExitedError(0))`, not `Ok(())`. Prior to the fix this test guards,
//! `src/main.rs` `?`-propagated that `Err` unconditionally, and
//! `#[tokio::main]`'s default `Termination` impl turned every `Err` --
//! including a lawful one -- into exit code 1. This was previously proven
//! only by a hand-run replay (`evidence/lsp-contract/stdio-replay-*.json`);
//! this test turns it into a standing `cargo test` gate.

use std::io::{BufRead, BufReader, Write};
use std::process::{Command, Stdio};

fn write_message(stdin: &mut impl Write, body: &serde_json::Value) {
    let body = serde_json::to_vec(body).expect("serialize LSP message");
    write!(stdin, "Content-Length: {}\r\n\r\n", body.len()).expect("write header");
    stdin.write_all(&body).expect("write body");
    stdin.flush().expect("flush stdin");
}

fn read_message(reader: &mut impl BufRead) -> serde_json::Value {
    let mut content_length = 0usize;
    loop {
        let mut line = String::new();
        reader.read_line(&mut line).expect("read header line");
        let trimmed = line.trim_end();
        if trimmed.is_empty() {
            break;
        }
        if let Some(value) = trimmed.strip_prefix("Content-Length: ") {
            content_length = value.parse().expect("parse Content-Length");
        }
    }
    let mut body = vec![0u8; content_length];
    reader.read_exact(&mut body).expect("read message body");
    serde_json::from_slice(&body).expect("parse LSP message JSON")
}

/// Reads messages until it finds the response with `target_id`, auto-answering
/// any server-initiated request encountered along the way (e.g.
/// `client/registerCapability`, sent during `initialized` for dynamic
/// type-hierarchy registration) -- a real LSP client must answer these, or a
/// server-side task awaiting the response never resolves. An earlier version
/// of this repo's own manual stdio replay got this wrong and misreported a
/// real bug (see evidence/lsp-contract/stdio-replay-2026-08-03.json).
fn read_until_response(
    reader: &mut impl BufRead, stdin: &mut impl Write, target_id: i64,
) -> serde_json::Value {
    loop {
        let message = read_message(reader);
        let has_method = message.get("method").is_some();
        let id = message.get("id").cloned();

        if !has_method && id == Some(serde_json::json!(target_id)) {
            return message;
        }

        if has_method {
            if let Some(id) = id {
                write_message(
                    stdin,
                    &serde_json::json!({ "jsonrpc": "2.0", "id": id, "result": null }),
                );
            }
        }
    }
}

#[test]
fn exits_lawfully_after_shutdown_and_exit() {
    let mut child = Command::new(env!("CARGO_BIN_EXE_ggen-lsp"))
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn ggen-lsp");

    let mut stdin = child.stdin.take().expect("child stdin");
    let mut stdout = BufReader::new(child.stdout.take().expect("child stdout"));

    write_message(
        &mut stdin,
        &serde_json::json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": { "processId": null, "rootUri": null, "capabilities": {} },
        }),
    );
    let initialize_response = read_until_response(&mut stdout, &mut stdin, 1);
    assert_eq!(
        initialize_response["id"], 1,
        "expected the initialize response"
    );

    write_message(
        &mut stdin,
        &serde_json::json!({ "jsonrpc": "2.0", "method": "initialized", "params": {} }),
    );

    write_message(
        &mut stdin,
        &serde_json::json!({ "jsonrpc": "2.0", "id": 2, "method": "shutdown", "params": null }),
    );
    let shutdown_response = read_until_response(&mut stdout, &mut stdin, 2);
    assert_eq!(shutdown_response["id"], 2, "expected the shutdown response");

    write_message(
        &mut stdin,
        &serde_json::json!({ "jsonrpc": "2.0", "method": "exit", "params": null }),
    );
    drop(stdin); // close stdin, matching a real client disconnecting

    let status = child
        .wait_timeout_ms(5_000)
        .expect("ggen-lsp exited within 5s of shutdown+exit+stdin-close");

    assert!(
        status.success(),
        "expected exit code 0 after a lawful shutdown, got: {status:?}"
    );
}

/// `std::process::Child` has no built-in timed wait; poll with a short
/// sleep instead of pulling in a dependency just for this one test.
trait WaitTimeout {
    fn wait_timeout_ms(&mut self, timeout_ms: u64) -> Option<std::process::ExitStatus>;
}

impl WaitTimeout for std::process::Child {
    fn wait_timeout_ms(&mut self, timeout_ms: u64) -> Option<std::process::ExitStatus> {
        let deadline = std::time::Instant::now() + std::time::Duration::from_millis(timeout_ms);
        loop {
            if let Ok(Some(status)) = self.try_wait() {
                return Some(status);
            }
            if std::time::Instant::now() >= deadline {
                let _ = self.kill();
                let _ = self.wait();
                return None;
            }
            std::thread::sleep(std::time::Duration::from_millis(25));
        }
    }
}
