# GL-ERRC-022 — Wire `dsrust-disposition-proposer`'s `propose-disposition` CLI into the admission workflow

**Status:** `EXECUTED` — real recipe added, real binary compiled and invoked, see
"Acceptance (executed)" below for the actual command output
**Base:** `seanchatmangpt/ggen-legacy@f9b283e` (HEAD at drafting time)
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

**Recovery note**: this ticket was drafted by the "create" quadrant judge in
the same exploration pass that produced `GL-ERRC-020` — three quadrant
agents (`eliminate`, `reduce`, `create`) raced on the filename
`tickets/GL-ERRC-020.md` in that pass and only `eliminate`'s content
survived. This file reconstructs `create`'s real, already-verified finding
from the workflow's own returned result (not re-invented), given a real
unused id (`022`).

## Outcome

`tools/dsrust-disposition-proposer` is a real, tested crate
(`Cargo.toml` declares `[[bin]] name = "propose-disposition"`, `src/main.rs`
present, real unit tests per commit `60abd88`) that proposes a legacy-
capability disposition — but nothing wires it into this repo's admission
workflow: `grep -rn "dsrust-disposition-proposer|propose-disposition"
justfile tools/v26.8.1/justfile .github/workflows/*.yml` returns zero
matches, and no `tickets/GL-*.md` file owns this crate. This ticket wires
the existing, working CLI in as an optional, suggestion-only pre-step —
it does not change what the admission workflow actually admits.

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md` —
check there before assuming sole ownership of a path below.)

```text
justfile                              # new recipe only, additive
tools/dsrust-disposition-proposer/    # no source change — wiring only, not modifying the crate's own logic
tickets/GL-ERRC-022.md
```

No change to `tools/v26.8.1/legacy_archaeology.py`'s `CATALOG`/
`draft_candidates()` (GL-ARCH-003/GL-ERRC-008's boundary) — this ticket
adds a separate, optional recipe a human can run, it does not auto-invoke
the proposer inside the existing archaeology pipeline.

## Hard laws

1. The proposer's output is **suggestion-only** — this ticket must not make
   `propose-disposition`'s output auto-write into `CATALOG` or
   `draft-candidates.json`. A human still decides.
2. The new `justfile` recipe is additive; it does not change any existing
   recipe's behavior.
3. No new CI step is added by this ticket — CLI wiring only (a future
   ticket may separately propose making this a CI check, out of scope
   here per the ticket's own "optional pre-step" framing).

## Falsifiers

- `just propose-disposition` (or whatever recipe name is chosen) does not
  exist / fails to invoke the real binary.
- The proposer's output is silently merged into `CATALOG` or
  `draft-candidates.json` without a human step (Hard Law 1).
- Any existing `justfile` recipe's behavior changes as a side effect.

## Acceptance (executed)

Added recipe (`justfile`, additive only, not wired into `ci`/`ci-all`/`v26-ci`):

```just
propose-disposition *ARGS:
    cargo run --manifest-path tools/dsrust-disposition-proposer/Cargo.toml --bin propose-disposition -- {{ARGS}}
```

Real command output from this session (main checkout, not a worktree):

```console
$ just --list | grep -i disposition
    propose-disposition *ARGS # Requires GROQ_API_KEY in the environment for a real proposal (not needed for --help).
# exit code: 0

$ just propose-disposition --help
   Compiling dsrust-disposition-proposer v0.1.0 (/Users/sac/ggen-legacy/tools/dsrust-disposition-proposer)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 14.52s
     Running `tools/dsrust-disposition-proposer/target/debug/propose-disposition --help`
Real dsrust/Groq disposition proposal for a legacy capability -- human/tool review only, never auto-admitting

Usage: propose-disposition [OPTIONS] --capability-id <CAPABILITY_ID> --historical-source-commit <HISTORICAL_SOURCE_COMMIT> --legacy-source-path <LEGACY_SOURCE_PATH> --default-behavior <DEFAULT_BEHAVIOR> --evidence-fixtures <EVIDENCE_FIXTURES>

Options:
      --capability-id <CAPABILITY_ID>
      --historical-source-commit <HISTORICAL_SOURCE_COMMIT>
      --legacy-source-path <LEGACY_SOURCE_PATH>
      --default-behavior <DEFAULT_BEHAVIOR>
      --evidence-fixtures <EVIDENCE_FIXTURES>
      --model <MODEL>            Groq model id, without the `openai/` provider prefix dsrust expects [default: llama-3.3-70b-versatile]
  -h, --help                     Print help
# exit code: 0

$ git diff --stat -- justfile
 justfile | 9 +++++++++
 1 file changed, 9 insertions(+)

$ git status --porcelain --untracked-files=all -- justfile tickets/GL-ERRC-022.md
 M justfile
?? tickets/GL-ERRC-022.md
```

This is the real `propose-disposition` binary (clap-generated `--help`, real
`cargo run` compile of `tools/dsrust-disposition-proposer`) invoked through the
new recipe in this main checkout -- no mocking, no stub. `--help` exits via
clap before the `GROQ_API_KEY` check in `main()`, so it succeeds with no key
set, matching Hard Law 1/3 (suggestion-only pre-step, human runs it, nothing
auto-invoked). The `justfile` diff is exactly 9 insertions / 0 deletions
(additive, no existing recipe touched); `tickets/GL-ERRC-022.md` is the only
other file this ticket's boundary touches. `.github/workflows/` diff is empty
(Hard Law 3).

## Standing

`PARTIAL_ALIVE` — the wiring itself is real and verified end-to-end this
session (recipe exists, real binary compiles and runs, `--help` exits 0). Not
promoted to full `ALIVE` because a real disposition *proposal* call (passing
all five required args plus a live `GROQ_API_KEY`) was not exercised in this
run -- only the argument-parsing/help path was. See
`docs/v26.9.1/innovation-candidates.md`'s #1-ranked candidate (score 10) for
the original finding this ticket closes.
