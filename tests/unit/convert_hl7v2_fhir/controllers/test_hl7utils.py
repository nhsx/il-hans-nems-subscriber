from convert_hl7v2_fhir.controllers.utils import is_nhs_number_valid


def test_is_nhs_number_valid__invalid_modulus_fails():
    assert is_nhs_number_valid("9999999993") is False


def test_is_nhs_number_valid__invalid_length_fails():
    assert is_nhs_number_valid("1234") is False


def test_is_nhs_number_valid__valid_number_passes():
    assert is_nhs_number_valid("9999999999") is True
