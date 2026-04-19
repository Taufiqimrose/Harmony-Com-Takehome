"""ADE extract confidence: honest None when the API omits scores."""

from src.pipeline.extract import _build_fields_from_extraction, _cell_value_and_confidence
from src.pipeline.verify import _composite_no_llm, _composite_no_llm_optional_ade


def test_cell_plain_string_has_no_confidence() -> None:
    assert _cell_value_and_confidence("hello") == ("hello", None)


def test_cell_dict_with_confidence() -> None:
    raw = {"value": "  x  ", "confidence": 0.9}
    assert _cell_value_and_confidence(raw) == ("x", 0.9)


def test_cell_dict_without_confidence() -> None:
    raw = {"value": "x", "references": ["a"]}
    assert _cell_value_and_confidence(raw) == ("x", None)


def test_build_fields_prefers_extraction_metadata_dict() -> None:
    extraction = {"decal": "IGNORED_WHEN_META_PRESENT"}
    meta = {"decal": {"value": "DEC", "confidence": 0.77}}
    fields = _build_fields_from_extraction(extraction, meta)
    assert fields["decal"].value == "DEC"
    assert fields["decal"].ade_confidence == 0.77


def test_composite_no_llm_uses_rule_only_when_ade_missing() -> None:
    assert _composite_no_llm_optional_ade(None, 0.88) == 0.88


def test_composite_no_llm_averages_ade_and_rule() -> None:
    assert _composite_no_llm(0.8, 0.6) == 0.7
