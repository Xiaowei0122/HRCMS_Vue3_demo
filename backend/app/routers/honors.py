"""荣誉管理路由"""
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error, paginate

router = APIRouter(prefix="/honors", tags=["荣誉管理"])


@router.get("")
async def get_honor_list(
    page: int = 1,
    size: int = 10,
    type: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if type:
        filter_q["type"] = type
    total = await db.honors.count_documents(filter_q)
    cursor = db.honors.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for h in cursor:
        records.append({"id": str(h["_id"]), "title": h.get("title", ""), "type": h.get("type", ""), "url": h.get("url", ""), "date": h.get("date", "")})
    return success(paginate(records, total, page, size))


@router.post("")
async def create_honor(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.honors.insert_one(body)
    return success({"id": str(result.inserted_id)}, "荣誉创建成功")


@router.put("/{honor_id}")
async def update_honor(
    honor_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.honors.update_one({"_id": ObjectId(honor_id)}, {"$set": body})
    return success(None, "荣誉更新成功")


@router.delete("/{honor_id}")
async def delete_honor(
    honor_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.honors.delete_one({"_id": ObjectId(honor_id)})
    return success(None, "荣誉已删除")
