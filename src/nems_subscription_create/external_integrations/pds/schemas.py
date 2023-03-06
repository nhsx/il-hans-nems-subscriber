from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class AccessTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    issued_at: datetime


class _Period(BaseModel):
    start: str


class _Name(BaseModel):
    family: str
    given: List[str]
    id: str
    period: _Period
    prefix: List[str]
    use: str


class PatientDetailsResponse(BaseModel):
    birth_date: str = Field(..., alias="birthDate")
    name: List[_Name]
    # + many more fields we don't care about right now
