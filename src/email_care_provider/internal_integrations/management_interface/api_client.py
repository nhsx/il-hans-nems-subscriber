from typing import Optional

import requests
from aws_lambda_powertools import Logger
from pydantic import HttpUrl

from internal_integrations.management_interface.schemas import CareProviderResponse
from internal_integrations.management_interface.settings import (
    get_management_interface_settings,
)

_LOGGER = Logger()


class ManagementInterfaceApiClient:
    def __init__(
        self,
        base_url: Optional[HttpUrl] = None,
        session: Optional[requests.Session] = None,
    ):
        self.session: requests.Session = session or requests.Session()
        # self.base_url: HttpUrl = (
        #     base_url or get_management_interface_settings().base_url
        # )

    def get_care_provider(self, *, patient_nhs_number: str) -> CareProviderResponse:
        # TODO
        return CareProviderResponse(
            given_name="Michal", email="michal.kras@thepsc.co.uk"
        )
