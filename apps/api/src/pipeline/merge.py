"""Merge verified extraction + buyer review into a flat PDF payload."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from src.pipeline.state import JobState
from src.schema.buyer import BuyerInfo
from src.schema.verified import VerifiedField
from src.schema.yes_no import HCD_NO, HCD_YES


def build_merged_payload(job: JobState) -> dict[str, str]:
    if not job.verified or not job.buyer:
        msg = "verified fields and buyer are required to build the payload"
        raise ValueError(msg)
    out: dict[str, str] = {}
    vf: dict[str, VerifiedField] = job.verified
    ov = job.extracted_overrides or {}
    for k, v in vf.items():
        out[k] = ov.get(k, v.value)
    b: BuyerInfo = job.buyer
    owner_fallback = split_registered_owner(out.get("registered_owner", ""))
    situs = split_site_address(out.get("site_address", ""))
    total_price = sum_currency_strings(
        b.f4805_4a_base_unit_price,
        b.f4805_4b_unattached_accessories_price,
    )
    out.update(
        {
            "manual.g6_smoke_detector": HCD_YES if b.g6_smoke_detector_confirmed else HCD_NO,
            "manual.g6_water_heater": HCD_YES if b.g6_water_heater_confirmed else HCD_NO,
            "manual.g6_own_home": HCD_YES if b.g6_own_home_confirmed else HCD_NO,
            "manual.g6_own_land": b.g6_own_land_answer,
            "manual.f4805_ro1_last": b.f4805_ro1_last or owner_fallback["last"],
            "manual.f4805_ro1_first": b.f4805_ro1_first or owner_fallback["first"],
            "manual.f4805_ro1_middle": b.f4805_ro1_middle or owner_fallback["middle"],
            "manual.f4805_ro2_last": b.f4805_ro2_last,
            "manual.f4805_ro2_first": b.f4805_ro2_first,
            "manual.f4805_ro2_middle": b.f4805_ro2_middle,
            "manual.f4805_ro3_last": b.f4805_ro3_last,
            "manual.f4805_ro3_first": b.f4805_ro3_first,
            "manual.f4805_ro3_middle": b.f4805_ro3_middle,
            "manual.f4805_current_mailing_street": b.f4805_current_mailing_street,
            "manual.f4805_current_mailing_city": b.f4805_current_mailing_city,
            "manual.f4805_current_mailing_county": b.f4805_current_mailing_county,
            "manual.f4805_current_mailing_state": b.f4805_current_mailing_state,
            "manual.f4805_current_mailing_zip": b.f4805_current_mailing_zip,
            "manual.f4805_section2_purchased_from": b.f4805_section2_purchased_from,
            "manual.f4805_s4_date_of_sale": b.f4805_s4_date_of_sale,
            "manual.f4805_s2_is_new_unit": b.f4805_s2_is_new_unit,
            "manual.f4805_s2_first_sold_new_date": b.f4805_s2_first_sold_new_date,
            "manual.f4805_s2_registered_in_ca_or_other_state": b.f4805_s2_registered_in_ca_or_other_state,
            "manual.f4805_s2_last_registered_state_and_date": b.f4805_s2_last_registered_state_and_date,
            "manual.f4805_s2_entered_california_date": b.f4805_s2_entered_california_date,
            "manual.f4805_s2_last_licensed_resident_state": b.f4805_s2_last_licensed_resident_state,
            "manual.f4805_s2_resident_of_california": b.f4805_s2_resident_of_california,
            "manual.f4805_s2_became_resident_when": b.f4805_s2_became_resident_when,
            "manual.f4805_s3_outstanding_titles": b.f4805_s3_outstanding_titles,
            "manual.f4805_s3_security_lien": b.f4805_s3_security_lien,
            "manual.f4805_4a_base_unit_price": b.f4805_4a_base_unit_price,
            "manual.f4805_4b_unattached_accessories_price": b.f4805_4b_unattached_accessories_price,
            "manual.f4805_4_total_price": total_price,
            "manual.f4805_4d_sale_price": b.f4805_4d_sale_price,
            "manual.f4805_executed_at": "Stockton, CA",
            "manual.f4805_s5_active_duty": HCD_NO,
            "manual.f4805_s5_last_licensed_active_duty": HCD_NO,
            "manual.f4805_s5_military_reservation": HCD_NO,
            "manual.f4805_s5_federally_recognized_tribe": HCD_NO,
            "manual.f4805_s5_disabled_veteran": HCD_NO,
            "manual.f4805_s5_exempt_registration": HCD_NO,
            "manual.f4766_statement": b.f4766_statement,
            "situs.street": situs["street"],
            "situs.city": situs["city"],
            "situs.county": situs["county"],
            "situs.state": situs["state"],
            "situs.zip": situs["zip"],
        }
    )
    out["trade_name"] = out.get("trade_name", out.get("make", ""))
    out["length_inches"] = normalize_inches(out.get("length_inches", ""))
    out["width_inches"] = normalize_inches(out.get("width_inches", ""))
    return out


def sum_currency_strings(*values: str) -> str:
    total = Decimal("0")
    saw_value = False
    for value in values:
        cleaned = value.replace(",", "").replace("$", "").strip()
        if not cleaned:
            continue
        try:
            total += Decimal(cleaned)
            saw_value = True
        except InvalidOperation:
            continue
    if not saw_value:
        return ""
    normalized = total.quantize(Decimal("0.01"))
    return f"{normalized:.2f}"


def split_site_address(site_address: str) -> dict[str, str]:
    """
    Best-effort split for strings like:
    - '520 Pine Ave #55, Santa Barbara, CA 93117'
    - '520 Pine Ave #55, Santa Barbara, Santa Barbara County, CA 93117'
    """
    out = {"street": "", "city": "", "county": "", "state": "", "zip": ""}
    text = re.sub(r"\s+", " ", site_address).strip()
    if not text:
        return out

    m = re.search(r"\b([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b\s*$", text, re.IGNORECASE)
    if m:
        out["state"] = m.group(1).upper()
        out["zip"] = m.group(2)
        text = text[: m.start()].rstrip(", ").strip()

    parts = [p.strip() for p in text.split(",") if p.strip()]
    if len(parts) >= 3:
        out["street"] = parts[0]
        out["city"] = parts[1]
        out["county"] = parts[2]
    elif len(parts) == 2:
        out["street"] = parts[0]
        out["city"] = parts[1]
    elif len(parts) == 1:
        tokens = parts[0].split()
        if len(tokens) >= 2 and tokens[-1].isalpha() and tokens[-2].isalpha():
            out["city"] = f"{tokens[-2]} {tokens[-1]}"
            out["street"] = " ".join(tokens[:-2]).strip()
        elif len(tokens) >= 1 and tokens[-1].isalpha():
            out["city"] = tokens[-1]
            out["street"] = " ".join(tokens[:-1]).strip()
        else:
            out["street"] = parts[0]

    return out


def split_registered_owner(value: str) -> dict[str, str]:
    text = re.sub(r"\s+", " ", value).strip()
    result = {"first": "", "middle": "", "last": ""}
    if not text:
        return result

    if re.search(r"\b(llc|inc|corp|co|company|sales|hub|homes?|housing)\b", text, re.IGNORECASE):
        result["last"] = text
        return result

    if "," in text:
        last, rest = [part.strip() for part in text.split(",", 1)]
        tokens = [token for token in rest.split(" ") if token]
        result["last"] = last
        result["first"] = tokens[0] if tokens else ""
        result["middle"] = " ".join(tokens[1:]) if len(tokens) > 1 else ""
        return result

    tokens = [token for token in text.split(" ") if token]
    if len(tokens) == 1:
        result["last"] = tokens[0]
        return result

    result["first"] = tokens[0]
    result["last"] = tokens[-1]
    result["middle"] = " ".join(tokens[1:-1])
    return result


def normalize_inches(raw: str) -> str:
    value = _normalize_quote_symbols(raw.strip().lower())
    if not value:
        return ""

    feet_only = re.fullmatch(r"(\d{1,3})\s*'", value)
    if feet_only:
        return str(int(feet_only.group(1)) * 12)

    feet_inches = re.fullmatch(r"(\d{1,3})\s*'\s*(\d{1,2})\s*(?:\"|in|inch|inches)?", value)
    if feet_inches:
        return str(int(feet_inches.group(1)) * 12 + int(feet_inches.group(2)))

    feet_inches_alt = re.fullmatch(
        r"(\d{1,3})\s*(?:ft|foot|feet)(?:\s*(\d{1,2})\s*in(?:ch|ches)?)?",
        value,
    )
    if feet_inches_alt:
        feet = int(feet_inches_alt.group(1))
        inches = int(feet_inches_alt.group(2)) if feet_inches_alt.group(2) else 0
        return str(feet * 12 + inches)

    numeric_inches = re.fullmatch(r"(\d{1,4})\s*(?:in|inch|inches)?", value)
    if numeric_inches:
        return numeric_inches.group(1)

    return raw.strip()


def _normalize_quote_symbols(value: str) -> str:
    return (
        value.replace("\u2019", "'")
        .replace("\u2032", "'")
        .replace("\u201d", '"')
        .replace("\u2033", '"')
    )
