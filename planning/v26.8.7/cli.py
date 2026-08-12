#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from lib import (  # noqa: E402
    CapabilityProblem,
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


def _load_json(path: str) -> dict:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _emit(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ggen-legacy-planning-max")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("reconstruct-goal")
    p.add_argument("benchmark")

    p = sub.add_parser("solve-capabilities")
    p.add_argument("problem")

    p = sub.add_parser("classify-pddl")
    p.add_argument("domain")

    p = sub.add_parser("project-mfw")
    p.add_argument("problem")

    p = sub.add_parser("project-powl")
    p.add_argument("problem")
    p.add_argument("benchmark_id")
    p.add_argument("out")

    p = sub.add_parser("orchestrate")
    p.add_argument("problem")
    p.add_argument("goal")

    p = sub.add_parser("replay")
    p.add_argument("snapshot")

    p = sub.add_parser("verify-plan")
    p.add_argument("plan")

    p = sub.add_parser("probe-engine")
    p.add_argument("registry")
    p.add_argument("role")

    p = sub.add_parser("run-engine")
    p.add_argument("registry")
    p.add_argument("role")
    p.add_argument("domain")
    p.add_argument("problem")
    p.add_argument("plan")
    p.add_argument("--timeout", type=float, default=60.0)

    args = parser.parse_args(argv)
    try:
        if args.command == "reconstruct-goal":
            _emit(reconstruct_goal(_load_json(args.benchmark)).as_mapping())
            return 0
        if args.command == "solve-capabilities":
            plan = solve_capability_astar(CapabilityProblem.from_mapping(_load_json(args.problem)))
            _emit(plan.as_mapping())
            return 0 if plan.solved else 3
        if args.command == "classify-pddl":
            _emit(classify_pddl_features(Path(args.domain).read_text(encoding="utf-8")))
            return 0
        if args.command == "project-mfw":
            _emit(project_mfw_request(CapabilityProblem.from_mapping(_load_json(args.problem))))
            return 0
        if args.command == "project-powl":
            problem = CapabilityProblem.from_mapping(_load_json(args.problem))
            plan = solve_capability_astar(problem)
            if not plan.solved:
                _emit(plan.as_mapping())
                return 3
            out = Path(args.out)
            out.write_text(project_powl(plan, benchmark_id=args.benchmark_id), encoding="utf-8")
            _emit({"state": State.PARTIAL_ALIVE.value, "projection": str(out), "execution_authority": "none"})
            return 0
        if args.command == "orchestrate":
            ctl = RecursiveController(CapabilityProblem.from_mapping(_load_json(args.problem)))
            ctl.start(args.goal)
            _emit(ctl.snapshot())
            return 0
        if args.command == "replay":
            snap = _load_json(args.snapshot)
            report = replay_event_chain(snap.get("events", []))
            _emit(report)
            return 0 if report["valid"] else 2
        if args.command == "verify-plan":
            report = validate_val_plan(Path(args.plan).read_text(encoding="utf-8"))
            _emit(report)
            return 0 if report["valid"] else 2
        if args.command in {"probe-engine", "run-engine"}:
            profiles = load_profiles(Path(args.registry))
            if args.role not in profiles:
                raise PlanningError("UNKNOWN_PLANNER_ROLE_REFUSED", args.role)
            profile = profiles[args.role]
            if args.command == "probe-engine":
                receipt = probe_engine(profile)
            else:
                receipt = run_engine(
                    profile,
                    domain=Path(args.domain),
                    problem=Path(args.problem),
                    plan=Path(args.plan),
                    timeout_s=args.timeout,
                )
            _emit(receipt.as_mapping())
            return 0 if receipt.outcome.value == "success" else 2
    except (PlanningError, OSError, json.JSONDecodeError) as exc:
        code = exc.code if isinstance(exc, PlanningError) else type(exc).__name__.upper()
        _emit({"state": State.REFUSED.value, "code": code, "message": str(exc)})
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
