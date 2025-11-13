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
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///hr_data.db")
    ENABLE_DATABASE: bool = os.getenv("ENABLE_DATABASE", "true").lower() == "true"

    # PDF Policies Folder
    HR_POLICIES_FOLDER: str = os.getenv("HR_POLICIES_FOLDER", "HR Policies Index")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"


settings = Settings()

# If a sqlite URL points to a relative file (e.g. sqlite:///hr_data.db),
# resolve it to an absolute path relative to the `app/` package so the
# application will find the bundled `hr_data.db` regardless of the
# current working directory when the process starts.
try:
    if isinstance(settings.DATABASE_URL, str) and settings.DATABASE_URL.startswith(
        "sqlite"
    ):
        url = settings.DATABASE_URL
        # strip scheme prefix and any leading slashes to get the file portion
        if url.startswith("sqlite:///"):
            db_path_part = url[len("sqlite:///") :]
        elif url.startswith("sqlite://"):
            db_path_part = url[len("sqlite://") :]
        else:
            db_path_part = url.split(":", 1)[-1]

        from pathlib import Path

        # If the extracted path is not absolute, resolve it relative to the app package
        if db_path_part and not Path(db_path_part).is_absolute():
            resolved_path = (Path(__file__).parent.parent / db_path_part).resolve()
            # Use forward slashes for the URL part; on Windows this is accepted by SQLAlchemy
            settings.DATABASE_URL = f"sqlite:///{resolved_path.as_posix()}"
except Exception:
    # Fall back to the original value on any unexpected error; don't crash at import time
    pass
