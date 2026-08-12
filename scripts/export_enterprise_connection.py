#!/usr/bin/env python3
"""Export admitted ggen-legacy foundry state as ConnectionEnvelope v1.

This is a CONSTRUCT-only transport projection. Native Foundry admission
reports are verified with the same BLAKE3-over-report-byte law used by ggen's
architecture-foundry producer. The report predicate map must exactly equal the
typed predicate map in the admitted work program; predicates are not assumed
to be booleans (for example, observation cardinalities are integer values).

The Connection separately uses SHA-256 as transport content identity. Native
BLAKE3 evidence and Connection SHA-256 identity are deliberately distinct.
`foundry/receipts/` is gitignored local/generated evidence, so a clean checkout
may corroborate those receipts when present but never requires them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
from typing import Any

try:
    from blake3 import blake3
except ImportError:  # pragma: no cover - exercised by the CLI refusal path
    blake3 = None

SCHEMA = "urn:ggen:enterprise-connection:v1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class Refusal(ValueError):
    pass


def _transport_digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _native_report_digest(data: bytes) -> str:
    if blake3 is None:
        raise Refusal(
            "UNSUPPORTED:BLAKE3_BINDING:install requirements-connection.txt"
        )
    return blake3(data).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _safe_rel(value: str) -> bool:
    normalized = value.replace("\\", "/")
    p = PurePosixPath(normalized)
    w = PureWindowsPath(value)
    return (
        bool(value)
        and not p.is_absolute()
        and not w.is_absolute()
        and not w.drive
        and ".." not in p.parts
    )


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Refusal(f"REFUSED:INPUT:{path}:{exc}") from exc
    if not isinstance(value, dict):
        raise Refusal(f"REFUSED:INPUT:{path}:expected object")
    return value


def _artifact(
    root: Path,
    relative: str,
    role: str,
    media_type: str,
) -> dict[str, str]:
    if not _safe_rel(relative):
        raise Refusal(f"REFUSED:UNSAFE_PATH:{relative}")
    path = root / relative
    if not path.is_file():
        raise Refusal(f"REFUSED:EVIDENCE_MISSING:{relative}")
    return {
        "path": relative,
        "role": role,
        "media_type": media_type,
        "digest": _transport_digest(path.read_bytes()),
    }


def _program_workstreams(program: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = program.get("workstreams")
    if not isinstance(raw, list) or not raw:
        raise Refusal("REFUSED:PROGRAM_WORKSTREAMS")
    mapped: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            raise Refusal("REFUSED:PROGRAM_WORKSTREAM")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise Refusal("REFUSED:PROGRAM_WORKSTREAM_ID")
        if identifier in mapped:
            raise Refusal(f"REFUSED:DUPLICATE_PROGRAM_WORKSTREAM:{identifier}")
        predicates = item.get("predicates")
        if not isinstance(predicates, dict) or not predicates:
            raise Refusal(f"REFUSED:PROGRAM_WORKSTREAM_PREDICATES:{identifier}")
        mapped[identifier] = item
    return mapped


def _admission_report(
    root: Path,
    name: str,
    item: dict[str, Any],
    expected_predicates: dict[str, Any],
) -> tuple[dict[str, str], dict[str, Any], str]:
    expected_digest = item.get("report_digest")
    if not isinstance(expected_digest, str) or not HEX64.fullmatch(expected_digest):
        raise Refusal(f"REFUSED:ADMITTED_WITHOUT_REPORT_DIGEST:{name}")

    relative = f"foundry/workstreams/{name}/admission-report.json"
    path = root / relative
    artifact = _artifact(
        root,
        relative,
        f"ggen-legacy:workstream-{name}-admission-report",
        "application/json",
    )
    actual_native = _native_report_digest(path.read_bytes())
    if actual_native != expected_digest:
        raise Refusal(
            "REFUSED:ADMISSION_REPORT_DRIFT:"
            f"{name}:algorithm=BLAKE3:expected={expected_digest}:actual={actual_native}"
        )

    report = _read_object(path)
    if report.get("workstream_id") != name:
        raise Refusal(f"REFUSED:ADMISSION_REPORT_ID:{name}")
    predicates = report.get("predicates")
    if predicates != expected_predicates:
        raise Refusal(
            "REFUSED:ADMISSION_REPORT_PREDICATE_DRIFT:"
            f"{name}:expected={json.dumps(expected_predicates, sort_keys=True)}:"
            f"actual={json.dumps(predicates, sort_keys=True)}"
        )
    return artifact, report, actual_native


def export_connection(
    root: Path,
    revision: str,
    out: Path,
    connection_id: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    if not HEX40.fullmatch(revision):
        raise Refusal(f"REFUSED:REVISION:{revision}")

    program_path = root / "authority/foundry-work-program.json"
    state_path = root / "foundry/workstreams/state.json"
    program = _read_object(program_path)
    state = _read_object(state_path)
    if program.get("schema_version") != "ggen.enterprise-architecture-foundry.work-program/1":
        raise Refusal("REFUSED:PROGRAM_SCHEMA")
    if state.get("schema_version") != "ggen.enterprise-architecture-foundry.corpus/1":
        raise Refusal("REFUSED:STATE_SCHEMA")
    if program.get("program_id") != state.get("program_id"):
        raise Refusal("REFUSED:PROGRAM_ID_DRIFT")

    program_workstreams = _program_workstreams(program)
    workstreams = state.get("workstreams")
    if not isinstance(workstreams, dict) or not workstreams:
        raise Refusal("REFUSED:WORKSTREAM_STATE")
    admitted = sorted(
        str(name)
        for name, item in workstreams.items()
        if isinstance(item, dict) and item.get("status") == "ADMITTED"
    )

    graph_rel = "foundry/evidence/B/legacy-capabilities.ttl"
    graph_artifact = _artifact(
        root,
        graph_rel,
        "ggen-legacy:admitted-capability-graph",
        "text/turtle",
    )
    artifacts = [
        _artifact(
            root,
            "authority/foundry-work-program.json",
            "ggen-legacy:work-program",
            "application/json",
        ),
        _artifact(
            root,
            "foundry/workstreams/state.json",
            "ggen-legacy:workstream-state",
            "application/json",
        ),
        graph_artifact,
    ]
    evidence: list[dict[str, Any]] = []
    local_receipts_present: list[str] = []
    native_report_digests: list[str] = []

    for name in admitted:
        item = workstreams[name]
        program_workstream = program_workstreams.get(name)
        if program_workstream is None:
            raise Refusal(f"REFUSED:ADMITTED_WORKSTREAM_NOT_IN_PROGRAM:{name}")
        report_artifact, report, native_digest = _admission_report(
            root,
            name,
            item,
            program_workstream["predicates"],
        )
        artifacts.append(report_artifact)
        native_report_digests.append(f"{name}={native_digest}")
        evidence.append(
            {
                "kind": "foundry-workstream-admission-report",
                "identity": (
                    f"{name}:ADMITTED:{report.get('verifier', 'unknown-verifier')}:"
                    f"BLAKE3={native_digest}"
                ),
                "digest": report_artifact["digest"],
            }
        )

        receipt = item.get("receipt_path")
        if isinstance(receipt, str) and _safe_rel(receipt) and (root / receipt).is_file():
            receipt_artifact = _artifact(
                root,
                receipt,
                f"ggen-legacy:workstream-{name}-local-receipt",
                "application/json",
            )
            artifacts.append(receipt_artifact)
            evidence.append(
                {
                    "kind": "foundry-workstream-local-receipt",
                    "identity": f"{name}:LOCAL_RECEIPT",
                    "digest": receipt_artifact["digest"],
                }
            )
            local_receipts_present.append(name)

    capabilities = program.get("initial_solution_packs")
    invariants = program.get("invariants")
    if not isinstance(capabilities, list) or any(
        not isinstance(x, str) or not x for x in capabilities
    ):
        raise Refusal("REFUSED:CAPABILITY_SET")
    if not isinstance(invariants, list) or any(
        not isinstance(x, str) or not x for x in invariants
    ):
        raise Refusal("REFUSED:INVARIANT_SET")

    program_digest = _transport_digest(program_path.read_bytes())
    state_digest = _transport_digest(state_path.read_bytes())
    env = {
        "schema": SCHEMA,
        "connection_id": connection_id
        or f"urn:ggen:connection:{program['program_id']}",
        "stage": "RECONSTITUTE",
        "producer": {
            "repository": "seanchatmangpt/ggen-legacy",
            "revision": revision,
            "component": "GL-CONN-001",
        },
        "subject": {
            "id": str(program["program_id"]),
            "kind": "enterprise-architecture-reconstitution",
            "revision": program_digest,
        },
        "architecture": {
            "graph": {
                "path": graph_rel,
                "media_type": "text/turtle",
                "digest": graph_artifact["digest"],
            },
            "capabilities": sorted(set(capabilities)),
            "constraints": sorted(set(invariants)),
        },
        "packs": [],
        "artifacts": sorted(artifacts, key=lambda x: x["path"]),
        "authority": {"ceiling": "CONSTRUCT_ONLY", "do_authority": False},
        "standing": {
            "state": "PARTIAL_ALIVE" if admitted else "UNKNOWN",
            "claim": (
                f"NATIVE_BLAKE3_AND_PROGRAM_PREDICATES_VERIFIED={','.join(admitted) or 'NONE'}; "
                "LOCAL_RECEIPTS_ARE_OPTIONAL_IGNORED_EVIDENCE; "
                "CONNECTION_EXPORT_EXECUTED; COMPLETE_A_K_AND_EXTERNAL_PRODUCTION_NOT_INFERRED"
            ),
        },
        "parent": None,
        "evidence": sorted(evidence, key=lambda x: x["identity"]),
        "next": [
            {"consumer": "seanchatmangpt/ggen-create", "operation": "generalize"}
        ],
        "labels": {
            "program_status": str(program.get("status", "UNKNOWN")),
            "admitted_workstreams": ",".join(admitted),
            "native_report_digest_algorithm": "BLAKE3",
            "native_report_digests_verified": ";".join(native_report_digests),
            "program_predicates_verified": ",".join(admitted),
            "local_receipts_present": ",".join(local_receipts_present),
            "workstream_count": str(len(workstreams)),
            "program_transport_digest": program_digest,
            "state_transport_digest": state_digest,
        },
    }
    data = _canonical(env)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return env


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--revision", required=True)
    parser.add_argument("--connection-id")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        env = export_connection(args.root, args.revision, args.out, args.connection_id)
    except (Refusal, OSError) as exc:
        print(json.dumps({"standing": "REFUSED", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "standing": env["standing"]["state"],
                "stage": env["stage"],
                "out": str(args.out),
                "digest": _transport_digest(args.out.read_bytes()),
                "do_authority": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
