"""品牌管理路由"""
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error, paginate

router = APIRouter(prefix="/brands", tags=["品牌管理"])


@router.get("")
async def get_brand_list(
    page: int = 1,
    size: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    total = await db.brands.count_documents({})
    cursor = db.brands.find({}).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for b in cursor:
        records.append({"id": str(b["_id"]), "name": b.get("name", ""), "logo": b.get("logo", ""), "level": b.get("level", ""), "url": b.get("url", "")})
    return success(paginate(records, total, page, size))


@router.post("")
async def create_brand(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.brands.insert_one(body)
    return success({"id": str(result.inserted_id)}, "品牌创建成功")


@router.put("/{brand_id}")
async def update_brand(
    brand_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.brands.update_one({"_id": ObjectId(brand_id)}, {"$set": body})
    return success(None, "品牌更新成功")


@router.delete("/{brand_id}")
async def delete_brand(
    brand_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.brands.delete_one({"_id": ObjectId(brand_id)})
    return success(None, "品牌已删除")
