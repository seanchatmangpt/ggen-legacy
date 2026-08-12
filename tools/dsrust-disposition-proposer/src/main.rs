//! Real dsrust (DSPy-for-Rust) example: proposes a legacy-capability disposition
//! (ARCHIVED/REFUSED/REPLACED/SUBSUMED/PRESERVED) from real evidence fields already
//! present in `foundry/evidence/B/legacy-capabilities.ttl`, for human/`admit_capabilities`
//! review -- it never writes to the corpus or bypasses that binary's real admission gate.
//!
//! Mirrors the exact judgment this repo's own real disposition resolutions made by hand
//! this session (see `docs/src/16-foundry-completion-ard.md`): given a capability's
//! historical source commit, legacy source path, default behavior, and evidence fixtures,
//! propose a disposition with rationale -- a proposal, not an admission.
//!
//! Requires `GROQ_API_KEY` in the environment. Never hardcode or commit a key.
//!
//!     GROQ_API_KEY=... cargo run --bin propose-disposition -- \
//!       --capability-id legacy_ext_template_mode_append \
//!       --historical-source-commit "fca98756f (...)" \
//!       --legacy-source-path "crates/ggen-daemon/src/generator.rs (...)" \
//!       --default-behavior "Not one of the 3 variants ... in the live GenerationMode enum" \
//!       --evidence-fixtures "git log --all --oneline -S'mode = \"Update\"'"

use anyhow::{Context, Result};
use clap::Parser;
use dsrust::{call, configure, predict, Prediction, LM};
use serde::Serialize;

#[derive(Debug, Parser)]
#[command(
    name = "propose-disposition",
    about = "Real dsrust/Groq disposition proposal for a legacy capability -- human/tool review only, never auto-admitting"
)]
struct Cli {
    #[arg(long)]
    capability_id: String,
    #[arg(long)]
    historical_source_commit: String,
    #[arg(long)]
    legacy_source_path: String,
    #[arg(long)]
    default_behavior: String,
    #[arg(long)]
    evidence_fixtures: String,
    /// Groq model id, without the `openai/` provider prefix dsrust expects.
    #[arg(long, default_value = "llama-3.3-70b-versatile")]
    model: String,
}

#[derive(Debug, Serialize)]
struct DispositionProposal {
    capability_id: String,
    proposed_disposition: String,
    rationale: String,
    note: String,
}

fn text(prediction: &Prediction, field: &str) -> String {
    prediction
        .get(field)
        .and_then(|value| value.as_str())
        .unwrap_or_default()
        .to_owned()
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    let groq_key = std::env::var("GROQ_API_KEY")
        .context("GROQ_API_KEY must be set -- never hardcoded, never committed")?;
    configure(
        LM::new(&format!("openai/{}", cli.model))?
            .with_openai_base_url("https://api.groq.com/openai/v1")
            .with_openai_key(groq_key),
    );

    // Real, code-grounded task instructions -- the same five real fields and the same
    // five-value disposition vocabulary (ARCHIVED/REFUSED/REPLACED/SUBSUMED/PRESERVED)
    // this repo's admit_capabilities.rs (tools/architecture-foundry) actually admits;
    // see governance's real disposition definitions in
    // foundry/evidence/B/legacy-capabilities.ttl for the vocabulary this mirrors.
    let program = predict!(
        "historical_source_commit, legacy_source_path, default_behavior, evidence_fixtures -> proposed_disposition, rationale"
    );

    let prediction = call!(
        program,
        historical_source_commit = cli.historical_source_commit.as_str(),
        legacy_source_path = cli.legacy_source_path.as_str(),
        default_behavior = cli.default_behavior.as_str(),
        evidence_fixtures = cli.evidence_fixtures.as_str()
    )
    .await
    .context("real Groq call failed")?;

    let proposal = DispositionProposal {
        capability_id: cli.capability_id,
        proposed_disposition: text(&prediction, "proposed_disposition"),
        rationale: text(&prediction, "rationale"),
        note: "PROPOSAL ONLY -- not an admission. Real disposition is decided by \
               admit_capabilities (tools/architecture-foundry) against real evidence; \
               this output is for human/tool review, per this program's own \
               no-self-certification doctrine."
            .to_string(),
    };
    println!("{}", serde_json::to_string_pretty(&proposal)?);
    Ok(())
}
