#!/usr/bin/env python3
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
replacements = [
    (
        "import os\nimport shutil\n",
        "import os\nimport re\nimport shutil\n",
    ),
    (
        "def execute(argv: list[str], *, cwd: Path, timeout: int = 900) -> tuple[CommandReceipt, str, str]:\n",
        "def canonical_receipt_output(\n"
        "    argv: list[str], stdout: str, stderr: str\n"
        ") -> tuple[str, str]:\n"
        "    if argv[:2] != [\"cargo\", \"test\"]:\n"
        "        return stdout, stderr\n"
        "    elapsed = re.compile(r\"\\b\\d+(?:\\.\\d+)?s\\b\")\n"
        "\n"
        "    def normalize(value: str) -> str:\n"
        "        return elapsed.sub(\"<DURATION>\", value)\n"
        "\n"
        "    return normalize(stdout), normalize(stderr)\n"
        "\n"
        "\n"
        "def execute(argv: list[str], *, cwd: Path, timeout: int = 900) -> tuple[CommandReceipt, str, str]:\n",
    ),
    (
        "    receipt = CommandReceipt(\n",
        "    receipt_stdout, receipt_stderr = canonical_receipt_output(\n"
        "        argv, result.stdout, result.stderr\n"
        "    )\n"
        "    receipt = CommandReceipt(\n",
    ),
    (
        "        stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest(),\n"
        "        stderr_sha256=hashlib.sha256(result.stderr.encode()).hexdigest(),\n"
        "        stdout_excerpt=result.stdout[-2000:],\n"
        "        stderr_excerpt=result.stderr[-2000:],\n",
        "        stdout_sha256=hashlib.sha256(receipt_stdout.encode()).hexdigest(),\n"
        "        stderr_sha256=hashlib.sha256(receipt_stderr.encode()).hexdigest(),\n"
        "        stdout_excerpt=receipt_stdout[-2000:],\n"
        "        stderr_excerpt=receipt_stderr[-2000:],\n",
    ),
    (
        "            item = path.relative_to(base).as_posix()\n",
        "            item = (\n"
        "                path.name\n"
        "                if len(records) == 1 and path == base\n"
        "                else path.relative_to(base).as_posix()\n"
        "            )\n",
    ),
    (
        "    write_json(destination_root / EQUIVALENCE_PARH, equivalence)\n",
        "    write_json(destination_root / EQUIVALENCE_PATH, equivalence)\n",
    ),
    (
        "        destination_head = git_head(destination_root)\n"
        "        if not is_ancestor(destination_root, manifest[\"corpus_head\"], destination_head):\n"
        "            raise VerificationRefusal(\n"
        "                f\"CORPUS_HEAD_NOT_ANCESTOR_REFUSED corpus={manifest['corpus_head']} candidate={destination_head}\"\n"
        "            )\n",
        "        destination_head = git_head(destination_root)\n"
        "        corpus_head = manifest[\"corpus_head\"]\n"
        "        if is_ancestor(destination_root, corpus_head, destination_head):\n"
        "            corpus_head_relation = \"CORPUS_ANCESTOR_OF_CANDIDATE\"\n"
        "        elif is_ancestor(destination_root, destination_head, corpus_head):\n"
        "            checkpoint_paths = [\n"
        "                *[path.as_posix() for path in ACTIVE_ROOTS],\n"
        "                \"rustfmt.toml\",\n"
        "                \"scripts/verify_ggen_v26_8_1_migration.py\",\n"
        "                \"authority/ggen-v26.8.1-migration.json\",\n"
        "                \"projects/001/TICKET-013-migrate-ggen-v26.8.1-corpus.md\",\n"
        "                \"migrations/ggen-v26.8.1/SOURCE_LEDGER.md\",\n"
        "                \"migrations/ggen-v26.8.1/migration-intent.json\",\n"
        "                \"migrations/ggen-v26.8.1/source-workflows\",\n"
        "            ]\n"
        "            checkpoint_receipt, _, _ = execute(\n"
        "                [\"git\", \"diff\", \"--quiet\", corpus_head, \"--\", *checkpoint_paths],\n"
        "                cwd=destination_root,\n"
        "            )\n"
        "            if checkpoint_receipt.exit_status != 0:\n"
        "                raise VerificationRefusal(\n"
        "                    f\"LOCAL_CORPUS_CHECKPOINT_DRIFT_REFUSED corpus={corpus_head} candidate={destination_head}\"\n"
        "                )\n"
        "            corpus_head_relation = \"LOCAL_CORPUS_CHECKPOINT_DESCENDANT\"\n"
        "        else:\n"
        "            raise VerificationRefusal(\n"
        "                f\"CORPUS_HEAD_UNRELATED_REFUSED corpus={corpus_head} candidate={destination_head}\"\n"
        "            )\n",
    ),
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
        "        \"command_receipt_normalization\": [\n"
        "            \"workspace-identity\",\n"
        "            \"cargo-test-duration-tokens\",\n"
        "        ],\n"
        "        \"standalone_verifier_workspace_tests\": \"PASS\",\n",
    ),
    (
        "def parse_args() -> argparse.Namespace:\n",
        "def canonical_command_receipt(\n"
        "    receipt: CommandReceipt, destination_root: Path\n"
        ") -> dict[str, Any]:\n"
        "    result = asdict(receipt)\n"
        "    physical_cwd = receipt.cwd\n"
        "    destination_token = str(destination_root)\n"
        "    if Path(physical_cwd) == destination_root:\n"
        "        logical_cwd = \"<DESTINATION>\"\n"
        "    elif \"ggen-v26-8-1-composed-\" in physical_cwd:\n"
        "        logical_cwd = \"<COMPOSED_SOURCE>\"\n"
        "    else:\n"
        "        logical_cwd = physical_cwd\n"
        "\n"
        "    def canonical_text(value: str) -> str:\n"
        "        normalized = value.replace(destination_token, \"<DESTINATION>\")\n"
        "        if logical_cwd != physical_cwd:\n"
        "            normalized = normalized.replace(physical_cwd, logical_cwd)\n"
        "        return normalized\n"
        "\n"
        "    result[\"argv\"] = [canonical_text(value) for value in receipt.argv]\n"
        "    result[\"cwd\"] = logical_cwd\n"
        "    result[\"stdout_excerpt\"] = canonical_text(receipt.stdout_excerpt)\n"
        "    result[\"stderr_excerpt\"] = canonical_text(receipt.stderr_excerpt)\n"
        "    return result\n"
        "\n"
        "\n"
        "def parse_args() -> argparse.Namespace:\n",
    ),
    (
        "            \"rustfmt\",\n",
        "            \"rustfmt-equivalence\",\n",
    ),
    (
        "            \"candidate_head\": destination_head,\n"
        "            \"components\": component_reports,\n",
        "            \"candidate_head\": destination_head,\n"
        "            \"corpus_head_relation\": corpus_head_relation,\n"
        "            \"components\": component_reports,\n",
    ),
    (
        "            \"commands\": [asdict(compile_receipt), *[asdict(item) for item in command_receipts]],\n",
        "            \"commands\": [\n"
        "                canonical_command_receipt(compile_receipt, destination_root),\n"
        "                *[\n"
        "                    canonical_command_receipt(item, destination_root)\n"
        "                    for item in command_receipts\n"
        "                ],\n"
        "            ],\n",
    ),
]
for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"PATCH_PRECONDITION_REFUSED count={count} snippet={old[:80]!r}")
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
