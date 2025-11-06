"""
Config
"""

from pathlib import Path

import hjson
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent.parent
TEMP_DIR = ROOT_DIR / "artifact/temp"
DOTENV_PATH = ROOT_DIR / "config/.env"
load_dotenv(DOTENV_PATH)


def get_app_config():
    """getter utility for config

    Args:
        app_name (str, optional): Defaults to APP_NAME.

    Raises:
        ValueError: If invalid app_name is passed
        ValueError: _description_

    Returns:
        app_config: Config (specific to required app)
    """
    config_path = ROOT_DIR / "config/config.hjson"
    with open(config_path, "r", encoding="utf-8") as config_file:
        app_config = hjson.load(config_file)
    return app_config


config = get_app_config()
