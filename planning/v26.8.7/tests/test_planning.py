from __future__ import annotations

import json
import stat
import subprocess
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from lib import (  # noqa: E402
    MFW_PLANNING_TYPES,
    CapabilityFact,
    CapabilityProblem,
    EngineOutcome,
    OutputMode,
    PlannerProfile,
    PlanningError,
    RecursiveController,
    State,
    classify_pddl_features,
    load_profiles,
    probe_engine,
    project_mfw_request,
    project_powl,
    reconstruct_goal,
    replay_event_chain,
    run_engine,
    solve_capability_astar,
    validate_val_plan,
)

FIXTURES = HERE / "fixtures"
ROOT = HERE.parents[1]


def load_problem() -> CapabilityProblem:
    return CapabilityProblem.from_mapping(
        json.loads((FIXTURES / "career-capabilities.json").read_text(encoding="utf-8"))
    )


class CapabilitySearchTests(unittest.TestCase):
    def test_capability_fact_is_immutable(self):
        fact = CapabilityFact("python")
        with self.assertRaises(FrozenInstanceError):
            fact.id = "rust"  # type: ignore[misc]

    def test_astar_solves_real_blocked_prerequisite_graph(self):
        plan = solve_capability_astar(load_problem())
        self.assertTrue(plan.solved)
        self.assertEqual(plan.state, State.ALIVE)
        self.assertEqual(plan.total_cost, 9)
        ids = [step.capability_id for step in plan.steps]
        self.assertEqual(set(ids), {"cloud", "distributed-systems", "agentic-architecture", "forward-deployment"})
        self.assertLess(ids.index("cloud"), ids.index("agentic-architecture"))
        self.assertLess(ids.index("distributed-systems"), ids.index("agentic-architecture"))
        self.assertLess(ids.index("agentic-architecture"), ids.index("forward-deployment"))

    def test_unknown_prerequisite_refused(self):
        with self.assertRaisesRegex(PlanningError, "unknown prerequisites"):
            CapabilityProblem.from_mapping(
                {"facts": [{"id": "x", "prerequisite_ids": ["missing"]}], "goals": ["x"]}
            )


class GoalReconstructionTests(unittest.TestCase):
    def test_goal_reconstruction_has_constraints_not_reference_solution(self):
        benchmark = json.loads((FIXTURES / "benchmark.json").read_text(encoding="utf-8"))
        goal = reconstruct_goal(benchmark)
        self.assertEqual(goal.benchmark_id, "career-capability-admission-v1")
        self.assertIn("forward-deployment", goal.required_facts)
        self.assertIn("unreceipted-actuation", goal.forbidden_facts)
        self.assertEqual(goal.state, State.PARTIAL_ALIVE)

    def test_reference_solution_leak_is_typed_refusal(self):
        benchmark = json.loads((FIXTURES / "benchmark-reference-leak.json").read_text(encoding="utf-8"))
        with self.assertRaises(PlanningError) as ctx:
            reconstruct_goal(benchmark)
        self.assertEqual(ctx.exception.code, "REFERENCE_SOLUTION_LEAK_REFUSED")


class PddlAndPlanTests(unittest.TestCase):
    def test_career_fixture_is_supported_strips(self):
        report = classify_pddl_features((FIXTURES / "career-domain.pddl").read_text(encoding="utf-8"))
        self.assertEqual(report["state"], State.PARTIAL_ALIVE.value)
        self.assertEqual(report["unsupported_requirements"], [])

    def test_legacy_advanced_features_remain_unsupported_not_simplified(self):
        text = "(define (domain x) (:requirements :strips :derived-predicates :constraints :preferences :fluents))"
        report = classify_pddl_features(text)
        self.assertEqual(report["state"], State.UNSUPPORTED.value)
        self.assertFalse(report["simplified"])
        self.assertEqual(
            set(report["unsupported_requirements"]),
            {":constraints", ":derived-predicates", ":fluents", ":preferences"},
        )

    def test_val_plan_shape(self):
        report = validate_val_plan("(admit-cloud)\n(admit-distributed-systems)\n; cost = 4\n")
        self.assertTrue(report["valid"])
        self.assertEqual(report["cost"], 4)
        self.assertEqual(report["actions"], ["admit-cloud", "admit-distributed-systems"])

    def test_val_plan_rejects_non_action_noise(self):
        report = validate_val_plan("this is not a plan\n")
        self.assertFalse(report["valid"])


class ProjectionTests(unittest.TestCase):
    def test_mfw_projection_preserves_all_reachable_edges(self):
        request = project_mfw_request(load_problem())
        self.assertEqual(request["planning_type"], "classical")
        self.assertGreater(len(request["problem"]["states"]), 4)
        self.assertGreater(len(request["problem"]["transitions"]), 4)
        self.assertIn("forward-deployment", request["problem"]["goal"]["facts"])

    def test_mfw_family_inventory_is_combinatorial(self):
        self.assertEqual(len(MFW_PLANNING_TYPES), 18)
        self.assertIn("partial_order", MFW_PLANNING_TYPES)
        self.assertIn("mcp_bound", MFW_PLANNING_TYPES)
        self.assertIn("a2a_delegated", MFW_PLANNING_TYPES)

    def test_powl_projection_has_no_execution_authority(self):
        plan = solve_capability_astar(load_problem())
        ttl = project_powl(plan, benchmark_id="career")
        self.assertIn("pplan:Plan", ttl)
        self.assertIn("candidate projection only; no execution authority", ttl)
        self.assertNotIn("broker:execute", ttl)


class RecursiveControllerTests(unittest.TestCase):
    def test_blocked_spawn_child_manufacture_verify_admit_resume_parent(self):
        ctl = RecursiveController(load_problem())
        ctl.start("forward-deployment")
        agentic = ctl.tasks["task:agentic-architecture"]
        self.assertEqual(agentic.state, State.BLOCKED)
        self.assertEqual(
            set(agentic.candidate_children),
            {"task:cloud", "task:distributed-systems"},
        )
        self.assertEqual(agentic.selected_child, "task:distributed-systems")

        # Selected child becomes manufacturable because python is already admitted.
        ctl.manufacture_intent("task:distributed-systems")
        ctl.verify_and_admit(
            "task:distributed-systems",
            {"verified": True, "subject": "distributed-systems", "verifier": "independent"},
        )
        self.assertEqual(ctl.tasks["task:agentic-architecture"].selected_child, "task:cloud")

        ctl.manufacture_intent("task:cloud")
        ctl.verify_and_admit("task:cloud", {"verified": True, "subject": "cloud"})
        self.assertEqual(ctl.tasks["task:agentic-architecture"].state, State.PARTIAL_ALIVE)

        ctl.manufacture_intent("task:agentic-architecture")
        ctl.verify_and_admit(
            "task:agentic-architecture",
            {"verified": True, "subject": "agentic-architecture"},
        )
        self.assertEqual(ctl.tasks["task:forward-deployment"].state, State.PARTIAL_ALIVE)

        ctl.manufacture_intent("task:forward-deployment")
        ctl.verify_and_admit(
            "task:forward-deployment",
            {"verified": True, "subject": "forward-deployment"},
        )
        self.assertEqual(ctl.tasks["task:forward-deployment"].state, State.ALIVE)
        kinds = [e.kind for e in ctl.events]
        self.assertIn("task_blocked", kinds)
        self.assertIn("manufacture_intent", kinds)
        self.assertIn("child_admitted", kinds)
        self.assertIn("parent_resumed", kinds)

    def test_manufacture_is_intent_only(self):
        ctl = RecursiveController(load_problem())
        ctl.start("cloud")
        intent = ctl.manufacture_intent("task:cloud")
        self.assertEqual(intent.authority, "construct-only")
        self.assertEqual(intent.actuation, "none")
        self.assertNotIn("cloud", ctl.admitted)

    def test_receipt_subject_mismatch_refused(self):
        ctl = RecursiveController(load_problem())
        ctl.start("cloud")
        with self.assertRaises(PlanningError) as ctx:
            ctl.verify_and_admit("task:cloud", {"verified": True, "subject": "wrong"})
        self.assertEqual(ctx.exception.code, "RECEIPT_SUBJECT_MISMATCH_REFUSED")

    def test_empty_replay_is_valid_and_total(self):
        report = replay_event_chain([])
        self.assertTrue(report["valid"])
        self.assertEqual(report["events_replayed"], 0)
        self.assertIsNone(report["head_digest"])

    def test_snapshot_matches_declared_orchestration_schema(self):
        ctl = RecursiveController(load_problem())
        ctl.start("forward-deployment")
        snap = ctl.snapshot()
        self.assertEqual(snap["schema"], "ggen.legacy.orchestration-snapshot.v1")
        self.assertEqual(snap["policy"], "max-options/min-wip")
        self.assertIsInstance(snap["tasks"], list)

    def test_replay_detects_tamper(self):
        ctl = RecursiveController(load_problem())
        ctl.start("cloud")
        snap = ctl.snapshot()
        good = replay_event_chain(snap["events"])
        self.assertTrue(good["valid"])
        tampered = json.loads(json.dumps(snap["events"]))
        tampered[0]["data"]["capability_id"] = "tampered"
        bad = replay_event_chain(tampered)
        self.assertFalse(bad["valid"])
        self.assertIn("DIGEST_MISMATCH", bad["findings"][0])


class EngineBoundaryTests(unittest.TestCase):
    def test_registry_preserves_multiple_planner_edges(self):
        profiles = load_profiles(HERE / "engines.toml")
        self.assertEqual(set(profiles), {"skdecide_astar", "fast_downward_lama", "val_validator"})
        self.assertTrue(profiles["skdecide_astar"].version_witness_prefix.startswith("skdecide-classical-engine"))

    def test_skdecide_wrapper_help_has_stable_witness(self):
        engine = HERE / "skdecide_classical_engine.py"
        proc = subprocess.run([str(engine), "--help"], cwd=ROOT, capture_output=True, text=True, env={})
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.startswith("skdecide-classical-engine/26.8.7"))

    def test_skdecide_wrapper_refuses_missing_inputs_distinctly(self):
        engine = HERE / "skdecide_classical_engine.py"
        with tempfile.TemporaryDirectory() as td:
            plan = Path(td) / "plan.txt"
            proc = subprocess.run(
                [str(engine), "/missing/domain.pddl", "/missing/problem.pddl", str(plan)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env={},
            )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("REFUSED:PDDL_INPUT_MISSING", proc.stderr)

    def test_runner_success_receipt_with_bounded_fixture_process(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            helper = td_path / "engine.py"
            helper.write_text(
                "#!/usr/bin/env python3\n"
                "import pathlib,sys\n"
                "if sys.argv[1:]==['--help']:\n"
                " print('fixture-engine/1'); raise SystemExit(0)\n"
                "pathlib.Path(sys.argv[3]).write_text('(finish)\\n; cost = 1\\n')\n",
                encoding="utf-8",
            )
            helper.chmod(helper.stat().st_mode | stat.S_IXUSR)
            domain = td_path / "d.pddl"
            problem = td_path / "p.pddl"
            domain.write_text("(define (domain d))", encoding="utf-8")
            problem.write_text("(define (problem p))", encoding="utf-8")
            plan = td_path / "plan.txt"
            profile = PlannerProfile(
                role="fixture",
                program=str(helper),
                args=("{domain}", "{problem}", "{plan}"),
                version_witness_prefix="fixture-engine/",
                output_mode=OutputMode.FILE,
            )
            receipt = run_engine(profile, domain=domain, problem=problem, plan=plan)
            self.assertEqual(receipt.outcome, EngineOutcome.SUCCESS)
            self.assertIsNotNone(receipt.plan_digest)
            self.assertTrue(validate_val_plan(plan.read_text(encoding="utf-8"))["valid"])

    def test_probe_missing_binary_is_typed_not_exception(self):
        profile = PlannerProfile(
            role="missing",
            program="definitely-not-a-real-planner-binary-4c73d",
            args=("{domain}", "{problem}", "{plan}"),
        )
        receipt = probe_engine(profile)
        self.assertEqual(receipt.outcome, EngineOutcome.MISSING_BINARY)


class AuthoritySurfaceTests(unittest.TestCase):
    def test_manifest_and_engine_registry_are_parseable(self):
        import tomllib
        manifest = tomllib.loads((HERE / "manifest.toml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["ticket"], "GL-PLAN-002")
        self.assertEqual(manifest["standing_ceiling"], "PARTIAL_ALIVE")
        self.assertEqual(manifest["actuation_authority"], "none")

    def test_json_schemas_and_mfw_contract_are_parseable(self):
        for path in sorted((HERE / "schemas").glob("*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(value["$schema"], "https://json-schema.org/draft/2020-12/schema")
        contract = json.loads((HERE / "mfw-receiving-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["producer"]["commit"], "e4fbda46f13d8213b86aa4f981d2387638983066")
        self.assertEqual(tuple(contract["planning_types"]), MFW_PLANNING_TYPES)

    def test_ontology_uses_public_vocabulary_and_no_actuation_policy(self):
        ttl = (HERE / "ontology.ttl").read_text(encoding="utf-8")
        for prefix in ("prov:", "dcterms:", "skos:", "pplan:", "odrl:"):
            self.assertIn(prefix, ttl)
        self.assertIn("NoActuationPolicy", ttl)

    def test_concurrent_ticket_does_not_edit_generated_lsp_contract_surface(self):
        ticket = (ROOT / "tickets/GL-PLAN-002.md").read_text(encoding="utf-8")
        self.assertIn("GL-LSP-001", ticket)
        self.assertIn("outside this ticket", ticket)


if __name__ == "__main__":
    unittest.main()
