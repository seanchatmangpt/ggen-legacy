"""Shared typed states, refusals, and canonical receipt hashing for GL-PLAN-002."""
from __future__ import annotations
import hashlib
import json
from enum import Enum
from typing import Any

class State(str, Enum):
    UNKNOWN = "UNKNOWN"
    PARTIAL_ALIVE = "PARTIAL_ALIVE"
    ALIVE = "ALIVE"
    BLOCKED = "BLOCKED"
    BUILD_BROKEN = "BUILD_BROKEN"
    UNSUPPORTED = "UNSUPPORTED"
    REFUSED = "REFUSED"


class EngineOutcome(str, Enum):
    SUCCESS = "success"
    UNSOLVABLE = "unsolvable"
    PARSE_REFUSED = "parse_refused"
    TOOL_FAILED = "tool_failed"
    BOUNDED = "bounded"
    MISSING_BINARY = "missing_binary"
    NO_CANDIDATE = "no_candidate"
    VERSION_WITNESS_REFUSED = "version_witness_refused"


class PlanningError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_value(value: Any) -> str:
    if isinstance(value, bytes):
        payload = value
    elif isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()
