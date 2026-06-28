"""认证路由：POST /auth/login  GET /auth/userinfo  POST /auth/logout  PUT /auth/password"""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error
from app.models.user import LoginIn, PasswordChangeIn
from app.services.auth_service import authenticate, change_user_password

router = APIRouter(tags=["认证"])


@router.post("/auth/login")
async def login(body: LoginIn, db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await authenticate(db, body.username, body.password)
    if not result:
        return error(401, "用户名或密码错误")
    token, user_info = result
    return success({"token": token, "userInfo": user_info}, "登录成功")


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
