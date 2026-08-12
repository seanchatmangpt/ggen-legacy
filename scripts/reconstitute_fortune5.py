#!/usr/bin/env python3
"""GL-ERRC-003: deterministic Fortune-5 self-reconstitution observer/planner.

This program has no world-actuation authority. It observes the repository,
reconstructs the bounded product/enterprise obligation graph, classifies local
evidence, emits ERRC work orders, and writes a replayable receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

STANDINGS = {"UNKNOWN", "PARTIAL_ALIVE", "ALIVE", "BLOCKED", "BUILD_BROKEN", "UNSUPPORTED", "REFUSED"}
ERRC = {"ELIMINATE", "REDUCE", "RAISE", "CREATE"}
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ttl", ".rq", ".sparql",
    ".py", ".rs", ".sh", ".pddl", ".js", ".ts", ".tsx", ".jsx", ".html", ".css",
}
SKIP_PARTS = {".git", "target", "node_modules", "book", "__pycache__", ".ggen", ".ggen-v2"}
GENERATED_PREFIXES = ("foundry/generated/", "foundry/reports/", "foundry/receipts/", "evidence/reconstitution/")


class Refusal(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes())


def atomic_write(root: Path, rel: str, data: bytes) -> None:
    root = root.resolve()
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise Refusal("REFUSED:OUTPUT_ESCAPE")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, target)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Refusal(f"REFUSED:INVALID_JSON:{path.as_posix()}:{exc}") from exc


def git_head(root: Path) -> str:
    try:
        p = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False, timeout=5
        )
    except (OSError, subprocess.TimeoutExpired):
        return "UNKNOWN"
    return p.stdout.strip() if p.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", p.stdout.strip()) else "UNKNOWN"


@dataclass(frozen=True)
class ObjectRecord:
    object_id: str
    kind: str
    title: str
    source_path: str
    source_standing: str = "UNKNOWN"
    external_gate: bool = False


def parse_requirements(root: Path) -> list[ObjectRecord]:
    path = root / "product/PRD.md"
    text = read_text(path)
    rows: list[ObjectRecord] = []
    for m in re.finditer(r"^###\s+(PRD-FR-\d+)\s+—\s+(.+?)\s*$", text, re.MULTILINE):
        rows.append(ObjectRecord(m.group(1), "product_requirement", m.group(2), "product/PRD.md"))
    return rows


def parse_claims(root: Path, external_claims: set[str]) -> list[ObjectRecord]:
    path = root / "governance/claims-register.md"
    text = read_text(path)
    rows: list[ObjectRecord] = []
    for line in text.splitlines():
        if not line.startswith("| CLM-"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        object_id, title, _ceiling, standing = cells[:4]
        standing = standing.strip("`")
        if standing.startswith("REFUSED"):
            standing = "REFUSED"
        rows.append(
            ObjectRecord(
                object_id=object_id,
                kind="claim",
                title=title,
                source_path="governance/claims-register.md",
                source_standing=standing if standing in STANDINGS else "UNKNOWN",
                external_gate=object_id in external_claims,
            )
        )
    return rows


def parse_maturity(root: Path) -> list[ObjectRecord]:
    path = root / "governance/enterprise-maturity-model.md"
    text = read_text(path)
    rows: list[ObjectRecord] = []
    for m in re.finditer(r"^##\s+(EM-(\d{2}))\s+(.+?)\s*$", text, re.MULTILINE):
        dimension = m.group(1)
        title = m.group(3)
        for suffix, label in (("P", "Positive"), ("N", "Negative"), ("R", "Replay")):
            rows.append(
                ObjectRecord(
                    object_id=f"{dimension}-{suffix}",
                    kind="enterprise_obligation",
                    title=f"{title} — {label}",
                    source_path="governance/enterprise-maturity-model.md",
                )
            )
    return rows


def parse_workstreams(root: Path) -> list[ObjectRecord]:
    path = root / "foundry/bootstrap.yaml"
    data = load_json(path)
    rows: list[ObjectRecord] = []
    for raw in data.get("workstreams", []):
        wid = str(raw.get("id", ""))
        if not re.fullmatch(r"[A-K]", wid):
            raise Refusal(f"REFUSED:INVALID_WORKSTREAM:{wid}")
        status = str(raw.get("status", "UNKNOWN"))
        mapped = "PARTIAL_ALIVE" if status in {"IN_PROGRESS", "PARTIAL_ALIVE"} else status
        if mapped not in STANDINGS and mapped != "NOT_STARTED":
            mapped = "UNKNOWN"
        rows.append(ObjectRecord(f"FOUNDRY-{wid}", "foundry_workstream", f"Foundry workstream {wid}", "foundry/bootstrap.yaml", mapped))
    return rows


def normalized_exclusions(root: Path, contract: dict[str, Any]) -> set[str]:
    exclusions: set[str] = set()
    for raw in contract.get("evidence_exclusions", []):
        rel = str(raw)
        if not rel or rel.startswith("/") or ".." in Path(rel).parts:
            raise Refusal(f"REFUSED:INVALID_EVIDENCE_EXCLUSION:{rel}")
        target = root / rel
        if not target.is_file():
            raise Refusal(f"REFUSED:MISSING_EVIDENCE_EXCLUSION:{rel}")
        exclusions.add(Path(rel).as_posix())
    return exclusions


def iter_text_files(root: Path, excluded_paths: set[str] | None = None) -> Iterable[Path]:
    excluded_paths = excluded_paths or set()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel_path = path.relative_to(root)
        rel = rel_path.as_posix()
        if any(part in SKIP_PARTS for part in rel_path.parts):
            continue
        if rel.startswith(GENERATED_PREFIXES) or rel in excluded_paths:
            continue
        yield path


def evidence_class(rel: str) -> str:
    if rel.startswith("evidence/"):
        return "evidence"
    if rel.startswith(".github/workflows/"):
        return "workflow"
    if "/tests/" in f"/{rel}" or rel.startswith("tests/") or Path(rel).name.startswith("test_"):
        return "test"
    if rel.startswith(("src/", "scripts/", "tools/", "planning/")) and Path(rel).suffix in {".py", ".rs", ".sh"}:
        return "implementation"
    if rel.startswith(("authority/", "product/", "governance/", "architecture/", "foundry/", "tickets/")):
        return "authority"
    return "documentation"


def build_index(root: Path, ids: list[str], excluded_paths: set[str]) -> dict[str, dict[str, list[str]]]:
    needles = {i: re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(i)}(?![A-Za-z0-9_-])") for i in ids}
    classes = ("implementation", "test", "workflow", "evidence", "authority", "documentation")
    out = {i: {k: [] for k in classes} for i in ids}
    for path in iter_text_files(root, excluded_paths):
        rel = path.relative_to(root).as_posix()
        text = read_text(path)
        if not text:
            continue
        klass = evidence_class(rel)
        for oid, rx in needles.items():
            if rx.search(text):
                out[oid][klass].append(rel)
    for oid in out:
        for klass in out[oid]:
            out[oid][klass] = sorted(set(out[oid][klass]))
    return out


def computed_state(obj: ObjectRecord, evidence: dict[str, list[str]]) -> tuple[str, str, int, list[str]]:
    impl = bool(evidence["implementation"])
    tests = bool(evidence["test"])
    workflows = bool(evidence["workflow"])
    receipts = bool(evidence["evidence"])
    missing: list[str] = []
    if obj.external_gate:
        missing.append("independent external evidence")
        return "EXTERNAL_GATE", "RAISE", 0, missing
    if obj.kind == "enterprise_obligation":
        if not (impl or tests or workflows or receipts):
            return "DOCUMENTED_ONLY", "CREATE", 1, ["executable evidence"]
        if not tests:
            missing.append("negative/positive executable witness")
        if not receipts:
            missing.append("replay receipt")
        return (
            "LOCAL_EVIDENCE_PRESENT" if not missing else "LOCAL_EVIDENCE_PARTIAL",
            "REDUCE" if not missing else "RAISE",
            2 if not missing else 1,
            missing,
        )
    if not impl and not tests and not workflows and not receipts:
        return "DOCUMENTED_ONLY", "CREATE", 1, ["implementation", "test", "replay evidence"]
    if impl and not tests:
        return "IMPLEMENTED_UNVERIFIED", "RAISE", 1, ["independent test", "negative control", "replay evidence"]
    if tests and not receipts:
        return "TESTED_UNRECEIPTED", "RAISE", 2, ["replay/evidence receipt"]
    if (impl or workflows) and tests and receipts:
        return "LOCAL_EVIDENCE_COMPLETE", "REDUCE", 3, []
    return "LOCAL_EVIDENCE_PARTIAL", "RAISE", 1, ["implementation/test/evidence closure"]


def source_invariants(root: Path, contract: dict[str, Any], objects: list[ObjectRecord]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    expected = contract["expected_cardinality"]
    actual = {
        "product_requirements": sum(o.kind == "product_requirement" for o in objects),
        "claims": sum(o.kind == "claim" for o in objects),
        "maturity_dimensions": len({o.object_id[:5] for o in objects if o.kind == "enterprise_obligation"}),
        "maturity_obligations": sum(o.kind == "enterprise_obligation" for o in objects),
        "workstreams": sum(o.kind == "foundry_workstream" for o in objects),
    }
    for key, exp in expected.items():
        got = actual.get(key)
        if got != exp:
            raise Refusal(f"REFUSED:CARDINALITY_DRIFT:{key}:expected={exp}:observed={got}")

    ids = [o.object_id for o in objects]
    if len(ids) != len(set(ids)):
        seen: set[str] = set()
        dup: set[str] = set()
        for oid in ids:
            if oid in seen:
                dup.add(oid)
            seen.add(oid)
        raise Refusal("REFUSED:DUPLICATE_OBJECT:" + ",".join(sorted(dup)))

    workflow_dir = root / ".github/workflows"
    workflow_count = (
        len(list(workflow_dir.glob("*.yml"))) + len(list(workflow_dir.glob("*.yaml")))
        if workflow_dir.exists() else 0
    )
    expected_workflows = int(contract["expected_workflow_count"])
    if workflow_count != expected_workflows:
        raise Refusal(f"REFUSED:WORKFLOW_TOPOLOGY_DRIFT:expected={expected_workflows}:observed={workflow_count}")
    findings.append({"code": "WORKFLOW_TOPOLOGY", "state": "ALIVE", "observed": workflow_count})

    bootstrap = load_json(root / "foundry/bootstrap.yaml")
    statuses = [str(w.get("status", "UNKNOWN")) for w in bootstrap.get("workstreams", [])]
    claims = {o.object_id: o for o in objects if o.kind == "claim"}
    clm012 = claims.get("CLM-012")
    if statuses and all(s == "NOT_STARTED" for s in statuses) and clm012 and clm012.source_standing == "PARTIAL_ALIVE":
        findings.append({
            "code": "FOUNDRY_BOOTSTRAP_STATUS_LAG",
            "state": "PARTIAL_ALIVE",
            "operator": "RAISE",
            "reason": "bootstrap workstreams remain NOT_STARTED while CLM-012 is PARTIAL_ALIVE; authority must be re-admitted, not auto-promoted",
        })

    gap_path = root / "governance/production-gaps.md"
    receiving_path = root / "authority/ggen-create-receiving-contract.json"
    if gap_path.exists() and receiving_path.exists():
        gaps = read_text(gap_path)
        receiving = load_json(receiving_path)
        producer = receiving.get("producer", receiving.get("producer_identity", {}))
        current_commit = str(producer.get("commit", "")) if isinstance(producer, dict) else ""
        stale = re.search(r"producer pin .*?commit `([0-9a-f]{7,40})`", gaps, re.IGNORECASE | re.DOTALL)
        if stale and current_commit and not current_commit.startswith(stale.group(1)):
            findings.append({
                "code": "STALE_PRODUCTION_GAP_ASSERTION",
                "state": "PARTIAL_ALIVE",
                "operator": "ELIMINATE",
                "observed": stale.group(1),
                "current": current_commit,
                "reason": "historical blocker text no longer matches admitted producer coordinate",
            })
    return findings


def build(root: Path, contract_path: Path) -> dict[str, Any]:
    contract = load_json(contract_path)
    if contract.get("ticket") != "GL-ERRC-003":
        raise Refusal("REFUSED:WRONG_RECONSTITUTION_TICKET")
    external_claims = set(contract.get("external_claims", []))
    exclusions = normalized_exclusions(root, contract)
    objects = parse_requirements(root) + parse_claims(root, external_claims) + parse_maturity(root) + parse_workstreams(root)
    findings = source_invariants(root, contract, objects)
    index = build_index(root, [o.object_id for o in objects], exclusions)
    matrix: list[dict[str, Any]] = []
    queue: list[dict[str, Any]] = []
    for obj in sorted(objects, key=lambda x: x.object_id):
        evidence = index[obj.object_id]
        state, operator, level, missing = computed_state(obj, evidence)
        row = {
            "id": obj.object_id,
            "kind": obj.kind,
            "title": obj.title,
            "source_path": obj.source_path,
            "source_standing": obj.source_standing,
            "external_gate": obj.external_gate,
            "computed_state": state,
            "computed_level": level,
            "computed_standing_ceiling": "PARTIAL_ALIVE" if level >= 2 else "UNKNOWN",
            "errc_operator": operator,
            "missing": missing,
            "evidence": evidence,
        }
        matrix.append(row)
        if missing:
            priority = 0 if obj.external_gate else (1 if operator in {"CREATE", "RAISE"} else 2)
            queue.append({
                "priority": priority,
                "object_id": obj.object_id,
                "operator": operator,
                "reason": "; ".join(missing),
                "auto_executable": False,
                "authority": "CONSTRUCT_ONLY",
                "actuation": "REFUSED:AMBIENT_ACTUATION",
            })
    for finding in findings:
        if finding.get("operator") in ERRC:
            queue.append({
                "priority": 0 if finding["operator"] == "ELIMINATE" else 1,
                "object_id": finding["code"],
                "operator": finding["operator"],
                "reason": finding.get("reason", "reconstitution finding"),
                "auto_executable": False,
                "authority": "CONSTRUCT_ONLY",
                "actuation": "REFUSED:AMBIENT_ACTUATION",
            })
    queue.sort(key=lambda x: (x["priority"], x["operator"], x["object_id"]))
    counts = {
        "objects": len(matrix),
        "product_requirements": sum(r["kind"] == "product_requirement" for r in matrix),
        "claims": sum(r["kind"] == "claim" for r in matrix),
        "maturity_obligations": sum(r["kind"] == "enterprise_obligation" for r in matrix),
        "workstreams": sum(r["kind"] == "foundry_workstream" for r in matrix),
        "external_gates": sum(r["external_gate"] for r in matrix),
        "documented_only": sum(r["computed_state"] == "DOCUMENTED_ONLY" for r in matrix),
        "local_evidence_complete": sum(r["computed_state"] == "LOCAL_EVIDENCE_COMPLETE" for r in matrix),
        "work_orders": len(queue),
    }
    return {
        "schema": "ggen.legacy.errc.reconstitution.matrix/1",
        "ticket": "GL-ERRC-003",
        "repository": "seanchatmangpt/ggen-legacy",
        "subject_head": git_head(root),
        "claim_ceiling": contract["claim_ceiling"],
        "standing": "PARTIAL_ALIVE",
        "counts": counts,
        "findings": findings,
        "matrix": matrix,
        "work_queue": queue,
        "invariants": {
            "zero_unreceipted_actuation": True,
            "self_certification": False,
            "external_claims_auto_promoted": False,
            "generated_outputs_excluded_from_evidence": True,
            "reconstitution_source_excluded_from_evidence": True,
            "evidence_exclusions": sorted(exclusions),
        },
    }


def render_report(result: dict[str, Any]) -> str:
    c = result["counts"]
    lines = [
        "# Fortune 5 ERRC Self-Reconstitution",
        "",
        f"Subject: `{result['subject_head']}`",
        f"Standing: `{result['standing']}`",
        f"Claim ceiling: `{result['claim_ceiling']}`",
        "",
        "## Exact bounded inventory",
        "",
        f"- Product requirements: **{c['product_requirements']}**",
        f"- Claims: **{c['claims']}**",
        f"- Enterprise P/N/R obligations: **{c['maturity_obligations']}**",
        f"- Foundry A–K workstreams: **{c['workstreams']}**",
        f"- Total reconstitution objects: **{c['objects']}**",
        f"- External gates: **{c['external_gates']}**",
        f"- Work orders: **{c['work_orders']}**",
        "",
        "## Reconstitution findings",
        "",
    ]
    for finding in result["findings"]:
        suffix = f": {finding.get('reason', '')}" if finding.get("reason") else ""
        lines.append(f"- `{finding['code']}` — `{finding['state']}`{suffix}")
    lines += ["", "## Highest-priority ERRC work", ""]
    for item in result["work_queue"][:25]:
        lines.append(f"- P{item['priority']} `{item['operator']}` `{item['object_id']}` — {item['reason']}")
    lines += ["", "No work order has ambient actuation authority. Generated analysis cannot promote its own standing.", ""]
    return "\n".join(lines)


def write_outputs(root: Path, output: Path, contract_path: Path) -> dict[str, Any]:
    result = build(root, contract_path)
    matrix = dict(result)
    queue = matrix.pop("work_queue")
    products = {
        "matrix.json": canonical(matrix),
        "work-queue.json": canonical({"schema": "ggen.legacy.errc.work-queue/1", "ticket": "GL-ERRC-003", "items": queue}),
        "report.md": render_report(result).encode(),
    }
    source_paths = [
        "AGENTS.md", "RELEASE_CONTROL.md", "product/PRD.md", "architecture/ARD.md",
        "governance/claims-register.md", "governance/enterprise-maturity-model.md",
        "governance/production-gaps.md", "foundry/bootstrap.yaml", contract_path.relative_to(root).as_posix(),
        "scripts/reconstitute_fortune5.py", "scripts/verify_fortune5_reconstitution.py",
        "tickets/GL-ERRC-003.md", ".github/workflows/ci.yml",
    ]
    source_manifest = {path: file_sha(root / path) for path in source_paths if (root / path).exists()}
    output_manifest = {path: sha256(data) for path, data in sorted(products.items())}
    receipt = {
        "schema": "ggen.legacy.errc.reconstitution.receipt/1",
        "ticket": "GL-ERRC-003",
        "repository": "seanchatmangpt/ggen-legacy",
        "subject_head": result["subject_head"],
        "claim_ceiling": result["claim_ceiling"],
        "source_manifest": source_manifest,
        "output_manifest": output_manifest,
        "replay_identity": sha256(canonical({"sources": source_manifest, "outputs": output_manifest})),
        "standing": "PARTIAL_ALIVE",
        "actuation": "ANALYSIS_OUTPUT_DIRECTORY_ONLY",
        "external_production_standing": "UNKNOWN",
    }
    products["receipt.json"] = canonical(receipt)
    output.mkdir(parents=True, exist_ok=True)
    for rel, data in sorted(products.items()):
        atomic_write(output, rel, data)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = (args.contract or (root / "authority/fortune5-reconstitution.json")).resolve()
    try:
        receipt = write_outputs(root, args.output.resolve(), contract)
    except (OSError, Refusal) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
