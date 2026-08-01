#!/usr/bin/env python3
"""Resume the Enterprise Architecture Foundry from committed evidence to ALIVE.

The controller is intentionally sequential. Every mutating workstream starts
from a clean exact branch head, emits its native receipt, transfers ownership
of superseded mutable projections, commits the complete consequence, replays
all active receipts, and only then publishes the next head.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


class Refusal(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def payload(self) -> dict[str, str]:
        return {
            "schema": "ggen.enterprise-architecture-foundry.completion-refusal/1",
            "code": self.code,
            "message": self.message,
        }


def run(argv: Sequence[str], cwd: Path, *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(argv),
        cwd=cwd,
        text=True,
        capture_output=capture,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "RUSTC_WRAPPER": ""},
    )
    if completed.returncode != 0:
        detail = (completed.stderr if capture else "").strip()
        raise Refusal(
            "FOUNDRY_COMMAND_FAILED",
            f"exit={completed.returncode} cwd={cwd} command={list(argv)!r} stderr={detail[-4000:]}",
        )
    return completed


def output(argv: Sequence[str], cwd: Path) -> str:
    return run(argv, cwd, capture=True).stdout.strip()


def purge_transients(root: Path) -> None:
    for path in root.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)
    for relative in (".pytest_cache", ".mypy_cache", ".ruff_cache"):
        path = root / relative
        if path.exists():
            shutil.rmtree(path)


def require_clean(root: Path) -> None:
    purge_transients(root)
    status = output(["git", "status", "--porcelain=v1", "--untracked-files=all"], root)
    if status:
        raise Refusal("FOUNDRY_CORPUS_DIRTY", status)


def sync_remote(root: Path, branch: str) -> None:
    require_clean(root)
    run(["git", "fetch", "--quiet", "origin", branch], root)
    local = output(["git", "rev-parse", "HEAD"], root)
    remote = output(["git", "rev-parse", f"origin/{branch}"], root)
    if local == remote:
        return
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", local, remote], cwd=root
    ).returncode == 0
    if not ancestor:
        raise Refusal(
            "FOUNDRY_REMOTE_DIVERGED",
            f"local={local} remote={remote}; refusing to rebase receipt-bearing consequences",
        )
    run(["git", "reset", "--hard", remote], root)
    require_clean(root)


def state(root: Path) -> dict:
    return json.loads((root / "foundry/workstreams/state.json").read_text(encoding="utf-8"))


def status(root: Path, workstream: str) -> str:
    return str(state(root)["workstreams"][workstream]["status"])


def normalize(root: Path) -> None:
    run(
        [
            sys.executable,
            "verifiers/normalize_foundry_receipts_interphase.py",
            "apply",
            "--root",
            ".",
            "--ownership",
            "foundry/receipt-ownership.json",
        ],
        root,
    )
    purge_transients(root)


def replay(runtime: Path, source: Path, corpus: Path) -> None:
    run(
        [str(runtime / "ggen-foundry"), "replay", "--source", str(source), "--corpus", str(corpus)],
        runtime.parent.parent.parent,
    )


def verify(runtime: Path, program: Path, source: Path, corpus: Path) -> None:
    run(
        [
            str(runtime / "ggen-foundry"),
            "verify",
            "--program",
            str(program),
            "--source",
            str(source),
            "--corpus",
            str(corpus),
        ],
        runtime.parent.parent.parent,
    )


def commit_publish(
    root: Path,
    branch: str,
    message: str,
    runtime: Path,
    source: Path,
) -> str:
    purge_transients(root)
    raw = output(["git", "status", "--porcelain=v1", "--untracked-files=all"], root)
    if not raw:
        replay(runtime, source, root)
        return output(["git", "rev-parse", "HEAD"], root)

    unexpected = []
    for line in raw.splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith("foundry/"):
            unexpected.append(line)
    if unexpected:
        raise Refusal("FOUNDRY_UNOWNED_MUTATION", "\n".join(unexpected))

    run(["git", "add", "foundry"], root)
    run(["git", "commit", "--no-verify", "-m", message], root)
    replay(runtime, source, root)
    head = output(["git", "rev-parse", "HEAD"], root)
    pushed = subprocess.run(
        ["git", "push", "origin", f"HEAD:{branch}"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if pushed.returncode != 0:
        raise Refusal(
            "FOUNDRY_REMOTE_MOVED_DURING_PHASE",
            f"head={head} stderr={pushed.stderr[-4000:]}",
        )
    require_clean(root)
    return head


def run_stage(
    root: Path,
    branch: str,
    workstream: str,
    command: Sequence[str],
    runtime: Path,
    source: Path,
) -> dict[str, str]:
    sync_remote(root, branch)
    observed = status(root, workstream)
    if observed == "ADMITTED":
        replay(runtime, source, root)
        return {"workstream": workstream, "result": "ALREADY_ADMITTED", "head": output(["git", "rev-parse", "HEAD"], root)}
    if observed != "READY":
        raise Refusal("FOUNDRY_WORKSTREAM_NOT_READY", f"{workstream}={observed}")

    require_clean(root)
    run(command, runtime.parent.parent.parent)
    normalize(root)
    head = commit_publish(
        root,
        branch,
        f"feat(foundry): admit workstream {workstream}",
        runtime,
        source,
    )
    if status(root, workstream) != "ADMITTED":
        raise Refusal("FOUNDRY_WORKSTREAM_NOT_ADMITTED", workstream)
    return {"workstream": workstream, "result": "ADMITTED", "head": head}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--runtime-target", type=Path, required=True)
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    corpus = args.corpus.resolve()
    source = args.source.resolve()
    runtime = args.runtime_target.resolve()
    program = args.program.resolve()
    results: list[dict[str, str]] = []

    try:
        sync_remote(corpus, args.branch)
        normalize(corpus)
        commit_publish(
            corpus,
            args.branch,
            "fix(foundry): normalize inter-phase receipt ownership",
            runtime,
            source,
        )

        products = runtime / "admit_products"
        results.append(run_stage(corpus, args.branch, "G", [str(products), "--program", str(program), "--source", str(source), "--corpus", str(corpus), "packs"], runtime, source))
        results.append(run_stage(corpus, args.branch, "H", [str(products), "--program", str(program), "--source", str(source), "--corpus", str(corpus), "equivalence"], runtime, source))
        results.append(run_stage(corpus, args.branch, "I", [str(runtime / "admit_verification"), "--program", str(program), "--source", str(source), "--corpus", str(corpus)], runtime, source))
        results.append(run_stage(corpus, args.branch, "J", [str(runtime / "admit_clean_room"), "--program", str(program), "--source", str(source), "--corpus", str(corpus)], runtime, source))
        results.append(run_stage(corpus, args.branch, "K", [str(runtime / "admit_reference"), "--program", str(program), "--source", str(source), "--corpus", str(corpus)], runtime, source))

        sync_remote(corpus, args.branch)
        standing_path = corpus / "foundry/standing.json"
        standing = json.loads(standing_path.read_text(encoding="utf-8")) if standing_path.exists() else {}
        if standing.get("standing") != "ALIVE" or standing.get("admitted") is not True:
            require_clean(corpus)
            run([str(runtime / "admit_final"), "--program", str(program), "--source", str(source), "--corpus", str(corpus)], runtime.parent.parent.parent)
            normalize(corpus)
            head = commit_publish(corpus, args.branch, "feat(foundry): admit terminal ALIVE theorem", runtime, source)
            results.append({"workstream": "FINAL", "result": "ALIVE", "head": head})
        else:
            results.append({"workstream": "FINAL", "result": "ALREADY_ALIVE", "head": output(["git", "rev-parse", "HEAD"], corpus)})

        replay(runtime, source, corpus)
        verify(runtime, program, source, corpus)
        final_state = state(corpus)
        missing = [letter for letter in "ABCDEFGHIJK" if final_state["workstreams"][letter]["status"] != "ADMITTED"]
        final_standing = json.loads((corpus / "foundry/standing.json").read_text(encoding="utf-8"))
        if missing or final_standing.get("standing") != "ALIVE" or final_standing.get("admitted") is not True:
            raise Refusal("FOUNDRY_TERMINAL_THEOREM_OPEN", f"missing={missing} standing={final_standing}")

        report = {
            "schema": "ggen.enterprise-architecture-foundry.completion-report/1",
            "standing": "ALIVE",
            "workstreams": {letter: final_state["workstreams"][letter]["status"] for letter in "ABCDEFGHIJK"},
            "results": results,
            "head": output(["git", "rev-parse", "HEAD"], corpus),
            "receipt_replay": True,
            "independent_verification": True,
            "direct_actuation": False,
        }
        text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    except Refusal as refusal:
        payload = refusal.payload()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
