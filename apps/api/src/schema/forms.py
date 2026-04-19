"""Shared HCD form identifiers (keep in sync with ``hcd-forms.ts``)."""

from __future__ import annotations

from typing import Literal

HcdFormId = Literal["476-6g", "476-6", "480-5"]

HCD_FORM_SPECS: tuple[tuple[HcdFormId, str], ...] = (
    ("476-6g", "hcd-rt-476-6g.pdf"),
    ("476-6", "hcd-rt-476-6.pdf"),
    ("480-5", "hcd-rt-480-5.pdf"),
)

# Review UI tab order (differs from zip/fill order in HCD_FORM_SPECS).
# Keep in sync with `HCD_FORM_REVIEW_ORDER` in `hcd-forms.ts`.
HCD_FORM_REVIEW_ORDER: tuple[HcdFormId, ...] = ("476-6g", "480-5", "476-6")
