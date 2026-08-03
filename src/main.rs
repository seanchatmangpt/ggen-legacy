#![deny(clippy::print_stdout)]

use ggen_legacy_lsp::GgenLanguageServer;
use lsp_max::{LspService, Server};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .init();

    let (service, socket) = LspService::new(GgenLanguageServer::new);
    Server::new(tokio::io::stdin(), tokio::io::stdout(), socket)
        .serve(service)
        .await?;
    Ok(())
}
