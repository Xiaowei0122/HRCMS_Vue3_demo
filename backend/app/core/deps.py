"""FastAPI 依赖注入"""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from .config import settings
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/auth/login", auto_error=False)


async def get_db(request: Request) -> AsyncIOMotorDatabase:
    """获取当前请求对应的数据库实例"""
    return request.app.state.db


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    """JWT 守卫：解析 token，返回当前用户；无效则 401"""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已过期，请重新登录")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌")

    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

    if not user.get("status", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")

    return user


async def get_optional_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict | None:
    """可选认证：有 token 且有效则返回用户，否则返回 None"""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    username = payload.get("sub")
    if not username:
        return None
    user = await db.users.find_one({"username": username})
    return user if user else None


# ─── RBAC ──────────────────────────────────────────

_ROLE_TYPE_MAP = {
    "管理员": "admin",
    "工程师": "engineer",
    "内部员工": "internal",
    "外部人员": "normal",
    "超级管理员": "admin",
    "技术支持": "engineer",
    "销售主管": "internal",
    "财务经理": "internal",
}


def resolve_user_type(user: dict) -> str:
    """返回用户的 userType（缺失时按中文角色名兜底映射）"""
    return user.get("userType") or _ROLE_TYPE_MAP.get(user.get("role", ""), "normal")


def require_user_types(*allowed_types: str):
    """RBAC 守卫：校验当前用户 userType 属于允许列表，否则 403"""
    async def checker(user: dict = Depends(get_current_user)) -> dict:
        if resolve_user_type(user) not in allowed_types:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有操作权限")
        return user
    return checker
