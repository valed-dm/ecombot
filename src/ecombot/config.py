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
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import SettingsConfigDict

from .config_db import DatabaseSettings


BASE_DIR: Path = Path(__file__).resolve().parents[2]
OUTPUT_DIR: Path = BASE_DIR / "output"


class Settings(DatabaseSettings):
    """
    Defines and validates all environment variables for the application.

    Inherits from `pydantic_settings.BaseSettings` to automatically load values
    from the environment or the specified `.env` file. It also performs type
    casting and validation.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", case_sensitive=False, extra="ignore"
    )

    APP_NAME: Annotated[str, Field(default="ECOMBot")]
    APP_NAME_RU: Annotated[str, Field(default="")]
    APP_NAME_EN: Annotated[str, Field(default="")]
    APP_TG_USER: Annotated[str, Field(default="")]
    BOT_TOKEN: Annotated[str, Field(default="")]
    ADMIN_IDS: Annotated[list[int], Field(default=[1644421909])]

    STATIC_DIR: Annotated[Path, Field(default=BASE_DIR / "static")]

    @property
    def PRODUCT_IMAGE_DIR(self) -> Path:
        return self.STATIC_DIR / "products"

    DEBUG: Annotated[bool, Field(default=False)]

    LOG_LEVEL: Annotated[str, Field(default="INFO")]
    LOG_FILE: Annotated[Path, Field(default=OUTPUT_DIR / "ecombot.log")]

    CURRENCY: Annotated[str, Field(default="₽")]
    TIMEZONE: Annotated[str, Field(default="Europe/Moscow")]
    WEBHOOK_URL: Annotated[str, Field(default="")]

    @field_validator("WEBHOOK_URL")
    @classmethod
    def strip_webhook_url(cls, v: str) -> str:
        return v.strip() if v else v

    def get_zoneinfo(self) -> ZoneInfo:
        return ZoneInfo(self.TIMEZONE)


settings = Settings()
