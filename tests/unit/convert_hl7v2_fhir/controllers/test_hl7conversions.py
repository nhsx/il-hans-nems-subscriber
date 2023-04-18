import pytest

from convert_hl7v2_fhir.controllers.hl7.hl7_conversions import (
    to_fhir_date,
    to_fhir_datetime,
)


@pytest.mark.parametrize(
    "input,expected", [("20230405144903", "2023-04-05"), ("20130301", "2013-03-01")]
)
def test_to_fhir_date__valid_DTM_converts_OK(input, expected):
    assert to_fhir_date(input) == expected


def test_to_fhir_datetime__invalid_DTM_raises_value_error():
    with pytest.raises(ValueError):
        to_fhir_datetime("20230302")


def test_to_fhir_datetime__valid_DTM_with_time_converts_OK():
    assert to_fhir_datetime("20230405150023") == "2023-04-05T15:00:23Z"
