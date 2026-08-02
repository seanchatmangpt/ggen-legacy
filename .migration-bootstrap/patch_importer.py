#!/usr/bin/env python3
import json
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding='utf-8')
replacements = [
    (
        '    destination.parent.mkdir(parents=True, exist_ok=True)\n'
        '    shutil.copytree(source, destination, symlinks=True)\n',
        '    destination.parent.mkdir(parents=True, exist_ok=True)\n'
        '    if source.is_dir():\n'
        '        shutil.copytree(source, destination, symlinks=True)\n'
        '    elif source.is_file():\n'
        '        shutil.copy2(source, destination)\n'
        '    else:\n'
        '        raise MigrationRefusal(\n'
        '            f"SOURCE_PATH_UNSUPPORTED_REFUSED path={source.as_posix()}"\n'
        '        )\n',
    ),
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

# The verifier is already decoded when this patcher runs. Add a bounded replay
# probe that compares only the two reports produced inside this workflow run.
verifier_path = Path('/tmp/verify_ggen_v26_8_1_migration.py')
verifier_text = verifier_path.read_text(encoding='utf-8')
verifier_lines = verifier_text.splitlines()
data_count_context = []
for index, line in enumerate(verifier_lines):
    if 'data_counts' in line:
        start = max(0, index - 6)
        end = min(len(verifier_lines), index + 7)
        data_count_context.append(
            {
                'line': index + 1,
                'context': [
                    f'{line_number + 1}: {verifier_lines[line_number]}'
                    for line_number in range(start, end)
                ],
            }
        )
print('DATA_COUNTS_SOURCE=' + json.dumps(data_count_context, sort_keys=True))
report_sinks = [
    line
    for line in verifier_text.splitlines(keepends=True)
    if 'write_json(' in line and line.rstrip().endswith(', report)')
]
if len(report_sinks) != 1:
    raise SystemExit(
        'REPLAY_PROBE_PRECONDITION_REFUSED '
        f'count={len(report_sinks)} candidates={report_sinks!r}'
    )
needle = report_sinks[0]
indent = needle[: len(needle) - len(needle.lstrip())]
diagnostic_lines = [
    'replay_probe = Path("/tmp/ggen-v26-8-1-replay-probe.json")',
    'if replay_probe.exists():',
    '    previous_report = json.loads(replay_probe.read_text(encoding="utf-8"))',
    '',
    '    def first_replay_diff(left: Any, right: Any, location: str = "$") -> Any:',
    '        if type(left) is not type(right):',
    '            return [location, left, right]',
    '        if isinstance(left, dict):',
    '            for key in sorted(set(left) | set(right)):',
    '                if key not in left or key not in right:',
    '                    return [location + "." + key, left.get(key, "<MISSING>"), right.get(key, "<MISSING>")]',
    '                found = first_replay_diff(left[key], right[key], location + "." + key)',
    '                if found is not None:',
    '                    return found',
    '            return None',
    '        if isinstance(left, list):',
    '            if len(left) != len(right):',
    '                return [location + ".length", len(left), len(right)]',
    '            for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):',
    '                found = first_replay_diff(left_item, right_item, f"{location}[{index}]")',
    '                if found is not None:',
    '                    return found',
    '            return None',
    '        if left != right:',
    '            return [location, left, right]',
    '        return None',
    '',
    '    observed_diff = first_replay_diff(previous_report, report)',
    '    os.write(2, ("FIRST_REPLAY_DIFF=" + json.dumps(observed_diff, sort_keys=True, default=str) + "\\n").encode())',
    'else:',
    '    replay_probe.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")',
    '',
]
diagnostic = ''.join(
    (indent + line + '\n') if line else '\n'
    for line in diagnostic_lines
)
verifier_path.write_text(verifier_text.replace(needle, diagnostic + needle, 1), encoding='utf-8')
