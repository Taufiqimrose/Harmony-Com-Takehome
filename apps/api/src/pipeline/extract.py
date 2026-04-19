"""LandingAI ADE extraction (DPT-2) only."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

import httpx

from src.pipeline.events import broadcast
from src.pipeline.paths import JobPaths
from src.pipeline.state import JobState
from src.schema.extract_schema import ExtractSchema
from src.schema.extracted import ExtractedField
from src.settings import settings

logger = logging.getLogger(__name__)

EXTRACT_FIELD_ORDER = (
    "decal",
    "serial",
    "make",
    "registered_owner",
    "site_address",
    "manufacturer_name",
    "trade_name",
    "date_of_manufacture",
    "model_name_or_number",
    "date_first_sold_new",
    "hud_label_or_hcd_insignia",
    "length_inches",
    "width_inches",
)


async def run_extract(job: JobState) -> bool:
    paths = JobPaths(job.job_id)
    job.status = "extracting"
    await broadcast(job, "extract.started", {"job_id": job.job_id})
    await broadcast(
        job,
        "extract.provider",
        {"provider": "landingai", "parse_model": settings.landingai_parse_model},
    )
    try:
        ade_fields = await _landingai_extract(paths.title_pdf)
    except httpx.HTTPError:
        logger.exception("LandingAI HTTP failure")
        job.status = "failed"
        await broadcast(
            job,
            "extract.failed",
            {"error": "LandingAI request failed", "retry_hint": "Check network and API key"},
        )
        return False
    except (RuntimeError, ValueError, TypeError, KeyError) as exc:
        logger.exception("LandingAI extraction failed")
        job.status = "failed"
        await broadcast(
            job,
            "extract.failed",
            {
                "error": str(exc),
                "retry_hint": "Check LandingAI config, schema, and document quality",
            },
        )
        return False

    job.extracted = ade_fields

    t0 = time.perf_counter()

    for name in EXTRACT_FIELD_ORDER:
        field = ade_fields[name]
        await broadcast(
            job,
            "extract.field",
            {
                "name": name,
                "value": field.value,
                "bbox": list(field.bbox),
                "ade_confidence": field.ade_confidence,
            },
        )
        await asyncio.sleep(0.1)

    elapsed = time.perf_counter() - t0
    await broadcast(
        job,
        "extract.complete",
        {"count": len(EXTRACT_FIELD_ORDER), "seconds": round(elapsed, 2)},
    )
    return True


async def _landingai_extract(pdf_path: Path) -> dict[str, ExtractedField]:
    if not settings.landingai_api_key:
        raise RuntimeError("LandingAI API key is missing")

    headers = {"Authorization": f"Bearer {settings.landingai_api_key}"}
    base_url = settings.landingai_base_url.rstrip("/")

    timeout = httpx.Timeout(90.0, connect=20.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        parse_url = f"{base_url}/v1/ade/parse"
        parse_data = {"model": settings.landingai_parse_model}
        pdf_bytes = await asyncio.to_thread(pdf_path.read_bytes)
        parse_files = {"document": (pdf_path.name, pdf_bytes, "application/pdf")}
        parse_resp = await client.post(
            parse_url,
            headers=headers,
            data=parse_data,
            files=parse_files,
        )
        parse_resp.raise_for_status()
        parse_json: dict[str, Any] = parse_resp.json()
        markdown = parse_json.get("markdown")
        if not isinstance(markdown, str) or not markdown.strip():
            raise RuntimeError("LandingAI parse returned empty markdown")

        extract_url = f"{base_url}/v1/ade/extract"
        schema_json = json.dumps(_landingai_extract_schema())
        extract_data = {
            "schema": schema_json,
            "markdown": markdown,
            "model": settings.landingai_extract_model,
            "strict": "true",
        }
        extract_resp = await client.post(extract_url, headers=headers, data=extract_data)
        if extract_resp.status_code >= 400:
            detail = extract_resp.text[:2000]
            raise RuntimeError(
                f"LandingAI extract failed ({extract_resp.status_code}): {detail}"
            )
        extract_json: dict[str, Any] = extract_resp.json()
        extraction = extract_json.get("extraction")
        if not isinstance(extraction, dict):
            raise RuntimeError("LandingAI extract returned no extraction object")
        meta_raw = extract_json.get("extraction_metadata")
        extraction_metadata = meta_raw if isinstance(meta_raw, dict) else {}

        return _build_fields_from_extraction(extraction, extraction_metadata)


def _landingai_extract_schema() -> dict[str, Any]:
    properties: dict[str, dict[str, str]] = {}
    required: list[str] = []
    for name, field in ExtractSchema.model_fields.items():
        properties[name] = {
            "type": "string",
            "description": field.description or name.replace("_", " "),
        }
        required.append(name)
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _cell_value_and_confidence(raw: Any) -> tuple[str, float | None]:
    """Normalize LandingAI cell output; None confidence when the API omits a score."""
    if raw is None:
        return "", None
    if isinstance(raw, dict):
        val = raw.get("value", raw.get("text", raw.get("content", "")))
        score = raw.get("confidence", raw.get("score"))
        text = str(val).strip() if val is not None else ""
        if not text:
            return "", None
        if isinstance(score, (int, float)):
            return text, max(0.0, min(1.0, float(score)))
        return text, None
    text = str(raw).strip()
    if not text:
        return "", None
    return text, None


def _build_fields_from_extraction(
    extraction: dict[str, Any],
    extraction_metadata: dict[str, Any],
) -> dict[str, ExtractedField]:
    out: dict[str, ExtractedField] = {}
    for key in EXTRACT_FIELD_ORDER:
        meta_cell = extraction_metadata.get(key)
        raw: Any = meta_cell if isinstance(meta_cell, dict) else extraction.get(key, "")
        value, conf = _cell_value_and_confidence(raw)
        out[key] = ExtractedField(value=value, bbox=(0.0, 0.0, 0.0, 0.0), ade_confidence=conf)
    return out
