#!/usr/bin/env python3
"""Independent structural verifier for the Chatman Ecosystem Architecture Corpus."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_STATES = {
    "PARTIAL_ALIVE",
    "ALIVE",
    "BLOCKED",
    "BUILD_BROKEN",
    "UNKNOWN",
    "UNSUPPORTED",
}


@dataclass(frozen=True)
class Finding:
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicate: set[str] = set()
    for value in values:
        if value in seen:
            duplicate.add(value)
        seen.add(value)
    return sorted(duplicate)


def structural_findings(data: dict[str, Any], architecture_text: str) -> list[Finding]:
    findings: list[Finding] = []

    if data.get("authority") != "AUTHORED_INPUT_ONLY":
        findings.append(Finding("AUTHORITY_ESCALATION", "authority must remain AUTHORED_INPUT_ONLY"))
    if data.get("direct_actuation") is not False:
        findings.append(Finding("DIRECT_ACTUATION", "ecosystem direct_actuation must be false"))
    if data.get("final_admission_allowed") is not False:
        findings.append(Finding("FINAL_ADMISSION_ESCALATION", "authored corpus cannot grant final admission"))
    if data.get("standing") == "ALIVE":
        findings.append(Finding("PREDECLARED_ALIVE", "authored input cannot predeclare ecosystem ALIVE"))

    defaults = data.get("defaults", {})
    capability_defaults = defaults.get("capability", {})
    repository_defaults = defaults.get("repository", {})
    relationship_defaults = defaults.get("relationship", {})

    if relationship_defaults.get("receipt_required") is not True:
        findings.append(Finding("UNRECEIPTED_RELATIONSHIP_DEFAULT", "relationship default must require receipts"))
    if relationship_defaults.get("direct_actuation") is not False:
        findings.append(Finding("DIRECT_ACTUATION_DEFAULT", "relationship default must refuse direct actuation"))
    if repository_defaults.get("validation_authority") != "REPOSITORY_OWNED":
        findings.append(Finding("VALIDATION_AUTHORITY_ESCALATION", "repository validation must remain repository-owned"))

    capabilities = data.get("capabilities", [])
    repositories = data.get("repositories", [])
    relationships = data.get("relationships", [])
    planes = data.get("planes", [])

    if len(capabilities) != 26:
        findings.append(Finding("CAPABILITY_CARDINALITY", f"expected 26 capabilities, observed {len(capabilities)}"))
    if len(repositories) != 19:
        findings.append(Finding("REPOSITORY_CARDINALITY", f"expected 19 repositories, observed {len(repositories)}"))

    capability_ids = [str(item.get("id", "")) for item in capabilities]
    repository_ids = [str(item.get("id", "")) for item in repositories]
    plane_ids = [str(item.get("id", "")) for item in planes]

    for duplicate in _duplicates(capability_ids):
        findings.append(Finding("DUPLICATE_CAPABILITY_ID", duplicate))
    for duplicate in _duplicates(repository_ids):
        findings.append(Finding("DUPLICATE_REPOSITORY_ID", duplicate))
    for duplicate in _duplicates([str(item.get("id", "")) for item in relationships]):
        findings.append(Finding("DUPLICATE_RELATIONSHIP_ID", duplicate))
    for duplicate in _duplicates(plane_ids):
        findings.append(Finding("DUPLICATE_PLANE_ID", duplicate))

    capability_set = set(capability_ids)
    repository_set = set(repository_ids)
    plane_set = set(plane_ids)

    for capability in capabilities:
        cid = str(capability.get("id", ""))
        if capability.get("plane") not in plane_set:
            findings.append(Finding("UNKNOWN_CAPABILITY_PLANE", f"{cid}: {capability.get('plane')}"))
        current = capability.get("repository_realizations", [])
        external = capability.get("external_realizations", [])
        if not current and not external:
            findings.append(Finding("CAPABILITY_WITHOUT_REALIZATION", cid))
        for repository in current:
            if repository not in repository_set:
                findings.append(Finding("UNKNOWN_REPOSITORY_REALIZATION", f"{cid}: {repository}"))
        can_actuate = capability.get("can_actuate", capability_defaults.get("can_actuate"))
        if cid == "brce":
            if can_actuate is not True:
                findings.append(Finding("BRCE_ACTUATION_DISABLED", "BRCE must be the sole actuation capability"))
        elif can_actuate is not False:
            findings.append(Finding("NON_BRCE_ACTUATION", cid))
        if not capability.get("authority_denied"):
            findings.append(Finding("MISSING_AUTHORITY_DENIAL", cid))
        standing = capability.get("standing", capability_defaults.get("standing"))
        evidence_refs = capability.get("evidence_refs", capability_defaults.get("evidence_refs", []))
        if standing not in ALLOWED_STATES:
            findings.append(Finding("INVALID_CAPABILITY_STANDING", f"{cid}: {standing}"))
        if standing == "ALIVE" and not evidence_refs:
            findings.append(Finding("ALIVE_WITHOUT_EVIDENCE", cid))
        if f"`{cid}`" not in architecture_text:
            findings.append(Finding("UNDOCUMENTED_CAPABILITY", cid))

    for repository in repositories:
        rid = str(repository.get("id", ""))
        for cid in repository.get("capabilities_realized", []):
            if cid not in capability_set:
                findings.append(Finding("UNKNOWN_REPOSITORY_CAPABILITY", f"{rid}: {cid}"))
        transport_only = repository.get("transport_lineage_only", repository_defaults.get("transport_lineage_only"))
        product_authority = repository.get("product_authority", repository_defaults.get("product_authority"))
        if transport_only is True and product_authority is not False:
            findings.append(Finding("TRANSPORT_PROMOTED", rid))
        if repository.get("validation_authority", repository_defaults.get("validation_authority")) != "REPOSITORY_OWNED":
            findings.append(Finding("VALIDATION_AUTHORITY_ESCALATION", rid))
        standing = repository.get("standing", repository_defaults.get("standing"))
        if standing not in ALLOWED_STATES:
            findings.append(Finding("INVALID_REPOSITORY_STANDING", rid))

    for relationship in relationships:
        rid = str(relationship.get("id", ""))
        source = relationship.get("source")
        target = relationship.get("target")
        if source not in capability_set:
            findings.append(Finding("UNKNOWN_RELATIONSHIP_SOURCE", f"{rid}: {source}"))
        if target not in capability_set:
            findings.append(Finding("UNKNOWN_RELATIONSHIP_TARGET", f"{rid}: {target}"))
        if source == target:
            findings.append(Finding("SELF_CERTIFICATION_PATH", f"{rid}: {source}"))
        if relationship.get("receipt_required", relationship_defaults.get("receipt_required")) is not True:
            findings.append(Finding("UNRECEIPTED_RELATIONSHIP", rid))
        if relationship.get("direct_actuation", relationship_defaults.get("direct_actuation")) is not False:
            findings.append(Finding("DIRECT_ACTUATION_RELATIONSHIP", rid))
        if not relationship.get("contract"):
            findings.append(Finding("RELATIONSHIP_WITHOUT_CONTRACT", rid))
        if relationship.get("relation") == "computes-bounded-standing-for" and source != "verifier-ladder":
            findings.append(Finding("SELF_CERTIFICATION_PATH", f"{rid}: standing source {source}"))
        authority_transfer = relationship.get("authority_transfer", relationship_defaults.get("authority_transfer"))
        if authority_transfer is True:
            admitted = (
                source == "mfw"
                and target == "brce"
                and relationship.get("relation") == "requests-execution-grant-from"
            )
            if not admitted:
                findings.append(Finding("UNADMITTED_AUTHORITY_TRANSFER", rid))

    for claim in data.get("standing_ledger", []):
        state = claim.get("state")
        if state not in ALLOWED_STATES:
            findings.append(Finding("INVALID_LEDGER_STANDING", str(claim.get("claim"))))
        if state == "ALIVE" and not claim.get("evidence_refs"):
            findings.append(Finding("ALIVE_WITHOUT_EVIDENCE", str(claim.get("claim"))))

    required_boundaries = {
        "ZERO_UNRECEIPTED_ACTUATION",
        "OBSERVATION_IS_NOT_ADMISSION",
        "CONSTRUCTION_IS_NOT_ACTUATION",
        "NO_SELF_CERTIFICATION",
        "CHECKPOINT_IS_NOT_CROWN",
        "REPOSITORIES_REALIZE_CAPABILITIES",
        "COHORT_IS_NOT_ECOSYSTEM",
    }
    boundary_names = {item.get("name") for item in data.get("boundaries", [])}
    for missing in sorted(required_boundaries - boundary_names):
        findings.append(Finding("MISSING_BOUNDARY", missing))

    return findings


def validate_json_schema(data_path: Path, schema_path: Path) -> tuple[str, str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return "UNSUPPORTED", "jsonschema is not installed"
    jsonschema.Draft202012Validator(load_json(schema_path)).validate(load_json(data_path))
    return "PASS", "Draft 2020-12 validation passed"


def build_rdf_graph(data: dict[str, Any]) -> Any:
    from rdflib import Graph, Literal, Namespace, RDF, URIRef  # type: ignore
    from rdflib.namespace import DCTERMS, PROV, SKOS, XSD  # type: ignore

    ce = Namespace("https://chatmangpt.com/ns/ecosystem#")
    graph = Graph()
    graph.bind("ce", ce)
    graph.bind("dcterms", DCTERMS)
    graph.bind("prov", PROV)
    graph.bind("skos", SKOS)

    ecosystem = ce["chatman-ecosystem"]
    graph.add((ecosystem, RDF.type, ce.Ecosystem))
    graph.add((ecosystem, DCTERMS.identifier, Literal(data["corpus_id"])))
    graph.add((ecosystem, DCTERMS.title, Literal(data["title"])))
    graph.add((ecosystem, ce.authorityClass, Literal(data["authority"])))
    graph.add((ecosystem, ce.directActuation, Literal(False, datatype=XSD.boolean)))
    graph.add((ecosystem, ce.finalAdmissionAllowed, Literal(False, datatype=XSD.boolean)))
    graph.add((ecosystem, ce.standing, Literal(data["standing"])))
    graph.add((
        ecosystem,
        PROV.wasDerivedFrom,
        URIRef(
            "https://github.com/seanchatmangpt/ggen-legacy/blob/"
            f"{data['corpus_base_sha']}/{data['source_cohort']}"
        ),
    ))

    for plane in data["planes"]:
        node = ce[plane["id"].lower()]
        graph.add((node, RDF.type, ce.CapabilityPlane))
        graph.add((node, DCTERMS.identifier, Literal(plane["id"])))
        graph.add((node, SKOS.prefLabel, Literal(plane["name"])))
        graph.add((ecosystem, ce.hasPlane, node))

    for capability in data["capabilities"]:
        node = ce[f"capability/{capability['id']}"]
        graph.add((node, RDF.type, ce.Capability))
        graph.add((node, DCTERMS.identifier, Literal(capability["id"])))
        graph.add((node, SKOS.prefLabel, Literal(capability["name"])))
        graph.add((node, DCTERMS.description, Literal(capability["purpose"])))
        graph.add((node, ce.inPlane, ce[capability["plane"].lower()]))
        graph.add((node, ce.canActuate, Literal(capability.get("can_actuate", data["defaults"]["capability"]["can_actuate"]), datatype=XSD.boolean)))
        graph.add((node, ce.standing, Literal(capability.get("standing", data["defaults"]["capability"]["standing"]))))
        graph.add((ecosystem, ce.hasCapability, node))
        for denied in capability["authority_denied"]:
            graph.add((node, ce.deniesAuthority, Literal(denied)))
        for repository in capability.get("repository_realizations", []):
            graph.add((node, ce.realizedBy, ce[f"repository/{repository}"]))

    for repository in data["repositories"]:
        node = ce[f"repository/{repository['id']}"]
        graph.add((node, RDF.type, ce.RepositoryRealization))
        graph.add((node, DCTERMS.identifier, Literal(repository["id"])))
        graph.add((node, ce.role, Literal(repository["role"])))
        graph.add((node, ce.productAuthority, Literal(repository.get("product_authority", data["defaults"]["repository"]["product_authority"]), datatype=XSD.boolean)))
        graph.add((node, ce.transportLineageOnly, Literal(repository.get("transport_lineage_only", data["defaults"]["repository"]["transport_lineage_only"]), datatype=XSD.boolean)))
        graph.add((ecosystem, ce.hasRepositoryRealization, node))

    relationship_defaults = data["defaults"]["relationship"]
    for relationship in data["relationships"]:
        node = ce[f"relationship/{relationship['id']}"]
        graph.add((node, RDF.type, ce.CapabilityRelationship))
        graph.add((node, DCTERMS.identifier, Literal(relationship["id"])))
        graph.add((node, ce.sourceCapability, ce[f"capability/{relationship['source']}"]))
        graph.add((node, ce.targetCapability, ce[f"capability/{relationship['target']}"]))
        graph.add((node, ce.relationshipType, Literal(relationship["relation"])))
        graph.add((node, ce.contract, Literal(relationship["contract"])))
        graph.add((node, ce.authorityTransfer, Literal(relationship.get("authority_transfer", relationship_defaults["authority_transfer"]), datatype=XSD.boolean)))
        graph.add((node, ce.receiptRequired, Literal(relationship_defaults["receipt_required"], datatype=XSD.boolean)))
        graph.add((node, ce.directActuation, Literal(relationship_defaults["direct_actuation"], datatype=XSD.boolean)))
        graph.add((node, ce.standing, Literal(relationship.get("standing", relationship_defaults["standing"]))))

    return graph


def validate_rdf(data: dict[str, Any], shapes_ttl: Path, strict_tools: bool) -> list[dict[str, str]]:
    try:
        from rdflib import Graph  # type: ignore
    except ImportError:
        status = "FAIL" if strict_tools else "UNSUPPORTED"
        return [{"check": "rdf-projection", "status": status, "detail": "rdflib is not installed"}]

    graph = build_rdf_graph(data)
    shapes_graph = Graph()
    shapes_graph.parse(shapes_ttl, format="turtle")
    checks = [{
        "check": "rdf-projection",
        "status": "PASS",
        "detail": f"{len(graph)} manufactured data triples; {len(shapes_graph)} shape triples",
    }]

    try:
        from pyshacl import validate  # type: ignore
    except ImportError:
        status = "FAIL" if strict_tools else "UNSUPPORTED"
        checks.append({"check": "shacl", "status": status, "detail": "pyshacl is not installed"})
        return checks

    conforms, _, report_text = validate(
        data_graph=graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        advanced=True,
    )
    checks.append({
        "check": "shacl",
        "status": "PASS" if conforms else "FAIL",
        "detail": "SHACL conformance passed" if conforms else str(report_text),
    })
    return checks


def verify(root: Path, strict_tools: bool = False) -> dict[str, Any]:
    data_path = root / "authority/chatman-ecosystem/ecosystem.json"
    schema_path = root / "authority/chatman-ecosystem/schemas/ecosystem.schema.json"
    architecture_path = root / "authority/chatman-ecosystem/architecture.md"
    shapes_ttl = root / "ontology/chatman-ecosystem/shapes.ttl"

    data = load_json(data_path)
    findings = structural_findings(data, architecture_path.read_text(encoding="utf-8"))
    checks: list[dict[str, str]] = [{
        "check": "structural-authority",
        "status": "PASS" if not findings else "FAIL",
        "detail": f"{len(findings)} finding(s)",
    }]

    try:
        schema_status, schema_detail = validate_json_schema(data_path, schema_path)
    except Exception as exc:
        schema_status, schema_detail = "FAIL", str(exc)
    if strict_tools and schema_status == "UNSUPPORTED":
        schema_status = "FAIL"
    checks.append({"check": "json-schema", "status": schema_status, "detail": schema_detail})

    try:
        checks.extend(validate_rdf(data, shapes_ttl, strict_tools))
    except Exception as exc:
        checks.append({"check": "rdf-shacl", "status": "FAIL", "detail": str(exc)})

    failed = [item for item in checks if item["status"] == "FAIL"]
    return {
        "schema_version": "chatman-ecosystem-verifier/v1",
        "subject": data.get("corpus_id"),
        "source_base_sha": data.get("corpus_base_sha"),
        "authority": data.get("authority"),
        "observed_counts": {
            "capabilities": len(data.get("capabilities", [])),
            "repositories": len(data.get("repositories", [])),
            "relationships": len(data.get("relationships", [])),
            "boundaries": len(data.get("boundaries", [])),
        },
        "checks": checks,
        "findings": [item.as_dict() for item in findings],
        "direct_actuation": data.get("direct_actuation"),
        "final_admission_allowed": data.get("final_admission_allowed"),
        "standing": "PARTIAL_ALIVE" if not failed else "BUILD_BROKEN",
        "claim_ceiling": (
            "Authored structural ecosystem documentation only; exact-source, runtime, "
            "release, and aggregate ecosystem standing remain unpromoted."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict-tools", action="store_true")
    args = parser.parse_args(argv)

    report = verify(args.root, strict_tools=args.strict_tools)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["standing"] == "PARTIAL_ALIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
