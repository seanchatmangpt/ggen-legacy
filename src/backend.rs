#![allow(deprecated)]

use crate::{analysis::analyze_document, capabilities::server_capabilities};
use lsp_max::lsp_types_max::*;
use lsp_max::{jsonrpc::Result, Client, LanguageServer};
use regex::Regex;
use std::{collections::HashMap, sync::Arc};
use tokio::sync::RwLock;

#[derive(Clone, Debug)]
struct Document {
    language_id: String,
    version: i32,
    text: String,
}

pub struct GgenLanguageServer {
    client: Client,
    documents: Arc<RwLock<HashMap<Url, Document>>>,
}

impl GgenLanguageServer {
    pub fn new(client: Client) -> Self {
        Self {
            client,
            documents: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    async fn publish(&self, uri: Url, text: &str, version: Option<i32>) {
        self.client
            .publish_diagnostics(uri.clone(), analyze_document(&uri, text), version)
            .await;
    }

    async fn document(&self, uri: &Url) -> Option<Document> {
        self.documents.read().await.get(uri).cloned()
    }

    fn completion_items(uri: &Url) -> Vec<CompletionItem> {
        let values: &[(&str, &str)] = match uri.path().rsplit_once('.').map(|(_, ext)| ext) {
            Some("ttl" | "rdf" | "n3") => &[
                ("@prefix", "@prefix ${1:prefix}: <${2:iri}> ."),
                ("rdfs:label", "rdfs:label \"${1:label}\" ;"),
                (
                    "prov:wasDerivedFrom",
                    "prov:wasDerivedFrom ${1:source} ;",
                ),
            ],
            Some("toml") => &[
                ("[project]", "[project]\nname = \"${1:name}\""),
                (
                    "[ontology]",
                    "[ontology]\nsource = \"${1:ontology.ttl}\"",
                ),
                (
                    "[[generation.rules]]",
                    "[[generation.rules]]\nname = \"${1:rule}\"",
                ),
            ],
            Some("tera" | "tmpl" | "j2" | "jinja" | "jinja2") => &[
                ("{{ }}", "{{ ${1:value} }}"),
                (
                    "{% if %}",
                    "{% if ${1:condition} %}\n${2}\n{% endif %}",
                ),
                (
                    "{% for %}",
                    "{% for ${1:item} in ${2:items} %}\n${3}\n{% endfor %}",
                ),
            ],
            _ => &[],
        };

        values
            .iter()
            .map(|(label, insert_text)| CompletionItem {
                label: (*label).to_owned(),
                kind: Some(CompletionItemKind::SNIPPET),
                insert_text: Some((*insert_text).to_owned()),
                insert_text_format: Some(InsertTextFormat::SNIPPET),
                ..Default::default()
            })
            .collect()
    }

    fn symbols(text: &str) -> Vec<DocumentSymbol> {
        let patterns = [
            Regex::new(r"(?m)^\s*(\[\[?[^\]\n]+\]\]?)\s*$").expect("static regex"),
            Regex::new(r"(?im)^\s*(?:@prefix|prefix)\s+([A-Za-z][\w-]*):")
                .expect("static regex"),
            Regex::new(r"{%\s*(?:block|macro)\s+([A-Za-z_][\w-]*)")
                .expect("static regex"),
        ];
        patterns
            .iter()
            .flat_map(|pattern| pattern.captures_iter(text))
            .filter_map(|captures| {
                let item = captures.get(1)?;
                let start = offset_position(text, item.start());
                let end = offset_position(text, item.end());
                Some(DocumentSymbol {
                    name: item.as_str().to_owned(),
                    detail: None,
                    kind: SymbolKind::OBJECT,
                    tags: None,
                    deprecated: None,
                    range: Range::new(start, end),
                    selection_range: Range::new(start, end),
                    children: None,
                })
            })
            .collect()
    }
}

fn offset_position(text: &str, offset: usize) -> Position {
    let prefix = &text[..offset.min(text.len())];
    let line = prefix.bytes().filter(|byte| *byte == b'\n').count() as u32;
    let character = prefix
        .rsplit_once('\n')
        .map_or(prefix.chars().count(), |(_, tail)| tail.chars().count()) as u32;
    Position::new(line, character)
}

#[lsp_max::async_trait]
impl LanguageServer for GgenLanguageServer {
    async fn initialize(&self, _params: InitializeParams) -> Result<InitializeResult> {
        Ok(InitializeResult {
            capabilities: server_capabilities(),
            server_info: Some(ServerInfo {
                name: "ggen-lsp".to_owned(),
                version: Some(env!("CARGO_PKG_VERSION").to_owned()),
            }),
            ..Default::default()
        })
    }

    async fn initialized(&self, _: InitializedParams) {
        self.client
            .log_message(MessageType::INFO, "ggen-lsp initialized on lsp-max")
            .await;
    }

    async fn shutdown(&self) -> Result<()> {
        Ok(())
    }

    async fn did_open(&self, params: DidOpenTextDocumentParams) {
        let item = params.text_document;
        let document = Document {
            language_id: item.language_id,
            version: item.version,
            text: item.text,
        };
        self.documents
            .write()
            .await
            .insert(item.uri.clone(), document.clone());
        self.publish(item.uri, &document.text, Some(document.version))
            .await;
    }

    async fn did_change(&self, params: DidChangeTextDocumentParams) {
        if params
            .content_changes
            .iter()
            .any(|change| change.range.is_some())
        {
            self.client
                .log_message(
                    MessageType::ERROR,
                    "incremental changes refused: ggen-lsp advertises full synchronization",
                )
                .await;
            return;
        }
        let Some(change) = params.content_changes.into_iter().last() else {
            return;
        };
        let uri = params.text_document.uri;
        let version = params.text_document.version;
        let language_id = self
            .document(&uri)
            .await
            .map_or_else(String::new, |document| document.language_id);
        let document = Document {
            language_id,
            version,
            text: change.text,
        };
        self.documents
            .write()
            .await
            .insert(uri.clone(), document.clone());
        self.publish(uri, &document.text, Some(document.version))
            .await;
    }

    async fn did_save(&self, _params: DidSaveTextDocumentParams) {}

    async fn did_close(&self, params: DidCloseTextDocumentParams) {
        let uri = params.text_document.uri;
        self.documents.write().await.remove(&uri);
        self.client.publish_diagnostics(uri, Vec::new(), None).await;
    }

    async fn completion(&self, params: CompletionParams) -> Result<Option<CompletionResponse>> {
        Ok(Some(CompletionResponse::Array(Self::completion_items(
            &params.text_document_position.text_document.uri,
        ))))
    }

    async fn hover(&self, params: HoverParams) -> Result<Option<Hover>> {
        let uri = params.text_document_position_params.text_document.uri;
        let Some(document) = self.document(&uri).await else {
            return Ok(None);
        };
        let position = params.text_document_position_params.position;
        let line = document
            .text
            .lines()
            .nth(position.line as usize)
            .unwrap_or_default();
        let message = if line.contains("@prefix") {
            "Declares a Turtle namespace prefix."
        } else if line.trim_start().starts_with('[') {
            "Declares a ggen TOML configuration table."
        } else if line.contains("{{") || line.contains("{%") {
            "Tera template expression or control block."
        } else {
            return Ok(None);
        };
        Ok(Some(Hover {
            contents: HoverContents::Markup(MarkupContent {
                kind: MarkupKind::Markdown,
                value: message.to_owned(),
            }),
            range: None,
        }))
    }

    async fn document_symbol(
        &self,
        params: DocumentSymbolParams,
    ) -> Result<Option<DocumentSymbolResponse>> {
        let uri = params.text_document.uri;
        Ok(self
            .document(&uri)
            .await
            .map(|document| DocumentSymbolResponse::Nested(Self::symbols(&document.text))))
    }

    async fn formatting(
        &self,
        params: DocumentFormattingParams,
    ) -> Result<Option<Vec<TextEdit>>> {
        let uri = params.text_document.uri;
        let Some(document) = self.document(&uri).await else {
            return Ok(None);
        };
        let formatted = document
            .text
            .lines()
            .map(str::trim_end)
            .collect::<Vec<_>>()
            .join("\n")
            + "\n";
        if formatted == document.text {
            return Ok(Some(Vec::new()));
        }
        Ok(Some(vec![TextEdit {
            range: Range::new(
                Position::new(0, 0),
                offset_position(&document.text, document.text.len()),
            ),
            new_text: formatted,
        }]))
    }

    async fn code_action(
        &self,
        params: CodeActionParams,
    ) -> Result<Option<CodeActionResponse>> {
        let actions = params
            .context
            .diagnostics
            .into_iter()
            .filter(|diagnostic| {
                matches!(
                    &diagnostic.code,
                    Some(NumberOrString::String(code)) if code == "GGEN-MANIFEST-001"
                )
            })
            .map(|diagnostic| {
                CodeActionOrCommand::CodeAction(CodeAction {
                    title: "Add [project] table".to_owned(),
                    kind: Some(CodeActionKind::QUICKFIX),
                    diagnostics: Some(vec![diagnostic]),
                    edit: Some(WorkspaceEdit {
                        changes: Some(HashMap::from([(
                            params.text_document.uri.clone(),
                            vec![TextEdit {
                                range: Range::new(Position::new(0, 0), Position::new(0, 0)),
                                new_text: "[project]\nname = \"project\"\n\n".to_owned(),
                            }],
                        )])),
                        ..Default::default()
                    }),
                    ..Default::default()
                })
            })
            .collect();
        Ok(Some(actions))
    }
}
