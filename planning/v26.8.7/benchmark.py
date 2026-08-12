"""Anti-leak benchmark goal reconstruction and non-destructive PDDL classification."""
from __future__ import annotations
import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence
from common import PlanningError, State, sha256_value

REFERENCE_LEAK_KEYS = frozenset(
    {
        "reference_solution",
        "gold_solution",
        "gold_patch",
        "answer_key",
        "hidden_solution",
        "expected_plan",
        "reference_plan",
    }
)


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key).lower()
            yield from _walk_keys(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            yield from _walk_keys(child)


@dataclass(frozen=True)
class GoalReconstruction:
    benchmark_id: str
    required_facts: tuple[str, ...]
    forbidden_facts: tuple[str, ...]
    invariants: tuple[str, ...]
    exclusions: tuple[str, ...]
    verifier_obligations: tuple[str, ...]
    source_digest: str
    state: State = State.PARTIAL_ALIVE

    def as_mapping(self) -> dict[str, Any]:
        return {
            "schema": "ggen.legacy.benchmark-goal.v1",
            **asdict(self),
            "state": self.state.value,
        }


def reconstruct_goal(benchmark: Mapping[str, Any]) -> GoalReconstruction:
    """Reconstruct admissible goal-state constraints without a reference solution."""
    leaking = sorted(REFERENCE_LEAK_KEYS & set(_walk_keys(benchmark)))
    if leaking:
        raise PlanningError(
            "REFERENCE_SOLUTION_LEAK_REFUSED",
            f"benchmark contains prohibited solution-bearing fields: {leaking}",
        )
    benchmark_id = str(benchmark.get("benchmark_id", "")).strip()
    if not benchmark_id:
        raise PlanningError("BENCHMARK_ID_REQUIRED", "benchmark_id is required")
    goal = benchmark.get("goal", {})
    if not isinstance(goal, Mapping):
        raise PlanningError("GOAL_SCHEMA_REFUSED", "goal must be an object")
    required = tuple(sorted({str(v) for v in goal.get("required_facts", [])}))
    forbidden = tuple(sorted({str(v) for v in goal.get("forbidden_facts", [])}))
    overlap = set(required) & set(forbidden)
    if overlap:
        raise PlanningError("CONTRADICTORY_GOAL_REFUSED", f"facts both required and forbidden: {sorted(overlap)}")
    if not required and not goal.get("verifier_obligations"):
        raise PlanningError("EMPTY_GOAL_REFUSED", "goal must include required facts or verifier obligations")
    return GoalReconstruction(
        benchmark_id=benchmark_id,
        required_facts=required,
        forbidden_facts=forbidden,
        invariants=tuple(sorted({str(v) for v in benchmark.get("invariants", [])})),
        exclusions=tuple(sorted({str(v) for v in benchmark.get("exclusions", [])})),
        verifier_obligations=tuple(sorted({str(v) for v in goal.get("verifier_obligations", [])})),
        source_digest=sha256_value(benchmark),
    )


SKDECIDE_SUPPORTED_REQUIREMENTS = frozenset(
    {":strips", ":typing", ":negative-preconditions", ":equality"}
)
# Features are preserved as topology. Detection does not rewrite/simplify the domain.
KNOWN_REQUIREMENTS = frozenset(
    {
        ":strips",
        ":typing",
        ":negative-preconditions",
        ":disjunctive-preconditions",
        ":equality",
        ":existential-preconditions",
        ":universal-preconditions",
        ":conditional-effects",
        ":derived-predicates",
        ":fluents",
        ":numeric-fluents",
        ":action-costs",
        ":preferences",
        ":constraints",
        ":durative-actions",
        ":duration-inequalities",
        ":continuous-effects",
        ":probabilistic-effects",
        ":hierarchy",
        ":method-preconditions",
    }
)


def classify_pddl_features(text: str) -> dict[str, Any]:
    stripped = re.sub(r";[^\n]*", "", text.lower())
    match = re.search(r"\(:requirements\s+([^)]*)\)", stripped, flags=re.S)
    requirements = tuple(sorted(set(re.findall(r":[a-z0-9_-]+", match.group(1) if match else ""))))
    unsupported = tuple(sorted(set(requirements) - SKDECIDE_SUPPORTED_REQUIREMENTS))
    unknown = tuple(sorted(set(requirements) - KNOWN_REQUIREMENTS))
    state = State.UNSUPPORTED if unsupported or unknown else State.PARTIAL_ALIVE
    return {
        "schema": "ggen.legacy.pddl-feature-classification.v1",
        "state": state.value,
        "requirements": list(requirements),
        "supported_requirements": sorted(SKDECIDE_SUPPORTED_REQUIREMENTS),
        "unsupported_requirements": list(unsupported),
        "unknown_requirements": list(unknown),
        "simplified": False,
    }
