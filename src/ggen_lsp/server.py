"""Public facade for the dependency-free ggen reference LSP."""
from .analyzers import analyze_document
from .dispatch import GgenLanguageServer
from .protocol import main, read_frame, serve, write_message

__all__ = [
    "GgenLanguageServer",
    "analyze_document",
    "main",
    "read_frame",
    "serve",
    "write_message",
]
