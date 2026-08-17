"""财务管理路由 — 共享文件 + 资产管理"""
import os
import uuid
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, require_user_types
from app.core.response import success, error, paginate
from app.core.config import settings

router = APIRouter(prefix="/finance", tags=["财务管理"], dependencies=[Depends(require_user_types("admin", "internal"))])

ALLOWED_FILE_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".docx", ".doc", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".txt", ".csv", ".zip"}
FILE_CATEGORIES = {"invoice", "report", "policy", "contract", "other"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


# ─── 共享文件 ──────────────────────────────────────

@router.get("/files")
async def get_file_list(
    page: int = 1,
    size: int = 20,
    category: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    filter_q = {}
    if category and category != "all":
        filter_q["category"] = category
    total = await db.finance_files.count_documents(filter_q)
    cursor = db.finance_files.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for f in cursor:
        records.append(_format_file(f))
    return success(paginate(records, total, page, size))


@router.post("/files")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(default="other"),
    visibility: str = Form(default="public"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if category not in FILE_CATEGORIES:
        return error(400, f"不支持的文件分类: {category}")
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_FILE_EXTENSIONS:
        return error(400, f"不支持的文件类型: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return error(400, "文件大小不能超过 20MB")

    save_dir = os.path.join(settings.upload_dir, "finance")
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(save_dir, filename), "wb") as fh:
        fh.write(content)

    doc = {
        "name": file.filename,
        "type": ext.lstrip("."),
        "category": category,
        "visibility": visibility,
        "url": f"/uploads/finance/{filename}",
        "size": _format_size(len(content)),
        "uploader": "admin",
        "uploadTime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "createdAt": datetime.now(timezone.utc),
    }
    result = await db.finance_files.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "文件上传成功")


@router.put("/files/{file_id}")
async def update_file_meta(
    file_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_files.update_one({"_id": ObjectId(file_id)}, {"$set": body})
    return success(None, "文件信息已更新")


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_files.delete_one({"_id": ObjectId(file_id)})
    return success(None, "文件已删除")


@router.put("/files/{file_id}/permission")
async def update_file_permission(
    file_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_files.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {"visibility": body.get("visibility", "public")}},
    )
    return success(None, "权限已更新")


# ─── 资产管理 ──────────────────────────────────────

@router.get("/assets")
async def get_asset_list(
    page: int = 1,
    size: int = 20,
    category: str = "",
    status: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    filter_q = {}
    if category:
        filter_q["category"] = category
    if status:
        filter_q["status"] = status
    total = await db.finance_assets.count_documents(filter_q)
    cursor = db.finance_assets.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for a in cursor:
        records.append(_format_asset(a))
    return success(paginate(records, total, page, size))


@router.post("/assets")
async def create_asset(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = {**body, "createdAt": datetime.now(timezone.utc)}
    result = await db.finance_assets.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "资产已录入")


@router.put("/assets/{asset_id}")
async def update_asset(
    asset_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_assets.update_one({"_id": ObjectId(asset_id)}, {"$set": body})
    return success(None, "资产已更新")


@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_assets.delete_one({"_id": ObjectId(asset_id)})
    return success(None, "资产已删除")


@router.put("/assets/{asset_id}/status")
async def update_asset_status(
    asset_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_assets.update_one(
        {"_id": ObjectId(asset_id)},
        {"$set": {"status": body.get("status", "在用")}},
    )
    return success(None, "资产状态已更新")


@router.get("/assets/{asset_id}/maintenance")
async def get_maintenance_records(
    asset_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    asset = await db.finance_assets.find_one({"_id": ObjectId(asset_id)})
    records = asset.get("maintenance", []) if asset else []
    return success(records)


@router.post("/assets/{asset_id}/maintenance")
async def add_maintenance_record(
    asset_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    record = {
        "type": body.get("type", "维修"),
        "date": body.get("date", ""),
        "description": body.get("description", ""),
        "cost": body.get("cost"),
        "vendor": body.get("vendor", ""),
        "createdAt": datetime.now(timezone.utc),
    }
    await db.finance_assets.update_one(
        {"_id": ObjectId(asset_id)},
        {"$push": {"maintenance": record}},
    )
    return success(None, "维修记录已保存")


# ─── 格式化辅助 ────────────────────────────────────

def _format_file(f: dict) -> dict:
    return {
        "id": str(f["_id"]),
        "name": f.get("name", ""),
        "type": f.get("type", ""),
        "category": f.get("category", "other"),
        "visibility": f.get("visibility", "public"),
        "url": f.get("url", ""),
        "size": f.get("size", ""),
        "uploader": f.get("uploader", ""),
        "uploadTime": f.get("uploadTime", ""),
    }


def _format_asset(a: dict) -> dict:
    return {
        "id": str(a["_id"]),
        "name": a.get("name", ""),
        "category": a.get("category", ""),
        "model": a.get("model", ""),
        "serialNo": a.get("serialNo", ""),
        "department": a.get("department", ""),
        "location": a.get("location", ""),
        "status": a.get("status", "在用"),
        "purchaseDate": a.get("purchaseDate", ""),
        "supplier": a.get("supplier", ""),
        "warrantyExpiry": a.get("warrantyExpiry", ""),
    }


def _format_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / 1024 / 1024:.1f} MB"
