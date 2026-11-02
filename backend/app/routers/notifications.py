"""站内通知路由：GET /notifications  GET /notifications/unread-count  POST /notifications/read"""
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success
from app.services import notify

router = APIRouter(prefix="/notifications", tags=["站内通知"])


@router.get("")
async def get_notifications(
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """我的通知列表（按角色或按用户命中）"""
    return success(await notify.list_notifications(db, user, limit))


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return success({"count": await notify.unread_count(db, user)})


@router.post("/read")
async def mark_read(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """标记已读：body 传 { id } 单条，或 { all: true } 全部"""
    uid = str(user.get("_id", ""))
    if body.get("all"):
        match = await notify.my_match(user)
        await db.notifications.update_many(match, {"$addToSet": {"readBy": uid}})
    elif body.get("id"):
        await db.notifications.update_one(
            {"_id": ObjectId(body["id"])},
            {"$addToSet": {"readBy": uid}},
        )
    return success(None, "已读")
