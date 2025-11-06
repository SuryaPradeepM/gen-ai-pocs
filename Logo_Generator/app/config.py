from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):  # pylint: disable=too-few-public-methods
    azure_openai_endpoint: str
    azure_openai_key: str
    azure_openai_deployment_name: str

    class Config:  # pylint: disable=too-few-public-methods
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
