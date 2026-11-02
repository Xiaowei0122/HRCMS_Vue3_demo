"""站内通知服务：写入 + 查询/未读/标读（通知失败不影响主流程）"""
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.timeutil import now_cn


async def push_notify(
    db: AsyncIOMotorDatabase,
    *,
    type_: str,
    title: str,
    content: str = "",
    link: str = "",
    role_codes: list[str] | None = None,
    user_ids: list[str] | None = None,
):
    """写入一条站内通知。

    role_codes：目标角色 code 列表（该角色下所有用户可见）；
    user_ids：目标用户 _id 列表（指定用户可见）。二者可同时传。
    """
    try:
        await db.notifications.insert_one({
            "type": type_,
            "title": title,
            "content": content,
            "link": link,
            "roleCodes": role_codes or [],
            "userIds": user_ids or [],
            "readBy": [],
            "createdAt": now_cn(),
        })
    except Exception:
        # 通知失败不影响业务主流程
        pass


async def my_match(user: dict) -> dict:
    """当前用户可见通知的匹配条件：我的用户 id 或我的角色 code 命中即算"""
    uid = str(user.get("_id", ""))
    rc = user.get("roleCode", "")
    return {"$or": [{"userIds": uid}, {"roleCodes": rc}]}


async def list_notifications(db: AsyncIOMotorDatabase, user: dict, limit: int = 20) -> list[dict]:
    uid = str(user.get("_id", ""))
    match = await my_match(user)
    docs = await db.notifications.find(match).sort("createdAt", -1).limit(max(1, min(limit, 50))).to_list(None)
    result = []
    for d in docs:
        created = d.get("createdAt")
        if isinstance(created, datetime):
            created = created.strftime("%Y-%m-%d %H:%M")
        result.append({
            "id": str(d["_id"]),
            "type": d.get("type", ""),
            "title": d.get("title", ""),
            "content": d.get("content", ""),
            "link": d.get("link", ""),
            "read": uid in (d.get("readBy") or []),
            "createdAt": created or "",
        })
    return result


async def unread_count(db: AsyncIOMotorDatabase, user: dict) -> int:
    uid = str(user.get("_id", ""))
    match = await my_match(user)
    match["readBy"] = {"$ne": uid}
    return await db.notifications.count_documents(match)
