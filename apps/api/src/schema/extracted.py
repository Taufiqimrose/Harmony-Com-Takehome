"""Extracted field shapes."""

from dataclasses import dataclass


@dataclass(slots=True)
class ExtractedField:
    value: str
    bbox: tuple[float, float, float, float]
    # Provider-supplied score only; None when ADE omits confidence (common for /v1/ade/extract).
    ade_confidence: float | None = None
