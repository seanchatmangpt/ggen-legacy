"""Recursive max-options/min-WIP controller with exact-subject receipt admission and replay."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence
from capability import CapabilityProblem
from common import PlanningError, State, sha256_value

@dataclass(frozen=True)
class ManufactureIntent:
    intent_id: str
    parent_task_id: str
    child_task_id: str
    capability_id: str
    authority: str = "construct-only"
    actuation: str = "none"


@dataclass
class TaskNode:
    task_id: str
    capability_id: str
    parent_task_id: str | None
    state: State = State.UNKNOWN
    candidate_children: tuple[str, ...] = ()
    selected_child: str | None = None
    verification_receipt_digest: str | None = None


@dataclass(frozen=True)
class OrchestrationEvent:
    seq: int
    kind: str
    task_id: str
    data: Mapping[str, Any]
    previous_digest: str | None
    digest: str

    @classmethod
    def manufacture(
        cls,
        seq: int,
        kind: str,
        task_id: str,
        data: Mapping[str, Any],
        previous_digest: str | None,
    ) -> "OrchestrationEvent":
        body = {
            "seq": seq,
            "kind": kind,
            "task_id": task_id,
            "data": dict(data),
            "previous_digest": previous_digest,
        }
        return cls(seq, kind, task_id, dict(data), previous_digest, sha256_value(body))


class RecursiveController:
    """Pure parent/child search controller; emits intents, never actuates them."""

    def __init__(self, problem: CapabilityProblem):
        self.problem = problem
        self.admitted = set(problem.admitted)
        self.tasks: dict[str, TaskNode] = {}
        self.events: list[OrchestrationEvent] = []
        self._seq = 0

    def _emit(self, kind: str, task_id: str, **data: Any) -> OrchestrationEvent:
        previous = self.events[-1].digest if self.events else None
        event = OrchestrationEvent.manufacture(self._seq, kind, task_id, data, previous)
        self._seq += 1
        self.events.append(event)
        return event

    def start(self, capability_id: str) -> TaskNode:
        if capability_id not in self.problem.by_id:
            raise PlanningError("UNKNOWN_GOAL_REFUSED", capability_id)
        task_id = f"task:{capability_id}"
        node = self.tasks.setdefault(task_id, TaskNode(task_id, capability_id, None))
        self._emit("task_started", task_id, capability_id=capability_id)
        self.replan(task_id)
        return node

    def _direct_missing(self, capability_id: str) -> tuple[str, ...]:
        fact = self.problem.by_id[capability_id]
        return tuple(sorted(p for p in fact.prerequisite_ids if p not in self.admitted))

    def replan(self, task_id: str) -> TaskNode:
        node = self.tasks[task_id]
        if node.capability_id in self.admitted:
            node.state = State.ALIVE
            node.candidate_children = ()
            node.selected_child = None
            self._emit("task_alive", task_id, capability_id=node.capability_id)
            return node
        missing = self._direct_missing(node.capability_id)
        if not missing:
            node.state = State.PARTIAL_ALIVE
            self._emit("task_ready_to_manufacture", task_id, capability_id=node.capability_id)
            return node

        # Combinatorial maximalism: preserve every lawful direct child edge.
        child_ids = tuple(f"task:{cap}" for cap in missing)
        node.state = State.BLOCKED
        node.candidate_children = child_ids
        # Consequential WIP remains one: deterministic lowest-cost child is selected,
        # while every reversible option stays represented in candidate_children.
        by_id = self.problem.by_id
        selected_cap = min(missing, key=lambda cap: (by_id[cap].cost, by_id[cap].category, cap))
        selected = f"task:{selected_cap}"
        node.selected_child = selected
        for cap in missing:
            child_id = f"task:{cap}"
            self.tasks.setdefault(child_id, TaskNode(child_id, cap, task_id))
        self._emit(
            "task_blocked",
            task_id,
            candidates=list(child_ids),
            selected=selected,
            policy="max-options/min-wip",
        )
        self.replan(selected)
        return node

    def manufacture_intent(self, task_id: str) -> ManufactureIntent:
        node = self.tasks[task_id]
        if node.state != State.PARTIAL_ALIVE:
            raise PlanningError("TASK_NOT_MANUFACTURABLE_REFUSED", f"{task_id} state={node.state.value}")
        intent = ManufactureIntent(
            intent_id="intent:" + sha256_value({"task": task_id, "seq": self._seq}).split(":", 1)[1][:20],
            parent_task_id=node.parent_task_id or node.task_id,
            child_task_id=node.task_id,
            capability_id=node.capability_id,
        )
        self._emit("manufacture_intent", task_id, **asdict(intent))
        return intent

    def verify_and_admit(self, task_id: str, receipt: Mapping[str, Any]) -> TaskNode:
        """Consume independent verification; no verifier execution happens here."""
        node = self.tasks[task_id]
        if node.state != State.PARTIAL_ALIVE:
            raise PlanningError("TASK_NOT_READY_REFUSED", f"{task_id} state={node.state.value}")
        if receipt.get("verified") is not True:
            raise PlanningError("UNVERIFIED_CHILD_REFUSED", f"verification did not admit {task_id}")
        subject = str(receipt.get("subject", ""))
        if subject != node.capability_id:
            raise PlanningError("RECEIPT_SUBJECT_MISMATCH_REFUSED", f"expected {node.capability_id}, got {subject}")
        digest = sha256_value(receipt)
        node.verification_receipt_digest = digest
        self.admitted.add(node.capability_id)
        node.state = State.ALIVE
        self._emit("child_admitted", task_id, capability_id=node.capability_id, receipt_digest=digest)
        if node.parent_task_id:
            self._emit("parent_resumed", node.parent_task_id, admitted_child=task_id)
            self.replan(node.parent_task_id)
        return node

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": "ggen.legacy.orchestration-snapshot.v1",
            "policy": "max-options/min-wip",
            "admitted": sorted(self.admitted),
            "tasks": [
                {
                    **asdict(value),
                    "state": value.state.value,
                }
                for _, value in sorted(self.tasks.items())
            ],
            "events": [
                {
                    **asdict(event),
                    "data": dict(event.data),
                }
                for event in self.events
            ],
            "event_chain_digest": self.events[-1].digest if self.events else None,
        }


def replay_event_chain(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    previous: str | None = None
    findings: list[str] = []
    for expected_seq, raw in enumerate(events):
        if int(raw.get("seq", -1)) != expected_seq:
            findings.append(f"EVENT_{expected_seq}_SEQ_MISMATCH")
            break
        if raw.get("previous_digest") != previous:
            findings.append(f"EVENT_{expected_seq}_PREVIOUS_DIGEST_MISMATCH")
            break
        body = {
            "seq": expected_seq,
            "kind": raw.get("kind"),
            "task_id": raw.get("task_id"),
            "data": raw.get("data", {}),
            "previous_digest": previous,
        }
        digest = sha256_value(body)
        if raw.get("digest") != digest:
            findings.append(f"EVENT_{expected_seq}_DIGEST_MISMATCH")
            break
        previous = digest
    return {
        "schema": "ggen.legacy.replay-report.v1",
        "valid": not findings,
        "state": State.ALIVE.value if not findings else State.BUILD_BROKEN.value,
        "events_replayed": len(events) if not findings else max(0, len(events) - 1),
        "head_digest": previous,
        "findings": findings,
    }
