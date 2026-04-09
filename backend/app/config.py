import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://wildcard:wildcard@localhost:5432/wildcard"
    database_url_sync: str = "postgresql+psycopg2://wildcard:wildcard@localhost:5432/wildcard"
    anthropic_api_key: str = ""
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        if not path.is_absolute():
            path = Path(os.path.dirname(os.path.dirname(__file__))) / path
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()
