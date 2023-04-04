from functools import lru_cache

from pydantic import BaseSettings

class SQSSettings(BaseSettings):
    converted_queue_url: str 

    class Config:
        env_prefix = "SQS_"

@lru_cache(maxsize=1)
def get_sqs_settings() -> SQSSettings:
    return SQSSettings()
