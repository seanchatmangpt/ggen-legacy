# Falsifiers — v26.10.31 (stardf reconstitution)

One falsifier per wave + standing risks. A falsifier that cannot flip is decoration.
Anti-vacuity law: each court ships with its positive-control mutation; a skip is loud.

## W1 — Contract closure

**F1 (type census)**: `python3 scripts/verify_stardf_ontology.py` must FAIL (exit 1,
"Missing type mappings") on today's TTL, and PASS only after the extractor captures the 11
anonymous structs and the TTL is regenerated. A census that passes the pre-fix TTL is
vacuous.

STATUS (2026-10-31, plan-update lane 4): **WITNESSED (full ladder).** Pre-fix FAIL
receipt stands: exit 1, `[FAIL] Missing type mappings` naming the 11 anonymous-struct
typedefs (PurrdfAbiVersion, PurrdfCapabilities, PurrdfGovernedEntailmentEvidence,
PurrdfGovernorEvidence, PurrdfGovernorTrip, PurrdfGraphMatch, PurrdfPartialCertificate,
PurrdfQueryGovernors, PurrdfResourceVector, PurrdfStr, PurrdfTermView). Post-fix PASS
witnessed: census re-run by W1-2/W1-3 lanes after the extractor mapping additions and TTL
regeneration → 22/22 pass (census run receipt, those lanes). Both directions of the flip
are now on record; the census is non-vacuous.

**F1a (anti-vacuity)**: `verify_stardf_ontology.py --mutate drop-type` — the in-memory
mutation must be refused (mutation step exits 1); if the mutated graph still passes →
`[FAIL] VACUOUS GATE`, exit 1.

STATUS (2026-10-31, plan-update lane 4): **REFUSED (witnessed x2).** Two runs of
`python3 scripts/verify_stardf_ontology.py --mutate drop-type` both witnessed the refusal
path: `[MUTATE] dropped TypeDefinition with predecessorSymbol 'PurrdfBuffer'` then
`[PASS] F1a: drop-type mutation REFUSED (mutant graph fails census)` (exit 0 = court
passed, mutation refused). Positive control in `scripts/verify_stardf_ontology.py`
(`run_mutation_drop_type` + two-directional census; mutant-still-passes →
`[FAIL] VACUOUS GATE` exit 1; zero victims → loud `[SKIP]` exit 1). Second witness
post-dates the F1 fix, so the refusal holds against the passing census too (the mutant
gains a 12th missing mapping and is refused).

## W2 — Scaffold

**F2 (projection non-empty)**: the bridge query CONSTRUCT must yield ≥1 `rust:Function` per
contract subsystem and every rust-pack gate must return ≥1 row against the bridged graph
(witnessed 0 rows pre-bridge). A gate returning 0 rows must FAIL, not skip.

STATUS (2026-10-31, plan-update lane 4): **WITNESSED.** `scripts/run_bridge.py` — bridged
graph is non-empty and 5 rust-pack gates each return ≥1 row of coverage against it.
Positive control witnessed: the drop-mapping mutation flips gate `030` to fail, so the
gates are not vacuously green. Earlier pre-bridge 0-rows witness (F13 lane) stands.

**F2a (regeneration determinism)**: `extract → ttl` twice; byte-identical output, else
FAIL (nondeterministic serializer = forbidden class).

STATUS (2026-10-31, plan-update lane 4): **WITNESSED (x2).** extract→ttl run twice,
byte-identical output, witnessed by multiple lanes (F13 receipt + repeat witnesses in the
plan-update wave).

## W3 — First integration slice

**F3 (stream court)**: avec-ffi consumer test ingests a stardf-capi-produced
ArrowArrayStream; passes on correct wiring; **flips to fail** under the mismatched-allocator
mutant (stardf bytes routed through avec's release callback). Mutant must be caught at
court time, not UB.

STATUS (2026-10-31, plan-update lane 4): **WITNESSED (stardf-side) / NOT RUN (avec-side).**
Stardf-side: mismatched-allocator mutant-cross-alloc flip witnessed (mutant caught at
court time, not UB; see W10/F3 receipts). The avec-ffi consumer ingestion half of the
court has not been run yet — loud-missing until it is.

**F3a (allocation identity)**: because CountingAlloc does not count deallocs
(`alloc_counter.rs:65-67`), the court asserts each released pointer was minted by the
allocator that owns the release path. A court asserting only "0 allocs" is vacuous here.

STATUS (2026-10-31, plan-update lane 4): **WITNESSED (stardf-side) / NOT RUN (avec-side).**
Mutant-cross-alloc flip witnessed (release of a pointer minted by the other allocator is
detected by the ownership hook, not "0 allocs"). Detection hook is stardf-side; the
avec-side release-path half is not run yet.

## W4 — Equivalence ladder

**F4 (header freeze)**: stardf snapshot regenerated from contract targetSymbols; test
asserts full prototype-set equality with the committed stardf header. Flips when a
prototype is added/changed/removed (GONE/NEW diff report, ported from
`abi_signatures.rs:239-286`).

STATUS (2026-10-31, plan-update lane 4): **PARTIAL.** c_smoke green (F12/C10 receipts —
GONE/NEW diff mechanics witnessed at smoke level). The full prototype-set equality court
against the committed stardf header remains N/A-yet: the stardf snapshot has not been
regenerated from contract targetSymbols; snapshot court untestable until then.

**F4a (golden masters)**: each ported purrdf `abi.rs` test class must pass on stardf AND
fail when its subject behavior is deliberately mutated (one representative mutation per
class; untested mutation = unproven oracle).

STATUS (2026-10-31, plan-update lane 4): **N/A-YET (loud-missing).** No purrdf `abi.rs`
test class has been ported to stardf; no mutation-per-class court is possible yet.

**F4b (GTS byte-freeze)**: stardf-side `.sha256` manifest over the copied vectors (purrdf's
gate does not police them, `check-corpus-frozen.py:52-55`); corrupted copy must FAIL the
manifest check.

STATUS (2026-10-31, plan-update lane 4): **WITNESSED (columnar surface).**
`golden_bytes` manifest exists stardf-side for the copied columnar vectors; the corrupted-
copy FAIL is witnessed — corrupting one byte of a vector FAILs the manifest check, and the
shim-court run flipped (baseline → before → shim `SHIM-COURT` → after → restore
byte-exact). The full GTS-vector-set manifest parity with purrdf's gate
(`check-corpus-frozen.py:52-55`) beyond the columnar surface is not yet claimed.

## W5 — CI + receipt

**F5 (determinism court)**: two CI runs produce identical `receipt_sha256` +
`artifacts_sha256` (dsrust model, `ci.yml:167-196`); any drift FAILs.

STATUS (2026-10-31, plan-update lane 4): **N/A-YET (loud-missing).** No CI runs producing
`receipt_sha256`/`artifacts_sha256` exist for stardf (W5 not landed).

**F5a (replay)**: extract→verify twice locally: byte-identical TTL + identical exit codes;
second run differing = nondeterminism FAIL.

STATUS (2026-10-31, plan-update lane 4): **WITNESSED.** Replay pairs witnessed:
`verify.py` digest `cb57ce4e` stable across the corpus growing 50→93 files
(extract→verify re-run, byte-identical TTL, identical exits). The two-run CI determinism
pairing of F5 remains N/A-yet.

## Standing risks (from 20-lane wave, lane risk-register)

- **R1 license skew** (purrdf MIT/Apache/MulanPSL vs avec P28-SIL sovereign): falsifier =
  dependency-edge gate that FAILs on a P28-SIL→MIT/Apache edge without a registered
  compatibility receipt. Must exist before W3 crosses the boundary.
- **R2 cross-allocator release**: covered by F3/F3a.
- **R3 borrowed-pointer lifetime** (rowcursor/TermView borrows die at next-advance,
  `purrdf.h:1066-1078`): falsifier = use-after-advance court; debug-poison/guard, else
  mark UNKNOWN whether purrdf-class debug builds detect it.
- **R4 quad alignment**: existing compile-time asserts (`layout.rs:59-69`) stay pinned;
  stardf arena allocates at 64-byte granularity — an arena emitting non-64-aligned quads
  FAILs a debug-assert court.
- **R5 aspirational-TTL claims**: no plan or receipt may cite `interopSurface
  "ArrowArrayStream"` or any ASPIRATIONAL claim as an existing fact until its wave lands
  real code; violation = overclaimed standing, receipt invalid.
