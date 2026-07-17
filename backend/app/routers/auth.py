"""认证路由：POST /auth/login  POST /auth/register  GET /auth/userinfo  POST /auth/logout  PUT /auth/password"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, get_optional_user
from app.core.response import success, error
from app.core.security import hash_password
from app.models.user import LoginIn, PasswordChangeIn
from app.services.auth_service import authenticate, change_user_password, _get_user_type

router = APIRouter(tags=["认证"])


@router.post("/auth/login")
async def login(body: LoginIn, db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await authenticate(db, body.username, body.password)
    if not result:
        return error(401, "用户名或密码错误")
    token, user_info = result
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
        "role": "",
        "userType": "normal",
        "phone": phone,
        "hashedPassword": hash_password(password),
        "status": True,
        "lastLogin": None,
        "createdAt": datetime.now(timezone.utc),
    }
    await db.users.insert_one(doc)
    # 注册成功直接返回登录态
    token, user_info = await authenticate(db, username, password)
    return success({"token": token, "userInfo": user_info}, "注册成功")


@router.post("/auth/logout")
async def logout(user: dict = Depends(get_current_user)):
    return success(None, "已退出登录")


@router.get("/auth/userinfo")
async def get_userinfo(user: dict = Depends(get_current_user)):
    info = {
        "id": str(user["_id"]),
        "username": user["username"],
        "realName": user.get("realName", user["username"]),
        "role": user.get("role", ""),
        "userType": user.get("userType") or _get_user_type(user),
        "avatar": user.get("avatar", ""),
        "phone": user.get("phone", ""),
    }
    return success(info)


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
