from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    default_llm: str = "gpt-3.5-turbo"

    class Config:
        env_file = ".env"


settings = Settings()
