# GL-RECEIPT-007 — SLSA v1.0 provenance projection + DSSE wrap (Gall checkpoint 5)

**Status:** admitted, `NOT_STARTED` — drafted this session, not executed
**Base:** `seanchatmangpt/ggen-legacy@f9b283e`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

Add an in-toto `Statement`/SLSA v1.0 provenance predicate schema
(`schemas/slsa-provenance.schema.json`) and a projector from this repo's
existing `ggen.legacy.receipt.v1` shape
(`appliance/bin/build-standing-portfolio.py`) into it; DSSE-wrap the
existing raw `openssl dgst -sign` signing step so the output is consumable
by standard tooling (`slsa-verifier`, cosign) instead of only this repo's
own bespoke verifiers.

## Authored boundary

```text
schemas/slsa-provenance.schema.json     # new
appliance/bin/build-standing-portfolio.py  # projector + DSSE wrap, additive
tickets/GL-RECEIPT-007.md
```

`appliance/bin/transparency-log.py`'s existing SHA-256 hash-chain, and every
`verify_*.py` literal-constant-equality script, remain unchanged — this
ticket adds a parallel, standards-shaped output, it does not replace the
repo's existing working verifiers.

## Explicit open question — not resolved by this ticket

**Correction (ultracode backlog item 8, verified against the real in-toto/SLSA
spec text — this ticket's original framing overclaimed a spec restriction
that doesn't exist):** in-toto's `DigestSet` keys are an open JSON object, not
a fixed enum — the spec's own worked example is
`{"somecoolhash": "abcd"} uses a non-predefined algorithm`, and SLSA v1.0's
`ResourceDescriptor.digest` has an explicit open index signature
(`[string]: string`) alongside the named `sha256`/`sha512` convenience
fields. A `{"blake3": "..."}` digest entry is spec-legal with no
"registration" required — there is no registry. The real constraint is
**interoperability, not conformance**: the spec's own consumer guidance says
"Consumers MUST only accept algorithms they consider secure and MUST ignore
unrecognized or unaccepted algorithms" — so a `slsa-verifier`/cosign-class
consumer that only recognizes the predefined names will silently ignore a
bare `blake3` key, not reject the statement.

This repo's real receipt chain (`ReceiptRecord`/`ReceiptEpochV2`, external
to this repo, in `ggen`'s `praxis-core`) uses BLAKE3 (`chain_hash_hex`). Two
resolutions exist — dual-hash (publish both `sha256` and `blake3` keys) or
publish `blake3` alone (spec-legal but invisible to sha256-only consumers) —
and per this repo's own "no self-certification" precedent
(`tickets/GL-LSP-001.md`'s "No self-certification" invariant, line 71 —
**correction**: this file previously mis-cited it as "ADR-002 handling";
`GL-LSP-001.md` has no ADR-002 label anywhere, per
`tickets/AUDIT-REPORT.md`'s check 4 finding), **which one to pick is named as
an owner decision in this ticket, not decided unilaterally here** — but the
decision is an interoperability tradeoff, not a spec-compliance question.

## Hard laws

1. No BLAKE3 receipt is silently re-labeled as SHA-256 — if dual-hashing,
   both digests are present and named explicitly.
2. The DSSE wrapper is additive alongside the existing detached-signature
   file, not a replacement, until the open question above is resolved.
3. `transparency-log.py`'s existing `append`/`verify`/`revoke` CLI and its
   chain-verification logic are untouched.

## Pre-work: DSSE wrapper prototype exists (ultracode backlog item 19)

`tools/v26.8.1/dsse_wrap.py` (new, additive-only, not wired into any
existing signing script) implements DSSE's PAE encoding and envelope shape
per spec, delegating sign/verify to the same `openssl dgst` RSA-PSS
convention this repo already uses. Real self-test passed (`python3
tools/v26.8.1/dsse_wrap.py selftest`): sign+verify round-trip succeeded
against a disposable RSA-3072 keypair (never touching real appliance key
material), and tamper detection correctly failed a mutated payload with a
real openssl "bad signature" error.

**Correction to this ticket's original premise**: the RSA-PSS `openssl
dgst -sign` step does **not** live in `appliance/bin/build-standing-portfolio.py`
as originally assumed — it's in `appliance/bin/run-reference-e2e.sh`
(signing step, verified by `appliance/bin/verify-standing-portfolio.py`/
`cross-check-portfolio.py`), with keys generated fresh per e2e run, no
fixed production key path to preserve.

This prototype is a standalone tool, not yet wired into
`run-reference-e2e.sh`'s actual signing step — that wiring, plus the
in-toto/SLSA `Statement` envelope this ticket's `Outcome` describes, remains
this ticket's real (`NOT_STARTED`) scope. Treat `dsse_wrap.py` as verified
pre-work, not as this ticket's completion.

## Falsifiers

- A `slsa-verifier`-shaped consumer rejects the projected statement for a
  reason other than the named open digest-algorithm question.
- DSSE payload/signature round-trip fails to verify against the same key
  material the existing `openssl dgst -sign` step uses.

## Acceptance (not yet run — ticket not started)

```bash
# once implemented:
python3 -c "import json,jsonschema; jsonschema.validate(json.load(open('evidence/.../slsa-provenance.json')), json.load(open('schemas/slsa-provenance.schema.json')))"
```

## Standing

`UNKNOWN` — not started. See `CLAUDE.md`'s Gall's Law checkpoint 5 and this
session's Explore finding on the receipt/provenance machinery (SLSA v1.0,
`schemas/transparency-entry.schema.json`, `build-standing-portfolio.py`).
