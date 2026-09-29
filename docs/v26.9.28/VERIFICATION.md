# v26.9.28 verification and replay

The v26.9.28 crown verifies a composition contract, not the complete behavior of
every external repository.

## Local court

```bash
python3 -m unittest scripts/tests/test_v26_9_28_crown.py -v
python3 scripts/verify_v26_9_28.py --root .
```

The local court verifies exact SHA syntax, capability ownership, the single
consequential-DO owner, candidate non-promotion, required semantic/planning
artifacts, release ordering, and negative controls.

## Exact external subjects

The crown additionally uses `--probe-remotes`. Required external owners are
fetched by their 40-character commit SHA into disposable bare Git repositories.
A branch name, tag name, latest commit, or API lookup is never substituted for
the pinned subject.

## Non-promoting manufacture and replay

```bash
python3 scripts/manufacture_v26_9_28_receipt.py \
  --expected-revision "$(git rev-parse HEAD)" --output /tmp/a.json
python3 scripts/manufacture_v26_9_28_receipt.py \
  --expected-revision "$(git rev-parse HEAD)" --output /tmp/b.json
cmp /tmp/a.json /tmp/b.json
```

The producer receipt is always `PARTIAL_ALIVE` and
`final_admission_allowed=false`. Only the independent crown can promote the
bounded v26.9.28 composition corpus after the replay pair and remote subject
probes agree.

## Falsifiers

The crown must refuse mutable refs, additional DO owners, candidate authority
widening, replay divergence, digest drift, producer self-certification, and
release before replay.
