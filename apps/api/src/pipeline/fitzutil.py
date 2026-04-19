"""PyMuPDF: reduce stderr noise from recoverable PDF issues (e.g. broken structure trees)."""

from collections.abc import Iterator
from contextlib import contextmanager

import fitz


@contextmanager
def mupdf_no_stderr_errors() -> Iterator[None]:
    """Hide MuPDF errors/warnings on stderr while the block runs; restore after."""
    prev_err = fitz.TOOLS.mupdf_display_errors(False)
    prev_warn = fitz.TOOLS.mupdf_display_warnings(False)
    try:
        yield
    finally:
        fitz.TOOLS.mupdf_display_warnings(prev_warn)
        fitz.TOOLS.mupdf_display_errors(prev_err)
