from functools import lru_cache

from pydantic import BaseSettings


class EmailTemplatesIDs:
    ADMISSION = "5ae27d4d-8c70-4ee3-b906-9983a004a2f4"


class NotifySettings(BaseSettings):
    api_key: str
    email_templates = EmailTemplatesIDs

    class Config:
        env_prefix = "NOTIFY_"


@lru_cache(maxsize=1)
def get_notify_settings() -> NotifySettings:
    return NotifySettings()
