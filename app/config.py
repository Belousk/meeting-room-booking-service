import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/booking"
    JWT_SECRET: str = "secret_key_for_testing_only_change_in_prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ADMIN_UUID: str = "11111111-1111-1111-1111-111111111111"
    USER_UUID: str = "22222222-2222-2222-2222-222222222222"

    model_config = ConfigDict(env_file=".env")

settings = Settings()