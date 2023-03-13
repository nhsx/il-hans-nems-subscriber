from functools import lru_cache

from pydantic import BaseSettings


class NotifySettings(BaseSettings):
    api_key: str

    class Config:
        env_prefix = "NOTIFY_"


@lru_cache(maxsize=1)
def get_notify_settings() -> NotifySettings:
    return NotifySettings()


NOTIFY_SETTINGS: NotifySettings = get_notify_settings()
