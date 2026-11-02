"""上传文件读取代理：优先从 SeaweedFS 读，回退本地磁盘，缺失给兜底占位。

替代原来的 StaticFiles 静态挂载，前端图片 src 仍走 /uploads/{category}/{filename}。
"""
import os
import re

from fastapi import APIRouter
from fastapi.responses import Response

from app.services import storage

router = APIRouter(tags=["文件访问"])

# 文件名规则：uuid4().hex(32) + 扩展名，防路径穿越
_FILENAME_RE = re.compile(r"^[a-f0-9]{32}\.[a-z0-9]+$")
_CATEGORY_RE = re.compile(r"^[a-z]+$")
_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico"}


@router.get("/uploads/{category}/{filename}")
async def serve_upload(category: str, filename: str):
    # 非法路径直接 404，防目录穿越
    if not _CATEGORY_RE.fullmatch(category) or not _FILENAME_RE.fullmatch(filename):
        return Response(content="not found", status_code=404)

    result = storage.read(category, filename)
    if result is None:
        ext = os.path.splitext(filename)[1].lower()
        if ext in _IMAGE_EXT:
            # 图片缺失时返回 1x1 透明占位图，避免页面破图/布局错乱
            return Response(
                content=storage.PLACEHOLDER_PNG,
                media_type="image/png",
                headers={"Cache-Control": "no-store"},
            )
        return Response(content="not found", status_code=404)

    content, media_type = result
    return Response(content=content, media_type=media_type)
