from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str = os.environ.get("DATABASE_URI", "mongodb://mongodb:27017")
    database_user: str = os.environ.get("DATABASE_USERNAME", None)
    database_password: str = os.environ.get("DATABASE_PASSWORD", None)
    redis_url: str = os.environ.get("REDIS_URL", "redis://redis")
    redis_port: int = os.environ.get("REDIS_PORT", 6379)
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", '')
    default_llm: str = "gpt-3.5-turbo"
    LANGCHAIN_API_KEY: str = os.environ.get("LANGCHAIN_API_KEY", '')
    LANGCHAIN_ENDPOINT: str = os.environ.get("LANGCHAIN_ENDPOINT", '')

    class Config:
        env_file = ".env"


settings = Settings()
