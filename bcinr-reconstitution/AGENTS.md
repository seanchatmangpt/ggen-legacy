# BCINR reconstruction receiver contract

This subtree extends the root `AGENTS.md` for ticket `GL-BCINR-001` and may not weaken root safety, evidence, or publication rules.

## Mission

Receive the BCINR claim/evidence contract manufactured by `seanchatmangpt/ggen`, verify it independently, and prepare a bounded reconstitution path for `seanchatmangpt/bcinr`.

```text
ggen ontology
→ ggen projection
→ byte-identical received contract
→ independent legacy verifier
→ admitted BCINR consumer contract
→ later generated/runtime integration in BCINR
```

## Authority

- producer authority: `seanchatmangpt/ggen:self-host/bcinr-evidence-contract/ontology.ttl`
- generator config: `seanchatmangpt/ggen:self-host/bcinr-evidence-contract/ggen.toml`
- receiver: this subtree
- eventual consumer: `seanchatmangpt/bcinr`

The receiver may reject malformed or overclaiming contracts. It cannot alter the producer ontology, certify ggen manufacture, grant BCINR runtime standing, or perform consequential DO.

## Generated boundary

A received producer projection must be copied byte-for-byte from an observed ggen output. Do not author a substitute JSON file by hand.

Until an exact generated contract is available, the receiver verifier itself may be syntax-checked but contract synchronization remains `BLOCKED:PROJECTION_UNAVAILABLE`.

## Acceptance

```bash
python3 bcinr-reconstitution/verify_contract.py --contract /path/to/generated/bcinr-evidence-contract.json
```

A successful receiver check proves only contract-shape and anti-overclaiming agreement. It does not prove branchlessness, formal correctness, WCET, semantic equivalence, runtime receipts, or BCINR release standing.
