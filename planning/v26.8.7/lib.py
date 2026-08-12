"""Public compatibility facade for the GL-PLAN-002 combinatorial-max planning substrate."""
from common import EngineOutcome, PlanningError, State, canonical_json, sha256_value
from capability import CapabilityFact, CapabilityProblem, CandidatePlan, PlanStep, solve_capability_astar
from benchmark import GoalReconstruction, classify_pddl_features, reconstruct_goal
from engines import EngineRunReceipt, OutputMode, PlannerProfile, load_profiles, probe_engine, run_engine, validate_val_plan
from projections import MFW_PLANNING_TYPES, project_mfw_request, project_powl
from orchestration import ManufactureIntent, OrchestrationEvent, RecursiveController, TaskNode, replay_event_chain

VERSION = "26.8.7"
SCHEMA_VERSION = "ggen.legacy.planning.max.v1"

__all__ = [
    "EngineOutcome", "PlanningError", "State", "canonical_json", "sha256_value",
    "CapabilityFact", "CapabilityProblem", "CandidatePlan", "PlanStep", "solve_capability_astar",
    "GoalReconstruction", "classify_pddl_features", "reconstruct_goal",
    "EngineRunReceipt", "OutputMode", "PlannerProfile", "load_profiles", "probe_engine", "run_engine", "validate_val_plan",
    "MFW_PLANNING_TYPES", "project_mfw_request", "project_powl",
    "ManufactureIntent", "OrchestrationEvent", "RecursiveController", "TaskNode", "replay_event_chain",
]
