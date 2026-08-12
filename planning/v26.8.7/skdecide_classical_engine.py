#!/usr/bin/env python3
"""MFW-compatible scikit-decide A* classical PDDL engine.

Contract:
    skdecide-classical-engine <domain.pddl> <problem.pddl> <plan-out>

Exit codes:
    0 solved and plan written
    2 PDDL/import/admission refusal
    3 unsolvable/no policy
    4 solver/runtime failure
    5 bounded step limit

The program has no shell or environment lookup path and writes only the supplied plan
file. `--help` and `--version` begin with VERSION_WITNESS_PREFIX.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

VERSION = "26.8.7"
VERSION_WITNESS_PREFIX = f"skdecide-classical-engine/{VERSION}"
MAX_STEPS = 100_000


def _help() -> str:
    return (
        f"{VERSION_WITNESS_PREFIX}\n"
        "usage: skdecide-classical-engine <domain.pddl> <problem.pddl> <plan-out>\n"
        "registered-solver: Astar\n"
        "domain: skdecide.hub.domain.pddl.PDDLDomain\n"
    )


def _write_plan(path: Path, actions: list[str], cost: int) -> None:
    if not path.parent.exists() or not path.parent.is_dir():
        raise ValueError("plan-out parent directory must already exist")
    body = "\n".join(actions)
    if body:
        body += "\n"
    body += f"; cost = {cost}\n"
    path.write_text(body, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args in (["--help"], ["-h"]):
        sys.stdout.write(_help())
        return 0
    if args == ["--version"]:
        sys.stdout.write(VERSION_WITNESS_PREFIX + "\n")
        return 0
    if len(args) != 3:
        sys.stderr.write("REFUSED:CLI_ARITY\n")
        sys.stderr.write(_help())
        return 2

    domain_path = Path(args[0])
    problem_path = Path(args[1])
    plan_path = Path(args[2])
    if not domain_path.is_file() or not problem_path.is_file():
        sys.stderr.write("REFUSED:PDDL_INPUT_MISSING\n")
        return 2
    if plan_path.exists() and not plan_path.is_file():
        sys.stderr.write("REFUSED:PLAN_PATH_NOT_FILE\n")
        return 2

    try:
        from skdecide import utils
        from skdecide.hub.domain.pddl import PDDLDomain
    except Exception as exc:  # import refusal is an admission failure, not build proof
        sys.stderr.write(f"REFUSED:SKDECIDE_UNAVAILABLE:{type(exc).__name__}\n")
        return 2

    try:
        domain = PDDLDomain(str(domain_path), str(problem_path))
        astar = utils.load_registered_solver("Astar")
    except Exception as exc:
        sys.stderr.write(f"REFUSED:PDDL_PARSE_OR_SOLVER_LOAD:{type(exc).__name__}\n")
        return 2

    actions: list[str] = []
    total_cost = 0
    try:
        with astar(domain_factory=lambda: domain) as solver:
            solver.solve()
            obs = domain.reset()
            seen: set[int] = set()
            for _ in range(MAX_STEPS):
                if domain._is_terminal(obs):
                    _write_plan(plan_path, actions, total_cost)
                    return 0
                state_hash = hash(obs)
                if state_hash in seen:
                    sys.stderr.write("UNSOLVABLE:POLICY_LOOP\n")
                    return 3
                seen.add(state_hash)
                try:
                    action = solver.sample_action(obs)
                except Exception as exc:
                    sys.stderr.write(f"UNSOLVABLE:NO_POLICY:{type(exc).__name__}\n")
                    return 3
                if action is None:
                    sys.stderr.write("UNSOLVABLE:NO_POLICY\n")
                    return 3
                outcome = domain.step(action)
                try:
                    transition_value = domain._get_transition_value(obs, action, outcome.observation)
                    total_cost += int(round(float(transition_value.cost)))
                except Exception:
                    # PDDLDomain's ordinary classical contract is unit-cost. Preserve a
                    # deterministic plan even when a custom Value cannot be coerced.
                    total_cost += 1
                actions.append(repr(action))
                obs = outcome.observation
            sys.stderr.write("BLOCKED:STEP_BOUND_EXHAUSTED\n")
            return 5
    except ValueError as exc:
        sys.stderr.write(f"REFUSED:PLAN_WRITE:{exc}\n")
        return 2
    except Exception as exc:
        sys.stderr.write(f"BUILD_BROKEN:SOLVER_RUNTIME:{type(exc).__name__}\n")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
