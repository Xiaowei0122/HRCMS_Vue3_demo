"""全局配置路由"""
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, get_optional_user, require_permission
from app.core.response import success

router = APIRouter(prefix="/config", tags=["全局配置"])

_manage = Depends(require_permission("config"))


@router.get("")
async def get_global_config(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict | None = Depends(get_optional_user),
):
    """获取全局配置 — 公开访问（小程序联系我们页面需要，平铺结构）"""
    config = await db.global_config.find_one({"_id": "global"})
    if not config:
        return success({})
    basic = config.get("basic", {})
    contact = config.get("contact", {})
    return success({
        "siteName": basic.get("siteName", "鸿瑞科技"),
        "description": basic.get("seoDescription", ""),
        "servicePhone": contact.get("phone", ""),
        "businessPhone": contact.get("businessPhone", contact.get("phone", "")),
        "address": contact.get("address", ""),
        "businessHours": contact.get("workingHours", ""),
        "qrcode": basic.get("qrcode", ""),
        "lat": str(config.get("map", {}).get("latitude", "")),
        "lng": str(config.get("map", {}).get("longitude", "")),
    })


@router.get("/full")
async def get_full_config(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    """获取完整全局配置（管理端编辑用，结构化返回）"""
    config = await db.global_config.find_one({"_id": "global"})
    if not config:
        return success({})
    config.pop("_id", None)
    return success(config)


@router.put("/basic")
async def save_basic_config(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    await db.global_config.update_one({"_id": "global"}, {"$set": {"basic": body}}, upsert=True)
    return success(None, "基础配置已保存")


# ─── Banner ───────────────────────────────────────

@router.get("/banners")
async def get_banners(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    config = await db.global_config.find_one({"_id": "global"})
    return success(config.get("banners", []) if config else [])


@router.post("/banners")
async def create_banner(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    body["_id"] = str(ObjectId())
    await db.global_config.update_one({"_id": "global"}, {"$push": {"banners": body}}, upsert=True)
    return success(body, "Banner 添加成功")


@router.put("/banners/{banner_id}")
async def update_banner(
    banner_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
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
    user: dict = _manage,
):
    await db.global_config.update_one({"_id": "global"}, {"$pull": {"banners": {"_id": banner_id}}})
    return success(None, "Banner 已删除")


# ─── 联系 / 地图 ───────────────────────────────────

@router.put("/contact")
async def save_contact_config(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    await db.global_config.update_one({"_id": "global"}, {"$set": {"contact": body}}, upsert=True)
    return success(None, "联系配置已保存")


@router.put("/map")
async def save_map_config(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    await db.global_config.update_one({"_id": "global"}, {"$set": {"map": body}}, upsert=True)
    return success(None, "地图配置已保存")


# ─── 服务板块 / 关于（官网内容）────────────────────

@router.get("/services")
async def get_services(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    config = await db.global_config.find_one({"_id": "global"})
    return success(config.get("services", []) if config else [])


@router.put("/services")
async def save_services(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    services = body.get("services", body if isinstance(body, list) else [])
    await db.global_config.update_one({"_id": "global"}, {"$set": {"services": services}}, upsert=True)
    return success(None, "服务板块已保存")


@router.get("/about")
async def get_about(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    config = await db.global_config.find_one({"_id": "global"})
    return success(config.get("about", {}) if config else {})


@router.put("/about")
async def save_about(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    about = body.get("about", body)
    await db.global_config.update_one({"_id": "global"}, {"$set": {"about": about}}, upsert=True)
    return success(None, "关于内容已保存")
