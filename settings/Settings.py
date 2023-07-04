from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str = os.environ.get("DATABASE_URL", "mongodb://localhost:27018")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", '')
    default_llm: str = "gpt-3.5-turbo"

    class Config:
        env_file = ".env"


settings = Settings()
