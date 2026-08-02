"""Bounded bootstrap hook for deterministic verifier manufacture.

Python loads this module because the bootstrap patcher executes from the
.migration-bootstrap directory.  The hook changes only the generated migration
verifier and refuses if the expected single insertion point drifts.
"""

from pathlib import Path
from typing import Any

_ORIGINAL_WRITE_TEXT = Path.write_text
_TARGET_NAME = "verify_ggen_v26_8_1_migration.py"
_SENTINEL = '        command_env["RUST_TEST_THREADS"] = "1"\n'
_INSERTION = (
    _SENTINEL
    + '        command_env["RUSTUP_TOOLCHAIN"] = "nightly-2026-06-22"\n'
    + '        command_env["RUSTUP_NO_UPDATE_CHECK"] = "1"\n'
)


def _write_text(self: Path, data: str, *args: Any, **kwargs: Any) -> int:
    if self.name == _TARGET_NAME and "def canonical_receipt_output(" in data:
        count = data.count(_SENTINEL)
        if count != 1:
            raise RuntimeError(
                "PINNED_RUSTUP_INSERTION_PRECONDITION_REFUSED "
                f"target={self} count={count}"
            )
        data = data.replace(_SENTINEL, _INSERTION, 1)
    return _ORIGINAL_WRITE_TEXT(self, data, *args, **kwargs)


Path.write_text = _write_text
