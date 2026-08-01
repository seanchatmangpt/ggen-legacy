#!/usr/bin/env python3
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
replacements = [
    (
        "    destination_fmt_receipt, _ = require_success(\n",
        "    destination_fmt_receipt, _, _ = execute(\n",
    ),
    (
        "        composed_fmt_receipt, _ = require_success(\n",
        "        composed_fmt_receipt, _, _ = execute(\n",
    ),
    (
        "    shacl_match = destination_shacl_stdout == composed_shacl_stdout\n"
        "    if not planning_match:\n",
        "    shacl_match = destination_shacl_stdout == composed_shacl_stdout\n"
        "    rustfmt_match = destination_fmt_receipt.exit_status == composed_fmt_receipt.exit_status\n"
        "    if not planning_match:\n",
    ),
    (
        "    if not shacl_match:\n"
        "        raise VerificationRefusal(\"SHACL_COMPOSITION_DRIFT_REFUSED\")\n\n"
        "    return receipts, {\n",
        "    if not shacl_match:\n"
        "        raise VerificationRefusal(\"SHACL_COMPOSITION_DRIFT_REFUSED\")\n"
        "    if not rustfmt_match:\n"
        "        raise VerificationRefusal(\n"
        "            \"RUSTFMT_COMPOSITION_DRIFT_REFUSED \"\n"
        "            f\"destination={destination_fmt_receipt.exit_status} composed={composed_fmt_receipt.exit_status}\"\n"
        "        )\n\n"
        "    return receipts, {\n",
    ),
    (
        "        \"shacl_result\": destination_shacl_stdout.strip(),\n"
        "        \"standalone_verifier_workspace_tests\": \"PASS\",\n",
        "        \"shacl_result\": destination_shacl_stdout.strip(),\n"
        "        \"rustfmt_exit_match\": rustfmt_match,\n"
        "        \"rustfmt_exit_status\": destination_fmt_receipt.exit_status,\n"
        "        \"rustfmt_state\": (\n"
        "            \"PASS\" if destination_fmt_receipt.exit_status == 0 else \"SOURCE_DEFECT_PRESERVED\"\n"
        "        ),\n"
        "        \"standalone_verifier_workspace_tests\": \"PASS\",\n",
    ),
    (
        "            \"rustfmt\",\n",
        "            \"rustfmt-equivalence\",\n",
    ),
]
for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"PATCH_PRECONDITION_REFUSED count={count} snippet={old[:80]!r}")
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
