"""Immutable finite capability graph and deterministic A* checkpoint."""
from __future__ import annotations
import heapq
import itertools
from dataclasses import asdict, dataclass
from typing import Any, Mapping
from common import PlanningError, State

SCHEMA_VERSION = "ggen.legacy.planning.max.v1"

@dataclass(frozen=True, order=True)
class CapabilityFact:
    id: str
    category: str = "capability"
    cost: int = 1
    prerequisite_ids: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CapabilityFact":
        fact_id = str(value.get("id", "")).strip()
        if not fact_id:
            raise PlanningError("CAPABILITY_ID_REQUIRED", "capability id must be non-empty")
        cost = int(value.get("cost", 1))
        if cost < 0:
            raise PlanningError("NEGATIVE_COST_REFUSED", f"negative cost for {fact_id}")
        prereqs = tuple(sorted({str(v) for v in value.get("prerequisite_ids", [])}))
        if fact_id in prereqs:
            raise PlanningError("SELF_PREREQUISITE_REFUSED", f"{fact_id} depends on itself")
        return cls(
            id=fact_id,
            category=str(value.get("category", "capability")),
            cost=cost,
            prerequisite_ids=prereqs,
        )


@dataclass(frozen=True)
class CapabilityProblem:
    facts: tuple[CapabilityFact, ...]
    admitted: frozenset[str]
    goals: frozenset[str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CapabilityProblem":
        facts = tuple(CapabilityFact.from_mapping(v) for v in value.get("facts", []))
        ids = [f.id for f in facts]
        if len(ids) != len(set(ids)):
            raise PlanningError("DUPLICATE_CAPABILITY_REFUSED", "capability ids must be unique")
        known = set(ids)
        for fact in facts:
            unknown = set(fact.prerequisite_ids) - known
            if unknown:
                raise PlanningError(
                    "UNKNOWN_PREREQUISITE_REFUSED",
                    f"{fact.id} references unknown prerequisites: {sorted(unknown)}",
                )
        admitted = frozenset(map(str, value.get("admitted", [])))
        goals = frozenset(map(str, value.get("goals", [])))
        if not goals:
            raise PlanningError("GOAL_REQUIRED", "at least one goal capability is required")
        if admitted - known:
            raise PlanningError("UNKNOWN_ADMITTED_REFUSED", f"unknown admitted facts: {sorted(admitted-known)}")
        if goals - known:
            raise PlanningError("UNKNOWN_GOAL_REFUSED", f"unknown goals: {sorted(goals-known)}")
        return cls(facts=facts, admitted=admitted, goals=goals)

    @property
    def by_id(self) -> dict[str, CapabilityFact]:
        return {f.id: f for f in self.facts}


@dataclass(frozen=True)
class PlanStep:
    action: str
    capability_id: str
    cost: int
    before: tuple[str, ...]
    after: tuple[str, ...]


@dataclass(frozen=True)
class CandidatePlan:
    state: State
    solved: bool
    steps: tuple[PlanStep, ...]
    total_cost: int
    expanded: int
    final_admitted: tuple[str, ...]
    planner: str = "ggen-legacy.capability-astar/v1"

    def as_mapping(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA_VERSION,
            "planner": self.planner,
            "state": self.state.value,
            "solved": self.solved,
            "steps": [asdict(s) for s in self.steps],
            "total_cost": self.total_cost,
            "expanded": self.expanded,
            "final_admitted": list(self.final_admitted),
        }


def _heuristic(problem: CapabilityProblem, state: frozenset[str]) -> int:
    by_id = problem.by_id
    missing = problem.goals - state
    # Admissible lower bound when costs are non-negative: each missing goal must be
    # admitted at least once. Dependencies are deliberately not counted twice.
    return sum(by_id[g].cost for g in missing)


def solve_capability_astar(problem: CapabilityProblem, *, max_expansions: int = 100_000) -> CandidatePlan:
    """Deterministic finite A* over immutable admitted-capability sets.

    This is a harness checkpoint, not a substitute for the registered scikit-decide
    engine. It proves the career-capability search topology and orchestration logic.
    """
    start = problem.admitted
    by_id = problem.by_id
    if problem.goals <= start:
        return CandidatePlan(State.ALIVE, True, (), 0, 0, tuple(sorted(start)))

    counter = itertools.count()
    frontier: list[tuple[int, int, tuple[str, ...], int, frozenset[str]]] = []
    heapq.heappush(frontier, (_heuristic(problem, start), 0, tuple(sorted(start)), next(counter), start))
    best: dict[frozenset[str], int] = {start: 0}
    parent: dict[frozenset[str], tuple[frozenset[str], CapabilityFact]] = {}
    expanded = 0

    while frontier:
        _, g, _, _, state = heapq.heappop(frontier)
        if g != best.get(state):
            continue
        if problem.goals <= state:
            chain: list[tuple[frozenset[str], CapabilityFact, frozenset[str]]] = []
            cursor = state
            while cursor != start:
                prev, fact = parent[cursor]
                chain.append((prev, fact, cursor))
                cursor = prev
            chain.reverse()
            steps = tuple(
                PlanStep(
                    action="admit-capability",
                    capability_id=fact.id,
                    cost=fact.cost,
                    before=tuple(sorted(prev)),
                    after=tuple(sorted(after)),
                )
                for prev, fact, after in chain
            )
            return CandidatePlan(State.ALIVE, True, steps, g, expanded, tuple(sorted(state)))
        expanded += 1
        if expanded > max_expansions:
            return CandidatePlan(State.BLOCKED, False, (), 0, expanded, tuple(sorted(state)))
        applicable = sorted(
            (
                fact
                for fact in problem.facts
                if fact.id not in state and set(fact.prerequisite_ids) <= state
            ),
            key=lambda f: (f.cost, f.category, f.id),
        )
        for fact in applicable:
            nxt = frozenset((*state, fact.id))
            ng = g + fact.cost
            if ng < best.get(nxt, 1 << 60):
                best[nxt] = ng
                parent[nxt] = (state, fact)
                tie = tuple(sorted(nxt))
                heapq.heappush(frontier, (ng + _heuristic(problem, nxt), ng, tie, next(counter), nxt))

    return CandidatePlan(State.UNSUPPORTED, False, (), 0, expanded, tuple(sorted(start)))
