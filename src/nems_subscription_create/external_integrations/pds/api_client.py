import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
import requests
from pydantic import HttpUrl

from schemas import (
    AccessTokenResponse,
    PatientDetailsResponse,
)
from settings import PDS_SETTINGS


class PDSApiClient:
    def __init__(
            self,
            base_url: Optional[HttpUrl] = None,
            session: Optional[requests.Session] = None,
    ):
        self.session: requests.Session = session or requests.Session()
        self.base_url: HttpUrl = base_url or PDS_SETTINGS.base_url
        self._access_token = None
        self._access_token_expires_at = None

    def get_patient_details(self, nhs_number: str):
        url = f"{self.base_url}/personal-demographics/FHIR/R4/Patient/{nhs_number}"
        headers = {
            "Authorization": f"Bearer {self._get_valid_access_token()}",
            "X-Request-ID": str(uuid.uuid4()),
        }
        response = requests.get(url=url, headers=headers)
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
        response = requests.post(url, headers=headers, data=data)
        return AccessTokenResponse(**response.json())

    def _get_valid_access_token(self):
        if (
                self._access_token_expires_at is not None
                and self._access_token_expires_at > datetime.utcnow()
        ):
            return self._access_token

        access_token_response = self.post_oauth2_token(encoded_jwt=self._generate_jwt())
        self._access_token = access_token_response.access_token
        self._access_token_expires_at = access_token_response.issued_at + timedelta(
            seconds=access_token_response.expires_in
        )
        return self._access_token

    @staticmethod
    def _generate_jwt() -> str:
        return jwt.encode(
            payload=PDS_SETTINGS.jwt_claims,
            key=PDS_SETTINGS.jwt_rsa_private_key,
            algorithm=PDS_SETTINGS.jwt_algorithm,
            headers=PDS_SETTINGS.jwt_headers,
        )
