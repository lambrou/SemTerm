from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str = os.environ.get("DATABASE_URL", "mongodb://mongodb:27017")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", '')
    default_llm: str = "gpt-3.5-turbo"
    LANGCHAIN_API_KEY: str = os.environ.get("LANGCHAIN_API_KEY", '')
    LANGCHAIN_ENDPOINT: str = os.environ.get("LANGCHAIN_ENDPOINT", '')

    class Config:
        env_file = ".env"


settings = Settings()
