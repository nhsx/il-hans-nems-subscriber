from controllers.utils import is_nhs_number_valid


def test_is_nhs_number_valid__invalid_modulus_fails():
    assert not is_nhs_number_valid("9999999993")


def test_is_nhs_number_valid__invalid_length_fails():
    assert not is_nhs_number_valid("1234")


def test_is_nhs_number_valid__valid_number_passes():
    assert is_nhs_number_valid("9999999999")
