"""Candidate POWL/RDF and MFW universal graph projections; no execution authority."""
from __future__ import annotations
import hashlib
import json
import re
from typing import Any
from capability import CandidatePlan, CapabilityProblem
from common import sha256_value

def project_powl(plan: CandidatePlan, *, benchmark_id: str) -> str:
    """Project a candidate plan to POWL-like RDF/Turtle without execution semantics."""
    plan_digest = sha256_value(plan.as_mapping())
    lines = [
        "@prefix prov: <http://www.w3.org/ns/prov#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix pplan: <http://purl.org/net/p-plan#> .",
        "@prefix glp: <https://example.org/ggen-legacy/planning#> .",
        "",
        f"glp:plan-{_safe_id(benchmark_id)} a pplan:Plan, prov:Plan ;",
        f'  dcterms:identifier {json.dumps(benchmark_id)} ;',
        f'  dcterms:conformsTo "candidate projection only; no execution authority" ;',
        f'  glp:digest {json.dumps(plan_digest)} .',
        "",
    ]
    previous: str | None = None
    for index, step in enumerate(plan.steps, 1):
        sid = f"glp:step-{index:04d}"
        lines.extend(
            [
                f"{sid} a pplan:Step ;",
                f'  skos:prefLabel {json.dumps(step.capability_id)} ;',
                f'  glp:action "admit-capability" ;',
                f'  glp:cost "{step.cost}" ;',
                f"  pplan:isStepOfPlan glp:plan-{_safe_id(benchmark_id)}" + (" ;" if previous else " ."),
            ]
        )
        if previous:
            lines.append(f"  glp:precededBy {previous} .")
        lines.append("")
        previous = sid
    return "\n".join(lines)


def _safe_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-")
    return cleaned or "unnamed"


MFW_PLANNING_TYPES = (
    "classical",
    "cost_optimal",
    "numeric",
    "temporal",
    "preferences",
    "flow_constrained",
    "multi_agent",
    "rdf_derived",
    "probabilistic",
    "fond",
    "contingent",
    "hierarchical",
    "resolution_adaptive",
    "partial_order",
    "workflow",
    "a2a_delegated",
    "mcp_bound",
    "conformant",
)


def project_mfw_request(problem: CapabilityProblem) -> dict[str, Any]:
    """Project capability admission into MFW's versioned universal JSON edge."""
    # Generate a finite explicit state graph. This is deliberately combinatorial: all
    # reachable reversible states are retained, bounded by the finite capability set.
    by_id = problem.by_id
    seen = {problem.admitted}
    queue = [problem.admitted]
    states: list[dict[str, Any]] = []
    transitions: list[dict[str, Any]] = []
    while queue:
        state = queue.pop(0)
        sid = _state_id(state)
        states.append({"id": sid, "facts": sorted(state), "fluents": {}})
        for fact in sorted(problem.facts):
            if fact.id in state or not set(fact.prerequisite_ids) <= state:
                continue
            nxt = frozenset((*state, fact.id))
            transitions.append(
                {
                    "action": f"admit:{fact.id}",
                    "from": sid,
                    "to": _state_id(nxt),
                    "probability_ppm": 1_000_000,
                    "cost": fact.cost,
                }
            )
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return {
        "planning_type": "classical",
        "problem": {
            "states": sorted(states, key=lambda s: s["id"]),
            "initial_states": [_state_id(problem.admitted)],
            "goal": {"facts": sorted(problem.goals)},
            "transitions": sorted(transitions, key=lambda t: (t["from"], t["action"], t["to"])),
        },
    }


def _state_id(state: frozenset[str]) -> str:
    return "s-" + hashlib.sha256("\0".join(sorted(state)).encode()).hexdigest()[:16]
