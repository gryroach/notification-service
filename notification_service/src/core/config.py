# stdlib
from logging import config as logging_config
from pathlib import Path

# thirdparty
from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# project
from core.logger import LOGGING

logging_config.dictConfig(LOGGING)
DOTENV_PATH = find_dotenv(".env")
load_dotenv(DOTENV_PATH)


class AppSettings(BaseSettings):
    project_name: str = Field(default="Notification API")
    api_production: bool = Field(default=True)

    # Настройки Postgres
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="pass")
    postgres_host: str = Field(default="db")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="notification_db")
    echo_queries: bool = Field(default=False)

    # Настройки Redis
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=1)

    # Sentry
    sentry_dsn: str = Field(default="")
    sentry_traces_sample_rate: float = Field(default=1.0)

    # RabbitMQ
    rabbitmq_host: str = Field(default="rabbitmq")
    rabbitmq_port: int = Field(default=5672)
    rabbitmq_user: str = Field(default="guest")
    rabbitmq_password: str = Field(default="password")

    # Работа с токенами
    jwt_algorithm: str = Field(default="RS256")
    jwt_public_key_path: str = Field(default="/app/keys/example_public_key.pem")

    # Другие настройки
    test_mode: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="notify_",
    )

    @property
    def database_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"

    @property
    def jwt_public_key(self) -> str:
        try:
            with Path(self.jwt_public_key_path).open() as key_file:
                return key_file.read()
        except FileNotFoundError as err:
            raise ValueError(f"Public key file not found at: {self.jwt_public_key_path}") from err
        except Exception as err:
            raise ValueError(f"Error reading public key: {err!s}") from err


settings = AppSettings()
