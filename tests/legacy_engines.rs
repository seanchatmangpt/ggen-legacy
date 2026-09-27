use ggen_legacy_lsp::legacy_engines::{
    compile_engine_handoff, LegacyEngineRefusal, ENGINE_HANDOFF_SCHEMA,
};
use serde_json::json;

fn receipt(ch: char) -> String {
    std::iter::repeat(ch).take(64).collect()
}

#[test]
fn equivalent_court_report_is_ready_for_review_but_not_self_admitted() {
    let report = json!({
        "schema": "beam4pm-legacy-equivalence/1",
        "subject": "orders.cancel",
        "legacy_identity": "legacy@abc",
        "candidate_identity": "candidate@def",
        "equivalent": true,
        "counterexamples": [],
        "receipt_digest": receipt('a'),
        "authority_ceiling": "OBSERVE"
    });

    let handoff = compile_engine_handoff(&report).expect("admitted engine envelope");

    assert_eq!(handoff["schema"], ENGINE_HANDOFF_SCHEMA);
    assert_eq!(handoff["state"], "READY_FOR_ADMISSION_REVIEW");
    assert_eq!(handoff["manufacture_allowed"], false);
    assert_eq!(handoff["retirement_allowed"], false);
    assert_eq!(handoff["next_edge"], "independent_admission_review");
    assert_eq!(handoff["source"]["receipt_digest"], receipt('a'));
}

#[test]
fn counterexample_routes_to_xaas_without_collapsing_the_subject() {
    let report = json!({
        "schema": "beam4pm-legacy-equivalence/1",
        "subject": "orders.cancel",
        "equivalent": false,
        "counterexamples": [{
            "index": 0,
            "legacy": {"outcome": "cancelled"},
            "candidate": {"outcome": "pending"}
        }],
        "receipt_digest": receipt('b'),
        "authority_ceiling": "OBSERVE"
    });

    let handoff = compile_engine_handoff(&report).expect("valid counterexample envelope");

    assert_eq!(handoff["state"], "REPAIR_REQUIRED");
    assert_eq!(handoff["next_edge"], "xaas_repair_campaign");
    assert_eq!(handoff["counterexamples"].as_array().unwrap().len(), 1);
    assert_eq!(handoff["manufacture_allowed"], false);
}

#[test]
fn authority_escalation_is_refused() {
    let report = json!({
        "schema": "beam4pm-legacy-equivalence/1",
        "subject": "orders.cancel",
        "equivalent": true,
        "counterexamples": [],
        "receipt_digest": receipt('c'),
        "authority_ceiling": "DO"
    });

    assert_eq!(
        compile_engine_handoff(&report),
        Err(LegacyEngineRefusal::AuthorityEscalation("DO".to_owned()))
    );
}

#[test]
fn contradictory_equivalence_is_refused() {
    let report = json!({
        "schema": "beam4pm-legacy-equivalence/1",
        "subject": "orders.cancel",
        "equivalent": true,
        "counterexamples": [{"index": 0}],
        "receipt_digest": receipt('d'),
        "authority_ceiling": "OBSERVE"
    });

    assert_eq!(
        compile_engine_handoff(&report),
        Err(LegacyEngineRefusal::ContradictoryEquivalentReport)
    );
}
