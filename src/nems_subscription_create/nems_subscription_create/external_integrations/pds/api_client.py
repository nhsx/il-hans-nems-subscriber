import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
import requests
from aws_lambda_powertools import Logger
from fhir.resources.operationoutcome import OperationOutcome
from pydantic import HttpUrl

from nems_subscription_create.external_integrations.pds.exceptions import (
    operation_outcome_to_exception,
    PDSUnavailable,
    UnknownPDSError,
)
from nems_subscription_create.external_integrations.pds.schemas import (
    PatientDetailsResponse,
    AccessTokenResponse,
)
from nems_subscription_create.external_integrations.pds.settings import get_pds_settings

_LOGGER = Logger()


class PDSApiClient:
    def __init__(
        self,
        base_url: Optional[HttpUrl] = None,
        session: Optional[requests.Session] = None,
    ):
        self.session: requests.Session = session or requests.Session()
        self.base_url: HttpUrl = base_url or get_pds_settings().base_url
        self._access_token: Optional[str] = None
        self._access_token_expires_at: Optional[datetime] = None

    def get_patient_details(self, nhs_number: str) -> PatientDetailsResponse:
        url = f"{self.base_url}/personal-demographics/FHIR/R4/Patient/{nhs_number}"
        headers = {
            "Authorization": f"Bearer {self._get_valid_access_token()}",
            "X-Request-ID": str(uuid.uuid4()),
        }
        response = self.session.get(url=url, headers=headers)
        if response.status_code in range(400, 500):
            operation_outcome = OperationOutcome(**response.json())
            _LOGGER.warning({"response_text": response.text})
            raise operation_outcome_to_exception(operation_outcome)

        if response.status_code >= 500:
            _LOGGER.warning({"response_text": response.text})
            raise PDSUnavailable

        response_json = response.json()
        return PatientDetailsResponse(**response_json)

    def post_oauth2_token(self, encoded_jwt: str) -> AccessTokenResponse:
        url = f"{self.base_url}/oauth2/token"
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": encoded_jwt,
        }
        response = self.session.post(url, headers=headers, data=data)
        if response.status_code != 200:
            _LOGGER.warning({"response_text": response.text})
            raise UnknownPDSError

        return AccessTokenResponse(**response.json())

    def _get_valid_access_token(self) -> str:
        if (
            self._access_token_expires_at is not None
            and self._access_token_expires_at > datetime.utcnow()
        ):
            _LOGGER.info("Reusing valid access token")
            return self._access_token

        _LOGGER.info(
            "Creating new access token",
            extra={
                "_access_token_expires_at": self._access_token_expires_at,
            },
        )
        access_token_response = self.post_oauth2_token(encoded_jwt=self._generate_jwt())
        self._access_token = access_token_response.access_token
        self._access_token_expires_at = datetime.utcnow() + timedelta(
            seconds=access_token_response.expires_in
        )
        _LOGGER.info(
            "Created new access token",
            extra={
                "_access_token_expires_at": self._access_token_expires_at,
            },
        )

        return self._access_token

    @staticmethod
    def _generate_jwt() -> str:
        pds_settings = get_pds_settings()
        return jwt.encode(
            payload=pds_settings.jwt_claims,
            key=pds_settings.jwt_rsa_private_key,
            algorithm=pds_settings.jwt_algorithm,
            headers=pds_settings.jwt_headers,
        )
