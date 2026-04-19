"""In-memory job registry."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

from src.schema.buyer import BuyerInfo
from src.schema.extracted import ExtractedField
from src.schema.verified import VerifiedField

JobStatus = Literal[
    "ingesting",
    "extracting",
    "verifying",
    "awaiting_review",
    "filling",
    "complete",
    "failed",
]


@dataclass
class JobState:
    job_id: str
    status: JobStatus
    title_path: Path
    title_image_path: Path | None
    extracted: dict[str, ExtractedField] | None
    verified: dict[str, VerifiedField] | None
    extracted_overrides: dict[str, str] | None
    buyer: BuyerInfo | None
    filled_paths: dict[str, Path]
    thumb_paths: dict[str, Path]
    zip_path: Path | None
    created_at: datetime
    # All SSE payloads ever emitted; each /events connection reads with its own cursor.
    event_chunks: list[str] = field(default_factory=list)
    sse_wake: asyncio.Event = field(default_factory=asyncio.Event)
    last_error: str | None = None


JOBS: dict[str, JobState] = {}
