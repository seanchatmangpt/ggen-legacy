# Contributing

Read `AGENTS.md`, `RELEASE_CONTROL.md`, and the active deterministic ticket before changing the repository.

Preserve the authority boundary, use bounded diffs, identify positive witnesses and negative falsifiers, and never hand-edit generated output as the final repair. Documentation changes that widen a customer-facing claim must update the claims register.

Run:

```bash
python3 scripts/verify_docs.py --strict
```

A pull request reports exact base, scope, exclusions, commands, observed results, receipts, replay status, remaining unknowns, and next lawful checkpoint.
