"""认证服务"""
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import verify_password, hash_password, create_access_token


async def authenticate(db: AsyncIOMotorDatabase, username: str, password: str) -> tuple[str, dict] | None:
    """验证用户，成功返回 (token, userInfo)，失败返回 None"""
    user = await db.users.find_one({"username": username})
    if not user:
        return None
    if not verify_password(password, user["hashedPassword"]):
        return None
    if not user.get("status", True):
        return None

    # 更新最后登录时间
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"lastLogin": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}},
    )

    token = create_access_token({"sub": username})
    user_info = {
        "id": str(user["_id"]),
        "username": user["username"],
        "realName": user.get("realName", user["username"]),
        "role": user.get("role", ""),
        "avatar": user.get("avatar", ""),
        "phone": user.get("phone", ""),
    }
    return token, user_info


async def change_user_password(db: AsyncIOMotorDatabase, user_id: str, old_pw: str, new_pw: str) -> bool:
    from bson import ObjectId
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False
    if not verify_password(old_pw, user["hashedPassword"]):
        return False
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashedPassword": hash_password(new_pw)}},
    )
    return True
