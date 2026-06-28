"""全局配置路由"""
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success

router = APIRouter(prefix="/config", tags=["全局配置"])


@router.get("")
async def get_global_config(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    config = await db.global_config.find_one({"_id": "global"})
    if not config:
        return success({})
    return success({
        "basic": config.get("basic", {}),
        "banners": config.get("banners", []),
        "contact": config.get("contact", {}),
        "map": config.get("map", {}),
    })


@router.put("/basic")
async def save_basic_config(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.global_config.update_one({"_id": "global"}, {"$set": {"basic": body}}, upsert=True)
    return success(None, "基础配置已保存")


@router.get("/banners")
async def get_banners(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    config = await db.global_config.find_one({"_id": "global"})
    return success(config.get("banners", []) if config else [])


@router.post("/banners")
async def create_banner(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    body["_id"] = str(ObjectId())
    await db.global_config.update_one({"_id": "global"}, {"$push": {"banners": body}}, upsert=True)
    return success(body, "Banner 添加成功")


@router.put("/banners/{banner_id}")
async def update_banner(
    banner_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.global_config.update_one(
        {"_id": "global", "banners._id": banner_id},
        {"$set": {f"banners.$": {**body, "_id": banner_id}}},
    )
    return success(None, "Banner 更新成功")


@router.delete("/banners/{banner_id}")
async def delete_banner(
    banner_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.global_config.update_one({"_id": "global"}, {"$pull": {"banners": {"_id": banner_id}}})
    return success(None, "Banner 已删除")


@router.put("/contact")
async def save_contact_config(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.global_config.update_one({"_id": "global"}, {"$set": {"contact": body}}, upsert=True)
    return success(None, "联系配置已保存")


@router.put("/map")
async def save_map_config(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.global_config.update_one({"_id": "global"}, {"$set": {"map": body}}, upsert=True)
    return success(None, "地图配置已保存")
