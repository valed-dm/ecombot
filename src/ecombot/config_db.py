from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """
    Database connection settings and connection pool configuration.

    Loads PostgreSQL database parameters and connection pool
    settings from environment variables.
    """

    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    PGHOST: Annotated[str, Field(default="localhost")]
    PGUSER: Annotated[str, Field(default="postgres")]
    PGPASSWORD: Annotated[str, Field(default="postgres_default")]
    PGPORT: Annotated[int, Field(default=5432)]
    PGDATABASE: Annotated[str, Field(default="bab")]
    PGTEST_DB_NAME: Annotated[str, Field(default="bab_test")]

    @property
    def database_url(self) -> str:
        """
        Construct the PostgreSQL database connection URL.

        Returns:
            str: PostgreSQL connection URL formatted for asyncpg.
        """
        return (
            f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}"
            f"@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"
        )
