use lsp_max::lsp_types_max::{Diagnostic, DiagnosticSeverity, NumberOrString, Position, Range, Url};
use regex::Regex;
use std::collections::HashSet;

fn offset_position(text: &str, offset: usize) -> Position {
    let prefix = &text[..offset.min(text.len())];
    let line = prefix.bytes().filter(|byte| *byte == b'\n').count() as u32;
    let character = prefix
        .rsplit_once('\n')
        .map_or(prefix.chars().count(), |(_, tail)| tail.chars().count()) as u32;
    Position::new(line, character)
}

fn diagnostic(
    text: &str,
    start: usize,
    end: usize,
    code: &str,
    message: impl Into<String>,
) -> Diagnostic {
    Diagnostic {
        range: Range::new(offset_position(text, start), offset_position(text, end)),
        severity: Some(DiagnosticSeverity::ERROR),
        code: Some(NumberOrString::String(code.to_owned())),
        source: Some("ggen-lsp".to_owned()),
        message: message.into(),
        ..Default::default()
    }
}

fn analyze_toml(uri: &Url, text: &str) -> Vec<Diagnostic> {
    match toml::from_str::<toml::Value>(text) {
        Ok(value) => {
            if uri.path().ends_with("/ggen.toml") && value.get("project").is_none() {
                vec![diagnostic(
                    text,
                    0,
                    text.len().min(1),
                    "GGEN-MANIFEST-001",
                    "ggen.toml requires a [project] table",
                )]
            } else {
                Vec::new()
            }
        }
        Err(error) => vec![diagnostic(
            text,
            0,
            text.len().min(1),
            "GGEN-TOML-001",
            format!("TOML parse refusal: {error}"),
        )],
    }
}

fn analyze_turtle(text: &str) -> Vec<Diagnostic> {
    let declaration = Regex::new(
        r"(?im)^\s*(?:@prefix|prefix)\s+([A-Za-z][\w-]*):",
    )
    .expect("static regex");
    let use_pattern = Regex::new(
        r"(?m)([A-Za-z][\w-]*):([A-Za-z_][\w.-]*)",
    )
    .expect("static regex");
    let mut declared: HashSet<String> = declaration
        .captures_iter(text)
        .filter_map(|captures| captures.get(1).map(|item| item.as_str().to_owned()))
        .collect();
    declared.extend(
        [
            "rdf", "rdfs", "xsd", "owl", "sh", "dcterms", "prov", "skos", "foaf",
            "dcat", "odrl", "sosa", "qudt",
        ]
        .into_iter()
        .map(str::to_owned),
    );

    let mut seen = HashSet::new();
    use_pattern
        .captures_iter(text)
        .filter_map(|captures| {
            let prefix = captures.get(1)?;
            let name = prefix.as_str();
            if declared.contains(name) || !seen.insert(name.to_owned()) {
                return None;
            }
            Some(diagnostic(
                text,
                prefix.start(),
                prefix.end(),
                "GGEN-TTL-001",
                format!("Prefix {name:?} is used but not declared"),
            ))
        })
        .collect()
}

fn analyze_tera(text: &str) -> Vec<Diagnostic> {
    [
        ("{{", "}}", "expression"),
        ("{%", "%}", "statement"),
        ("{#", "#}", "comment"),
    ]
    .into_iter()
    .filter_map(|(open, close, name)| {
        let start = text.find(open)?;
        if text[start + open.len()..].contains(close) {
            None
        } else {
            Some(diagnostic(
                text,
                start,
                start + open.len(),
                "GGEN-TERA-001",
                format!("Unclosed Tera {name}; expected {close:?}"),
            ))
        }
    })
    .collect()
}

pub fn analyze_document(uri: &Url, text: &str) -> Vec<Diagnostic> {
    match uri.path().rsplit_once('.').map(|(_, extension)| extension) {
        Some("toml") => analyze_toml(uri, text),
        Some("ttl" | "rdf" | "n3") => analyze_turtle(text),
        Some("tera" | "tmpl" | "j2" | "jinja" | "jinja2") => analyze_tera(text),
        _ => Vec::new(),
    }
}
