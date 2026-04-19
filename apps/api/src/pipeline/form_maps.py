"""Declarative mapping from merged payload keys into HCD form targets."""

import sys
from pathlib import Path

from pypdf import PdfReader

# Map: HCD field name -> merged payload key from merge.build_merged_payload().
ACRO_FIELD_MAPS: dict[str, dict[str, str]] = {
    "476-6g": {
        "Decal (License) No": "decal",
        "Decal (License) No.(s) (page 1):": "decal",
        "Decal (License) No.(s) (page 2):": "decal",
        "Serial No": "serial",
        "Serial No.(s) (page 1):": "serial",
        "Serial No.(s) (page 2):": "serial",
        "I/We, the undersigned, hereby state that the manufactured home, mobilehome, or multifamily manufactured home described above is equipped with a properly working, operable smoke detector in accordance with California Health and Safety Code Section 18029": "manual.g6_smoke_detector",
        "I/We, the undersigned, hereby state that the manufactured home, mobilehome, or multifamily manufactured home described above is equipped with a properly working, operable smoke detector in accordance with California Health and Safety Code Section 18029.6 and a carbon monoxide detector in accordance to California Residential Code Section R315": "manual.g6_smoke_detector",
        "Do you (the registered owner) own your manufactured home/mobilehome?": "manual.g6_own_home",
        "Do you (the registered owner) own the land your manufactured home/mobilehome is located on?": "manual.g6_own_land",
        "I/We the undersigned hereby state that all fuel gas-burning water heater appliances in the manufactured home, mobilehome, or multifamily manufactured housing described above are seismically braced, anchored, or strapped in accordance with Health and Safety Co": "manual.g6_water_heater",
    },
    "476-6": {
        "Decal (License) Number": "decal",
        "Trade Name:": "trade_name",
        "Statement": "manual.f4766_statement",
    },
    "480-5": {
        "DECAL/LICENSE # (1):": "decal",
        "MANUFACTURER SERIAL NUMBER(S) (1)": "serial",
        "Name of Manufacturer:": "manufacturer_name",
        "Trade Name:": "trade_name",
        "Date of Manufacture:": "date_of_manufacture",
        "Model Name or #:": "model_name_or_number",
        "Date First Sold New:": "date_first_sold_new",
        "HUD LABEL OR HCD INSIGNIA # (1)": "hud_label_or_hcd_insignia",
        "LENGTH (Inches) (1):": "length_inches",
        "WIDTH (Inches) (1):": "width_inches",
        "Last name of Registered Owner(s) (1):": "manual.f4805_ro1_last",
        "First name of Registered Owner(s) (1):": "manual.f4805_ro1_first",
        "Middle name of Registered Owner(s) (1):": "manual.f4805_ro1_middle",
        "Last name of Registered Owner(s) (2):": "manual.f4805_ro2_last",
        "First name of Registered Owner(s) (2):": "manual.f4805_ro2_first",
        "Middle name of Registered Owner(s) (2):": "manual.f4805_ro2_middle",
        "Last name of Registered Owner(s) (3):": "manual.f4805_ro3_last",
        "First name of Registered Owner(s) (3):": "manual.f4805_ro3_first",
        "Middle name of Registered Owner(s) (3):": "manual.f4805_ro3_middle",
        "Street of Current Mailing Address for Registered Owner(s):": "manual.f4805_current_mailing_street",
        "City of Current Mailing Address for Registered Owner(s):": "manual.f4805_current_mailing_city",
        "County of Current Mailing Address for Registered Owner(s):": "manual.f4805_current_mailing_county",
        "State of Current Mailing Address for Registered Owner(s):": "manual.f4805_current_mailing_state",
        "Zip of Current Mailing Address for Registered Owner(s):": "manual.f4805_current_mailing_zip",
        "Street of Situs (Location) Address of unit for Registered Owner(s):": "situs.street",
        "City of Situs (Location) Address of unit for Registered Owner(s):": "situs.city",
        "County of Situs (Location) Address of unit for Registered Owner(s):": "situs.county",
        "State of Situs (Location) Address of unit for Registered Owner(s):": "situs.state",
        "Zip of Situs (Location) Address of unit for Registered Owner(s):": "situs.zip",
        "This unit was purchased from": "manual.f4805_section2_purchased_from",
        "Enter the date of sale:": "manual.f4805_s4_date_of_sale",
        "Are you an active duty member of the U.S. Armed Forces?": "manual.f4805_s5_active_duty",
        "When this unit was last licensed, were you on active duty as a member of the U.S. Armed Forces?": "manual.f4805_s5_last_licensed_active_duty",
        "Is the unit installed on the tax-free portion of a military reservation?": "manual.f4805_s5_military_reservation",
        "Are you a member of a Federally Recognized American Indian Tribe?": "manual.f4805_s5_federally_recognized_tribe",
        "Are you a disabled veteran?": "manual.f4805_s5_disabled_veteran",
        "Are you requesting exempt registration?": "manual.f4805_s5_exempt_registration",
        "Is this a new unit?": "manual.f4805_s2_is_new_unit",
        'If "NO", enter the date the unit was first sold new:': "manual.f4805_s2_first_sold_new_date",
        "Has this unit been registered in California or any other State?": "manual.f4805_s2_registered_in_ca_or_other_state",
        'If "YES", enter the state and the date the unit was last registered in:': "manual.f4805_s2_last_registered_state_and_date",
        "Enter the month, day, and year the unit entered California:": "manual.f4805_s2_entered_california_date",
        "When the unit was last licensed, what state were you a resident of?:": "manual.f4805_s2_last_licensed_resident_state",
        "Are you a resident of California": "manual.f4805_s2_resident_of_california",
        'If "YES", when did you become a resident?:': "manual.f4805_s2_became_resident_when",
        "Except for any accompanying titles, are there any outstanding titles for this unit issued by any state?": "manual.f4805_s3_outstanding_titles",
        "Is this unit now being used as security for any lien(s) other than the lien(s) shown (if any) on the reverse side of this application?": "manual.f4805_s3_security_lien",
        "Base unit (do not include sales tax, finance charges, transportation or installation charges) ($):": "manual.f4805_4a_base_unit_price",
        "Unattached accessories (skirting, awning, refrigerator, etc.) ($):": "manual.f4805_4b_unattached_accessories_price",
        "TOTAL ($):": "manual.f4805_4_total_price",
        "Executed at:": "manual.f4805_executed_at",
    },
}


def dump_acro_fields(pdf_path: Path) -> list[str]:
    """Return sorted AcroForm field names from a PDF."""
    reader = PdfReader(str(pdf_path))
    fields = reader.get_fields() or {}
    return sorted(fields.keys())


def _main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python -m src.pipeline.form_maps <pdf>")
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"not found: {path}")
        return 1
    names = dump_acro_fields(path)
    if not names:
        print("(no acroform fields)")
        return 0
    for name in names:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
