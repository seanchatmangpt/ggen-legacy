#!/bin/bash
# usage: refresh_and_run.sh [report.json]
# Refresh the SHA-pinned manifests at current HEADs, then run the dry-run with --selftest,
# retrying while another session changes a file the run reads (BLOCKED:UNSTABLE_EVIDENCE).
# Exit code is the dry-run's: 0 only for a READY verdict.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT=${1:-$HERE/../../docs/jira/v26.11.9/receipts/dry-run-latest.json}
"$HERE/refresh_manifests.sh" "${TMPDIR:-/tmp}/ggen-legacy-sources" >/dev/null
for try in 1 2 3; do
  ggen-create cutover dryrun --selftest --receipt "$REPORT" >/dev/null
  rc=$?
  verdict=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['verdict'])" "$REPORT")
  echo "try $try: $verdict (rc=$rc)"
  [ "$verdict" != "BLOCKED:UNSTABLE_EVIDENCE" ] && exit $rc
done
exit 1
