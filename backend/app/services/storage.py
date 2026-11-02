"""对象存储服务：SeaweedFS(S3) 为主，本地磁盘兜底。

设计目标：任何情况下后端不因对象存储故障而崩溃或产生 500。
- 上传：优先写 S3，失败回退本地磁盘，保证上传始终成功。
- 读取：优先读 S3，失败或对象不存在回退本地磁盘。
- 二者都不可用返回 None，由调用方给兜底占位。
- boto3 未安装时直接走本地磁盘（惰性导入，不影响启动）。
"""
import base64
import logging
import mimetypes
import os
from typing import Optional, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)

# 1x1 透明 PNG，用于图片缺失时兜底，避免页面出现破图/错乱
PLACEHOLDER_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)

_client = None
_client_ready = False
_client_init_done = False


def _get_client():
    """惰性初始化 boto3 S3 客户端，避免未安装 boto3 时启动失败。"""
    global _client, _client_ready, _client_init_done
    if not _client_init_done:
        _client_init_done = True
        if not settings.s3_enabled:
            logger.info("对象存储未启用，使用本地磁盘存储")
        else:
            try:
                import boto3
                from botocore.client import Config as BotoConfig

                _client = boto3.client(
                    "s3",
                    endpoint_url=settings.s3_endpoint,
                    aws_access_key_id=settings.s3_access_key,
                    aws_secret_access_key=settings.s3_secret_key,
                    region_name=settings.s3_region,
                    config=BotoConfig(
                        signature_version="s3v4",
                        s3={"addressing_style": "path"},
                        connect_timeout=3,
                        read_timeout=5,
                        retries={"max_attempts": 1},
                    ),
                )
                _client_ready = True
                logger.info(
                    "S3 客户端就绪: endpoint=%s bucket=%s", settings.s3_endpoint, settings.s3_bucket
                )
            except Exception as e:  # noqa: BLE001
                logger.warning("S3 客户端初始化失败，回退本地磁盘: %s", e)
                _client_ready = False
    return _client if _client_ready else None


def _guess_type(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


def save(category: str, filename: str, content: bytes) -> str:
    """保存文件，返回相对 URL。S3 失败时回退本地磁盘，保证上传成功。"""
    key = f"{category}/{filename}"
    url = f"/uploads/{key}"

    client = _get_client()
    if client is not None:
        try:
            client.put_object(
                Bucket=settings.s3_bucket,
                Key=key,
                Body=content,
                ContentType=_guess_type(filename),
            )
            return url
        except Exception as e:  # noqa: BLE001
            logger.warning("S3 上传失败，回退本地磁盘: %s", e)

    # 本地兜底
    save_dir = os.path.join(settings.upload_dir, category)
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, filename), "wb") as f:
        f.write(content)
    return url


def read(category: str, filename: str) -> Optional[Tuple[bytes, str]]:
    """读取文件，返回 (内容, media_type)。S3 失败/缺失时回退本地；都不存在返回 None。"""
    key = f"{category}/{filename}"

    client = _get_client()
    if client is not None:
        try:
            obj = client.get_object(Bucket=settings.s3_bucket, Key=key)
            return obj["Body"].read(), obj.get("ContentType") or _guess_type(filename)
        except Exception as e:  # noqa: BLE001
            logger.warning("S3 读取失败，尝试本地磁盘: %s", e)

    filepath = os.path.join(settings.upload_dir, category, filename)
    if os.path.isfile(filepath):
        with open(filepath, "rb") as f:
            return f.read(), _guess_type(filename)

    return None


def delete(category: str, filename: str) -> bool:
    """删除文件，返回是否删除成功。S3 与本地都尝试删除。"""
    key = f"{category}/{filename}"
    deleted = False

    client = _get_client()
    if client is not None:
        try:
            client.delete_object(Bucket=settings.s3_bucket, Key=key)
            deleted = True
        except Exception as e:  # noqa: BLE001
            logger.warning("S3 删除失败: %s", e)

    filepath = os.path.join(settings.upload_dir, category, filename)
    if os.path.isfile(filepath):
        try:
            os.remove(filepath)
            deleted = True
        except OSError as e:
            logger.warning("本地文件删除失败: %s", e)

    return deleted
