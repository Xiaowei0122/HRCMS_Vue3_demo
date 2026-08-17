"""投诉管理路由"""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_user_types
from app.core.response import success, error, paginate

router = APIRouter(prefix="/complaints", tags=["投诉管理"])

_manage = Depends(require_user_types("admin", "internal"))


@router.get("")
async def get_complaint_list(
    page: int = 1,
    size: int = 10,
    status: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    filter_q = {}
    if status:
        filter_q["status"] = status
    total = await db.complaints.count_documents(filter_q)
    cursor = db.complaints.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for c in cursor:
        records.append(_fmt(c))
    return success(paginate(records, total, page, size))


@router.get("/my")
async def get_my_complaints(
    page: int = 1,
    size: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """我的投诉 — 按创建人筛选"""
    uname = user.get("username", "")
    filter_q = {"createdBy": uname}
    total = await db.complaints.count_documents(filter_q)
    cursor = db.complaints.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for c in cursor:
        records.append(_fmt(c))
    return success(paginate(records, total, page, size))


@router.post("")
async def create_complaint(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """提交投诉建议"""
    doc = {
        "type": body.get("type", ""),
        "title": body.get("title", ""),
        "content": body.get("content", ""),
        "contact": body.get("contact", ""),
        "priority": body.get("priority", "普通"),
        "target": body.get("target", ""),
        "status": "待处理",
        "reply": "",
        "createTime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "createdBy": user.get("username", ""),
        "customer": user.get("realName", user.get("username", "")),
    }
    result = await db.complaints.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "投诉提交成功")


@router.get("/stats")
async def get_complaint_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    return success({
        "total": await db.complaints.count_documents({}),
        "pending": await db.complaints.count_documents({"status": "待处理"}),
        "processing": await db.complaints.count_documents({"status": "处理中"}),
        "resolved": await db.complaints.count_documents({"status": "已解决"}),
    })


@router.put("/{complaint_id}/process")
async def process_complaint(
    complaint_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    update = {"status": "处理中"}
    if body.get("result"):
        update["result"] = body["result"]
    await db.complaints.update_one({"_id": ObjectId(complaint_id)}, {"$set": update})
    return success(None, "投诉已开始处理")


@router.patch("/{complaint_id}/close")
async def close_complaint(
    complaint_id: str,
    body: dict | None = Body(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    result_text = body.get("result", "") if body else ""
    await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"status": "已解决", "result": result_text}},
    )
    return success(None, "投诉已关闭")


def _fmt(c: dict) -> dict:
    return {
        "id": str(c["_id"]),
        "type": c.get("type", c.get("category", "")),
        "title": c.get("title", c.get("content", "")),
        "content": c.get("content", ""),
        "contact": c.get("contact", ""),
        "customer": c.get("customer", c.get("contact", "")),
        "target": c.get("target", ""),
        "category": c.get("category", c.get("type", "")),
        "priority": c.get("priority", "普通"),
        "status": c.get("status", "待处理"),
        "reply": c.get("reply", c.get("result", "")),
        "result": c.get("result", c.get("reply", "")),
        "createTime": c.get("createTime", c.get("date", "")),
        "createdBy": c.get("createdBy", ""),
    }

