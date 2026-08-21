use crate::generated_contract::GGEN_SRC_004;
use lsp_max::lsp_types_max::{
    Diagnostic, DiagnosticSeverity, NumberOrString, Position, Range, Url,
};
use regex::Regex;
use std::collections::HashSet;
use std::path::{Component, Path, PathBuf};

fn offset_position(text: &str, offset: usize) -> Position {
    let prefix = &text[..offset.min(text.len())];
    let line = prefix.bytes().filter(|byte| *byte == b'\n').count() as u32;
    let character = prefix
        .rsplit_once('\n')
        .map_or(prefix.chars().count(), |(_, tail)| tail.chars().count())
        as u32;
    Position::new(line, character)
}

fn diagnostic(
    text: &str, start: usize, end: usize, code: &str, message: impl Into<String>,
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
            if uri.path().as_str().ends_with("/ggen.toml") && value.get("project").is_none() {
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

/// Blank out Turtle regions in which a `prefix:name` token is not a prefixed
/// name: comments, string literals, and absolute IRI references. The returned
/// string has exactly the same byte length as `text` (masked bytes become
/// ASCII spaces, newlines are preserved), so byte offsets computed against it
/// remain valid offsets into the original document — diagnostic ranges stay
/// correct.
fn mask_turtle_noise(text: &str) -> String {
    let bytes = text.as_bytes();
    let mut out: Vec<u8> = bytes.to_vec();
    let mut index = 0usize;

    // Blank `out[from..to]`, keeping newlines so line/column math is unchanged.
    let blank = |out: &mut Vec<u8>, from: usize, to: usize| {
        for byte in &mut out[from..to.min(bytes.len())] {
            if *byte != b'\n' && *byte != b'\r' {
                *byte = b' ';
            }
        }
    };

    while index < bytes.len() {
        match bytes[index] {
            b'#' => {
                let end = bytes[index..]
                    .iter()
                    .position(|byte| *byte == b'\n')
                    .map_or(bytes.len(), |offset| index + offset);
                blank(&mut out, index, end);
                index = end;
            }
            quote @ (b'"' | b'\'') => {
                let triple = bytes[index..].starts_with(&[quote, quote, quote]);
                let delimiter_len = if triple { 3 } else { 1 };
                let mut cursor = index + delimiter_len;
                let end = loop {
                    if cursor >= bytes.len() {
                        break bytes.len();
                    }
                    if bytes[cursor] == b'\\' {
                        cursor += 2;
                        continue;
                    }
                    if !triple && bytes[cursor] == b'\n' {
                        // An unterminated short literal does not span lines.
                        break cursor;
                    }
                    if bytes[cursor] == quote
                        && (!triple || bytes[cursor..].starts_with(&[quote, quote, quote]))
                    {
                        break cursor + delimiter_len;
                    }
                    cursor += 1;
                };
                blank(&mut out, index, end);
                index = end;
            }
            b'<' => {
                // An IRI reference contains no whitespace and closes on the
                // same line; anything else is a real `<` token (e.g. a filter).
                let close = bytes[index + 1..]
                    .iter()
                    .position(|byte| matches!(byte, b'>' | b'\n' | b' ' | b'\t' | b'\r'))
                    .map(|offset| index + 1 + offset);
                match close {
                    Some(end) if bytes[end] == b'>' => {
                        blank(&mut out, index, end + 1);
                        index = end + 1;
                    }
                    _ => index += 1,
                }
            }
            _ => index += 1,
        }
    }

    String::from_utf8(out).expect("masking replaces whole ASCII bytes only")
}

fn analyze_turtle(text: &str) -> Vec<Diagnostic> {
    let declaration =
        Regex::new(r"(?im)^\s*(?:@prefix|prefix)\s+([A-Za-z][\w-]*):").expect("static regex");
    let use_pattern = Regex::new(r"(?m)([A-Za-z][\w-]*):([A-Za-z_][\w.-]*)").expect("static regex");
    let mut declared: HashSet<String> = declaration
        .captures_iter(text)
        .filter_map(|captures| captures.get(1).map(|item| item.as_str().to_owned()))
        .collect();
    declared.extend(
        [
            "rdf", "rdfs", "xsd", "owl", "sh", "dcterms", "prov", "skos", "foaf", "dcat", "odrl",
            "sosa", "qudt",
        ]
        .into_iter()
        .map(str::to_owned),
    );

    // Prefix *uses* are scanned over a masked copy so that comments, string
    // literals, and IRI references cannot raise GGEN-TTL-001. Declarations are
    // still read from the original text.
    let scannable = mask_turtle_noise(text);
    let mut seen = HashSet::new();
    use_pattern
        .captures_iter(&scannable)
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

fn analyze_rdf_lines(text: &str) -> Vec<Diagnostic> {
    for (index, line) in text.lines().enumerate() {
        let trimmed = line.trim();
        if !trimmed.is_empty() && !trimmed.starts_with('#') && !trimmed.ends_with('.') {
            let start = text
                .lines()
                .take(index)
                .map(|line| line.len() + 1)
                .sum::<usize>();
            return vec![diagnostic(
                text,
                start,
                start + line.len(),
                "GGEN-RDF-001",
                "RDF statement must end with '.'",
            )];
        }
    }
    Vec::new()
}

fn analyze_sparql(text: &str) -> Vec<Diagnostic> {
    let upper = text.to_ascii_uppercase();
    let admitted_form = ["SELECT", "ASK", "CONSTRUCT", "DESCRIBE"]
        .iter()
        .any(|keyword| upper.contains(keyword));
    let balanced = text.matches('{').count() == text.matches('}').count()
        && text.matches('(').count() == text.matches(')').count();
    if admitted_form && balanced {
        Vec::new()
    } else {
        vec![diagnostic(
            text,
            0,
            text.len().min(1),
            "GGEN-SPARQL-001",
            "SPARQL requires an admitted query form and balanced delimiters",
        )]
    }
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

fn normalize(path: &Path) -> PathBuf {
    let mut normalized = PathBuf::new();
    for component in path.components() {
        match component {
            Component::CurDir => {}
            Component::ParentDir => {
                normalized.pop();
            }
            other => normalized.push(other.as_os_str()),
        }
    }
    normalized
}

fn file_path(uri: &Url) -> Option<PathBuf> {
    url::Url::parse(uri.as_str()).ok()?.to_file_path().ok()
}

fn project_root(path: &Path) -> Option<PathBuf> {
    let mut current = path.parent();
    while let Some(candidate) = current {
        if candidate.join("ggen.toml").is_file() {
            return Some(candidate.to_path_buf());
        }
        current = candidate.parent();
    }
    None
}

fn generated_outputs(root: &Path) -> HashSet<PathBuf> {
    let Ok(content) = std::fs::read_to_string(root.join("ggen.toml")) else {
        return HashSet::new();
    };
    let Ok(value) = toml::from_str::<toml::Value>(&content) else {
        return HashSet::new();
    };
    value
        .get("generation")
        .and_then(|generation| generation.get("rules"))
        .and_then(toml::Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|rule| rule.get("output_file").and_then(toml::Value::as_str))
        .filter(|output| {
            !output.contains("{{") && !output.contains("}}") && !output.contains("://")
        })
        .map(|output| normalize(&root.join(output)))
        .collect()
}

fn module_candidates(source: &Path, name: &str) -> [PathBuf; 2] {
    let parent = source.parent().unwrap_or_else(|| Path::new("."));
    let stem = source.file_stem().and_then(|stem| stem.to_str());
    let base = match stem {
        Some("lib" | "main" | "mod") | None => parent.to_path_buf(),
        Some(stem) => parent.join(stem),
    };
    [
        normalize(&base.join(format!("{name}.rs"))),
        normalize(&base.join(name).join("mod.rs")),
    ]
}

fn analyze_generated_rust(uri: &Url, text: &str) -> Vec<Diagnostic> {
    let Some(path) = file_path(uri) else {
        return Vec::new();
    };
    let Some(root) = project_root(&path) else {
        return Vec::new();
    };
    let outputs = generated_outputs(&root);
    let path = normalize(&path);
    if !outputs.contains(&path) {
        return Vec::new();
    }

    let module = Regex::new(r"(?m)^\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+([A-Za-z_][A-Za-z0-9_]*)\s*;")
        .expect("static regex");
    module
        .captures_iter(text)
        .filter_map(|captures| {
            let name = captures.get(1)?;
            if module_candidates(&path, name.as_str())
                .iter()
                .any(|candidate| outputs.contains(candidate))
            {
                return None;
            }
            Some(diagnostic(
                text,
                name.start(),
                name.end(),
                GGEN_SRC_004,
                format!(
                    "Generated source declares module `{}` but no generation rule owns its Rust module path",
                    name.as_str()
                ),
            ))
        })
        .collect()
}

pub fn analyze_document(uri: &Url, text: &str) -> Vec<Diagnostic> {
    match uri
        .path()
        .as_str()
        .rsplit_once('.')
        .map(|(_, extension)| extension)
    {
        Some("toml") => analyze_toml(uri, text),
        Some("ttl" | "rdf" | "n3") => analyze_turtle(text),
        Some("nt" | "nq") => analyze_rdf_lines(text),
        Some("rq" | "sparql") => analyze_sparql(text),
        Some("tera" | "tmpl" | "j2" | "jinja" | "jinja2") => analyze_tera(text),
        Some("rs") => analyze_generated_rust(uri, text),
        _ => Vec::new(),
    }
}
