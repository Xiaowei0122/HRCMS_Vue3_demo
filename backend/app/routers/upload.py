"""文件上传路由"""
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error
from app.core.config import settings
from app.services import storage

router = APIRouter(prefix="/upload", tags=["文件上传"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf", ".xlsx", ".xls", ".docx", ".doc"}
ALLOWED_CATEGORIES = {"products", "news", "honors", "banners", "avatars", "logos", "vehicles", "knowledge", "cases", "repairs"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(default="products"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    # 校验分类
    if category not in ALLOWED_CATEGORIES:
        return error(400, f"不支持的上传分类: {category}")

    # 校验扩展名
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return error(400, f"不支持的文件类型: {ext}")

    # 校验大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return error(400, f"文件大小不能超过 {MAX_FILE_SIZE // 1024 // 1024}MB")

    # 保存文件（SeaweedFS 为主，本地磁盘兜底）
    filename = f"{uuid.uuid4().hex}{ext}"
    url = storage.save(category, filename, content)

    return success({"url": url, "filename": filename}, "上传成功")
