"""End-to-end pipeline orchestration."""

import asyncio
import logging

from src.pipeline import extract, ingest, verify
from src.pipeline.events import broadcast
from src.pipeline.fill import run_fill
from src.pipeline.state import JOBS
from src.schema.buyer import BuyerInfo

logger = logging.getLogger(__name__)


async def run_after_upload(job_id: str, upload_bytes: bytes, filename: str) -> None:
    job = JOBS.get(job_id)
    if not job:
        return
    try:
        await ingest.run_ingest(job, upload_bytes, filename)
        if job.status == "failed":
            return

        ok = await extract.run_extract(job)
        if not ok:
            return
        if not job.extracted:
            job.status = "failed"
            await broadcast(
                job,
                "extract.failed",
                {"error": "Extraction produced no fields", "retry_hint": "Try a clearer scan"},
            )
            return

        await verify.run_verify(job)
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("pipeline failed")
        job.status = "failed"
        await broadcast(
            job,
            "stage.error",
            {
                "stage": "pipeline",
                "error": "unexpected",
                "diagnostic": "check server logs",
            },
        )


async def run_confirm(job_id: str, buyer: BuyerInfo, overrides: dict[str, str]) -> None:
    job = JOBS.get(job_id)
    if not job:
        return
    if job.status != "awaiting_review":
        logger.warning("confirm ignored for job %s in status %s", job_id, job.status)
        await broadcast(
            job,
            "stage.error",
            {
                "stage": "confirm",
                "error": "invalid_state",
                "diagnostic": f"job is {job.status}, expected awaiting_review",
            },
        )
        return
    try:
        job.buyer = buyer
        job.extracted_overrides = overrides
        await run_fill(job)
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("fill failed")
        job.status = "failed"
        await broadcast(
            job,
            "fill.failed",
            {"error": "fill pipeline error", "form_id": None},
        )
