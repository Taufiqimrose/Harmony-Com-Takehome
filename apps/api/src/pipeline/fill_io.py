"""PDF stub output, thumbnails, zip bundling (PyMuPDF helpers)."""

from __future__ import annotations

import zipfile
from pathlib import Path

import fitz  # PyMuPDF
from pypdf import PdfReader

from src.pipeline.fitzutil import mupdf_no_stderr_errors


def _collect_button_on_rects(src: Path) -> list[list[tuple[float, float, float, float]]]:
    """
    Return, for each page, the list of rects of button widgets whose current
    appearance state is "on" (i.e. the widget should render as checked). We read
    this with pypdf because it reliably reflects the /V and /AS written during
    fill_acroform.
    """
    reader = PdfReader(str(src))
    pages_rects: list[list[tuple[float, float, float, float]]] = []
    for page in reader.pages:
        on_rects: list[tuple[float, float, float, float]] = []
        for annot_ref in page.get("/Annots") or []:
            annot = annot_ref.get_object()
            if annot.get("/Subtype") != "/Widget":
                continue
            parent = annot.get("/Parent")
            ft = (parent.get_object().get("/FT") if parent else None) or annot.get("/FT")
            if ft != "/Btn":
                continue
            ap = annot.get("/AP")
            ap_n_keys = [str(k) for k in ((ap.get("/N") if ap else {}) or [])]
            rect = annot.get("/Rect")
            if not rect:
                continue
            as_val = annot.get("/AS")
            as_str = str(as_val) if as_val else "/Off"
            if as_str == "/Off" or as_str not in ap_n_keys:
                continue
            on_rects.append(
                (float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])),
            )
        pages_rects.append(on_rects)
    return pages_rects


def _strip_button_widgets_and_draw_x(
    doc: fitz.Document,
    on_rects_per_page: list[list[tuple[float, float, float, float]]],
) -> None:
    """Remove checkbox/radio widgets and draw an "X" on each on-state rect."""
    for page_index, page in enumerate(doc):
        for widget in list(page.widgets() or []):
            if widget.field_type in (
                fitz.PDF_WIDGET_TYPE_CHECKBOX,
                fitz.PDF_WIDGET_TYPE_RADIOBUTTON,
            ):
                page.delete_widget(widget)

        if page_index >= len(on_rects_per_page):
            continue
        page_h = page.rect.height
        for x0, y0, x1, y1 in on_rects_per_page[page_index]:
            # PDF rects are y-up (origin bottom-left); PyMuPDF draws are y-down.
            rect = fitz.Rect(x0, page_h - y1, x1, page_h - y0)
            pad = min(rect.width, rect.height) * 0.15
            inner = fitz.Rect(
                rect.x0 + pad,
                rect.y0 + pad,
                rect.x1 - pad,
                rect.y1 - pad,
            )
            stroke = max(0.8, min(rect.width, rect.height) * 0.18)
            page.draw_line(
                fitz.Point(inner.x0, inner.y0),
                fitz.Point(inner.x1, inner.y1),
                color=(0, 0, 0),
                width=stroke,
            )
            page.draw_line(
                fitz.Point(inner.x0, inner.y1),
                fitz.Point(inner.x1, inner.y0),
                color=(0, 0, 0),
                width=stroke,
            )


def rasterize_pdf(src: Path, dst: Path, dpi: int = 200) -> None:
    """
    Re-render each page of ``src`` as a raster image and write a new PDF to ``dst``.

    Some PDF viewers (notably macOS Preview/Quartz) refuse to render specific page
    regions on HCD AcroForm templates, so filled checkbox/radio marks appear blank
    even though the field values and appearance streams are correct. Rasterizing
    every page produces a visually identical PDF that renders reliably in all
    viewers (Chrome, Preview, Acrobat, mobile, etc.) at the cost of text search.

    Checked button widgets are replaced with an inline "X" on the page before
    rasterization, so the output uses a consistent "X" mark across all viewers
    instead of the viewer-specific dot glyph PyMuPDF draws for form widgets.
    """
    on_rects_per_page = _collect_button_on_rects(src)
    with mupdf_no_stderr_errors():
        source = fitz.open(str(src))
        try:
            _strip_button_widgets_and_draw_x(source, on_rects_per_page)
            target = fitz.open()
            try:
                for page in source:
                    pix = page.get_pixmap(dpi=dpi, alpha=False)
                    new_page = target.new_page(
                        width=page.rect.width,
                        height=page.rect.height,
                    )
                    new_page.insert_image(
                        fitz.Rect(0, 0, page.rect.width, page.rect.height),
                        stream=pix.tobytes("png"),
                    )
                target.save(str(dst), garbage=3, deflate=True)
            finally:
                target.close()
        finally:
            source.close()


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
