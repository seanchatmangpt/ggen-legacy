"""Shell-free declared planner process boundaries and execution receipts."""
from __future__ import annotations
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping
from common import EngineOutcome, PlanningError, sha256_value
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

class OutputMode(str, Enum):
    FILE = "file"
    STDOUT = "stdout"
    NONE = "none"


@dataclass(frozen=True)
class PlannerProfile:
    role: str
    program: str
    args: tuple[str, ...]
    version_args: tuple[str, ...] = ("--help",)
    version_witness_prefix: str = ""
    output_mode: OutputMode = OutputMode.FILE
    success_codes: tuple[int, ...] = (0,)
    unsolvable_codes: tuple[int, ...] = (3,)
    parse_refusal_codes: tuple[int, ...] = (2,)

    @classmethod
    def from_table(cls, role: str, value: Mapping[str, Any]) -> "PlannerProfile":
        if "program" not in value:
            raise PlanningError("PLANNER_PROGRAM_REQUIRED", f"planner {role} has no program")
        return cls(
            role=role,
            program=str(value["program"]),
            args=tuple(map(str, value.get("args", []))),
            version_args=tuple(map(str, value.get("version_args", ["--help"]))),
            version_witness_prefix=str(value.get("version_witness_prefix", "")),
            output_mode=OutputMode(str(value.get("output_mode", "file"))),
            success_codes=tuple(map(int, value.get("success_codes", [0]))),
            unsolvable_codes=tuple(map(int, value.get("unsolvable_codes", [3]))),
            parse_refusal_codes=tuple(map(int, value.get("parse_refusal_codes", [2]))),
        )

    def resolve(self, *, domain: Path, problem: Path, plan: Path) -> tuple[str, ...]:
        values = {"{domain}": str(domain), "{problem}": str(problem), "{plan}": str(plan)}
        out: list[str] = []
        for arg in self.args:
            rendered = arg
            for marker, value in values.items():
                rendered = rendered.replace(marker, value)
            if "{" in rendered or "}" in rendered:
                raise PlanningError("UNKNOWN_ENGINE_PLACEHOLDER_REFUSED", f"unresolved planner arg: {arg}")
            out.append(rendered)
        return tuple(out)


def load_profiles(path: Path) -> dict[str, PlannerProfile]:
    if tomllib is None:  # pragma: no cover
        raise PlanningError("TOML_RUNTIME_UNAVAILABLE", "Python 3.11+ tomllib is required")
    with path.open("rb") as handle:
        value = tomllib.load(handle)
    return {role: PlannerProfile.from_table(role, table) for role, table in value.items()}


@dataclass(frozen=True)
class EngineRunReceipt:
    role: str
    program: str
    argv: tuple[str, ...]
    outcome: EngineOutcome
    exit_code: int | None
    duration_ms: int
    stdout_digest: str
    stderr_digest: str
    plan_digest: str | None
    version_witness: str | None = None

    def as_mapping(self) -> dict[str, Any]:
        value = asdict(self)
        value["outcome"] = self.outcome.value
        value["schema"] = "ggen.legacy.engine-run-receipt.v1"
        value["receipt_digest"] = sha256_value(value)
        return value


def _bounded_text(data: bytes, limit: int = 4096) -> str:
    return data[:limit].decode("utf-8", errors="replace")


def probe_engine(profile: PlannerProfile, *, timeout_s: float = 10.0) -> EngineRunReceipt:
    argv = (profile.program, *profile.version_args)
    start = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=timeout_s, shell=False, env={})
    except FileNotFoundError:
        return EngineRunReceipt(profile.role, profile.program, argv, EngineOutcome.MISSING_BINARY, None,
                                int((time.monotonic()-start)*1000), sha256_value(b""), sha256_value(b""), None)
    except subprocess.TimeoutExpired as exc:
        return EngineRunReceipt(profile.role, profile.program, argv, EngineOutcome.BOUNDED, None,
                                int((time.monotonic()-start)*1000), sha256_value(exc.stdout or b""),
                                sha256_value(exc.stderr or b""), None)
    witness_blob = (proc.stdout or b"") + (proc.stderr or b"")
    witness = _bounded_text(witness_blob).strip().splitlines()[0] if witness_blob.strip() else ""
    if profile.version_witness_prefix and not witness.startswith(profile.version_witness_prefix):
        outcome = EngineOutcome.VERSION_WITNESS_REFUSED
    elif proc.returncode in profile.success_codes:
        outcome = EngineOutcome.SUCCESS
    else:
        outcome = EngineOutcome.TOOL_FAILED
    return EngineRunReceipt(
        profile.role,
        profile.program,
        argv,
        outcome,
        proc.returncode,
        int((time.monotonic()-start)*1000),
        sha256_value(proc.stdout),
        sha256_value(proc.stderr),
        None,
        witness or None,
    )


def run_engine(
    profile: PlannerProfile,
    *,
    domain: Path,
    problem: Path,
    plan: Path,
    timeout_s: float = 60.0,
) -> EngineRunReceipt:
    """Execute exactly one declared planner edge, shell-free and fail-closed.

    The harness itself writes no world state. The only path the planner is authorized
    to create is the caller-supplied plan path.
    """
    domain = domain.resolve(strict=True)
    problem = problem.resolve(strict=True)
    plan = plan.resolve(strict=False)
    plan.parent.mkdir(parents=True, exist_ok=True)
    if plan.exists():
        plan.unlink()
    argv = (profile.program, *profile.resolve(domain=domain, problem=problem, plan=plan))
    start = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=timeout_s, shell=False, env={})
    except FileNotFoundError:
        return EngineRunReceipt(profile.role, profile.program, argv, EngineOutcome.MISSING_BINARY, None,
                                int((time.monotonic()-start)*1000), sha256_value(b""), sha256_value(b""), None)
    except subprocess.TimeoutExpired as exc:
        return EngineRunReceipt(profile.role, profile.program, argv, EngineOutcome.BOUNDED, None,
                                int((time.monotonic()-start)*1000), sha256_value(exc.stdout or b""),
                                sha256_value(exc.stderr or b""), None)
    if proc.returncode in profile.parse_refusal_codes:
        outcome = EngineOutcome.PARSE_REFUSED
    elif proc.returncode in profile.unsolvable_codes:
        outcome = EngineOutcome.UNSOLVABLE
    elif proc.returncode not in profile.success_codes:
        outcome = EngineOutcome.TOOL_FAILED
    elif profile.output_mode == OutputMode.FILE and (not plan.exists() or not plan.read_bytes().strip()):
        outcome = EngineOutcome.NO_CANDIDATE
    else:
        outcome = EngineOutcome.SUCCESS
    plan_digest = sha256_value(plan.read_bytes()) if plan.exists() else None
    return EngineRunReceipt(
        profile.role,
        profile.program,
        argv,
        outcome,
        proc.returncode,
        int((time.monotonic()-start)*1000),
        sha256_value(proc.stdout),
        sha256_value(proc.stderr),
        plan_digest,
    )


VAL_ACTION = re.compile(r"^\s*(?:\d+(?:\.\d+)?:\s*)?\(([-a-zA-Z0-9_]+)(?:\s+[-a-zA-Z0-9_?.]+)*\)(?:\s*\[[^]]+\])?\s*$")


def validate_val_plan(text: str) -> dict[str, Any]:
    actions: list[str] = []
    cost: int | None = None
    errors: list[str] = []
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith(";"):
            match = re.match(r";\s*cost\s*=\s*(\d+)\s*$", line, flags=re.I)
            if match:
                cost = int(match.group(1))
            continue
        match = VAL_ACTION.match(line)
        if not match:
            errors.append(f"PLAN_LINE_{line_no}_INVALID")
        else:
            actions.append(match.group(1))
    return {
        "schema": "ggen.legacy.val-plan-validation.v1",
        "valid": bool(actions) and not errors,
        "actions": actions,
        "cost": cost,
        "findings": errors,
        "digest": sha256_value(text),
    }
