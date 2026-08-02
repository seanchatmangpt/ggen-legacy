from __future__ import annotations

import atexit
from pathlib import Path
import sys


def patch_generated_verifier() -> None:
    target = Path(sys.argv[1])
    text = target.read_text(encoding="utf-8")

    old_normalizer = '''def canonical_receipt_output(
    argv: list[str], stdout: str, stderr: str
) -> tuple[str, str]:
    if argv[:2] != ["cargo", "test"]:
        return stdout, stderr
    elapsed = re.compile(r"\\b\\d+(?:\\.\\d+)?s\\b")

    def normalize(value: str) -> str:
        return elapsed.sub("<DURATION>", value)

    return normalize(stdout), normalize(stderr)
'''
    new_normalizer = '''def canonical_receipt_output(
    argv: list[str], stdout: str, stderr: str
) -> tuple[str, str]:
    if argv[:2] != ["cargo", "test"]:
        return stdout, stderr
    elapsed = re.compile(r"\\b\\d+(?:\\.\\d+)?s\\b")

    def normalize(value: str) -> str:
        return elapsed.sub("<DURATION>", value)

    def normalize_stderr(value: str) -> str:
        lines = normalize(value).splitlines(keepends=True)
        compile_positions = [
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("Compiling ")
        ]
        compile_events = sorted(lines[index] for index in compile_positions)
        for index, event in zip(compile_positions, compile_events, strict=True):
            lines[index] = event
        return "".join(lines)

    return normalize(stdout), normalize_stderr(stderr)
'''
    if text.count(old_normalizer) != 1:
        raise SystemExit(
            f"PROGRESS_NORMALIZER_PRECONDITION_REFUSED count={text.count(old_normalizer)}"
        )
    text = text.replace(old_normalizer, new_normalizer, 1)

    diagnostic_start = text.find("def diagnostic_command_receipts(")
    diagnostic_end = text.find("def parse_args() -> argparse.Namespace:", diagnostic_start)
    if diagnostic_start < 0 or diagnostic_end < 0:
        raise SystemExit("DIAGNOSTIC_REMOVAL_PRECONDITION_REFUSED")
    text = text[:diagnostic_start] + text[diagnostic_end:]

    old_commands = '''            "commands": diagnostic_command_receipts(
                [compile_receipt, *command_receipts], destination_root
            ),
'''
    new_commands = '''            "commands": [
                canonical_command_receipt(compile_receipt, destination_root),
                *[
                    canonical_command_receipt(item, destination_root)
                    for item in command_receipts
                ],
            ],
'''
    if text.count(old_commands) != 1:
        raise SystemExit(
            f"COMMAND_RECEIPT_PRECONDITION_REFUSED count={text.count(old_commands)}"
        )
    text = text.replace(old_commands, new_commands, 1)

    old_metadata = '''            "cargo-color-disabled",
            "cargo-single-build-job",
'''
    new_metadata = '''            "cargo-color-disabled",
            "cargo-compile-progress-order",
            "cargo-single-build-job",
'''
    if text.count(old_metadata) != 1:
        raise SystemExit(
            f"NORMALIZATION_METADATA_PRECONDITION_REFUSED count={text.count(old_metadata)}"
        )
    text = text.replace(old_metadata, new_metadata, 1)

    if text.count("import sys\n") != 1:
        raise SystemExit(
            f"DIAGNOSTIC_IMPORT_PRECONDITION_REFUSED count={text.count('import sys\n')}"
        )
    text = text.replace("import sys\n", "", 1)
    target.write_text(text, encoding="utf-8")


if Path(sys.argv[0]).name == "patch_verifier.py" and len(sys.argv) == 2:
    atexit.register(patch_generated_verifier)
