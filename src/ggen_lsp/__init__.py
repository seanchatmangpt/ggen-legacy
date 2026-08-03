"""ggen-legacy dependency-free language-server reference runtime."""

from .server import GgenLanguageServer, analyze_document, main

__all__ = ["GgenLanguageServer", "analyze_document", "main"]
__version__ = "26.8.1"
