"""角色管理路由：GET/POST/PUT/DELETE /roles, GET /permissions/tree, PUT /roles/{id}/permissions"""
from bson import ObjectId
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error
from app.models.role import RoleCreate, RoleUpdate, PermSaveIn

router = APIRouter(tags=["角色管理"])


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
    doc = {"roleName": body.roleName, "code": body.code, "permissionIds": []}
    await db.roles.insert_one(doc)
    return success(None, "角色创建成功")


@router.put("/roles/{role_id}")
async def update_role(
    role_id: str,
    body: RoleUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update_data:
        return error(400, "没有需要更新的字段")
    await db.roles.update_one({"_id": ObjectId(role_id)}, {"$set": update_data})
    return success(None, "角色已更新")


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
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
    await db.roles.update_one(
        {"_id": ObjectId(role_id)},
        {"$set": {"permissionIds": body.permissionIds}},
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
