from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str

    mongo_db_url: str = "mongodb://root:password@localhost:27017/"
    db_name: str = "mydatabase"


@lru_cache
def get_settings():
    return Settings()