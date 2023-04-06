from datetime import date

from src.email_care_provider.controllers.notify_care_provider import (
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
