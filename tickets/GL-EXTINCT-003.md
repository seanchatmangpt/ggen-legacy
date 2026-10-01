# GL-EXTINCT-003 — bounded protocol extinction test

**Input identity:** `portable-consequence/1` finite request/response vectors plus one replacement implementation command.

**Construction:** execute the replacement as a real subprocess only after the named original implementation path is absent. Compare exact observable responses with the finite vectors.

**Falsifiers:** original still present; process failure; non-single/non-object response; any expected response mismatch.

**Rice fence:** this establishes finite observable equivalence only. It never claims universal semantic equivalence.

**Claim ceiling:** `PARTIAL_ALIVE` for the exact vector set. External protocol standing requires independent implementations and an external conformance court.

**Verification:** `python3 tools/v26.8.19/test_protocol_extinction.py -v`.
