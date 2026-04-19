"""Bounded in-memory job registry with TTL eviction and disk cleanup."""

from __future__ import annotations

import logging
import shutil
import time
from collections import defaultdict
from datetime import UTC, datetime
from threading import Lock

from src.pipeline.paths import JobPaths
from src.pipeline.state import JOBS, JobState
from src.settings import settings

logger = logging.getLogger(__name__)

TERMINAL_STATUSES = frozenset({"complete", "failed"})
_UPLOAD_BUCKETS: dict[str, list[float]] = defaultdict(list)
_UPLOAD_LOCK = Lock()


def _job_root(job_id: str) -> JobPaths:
    return JobPaths(job_id)


def delete_job_directory(job_id: str) -> None:
    root = _job_root(job_id).root
    if root.is_dir():
        shutil.rmtree(root, ignore_errors=True)


def prune_expired_terminal_jobs() -> None:
    """Drop finished jobs older than ``settings.job_ttl_seconds``."""
    if settings.job_ttl_seconds <= 0:
        return
    now = datetime.now(tz=UTC)
    ttl = float(settings.job_ttl_seconds)
    doomed: list[str] = []
    for jid, job in list(JOBS.items()):
        if job.status not in TERMINAL_STATUSES:
            continue
        if (now - job.created_at).total_seconds() > ttl:
            doomed.append(jid)
    for jid in doomed:
        JOBS.pop(jid, None)
        delete_job_directory(jid)
        logger.info("pruned expired job %s", jid)


def evict_oldest_terminal_jobs() -> None:
    """Remove oldest terminal jobs until under the configured cap."""
    max_n = settings.jobs_max_count
    if max_n <= 0:
        return
    while len(JOBS) >= max_n:
        candidates = [
            (job.created_at, job.job_id)
            for job in JOBS.values()
            if job.status in TERMINAL_STATUSES
        ]
        if not candidates:
            break
        candidates.sort(key=lambda x: x[0])
        _, jid = candidates[0]
        JOBS.pop(jid, None)
        delete_job_directory(jid)
        logger.warning("evicted terminal job %s (registry cap %s)", jid, max_n)


def register_new_job(job: JobState) -> None:
    """Make room if needed, then insert *job* into ``JOBS``."""
    prune_expired_terminal_jobs()
    evict_oldest_terminal_jobs()
    if len(JOBS) >= settings.jobs_max_count:
        msg = "job registry is full; try again later"
        raise RuntimeError(msg)
    JOBS[job.job_id] = job


def check_upload_rate_limit(client_host: str) -> None:
    """Sliding-window limit on ``POST /jobs`` per client IP."""
    window = 60.0
    max_req = settings.upload_rate_limit_per_minute
    if max_req <= 0:
        return
    now = time.monotonic()
    with _UPLOAD_LOCK:
        bucket = _UPLOAD_BUCKETS[client_host]
        bucket[:] = [t for t in bucket if now - t < window]
        if len(bucket) >= max_req:
            msg = "too many uploads from this address; wait and retry"
            raise RuntimeError(msg)
        bucket.append(now)


def is_pdf_magic(data: bytes) -> bool:
    """True if *data* looks like a PDF (``%%PDF-`` in the header)."""
    if len(data) < 5:
        return False
    head = data[:2048]
    return head.startswith(b"%PDF-") or b"%PDF-" in head
