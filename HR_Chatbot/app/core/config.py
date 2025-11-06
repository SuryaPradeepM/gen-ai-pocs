import os
from typing import List
from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings

env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

class Settings(BaseSettings):
    # Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

    # Vector Store Settings
    VECTOR_STORE_PATH: str = "vector_store"

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
# print(settings.AZURE_OPENAI_ENDPOINT)
# print(settings.AZURE_OPENAI_API_KEY)
# print(settings.AZURE_OPENAI_API_VERSION)
# print(settings.AZURE_OPENAI_DEPLOYMENT_NAME)
# print(settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME)
# print(settings.VECTOR_STORE_PATH)
# print(settings.ALLOWED_ORIGINS)
