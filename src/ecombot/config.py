"""
Centralized, environment-aware application configuration.

This module uses `pydantic-settings` to load and validate application settings
from environment variables and a `.env` file. This provides a single source of
truth for all configuration, with type validation and clear defaults.

Attributes:
    BASE_DIR (Path): The absolute path to the project root directory.
    OUTPUT_DIR (Path): The directory for storing output files like logs.
    settings (Settings): A singleton instance of the validated settings class.
"""

from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR: Path = BASE_DIR / "output"


class Settings(BaseSettings):
    """
    Defines and validates all environment variables for the application.

    Inherits from `pydantic_settings.BaseSettings` to automatically load values
    from the environment or the specified `.env` file. It also performs type
    casting and validation.
    """

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", case_sensitive=False)

    APP_NAME: str = "ECOMBot"
    BOT_TOKEN: str = ""
    ADMIN_IDS: list[int] = [1644421909]

    STATIC_DIR: Path = BASE_DIR / "static"
    PRODUCT_IMAGE_DIR: Path = STATIC_DIR / "products"

    DEBUG: bool = True

    PGDATABASE: str = "ecombot"
    PGUSER: str = "postgres"
    PGPASSWORD: str = "postgres_default"
    PGHOST: str = "localhost"
    PGPORT: int = 5432

    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: Path = OUTPUT_DIR / "ecombot.log"


settings = Settings()
