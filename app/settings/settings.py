from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import app


class AppSettings(BaseModel):
    admin_session_ttl_minutes: int = 60
    cookie_session_max_age_minutes: int = 60


class MiddlewareSettings(BaseModel):
    ip_blocked_expires_minutes: int = 60
    max_ip_fail_logins: int = 10


class Settings(BaseSettings):
    admin_name: str
    admin_key: str
    admin_hs_256_key: str
    redis_host: str
    redis_port: int
    redis_password: str | None = None
    notes_swagger: str
    sql_database_url: str

    app_settings: AppSettings = AppSettings()
    middleware_settings: MiddlewareSettings = MiddlewareSettings()

    model_config = SettingsConfigDict(env_file=Path(app.__file__).parent.parent.joinpath(".env"),
                                      env_file_encoding="utf-8")


settings = Settings()
