#!/usr/bin/env python3
"""Greenfield Fortune-5 Procure-to-Pay DfCM Chicago court.

This court is deliberately bounded: it executes the full decision/manufacture/
BRCE/receipt/replay chain in-process and statically binds external producer
identities. It does not claim that external cloud or ERP systems were actuated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA = "https://ggen.chatmangpt.com/schema/dfcm-chicago/v1"
RECEIPT_SCHEMA = "https://ggen.chatmangpt.com/schema/dfcm-chicago-receipt/v1"
GGEN_ECOSYSTEM_SHA = "f42aa25c4974a0d5a701ed0e08f3bce46d69d115"
AUTOFDE_LAB_SHA = "8ece5884c6e776093cd08beb80c5d1c9a8d05a3d"
GYMACT_SHA = "dc8c8add4edd525e14815e44d03b84b347abfcc8"
REQUIRED_CAPABILITIES = (
    "supplier_onboarding",
    "requisition",
    "purchase_order",
    "approval",
    "goods_receipt",
    "invoice",
    "three_way_match",
    "payment",
    "audit_trail",
)
REQUIRED_STRATEGIES = ("big_bang", "dual_run", "canary")
REQUIRED_FAILURES = (
    "supplier_master_drift",
    "approval_partition",
    "duplicate_invoice",
    "receipt_loss",
    "payment_timeout",
)
SHA40 = re.compile(r"^[0-9a-f]{40}$")


class Refusal(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def require_exact_sha(value: Any, code: str) -> str:
    if not isinstance(value, str) or not SHA40.fullmatch(value):
        raise Refusal(f"REFUSED[{code}]")
    return value


def validate_provenance(p: dict[str, Any]) -> None:
    expected = {
        "ggen_ecosystem": GGEN_ECOSYSTEM_SHA,
        "autofde_lab": AUTOFDE_LAB_SHA,
        "gymact": GYMACT_SHA,
    }
    if p != expected:
        raise Refusal("REFUSED[STALE_SHA]")


def admit(scenario: dict[str, Any], subject_sha: str) -> dict[str, Any]:
    require_exact_sha(subject_sha, "MUTABLE_IDENTITY")
    if scenario.get("schema") != SCHEMA:
        raise Refusal("REFUSED[MALFORMED_ADMISSION]")
    if scenario.get("immutable_subject") is not True:
        raise Refusal("REFUSED[MUTABLE_IDENTITY]")
    validate_provenance(scenario.get("provenance") or {})

    capabilities = scenario.get("capabilities")
    strategies = scenario.get("strategies")
    failures = scenario.get("failure_injections")
    owners = scenario.get("owners")
    if not all(isinstance(x, list) for x in (capabilities, strategies, failures)):
        raise Refusal("REFUSED[MALFORMED_ADMISSION]")
    if sorted(capabilities) != sorted(REQUIRED_CAPABILITIES):
        raise Refusal("REFUSED[CAPABILITY_COVERAGE]")
    if sorted(strategies) != sorted(REQUIRED_STRATEGIES):
        raise Refusal("REFUSED[STRATEGY_COVERAGE]")
    if sorted(failures) != sorted(REQUIRED_FAILURES):
        raise Refusal("REFUSED[FAILURE_COVERAGE]")
    if not isinstance(owners, dict) or set(owners) != set(REQUIRED_CAPABILITIES):
        raise Refusal("REFUSED[OWNERSHIP_COVERAGE]")
    values = list(owners.values())
    if len(values) != len(set(values)):
        raise Refusal("REFUSED[OWNERSHIP_COLLISION]")

    architecture = scenario.get("architecture") or {}
    if architecture.get("linux_arm64") is not True:
        raise Refusal("REFUSED[ARCHITECTURE_WITNESS]")
    if architecture.get("linux_amd64") is not False:
        raise Refusal("REFUSED[ARCHITECTURE_WITNESS]")

    return {
        "subject_sha": subject_sha,
        "scenario_id": scenario.get("scenario_id"),
        "capabilities": sorted(capabilities),
        "strategies": sorted(strategies),
        "failures": sorted(failures),
        "owners": {k: owners[k] for k in sorted(owners)},
        "architecture": architecture,
        "provenance": scenario["provenance"],
        "standing": "PARTIAL_ALIVE",
        "authority": "ADMITTED_ONLY",
    }


def platform_support(admitted: dict[str, Any], platform: str) -> dict[str, str]:
    key = platform.replace("/", "_")
    supported = admitted["architecture"].get(key)
    if supported is True:
        return {"platform": platform, "standing": "PARTIAL_ALIVE"}
    if platform == "linux/amd64" and supported is False:
        raise Refusal("UNSUPPORTED[ECOSYSTEM_CONTAINER_AMD64]")
    raise Refusal(f"UNSUPPORTED[{platform.upper().replace('/', '_')}]")


@dataclass(frozen=True)
class Candidate:
    strategy: str
    failure: str
    reversibility: int
    coverage: int
    blast_radius: int
    learning_rate: int

    @property
    def utility(self) -> int:
        return 5 * self.reversibility + 4 * self.coverage + 3 * self.learning_rate - 6 * self.blast_radius

    def as_dict(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy,
            "failure": self.failure,
            "reversibility": self.reversibility,
            "coverage": self.coverage,
            "blast_radius": self.blast_radius,
            "learning_rate": self.learning_rate,
            "utility": self.utility,
        }


STRATEGY_METRICS = {
    "big_bang": (1, 9, 9, 3),
    "dual_run": (8, 9, 4, 8),
    "canary": (10, 7, 2, 10),
}


def enumerate_options(admitted: dict[str, Any]) -> list[Candidate]:
    result = []
    for strategy in admitted["strategies"]:
        rev, cov, blast, learn = STRATEGY_METRICS[strategy]
        for failure in admitted["failures"]:
            result.append(Candidate(strategy, failure, rev, cov, blast, learn))
    expected = len(REQUIRED_STRATEGIES) * len(REQUIRED_FAILURES)
    if len(result) != expected:
        raise Refusal("REFUSED[COMBINATORIAL_CLOSURE]")
    return result


def strategy_frontier(options: list[Candidate]) -> list[dict[str, Any]]:
    by_strategy: dict[str, list[Candidate]] = {}
    for option in options:
        by_strategy.setdefault(option.strategy, []).append(option)
    frontier = []
    for strategy in sorted(by_strategy):
        members = by_strategy[strategy]
        frontier.append({
            "strategy": strategy,
            "utility": min(x.utility for x in members),
            "falsifiers": sorted(x.failure for x in members),
            "reversible": min(x.reversibility for x in members) >= 8,
        })
    return sorted(frontier, key=lambda x: (-x["utility"], x["strategy"]))


def ppddl_problem(admitted: dict[str, Any], frontier: list[dict[str, Any]]) -> str:
    caps = " ".join(admitted["capabilities"])
    strategies = " ".join(x["strategy"] for x in frontier)
    failures = " ".join(admitted["failures"])
    return "\n".join([
        "(define (problem fortune5-p2p-chicago)",
        "  (:domain ggen-greenfield-enterprise-reconstruction)",
        f"  (:objects {caps} - capability)",
        f"  ; strategies {strategies}",
        f"  ; injected-failures {failures}",
        "  (:init (admitted) (brce-required) (receipts-required))",
        "  (:goal (and (all-capabilities-covered) (deterministic-replay) (zero-unreceipted-do)))",
        ")",
        "",
    ])


def planner_portfolio(admitted: dict[str, Any], problem: str) -> dict[str, Any]:
    if not problem.startswith("(define (problem fortune5-p2p-chicago)"):
        raise Refusal("REFUSED[PPDDL_PROJECTION]")
    planners = [
        {"id": "fast-downward", "strength": "classical-search", "available": False},
        {"id": "pyperplan", "strength": "reference-search", "available": False},
        {"id": "deterministic-dfcm", "strength": "bounded-greenfield-selection", "available": True},
    ]
    selected = next(p for p in planners if p["available"])
    return {
        "autofde_lab_sha": admitted["provenance"]["autofde_lab"],
        "planners": planners,
        "selected": selected["id"],
        "selection_reason": "first admitted executable planner; external planners are explicit unavailable edges",
    }


def select_strategy(frontier: list[dict[str, Any]], portfolio: dict[str, Any]) -> dict[str, Any]:
    if portfolio["selected"] != "deterministic-dfcm":
        raise Refusal("REFUSED[PLANNER_SELECTION]")
    if not frontier:
        raise Refusal("REFUSED[EMPTY_FRONTIER]")
    selected = frontier[0]
    if selected["strategy"] != "canary":
        raise Refusal("REFUSED[DFCM_SELECTION]")
    return selected


def construct_intent(admitted: dict[str, Any], selected: dict[str, Any], problem: str) -> dict[str, Any]:
    body = {
        "operation": "manufacture_enterprise_reconstruction",
        "subject_sha": admitted["subject_sha"],
        "scenario_id": admitted["scenario_id"],
        "strategy": selected["strategy"],
        "capabilities": admitted["capabilities"],
        "failure_injections": admitted["failures"],
        "ppddl_sha256": sha256(problem.encode()),
        "authority": "CONSTRUCT_ONLY",
        "brce_required": True,
    }
    return {"body": body, "intent_sha256": sha256(canonical(body)), "allows_do": False}


def manufacture_artifact(admitted: dict[str, Any], selected: dict[str, Any], portfolio: dict[str, Any]) -> bytes:
    artifact = {
        "kind": "fortune5-procure-to-pay-reconstruction",
        "scenario_id": admitted["scenario_id"],
        "subject_sha": admitted["subject_sha"],
        "strategy": selected["strategy"],
        "planner": portfolio["selected"],
        "capabilities": admitted["capabilities"],
        "owners": admitted["owners"],
        "controls": {
            "brce_only_do": True,
            "receipt_required": True,
            "replay_required": True,
            "failure_injections": admitted["failures"],
        },
        "provenance": admitted["provenance"],
    }
    return canonical(artifact)


def brce_do(intent: dict[str, Any], artifact: bytes, *, authorized: bool) -> dict[str, Any]:
    if intent.get("allows_do") is not False:
        raise Refusal("REFUSED[CONSTRUCT_HAS_DO]")
    if not authorized:
        raise Refusal("REFUSED[UNAUTHORIZED_DO]")
    body = intent["body"]
    if body.get("brce_required") is not True:
        raise Refusal("REFUSED[BRCE_NOT_REQUIRED]")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "subject_sha": body["subject_sha"],
        "scenario_id": body["scenario_id"],
        "intent_sha256": intent["intent_sha256"],
        "artifact_sha256": sha256(artifact),
        "replay_key": f"{body['scenario_id']}:{intent['intent_sha256'][:16]}",
        "authority": "BRCE",
        "standing": "ALIVE",
        "external_actuation": False,
    }
    receipt["receipt_sha256"] = sha256(canonical(receipt))
    return receipt


def verify_receipt(receipt: dict[str, Any], intent: dict[str, Any], artifact: bytes) -> None:
    if receipt.get("authority") != "BRCE":
        raise Refusal("REFUSED[UNAUTHORIZED_DO]")
    if receipt.get("intent_sha256") != intent.get("intent_sha256"):
        raise Refusal("REFUSED[UNBOUND_RECEIPT]")
    if receipt.get("artifact_sha256") != sha256(artifact):
        raise Refusal("REFUSED[ARTIFACT_TAMPER]")
    expected = dict(receipt)
    claimed = expected.pop("receipt_sha256", None)
    if claimed != sha256(canonical(expected)):
        raise Refusal("REFUSED[RECEIPT_TAMPER]")


def execute(scenario: dict[str, Any], subject_sha: str, *, authorized: bool = True) -> dict[str, Any]:
    admitted = admit(scenario, subject_sha)
    arm64 = platform_support(admitted, "linux/arm64")
    options = enumerate_options(admitted)
    frontier = strategy_frontier(options)
    problem = ppddl_problem(admitted, frontier)
    portfolio = planner_portfolio(admitted, problem)
    selected = select_strategy(frontier, portfolio)
    intent = construct_intent(admitted, selected, problem)
    artifact_a = manufacture_artifact(admitted, selected, portfolio)
    artifact_b = manufacture_artifact(admitted, selected, portfolio)
    if artifact_a != artifact_b:
        raise Refusal("BUILD_BROKEN[NONDETERMINISTIC_MANUFACTURE]")
    receipt = brce_do(intent, artifact_a, authorized=authorized)
    verify_receipt(receipt, intent, artifact_a)
    return {
        "admitted": admitted,
        "option_count": len(options),
        "frontier": frontier,
        "ppddl": problem,
        "planner_portfolio": portfolio,
        "selected": selected,
        "intent": intent,
        "artifact": json.loads(artifact_a),
        "artifact_sha256": sha256(artifact_a),
        "receipt": receipt,
        "platform": arm64,
        "standing": "ALIVE",
        "scope": "in-process-greenfield-enterprise-reconstruction",
    }


def replay(scenario: dict[str, Any], subject_sha: str, receipt: dict[str, Any]) -> dict[str, Any]:
    rerun = execute(scenario, subject_sha)
    if canonical(rerun["receipt"]) != canonical(receipt):
        raise Refusal("REFUSED[REPLAY_DIVERGENCE]")
    return {"standing": "ALIVE", "receipt_sha256": receipt["receipt_sha256"], "replay": "MATCHED"}


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Refusal("REFUSED[MALFORMED_ADMISSION]") from exc
    if not isinstance(value, dict):
        raise Refusal("REFUSED[MALFORMED_ADMISSION]")
    return value


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True, type=Path)
    ap.add_argument("--subject-sha", required=True)
    ap.add_argument("--receipt-out", type=Path)
    args = ap.parse_args()
    try:
        scenario = load(args.scenario)
        result = execute(scenario, args.subject_sha)
        replay_result = replay(scenario, args.subject_sha, result["receipt"])
        try:
            platform_support(result["admitted"], "linux/amd64")
        except Refusal as exc:
            result["amd64"] = str(exc)
        result["replay"] = replay_result
        if args.receipt_out:
            args.receipt_out.write_text(json.dumps(result["receipt"], indent=2, sort_keys=True) + "\n")
        print(json.dumps({
            "standing": result["standing"],
            "scope": result["scope"],
            "strategy": result["selected"]["strategy"],
            "planner": result["planner_portfolio"]["selected"],
            "option_count": result["option_count"],
            "artifact_sha256": result["artifact_sha256"],
            "receipt_sha256": result["receipt"]["receipt_sha256"],
            "replay": replay_result["replay"],
            "amd64": result["amd64"],
        }, sort_keys=True))
        return 0
    except Refusal as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
