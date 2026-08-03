use ggen_legacy_lsp::{
    analyze_document,
    generated_contract::{
        CONTRACT_SCHEMA, CONTRACT_VERSION, DECLARED_DIAGNOSTICS, REQUIRED_METHODS,
        REQUIRED_SURFACES,
    },
};
use lsp_max::lsp_types_max::{NumberOrString, Url};
use serde_json::Value;
use std::{fs, path::PathBuf};

fn diagnostic_codes(uri: &Url, source: &str) -> Vec<String> {
    analyze_document(uri, source)
        .into_iter()
        .filter_map(|diagnostic| match diagnostic.code {
            Some(NumberOrString::String(code)) => Some(code),
            _ => None,
        })
        .collect()
}

fn file_uri(path: &std::path::Path) -> Url {
    let url = url::Url::from_file_path(path).expect("file URL");
    url.to_string().parse().expect("LSP URI")
}

#[test]
fn received_json_matches_generated_rust_contract() {
    let authority: Value = serde_json::from_str(include_str!("../authority/lsp-contract.json"))
        .expect("contract JSON");
    assert_eq!(authority["schema"], CONTRACT_SCHEMA);
    assert_eq!(authority["version"], CONTRACT_VERSION);

    let methods = authority["methods"]
        .as_array()
        .expect("methods")
        .iter()
        .map(|row| row["method"].as_str().expect("method"))
        .collect::<Vec<_>>();
    let surfaces = authority["surfaces"]
        .as_array()
        .expect("surfaces")
        .iter()
        .map(|row| row["extension"].as_str().expect("extension"))
        .collect::<Vec<_>>();
    let diagnostics = authority["diagnostics"]
        .as_array()
        .expect("diagnostics")
        .iter()
        .map(|row| row["code"].as_str().expect("code"))
        .collect::<Vec<_>>();

    assert_eq!(methods, REQUIRED_METHODS);
    assert_eq!(surfaces, REQUIRED_SURFACES);
    assert_eq!(diagnostics, DECLARED_DIAGNOSTICS);
}

#[test]
fn required_analysis_surfaces_emit_typed_diagnostics() {
    let cases = [
        ("file:///contract/ggen.toml", "ontology = {}", "GGEN-MANIFEST-001"),
        ("file:///contract/model.ttl", "missing:Thing a missing:Type .", "GGEN-TTL-001"),
        ("file:///contract/model.nt", "<urn:s> <urn:p> <urn:o>", "GGEN-RDF-001"),
        ("file:///contract/model.nq", "<urn:s> <urn:p> <urn:o> <urn:g>", "GGEN-RDF-001"),
        ("file:///contract/query.rq", "SELECT * WHERE {", "GGEN-SPARQL-001"),
        ("file:///contract/query.sparql", "not a query", "GGEN-SPARQL-001"),
        ("file:///contract/view.tera", "{{ value", "GGEN-TERA-001"),
    ];
    for (uri, source, expected) in cases {
        let uri: Url = uri.parse().expect("URI");
        assert!(diagnostic_codes(&uri, source).contains(&expected.to_owned()));
    }
}

#[test]
fn generated_rust_requires_generation_rule_ownership() {
    let root: PathBuf = std::env::temp_dir().join(format!(
        "ggen-legacy-contract-{}",
        std::process::id()
    ));
    let _ = fs::remove_dir_all(&root);
    fs::create_dir_all(root.join("src")).expect("fixture directory");
    fs::write(
        root.join("ggen.toml"),
        "[project]\nname = \"fixture\"\n\n[generation]\noutput_dir = \".\"\n\n[[generation.rules]]\nname = \"lib\"\noutput_file = \"src/lib.rs\"\nquery = { inline = \"SELECT * WHERE { ?s ?p ?o }\" }\ntemplate = { inline = \"x\" }\n",
    )
    .expect("manifest");
    let source_path = root.join("src/lib.rs");
    fs::write(&source_path, "pub mod missing;\n").expect("source");
    let codes = diagnostic_codes(&file_uri(&source_path), "pub mod missing;\n");
    assert!(codes.contains(&"GGEN-SRC-004".to_owned()));
    fs::remove_dir_all(root).expect("fixture cleanup");
}
