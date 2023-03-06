from datetime import datetime

from fhir.resources.patient import Patient
from pydantic import BaseModel


class AccessTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    issued_at: datetime


class PatientDetailsResponse(Patient):
    ...
