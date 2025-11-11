import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Settings(BaseSettings):
    # Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
    )
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str = os.getenv(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
    )

    # Vector Store Settings
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "vector_store")

    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hr_data.db")
    ENABLE_DATABASE: bool = os.getenv("ENABLE_DATABASE", "true").lower() == "true"

    # PDF Policies Folder
    HR_POLICIES_FOLDER: str = os.getenv("HR_POLICIES_FOLDER", "HR Policies Index")

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"


settings = Settings()
