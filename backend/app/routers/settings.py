"""系统设置路由：对内系统配置（系统名称/logo、登录策略、审批开关、密码策略、通知开关、数据保留）"""
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success

router = APIRouter(prefix="/system/settings", tags=["系统设置"])

_admin = Depends(require_permission("system:settings"))

_DEFAULTS = {
    "siteName": "鸿瑞办公CMS",
    "logo": "",
    "loginStrategy": "password",
    "approvalSwitch": False,
    "notificationSwitch": True,
    "passwordPolicy": {"minLength": 6, "expireDays": 0},
    "dataRetention": {"repairDays": 365, "logDays": 180},
}


def _format(doc: dict | None) -> dict:
    if not doc:
        return dict(_DEFAULTS)
    return {
        "siteName": doc.get("siteName", _DEFAULTS["siteName"]),
        "logo": doc.get("logo", ""),
        "loginStrategy": doc.get("loginStrategy", "password"),
        "approvalSwitch": doc.get("approvalSwitch", False),
        "notificationSwitch": doc.get("notificationSwitch", True),
        "passwordPolicy": doc.get("passwordPolicy", _DEFAULTS["passwordPolicy"]),
        "dataRetention": doc.get("dataRetention", _DEFAULTS["dataRetention"]),
        "updatedAt": _fmt(doc.get("updatedAt")),
    }


def _fmt(dt) -> str:
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


@router.get("", dependencies=[_admin])
async def get_system_settings(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    doc = await db.system_settings.find_one({"_id": "system"})
    return success(_format(doc))


@router.put("", dependencies=[_admin])
async def update_system_settings(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    allowed = {
        "siteName": str(body.get("siteName", _DEFAULTS["siteName"])).strip() or _DEFAULTS["siteName"],
        "logo": body.get("logo", ""),
        "loginStrategy": body.get("loginStrategy", "password"),
        "approvalSwitch": bool(body.get("approvalSwitch", False)),
        "notificationSwitch": bool(body.get("notificationSwitch", True)),
        "passwordPolicy": body.get("passwordPolicy", _DEFAULTS["passwordPolicy"]),
        "dataRetention": body.get("dataRetention", _DEFAULTS["dataRetention"]),
        "updatedAt": datetime.now(timezone.utc),
    }
    await db.system_settings.update_one({"_id": "system"}, {"$set": allowed}, upsert=True)
    return success(None, "系统设置已保存")
