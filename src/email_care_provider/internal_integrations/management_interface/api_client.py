from typing import Optional

import requests
from aws_lambda_powertools import Logger

from internal_integrations.management_interface.exceptions import (
    CareProviderLocationNotFound,
    ManagementInterfaceNotAvailable,
)
from internal_integrations.management_interface.schemas import CareProviderResponse
from internal_integrations.management_interface.settings import (
    get_management_interface_settings,
)

_LOGGER = Logger()


class ManagementInterfaceApiClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ):
        self.session: requests.Session = session or requests.Session()
        self.base_url: str = base_url or get_management_interface_settings().base_url

    def get_care_provider(
        self, *, care_recipient_pseudo_id: str
    ) -> CareProviderResponse:
        url = f"{self.base_url}/care-provider-location/_search/"
        data = {"_careRecipientPseudoId": care_recipient_pseudo_id}
        response = self.session.post(url, data=data)
        if response.status_code in range(400, 500):
            _LOGGER.warning({"response_text": response.text})
            raise CareProviderLocationNotFound

        if response.status_code >= 500:
            _LOGGER.warning({"response_text": response.text})
            raise ManagementInterfaceNotAvailable

        response_json = response.json()
        return CareProviderResponse(**response_json)
