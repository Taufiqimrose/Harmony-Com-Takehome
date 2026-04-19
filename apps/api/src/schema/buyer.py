"""Buyer and confirm payloads."""

from pydantic import BaseModel, Field


class BuyerInfo(BaseModel):
    g6_smoke_detector_confirmed: bool = True
    g6_water_heater_confirmed: bool = True
    g6_own_home_confirmed: bool = True
    g6_own_land_answer: str = ""
    f4805_ro1_last: str = ""
    f4805_ro1_first: str = ""
    f4805_ro1_middle: str = ""
    f4805_ro2_last: str = ""
    f4805_ro2_first: str = ""
    f4805_ro2_middle: str = ""
    f4805_ro3_last: str = ""
    f4805_ro3_first: str = ""
    f4805_ro3_middle: str = ""
    f4805_current_mailing_street: str = ""
    f4805_current_mailing_city: str = ""
    f4805_current_mailing_county: str = ""
    f4805_current_mailing_state: str = "CA"
    f4805_current_mailing_zip: str = ""
    f4805_section2_purchased_from: str = ""
    f4805_s4_date_of_sale: str = ""
    f4805_s2_is_new_unit: str = ""
    f4805_s2_first_sold_new_date: str = ""
    f4805_s2_registered_in_ca_or_other_state: str = ""
    f4805_s2_last_registered_state_and_date: str = ""
    f4805_s2_entered_california_date: str = ""
    f4805_s2_last_licensed_resident_state: str = ""
    f4805_s2_resident_of_california: str = ""
    f4805_s2_became_resident_when: str = ""
    f4805_s3_outstanding_titles: str = ""
    f4805_s3_security_lien: str = ""
    f4805_4a_base_unit_price: str = ""
    f4805_4b_unattached_accessories_price: str = ""
    f4805_4d_sale_price: str = ""
    f4766_statement: str = ""

    model_config = {"populate_by_name": True, "extra": "ignore"}


class ConfirmBody(BaseModel):
    extracted_overrides: dict[str, str] = Field(default_factory=dict)
    buyer: BuyerInfo
