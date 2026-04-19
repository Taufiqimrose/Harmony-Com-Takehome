"""PDF ingest: validate, save, rasterize page 1."""

import asyncio
import hashlib

import fitz  # PyMuPDF
from pypdf import PdfReader

from src.pipeline.events import broadcast
from src.pipeline.fitzutil import mupdf_no_stderr_errors
from src.pipeline.paths import JobPaths
from src.pipeline.registry import is_pdf_magic
from src.pipeline.state import JobState

MAX_PAGES = 10


async def run_ingest(job: JobState, upload_bytes: bytes, filename: str) -> None:
    paths = JobPaths(job.job_id)
    paths.ensure()
    if not is_pdf_magic(upload_bytes):
        job.status = "failed"
        await broadcast(
            job,
            "stage.error",
            {
                "stage": "ingest",
                "error": "invalid_pdf",
                "diagnostic": "Missing PDF magic bytes",
            },
        )
        return
    paths.title_pdf.write_bytes(upload_bytes)

    reader = PdfReader(str(paths.title_pdf))
    page_count = len(reader.pages)
    if page_count > MAX_PAGES:
        job.status = "failed"
        await broadcast(
            job,
            "stage.error",
            {
                "stage": "ingest",
                "error": f"PDF has {page_count} pages; maximum is {MAX_PAGES}",
                "diagnostic": "validation",
            },
        )
        return

    # Rasterize page 1 for review thumbnail (MuPDF may stderr on broken tag trees; non-fatal).
    with mupdf_no_stderr_errors():
        doc = fitz.open(str(paths.title_pdf))
        try:
            page = doc.load_page(0)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            pix.save(str(paths.title_png))
        finally:
            doc.close()

    job.title_image_path = paths.title_png
    size_bytes = paths.title_pdf.stat().st_size
    h = hashlib.sha256(upload_bytes).hexdigest()[:12]

    await broadcast(
        job,
        "ingest.complete",
        {
            "job_id": job.job_id,
            "filename": filename,
            "size_bytes": size_bytes,
            "page_count": page_count,
            "sha256_preview": h,
        },
    )
    await asyncio.sleep(0.05)
