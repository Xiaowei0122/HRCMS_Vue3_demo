"""联系我们 — 工程师管理（用于对外展示）"""
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error, paginate

router = APIRouter(prefix="/contact", tags=["联系我们"])


@router.get("/engineers")
async def get_contact_engineers(
    page: int = 1,
    size: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    total = await db.engineers.count_documents({"showOnMobile": True})
    cursor = db.engineers.find({"showOnMobile": True}).skip((page - 1) * size).limit(size)
    records = []
    async for e in cursor:
        records.append({
            "id": str(e["_id"]),
            "name": e.get("name", ""),
            "phone": e.get("phone", ""),
            "avatar": e.get("avatar", ""),
            "skills": e.get("skills", []),
            "desc": e.get("desc", ""),
        })
    return success(paginate(records, total, page, size))


@router.post("/engineers")
async def create_contact_engineer(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.engineers.insert_one({**body, "showOnMobile": True})
    return success({"id": str(result.inserted_id)}, "工程师创建成功")


@router.put("/engineers/{eng_id}")
async def update_contact_engineer(
    eng_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.engineers.update_one({"_id": ObjectId(eng_id)}, {"$set": body})
    return success(None, "工程师信息已更新")


@router.delete("/engineers/{eng_id}")
async def delete_contact_engineer(
    eng_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.engineers.delete_one({"_id": ObjectId(eng_id)})
    return success(None, "工程师已删除")
