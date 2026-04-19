"""Verified field shapes."""

from dataclasses import dataclass


@dataclass(slots=True)
class VerifiedField:
    value: str
    bbox: tuple[float, float, float, float]
    ade_confidence: float | None
    rule_confidence: float
    final_confidence: float
    flags: list[str]
