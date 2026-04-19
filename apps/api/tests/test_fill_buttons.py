"""Tests for PDF button-state coercion."""

from src.pipeline.fill_acro import choose_button_state


def test_choose_button_yes() -> None:
    keys = ["/Yes", "/Off"]
    assert choose_button_state(keys, "Yes") == "/Yes"


def test_choose_button_no() -> None:
    keys = ["/Yes", "/No", "/Off"]
    assert choose_button_state(keys, "No") == "/No"
