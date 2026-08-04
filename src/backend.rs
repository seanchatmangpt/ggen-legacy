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
    type_hierarchy_dynamic: Arc<RwLock<bool>>,
}

impl GgenLanguageServer {
    pub fn new(client: Client) -> Self {
        Self {
            client,
            documents: Arc::new(RwLock::new(HashMap::new())),
            type_hierarchy_dynamic: Arc::new(RwLock::new(false)),
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
        let values: &[(&str, &str)] = match uri.path().as_str().rsplit_once('.').map(|(_, ext)| ext)
        {
            Some("ttl" | "rdf" | "n3" | "nt" | "nq") => &[
                ("@prefix", "@prefix ${1:prefix}: <${2:iri}> ."),
                ("rdfs:label", "rdfs:label \"${1:label}\" ;"),
            ],
            Some("toml") => &[
                ("[project]", "[project]\nname = \"${1:name}\""),
                ("[ontology]", "[ontology]\nsource = \"${1:ontology.ttl}\""),
                (
                    "[[generation.rules]]",
                    "[[generation.rules]]\nname = \"${1:rule}\"",
                ),
            ],
            Some("rq" | "sparql") => &[
                ("SELECT", "SELECT ${1:*} WHERE {\n  ${2:?s ?p ?o .}\n}"),
                ("PREFIX", "PREFIX ${1:ex}: <${2:urn:example:}>"),
            ],
            Some("tera" | "tmpl" | "j2" | "jinja" | "jinja2") => &[
                ("{{ }}", "{{ ${1:value} }}"),
                ("{% if %}", "{% if ${1:condition} %}\n${2}\n{% endif %}"),
            ],
            Some("rs") => &[("pub mod", "pub mod ${1:module};")],
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
            Regex::new(r"(?im)^\s*(?:@prefix|prefix)\s+([A-Za-z][\w-]*):").expect("static regex"),
            Regex::new(r"\{%\s*(?:block|macro)\s+([A-Za-z_][\w-]*)").expect("static regex"),
            Regex::new(r"(?m)^\s*(?:pub\s+)?mod\s+([A-Za-z_][A-Za-z0-9_]*)").expect("static regex"),
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

    fn token_range(text: &str, position: Position) -> Option<(String, Range)> {
        let line = text.lines().nth(position.line as usize)?;
        let character = position.character as usize;
        if character > line.len() {
            return None;
        }
        let bytes = line.as_bytes();
        let admitted = |byte: u8| byte.is_ascii_alphanumeric() || b"_:.-".contains(&byte);
        let mut start = character.min(bytes.len());
        while start > 0 && admitted(bytes[start - 1]) {
            start -= 1;
        }
        let mut end = character.min(bytes.len());
        while end < bytes.len() && admitted(bytes[end]) {
            end += 1;
        }
        if start == end {
            return None;
        }
        Some((
            line[start..end].to_owned(),
            Range::new(
                Position::new(position.line, start as u32),
                Position::new(position.line, end as u32),
            ),
        ))
    }
}

fn offset_position(text: &str, offset: usize) -> Position {
    let prefix = &text[..offset.min(text.len())];
    let line = prefix.bytes().filter(|byte| *byte == b'\n').count() as u32;
    let character = prefix
        .rsplit_once('\n')
        .map_or(prefix.chars().count(), |(_, tail)| tail.chars().count())
        as u32;
    Position::new(line, character)
}

fn client_capability_bool(capabilities: &ClientCapabilities, path: &[&str]) -> bool {
    let Ok(mut value) = serde_json::to_value(capabilities) else {
        return false;
    };
    for segment in path {
        let Some(next) = value.get(*segment).cloned() else {
            return false;
        };
        value = next;
    }
    value.as_bool().unwrap_or(false)
}

#[lsp_max::async_trait]
impl LanguageServer for GgenLanguageServer {
    async fn initialize(&self, params: InitializeParams) -> Result<InitializeResult> {
        *self.type_hierarchy_dynamic.write().await = client_capability_bool(
            &params.capabilities,
            &["textDocument", "typeHierarchy", "dynamicRegistration"],
        );
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
        if *self.type_hierarchy_dynamic.read().await {
            let registration = Registration {
                id: "ggen-legacy-type-hierarchy".to_owned(),
                method: "textDocument/prepareTypeHierarchy".to_owned(),
                register_options: Some(serde_json::json!({"documentSelector": null})),
            };
            if let Err(error) = self.client.register_capability(vec![registration]).await {
                self.client
                    .log_message(
                        MessageType::WARNING,
                        format!("type hierarchy registration failed: {error}"),
                    )
                    .await;
            }
        }
        self.client
            .log_message(MessageType::INFO, "ggen-lsp initialized on lsp-max")
            .await;
    }

    async fn shutdown(&self) -> Result<()> {
        self.documents.write().await.clear();
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
        } else if line.contains("SELECT") || line.contains("ASK") {
            "SPARQL query form."
        } else if line.contains("mod ") {
            "Generated Rust module declaration."
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

    async fn goto_definition(
        &self, _params: GotoDefinitionParams,
    ) -> Result<Option<GotoDefinitionResponse>> {
        Ok(None)
    }

    async fn references(&self, _params: ReferenceParams) -> Result<Option<Vec<Location>>> {
        Ok(Some(Vec::new()))
    }

    async fn prepare_rename(
        &self, params: TextDocumentPositionParams,
    ) -> Result<Option<PrepareRenameResponse>> {
        let Some(document) = self.document(&params.text_document.uri).await else {
            return Ok(None);
        };
        Ok(Self::token_range(&document.text, params.position)
            .map(|(_, range)| PrepareRenameResponse::Range(range)))
    }

    async fn rename(&self, _params: RenameParams) -> Result<Option<WorkspaceEdit>> {
        Ok(None)
    }

    async fn document_symbol(
        &self, params: DocumentSymbolParams,
    ) -> Result<Option<DocumentSymbolResponse>> {
        let uri = params.text_document.uri;
        Ok(self
            .document(&uri)
            .await
            .map(|document| DocumentSymbolResponse::Nested(Self::symbols(&document.text))))
    }

    async fn symbol(
        &self, _params: WorkspaceSymbolParams,
    ) -> Result<Option<Vec<SymbolInformation>>> {
        Ok(Some(Vec::new()))
    }

    async fn formatting(&self, params: DocumentFormattingParams) -> Result<Option<Vec<TextEdit>>> {
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

    async fn range_formatting(
        &self, _params: DocumentRangeFormattingParams,
    ) -> Result<Option<Vec<TextEdit>>> {
        Ok(Some(Vec::new()))
    }

    async fn code_action(&self, params: CodeActionParams) -> Result<Option<CodeActionResponse>> {
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

    async fn folding_range(
        &self, _params: FoldingRangeParams,
    ) -> Result<Option<Vec<FoldingRange>>> {
        Ok(Some(Vec::new()))
    }

    async fn semantic_tokens_full(
        &self, _params: SemanticTokensParams,
    ) -> Result<Option<SemanticTokensResult>> {
        Ok(None)
    }

    async fn inlay_hint(&self, _params: InlayHintParams) -> Result<Option<Vec<InlayHint>>> {
        Ok(Some(Vec::new()))
    }

    async fn code_lens(&self, _params: CodeLensParams) -> Result<Option<Vec<CodeLens>>> {
        Ok(Some(Vec::new()))
    }

    async fn prepare_call_hierarchy(
        &self, _params: CallHierarchyPrepareParams,
    ) -> Result<Option<Vec<CallHierarchyItem>>> {
        Ok(Some(Vec::new()))
    }

    async fn incoming_calls(
        &self, _params: CallHierarchyIncomingCallsParams,
    ) -> Result<Option<Vec<CallHierarchyIncomingCall>>> {
        Ok(Some(Vec::new()))
    }

    async fn outgoing_calls(
        &self, _params: CallHierarchyOutgoingCallsParams,
    ) -> Result<Option<Vec<CallHierarchyOutgoingCall>>> {
        Ok(Some(Vec::new()))
    }

    async fn prepare_type_hierarchy(
        &self, _params: TypeHierarchyPrepareParams,
    ) -> Result<Option<Vec<TypeHierarchyItem>>> {
        Ok(Some(Vec::new()))
    }

    async fn supertypes(
        &self, _params: TypeHierarchySupertypesParams,
    ) -> Result<Option<Vec<TypeHierarchyItem>>> {
        Ok(Some(Vec::new()))
    }

    async fn subtypes(
        &self, _params: TypeHierarchySubtypesParams,
    ) -> Result<Option<Vec<TypeHierarchyItem>>> {
        Ok(Some(Vec::new()))
    }
}
