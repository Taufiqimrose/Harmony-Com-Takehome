"""PDF stub output, thumbnails, zip bundling (PyMuPDF helpers)."""

from __future__ import annotations

import zipfile
from pathlib import Path

import fitz  # PyMuPDF

from src.pipeline.fitzutil import mupdf_no_stderr_errors


def write_stub_pdf(path: Path, title: str, lines: list[str]) -> int:
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    y = 72
    page.insert_text((72, y), title, fontsize=14)
    y += 28
    for line in lines:
        page.insert_text((72, y), line[:120], fontsize=10)
        y += 16
        if y > 720:
            break
    doc.save(str(path))
    page_count: int = int(doc.page_count)
    doc.close()
    return page_count


def render_thumb(pdf_path: Path, out_png: Path) -> None:
    with mupdf_no_stderr_errors():
        doc = fitz.open(str(pdf_path))
        try:
            page = doc.load_page(0)
            mat = fitz.Matrix(0.5, 0.5)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            pix.save(str(out_png))
        finally:
            doc.close()


def write_zip(zip_path: Path, filled_dir: Path, forms: tuple[tuple[str, str], ...]) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for _form_id, filename in forms:
            fp = filled_dir / filename
            zf.write(fp, arcname=filename)


def pdf_page_count(path: Path) -> int:
    with mupdf_no_stderr_errors():
        doc = fitz.open(str(path))
        try:
            return int(doc.page_count)
        finally:
            doc.close()
