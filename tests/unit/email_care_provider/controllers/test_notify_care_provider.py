from datetime import date, datetime
from unittest.mock import MagicMock

from email_care_provider.controllers.notify_care_provider import (
    NotifyCareProviderController,
)


def test_notify_care_provider_controller__generate_pseudo_id():
    # given
    nhs_number = "9728002432"
    date_of_birth = date(1958, 6, 10)

    # when
    pseudo_id = NotifyCareProviderController._generate_pseudo_id(
        nhs_number, date_of_birth
    )

    # then
    assert (
        pseudo_id
        == "3c8dc4bb3c6b63269c7b91e09cabe3db162d03eb3559568e2cbade6a41290ccef1605d103eb74915fb2474bf698ddcd6835f004b843bc93ec80dc14337df18a0"
    )


def test_notify_care_provider_controller__dates_are_correctly_passed_to_template():
    """Regression for HANS-346"""

    # given
    nhs_number = "9728002432"
    given_name = "John"
    family_name = "Doe"
    location_name = "The Best Hospital"
    date_of_birth = date(1958, 6, 10)
    admitted_at = datetime(2022, 10, 10, 8, 30)

    management_interface_api_client_mock = MagicMock()
    notifications_api_client_mock = MagicMock()

    # when
    NotifyCareProviderController(
        management_interface_api_client=management_interface_api_client_mock,
        notifications_api_client=notifications_api_client_mock,
    ).send_email_to_care_provider(
        patient_nhs_number=nhs_number,
        patient_given_name=given_name,
        patient_family_name=family_name,
        patient_birth_date=date_of_birth,
        location_name=location_name,
        admitted_at=admitted_at,
    )

    # then
    assert notifications_api_client_mock.send_email_notification.called
    personalisation = notifications_api_client_mock.send_email_notification.call_args[
        1
    ].pop("personalisation")
    assert personalisation["event_time_str"] == str(admitted_at.time())
    assert personalisation["event_date_str"] == str(admitted_at.date())
