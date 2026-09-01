from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://uemp:uemp@localhost:5432/uemp"
    jwt_secret: str = "fallback-development-secret-change-me-please-32"
    jwt_expire_seconds: int = 60 * 60 * 24 * 7
    otp_mode: str = "demo"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    vision_model: str = "gpt-4o-mini"
    neshan_api_key: str = ""
    public_base_url: str = ""
    upload_dir: str = "data/uploads"
    cors_origins: str = "http://localhost:3000"
    cookie_secure: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
