"""Application settings from environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    landingai_api_key: str = ""
    landingai_base_url: str = "https://api.va.landing.ai"
    landingai_parse_model: str = "dpt-2"
    landingai_extract_model: str = "extract-latest"
    cors_origin: str = "http://localhost:5173"
    job_root: str = "data/jobs"
    forms_dir: str = "assets/forms"
    forms_download_enabled: bool = True
    jobs_max_count: int = 200
    job_ttl_seconds: int = 86_400
    upload_rate_limit_per_minute: int = 20


settings = Settings()
