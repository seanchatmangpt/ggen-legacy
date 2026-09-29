#!/usr/bin/env python3
"""Independent v26.9.28 ecosystem/reconstitution crown.

This verifier does not reimplement capability owners. It verifies the exact
composition contract that binds ggen-legacy to those owners, optionally probes
pinned remote commits, validates deterministic manufacture receipts, and
refuses authority widening.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

RELEASE = "v26.9.28"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_PIPELINE = [
    "observe", "recover_contract", "admit_or_refuse", "plan", "manufacture",
    "verify", "receipt", "replay", "release_admission", "sunset_admission",
]
EXPECTED = {
    "seanchatmangpt/ggen-marketplace": ("semantic_manufacturing_basis", "CONSTRUCT_ONLY"),
    "seanchatmangpt/ggen_igniter": ("projection_and_provenance", "CONSTRUCT_ONLY"),
    "seanchatmangpt/ash_r2rml": ("virtual_knowledge_graph", "NONE"),
    "seanchatmangpt/graphlaw": ("semantic_law_boundary", "EVIDENCE_ONLY"),
    "seanchatmangpt/ash_a2a": ("consequence_protocol", "CONSTRUCT_ONLY"),
    "seanchatmangpt/xaas": ("runtime_core_and_brce", "CONSEQUENTIAL_DO"),
    "seanchatmangpt/affidavit": ("cryptographic_trust_plane", "TRUST_ONLY"),
    "seanchatmangpt/ash_pplan": ("planner_ownership", "NONE"),
    "seanchatmangpt/beam4pm": ("beam_planning_runtime", "NONE"),
    "seanchatmangpt/ferroplan": ("replanning_engine", "NONE"),
    "seanchatmangpt/wasm4pm": ("portable_runtime_evidence", "EVIDENCE_ONLY"),
    "seanchatmangpt/gymact": ("action_experiment_surface", "NONE"),
    "seanchatmangpt/autofde-lab": ("failure_and_research_court", "EVIDENCE_ONLY"),
    "seanchatmangpt/dspy-wasm": ("typed_model_portability", "NONE"),
    "seanchatmangpt/unrdf": ("event_semantics_owner", "EVIDENCE_ONLY"),
    "seanchatmangpt/gitvan": ("swarm_receipt_transport", "EVIDENCE_ONLY"),
}
REQUIRED_FILES = (
    "authority/v26.9.28/ecosystem-lock.json",
    "authority/v26.9.28/reconstitution-contract.json",
    "schemas/v26.9.28/ecosystem-lock.schema.json",
    "schemas/v26.9.28/reconstitution-contract.schema.json",
    "ontology/v26.9.28/reconstitution.ttl",
    "queries/v26.9.28/required-owners.rq",
    "queries/v26.9.28/no-authority-widening.rq",
    "planning/v26.9.28/domain.hddl",
    "planning/v26.9.28/fond-domain.pddl",
    "planning/v26.9.28/release.tla",
    "docs/v26.9.28/README.md",
    "docs/v26.9.28/ARCHITECTURE.md",
    "docs/v26.9.28/REUSE_MAP.md",
    "docs/v26.9.28/VERIFICATION.md",
    "tickets/GL-RECON-928.md",
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def verify_lock(lock: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if lock.get("release") != RELEASE:
        errors.append("LOCK_RELEASE_MISMATCH")
    policy = lock.get("policy", {})
    required_policy = {
        "mutable_refs_are_authority": False,
        "vendored_engines_allowed": False,
        "generated_output_is_authority": False,
        "candidate_can_widen_standing": False,
        "single_consequential_do_owner": "seanchatmangpt/xaas",
        "read_plane_authority": "NONE",
        "trust_plane_authorization_authority": False,
    }
    for key, expected in required_policy.items():
        if policy.get(key) != expected:
            errors.append(f"LOCK_POLICY_MISMATCH:{key}")

    components = lock.get("components", [])
    if not isinstance(components, list):
        return errors + ["LOCK_COMPONENTS_NOT_LIST"]
    by_repo: dict[str, dict[str, Any]] = {}
    for item in components:
        if not isinstance(item, dict):
            errors.append("LOCK_COMPONENT_NOT_OBJECT")
            continue
        repo = item.get("repo")
        if repo in by_repo:
            errors.append(f"LOCK_DUPLICATE_REPO:{repo}")
        by_repo[repo] = item
        sha = item.get("sha", "")
        if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            errors.append(f"LOCK_MUTABLE_OR_INVALID_SUBJECT:{repo}:{sha}")
        caps = item.get("capabilities")
        if not isinstance(caps, list) or not caps:
            errors.append(f"LOCK_CAPABILITIES_EMPTY:{repo}")

    for repo, (role, authority) in EXPECTED.items():
        item = by_repo.get(repo)
        if item is None:
            errors.append(f"LOCK_REQUIRED_OWNER_MISSING:{repo}")
            continue
        if item.get("role") != role:
            errors.append(f"LOCK_ROLE_MISMATCH:{repo}")
        if item.get("authority") != authority:
            errors.append(f"LOCK_AUTHORITY_MISMATCH:{repo}")

    do_owners = [
        item.get("repo") for item in components
        if isinstance(item, dict) and item.get("authority") == "CONSEQUENTIAL_DO"
    ]
    if do_owners != ["seanchatmangpt/xaas"]:
        errors.append(f"LOCK_DO_OWNER_SET_INVALID:{do_owners}")

    for candidate in lock.get("candidates", []):
        if not isinstance(candidate, dict):
            errors.append("LOCK_CANDIDATE_NOT_OBJECT")
            continue
        if candidate.get("state") != "CANDIDATE":
            errors.append(f"LOCK_CANDIDATE_STATE_INVALID:{candidate.get('repo')}")
        if candidate.get("authority_widening") is not False:
            errors.append(f"LOCK_CANDIDATE_AUTHORITY_WIDENING:{candidate.get('repo')}")
        if not SHA_RE.fullmatch(str(candidate.get("sha", ""))):
            errors.append(f"LOCK_CANDIDATE_SHA_INVALID:{candidate.get('repo')}")
    return errors


def verify_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("release") != RELEASE:
        errors.append("CONTRACT_RELEASE_MISMATCH")
    if contract.get("pipeline") != EXPECTED_PIPELINE:
        errors.append("CONTRACT_PIPELINE_MISMATCH")
    ownership = contract.get("ownership", {})
    expected_ownership = {
        "semantic_source": "seanchatmangpt/ggen-marketplace",
        "projection": "seanchatmangpt/ggen_igniter",
        "read_federation": "seanchatmangpt/ash_r2rml",
        "semantic_law": "seanchatmangpt/graphlaw",
        "consequence_protocol": "seanchatmangpt/ash_a2a",
        "consequential_do": "seanchatmangpt/xaas",
        "trust_plane": "seanchatmangpt/affidavit",
        "planner": "seanchatmangpt/ash_pplan",
    }
    for key, expected in expected_ownership.items():
        if ownership.get(key) != expected:
            errors.append(f"CONTRACT_OWNER_MISMATCH:{key}")
    manufacture = contract.get("manufacture", {})
    if manufacture.get("strategy") != "reuse_compose_extend_before_invent":
        errors.append("CONTRACT_REUSE_LAW_MISSING")
    if manufacture.get("generated_files_hand_editable") is not False:
        errors.append("CONTRACT_GENERATED_EDIT_WIDENING")
    verification = contract.get("verification", {})
    for key in ("exact_subject_required", "positive_witnesses_required", "negative_controls_required",
                "deterministic_replay_required", "receipt_binding_required"):
        if verification.get(key) is not True:
            errors.append(f"CONTRACT_VERIFICATION_CONTROL_MISSING:{key}")
    if verification.get("producer_may_self_certify") is not False:
        errors.append("CONTRACT_SELF_CERTIFICATION_ALLOWED")
    release = contract.get("release_decision", {})
    if release.get("release_admitted") is not False:
        errors.append("CONTRACT_PREMATURE_RELEASE")
    if release.get("sunset_admitted") is not False:
        errors.append("CONTRACT_PREMATURE_SUNSET")
    if len(contract.get("falsifiers", [])) < 8:
        errors.append("CONTRACT_FALSIFIER_FLOOR")
    return errors


def verify_artifacts(root: Path) -> list[str]:
    errors = [f"REQUIRED_FILE_MISSING:{p}" for p in REQUIRED_FILES if not (root / p).is_file()]
    if errors:
        return errors
    ttl = (root / "ontology/v26.9.28/reconstitution.ttl").read_text(encoding="utf-8")
    for token in ("gl:ggenMarketplace", "gl:ashR2RML", "gl:graphlaw", "gl:ashA2A", "gl:xaas",
                  'gl:authority "CONSEQUENTIAL_DO"', "gl:generatedIsAuthority false"):
        if token not in ttl:
            errors.append(f"ONTOLOGY_TERM_MISSING:{token}")
    widening = (root / "queries/v26.9.28/no-authority-widening.rq").read_text(encoding="utf-8")
    if "FILTER (?owner != gl:xaas)" not in widening:
        errors.append("SPARQL_XAAS_EXCLUSION_MISSING")
    hddl = (root / "planning/v26.9.28/domain.hddl").read_text(encoding="utf-8")
    for action in ("observe", "admit", "plan", "manufacture", "verify", "receipt", "replay", "release"):
        if f"(:action {action}" not in hddl:
            errors.append(f"HDDL_ACTION_MISSING:{action}")
    tla = (root / "planning/v26.9.28/release.tla").read_text(encoding="utf-8")
    for token in ("Receipted", "Replayed", "Released", "NoReleaseWithoutReplay"):
        if token not in tla:
            errors.append(f"TLA_TERM_MISSING:{token}")
    return errors


def verify_receipt(receipt: dict[str, Any], root: Path, revision: str, tree: str) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema") != "ggen.legacy.v26.9.28.manufacture-receipt.v1":
        errors.append("RECEIPT_SCHEMA_MISMATCH")
    subject = receipt.get("subject", {})
    if subject.get("release") != RELEASE or subject.get("revision") != revision or subject.get("tree") != tree:
        errors.append("RECEIPT_EXACT_SUBJECT_MISMATCH")
    if receipt.get("standing") != "PARTIAL_ALIVE":
        errors.append("RECEIPT_PRODUCER_STANDING_MUST_BE_PARTIAL")
    if receipt.get("final_admission_allowed") is not False:
        errors.append("RECEIPT_SELF_CERTIFICATION")
    if receipt.get("actuation_performed") is not False:
        errors.append("RECEIPT_UNEXPECTED_ACTUATION")
    expected_lock = sha256_bytes((root / "authority/v26.9.28/ecosystem-lock.json").read_bytes())
    expected_contract = sha256_bytes((root / "authority/v26.9.28/reconstitution-contract.json").read_bytes())
    if receipt.get("lock_sha256") != expected_lock:
        errors.append("RECEIPT_LOCK_DIGEST_MISMATCH")
    if receipt.get("contract_sha256") != expected_contract:
        errors.append("RECEIPT_CONTRACT_DIGEST_MISMATCH")
    claimed = receipt.get("receipt_sha256")
    clone = dict(receipt)
    clone.pop("receipt_sha256", None)
    if claimed != sha256_bytes(canonical(clone)):
        errors.append("RECEIPT_DIGEST_INVALID")
    return errors


def probe_commit(repo: str, sha: str) -> str | None:
    url = f"https://github.com/{repo}.git"
    try:
        with tempfile.TemporaryDirectory(prefix="ggen-legacy-probe-") as tmp:
            subprocess.run(["git", "init", "--bare", "-q", tmp], check=True, timeout=20)
            subprocess.run(
                ["git", "-C", tmp, "fetch", "-q", "--depth=1", url, sha],
                check=True, timeout=60, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            observed = subprocess.run(
                ["git", "-C", tmp, "rev-parse", "FETCH_HEAD"],
                check=True, timeout=10, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            ).stdout.strip()
            return observed
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--expected-revision")
    parser.add_argument("--receipt-a", type=Path)
    parser.add_argument("--receipt-b", type=Path)
    parser.add_argument("--probe-remotes", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    revision = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    if args.expected_revision and revision != args.expected_revision:
        errors.append(f"EXACT_REVISION_MISMATCH:{revision}:{args.expected_revision}")

    lock = read_json(root / "authority/v26.9.28/ecosystem-lock.json")
    contract = read_json(root / "authority/v26.9.28/reconstitution-contract.json")
    errors += verify_lock(lock)
    errors += verify_contract(contract)
    errors += verify_artifacts(root)

    probes: list[dict[str, Any]] = []
    if args.probe_remotes:
        for item in lock.get("components", []):
            if not item.get("probe_required"):
                continue
            observed = probe_commit(item["repo"], item["sha"])
            passed = observed == item["sha"]
            probes.append({"repo": item["repo"], "expected": item["sha"], "observed": observed, "passed": passed})
            if not passed:
                errors.append(f"REMOTE_EXACT_SUBJECT_UNOBSERVED:{item['repo']}")

    replay_match = False
    receipts_present = bool(args.receipt_a and args.receipt_b)
    if bool(args.receipt_a) != bool(args.receipt_b):
        errors.append("REPLAY_RECEIPT_PAIR_REQUIRED")
    if receipts_present:
        a = read_json(args.receipt_a)
        b = read_json(args.receipt_b)
        errors += [f"A:{e}" for e in verify_receipt(a, root, revision, tree)]
        errors += [f"B:{e}" for e in verify_receipt(b, root, revision, tree)]
        replay_match = canonical(a) == canonical(b)
        if not replay_match:
            errors.append("DETERMINISTIC_REPLAY_MISMATCH")

    release_admitted = not errors and args.probe_remotes and replay_match
    standing = "ALIVE" if release_admitted else ("PARTIAL_ALIVE" if not errors else "BLOCKED")
    report = {
        "schema": "ggen.legacy.v26.9.28.crown.v1",
        "subject": {"repository": "seanchatmangpt/ggen-legacy", "release": RELEASE, "revision": revision, "tree": tree},
        "verifier_role": "independent_composition_court",
        "external_remote_probe": args.probe_remotes,
        "probes": probes,
        "replay_match": replay_match,
        "producer_verifier_separated": True,
        "actuation_performed": False,
        "release_admitted": release_admitted,
        "sunset_admitted": False,
        "standing": standing,
        "claim_ceiling": "REFERENCE_CONFORMANT" if release_admitted else "DOCUMENTED",
        "errors": errors,
        "nonclaims": [
            "Pinned external capability ownership does not certify every external runtime.",
            "CANDIDATE branches do not widen released standing.",
            "No real predecessor receives Sunset Admission from this crown.",
            "No external production deployment is claimed."
        ],
    }
    report["receipt_sha256"] = sha256_bytes(canonical(report))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"standing": standing, "release_admitted": release_admitted, "errors": errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
