// stardf v26.11.1 campaign — 10 waves x 20 concurrent lanes (200 agents), ultracode.
// Authored 2026-10-31 per operator request: "10 wave workflow where each wave has
// 20 concurrent agents PER WAVE NO LESS THAN 20 running at a time".
//
// CAP DISCLOSURE (read before running): the Workflow engine caps physically
// concurrent agent() calls at min(16, CPUs - 2) per workflow; that cap is not
// settable from script. This workflow therefore guarantees the guaranteeable part:
// every wave DISPATCHES exactly 20 lanes into the queue together and barriers the
// wave (all 20 in flight per wave, next wave waits for full integration). Physical
// simultaneity above the engine cap cannot be forced and is claimed by no lane.
//
// Run: Workflow({scriptPath: ".../stardf-10x20.workflow.mjs"})
//      optionally with args: {repo, waves: [ ten arrays of exactly 20 task strings ]}
// Concrete per-lane task bodies belong in args.waves; the built-in defaults are
// census/audit-class prompts that make each lane derive its own 1/20 partition.

export const meta = {
  name: 'stardf-10x20',
  description: 'stardf v26.11.1 campaign: 10 sequential waves x 20 concurrent lanes (200 agents), one canonical checkout, Chicago courts',
  whenToUse: 'Wave-structured completion+validation fan-out over /Users/sac/ggen-legacy (stardf campaign)',
  phases: [
    { title: 'Wave 1', detail: 'census/observe, read-only, 20 partition lenses' },
    { title: 'Wave 2', detail: 'repair under disjoint file leases, 20 lanes' },
    { title: 'Wave 3', detail: 'court-verify: real subprocess gates, 20 lanes' },
    { title: 'Wave 4', detail: 'parity sweep: every cell pass/divergence/loudly-MISSING, 20 lanes' },
    { title: 'Wave 5', detail: 'license/authority gates, 20 lanes' },
    { title: 'Wave 6', detail: 'receipt/claim reconciliation, 20 lanes' },
    { title: 'Wave 7', detail: 'adversarial mutation courts (anti-vacuity), 20 lanes' },
    { title: 'Wave 8', detail: 'determinism re-runs (flake hunting), 20 lanes' },
    { title: 'Wave 9', detail: 'skeptic panel: refute standing claims, 20 lanes' },
    { title: 'Wave 10', detail: 'integration verification + completeness critic, 20 lanes' },
  ],
}

const REPO = (args && args.repo) || '/Users/sac/ggen-legacy'
const N_WAVES = 10
const N_LANES = 20

// Campaign lane contract, relayed by the dispatching harness 2026-10-31 (operator-
// signed D9-D14 block). Fixed preamble for every lane prompt.
const CONTRACT = [
  'LANE CONTRACT (stardf v26.11.1 completion+validation; ' + REPO + '/):',
  '- Operator signed D9-D14 (OPERATOR-DECISIONS.md, 2026-10-31 block). R1 ADMITTED+GREEN',
  '  (license gate exit 0). Commits: c1=26d0140, c2=98afd71 on fix/v26.9.29-ci-gates.',
  '  c3-c6 are coordinator-only, post-campaign. NO git state-changing commands from any',
  '  lane (read-only status/log/rev-parse ok).',
  '- One canonical checkout; disjoint file ownership per lane label; shared-seam edits =',
  '  disclosed compile-freeze unblocks; re-read before editing (other lanes run',
  '  concurrently). NO worktrees, NO repo copies.',
  '- Chicago: real subprocesses/tests, no mocks; a court that cannot flip is FAIL; skips',
  '  loud ([SKIP: reason] + nonzero). Receipts only from commands YOU ran; cite',
  '  stardf/docs/jira/v26.10.31/*.md + stardf/arrow/docs/* for everything else.',
  '- Vendoring law: source = purrdf rev 0da05783 via',
  '  "git -C /Users/sac/purrdf archive 0da0578306983da851a9073337d57e2e2c41ab3a <path>"',
  '  (never the dirty tree); rename packages purrdf-* -> stardf-* ONLY; lib names,',
  '  LICENSE files, in-file notices verbatim; a NON-rename edit needed to build =',
  '  falsifier — escalate, never fix silently. New external deps: observe license from',
  '  ~/.cargo/registry, add dependency_licenses + compatibility_receipts entries in',
  '  authority/stardf/license-compat.json (Apache/MIT-arm basis, operator blanket',
  '  sign-off 2026-10-31), disclose.',
  '- ABI: 13 exports frozen + D9 Tier A RATIFIED (stardf_query, stardf_query_governed,',
  '  stardf_query_governors_init + carriers may be implemented as Rust surface; C',
  '  exports land only via the ratified ticket process).',
  '- Bridge edge (campaign-flagged): QuadKey::new/misses mask semantics adapted to u32',
  '  sentinels (in slice or results — locate where the probe plan lives).',
  '- Return raw report: STANDING (ALIVE/PARTIAL_ALIVE/UNKNOWN/BLOCKED) + files +',
  '  commands/exits + nonclaims. Your final text is data, not prose.',
].join('\n')

const LANE_REPORT = {
  type: 'object',
  properties: {
    lane: { type: 'string' },
    standing: {
      type: 'string',
      enum: ['ALIVE', 'PARTIAL_ALIVE', 'UNKNOWN', 'BLOCKED', 'BUILD_BROKEN', 'UNSUPPORTED', 'REFUSED'],
    },
    files: { type: 'array', items: { type: 'string' } },
    commands: {
      type: 'array',
      items: {
        type: 'object',
        properties: { cmd: { type: 'string' }, exit: { type: 'number' } },
        required: ['cmd', 'exit'],
      },
    },
    nonclaims: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['standing', 'summary'],
}

// Wave role ladder. Wave 1 read-only per fanout-first law; waves 7/9 are the
// adversarial courts (effort 'high'); wave 10 integrates.
const ROLES = [
  {
    name: 'census',
    brief: (n) =>
      'READ-ONLY census. Sort the campaign surface (stardf/arrow, stardf/crates, ' +
      'authority/stardf, stardf/docs/jira/v26.10.31, stardf/arrow/docs, tickets/) into ' +
      '20 disjoint slices in sorted path order; you own slice ' + n + '/20. Inventory ' +
      'every file in your slice: purpose, standing evidence, defect candidates, ' +
      'receipts present vs claimed. Locate where the QuadKey probe plan lives in your ' +
      'slice if present. ZERO edits, ZERO git writes.',
  },
  {
    name: 'repair',
    brief: (n) =>
      'REPAIR under a disjoint file lease. Take the defect candidates from the Wave-1 ' +
      'receipts for slice ' + n + '/20 (re-read the files — other lanes have run since). ' +
      'Apply the smallest coherent fix per file you lease. Re-read before every edit. ' +
      'Shared-seam fixes are disclosed compile-freeze unblocks. A non-rename edit ' +
      'required by vendoring law is a falsifier: escalate, do not fix. If the QuadKey ' +
      'u32-sentinel bridge edge lives in your lease, implement it under that law.',
  },
  {
    name: 'court',
    brief: (n) =>
      'COURT-VERIFY. Run the real gate for slice ' + n + '/20 (cargo test/clippy subset, ' +
      'just ci-all step, python3 scripts/verify_*.py — the gate your slice declares). ' +
      'Real subprocess, real exit codes. A gate that cannot exit 1 is not a gate: if ' +
      'your gate cannot fail, receipt it FAIL. Skips are loud ([SKIP: reason] + nonzero).',
  },
  {
    name: 'parity',
    brief: (n) =>
      'PARITY SWEEP. For slice ' + n + '/20 render the coverage cells (census-parity ' +
      'class): every cell pass / registered-divergence / loudly-MISSING. A silently ' +
      'skipped cell is a defect. Cite the receipt for every pass cell.',
  },
  {
    name: 'license',
    brief: (n) =>
      'LICENSE/AUTHORITY. For slice ' + n + '/20 of declared deps: observe each license ' +
      'from ~/.cargo/registry (not from memory); confirm dependency_licenses + ' +
      'compatibility_receipts entries exist in authority/stardf/license-compat.json; ' +
      'report any dep with no entry as MISSING with the observed license text path.',
  },
  {
    name: 'receipts',
    brief: (n) =>
      'RECEIPT RECONCILIATION. For slice ' + n + '/20 of stardf/docs/jira/v26.10.31/*.md ' +
      '+ docs/DECISION-BRIEFS/: re-read every count/status/standing claim from the ' +
      'receipt it cites at use time; flag stale cites (receipt moved, count drifted, ' +
      'claim predates the artifact). Claims without a receipt are UNKNOWN, never rounded.',
  },
  {
    name: 'mutation',
    brief: (n) =>
      'ADVERSARIAL MUTATION COURT. On a real temp copy (never the canonical tree), ' +
      'insert ONE unclassified defect in slice ' + n + '/20 (unclassified sleep, silent ' +
      'skip, unguarded unwrap — pick one). The matching gate must REFUSE. A gate that ' +
      'accepts the mutation is VACUOUS: receipt FAIL with the mutation diff + both exit ' +
      'codes. Restore byte-exact (sha256 before/after).',
  },
  {
    name: 'determinism',
    brief: (n) =>
      'DETERMINISM. Re-run slice ' + n + '/20 gates 3x back-to-back. Divergent outcomes ' +
      'across runs = flake defect with all three receipts attached. No sleeps as ' +
      'coordination; bounded polls on observables only.',
  },
  {
    name: 'skeptic',
    brief: (n) =>
      'SKEPTIC PANEL. Take the strongest standing claim (ALIVE/PASS/CONFORMANT) from ' +
      'slice ' + n + '/20 prior-wave receipts and try to REFUTE it: replay the cited ' +
      'command yourself. Default to refuted=true if the receipt does not replay or is ' +
      'missing. Symmetric burden: your counterclaim carries its own command+exit.',
  },
  {
    name: 'integration',
    brief: (n) =>
      'INTEGRATION + COMPLETENESS. For slice ' + n + '/20: verify the seams (compile ' +
      'clean at current HEAD, declared gates green, no orphaned lane artifacts, no new ' +
      'unowned files). Then answer the completeness critic: what modality was not run, ' +
      'which claim is unverified, which source unread? Name what is missing plainly.',
  },
]

function lanePrompt(waveIdx, laneIdx, task) {
  const role = ROLES[waveIdx]
  const label = 'w' + (waveIdx + 1) + '-l' + String(laneIdx + 1).padStart(2, '0')
  return [
    CONTRACT,
    '',
    'YOU ARE LANE ' + label + ' (wave ' + (waveIdx + 1) + '/' + N_WAVES + ', lane ' +
      (laneIdx + 1) + '/' + N_LANES + ', role: ' + role.name + ').',
    '',
    'ROLE BRIEF: ' + role.brief(laneIdx + 1),
    '',
    'TASK: ' + task,
    '',
    'Your lane lease is only the files your slice names. Re-read before editing. ' +
      'No mocks. No git state changes. Skips loud. Receipts only from commands you ran. ' +
      'Return the structured report.',
  ].join('\n')
}

// Default lane tasks are census-class self-partitioning prompts; the coordinator is
// expected to override waves with concrete task bodies via args.waves.
function defaultTask(waveIdx, laneIdx) {
  const role = ROLES[waveIdx]
  return (
    'Self-partition per your role brief and execute it. Report your slice boundary ' +
      'explicitly so the coordinator can check disjointness against lanes ' +
      Math.max(1, laneIdx) + ' and ' + Math.min(N_LANES, laneIdx + 2) + '.'
  )
}

// Build + validate the wave matrix. Undersized waves are refused, never silently run.
const override = (args && Array.isArray(args.waves)) ? args.waves : []
const waves = []
for (let w = 0; w < N_WAVES; w++) {
  const src = (Array.isArray(override[w]) && override[w].length) ? override[w] : null
  const list = src || Array.from({ length: N_LANES }, (_, i) => defaultTask(w, i))
  if (!Array.isArray(list) || list.length !== N_LANES) {
    throw new Error(
      'wave ' + (w + 1) + ' must carry exactly ' + N_LANES + ' lane tasks (got ' +
        (list ? list.length : 'non-array') + '); waves smaller than 20 lanes are refused'
    )
  }
  waves.push(list)
}
if (waves.length !== N_WAVES) {
  throw new Error('expected exactly ' + N_WAVES + ' waves, built ' + waves.length)
}

phase('Wave 1')
const receipts = []
let totalReturned = 0
let totalDropped = 0

for (let w = 0; w < N_WAVES; w++) {
  const title = 'Wave ' + (w + 1)
  log(title + '/' + N_WAVES + ' (' + ROLES[w].name + '): dispatching ' + N_LANES +
    ' concurrent lanes — no fewer than 20 per wave')

  const results = await parallel(
    waves[w].map((task, i) => () =>
      agent(lanePrompt(w, i, task), {
        label: 'w' + (w + 1) + '-l' + String(i + 1).padStart(2, '0'),
        phase: title,
        schema: LANE_REPORT,
        // higher reasoning only on the adversarial courts (waves 7 and 9)
        ...((w === 6 || w === 8) ? { effort: 'high' } : {}),
      })
    )
  )
  // Barrier is genuinely required here: wave N+1 leases integrate on top of wave N
  // outcomes (same-checkout fan-out law: integration is serialized across waves).

  const lanes = results.map((r, i) => {
    const label = 'w' + (w + 1) + '-l' + String(i + 1).padStart(2, '0')
    if (!r) {
      return { lane: label, standing: 'UNKNOWN', summary: 'lane dropped (user skip or terminal agent error) — loudly missing, not silently skipped' }
    }
    return { lane: label, standing: r.standing, summary: r.summary, files: r.files, commands: r.commands, nonclaims: r.nonclaims }
  })
  const returned = results.filter(Boolean).length
  totalReturned += returned
  totalDropped += results.length - returned
  receipts.push({ wave: w + 1, role: ROLES[w].name, dispatched: N_LANES, returned, dropped: results.length - returned, lanes })
  log(title + ' complete: ' + returned + '/' + N_LANES + ' lanes returned' +
    (returned < N_LANES ? ' (' + (N_LANES - returned) + ' loudly missing)' : ''))
}

return {
  campaign: 'stardf v26.11.1 completion+validation',
  repo: REPO,
  shape: { waves: N_WAVES, lanesPerWave: N_LANES, totalLanes: N_WAVES * N_LANES },
  capDisclosure: 'engine concurrency cap min(16, CPUs-2) applies to physical simultaneity; every wave dispatched all 20 lanes together and barriered',
  totals: { lanesReturned: totalReturned, lanesDropped: totalDropped },
  waves: receipts,
}
