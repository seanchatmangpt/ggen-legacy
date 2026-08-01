#!/usr/bin/env python3
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding='utf-8')
replacements = [
    (
        ')\nWORKFLOW_COMPONENT_ID = "GGEN-V26.8.1-SOURCE-WORKFLOW-EVIDENCE"\n',
        ')\nCONTEXT_COMPONENTS = (\n'
        '    (\n'
        '        "GGEN-V26.8.1-RUSTFMT-CONTEXT",\n'
        '        Path("rustfmt.toml"),\n'
        '        Path("rustfmt.toml"),\n'
        '        ("workspace-format-law", "source-context-projection"),\n'
        '    ),\n'
        ')\nWORKFLOW_COMPONENT_ID = "GGEN-V26.8.1-SOURCE-WORKFLOW-EVIDENCE"\n',
    ),
    (
        '    for _, relative, _ in ACTIVE_COMPONENTS:\n'
        '        copy_tree_refusing_occupied(source_root / relative, destination_root / relative)\n\n'
        '    workflow_paths = selected_workflows(source_root)\n',
        '    for _, relative, _ in ACTIVE_COMPONENTS:\n'
        '        copy_tree_refusing_occupied(source_root / relative, destination_root / relative)\n'
        '    for _, source_relative, destination_relative, _ in CONTEXT_COMPONENTS:\n'
        '        copy_tree_refusing_occupied(\n'
        '            source_root / source_relative, destination_root / destination_relative\n'
        '        )\n\n'
        '    workflow_paths = selected_workflows(source_root)\n',
    ),
    (
        '            for component_id, relative, capabilities in ACTIVE_COMPONENTS\n'
        '        ]\n'
        '        + [\n',
        '            for component_id, relative, capabilities in ACTIVE_COMPONENTS\n'
        '        ]\n'
        '        + [\n'
        '            {\n'
        '                "component_id": component_id,\n'
        '                "source_path": source_relative.as_posix(),\n'
        '                "destination_path": destination_relative.as_posix(),\n'
        '                "capability_ids": list(capabilities),\n'
        '            }\n'
        '            for component_id, source_relative, destination_relative, capabilities in CONTEXT_COMPONENTS\n'
        '        ]\n'
        '        + [\n',
    ),
    (
        '    components.append(\n'
        '        {\n'
        '            "component_id": WORKFLOW_COMPONENT_ID,\n',
        '    for component_id, source_relative, destination_relative, capabilities in CONTEXT_COMPONENTS:\n'
        '        components.append(\n'
        '            {\n'
        '                "component_id": component_id,\n'
        '                "capability_ids": list(capabilities),\n'
        '                "source_path": source_relative.as_posix(),\n'
        '                "destination_path": destination_relative.as_posix(),\n'
        '                "source_digest": tree_digest(source_root, source_relative),\n'
        '                "source_files": len(files_under(source_root, source_relative)),\n'
        '            }\n'
        '        )\n'
        '    components.append(\n'
        '        {\n'
        '            "component_id": WORKFLOW_COMPONENT_ID,\n',
    ),
    (
        '    source_base = source_root / source_relative\n'
        '    destination_base = destination_root / destination_relative\n'
        '    for source_path in sorted(source_files):\n'
        '        item = source_path.relative_to(source_base).as_posix()\n'
        '        destination_path = destination_base / item\n',
        '    source_base = source_root / source_relative\n'
        '    destination_base = destination_root / destination_relative\n'
        '    for source_path in sorted(source_files):\n'
        '        if source_base.is_file():\n'
        '            item = source_path.name\n'
        '            destination_path = destination_base\n'
        '        else:\n'
        '            item = source_path.relative_to(source_base).as_posix()\n'
        '            destination_path = destination_base / item\n',
    ),
    (
        '    source_workflows = selected_workflows(source_root)\n',
        '    for component_id, source_relative, destination_relative, capabilities in CONTEXT_COMPONENTS:\n'
        '        lineage = build_lineage(\n'
        '            source_root,\n'
        '            destination_root,\n'
        '            component_id,\n'
        '            source_relative,\n'
        '            destination_relative,\n'
        '            files_under(source_root, source_relative),\n'
        '        )\n'
        '        lineage_path = lineage_root / f"{component_id.lower()}.json"\n'
        '        write_json(lineage_path, lineage)\n'
        '        source_digest = tree_digest(source_root, source_relative)\n'
        '        destination_digest = tree_digest(destination_root, destination_relative)\n'
        '        if source_digest != destination_digest:\n'
        '            raise MigrationRefusal(f"CONTEXT_DRIFT_REFUSED component={component_id}")\n'
        '        manifest_components.append(\n'
        '            {\n'
        '                "component_id": component_id,\n'
        '                "capability_ids": list(capabilities),\n'
        '                "source_commit": source_commit,\n'
        '                "source_path": source_relative.as_posix(),\n'
        '                "source_digest": source_digest,\n'
        '                "disposition": "PRESERVED",\n'
        '                "destination_path": destination_relative.as_posix(),\n'
        '                "destination_digest": destination_digest,\n'
        '                "replacement_owner": DESTINATION_REPOSITORY,\n'
        '                "migration_evidence": lineage_path.relative_to(destination_root).as_posix(),\n'
        '                "equivalence_case": (MIGRATION_ROOT / "equivalence-report.json").as_posix(),\n'
        '                "verifier_report": (MIGRATION_ROOT / "verifier-report.json").as_posix(),\n'
        '                "receipt": (MIGRATION_ROOT / "migration-receipt.json").as_posix(),\n'
        '            }\n'
        '        )\n\n'
        '    source_workflows = selected_workflows(source_root)\n',
    ),
]
for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'PATCH_PRECONDITION_REFUSED count={count} snippet={old[:100]!r}')
    text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
