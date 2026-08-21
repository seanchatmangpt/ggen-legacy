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

#[test]
fn turtle_prefixes_inside_comments_are_not_reported() {
    let uri: Url = "file:///tmp/model.ttl".parse().expect("valid URI");
    let diagnostics = analyze_document(
        &uri,
        "@prefix ex: <http://example.org/> .\n# see acme:Thing for details\nex:a a ex:B .\n",
    );
    assert!(
        diagnostics.is_empty(),
        "a prefixed name inside a Turtle comment is not a prefix use, got: {diagnostics:?}"
    );
}

#[test]
fn turtle_prefixes_inside_string_literals_are_not_reported() {
    let uri: Url = "file:///tmp/model.ttl".parse().expect("valid URI");
    let diagnostics = analyze_document(
        &uri,
        "@prefix ex: <http://example.org/> .\nex:a ex:label \"contact bob:smith today\" .\nex:a ex:note '''block foo:bar text''' .\n",
    );
    assert!(
        diagnostics.is_empty(),
        "a prefixed name inside a Turtle string literal is not a prefix use, got: {diagnostics:?}"
    );
}

#[test]
fn turtle_prefixes_inside_iri_references_are_not_reported() {
    let uri: Url = "file:///tmp/model.ttl".parse().expect("valid URI");
    let diagnostics = analyze_document(
        &uri,
        "@prefix ex: <http://example.org/> .\nex:a <urn:example:thing> ex:b .\n",
    );
    assert!(
        diagnostics.is_empty(),
        "a colon inside an absolute IRI reference is not a prefix use, got: {diagnostics:?}"
    );
}

#[test]
fn genuinely_undeclared_prefix_still_reported_at_correct_offset() {
    let uri: Url = "file:///tmp/model.ttl".parse().expect("valid URI");
    let text = "@prefix ex: <http://example.org/> .\n# comment acme:Thing\nex:a a missing:Type .\n";
    let diagnostics = analyze_document(&uri, text);
    assert_eq!(
        diagnostics.len(),
        1,
        "only the real undeclared prefix should be reported, got: {diagnostics:?}"
    );
    assert_eq!(
        diagnostics[0].message,
        "Prefix \"missing\" is used but not declared"
    );
    // Masking preserves byte offsets, so the range must point at `missing`
    // on the third line (zero-based line 2), columns 7..14.
    assert_eq!(diagnostics[0].range.start.line, 2);
    assert_eq!(diagnostics[0].range.start.character, 7);
    assert_eq!(diagnostics[0].range.end.character, 14);
}
