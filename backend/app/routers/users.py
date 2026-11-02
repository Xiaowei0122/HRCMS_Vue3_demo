"""用户管理路由：GET/POST/PUT/DELETE /users + 审批/驳回"""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission, resolve_user_role, can_assign_role
from app.core.response import success, error, paginate
from app.core.security import hash_password
from app.models.user import UserCreate, UserUpdate
from app.services import notify

router = APIRouter(prefix="/users", tags=["用户管理"], dependencies=[Depends(require_permission("system:users"))])


async def _role_by_code(db: AsyncIOMotorDatabase, code: str) -> dict | None:
    if not code:
        return None
    return await db.roles.find_one({"code": code})


async def _can_manage_target(db: AsyncIOMotorDatabase, caller: dict, target: dict) -> bool:
    """caller 能否管理 target：超管可管理任意；否则只能管理 rank 严格更大的目标"""
    caller_role = await resolve_user_role(caller, db)
    caller_rank = caller_role.get("rank", 99) if caller_role else 99
    if caller_rank == 0:
        return True
    target_role = await resolve_user_role(target, db)
    target_rank = target_role.get("rank", 99) if target_role else 99
    return target_rank > caller_rank


def _is_super_admin(target: dict) -> bool:
    """是否为超级管理员账号（不可删除/停用/降级）"""
    return target.get("roleCode") == "super_admin"


@router.get("")
async def get_user_list(
    name: str = "",
    page: int = 1,
    size: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if name:
        filter_q["$or"] = [
            {"username": {"$regex": name, "$options": "i"}},
            {"realName": {"$regex": name, "$options": "i"}},
        ]
    total = await db.users.count_documents(filter_q)
    cursor = db.users.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for u in cursor:
        records.append({
            "id": str(u["_id"]),
            "username": u["username"],
            "realName": u.get("realName", ""),
            "role": u.get("role", ""),
            "roleCode": u.get("roleCode", ""),
            "phone": u.get("phone", ""),
            "status": u.get("status", "active"),
            "lastLogin": u.get("lastLogin", ""),
        })
    return success(paginate(records, total, page, size))


@router.post("")
async def create_user(
    body: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    exists = await db.users.find_one({"username": body.username})
    if exists:
        return error(400, f"账号 [{body.username}] 已存在")

    role = await _role_by_code(db, body.roleCode)
    if role is None:
        return error(400, "请选择有效角色")
    if not await can_assign_role(user, role, db):
        return error(403, "无权分配该角色")

    doc = {
        "username": body.username,
        "realName": body.realName,
        "role": role["roleName"],
        "roleCode": role["code"],
        "phone": body.phone,
        "hashedPassword": hash_password(body.password),
        "status": "active",
        "lastLogin": None,
        "createdAt": datetime.now(timezone.utc),
    }
    await db.users.insert_one(doc)
    await _add_log(db, user, "成员管理", f"新增成员：{body.username}")
    return success(None, "成员创建成功")


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    body: UserUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        return error(404, "用户不存在")
    if not await _can_manage_target(db, user, target):
        return error(403, "无权操作该成员")

    update_data = {}
    if body.roleCode is not None:
        if _is_super_admin(target) and body.roleCode != "super_admin":
            return error(403, "超级管理员账号的角色不可修改")
        role = await _role_by_code(db, body.roleCode)
        if role is None:
            return error(400, "请选择有效角色")
        if not await can_assign_role(user, role, db):
            return error(403, "无权分配该角色")
        update_data["roleCode"] = role["code"]
        update_data["role"] = role["roleName"]
    if body.realName is not None:
        update_data["realName"] = body.realName
    if body.phone is not None:
        update_data["phone"] = body.phone

    if not update_data:
        return error(400, "没有需要更新的字段")
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    await _add_log(db, user, "成员管理", f"更新成员：{user_id}")
    return success(None, "成员信息已更新")


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        return error(404, "用户不存在")
    if not await _can_manage_target(db, user, target):
        return error(403, "无权操作该成员")
    if _is_super_admin(target):
        return error(403, "超级管理员账号不可删除")
    await db.users.delete_one({"_id": ObjectId(user_id)})
    await _add_log(db, user, "成员管理", f"删除成员：{user_id}")
    return success(None, "删除成功")


@router.patch("/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """启用/停用（active ↔ disabled）"""
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        return error(404, "用户不存在")
    if not await _can_manage_target(db, user, target):
        return error(403, "无权操作该成员")
    if _is_super_admin(target):
        return error(403, "超级管理员账号不可停用")
    cur = target.get("status")
    if cur is True:
        cur = "active"
    new_status = "disabled" if cur == "active" else "active"
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"status": new_status}})
    await _add_log(db, user, "成员管理", f"{'启用' if new_status == 'active' else '停用'}成员：{target['username']}")
    return success(new_status, "状态已更新")


@router.patch("/{user_id}/approve")
async def approve_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """审批通过（pending → active）"""
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        return error(404, "用户不存在")
    if not await _can_manage_target(db, user, target):
        return error(403, "无权操作该成员")
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"status": "active"}})
    await _add_log(db, user, "成员管理", f"审批通过成员：{target['username']}")
    await notify.push_notify(
        db,
        type_="user_approved",
        title="账号审批通过",
        content=f"你的账号 [{target.get('username')}] 已通过审批，现在可以登录系统",
        link="/dashboard",
        user_ids=[str(target["_id"])],
    )
    return success(None, "已审批通过")


@router.patch("/{user_id}/reject")
async def reject_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """审批驳回（pending → disabled）"""
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        return error(404, "用户不存在")
    if not await _can_manage_target(db, user, target):
        return error(403, "无权操作该成员")
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"status": "disabled"}})
    await _add_log(db, user, "成员管理", f"审批驳回成员：{target['username']}")
    await notify.push_notify(
        db,
        type_="user_rejected",
        title="账号审批未通过",
        content=f"你的账号 [{target.get('username')}] 审批未通过，请联系管理员",
        link="",
        user_ids=[str(target["_id"])],
    )
    return success(None, "已驳回")


@router.put("/{user_id}/password/reset")
async def reset_user_password(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        return error(404, "用户不存在")
    if not await _can_manage_target(db, user, target):
        return error(403, "无权操作该成员")
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashedPassword": hash_password("123456")}},
    )
    await _add_log(db, user, "成员管理", f"重置成员密码：{target['username']}")
    return success(None, "密码已重置为 123456")


async def _add_log(db: AsyncIOMotorDatabase, user: dict, module: str, content: str, result: str = "成功"):
    from datetime import datetime, timezone
    await db.logs.insert_one({
        "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "user": user.get("username", "unknown"),
        "module": module,
        "content": content,
        "ip": "127.0.0.1",
        "result": result,
    })
