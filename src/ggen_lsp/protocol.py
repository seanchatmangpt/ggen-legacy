"""Content-Length framing and stdio lifecycle for the ggen reference LSP."""
from __future__ import annotations

import io
import json
import sys
from typing import Any, BinaryIO, Mapping, Sequence

from .dispatch import GgenLanguageServer

MAX_FRAME_BYTES = 16 * 1024 * 1024

class TransportRefusal(RuntimeError):
    """Fatal frame-level refusal where stream resynchronization is unsafe."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code

def read_frame(stream: BinaryIO) -> bytes | None:
    """Read one Content-Length frame; return None on clean EOF."""
    headers: dict[str, str] = {}
    saw_any = False
    while True:
        line = stream.readline()
        if line == b"":
            if not saw_any:
                return None
            raise TransportRefusal("GGEN-LSP-TRANSPORT-001", "Unexpected EOF inside headers.")
        saw_any = True
        if line in {b"\r\n", b"\n"}:
            break
        try:
            decoded = line.decode("ascii").strip()
        except UnicodeDecodeError as error:
            raise TransportRefusal("GGEN-LSP-TRANSPORT-002", "Headers must be ASCII.") from error
        if ":" not in decoded:
            raise TransportRefusal("GGEN-LSP-TRANSPORT-003", f"Malformed header line: {decoded!r}.")
        name, value = decoded.split(":", 1)
        headers[name.strip().lower()] = value.strip()
    raw_length = headers.get("content-length")
    if raw_length is None:
        raise TransportRefusal("GGEN-LSP-TRANSPORT-004", "Missing Content-Length header.")
    try:
        length = int(raw_length)
    except ValueError as error:
        raise TransportRefusal("GGEN-LSP-TRANSPORT-005", "Content-Length must be an integer.") from error
    if length < 0 or length > MAX_FRAME_BYTES:
        raise TransportRefusal("GGEN-LSP-TRANSPORT-006", f"Content-Length {length} is outside 0..{MAX_FRAME_BYTES}.")
    body = stream.read(length)
    if len(body) != length:
        raise TransportRefusal("GGEN-LSP-TRANSPORT-007", f"Expected {length} body bytes, received {len(body)}.")
    return body


def write_message(stream: BinaryIO, message: Mapping[str, Any]) -> None:
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    stream.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
    stream.write(body)
    stream.flush()


def serve(stdin: BinaryIO, stdout: BinaryIO, stderr: io.TextIOBase) -> int:
    server = GgenLanguageServer()
    while not server.exit_requested:
        try:
            body = read_frame(stdin)
        except TransportRefusal as refusal:
            print(f"{refusal.code}: {refusal}", file=stderr, flush=True)
            return 2
        if body is None:
            return 0 if server.shutdown_requested else 1
        try:
            text = body.decode("utf-8")
            message = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            write_message(stdout, GgenLanguageServer._error(None, -32700, f"Parse error: {error}"))
            continue
        response, notifications = server.dispatch(message)
        if response is not None:
            write_message(stdout, response)
        for notification in notifications:
            write_message(stdout, notification)
    return 0 if server.shutdown_requested else 1


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args not in ([], ["stdio"]):
        print(f"ggen-lsp: unsupported transport arguments {args!r}; usage: ggen-lsp [stdio]", file=sys.stderr)
        return 2
    stdin = getattr(sys.stdin.buffer, "raw", sys.stdin.buffer)
    stdout = getattr(sys.stdout.buffer, "raw", sys.stdout.buffer)
    return serve(stdin, stdout, sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
