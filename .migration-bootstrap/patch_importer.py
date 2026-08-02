#!/usr/bin/env python3
"""Run the preserved importer patcher, then fence verifier-generated outputs."""

from pathlib import Path
import runpy

base = Path(__file__).with_name("patch_importer_base.py")
runpy.run_path(str(base), run_name="__main__")

verifier_path = Path("/tmp/verify_ggen_v26_8_1_migration.py")
verifier_text = verifier_path.read_text(encoding="utf-8")
needle = "        data_counts = parse_data_files(destination_root)\n"
replacement = """        generated_outputs = (
            destination_root / ".ggen/v26.8.1/planning-report.json",
            destination_root / "tools/v26.8.1/target",
        )
        destination_boundary = destination_root.resolve()
        for generated_output in generated_outputs:
            resolved_output = generated_output.resolve()
            try:
                resolved_output.relative_to(destination_boundary)
            except ValueError as exc:
                raise VerificationRefusal(
                    f"GENERATED_OUTPUT_CLEANUP_ESCAPE_REFUSED path={generated_output}"
                ) from exc
            if generated_output.is_symlink():
                raise VerificationRefusal(
                    f"GENERATED_OUTPUT_SYMLINK_REFUSED path={generated_output}"
                )
            if generated_output.is_dir():
                shutil.rmtree(generated_output)
            elif generated_output.exists():
                generated_output.unlink()
        data_counts = parse_data_files(destination_root)
"""
count = verifier_text.count(needle)
if count != 1:
    raise SystemExit(f"GENERATED_OUTPUT_FENCE_PRECONDITION_REFUSED count={count}")
verifier_path.write_text(verifier_text.replace(needle, replacement, 1), encoding="utf-8")
