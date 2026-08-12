# GL-DSPY-001 — Admit `dsrust` as an exact external reconstitution subject

## Outcome

Create the first executable external-source rail for `ggen-legacy` using the permissively licensed `seanchatmangpt/dsrust` clone as the frozen specimen. The rail must manufacture deterministic observation evidence from an exact source identity without upgrading observations into semantic admissions.

## Identity

- reconstitution repository: `seanchatmangpt/ggen-legacy`
- admitted base: `ef2502522a01ef413c588f9ee135139b097efb7b`
- legacy specimen: `seanchatmangpt/dsrust`
- exact legacy commit: `f24adde08c1d8850e4d7079d019643bb40f905cb`
- license expression: `MIT OR Apache-2.0`
- source manifest edition: `2024`
- source-declared `rust-version`: absent
- hosted verification toolchain: `1.86.0` (evidence-derived verifier floor, not source-declared MSRV)
- observed workspace members: `derive`, `bridge`, `tpe`, `pyrng`, `gepa`

The exact commit is immutable for this ticket. Moving the source ref requires a new admission event and new receipt.

## Toolchain discovery evidence

Rust `1.85.0` was executed against the exact frozen lockfile and refused before compilation because the locked ICU 2.2.0 / `idna_adapter` dependency set requires rustc `1.86`. The dependency graph is not rewritten to manufacture compatibility. Rust `1.86.0` is therefore the next admitted verifier candidate.

## Chesterton fence

The existing `tools/v26.8.1/legacy_archaeology.py` is preserved. It encodes historical ggen-specific archaeology and therefore cannot lawfully be generalized by silently replacing its curated catalog. This ticket adds a separate external-source observation front end and reuses the repository's manifest-driven equivalence machinery later in the reconstitution chain.

The existing bounded planning replay is also preserved while restoring the repository's declared one-workflow topology by moving that job into the canonical CI workflow.

## Calculus

`source tree -> exact identity admission -> tracked-file evidence -> Cargo evidence -> lexical Rust observations -> deterministic observation graph -> receipt -> replay`

Objects emitted by this ticket are **OBSERVED** only:

- source capsule
- workspace observations
- Rust lexical surface observations
- N-Triples observation graph
- reconstitution receipt

No object produced here has execution authority and no semantic domain concept is admitted merely because a Rust identifier exists.

## Acceptance

1. Reject a source whose checked-out `HEAD` differs from the contract SHA with `SOURCE_IDENTITY_MISMATCH`.
2. Reject tracked local source mutations with `SOURCE_TREE_DIRTY`.
3. Verify all contract-declared source files exist, including every workspace-member manifest observed at the frozen commit.
4. Execute `cargo metadata --format-version 1 --locked --no-deps` against the exact specimen in hosted verification.
5. Execute the specimen's workspace/all-target baseline against the exact specimen with the explicitly selected verifier toolchain.
6. Run reconstitution twice against the same exact checkout and require identical receipt/artifact digests.
7. Observe all tracked Rust paths rather than silently restricting archaeology to a guessed subtree.
8. Preserve planning replay after consolidating CI to one workflow.
9. Upload the exact reconstitution evidence from the pull-request head.

## Exclusions

This ticket does **not** claim:

- a source-declared MSRV;
- semantic DSPy ontology admission;
- a ggen pack has been manufactured;
- a replacement Rust ecosystem exists;
- differential equivalence with the legacy specimen;
- clean-room predecessor retirement;
- production standing.

Those claims remain `UNKNOWN` until observed execution crosses their respective boundaries.

## Falsifiers

- source SHA mismatch;
- dirty tracked source;
- missing expected license/workspace files;
- Cargo metadata failure at the frozen subject;
- selected verifier toolchain differs from `1.86.0`;
- legacy workspace test failure;
- nondeterministic reconstitution digest on replay;
- any emitted observation labeled as admitted semantic truth without an explicit admission artifact.

## Replay

Hosted replay command after the exact source checkout:

```bash
RUSTUP_TOOLCHAIN=1.86.0 \
python3 tools/v26.8.1/external_reconstitution.py \
  --source _subjects/dsrust \
  --contract reconstitution/dsrust/source-contract.json \
  --out evidence/reconstitution/dsrust/run1
```

Repeat with `run2` and compare `receipt_sha256` plus `artifacts_sha256` exactly.
