"""应用配置"""
import json
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    mongodb_uri: str = "mongodb://admin:123456@127.0.0.1:27017"
    database_name: str = "hrcms_test"

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

    # 对象存储 SeaweedFS (S3 兼容)，失败时自动回退本地磁盘
    s3_enabled: bool = True
    s3_endpoint: str = "http://192.168.1.111:8333"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin123"
    s3_region: str = "us-east-1"
    s3_bucket: str = "hrcms"

    # CORS
    cors_origins: str = '["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174","http://127.0.0.1:5174"]'

    # WeChat 小程序登录（jscode2session）
    wechat_appid: str = ""
    wechat_secret: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_cors_origins(self) -> list[str]:
        return json.loads(self.cors_origins)


settings = Settings()
