"""AcroForm detection, value fill, and radio/button widget fixes (pypdf)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject


def detect_acro_fields(pdf_path: Path) -> dict[str, dict[str, Any]]:
    return PdfReader(str(pdf_path)).get_fields() or {}


def fill_acroform(
    blank: Path,
    out: Path,
    mapping: dict[str, str],
    data: dict[str, str],
    available_fields: dict[str, dict[str, Any]],
) -> int:
    reader = PdfReader(str(blank))
    writer = PdfWriter(clone_from=reader)

    values: dict[str, str] = {}
    for hcd_field, payload_key in mapping.items():
        if hcd_field not in available_fields:
            continue
        desired = data.get(payload_key, "")
        field_def = available_fields.get(hcd_field, {})
        if str(field_def.get("/FT", "")) == "/Btn":
            desired = coerce_button_value(field_def, desired)
        values[hcd_field] = desired

    for page in writer.pages:
        writer.update_page_form_field_values(
            page,
            values,
            auto_regenerate=False,
        )
    apply_button_widgets(writer, values)
    writer.set_need_appearances_writer(True)

    with out.open("wb") as fh:
        writer.write(fh)
    return len(values)


def coerce_button_value(field_def: dict[str, Any], desired: str) -> str:
    """
    Convert Yes/No-like values to concrete PDF export states (e.g. /YES, /NO)
    so pypdf updates button widgets correctly.
    """
    candidate_keys = (
        collect_group_keys(field_def) if field_def.get("/Kids") else widget_ap_keys(field_def)
    )
    chosen = choose_button_state(candidate_keys, desired)
    if chosen is None:
        return desired
    return chosen


def apply_button_widgets(writer: PdfWriter, values: dict[str, str]) -> None:
    for page in writer.pages:
        annots = page.get("/Annots") or []
        for annot_ref in annots:
            annot = annot_ref.get_object()
            parent_ref = annot.get("/Parent")
            parent = parent_ref.get_object() if parent_ref else None
            field_holder = parent if parent is not None else annot
            field_name_raw = field_holder.get("/T")
            field_name = str(field_name_raw) if field_name_raw is not None else ""
            if not field_name or field_name not in values:
                continue

            desired = values[field_name]
            if parent is not None and parent.get("/Kids"):
                candidate_keys = collect_group_keys(parent)
                chosen = choose_button_state(candidate_keys, desired)
                if chosen is None:
                    continue
                set_group_state(parent, chosen)
                parent[NameObject("/V")] = NameObject(chosen)
                continue

            if str(annot.get("/FT", "")) != "/Btn":
                continue
            candidate_keys = widget_ap_keys(annot)
            chosen = choose_button_state(candidate_keys, desired)
            if chosen is None:
                continue
            annot[NameObject("/AS")] = NameObject(chosen)
            if parent is not None:
                parent[NameObject("/V")] = NameObject(chosen)


def collect_group_keys(parent: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for kid_ref in parent.get("/Kids", []):
        kid = kid_ref.get_object()
        keys.extend(widget_ap_keys(kid))
    return list(dict.fromkeys(keys))


def set_group_state(parent: dict[str, Any], chosen: str) -> None:
    for kid_ref in parent.get("/Kids", []):
        kid = kid_ref.get_object()
        keys = widget_ap_keys(kid)
        if chosen in keys:
            kid[NameObject("/AS")] = NameObject(chosen)
        elif "/Off" in keys:
            kid[NameObject("/AS")] = NameObject("/Off")


def widget_ap_keys(widget: dict[str, Any]) -> list[str]:
    ap = widget.get("/AP")
    if ap is None:
        return []
    normal = ap.get("/N")
    if normal is None:
        return []
    return [str(k) for k in normal]


def choose_button_state(candidate_keys: list[str], desired: str) -> str | None:
    if not candidate_keys:
        return None
    norm = desired.strip().lower()
    clean_keys = [k.lstrip("/").strip().lower() for k in candidate_keys]

    yes_like = {"yes", "y", "true", "1", "on", "checked"}
    no_like = {"no", "n", "false", "0", "off", "unchecked"}

    if norm in yes_like:
        for idx, ck in enumerate(clean_keys):
            if ck in yes_like:
                return candidate_keys[idx]
        for idx, ck in enumerate(clean_keys):
            if ck != "off":
                return candidate_keys[idx]

    if norm in no_like:
        explicit_no = {"no", "n", "false", "0", "unchecked"}
        for idx, ck in enumerate(clean_keys):
            if ck in explicit_no:
                return candidate_keys[idx]
        for idx, ck in enumerate(clean_keys):
            if ck == "off":
                return candidate_keys[idx]

    for idx, ck in enumerate(clean_keys):
        if ck == norm:
            return candidate_keys[idx]

    if norm == "":
        for idx, ck in enumerate(clean_keys):
            if ck == "off":
                return candidate_keys[idx]
    return None
