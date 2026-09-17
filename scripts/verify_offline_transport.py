#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
# EXPECTED_HEAD_SOURCE: claimed to represent PR #537's source-repo HEAD.
# Unreachable in this worktree (`git cat-file -t` fails); producing-repo/
# commit not independently confirmed. See tickets/GL-ERRC-011.md.
EXPECTED_HEAD = "4bd2df69362c2708551f870c3dac36bce97898c2"
# EXPECTED_WORKFLOW_RUN is a CI run-number identity claim, not a git SHA
# object; it is not in scope for GL-ERRC-011's git-object-reachability
# check and is left unannotated here.
EXPECTED_WORKFLOW_RUN = 30654755433
EXPECTED_PROPERTIES = [
    "exact_source_head",
    "exact_ggen_coordinate",
    "sorted_file_manifest",
    "fixed_archive_metadata",
    "offline_activation",
    "self_verification",
    "byte_identical_rebuild",
    "no_customer_source",
    "portable_receipt",
]


def main() -> int:
    authority = json.loads(
        (ROOT / "authority/offline-verifier-transport.json").read_text()
    )
    errors: list[str] = []
    provenance = authority.get("provenance", {})
    implementation = authority.get("implementation", {})

    if provenance.get("pull_request") != 537:
        errors.append("PR_537_IDENTITY")
    if provenance.get("head") != EXPECTED_HEAD:
        # EXPECTED_HEAD is a confirmed-unreachable git object in this
        # worktree (see tickets/GL-ERRC-011.md): a mismatch cannot be
        # distinguished from "the constant is stale" vs "the live value
        # genuinely drifted" without repo-owner input, so it is reported
        # as STALE_REFERENCE_UNVERIFIABLE rather than a bare
        # PR_537_HEAD_DRIFT claim.
        errors.append(
            f"STALE_REFERENCE_UNVERIFIABLE:PR_537_HEAD_DRIFT:"
            f"observed={provenance.get('head')}"
        )
    if provenance.get("dedicated_workflow_run") != EXPECTED_WORKFLOW_RUN:
        errors.append("PR_537_WORKFLOW_IDENTITY")
    if provenance.get("dedicated_workflow_conclusion") != "success":
        errors.append("DEDICATED_WORKFLOW_NOT_SUCCESS")
    if provenance.get("standing_transferred") is not False:
        errors.append("PR_537_STANDING_TRANSFER")
    if provenance.get("dependency_admitted") is not False:
        errors.append("OPEN_TRANSPORT_DEPENDENCY_ADMITTED")
    if authority.get("required_properties") != EXPECTED_PROPERTIES:
        errors.append("TRANSPORT_PROPERTY_DRIFT")
    if authority.get("transport_class") != "PORTABLE_APPLICATION_BUNDLE":
        errors.append("TRANSPORT_CLASS_DRIFT")
    if implementation.get("customer_source_included") is not False:
        errors.append("CUSTOMER_SOURCE_INCLUDED")
    if implementation.get("network_required") is not False:
        errors.append("NETWORK_REQUIREMENT_DRIFT")

    builder = ROOT / str(implementation.get("builder", ""))
    template = ROOT / str(implementation.get("generator_template", ""))
    if not builder.is_file():
        errors.append("OFFLINE_BUILDER_MISSING")
    if not template.is_file():
        errors.append("OFFLINE_BUILDER_TEMPLATE_MISSING")

    report = {
        "schema": "ggen.legacy.offline.transport.verifier.v1",
        "source_head": provenance.get("head"),
        "dedicated_workflow_run": provenance.get("dedicated_workflow_run"),
        "dedicated_workflow_conclusion": provenance.get(
            "dedicated_workflow_conclusion"
        ),
        "branch_ci_conclusion": provenance.get("branch_ci_conclusion"),
        "branch_quality_conclusion": provenance.get("branch_quality_conclusion"),
        "dependency_admitted": provenance.get("dependency_admitted"),
        "transport_class": authority.get("transport_class"),
        "errors": errors,
        "standing": "ALIVE" if not errors else "BUILD_BROKEN",
        "nonclaims": authority.get("nonclaims", []),
    }
    output = ROOT / "evidence/offline-transport-provenance.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
