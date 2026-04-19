"""Job upload, SSE, confirm, downloads."""

import asyncio
import shutil
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse

from src.pipeline.paths import JobPaths
from src.pipeline.registry import (
    check_upload_rate_limit,
    is_pdf_magic,
    register_new_job,
)
from src.pipeline.run import run_after_upload, run_confirm
from src.pipeline.state import JOBS, JobState
from src.schema.buyer import ConfirmBody

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _public_base(request: Request) -> str:
    return str(request.base_url).rstrip("/")


@router.post("")
async def create_job(request: Request, file: UploadFile = File(...)) -> dict[str, str]:
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Expected application/pdf")
    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")
    if not is_pdf_magic(raw):
        raise HTTPException(400, "File is not a valid PDF")
    client_host = request.client.host if request.client else "unknown"
    try:
        check_upload_rate_limit(client_host)
    except RuntimeError as exc:
        raise HTTPException(429, str(exc)) from exc

    job_id = str(uuid.uuid4())
    paths = JobPaths(job_id)
    paths.ensure()

    job = JobState(
        job_id=job_id,
        status="ingesting",
        title_path=paths.title_pdf,
        title_image_path=None,
        extracted=None,
        verified=None,
        extracted_overrides=None,
        buyer=None,
        filled_paths={},
        thumb_paths={},
        zip_path=None,
        created_at=datetime.now(tz=UTC),
    )
    try:
        register_new_job(job)
    except RuntimeError as exc:
        shutil.rmtree(paths.root, ignore_errors=True)
        raise HTTPException(503, str(exc)) from exc

    base = _public_base(request)
    asyncio.create_task(run_after_upload(job_id, raw, file.filename or "title.pdf"))

    return {
        "job_id": job_id,
        "sse_url": f"{base}/jobs/{job_id}/events",
    }


TERMINAL_SSE_EVENTS = frozenset({"packet.ready", "extract.failed", "fill.failed", "stage.error"})


def _should_close_stream(msg: str) -> bool:
    first = msg.split("\n", 1)[0]
    if not first.startswith("event: "):
        return False
    return first.removeprefix("event: ") in TERMINAL_SSE_EVENTS


async def _sse_stream(job_id: str) -> AsyncIterator[bytes]:
    job = JOBS.get(job_id)
    if not job:
        yield b'event: stage.error\ndata: {"error":"not_found"}\n\n'
        return

    # Read from append-only log. The pipeline often emits before EventSource connects;
    # we poll with an Event so we never miss chunks and never duplicate them.
    idx = 0
    while True:
        while idx < len(job.event_chunks):
            msg = job.event_chunks[idx]
            idx += 1
            yield msg.encode("utf-8")
            if _should_close_stream(msg):
                return

        try:
            await asyncio.wait_for(job.sse_wake.wait(), timeout=15.0)
        except TimeoutError:
            yield b": ping\n\n"
        else:
            # Wake was consumed; allow coalesced appends to drain in the inner loop.
            job.sse_wake.clear()


@router.get("/{job_id}/events")
async def job_events(job_id: str) -> StreamingResponse:
    if job_id not in JOBS:
        raise HTTPException(404, "job not found")
    return StreamingResponse(
        _sse_stream(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{job_id}/confirm")
async def confirm(job_id: str, body: ConfirmBody) -> Response:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    if job.status != "awaiting_review":
        raise HTTPException(409, "job not awaiting review")
    asyncio.create_task(run_confirm(job_id, body.buyer, body.extracted_overrides))
    return Response(status_code=202)


@router.get("/{job_id}/packet")
async def download_packet(job_id: str) -> FileResponse:
    job = JOBS.get(job_id)
    if not job or not job.zip_path or not job.zip_path.is_file():
        raise HTTPException(404, "packet not ready")
    return FileResponse(
        path=job.zip_path,
        filename="packet.zip",
        media_type="application/zip",
    )


@router.get("/{job_id}/title.png")
async def title_png(job_id: str) -> FileResponse:
    job = JOBS.get(job_id)
    if not job or not job.title_image_path or not job.title_image_path.is_file():
        raise HTTPException(404, "not found")
    return FileResponse(job.title_image_path, media_type="image/png")


@router.get("/{job_id}/thumbs/{form_id}.png")
async def thumb(job_id: str, form_id: str) -> FileResponse:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "not found")
    p = job.thumb_paths.get(form_id)
    if not p or not p.is_file():
        raise HTTPException(404, "not found")
    return FileResponse(p, media_type="image/png")
