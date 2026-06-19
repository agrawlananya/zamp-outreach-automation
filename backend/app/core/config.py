from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LLM_API_KEY: str = ""
    LLM_PROVIDER: str = "anthropic"
    TAVILY_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./zamp_sdr.db"
    CORS_ALLOWED_ORIGIN: str = "http://localhost:5500"
    SENDER_NAME: str = ""
    SENDER_TITLE: str = ""


settings = Settings()
