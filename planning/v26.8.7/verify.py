#!/usr/bin/env python3
"""Independent bounded verifier for GL-PLAN-002.

This verifier establishes subsystem evidence only. It cannot promote repository or
release standing and it never actuates world state.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from lib import (  # noqa: E402
    EngineOutcome,
    MFW_PLANNING_TYPES,
    CapabilityProblem,
    RecursiveController,
    State,
    canonical_json,
    classify_pddl_features,
    load_profiles,
    probe_engine,
    project_mfw_request,
    project_powl,
    reconstruct_goal,
    replay_event_chain,
    run_engine,
    sha256_value,
    solve_capability_astar,
)


def record(bucket: dict[str, list[dict]], kind: str, subject: str, **data) -> None:
    bucket.setdefault(kind, []).append({"subject": subject, **data})


def run() -> tuple[int, dict]:
    evidence: dict[str, list[dict]] = {
        name: []
        for name in (
            "observed",
            "admitted",
            "executed",
            "changed",
            "verified",
            "inferred",
            "refused",
            "blocked",
            "unsupported",
        )
    }
    failures: list[str] = []

    def must(condition: bool, code: str) -> None:
        if not condition:
            failures.append(code)

    must((ROOT / "AGENTS.md").exists(), "ROOT_AUTHORITY_MISSING")
    must((ROOT / "tickets/GL-PLAN-002.md").exists(), "TICKET_MISSING")

    # Execute the real local unit boundary.
    unit = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(HERE / "tests"), "-v"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        shell=False,
        env={},
    )
    record(evidence, "executed", "unit-suite", exit_code=unit.returncode)
    must(unit.returncode == 0, "UNIT_SUITE_FAILED")

    benchmark_raw = json.loads((HERE / "fixtures/benchmark.json").read_text(encoding="utf-8"))
    goal = reconstruct_goal(benchmark_raw)
    record(evidence, "observed", "benchmark", digest=goal.source_digest)
    record(evidence, "admitted", "benchmark-goal", required_facts=list(goal.required_facts))
    must("forward-deployment" in goal.required_facts, "GOAL_RECONSTRUCTION_DRIFT")

    # Negative admission fixture must fail closed.
    leak_raw = json.loads((HERE / "fixtures/benchmark-reference-leak.json").read_text(encoding="utf-8"))
    try:
        reconstruct_goal(leak_raw)
        failures.append("REFERENCE_SOLUTION_LEAK_ACCEPTED")
    except Exception as exc:  # verifier records the typed failure but does not hide it
        code = getattr(exc, "code", type(exc).__name__)
        record(evidence, "refused", "benchmark-reference-leak", code=str(code))
        must(code == "REFERENCE_SOLUTION_LEAK_REFUSED", "REFERENCE_LEAK_WRONG_REFUSAL")

    problem_raw = json.loads((HERE / "fixtures/career-capabilities.json").read_text(encoding="utf-8"))
    problem = CapabilityProblem.from_mapping(problem_raw)
    plan = solve_capability_astar(problem)
    record(evidence, "executed", "bounded-reference-astar", steps=len(plan.steps), total_cost=plan.total_cost)
    must(plan.solved and problem.goals <= set(plan.final_admitted), "BOUNDED_REFERENCE_SEARCH_FAILED")

    mfw = project_mfw_request(problem)
    record(
        evidence,
        "verified",
        "mfw-universal-projection",
        states=len(mfw["problem"]["states"]),
        transitions=len(mfw["problem"]["transitions"]),
        planner_families=len(MFW_PLANNING_TYPES),
    )
    must(len(MFW_PLANNING_TYPES) == 18, "MFW_FAMILY_INVENTORY_DRIFT")
    must(len(mfw["problem"]["transitions"]) > len(plan.steps), "MFW_GRAPH_NOT_COMBINATORIAL")

    powl = project_powl(plan, benchmark_id=goal.benchmark_id)
    record(evidence, "verified", "powl-projection", digest=sha256_value(powl))
    must("no execution authority" in powl, "POWL_ACTUATION_FENCE_MISSING")

    controller = RecursiveController(problem)
    parent = controller.start("forward-deployment")
    must(parent.state == State.BLOCKED, "RECURSIVE_PARENT_NOT_BLOCKED")
    record(
        evidence,
        "verified",
        "recursive-max-options",
        candidates=list(parent.candidate_children),
        selected=parent.selected_child,
    )
    # Drive the finite proof to completion through receipt-bound admissions only.
    while controller.tasks["task:forward-deployment"].state != State.ALIVE:
        ready = sorted(t.task_id for t in controller.tasks.values() if t.state == State.PARTIAL_ALIVE)
        if not ready:
            failures.append("RECURSIVE_CONTROLLER_DEADLOCK")
            break
        task_id = ready[0]
        intent = controller.manufacture_intent(task_id)
        receipt = {
            "verified": True,
            "subject": intent.capability_id,
            "verifier": "gl-plan-002-independent-fixture-verifier",
        }
        controller.verify_and_admit(task_id, receipt)
        # Replan all blocked ancestors; bounded fixture prevents infinite traversal.
        for candidate in sorted(controller.tasks):
            if controller.tasks[candidate].state == State.BLOCKED:
                controller.replan(candidate)
    snapshot = controller.snapshot()
    replay = replay_event_chain(snapshot["events"])
    record(evidence, "executed", "orchestration-replay", events=replay["events_replayed"])
    must(replay["valid"], "ORCHESTRATION_REPLAY_FAILED")
    must(controller.tasks["task:forward-deployment"].state == State.ALIVE, "PARENT_DID_NOT_RESUME")

    # Preserve unsupported topology from the previous planner corpus if its exact source
    # is materialized. Absence is a typed sparse-tree transport limitation, not success.
    legacy_core = ROOT / "planning/v26.8.1/domains/ggen-v2681-core.pddl"
    if legacy_core.exists():
        feature_report = classify_pddl_features(legacy_core.read_text(encoding="utf-8"))
        record(evidence, "observed", "v26.8.1-core-pddl", requirements=feature_report["requirements"])
        if feature_report["unsupported_requirements"]:
            record(
                evidence,
                "unsupported",
                "skdecide-v26.8.1-feature-edge",
                requirements=feature_report["unsupported_requirements"],
                simplified=feature_report["simplified"],
            )
        must(feature_report["simplified"] is False, "LEGACY_PDDL_WAS_SIMPLIFIED")
    else:
        record(evidence, "blocked", "v26.8.1-core-pddl", code="SPARSE_TREE_SOURCE_NOT_MATERIALIZED")

    profiles = load_profiles(HERE / "engines.toml")
    must(set(profiles) == {"skdecide_astar", "fast_downward_lama", "val_validator"}, "ENGINE_REGISTRY_DRIFT")
    for role, profile in sorted(profiles.items()):
        probe = probe_engine(profile)
        record(evidence, "executed", f"engine-probe:{role}", receipt=probe.as_mapping())
        if probe.outcome == EngineOutcome.MISSING_BINARY:
            record(evidence, "blocked", f"engine:{role}", code="ENGINE_BINARY_UNAVAILABLE")
        elif probe.outcome not in (EngineOutcome.SUCCESS,):
            record(evidence, "unsupported", f"engine:{role}", outcome=probe.outcome.value)

    # Execute the actual skdecide wrapper against the exact fixture. If the Python package
    # is absent, exit 2 is evidence of fail-closed dependency refusal, never solver ALIVE.
    with tempfile.TemporaryDirectory(prefix="gl-plan-002-") as td:
        receipt = run_engine(
            profiles["skdecide_astar"],
            domain=HERE / "fixtures/career-domain.pddl",
            problem=HERE / "fixtures/career-problem.pddl",
            plan=Path(td) / "plan.val",
            timeout_s=20.0,
        )
        record(evidence, "executed", "skdecide-classical-engine", receipt=receipt.as_mapping())
        if receipt.outcome == EngineOutcome.SUCCESS:
            record(evidence, "verified", "skdecide-classical-engine", outcome="success")
        elif receipt.outcome in (EngineOutcome.PARSE_REFUSED, EngineOutcome.MISSING_BINARY):
            record(evidence, "blocked", "skdecide-classical-engine", code="SKDECIDE_RUNTIME_UNAVAILABLE")
        else:
            failures.append(f"SKDECIDE_UNEXPECTED_OUTCOME:{receipt.outcome.value}")

    # The pinned MFW source contract is independently checkable; live cross-repo replay is
    # conditional on a sibling checkout and never inferred from the contract alone.
    mfw_contract = json.loads((HERE / "mfw-receiving-contract.json").read_text(encoding="utf-8"))
    must(mfw_contract["producer"]["commit"] == "e4fbda46f13d8213b86aa4f981d2387638983066", "MFW_PIN_DRIFT")
    must(tuple(mfw_contract["planning_types"]) == MFW_PLANNING_TYPES, "MFW_TYPE_CONTRACT_DRIFT")
    sibling_mfw = ROOT.parent / "mfw"
    if sibling_mfw.exists():
        record(evidence, "observed", "mfw-sibling-tree", path=str(sibling_mfw))
    else:
        record(evidence, "blocked", "mfw-live-replay", code="MFW_TREE_NOT_MOUNTED")

    report_state = State.BUILD_BROKEN if failures else State.PARTIAL_ALIVE
    report = {
        "schema": "ggen.legacy.planning-max-verifier-report.v1",
        "ticket": "GL-PLAN-002",
        "subject": "planning/v26.8.7",
        "state": report_state.value,
        "repository_crown_claimed": False,
        "authority": "subsystem-verifier-only",
        "evidence": evidence,
        "failures": failures,
    }
    report["report_digest"] = sha256_value(report)
    return (1 if failures else 0), report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="fail nonzero on any internal verifier failure")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    code, report = run()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return code if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
