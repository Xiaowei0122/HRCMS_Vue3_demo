"""投诉管理路由"""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error, paginate

router = APIRouter(prefix="/complaints", tags=["投诉管理"])


@router.get("")
async def get_complaint_list(
    page: int = 1,
    size: int = 10,
    status: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if status:
        filter_q["status"] = status
    total = await db.complaints.count_documents(filter_q)
    cursor = db.complaints.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for c in cursor:
        records.append({
            "id": str(c["_id"]),
            "date": c.get("date", ""),
            "customer": c.get("customer", ""),
            "target": c.get("target", ""),
            "category": c.get("category", ""),
            "priority": c.get("priority", "普通"),
            "status": c.get("status", "待处理"),
            "content": c.get("content", ""),
            "result": c.get("result", ""),
        })
    return success(paginate(records, total, page, size))


@router.get("/stats")
async def get_complaint_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
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
    user: dict = Depends(get_current_user),
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
    user: dict = Depends(get_current_user),
):
    result_text = body.get("result", "") if body else ""
    await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"status": "已解决", "result": result_text}},
    )
    return success(None, "投诉已关闭")
