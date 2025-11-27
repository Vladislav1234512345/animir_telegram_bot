import logging
from datetime import timedelta

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import subprocess

from container import BASE_DIR

def get_git_branch():
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        ).decode().strip()
        return branch
    except:
        return "default"


env_file_map = {
    "feature": ".env",
    "dev": ".env.dev",
    "main": ".env.prod"
}

env_file = env_file_map.get(get_git_branch(), ".env")

print(f"Загружаю переменные окружения из файла: {env_file}")


class WebSettings(BaseSettings):
    BOT_TOKEN: SecretStr
    ADMIN_ID: int

    WEBHOOK_URL: str
    FRONTEND_URL: str

    WEBHOOK_PATH: str = "/webhook"

    WEB_HOST: str
    WEB_PORT: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / env_file,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    DATABASE_ECHO: bool

    @property
    def POSTGRES_URL_psycopg(self):
        password = (
            self.POSTGRES_PASSWORD.get_secret_value()
            if hasattr(self.POSTGRES_PASSWORD, "get_secret_value")
            else self.POSTGRES_PASSWORD
        )
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    @property
    def POSTGRES_URL_asyncpg(self):
        password = (
            self.POSTGRES_PASSWORD.get_secret_value()
            if hasattr(self.POSTGRES_PASSWORD, "get_secret_value")
            else self.POSTGRES_PASSWORD
        )
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / env_file,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )


class JWTSettings(BaseSettings):
    private_key_path: Path = BASE_DIR / "server" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "server" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: timedelta = timedelta(minutes=15)
    refresh_token_expire_days: timedelta = timedelta(days=7)


class CookiesSettings(BaseSettings):
    access_token_name: str = "access_token"
    refresh_token_name: str = "refresh_token"
    httponly: bool = True
    samesite: str = "Lax"
    secure: bool = False

class LoggingSettings(BaseSettings):
    logging_level: int = logging.INFO

    model_config = SettingsConfigDict(
        case_sensitive=True,
    )


web_settings = WebSettings() #type: ignore
database_settings = DatabaseSettings() #type: ignore
jwt_settings = JWTSettings()
cookies_settings = CookiesSettings()
logging_settings = LoggingSettings()

