"""Pydantic schema for title extraction fields used by form fill."""

from pydantic import BaseModel, Field


class ExtractSchema(BaseModel):
    decal: str = Field(description="License decal number")
    serial: str = Field(description="Serial or VIN")
    make: str = Field(description="Manufacturer make")
    registered_owner: str = Field(description="Registered owner name")
    site_address: str = Field(description="Site or location address")
    manufacturer_name: str = Field(description="Manufacturer name from title")
    trade_name: str = Field(description="Trade name from title")
    date_of_manufacture: str = Field(description="Date of manufacture")
    model_name_or_number: str = Field(description="Model name or number")
    date_first_sold_new: str = Field(description="Date first sold new")
    hud_label_or_hcd_insignia: str = Field(description="HUD label or HCD insignia")
    length_inches: str = Field(description="Unit length in inches")
    width_inches: str = Field(description="Unit width in inches")
