from functools import lru_cache

from pydantic import BaseSettings


class ManagementInterfaceSettings(BaseSettings):
    base_url: str = "http://localhost:8000"

    class Config:
        env_prefix = "MANAGEMENT_INTERFACE_"


@lru_cache(maxsize=1)
def get_management_interface_settings() -> ManagementInterfaceSettings:
    return ManagementInterfaceSettings()
