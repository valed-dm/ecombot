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

from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


BASE_DIR: Path = Path(__file__).resolve().parents[2]
OUTPUT_DIR: Path = BASE_DIR / "output"


class Settings(BaseSettings):
    """
    Defines and validates all environment variables for the application.

    Inherits from `pydantic_settings.BaseSettings` to automatically load values
    from the environment or the specified `.env` file. It also performs type
    casting and validation.
    """

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", case_sensitive=False)

    APP_NAME: Annotated[str, Field(default="ECOMBot")]
    BOT_TOKEN: Annotated[str, Field(default="")]
    ADMIN_IDS: Annotated[list[int], Field(default=[1644421909])]

    STATIC_DIR: Annotated[Path, Field(default=BASE_DIR / "static")]
    PRODUCT_IMAGE_DIR: Annotated[Path, Field(default=STATIC_DIR / "products")]

    DEBUG: Annotated[bool, Field(default=True)]

    PGDATABASE: Annotated[str, Field(default="ecombot")]
    PGUSER: Annotated[str, Field(default="postgres")]
    PGPASSWORD: Annotated[str, Field(default="postgres_default")]
    PGHOST: Annotated[str, Field(default="localhost")]
    PGPORT: Annotated[int, Field(default=5432)]

    LOG_LEVEL: Annotated[str, Field(default="DEBUG")]
    LOG_FILE: Annotated[Path, Field(default=OUTPUT_DIR / "ecombot.log")]


settings = Settings()
