import base64
import time
import uuid
from functools import lru_cache
from typing import Mapping, Any

from pydantic import BaseSettings, HttpUrl, validator


class PDSSettings(BaseSettings):
    jwt_rsa_private_key: str
    jwt_sub: str
    jwt_iss: str
    jwt_aud: str
    jwt_lifetime_seconds: int = 5 * 60
    jwt_algorithm: str = "RS512"
    jwks_kid: str = "int-1"

    api_key: str
    base_url: HttpUrl

    class Config:
        env_prefix = "PDS_"

    @validator("jwt_rsa_private_key", pre=True)
    def _decode_jwt_rsa_private_key_if_encoded(cls, v: str):
        if "-----BEGIN RSA PRIVATE KEY-----" in v:
            return f"{v}"  # to escape newlines
        try:
            return base64.b64decode(v)
        except ValueError:
            return v

    @property
    def jwt_claims(self) -> Mapping[str, Any]:
        return {
            "sub": self.jwt_sub,
            "iss": self.jwt_iss,
            "jti": str(uuid.uuid4()),
            "aud": self.jwt_aud,
            "exp": int(time.time()) + self.jwt_lifetime_seconds,
        }

    @property
    def jwt_headers(self) -> Mapping[str, str]:
        return {"kid": self.jwks_kid}


@lru_cache(maxsize=1)
def get_pds_settings():
    return PDSSettings()
