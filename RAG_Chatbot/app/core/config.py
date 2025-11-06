from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str

    # Vector Store Settings
    VECTOR_STORE_PATH: str = "vector_store"

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
