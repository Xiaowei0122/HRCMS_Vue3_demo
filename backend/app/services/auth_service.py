"""认证服务"""
from datetime import datetime, timezone
import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import verify_password, hash_password, create_access_token
from app.core.deps import resolve_user_role, get_permission_codes
from app.core.config import settings


_TYPE_MAP = {
    "admin": "super_admin",
    "internal": "business",
    "engineer": "engineer",
    "normal": "normal",
    "business": "business",
    "logistics": "logistics",
    "super_admin": "super_admin",
}


def _get_user_type(user: dict) -> str:
    """返回用户角色码（roleCode），旧 userType/role 兜底"""
    code = user.get("roleCode")
    if code:
        return code
    ut = user.get("userType")
    if ut in _TYPE_MAP:
        return _TYPE_MAP[ut]
    role_map = {
        "超级管理员": "super_admin", "管理员": "super_admin",
        "业务": "business", "内部员工": "business",
        "工程师": "engineer",
        "普通用户": "normal", "外部人员": "normal",
        "后勤": "logistics",
    }
    return role_map.get(user.get("role", ""), "normal")


async def build_user_info(user: dict, db: AsyncIOMotorDatabase) -> dict:
    """构造登录态用户信息（含 roleCode + permissions）"""
    role = await resolve_user_role(user, db)
    perms = await get_permission_codes(role, db)
    code = _get_user_type(user)
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "realName": user.get("realName", user["username"]),
        "role": user.get("role", ""),
        "roleCode": code,
        "userType": code,  # 兼容旧前端
        "rank": role.get("rank", 99) if role else 99,
        "permissions": sorted(perms),
        "avatar": user.get("avatar", ""),
        "phone": user.get("phone", ""),
        "lastLogin": user.get("lastLogin", ""),
    }


async def authenticate(db: AsyncIOMotorDatabase, username: str, password: str) -> tuple[str, str, dict]:
    """验证用户。返回 (status, token, userInfo)：
    status: ok / invalid(用户名或密码错) / pending(待审批) / disabled(已停用)
    """
    user = await db.users.find_one({"username": username})
    if not user:
        return ("invalid", "", {})
    if not verify_password(password, user["hashedPassword"]):
        return ("invalid", "", {})

    st = user.get("status")
    if st is True:
        st = "active"
    if st == "pending":
        return ("pending", "", {})
    if st != "active":
        return ("disabled", "", {})

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"lastLogin": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}},
    )

    token = create_access_token({"sub": username})
    user_info = await build_user_info(user, db)
    return ("ok", token, user_info)


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


async def wechat_authenticate(
    db: AsyncIOMotorDatabase,
    code: str,
    nickname: str = "",
    avatar: str = "",
) -> tuple[str, str, dict, bool]:
    """微信小程序一键登录：code → openid/unionid → 自动注册/登录。

    返回 (status, token, userInfo, isNew)。
    status: ok / no_config(未配置 appid) / wechat_error(微信接口失败) / disabled(账号停用)
    """
    if not settings.wechat_appid or not settings.wechat_secret:
        return ("no_config", "", {}, False)

    url = (
        "https://api.weixin.qq.com/sns/jscode2session"
        f"?appid={settings.wechat_appid}"
        f"&secret={settings.wechat_secret}"
        f"&js_code={code}"
        "&grant_type=authorization_code"
    )
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            data = resp.json()
    except Exception:
        return ("wechat_error", "", {}, False)

    if data.get("errcode") or not data.get("openid"):
        return ("wechat_error", "", {}, False)

    openid = data.get("openid", "")
    unionid = data.get("unionid", "")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # 查找已有用户：优先 unionid，回退 openid（兼容旧 openid 注册）
    user = None
    if unionid:
        user = await db.users.find_one({"wxUnionid": unionid})
    if user is None:
        user = await db.users.find_one({"wxOpenid": openid})

    if user:
        st = user.get("status")
        if st is True:
            st = "active"
        if st != "active":
            return ("disabled", "", {}, False)

        updates = {"lastLogin": now}
        if avatar:
            updates["avatar"] = avatar
        if nickname:
            updates["realName"] = nickname
        if unionid and not user.get("wxUnionid"):
            updates["wxUnionid"] = unionid
        if updates:
            await db.users.update_one({"_id": user["_id"]}, {"$set": updates})
            for k, v in updates.items():
                user[k] = v
        token = create_access_token({"sub": user["username"]})
        user_info = await build_user_info(user, db)
        return ("ok", token, user_info, False)

    # 新用户：自动注册（免审批，默认 normal 角色）
    username = "wx_" + (unionid or openid)
    base = username
    idx = 1
    while await db.users.find_one({"username": username}):
        username = f"{base}_{idx}"
        idx += 1

    doc = {
        "username": username,
        "realName": nickname or "微信用户",
        "role": "普通用户",
        "roleCode": "normal",
        "phone": "",
        "hashedPassword": "",
        "wxOpenid": openid,
        "wxUnionid": unionid,
        "avatar": avatar,
        "status": "active",
        "lastLogin": now,
        "createdAt": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    token = create_access_token({"sub": username})
    user_info = await build_user_info(doc, db)
    return ("ok", token, user_info, True)
