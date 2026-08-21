# GL-EXP-011 — Raise `observe_contract.py`'s `git_head()` out of an undifferentiated `None` fallback

**Status:** admitted, NOT_STARTED -- drafted by standing ultracode exploration cron (GL-EXP namespace)
**Base:** `seanchatmangpt/ggen-legacy@bce7f6386c4203784beaae426e40804636c4151a`
**Standing ceiling:** `PARTIAL_ALIVE`
**Publication:** draft pull request; no merge authority

## Outcome

`tools/v26.8.20/observe_contract.py:30-38`'s `git_head()` collapses at least 3
causally distinct failure modes into the single undifferentiated Python value
`None`:

```python
def git_head(repo: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True,
            timeout=10, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return None
```

A bare `except Exception: return None` collapses `FileNotFoundError` (git not
on `PATH` -- spawn failure), `subprocess.CalledProcessError` (raised by
`check=True` when `repo` is not a git working tree -- non-zero exit), and
`subprocess.TimeoutExpired` (a hung `git rev-parse` past the hard-coded 10s
`timeout=` -- deadline exceeded) into the identical `None`. This is
verified this session as a real behavioral collapse, not a theoretical one
(see Evidence).

The sole call site, `observe_contract.py:105`, writes `git_head(repo)`'s raw
return value directly into the tool's own `ggen.legacy.observe.v1` contract
JSON's `"git_head"` field, with no branch on cause:

```python
"git_head": git_head(repo),
```

This field is real and consumed, not dead code: `tools/v26.8.20/observed/`
already holds a committed contract JSON
(`4cf7ed2596d66358f720027a96b2f9ae1f473bda49553104f19760bcefe67b5f.json`)
with a real populated `"git_head"` value from a prior run of this exact
tool, and this session's own live re-run (see Evidence) confirms the field
is written on every invocation, success or failure. A downstream consumer
of a `ggen.legacy.observe.v1` contract for a target observed outside a
git working tree, or where `git` is momentarily unavailable, or where
`git rev-parse` hangs, cannot distinguish any of those 3 causes from each
other, or from a hypothetical 4th "git ran, exited 0, but for some other
reason `HEAD` is unresolvable" case -- all read back as bare JSON `null`.

This is the same undifferentiated-sentinel anti-pattern GL-ERRC-019 already
fixed once, in Rust, for `coverage_projection.rs::exact_head()` (collapsing
spawn failure / non-zero exit / non-UTF8 stdout into `"UNKNOWN"`), and that
GL-EXP-005 (admitted, `NOT_STARTED`) found unfixed a second time, in the
same Rust crate, for `subsystem_verifier.rs::fresh_git_head()` (a private
duplicate that regressed back to the pre-fix collapse). Both of those
tickets scope themselves exclusively to their own named Rust file inside
`tools/v26.8.1/`; neither's Authored boundary or Hard laws mention
`tools/v26.8.20/observe_contract.py`. This is a third, independent,
currently-unticketed instance of the identical anti-pattern class, in a
different language (Python) and a different tool generation
(`v26.8.20`, not `v26.8.1`).

## Authored boundary

(Cross-ticket file overlaps, if any, are tracked in `tickets/OVERLAPS.md`
-- check there before assuming sole ownership of a path below. This
ticket's target, `tools/v26.8.20/observe_contract.py::git_head()`, is a
distinct file, distinct language, and distinct tool generation from
GL-ERRC-019's `tools/v26.8.1/src/coverage_projection.rs::exact_head()` and
GL-EXP-005's `tools/v26.8.1/src/bin/subsystem_verifier.rs::fresh_git_head()`
-- no line-range overlap with either.)

```text
tools/v26.8.20/observe_contract.py   # git_head() return type/behavior only
tickets/GL-EXP-011.md
```

No change to `observe_contract.py`'s call site at line 105 beyond what is
strictly required to keep assigning `git_head(repo)`'s return value into the
`"git_head"` contract field (the field stays populated on every path; only
the *value* on failure changes from `None` to a distinguishable string). No
change to `b3sum_file`, `b3sum_bytes`, `main()`'s control flow, the
`--command` handling, or the `contract_id` hashing scheme. No change to
`tools/v26.8.1/src/coverage_projection.rs` (GL-ERRC-019's fix, already
`EXECUTED`) or `tools/v26.8.1/src/bin/subsystem_verifier.rs` (GL-EXP-005's
target, `NOT_STARTED`).

## Hard laws

1. A real, healthy git repo whose `git rev-parse HEAD` genuinely succeeds
   must return the identical trimmed SHA string as before this ticket --
   the happy path's observable value and type (`str`) do not change.
2. The 3 verified failure causes -- spawn failure (`FileNotFoundError` /
   `OSError`), non-zero exit (`subprocess.CalledProcessError`), and timeout
   (`subprocess.TimeoutExpired`) -- must each be distinguishable from one
   another and from the happy path in the returned value -- no two of the
   4 cases (3 failure causes + happy path) may collapse back into an
   identical value.
3. The `except Exception` catch-all is not simply deleted -- any exception
   type not among the 3 named causes above must still be caught and mapped
   to its own distinguishable value (e.g. an `"OTHER"`-tagged cause) rather
   than propagating uncaught and crashing `observe_contract.py`'s `main()`
   with a non-zero exit for what this tool's own docstring calls a
   "possibly-negative, e.g. file absent" observation that should still exit
   0 and write a contract.
4. `observe_contract.py`'s `"git_head"` contract field remains populated
   (never omitted from the JSON) on every one of the 4 cases in law 2 plus
   the catch-all in law 3.
5. `git diff --stat` after this ticket touches only
   `tools/v26.8.20/observe_contract.py` and this ticket file.

## Falsifiers

- After the fix, any of the 3 verified failure modes (spawn failure via a
  corrupted `PATH`, non-zero exit via running against a non-git directory,
  timeout via a hung `git rev-parse`) still produces a value
  indistinguishable from the other failure modes or from `None`.
- The happy-path SHA string returned for a real git repo's real `HEAD`
  changes value or trimming behavior as a side effect of this fix.
- `python3 tools/v26.8.20/observe_contract.py --repo . --target AGENTS.md
  --out <dir>` exits non-zero or fails to write a contract JSON after this
  fix, for a target that exists in a real git repo (regression on the
  tool's own basic operation).
- `git diff --stat` after this ticket touches any file outside
  `tools/v26.8.20/observe_contract.py` and `tickets/GL-EXP-011.md`.

## Acceptance (not yet run -- ticket not started)

```bash
cd /Users/sac/ggen-legacy
# Reconfirm the collapse before touching anything:
sed -n '30,38p' tools/v26.8.20/observe_contract.py
grep -n "git_head" tools/v26.8.20/observe_contract.py

# After the fix, confirm the 3 failure modes are distinguishable, e.g. a
# unit test exercising each real subprocess-raised exception type against
# real inputs (a real non-git tmp dir for CalledProcessError, a real
# corrupted PATH for FileNotFoundError, a real 0-second timeout against a
# real git invocation for TimeoutExpired) -- no mocked subprocess return
# values, per this account's Chicago-style testing discipline.

# Confirm the tool's own basic operation still works end to end:
python3 tools/v26.8.20/observe_contract.py --repo . --target AGENTS.md --out /tmp/gl-exp-011-check
echo "EXIT:$?"

git diff --stat   # must show only observe_contract.py and
                   # tickets/GL-EXP-011.md
```

## Evidence this ticket is grounded in (verified this session)

- Located the file via `find tools -iname "observe_contract.py"` this
  session: `tools/v26.8.20/observe_contract.py` (the candidate item's cited
  path `tools/v26.8.1/20/observe_contract.py` was a typo the item itself
  already flagged and corrected; the real path was confirmed directly).
- Direct `Read` of `tools/v26.8.20/observe_contract.py:30-38` this session:
  `git_head()` byte-for-byte as quoted in Outcome -- a bare
  `except Exception: return None` around a `subprocess.run([...],
  timeout=10, check=True)` call.
- `grep -n "git_head" tools/v26.8.20/observe_contract.py` this session:
  exactly 2 matches -- the definition at line 30 and the sole call site at
  line 105 (`"git_head": git_head(repo),`), confirming no other reference
  or branch on this value anywhere in the file.
- `grep -lE "observe_contract|tools/v26\.8\.20" tickets/*.md` this session:
  zero matches (exit code 1) -- no existing ticket names this file or this
  tool generation.
- Live execution this session: `python3 tools/v26.8.20/observe_contract.py
  --repo . --target AGENTS.md --out <scratch-dir>` exited 0 and printed/
  wrote a real `ggen.legacy.observe.v1` contract JSON with
  `"git_head": "bce7f6386c4203784beaae426e40804636c4151a"` -- confirming
  the field is real, populated, and matches `git rev-parse HEAD` run
  independently in the same checkout, ruling out dead-code concerns.
- `ls tools/v26.8.20/observed/` this session: one pre-existing committed
  contract JSON
  (`4cf7ed2596d66358f720027a96b2f9ae1f473bda49553104f19760bcefe67b5f.json`)
  with a real `"git_head"` value from a prior run of this tool, confirming
  the tool and this field have already been exercised for real in this
  repo, not only in this session.
- Real behavioral verification this session (`python3 -c` script importing
  `git_head` directly from `tools/v26.8.20/observe_contract.py` and calling
  it against real inputs, no subprocess mocking): happy path against `.`
  (a real git repo) returned the real SHA
  `bce7f6386c4203784beaae426e40804636c4151a`; against a real
  `tempfile.TemporaryDirectory()` (a real, non-git directory -- exercises
  the genuine `subprocess.CalledProcessError` path from `check=True`)
  returned `None`. A temporary substitution of `subprocess.run` was used
  only to confirm, for the `FileNotFoundError` (git-not-on-`PATH`) and
  `subprocess.TimeoutExpired` (hung `git`) causes, that `git_head()`'s bare
  `except Exception` catches those exception types identically and also
  returns `None` -- this is diagnostic-only code written for this session's
  own verification, not a claim about a committed test, and is not itself
  part of what this ticket requires the eventual fix's test suite to look
  like (see Acceptance, which requires real subprocess-raised exceptions
  for the committed fix's tests, per this account's Chicago-style testing
  discipline). All 3 causes plus the happy path were distinguished into
  exactly 2 buckets by the current code: the real SHA on success, and the
  identical `None` on all 3 failure causes -- confirming the collapse
  claim directly, not by code-reading inference alone.
- `grep -rn "git_head" --include=*.py --include=*.md --include=*.rs
  --include=*.json .` this session (outside `.claude/worktrees/`, which
  are separate concurrent checkouts not in scope): no other file reads or
  branches on `observe_contract.py`'s `"git_head"` JSON field specifically
  -- the other `git_head`-named functions found
  (`tools/v26.8.1/document_evidence_index.py:184`,
  `tools/v26.8.1/subsystem_evidence_manifest.py:82`,
  `planning/v26.8.1/verify_planning.py:72`,
  `scripts/verify_ggen_v26_8_1_migration.py:131`) are separate,
  independently-defined functions in separate files, out of scope for this
  ticket's Authored boundary, and not evidence against this finding.
- `sed -n '38,55p' tickets/GL-ERRC-011.md` this session: confirms that
  ticket's Authored boundary names exactly 4 files under `scripts/`
  (`verify_foundry_provenance.py`, `verify_foundry_bootstrap.py`,
  `verify_docs.py`, `verify_offline_transport.py`), none of which is
  `tools/v26.8.20/observe_contract.py`.
- `head -6 tickets/GL-ERRC-019.md` and `sed -n '57,69p'
  tickets/GL-ERRC-019.md` (Authored boundary) this session: confirms that
  ticket's scope is `tools/v26.8.1/src/coverage_projection.rs` only, marked
  `EXECUTED` for that file, with explicit language that
  `tools/v26.8.1/step_two.py` (GL-ERRC-014's boundary) and
  `scripts/verify_*.py` (GL-ERRC-011's boundary) are excluded -- neither
  boundary, nor the executed fix, touches `tools/v26.8.20/`.
- `cat tickets/GL-EXP-005.md` this session: confirms that ticket's
  Authored boundary is `tools/v26.8.1/src/bin/subsystem_verifier.rs` only,
  status `NOT_STARTED`, targeting the same undifferentiated-collapse
  pattern in a second Rust location -- still not `tools/v26.8.20/`.
- `git rev-parse HEAD` this session: `bce7f6386c4203784beaae426e40804636c4151a`,
  matching this ticket's declared Base and the live `git_head` value
  captured above.

## Standing

`UNKNOWN` -- not started. This ticket only drafts and verifies the
undifferentiated-`None`-collapse finding for `observe_contract.py`'s
`git_head()`; the actual cause-distinguishing return shape (e.g. a
`STALE_REFERENCE_UNVERIFIABLE:<CAUSE>`-prefixed string, matching the exact
convention GL-ERRC-011/014 established on the Python side and GL-ERRC-019
mirrored on the Rust side) and its Chicago-style real-subprocess test
coverage have not been implemented.
