"""用户管理路由：GET/POST/PUT/DELETE /users"""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error, paginate
from app.core.security import hash_password
from app.models.user import UserCreate, UserUpdate, UserQuery

router = APIRouter(prefix="/users", tags=["用户管理"])


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
            "phone": u.get("phone", ""),
            "status": u.get("status", True),
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
    doc = {
        "username": body.username,
        "realName": body.realName,
        "role": body.role,
        "phone": body.phone,
        "hashedPassword": hash_password(body.password),
        "status": True,
        "lastLogin": None,
        "createdAt": datetime.now(timezone.utc),
    }
    await db.users.insert_one(doc)
    # 记日志
    await _add_log(db, user, "成员管理", f"新增成员：{body.username}")
    return success(None, "成员创建成功")


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    body: UserUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update_data:
        return error(400, "没有需要更新的字段")
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    if result.matched_count == 0:
        return error(404, "用户不存在")
    await _add_log(db, user, "成员管理", f"更新成员：{user_id}")
    return success(None, "成员信息已更新")


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        return error(404, "用户不存在")
    await _add_log(db, user, "成员管理", f"删除成员：{user_id}")
    return success(None, "删除成功")


@router.patch("/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        return error(404, "用户不存在")
    new_status = not target.get("status", True)
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"status": new_status}})
    await _add_log(db, user, "成员管理", f"{'启用' if new_status else '禁用'}成员：{target['username']}")
    return success(new_status, "状态已更新")


@router.put("/{user_id}/password/reset")
async def reset_user_password(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        return error(404, "用户不存在")
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
