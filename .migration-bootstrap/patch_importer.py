#!/usr/bin/env python3
"""Run the preserved importer patcher, then add a bounded JSON-output delta probe."""

from pathlib import Path
import runpy

base = Path(__file__).with_name("patch_importer_base.py")
runpy.run_path(str(base), run_name="__main__")

verifier_path = Path("/tmp/verify_ggen_v26_8_1_migration.py")
verifier_text = verifier_path.read_text(encoding="utf-8")

before_needle = "        data_counts = parse_data_files(destination_root)\n"
before_replacement = """        json_paths_before = {
            candidate.relative_to(destination_root).as_posix()
            for candidate in destination_root.rglob("*.json")
            if ".git" not in candidate.parts and ".source-ggen" not in candidate.parts
        }
        data_counts = parse_data_files(destination_root)
"""
if verifier_text.count(before_needle) != 1:
    raise SystemExit(
        f"JSON_DELTA_BEFORE_PRECONDITION_REFUSED count={verifier_text.count(before_needle)}"
    )
verifier_text = verifier_text.replace(before_needle, before_replacement, 1)

after_needle = "        controls = negative_controls(destination_root, source_root, manifest)\n"
after_replacement = after_needle + """        json_paths_after = {
            candidate.relative_to(destination_root).as_posix()
            for candidate in destination_root.rglob("*.json")
            if ".git" not in candidate.parts and ".source-ggen" not in candidate.parts
        }
        os.write(
            2,
            (
                "JSON_OUTPUT_DELTA="
                + json.dumps(sorted(json_paths_after - json_paths_before))
                + "\\n"
            ).encode(),
        )
"""
if verifier_text.count(after_needle) != 1:
    raise SystemExit(
        f"JSON_DELTA_AFTER_PRECONDITION_REFUSED count={verifier_text.count(after_needle)}"
    )
verifier_text = verifier_text.replace(after_needle, after_replacement, 1)
verifier_path.write_text(verifier_text, encoding="utf-8")
