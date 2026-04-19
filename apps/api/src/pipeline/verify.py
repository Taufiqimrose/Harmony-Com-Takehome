"""Verify: combine LandingAI ADE confidence with deterministic rule scores."""

import asyncio
import logging
import re

from src.pipeline.events import broadcast
from src.pipeline.state import JobState
from src.schema.verified import VerifiedField

logger = logging.getLogger(__name__)


def _rule_score(name: str, value: str) -> tuple[float, list[str]]:
    flags: list[str] = []
    v = value.strip()
    if not v:
        return 0.0, ["empty"]

    if name == "decal":
        if re.search(r"[A-Z0-9]{4,}", v, re.I):
            return 0.95, flags
        flags.append("decal_format_mismatch")
        return 0.5, flags

    if name == "serial":
        if len(v) >= 8:
            return 0.9, flags
        flags.append("serial_short")
        return 0.55, flags

    if name in {"make", "registered_owner", "site_address"}:
        if len(v) >= 2:
            return 0.85, flags
        return 0.5, flags

    return 0.8, flags


def _composite_no_llm(ade: float, rule: float) -> float:
    return 0.5 * ade + 0.5 * rule


def _composite_no_llm_optional_ade(ade: float | None, rule: float) -> float:
    if ade is not None:
        return _composite_no_llm(ade, rule)
    return rule


def _band(final: float) -> str:
    if final >= 0.85:
        return "HIGH"
    if final >= 0.6:
        return "MEDIUM"
    return "LOW"


async def run_verify(job: JobState) -> None:
    if not job.extracted:
        logger.error("run_verify: missing extraction for %s", job.job_id)
        job.status = "failed"
        await broadcast(
            job,
            "verify.failed",
            {"error": "verify_preconditions_missing"},
        )
        return

    job.status = "verifying"
    fields = job.extracted

    await broadcast(job, "verify.started", {"job_id": job.job_id})

    rule_results = await asyncio.to_thread(
        lambda: {n: _rule_score(n, fields[n].value) for n in fields}
    )

    verified = {}
    for name, ef in fields.items():
        rule_conf, flags = rule_results[name]
        flags = list(flags)
        final = _composite_no_llm_optional_ade(ef.ade_confidence, rule_conf)

        verified[name] = VerifiedField(
            value=ef.value,
            bbox=ef.bbox,
            ade_confidence=ef.ade_confidence,
            rule_confidence=rule_conf,
            final_confidence=final,
            flags=flags,
        )

    job.verified = verified

    for name, vf in verified.items():
        await broadcast(
            job,
            "verify.field_scored",
            {
                "name": name,
                "final_confidence": vf.final_confidence,
                "components": {
                    "ade": vf.ade_confidence,
                    "rule": vf.rule_confidence,
                },
                "flags": vf.flags,
                "band": _band(vf.final_confidence),
            },
        )
        await asyncio.sleep(0.05)

    await broadcast(job, "verify.complete", {})
    job.status = "awaiting_review"
    await broadcast(job, "awaiting_review", {"job_id": job.job_id})
