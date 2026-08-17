from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    database_url: str = "sqlite:///./toolkit.db"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    jwt_secret: str = "change_me_dev_secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60


settings = Settings()
