from unittest.mock import MagicMock

import pytest
from fhir.resources.humanname import HumanName

from nems_subscription_create.controllers.verify_patient import VerifyPatientController


@pytest.mark.parametrize(
    ("human_name_1", "human_name_2", "do_names_match"),
    [
        (
            HumanName(given=["John", "James"], family="Doe"),
            HumanName(given=["John", "Jamie"], family="DOE"),
            True,
        ),
        (
            HumanName(given=["Mark"], family="Flynn"),
            HumanName(given=["mark"], family="flynn"),
            True,
        ),
        (
            HumanName(given=["John", "James"], family="Doe"),
            HumanName(given=["James", "Jamie"], family="DOE"),
            False,
        ),
        (
            HumanName(given=["John", "James"], family="Doe"),
            HumanName(given=["James", "John"], family="Doe"),
            False,
        ),
        (
            HumanName(given=["Matilda"], family="Black"),
            HumanName(given=["Mathilda"], family="Black"),
            False,
        ),
    ],
)
def test_verify_patient_controller__do_human_names_match(
    human_name_1: HumanName, human_name_2: HumanName, do_names_match: bool
):
    # given
    verify_patient_controller = VerifyPatientController(pds_api_client=MagicMock())

    # then
    assert (
        verify_patient_controller._do_human_names_match(human_name_1, human_name_2)
        is do_names_match
    )
