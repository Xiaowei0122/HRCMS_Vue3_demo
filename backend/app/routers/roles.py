"""角色管理路由：GET/POST/PUT/DELETE /roles, GET /permissions/tree, PUT /roles/{id}/permissions"""
from bson import ObjectId
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success, error
from app.models.role import RoleCreate, RoleUpdate, PermSaveIn

router = APIRouter(tags=["角色管理"], dependencies=[Depends(require_permission("system:roles"))])


@router.get("/roles")
async def get_role_list(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    cursor = db.roles.find().sort("_id", 1)
    records = []
    async for r in cursor:
        records.append({
            "id": str(r["_id"]),
            "roleName": r["roleName"],
            "code": r["code"],
            "rank": r.get("rank", 2),
            "builtin": r.get("builtin", False),
            "permissions": r.get("permissionIds", []),
        })
    return success(records)


@router.post("/roles")
async def create_role(
    body: RoleCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    exists = await db.roles.find_one({"code": body.code})
    if exists:
        return error(400, f"角色标识 [{body.code}] 已存在")
    if body.rank in (0, 1):
        return error(403, "超级管理员与管理员为内置角色，不可新增")
    doc = {"roleName": body.roleName, "code": body.code, "rank": body.rank, "builtin": False, "permissionIds": []}
    await db.roles.insert_one(doc)
    return success(None, "角色创建成功")


@router.put("/roles/{role_id}")
async def update_role(
    role_id: str,
    body: RoleUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    role = await db.roles.find_one({"_id": ObjectId(role_id)})
    if not role:
        return error(404, "角色不存在")
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update_data:
        return error(400, "没有需要更新的字段")
    # 内置角色 code 不可改
    if role.get("builtin") and "code" in update_data and update_data["code"] != role["code"]:
        return error(403, "内置角色的标识不可修改")
    # 超级管理员不可降级，防止失去管理权限
    if role.get("code") == "super_admin" and "rank" in update_data and update_data["rank"] != 0:
        return error(403, "超级管理员的层级不可修改")
    # 非内置角色不可提升为超级管理员/管理员（0/1 为内置层级）
    if "rank" in update_data and update_data["rank"] in (0, 1) and not role.get("builtin"):
        return error(403, "超级管理员与管理员为内置层级，不可分配")
    await db.roles.update_one({"_id": ObjectId(role_id)}, {"$set": update_data})
    return success(None, "角色已更新")


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    role = await db.roles.find_one({"_id": ObjectId(role_id)})
    if not role:
        return error(404, "角色不存在")
    if role.get("builtin"):
        return error(403, "内置角色不可删除")
    await db.roles.delete_one({"_id": ObjectId(role_id)})
    return success(None, "角色已删除")


@router.get("/roles/{role_id}/permissions")
async def get_role_permissions(
    role_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    role = await db.roles.find_one({"_id": ObjectId(role_id)})
    if not role:
        return error(404, "角色不存在")
    return success(role.get("permissionIds", []))


@router.put("/roles/{role_id}/permissions")
async def save_role_permissions(
    role_id: str,
    body: PermSaveIn,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    role = await db.roles.find_one({"_id": ObjectId(role_id)})
    if not role:
        return error(404, "角色不存在")
    if role.get("code") == "super_admin" or role.get("rank") == 0:
        return error(403, "超级管理员的权限不可修改，防止误操作导致无法登录后台")

    # 后端兜底：过滤父分组 id（仅树分组，不直接授权），只存叶子权限
    parent_ids = set()
    cursor = db.permissions.find({"children": {"$exists": True}})
    async for p in cursor:
        if p.get("children"):
            parent_ids.add(p["_id"])
    leaf_ids = [pid for pid in body.permissionIds if pid not in parent_ids]
    await db.roles.update_one(
        {"_id": ObjectId(role_id)},
        {"$set": {"permissionIds": leaf_ids}},
    )
    return success(None, "权限保存成功")


@router.get("/permissions/tree")
async def get_permission_tree(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """返回权限树"""
    cursor = db.permissions.find({"parentId": None}).sort("sort", 1)
    tree = []
    async for perm in cursor:
        node = {
            "id": perm["_id"],
            "label": perm["label"],
            "code": perm["code"],
            "icon": perm.get("icon", ""),
            "children": _build_children(perm),
        }
        tree.append(node)
    return success(tree)


def _build_children(perm: dict) -> list:
    children = perm.get("children", [])
    result = []
    for child in children:
        result.append({
            "id": child["_id"],
            "label": child["label"],
            "code": child["code"],
            "children": child.get("children", []),
        })
    return result
