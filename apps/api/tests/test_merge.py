"""Unit tests for merge helpers."""

from datetime import UTC, datetime
from pathlib import Path

from src.pipeline.merge import (
    build_merged_payload,
    normalize_inches,
    split_site_address,
    sum_currency_strings,
)
from src.pipeline.state import JobState
from src.schema.buyer import BuyerInfo
from src.schema.verified import VerifiedField


def test_split_site_address_two_segments() -> None:
    s = split_site_address("520 Pine Ave, Santa Barbara, CA 93117")
    assert s["street"] == "520 Pine Ave"
    assert s["city"] == "Santa Barbara"
    assert s["county"] == ""
    assert s["state"] == "CA"
    assert s["zip"] == "93117"


def test_split_site_address_three_segments() -> None:
    s = split_site_address("1 Main St, Fresno, Fresno County, CA 93701")
    assert s["street"] == "1 Main St"
    assert s["city"] == "Fresno"
    assert s["county"] == "Fresno County"
    assert s["state"] == "CA"
    assert s["zip"] == "93701"


def test_sum_currency_strings_two_decimals() -> None:
    assert sum_currency_strings("100.50", "0") == "100.50"
    assert sum_currency_strings("$1,000.00", "25.5") == "1025.50"


def test_normalize_inches_feet() -> None:
    assert normalize_inches("10'") == "120"
    assert normalize_inches("5' 6\"") == "66"


def test_build_merged_payload_situs_county_not_city() -> None:
    vf = {
        "registered_owner": VerifiedField(
            value="Doe, Jane",
            bbox=(0, 0, 0, 0),
            ade_confidence=0.5,
            rule_confidence=0.5,
            final_confidence=0.5,
            flags=[],
        ),
        "site_address": VerifiedField(
            value="1 Main, Fresno, Fresno County, CA 93701",
            bbox=(0, 0, 0, 0),
            ade_confidence=0.5,
            rule_confidence=0.5,
            final_confidence=0.5,
            flags=[],
        ),
    }
    for k in (
        "decal",
        "serial",
        "make",
        "manufacturer_name",
        "trade_name",
        "date_of_manufacture",
        "model_name_or_number",
        "date_first_sold_new",
        "hud_label_or_hcd_insignia",
        "length_inches",
        "width_inches",
    ):
        vf[k] = VerifiedField(
            value="x",
            bbox=(0, 0, 0, 0),
            ade_confidence=0.5,
            rule_confidence=0.5,
            final_confidence=0.5,
            flags=[],
        )

    job = JobState(
        job_id="t",
        status="filling",
        title_path=Path("t.pdf"),
        title_image_path=None,
        extracted=None,
        verified=vf,
        extracted_overrides=None,
        buyer=BuyerInfo(
            f4805_ro1_last="Doe",
            f4805_ro1_first="Jane",
            f4805_current_mailing_street="1",
            f4805_current_mailing_city="c",
            f4805_current_mailing_county="co",
            f4805_current_mailing_zip="z",
        ),
        filled_paths={},
        thumb_paths={},
        zip_path=None,
        created_at=datetime.now(tz=UTC),
    )
    payload = build_merged_payload(job)
    assert payload["situs.county"] == "Fresno County"
    assert payload["situs.city"] == "Fresno"
