#![deny(clippy::print_stdout)]

pub mod analysis;
pub mod backend;
pub mod capabilities;
pub mod generated_contract;\npub mod legacy_engines;

pub use analysis::analyze_document;
pub use backend::GgenLanguageServer;
