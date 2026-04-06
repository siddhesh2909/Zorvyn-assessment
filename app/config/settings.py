from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PORT: int = 3000
    JWT_SECRET: str = "your-super-secret-key-change-in-production"
    JWT_EXPIRES_IN: str = "24h"
    DB_PATH: str = "./data/finance.db"
    NODE_ENV: str = "development"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def jwt_expiry_seconds(self) -> int:
        value = self.JWT_EXPIRES_IN.strip()
        if value.endswith("h"):
            return int(value[:-1]) * 3600
        if value.endswith("m"):
            return int(value[:-1]) * 60
        if value.endswith("d"):
            return int(value[:-1]) * 86400
        return int(value)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
