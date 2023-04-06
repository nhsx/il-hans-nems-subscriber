import json
from unittest.mock import MagicMock
from uuid import uuid4

import requests
import pytest
from internal_integrations.management_interface.api_client import (
    ManagementInterfaceApiClient,
)
from internal_integrations.management_interface.exceptions import (
    ManagementInterfaceApiClientException,
)


@pytest.mark.parametrize("response_status_code", (400, 404, 424, 500, 502))
def test_management_interface_api_client__not_ok_statuses_are_handled(
    response_status_code: int,
):
    # given
    session = MagicMock(spec=requests.Session)
    session.post.return_value.status_code = response_status_code
    management_interface_api_client = ManagementInterfaceApiClient(
        base_url="http://test", session=session
    )
    pseudo_id = str(uuid4())

    # then
    with pytest.raises(ManagementInterfaceApiClientException):
        # when
        management_interface_api_client.get_care_provider(
            care_recipient_pseudo_id=pseudo_id
        )


def test_management_interface_api_client__ok_response():
    # given
    session = MagicMock(spec=requests.Session)
    session.post.return_value.status_code = 200
    session.post.return_value.json.return_value = json.loads(
        """{
  "resourceType": "Organization",
  "name": "Your Care Provider Branch Name",
  "telecom": [
    {
      "system": "email",
      "value": "example@nhs.net",
      "use": "work"
    }
  ]
}"""
    )
    management_interface_api_client = ManagementInterfaceApiClient(
        base_url="http://test", session=session
    )
    pseudo_id = str(uuid4())

    # when
    care_provider = management_interface_api_client.get_care_provider(
        care_recipient_pseudo_id=pseudo_id
    )

    # then
    assert care_provider.name
    assert "nhs" in care_provider.telecom[0].value
