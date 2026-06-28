"""案例管理路由（归属于 /cases）和品牌路由的补充"""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error, paginate

router = APIRouter(prefix="/cases", tags=["案例管理"])


@router.get("")
async def get_case_list(
    page: int = 1,
    size: int = 10,
    industry: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if industry:
        filter_q["industry"] = {"$regex": industry, "$options": "i"}
    total = await db.cases.count_documents(filter_q)
    cursor = db.cases.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for c in cursor:
        records.append({
            "id": str(c["_id"]),
            "client": c.get("client", ""),
            "industry": c.get("industry", ""),
            "device": c.get("device", ""),
            "mode": c.get("mode", ""),
            "summary": c.get("summary", ""),
            "date": c.get("date", ""),
        })
    return success(paginate(records, total, page, size))


@router.post("")
async def create_case(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    body.setdefault("createdAt", datetime.now(timezone.utc))
    result = await db.cases.insert_one(body)
    return success({"id": str(result.inserted_id)}, "案例创建成功")


@router.put("/{case_id}")
async def update_case(
    case_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.cases.update_one({"_id": ObjectId(case_id)}, {"$set": body})
    return success(None, "案例更新成功")


@router.delete("/{case_id}")
async def delete_case(
    case_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.cases.delete_one({"_id": ObjectId(case_id)})
    return success(None, "案例已删除")
