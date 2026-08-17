"""认证服务"""
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import verify_password, hash_password, create_access_token


def _get_user_type(user: dict) -> str:
    """从用户 role 推导小程序端 userType
    角色 → userType 映射：
      管理员     → admin       (最高权限，CMS 全部可见)
      工程师     → engineer    (售后报修模块)
      内部员工   → internal    (内部业务模块)
      外部人员   → normal      (受限：报修 + 查看)
      旧版兼容   → 按 role 名模糊映射
    """
    role = user.get("role", "")
    # 新角色体系直映射
    mapping = {
        "管理员": "admin",
        "工程师": "engineer",
        "内部员工": "internal",
        "外部人员": "normal",
    }
    if role in mapping:
        return mapping[role]
    # 旧版兼容
    if role == "超级管理员":
        return "admin"
    if role == "技术支持":
        return "engineer"
    if role in ("销售主管", "财务经理"):
        return "internal"
    return "normal"


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
        "userType": user.get("userType") or _get_user_type(user),
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
