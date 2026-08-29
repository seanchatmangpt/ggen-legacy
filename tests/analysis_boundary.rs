//! Chicago-TDD boundary tests for `analyze_document`: real files on disk, not
//! inline string literals. `analyze_document` itself takes a `&str`, so the
//! boundary crossed here is real file I/O — a `TempWorkspace`-backed file is
//! written, then read back from disk exactly as an editor/LSP client would
//! read a document off the filesystem before sending its contents over.

use chicago_tdd_tools::cli_proof::TempWorkspace;
use ggen_legacy_lsp::analyze_document;
use lsp_max::lsp_types_max::{NumberOrString, Url};

fn read_fixture_and_analyze(
    rel_path: &str, content: &str,
) -> (Url, Vec<lsp_max::lsp_types_max::Diagnostic>) {
    let ws = TempWorkspace::new().expect("temp workspace");
    ws.write_file(rel_path, content)
        .expect("write real fixture file");

    let path = ws.resolve(rel_path);
    let uri: Url = url::Url::from_file_path(&path)
        .expect("file URL")
        .to_string()
        .parse()
        .expect("LSP URI");
    let text_from_disk =
        std::fs::read_to_string(&path).expect("read real fixture file back from disk");

    let diagnostics = analyze_document(&uri, &text_from_disk);
    (uri, diagnostics)
}

#[test]
fn malformed_toml_on_disk_is_diagnosed() {
    let (_uri, diagnostics) = read_fixture_and_analyze("ggen.toml", "[project\nname = 'demo'");

    assert!(
        diagnostics.iter().any(|d| matches!(
            d.code.as_ref(),
            Some(NumberOrString::String(code)) if code == "GGEN-TOML-001"
        )),
        "expected GGEN-TOML-001 diagnostic for malformed TOML read from a real file, got: {diagnostics:?}"
    );
}

#[test]
fn undeclared_turtle_prefix_on_disk_is_diagnosed() {
    let (_uri, diagnostics) = read_fixture_and_analyze("model.ttl", "ex:item a missing:Type .\n");

    assert_eq!(
        diagnostics.len(),
        2,
        "expected 2 diagnostics for undeclared prefixes read from a real file, got: {diagnostics:?}"
    );
}

#[test]
fn valid_toml_on_disk_has_no_toml_diagnostics() {
    let (_uri, diagnostics) = read_fixture_and_analyze("ggen.toml", "[project]\nname = \"demo\"\n");

    assert!(
        !diagnostics.iter().any(|d| matches!(
            d.code.as_ref(),
            Some(NumberOrString::String(code)) if code == "GGEN-TOML-001"
        )),
        "well-formed TOML read from a real file should not raise GGEN-TOML-001, got: {diagnostics:?}"
    );
}
