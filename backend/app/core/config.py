"""应用配置"""
import json
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    mongodb_uri: str = "mongodb://admin:123456@127.0.0.1:27017"
    database_name: str = "hrcms"

    # JWT
    jwt_secret: str = "hrcms-jwt-secret-key-2024"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Upload
    upload_dir: str = "./uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    # CORS
    cors_origins: str = '["http://localhost:3000","http://127.0.0.1:3000"]'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_cors_origins(self) -> list[str]:
        return json.loads(self.cors_origins)


settings = Settings()
