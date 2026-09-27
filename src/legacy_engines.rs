use serde_json::{json, Value};

pub const BEAM4PM_COURT_SCHEMA: &str = "beam4pm-legacy-equivalence/1";
pub const ENGINE_HANDOFF_SCHEMA: &str = "ggen-legacy-engine-handoff/1";

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LegacyEngineRefusal {
    ReportNotObject,
    UnsupportedSchema(String),
    EmptySubject,
    MissingReceiptDigest,
    InvalidReceiptDigest,
    AuthorityEscalation(String),
    MissingEquivalenceVerdict,
    MissingCounterexamples,
    ContradictoryEquivalentReport,
    CounterexampleReportWithoutWitness,
}

pub fn compile_engine_handoff(report: &Value) -> Result<Value, LegacyEngineRefusal> {
    let object = report
        .as_object()
        .ok_or(LegacyEngineRefusal::ReportNotObject)?;

    let schema = object
        .get("schema")
        .and_then(Value::as_str)
        .unwrap_or_default();

    if schema != BEAM4PM_COURT_SCHEMA {
        return Err(LegacyEngineRefusal::UnsupportedSchema(schema.to_owned()));
    }

    let subject = object
        .get("subject")
        .and_then(Value::as_str)
        .unwrap_or_default();

    if subject.trim().is_empty() {
        return Err(LegacyEngineRefusal::EmptySubject);
    }

    let receipt = object
        .get("receipt_digest")
        .and_then(Value::as_str)
        .ok_or(LegacyEngineRefusal::MissingReceiptDigest)?;

    if !valid_sha256(receipt) {
        return Err(LegacyEngineRefusal::InvalidReceiptDigest);
    }

    let authority = object
        .get("authority_ceiling")
        .and_then(Value::as_str)
        .unwrap_or_default();

    if authority != "OBSERVE" {
        return Err(LegacyEngineRefusal::AuthorityEscalation(authority.to_owned()));
    }

    let equivalent = object
        .get("equivalent")
        .and_then(Value::as_bool)
        .ok_or(LegacyEngineRefusal::MissingEquivalenceVerdict)?;

    let counterexamples = object
        .get("counterexamples")
        .and_then(Value::as_array)
        .ok_or(LegacyEngineRefusal::MissingCounterexamples)?;

    if equivalent && !counterexamples.is_empty() {
        return Err(LegacyEngineRefusal::ContradictoryEquivalentReport);
    }

    if !equivalent && counterexamples.is_empty() {
        return Err(LegacyEngineRefusal::CounterexampleReportWithoutWitness);
    }

    let state = if equivalent {
        "READY_FOR_ADMISSION_REVIEW"
    } else {
        "REPAIR_REQUIRED"
    };

    Ok(json!({
        "schema": ENGINE_HANDOFF_SCHEMA,
        "subject": subject,
        "state": state,
        "manufacture_allowed": false,
        "retirement_allowed": false,
        "authority_ceiling": "CONSTRUCT",
        "source": {
            "engine": "beam4pm",
            "schema": BEAM4PM_COURT_SCHEMA,
            "receipt_digest": receipt,
            "legacy_identity": object.get("legacy_identity").cloned().unwrap_or(Value::Null),
            "candidate_identity": object.get("candidate_identity").cloned().unwrap_or(Value::Null)
        },
        "counterexamples": counterexamples,
        "next_edge": if equivalent { "independent_admission_review" } else { "xaas_repair_campaign" }
    }))
}

fn valid_sha256(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}
