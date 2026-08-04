use ggen_legacy_lsp::{analyze_document, capabilities::server_capabilities};
use lsp_max::lsp_types_max::{NumberOrString, Url};

#[test]
fn invalid_toml_is_refused() {
    let uri: Url = "file:///tmp/ggen.toml".parse().expect("valid URI");
    let diagnostics = analyze_document(&uri, "[project\nname = 'demo'");
    assert!(diagnostics.iter().any(|diagnostic| {
        matches!(
            diagnostic.code.as_ref(),
            Some(NumberOrString::String(code)) if code == "GGEN-TOML-001"
        )
    }));
}

#[test]
fn undeclared_turtle_prefix_is_reported() {
    let uri: Url = "file:///tmp/model.ttl".parse().expect("valid URI");
    let diagnostics = analyze_document(&uri, "ex:item a missing:Type .\n");
    assert_eq!(diagnostics.len(), 2);
}

#[test]
fn advertised_capabilities_are_implemented() {
    let capabilities = server_capabilities();
    assert!(capabilities.completion_provider.is_some());
    assert!(capabilities.hover_provider.is_some());
    assert!(capabilities.document_symbol_provider.is_some());
    assert!(capabilities.document_formatting_provider.is_some());
    assert!(capabilities.code_action_provider.is_some());
}
