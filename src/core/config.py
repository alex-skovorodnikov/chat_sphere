from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
import logging
from logging import config as logging_config

from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv('PROJECT_NAME', 'chat_phases')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)


class RedisConfig(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=6379)


class SecurityConfig(BaseSettings):
    secret_key: str = Field(default='secret_key')
    algorithm: str = Field(default='HS256')
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)


class PostgresConfig(BaseSettings):
    postgres_host: str = Field(default='localhost')
    postgres_port: Optional[int] = 5432  # Default port for PostgreSQL
    postgres_db: str = Field(default='chat')
    postgres_user: str = Field(default='app')
    postgres_password: Optional[str] = Field(default='123qwe')
    postgres_driver: str = Field(default='postgresql+asyncpg')

    @property
    def dsn(self) -> str:
        password_part = f":{self.postgres_password}@" if self.postgres_password else ''
        port_part = f":{self.postgres_port}" if self.postgres_port else ''
        return (
            f"{self.postgres_driver}://"
            f"{self.postgres_user}{password_part}"
            f"{self.postgres_host}{port_part}/"
            f"{self.postgres_db}"
        )


class Settings(BaseSettings):
    db: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()
    security: SecurityConfig = SecurityConfig()


settings = Settings()
logger.info(settings.security)
