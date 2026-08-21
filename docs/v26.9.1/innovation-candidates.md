# Innovation exploration — cycle 1 candidates

**Status: CANDIDATE, not ALIVE.** Produced by the `innovation-explorer`
standing capability (`~/.claude/workflows/innovation-explorer.js`), a
multi-repo (ggen-legacy/wasm4pm/ggen) EXPLORE-mode sweep. These are
proposals surfaced by independent-lens agents and ranked
novelty×feasibility×leverage — not verified, not admitted, not committed
work. Per this repo's ticket-gated admission rule, none of these become
executable without a real `GL-*` ticket going through the same
evidence-verification discipline the rest of `tickets/` follows.

## Top-ranked (score = novelty + feasibility + leverage, 3-15 scale)

1. **dsrust/Groq disposition proposer never wired into admission
   (score 10)** — `tools/dsrust-disposition-proposer`'s
   `propose-disposition` CLI is real and tested, proposing a legacy-
   capability disposition from the same 5 evidence fields
   `admit_capabilities.rs` admits on, but nothing wires it into the
   admission workflow (no justfile target, no CI step, no import).
   Ggen-legacy-local, highest feasibility.
2. **`planning/v26.8.7` CLI subcommands not exposed via any top-level
   verb (score 10)** — `planning/v26.8.7/cli.py` implements a full
   A*-based capability planner CLI with real subprocess-tested
   subcommands, reachable only as a raw Python script today.
   Ggen-legacy-local.
3. **wasm4pm OCLA algorithm missing from the CLI/MCP registry (score 9)**
   — `wasm4pm/src/advanced/ocla.rs` implements a real object-centric
   footprint abstraction not registered in
   `apps/wasm4pm/src/engines/algorithms.ts`. External repo (`~/wasm4pm`),
   not this repo's authored boundary.
4. **`ocpq` → `praxis-graphlaw` cross-repo data flow (score 9)** —
   feeding wasm4pm's object-centric query violations into ggen's RDF/SHACL
   law-state engine as facts. Lower feasibility (2/5, real schema-mapping
   work), higher leverage (4/5, unlocks a first dynamic fact source for
   praxis-graphlaw). Cross-repo, external to this repo's authored
   boundary.

14 candidates total; full ranked list and per-candidate justification in
this cycle's workflow result (not persisted verbatim here to avoid
duplicating an EXPLORE-mode artifact as if it were durable authority —
re-run `innovation-explorer` for a fresh sweep rather than treating this
summary as exhaustive).

## What this means for v26.9.1

None of these are release blockers or release content — they're future-
work candidates surfaced alongside the release-prep execution loop. If
one is worth pursuing, it needs its own `GL-*` ticket with real,
independently-re-verified evidence (following `GL-ERRC-*`'s pattern), not
promotion straight from this candidate list.
