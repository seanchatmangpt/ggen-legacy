#![deny(clippy::print_stdout)]

use ggen_legacy_lsp::GgenLanguageServer;
use lsp_max::{ExitedError, LspService, Server};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .init();

    let (service, socket) = LspService::new(GgenLanguageServer::new);
    let result = Server::new(tokio::io::stdin(), tokio::io::stdout(), socket)
        .serve(service)
        .await;

    // `serve` signals process exit through `Err(ExitedError(code))` even on a
    // lawful shutdown (code 0) -- it is not a generic failure to be
    // `?`-propagated as one. Translate the intended exit code directly
    // rather than letting `#[tokio::main]`'s default `Termination` impl turn
    // every `Err`, including a lawful `ExitedError(0)`, into exit code 1.
    match result {
        Ok(()) => Ok(()),
        Err(ExitedError(code)) => std::process::exit(code),
    }
}
