"""认证路由：POST /auth/login  POST /auth/register  GET /auth/userinfo  POST /auth/logout  PUT /auth/password"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, get_optional_user
from app.core.response import success, error
from app.core.security import hash_password
from app.models.user import LoginIn, PasswordChangeIn, ProfileUpdateIn
from app.services.auth_service import authenticate, change_user_password, build_user_info, wechat_authenticate

router = APIRouter(tags=["认证"])


@router.post("/auth/login")
async def login(body: LoginIn, db: AsyncIOMotorDatabase = Depends(get_db)):
    status_, token, user_info = await authenticate(db, body.username, body.password)
    if status_ == "invalid":
        return error(401, "用户名或密码错误")
    if status_ == "pending":
        return error(403, "账号待审批，请等待管理员审核")
    if status_ == "disabled":
        return error(403, "账号已被禁用")
    return success({"token": token, "userInfo": user_info}, "登录成功")


@router.post("/auth/register")
async def register(body: dict, db: AsyncIOMotorDatabase = Depends(get_db)):
    """小程序端注册 — 无需登录"""
    username = body.get("username", "").strip()
    password = body.get("password", "")
    real_name = body.get("realName", username)
    phone = body.get("phone", "")

    if len(username) < 4:
        return error(400, "用户名至少4位")
    if len(password) < 6:
        return error(400, "密码至少6位")

    exists = await db.users.find_one({"username": username})
    if exists:
        return error(400, f"账号 [{username}] 已存在")

    doc = {
        "username": username,
        "realName": real_name,
        "role": "普通用户",
        "roleCode": "normal",
        "phone": phone,
        "hashedPassword": hash_password(password),
        "status": "pending",
        "lastLogin": None,
        "createdAt": datetime.now(timezone.utc),
    }
    await db.users.insert_one(doc)
    return success(None, "注册成功，请等待管理员审批")


@router.post("/auth/wechat-login")
async def wechat_login(body: dict, db: AsyncIOMotorDatabase = Depends(get_db)):
    """微信小程序一键登录 — code 换 openid/unionid，自动注册/登录"""
    code = body.get("code", "").strip()
    if not code:
        return error(400, "缺少微信登录 code")
    nickname = body.get("nickname", "")
    avatar = body.get("avatar", "")

    status_, token, user_info, is_new = await wechat_authenticate(db, code, nickname, avatar)
    if status_ == "no_config":
        return error(503, "微信登录未配置（缺少 appid/secret）")
    if status_ == "wechat_error":
        return error(401, "微信登录失败，请重试")
    if status_ == "disabled":
        return error(403, "账号已被禁用")
    return success({"token": token, "userInfo": user_info, "isNew": is_new}, "登录成功")


@router.post("/auth/logout")
async def logout(user: dict = Depends(get_current_user)):
    return success(None, "已退出登录")


@router.get("/auth/userinfo")
async def get_userinfo(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return success(await build_user_info(user, db))


@router.put("/auth/password")
async def update_password(
    body: PasswordChangeIn,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    ok = await change_user_password(db, str(user["_id"]), body.oldPassword, body.newPassword)
    if not ok:
        return error(400, "旧密码不正确")
    return success(None, "密码修改成功")


@router.put("/auth/profile")
async def update_profile(
    body: ProfileUpdateIn,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """个人中心：更新自己的姓名 / 手机 / 头像"""
    update = {}
    if body.realName is not None:
        update["realName"] = body.realName.strip()
    if body.phone is not None:
        update["phone"] = body.phone.strip()
    if body.avatar is not None:
        update["avatar"] = body.avatar.strip()
    if not update:
        return error(400, "没有需要更新的字段")
    await db.users.update_one({"_id": user["_id"]}, {"$set": update})
    fresh = await db.users.find_one({"_id": user["_id"]})
    return success(await build_user_info(fresh, db), "个人信息已更新")
