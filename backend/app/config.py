"""Settings for the sample TODO backend.

The database URL is read from the environment so the same source runs against
the docker-compose development database, a throwaway test database, or any
PostgreSQL a developer prefers.
"""

from __future__ import annotations

import os
from functools import lru_cache

DEFAULT_DATABASE_URL = "postgresql+psycopg://todo:todo@localhost:5432/todo"


class Settings:
    """Runtime configuration resolved once per process."""

    def __init__(self) -> None:
        self.database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
        self.cors_origins = [
            origin
            for origin in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
            if origin
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
