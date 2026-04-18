from functools import lru_cache
import os
from secrets import token_urlsafe
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AssistIQ"
    environment: str = "development"
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/assistancebot"
    database_ssl_mode: str | None = None
    secret_key: str = Field(default_factory=lambda: token_urlsafe(32))
    access_token_expire_minutes: int = 60 * 8
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080,http://localhost:8088"
    cors_origin_regex: str | None = None
    auto_create_tables: bool = True
    seed_demo_data: bool = True

    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str = "https://aaif-codebridge-llm.cognitiveservices.azure.com/"
    azure_openai_deployment: str = "codeBridge-gtp5-chat"
    azure_openai_api_version: str = "2025-01-01-preview"
    azure_openai_timeout_seconds: float = 15.0
    azure_openai_max_completion_tokens: int = 700
    azure_openai_temperature: float | None = None

    demo_admin_email: str = "admin@company.com"
    demo_admin_password: str = "AdminPass123!"
    demo_technician_email: str = "tech@company.com"
    demo_technician_password: str = "TechPass123!"
    demo_user_email: str = "user@company.com"
    demo_user_password: str = "UserPass123!"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)

        if self.database_ssl_mode and not url.startswith("sqlite"):
            parts = urlsplit(url)
            query = dict(parse_qsl(parts.query, keep_blank_values=True))
            query.setdefault("sslmode", self.database_ssl_mode)
            url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
        return url

    def validate_for_runtime(self) -> None:
        if self.environment.lower() not in {"production", "staging"}:
            return

        errors: list[str] = []
        secret_from_env = os.getenv("SECRET_KEY")
        if not secret_from_env or len(self.secret_key) < 32 or self.secret_key == "change-this-secret-before-deployment":
            errors.append("SECRET_KEY must be set to a stable random value of at least 32 characters.")
        if not os.getenv("DATABASE_URL") or "localhost" in self.database_url or self.database_url.startswith("sqlite"):
            errors.append("DATABASE_URL must point to the hosted Postgres database.")
        if not self.cors_origin_list and not self.cors_origin_regex:
            errors.append("CORS_ORIGINS or CORS_ORIGIN_REGEX must allow the deployed frontend URL.")
        if self.cors_origin_list and all("localhost" in origin for origin in self.cors_origin_list) and not self.cors_origin_regex:
            errors.append("CORS_ORIGINS must include the deployed frontend URL, not only localhost origins.")

        if errors:
            raise RuntimeError("Invalid deployment configuration: " + " ".join(errors))

    @field_validator("azure_openai_temperature", mode="before")
    @classmethod
    def parse_optional_float(cls, value: object) -> object:
        if value == "":
            return None
        return value

    @property
    def azure_openai_chat_endpoint(self) -> str:
        base_url = self.azure_openai_endpoint.rstrip("/")
        return (
            f"{base_url}/openai/deployments/{self.azure_openai_deployment}"
            f"/chat/completions?api-version={self.azure_openai_api_version}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
