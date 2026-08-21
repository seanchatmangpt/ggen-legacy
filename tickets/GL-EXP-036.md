# GL-EXP-036 — Create a `justfile` recipe that runs `mdbook build`, regenerating 2 of `GL-ERRC-017`'s 5 named missing-evidence files for real

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tickets/GL-ERRC-017.md` (admitted, `NOT_STARTED`, read in full this
session) found five cited evidence paths in
`authority/project-001-promotion.json` that do not exist on disk, two of
which are `docs/book/index.html` and `docs/book/print.html`. That ticket's
own resolution treats all five paths identically -- drop each rail's
standing from `ALIVE` to `PARTIAL_ALIVE`/`UNVERIFIED` and record the
missing paths, without investigating whether any of the five is actually
regenerable.

This session verified, for real, that two of the five are: `docs/book.toml`
(the real mdbook config, at `docs/book.toml`, not repo root) points its
`src` at `docs/src/`, whose `SUMMARY.md` (26 real chapter files) already
exists and is well-formed. `mdbook` is installed locally
(`/opt/homebrew/bin/mdbook`). Running `mdbook build` for real, from the
`docs/` directory, this session:

```console
$ cd docs && mdbook build
2026-08-21 02:39:34 [INFO] (mdbook::book): Book building has started
2026-08-21 02:39:34 [INFO] (mdbook::book): Running the html backend
```

produced real output files:

```console
$ ls docs/book/index.html docs/book/print.html
docs/book/index.html
docs/book/print.html
```

-- zero errors, exit clean. `.gitignore:9` intentionally excludes
`docs/book/` (a generated-projections comment heads that section of the
file, confirmed by direct read) -- these are meant to be build artifacts,
not committed source, the identical pattern already established for
`docs/book/` alongside `evidence/appliance/`,
`evidence/offline-bundle/`, etc. in the same `.gitignore` block.

**This is a materially different situation from the other three paths
`GL-ERRC-017` names as missing.** Verified this session:
`grep -rln "foundry-runtime-candidate.json\|ggen-legacy-verifier-v26.8.1.tar.gz\|ggen-legacy-verifier-v26.8.1.receipt.json"
--include="*.py" --include="*.sh" --include="*.yml" .` returns **zero
matches** -- none of those three files has any generator script anywhere
in the repo; they are genuinely absent build artifacts with no known
production path, exactly matching `GL-ERRC-017`'s own framing
("manufacturing the missing evidence files ... would launder an
unverified build artifact into a checked-in claim"). `docs/book/index.html`
and `docs/book/print.html`, by contrast, have a real, working, one-command
generator (`mdbook build`) already present in this repo's own
`docs/book.toml` + `docs/src/` tree -- this is not fabricating evidence,
it is running the exact tool this repo already ships to produce the
artifact its own authority file cites.

**Nothing currently runs `mdbook build`.** `grep -rn "mdbook"
.github/workflows/*.yml justfile tools/v26.8.1/justfile
scripts/verify_docs.py` (run this session) returns zero matches.
`scripts/verify_docs.py`'s own book-related check (read in full this
session, lines 200-210) only verifies that every relative link inside
`docs/src/SUMMARY.md` resolves to a real `.md` file under `docs/src/` --
it never invokes `mdbook build` itself, so it cannot catch a real mdbook
rendering failure (a broken cross-chapter link, invalid markdown a
renderer chokes on, a missing include) the way an actual build would.
`grep -il "mdbook" tickets/GL-*.md` (all 55 tickets, run this session)
returns zero matches -- no existing ticket names `mdbook` at all.

`governance/claims-register.md`'s `CLM-004` (read this session) cites "a
15-chapter mdBook" as part of its evidence for a `REFERENCE_CONFORMANT`/
`ALIVE` claim ("Documentation covers a Fortune 5-scale enterprise decision
surface"). This claim currently rests on the book's source files existing
and being internally link-consistent (what `verify_docs.py` checks), not
on the book actually compiling with `mdbook` -- this ticket closes that
gap for real, rather than only for the two specific paths
`GL-ERRC-017` names.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- `justfile` already has an existing section listing prior recipe-adding
tickets; this ticket adds a new row rather than a new section, disclosed
by this same write. No existing entry for `docs/book.toml` or `mdbook`.)

```text
justfile              # new recipe only, additive
tickets/GL-EXP-036.md
tickets/OVERLAPS.md   # add a row to the existing `justfile` section
```

No change to `docs/book.toml`, `docs/src/**`, `scripts/verify_docs.py`, or
`.gitignore` -- this ticket wires the existing, already-working `mdbook
build` command in as a new recipe; it does not modify the book's own
content, config, or the existing link-check script. No change to
`tickets/GL-ERRC-017.md`'s own scope or its treatment of the other three
missing paths (`ggen-legacy-verifier-v26.8.1.tar.gz`,
`ggen-legacy-verifier-v26.8.1.receipt.json`,
`evidence/foundry-runtime-candidate.json`) -- those remain that ticket's
own, unresolved finding; this ticket only addresses the two `docs/book/`
paths, for which a real generator already exists.

## Hard laws

1. The new recipe is a pure pass-through to `mdbook build` (run with
   `docs/` as its working directory, or an equivalent `--dest-dir`/`-d`
   invocation from the repo root) -- it must not reimplement or wrap
   `mdbook`'s own build logic.
2. The new `justfile` recipe is additive; it does not change any existing
   recipe's behavior, including `ci`, `ci-all`, `v26-ci`, `planning-max`,
   or `propose-disposition`.
3. No new CI step is added by this ticket -- local wiring only, mirroring
   this repo's own established discipline for "real tool, zero wiring"
   candidates (`GL-ERRC-022`, `GL-EXP-004`, `GL-EXP-008`, `GL-EXP-012`).
   A future ticket may separately propose making a clean `mdbook build`
   exit 0 a CI/admission gate; that is out of scope here.
4. This ticket does not modify `.gitignore`'s existing `docs/book/`
   exclusion -- the built output remains a local, regenerable artifact,
   not a committed one, matching the pattern the rest of that `.gitignore`
   block already establishes for generated evidence.
5. This ticket does not edit `tickets/GL-ERRC-017.md`'s own text or
   standing decisions for the two `docs/book/` paths -- that ticket's own
   execution, whenever it happens, may independently note that a real
   `mdbook build` (via this ticket's new recipe, if it has landed) now
   makes those two specific paths locally reproducible, without this
   ticket asserting that on its behalf.

## Falsifiers

- The new recipe does not exist, or fails to invoke a real `mdbook build`.
- `mdbook build` (run via the new recipe) exits non-zero against the
  current, real `docs/src/` tree (would mean this ticket's own "zero
  errors, exit clean" claim was wrong -- re-verify and correct rather than
  landing a recipe that wraps a broken build).
- The new recipe's build output is written somewhere other than
  `docs/book/` (breaking the existing `.gitignore:9` exclusion's
  assumption).
- Any existing `justfile` recipe's behavior changes as a side effect.
- `git diff --stat` shows any file changed other than `justfile`,
  `tickets/GL-EXP-036.md`, and `tickets/OVERLAPS.md`.
- `tickets/OVERLAPS.md`'s existing `justfile` section rows (for
  `GL-PLAN-002`, `GL-ERRC-022`, `GL-EXP-004`, `GL-EXP-006`, `GL-EXP-008`,
  `GL-EXP-012`, `GL-EXP-032`) are altered rather than only appended to.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy

# Confirm the gap before fixing:
grep -rn "mdbook" .github/workflows/*.yml justfile tools/v26.8.1/justfile
  # expect: no output (zero matches)
just --list | grep -i book
  # expect: no output (recipe doesn't exist yet)
test -f docs/book/index.html && echo "already built" || echo "not built"

# After adding the recipe (proposed name: docs-book, mirroring the
# existing single-purpose recipe naming convention):
just --list | grep -i docs-book
  # expect: the new recipe listed
just docs-book
  # expect: real mdbook build output, exit 0
test -f docs/book/index.html && test -f docs/book/print.html && echo "OK: both files now real"

# Confirm existing recipes untouched:
just --list | grep -i "planning-max\|propose-disposition"

git diff --stat   # must show only justfile, tickets/GL-EXP-036.md,
                   # tickets/OVERLAPS.md
```

## Evidence this ticket is grounded in (verified this session)

- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base.
- Direct `Read` of `tickets/GL-ERRC-017.md` in full this session: confirms
  its Outcome section names exactly 5 missing evidence paths, including
  `docs/book/index.html` and `docs/book/print.html`, and its own Hard Law
  1 explicitly declines to manufacture missing evidence files.
- `find . -maxdepth 2 -iname "book.toml"` this session: `./docs/book.toml`
  -- the real mdbook config lives under `docs/`, not repo root (an earlier
  bare `mdbook build` at repo root, run this session, correctly failed
  with `Couldn't open SUMMARY.md in ".../src"`, confirming the config's
  real location matters).
- `which mdbook` this session: `/opt/homebrew/bin/mdbook` -- a real,
  locally installed binary.
- Real command run this session: `cd docs && mdbook build` -- real
  output, `[INFO] (mdbook::book): Book building has started` /
  `[INFO] (mdbook::book): Running the html backend`, no error lines, exit
  clean.
- `ls docs/book/index.html docs/book/print.html` this session (run
  immediately after the build above): both files exist -- real, freshly
  generated output, not asserted from documentation.
- `git check-ignore -v docs/book/index.html` this session:
  `.gitignore:9:docs/book/` -- confirms the built output is intentionally
  excluded from version control, the same pattern as the surrounding
  `.gitignore` block's other generated-evidence entries.
- `grep -rln
  "foundry-runtime-candidate.json\|ggen-legacy-verifier-v26.8.1.tar.gz\|ggen-legacy-verifier-v26.8.1.receipt.json"
  --include="*.py" --include="*.sh" --include="*.yml" .` this session:
  zero matches -- confirms the other 3 of `GL-ERRC-017`'s 5 missing paths
  have no known generator anywhere in the repo, unlike the two `docs/book/`
  paths this ticket addresses.
- `grep -rn "mdbook" .github/workflows/*.yml justfile tools/v26.8.1/justfile
  scripts/verify_docs.py` this session: zero matches.
- Direct `Read` of `scripts/verify_docs.py:200-210` this session: confirms
  its `book-links` check only regexes `docs/src/SUMMARY.md` for
  `.md`-file links and checks each resolves under `docs/src/` -- it never
  shells out to `mdbook` itself.
- `grep -il "mdbook" tickets/GL-*.md` this session (55 tickets): zero
  matches -- no existing ticket names `mdbook`.
- Direct `Read` of `governance/claims-register.md`'s `CLM-004` row this
  session: cites "15-chapter mdBook" as evidence for a
  `REFERENCE_CONFORMANT`/`ALIVE` claim, without the claim currently
  resting on a real `mdbook build` having been run.
- `sed -n '60,80p' tickets/OVERLAPS.md` this session: confirms the
  existing `justfile` section and its current row list
  (`GL-PLAN-002`/`GL-ERRC-022`/`GL-EXP-004`/`GL-EXP-006`/`GL-EXP-008`/
  `GL-EXP-012`/`GL-EXP-032`), none of which claims a `docs-book`-named
  recipe.

## Standing

`PARTIAL_ALIVE` ceiling only -- this ticket is drafted and admitted,
`NOT_STARTED`. No code has been written or run beyond the read-only/
already-reverted-by-nature verification commands captured above
(confirming `mdbook build` genuinely works against this repo's real
`docs/` tree today and genuinely produces the two files `GL-ERRC-017`
found missing). Executing this ticket (adding the recipe, re-running the
"Acceptance" commands, and recording their real output) is required before
any higher standing can be claimed.
