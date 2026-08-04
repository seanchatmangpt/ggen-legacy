# GL-AUTO-001 automation receipt

The former manual process is now represented by one command:

```bash
python3 scripts/run_autonomic_crown.py
```

That command performs syntax compilation, deterministic manufacture, replay comparison, mutation testing, exact-base diff guarding, zero-gap closure, and machine-readable evidence generation.

The pull-request workflow `.github/workflows/autonomic-crown.yml` executes the same command and uploads `evidence/autonomic/GL-AUTO-001.json` as an artifact.

Exact-head workflow observations:

- run 1: `ANDON` — refused an incomplete admitted diff surface because `scripts/verify_autonomic_finish.py` was omitted;
- repair: verifier path added to the scripted guard;
- run 2: `ALIVE`;
- run 3 at the documented head: `ALIVE`.

The separate legacy assurance workflow continues to report the pre-existing `UNADMITTED_TOP_LEVEL_SOURCE: src` condition. It is outside the authored GL-AUTO-001 boundary and is not converted into a claim about this crown.
