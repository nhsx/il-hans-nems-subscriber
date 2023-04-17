from datetime import timedelta, datetime
from unittest.mock import MagicMock

import pytest
import requests
from pytest_mock import MockFixture

from nems_subscription_create.external_integrations.pds.exceptions import (
    PDSApiClientException,
)
from nems_subscription_create.external_integrations.pds.schemas import (
    AccessTokenResponse,
)
from nems_subscription_create.external_integrations.pds.api_client import (
    PDSApiClient,
)


def test_pds_api_client__generate_jwt():
    # given
    pds_api_client = PDSApiClient()
    # when
    jwt = pds_api_client._generate_jwt()

    # then
    assert jwt is not None
    assert jwt.startswith("eyJ")


@pytest.mark.parametrize("response_status_code", (500, 502, 503, 504))
def test_get_patient_details__handles_server_error_responses(
    mocker: MockFixture, response_status_code: int
):
    # given
    nhs_number = "1234567890"
    access_token = "123456789012345"
    mocker.patch.object(
        PDSApiClient,
        PDSApiClient._get_valid_access_token.__name__,
        MagicMock(return_value=access_token),
    )
    session = MagicMock(spec=requests.Session)
    session.get.return_value.status_code = response_status_code
    session.get.return_value.status_code = response_status_code
    pds_api_client = PDSApiClient(session=session)

    # then
    with pytest.raises(PDSApiClientException):
        # when
        pds_api_client.get_patient_details(nhs_number)


@pytest.mark.parametrize("response_status_code", (500, 502, 503, 504))
def test_post_oauth2_token__handles_server_error_responses(response_status_code: int):
    # given
    encoded_jwt = "123456789012345"
    session = MagicMock(spec=requests.Session)
    session.get.return_value.status_code = response_status_code
    pds_api_client = PDSApiClient(session=session)

    # then
    with pytest.raises(PDSApiClientException):
        # when
        pds_api_client.post_oauth2_token(encoded_jwt=encoded_jwt)


@pytest.mark.parametrize(
    "access_token_expires_at",
    (
        datetime.utcnow() + timedelta(minutes=60),
        datetime.utcnow() - timedelta(minutes=60),
    ),
)
def test_get_patient_details__get_valid_access_token__subsequent_authorization(
    mocker: MockFixture, access_token_expires_at: datetime
):
    # given
    session = MagicMock(spec=requests.Session)
    pds_api_client = PDSApiClient(session=session)
    pds_api_client._access_token = "123456789012345"
    pds_api_client._access_token_expires_at = access_token_expires_at
    post_oauth2_token_patched = mocker.patch.object(
        PDSApiClient,
        PDSApiClient.post_oauth2_token.__name__,
        MagicMock(
            return_value=AccessTokenResponse(
                access_token="123456789012345",
                expires_in=120,
                issued_at=datetime.utcnow(),
                token_type="Bearer",
            )
        ),
    )

    # when
    pds_api_client._get_valid_access_token()

    # then
    if access_token_expires_at > datetime.utcnow():
        assert not post_oauth2_token_patched.called
    else:
        assert post_oauth2_token_patched.called
