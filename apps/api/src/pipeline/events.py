"""SSE fan-out helpers."""

import json
from typing import Any

from src.pipeline.state import JobState


def format_sse(event_name: str, payload: dict[str, Any]) -> str:
    body = json.dumps(payload)
    return f"event: {event_name}\ndata: {body}\n\n"


async def broadcast(job: JobState, event_name: str, payload: dict[str, Any]) -> None:
    chunk = format_sse(event_name, payload)
    job.event_chunks.append(chunk)
    job.sse_wake.set()


def sse_ping() -> str:
    return ": ping\n\n"
