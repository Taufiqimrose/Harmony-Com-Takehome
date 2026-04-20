"""Fill three HCD forms and bundle a zip."""

from __future__ import annotations

import asyncio
import logging

from src.pipeline.events import broadcast
from src.pipeline.fill_acro import detect_acro_fields, fill_acroform
from src.pipeline.fill_io import (
    pdf_page_count,
    rasterize_pdf,
    render_thumb,
    write_stub_pdf,
    write_zip,
)
from src.pipeline.form_maps import ACRO_FIELD_MAPS
from src.pipeline.forms_assets import ensure_form_assets
from src.pipeline.merge import build_merged_payload
from src.pipeline.paths import JobPaths
from src.pipeline.state import JobState
from src.schema.forms import HCD_FORM_SPECS

logger = logging.getLogger(__name__)


async def run_fill(job: JobState) -> None:
    if not job.verified or not job.buyer:
        logger.error("run_fill: missing verified or buyer for job %s", job.job_id)
        job.status = "failed"
        await broadcast(
            job,
            "fill.failed",
            {"error": "internal_state", "form_id": None},
        )
        return

    paths = JobPaths(job.job_id)
    paths.ensure()
    job.status = "filling"
    await broadcast(job, "fill.started", {"job_id": job.job_id})

    try:
        merged = build_merged_payload(job)
    except ValueError as exc:
        logger.exception("merge payload failed")
        job.status = "failed"
        await broadcast(job, "fill.failed", {"error": str(exc), "form_id": None})
        return

    try:
        blank_forms = await ensure_form_assets()
    except (OSError, RuntimeError):
        logger.exception("form assets unavailable")
        blank_forms = {}

    files_meta: list[dict[str, str | int]] = []
    for form_id, filename in HCD_FORM_SPECS:
        out = paths.filled_dir / filename
        blank_path = blank_forms.get(form_id)

        fill_mode = "stub"
        fields_written = 0
        if blank_path and blank_path.is_file():
            available_fields = await asyncio.to_thread(detect_acro_fields, blank_path)
            acro_map = ACRO_FIELD_MAPS.get(form_id, {})
            if available_fields and acro_map:
                interactive = paths.filled_dir / f".{filename}.interactive.pdf"
                fields_written = await asyncio.to_thread(
                    fill_acroform,
                    blank_path,
                    interactive,
                    acro_map,
                    merged,
                    available_fields,
                )
                # Rasterize the filled PDF so checkbox/radio marks render reliably
                # in all viewers (macOS Preview/Quartz skips certain regions on the
                # HCD templates; Chrome/PDFium handles them fine). The raster output
                # is the final customer-facing PDF.
                await asyncio.to_thread(rasterize_pdf, interactive, out)
                try:
                    interactive.unlink()
                except OSError:
                    logger.warning("failed to unlink %s", interactive)
                fill_mode = "acroform"
            else:
                title = f"HCD Transfer — {form_id}"
                lines = [f"{k}: {v}" for k, v in list(merged.items())[:40]]
                fields_written = await asyncio.to_thread(write_stub_pdf, out, title, lines)
                fill_mode = "stub"
        else:
            title = f"HCD Transfer — {form_id}"
            lines = [f"{k}: {v}" for k, v in list(merged.items())[:40]]
            fields_written = await asyncio.to_thread(write_stub_pdf, out, title, lines)

        pages = await asyncio.to_thread(pdf_page_count, out)
        job.filled_paths[form_id] = out
        thumb = paths.thumbs_dir / f"{form_id}.png"
        await asyncio.to_thread(render_thumb, out, thumb)
        job.thumb_paths[form_id] = thumb
        await broadcast(
            job,
            "fill.form_complete",
            {
                "form_id": form_id,
                "thumbnail_url": f"/jobs/{job.job_id}/thumbs/{form_id}.png",
                "fill_mode": fill_mode,
                "fields_written": fields_written,
            },
        )
        files_meta.append(
            {
                "form_id": form_id,
                "filename": filename,
                "pages": pages,
                "fill_mode": fill_mode,
                "fields_written": fields_written,
            }
        )

    zip_path = paths.zip_path
    await asyncio.to_thread(write_zip, zip_path, paths.filled_dir, HCD_FORM_SPECS)
    job.zip_path = zip_path
    job.status = "complete"

    await broadcast(
        job,
        "packet.ready",
        {
            "zip_url": f"/jobs/{job.job_id}/packet",
            "size_bytes": zip_path.stat().st_size,
            "files": files_meta,
        },
    )
