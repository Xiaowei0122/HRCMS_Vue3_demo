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

    st = user.get("status")
    if st is True:
        st = "active"  # 旧布尔兼容
    if st != "active":
        if st == "pending":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号待审批，请等待管理员审核")
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


# ─── RBAC（动态权限引擎）──────────────────────────

_LEGACY_ROLE_CODE_MAP = {
    "admin": "super_admin",
    "internal": "business",
    "engineer": "engineer",
    "normal": "normal",
    "business": "business",
    "logistics": "logistics",
    "super_admin": "super_admin",
}


def _resolve_role_code(user: dict) -> str:
    """返回用户角色码：优先 roleCode，其次 userType/role 中文名兜底"""
    code = user.get("roleCode")
    if code:
        return code
    ut = user.get("userType")
    if ut in _LEGACY_ROLE_CODE_MAP:
        return _LEGACY_ROLE_CODE_MAP[ut]
    role_map = {
        "超级管理员": "super_admin", "管理员": "super_admin",
        "业务": "business", "内部员工": "business",
        "工程师": "engineer",
        "普通用户": "normal", "外部人员": "normal",
        "后勤": "logistics",
    }
    return role_map.get(user.get("role", ""), "normal")


async def resolve_user_role(user: dict, db: AsyncIOMotorDatabase) -> dict | None:
    """按 roleCode 解析用户角色；无则返回 None（视为无权限）"""
    code = _resolve_role_code(user)
    return await db.roles.find_one({"code": code})


async def get_user_rank(user: dict, db: AsyncIOMotorDatabase) -> int:
    """返回用户角色 rank（越小越高）；无角色返回 99"""
    role = await resolve_user_role(user, db)
    return role.get("rank", 99) if role else 99


async def get_permission_codes(role: dict | None, db: AsyncIOMotorDatabase) -> set[str]:
    """把角色 permissionIds 直接映射为权限 code 集合（每个 id 独立授权）"""
    if not role:
        return set()
    ids = role.get("permissionIds") or []
    if not ids:
        return set()
    id_to_code = {}
    async for d in db.permissions.find({}):
        id_to_code[d["_id"]] = d["code"]
        for c in d.get("children", []):
            id_to_code[c["_id"]] = c["code"]
    return {id_to_code[pid] for pid in ids if pid in id_to_code}


def require_permission(*codes: str):
    """RBAC 守卫：当前用户拥有任一指定权限 code 即放行；super_admin 直接放行"""
    async def checker(
        user: dict = Depends(get_current_user),
        db: AsyncIOMotorDatabase = Depends(get_db),
    ) -> dict:
        if _resolve_role_code(user) == "super_admin":
            return user
        role = await resolve_user_role(user, db)
        perms = await get_permission_codes(role, db)
        if not any(c in perms for c in codes):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有操作权限")
        return user
    return checker


async def can_assign_role(caller: dict, target_role: dict | None, db: AsyncIOMotorDatabase) -> bool:
    """caller 能否给他人分配 target_role：超管(rank 0)可分配任意；否则只能分配 rank 严格更大的角色"""
    if target_role is None:
        return False
    caller_rank = await get_user_rank(caller, db)
    if caller_rank == 0:
        return True
    return target_role.get("rank", 99) > caller_rank
