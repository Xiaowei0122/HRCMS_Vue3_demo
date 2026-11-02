"""部门管理路由：组织架构维护 + 业务下拉（资产/用户关联部门）"""
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success, error

router = APIRouter(prefix="/departments", tags=["部门管理"])

_admin = Depends(require_permission("system:depts"))


def _format(d: dict) -> dict:
    return {
        "id": str(d["_id"]),
        "name": d.get("name", ""),
        "parentId": str(d.get("parentId")) if d.get("parentId") else "",
        "leader": d.get("leader", ""),
        "sort": d.get("sort", 0),
    }


@router.get("", dependencies=[_admin])
async def get_dept_list(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """返回部门列表（扁平，含 parentId，前端按需组树）"""
    cursor = db.departments.find({}).sort([("sort", 1), ("_id", 1)])
    records = []
    async for d in cursor:
        records.append(_format(d))
    return success(records)


@router.get("/options")
async def get_dept_options(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """业务下拉读取（登录即可）：[{label, value}]"""
    cursor = db.departments.find({}).sort([("sort", 1), ("_id", 1)])
    records = []
    async for d in cursor:
        name = d.get("name", "")
        records.append({"label": name, "value": name})
    return success(records)


@router.post("", dependencies=[_admin])
async def create_dept(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    name = (body.get("name") or "").strip()
    if not name:
        return error(400, "部门名称不能为空")
    dup = await db.departments.find_one({"name": name})
    if dup:
        return error(400, f"部门 [{name}] 已存在")
    parent_id = body.get("parentId") or None
    if parent_id and not await db.departments.find_one({"_id": ObjectId(parent_id)}):
        return error(400, "上级部门不存在")
    doc = {
        "name": name,
        "parentId": parent_id,
        "leader": (body.get("leader") or "").strip(),
        "sort": body.get("sort", 0),
        "createdAt": datetime.now(timezone.utc),
    }
    result = await db.departments.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "部门已创建")


@router.put("/{dept_id}", dependencies=[_admin])
async def update_dept(
    dept_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    dept = await db.departments.find_one({"_id": ObjectId(dept_id)})
    if not dept:
        return error(404, "部门不存在")
    name = (body.get("name") or "").strip()
    if not name:
        return error(400, "部门名称不能为空")
    parent_id = body.get("parentId") or None
    if parent_id:
        if parent_id == dept_id:
            return error(400, "上级部门不能是自身")
        if not await db.departments.find_one({"_id": ObjectId(parent_id)}):
            return error(400, "上级部门不存在")
    update = {
        "name": name,
        "parentId": parent_id,
        "leader": (body.get("leader") or "").strip(),
        "sort": body.get("sort", 0),
    }
    await db.departments.update_one({"_id": ObjectId(dept_id)}, {"$set": update})
    return success(None, "部门已更新")


@router.delete("/{dept_id}", dependencies=[_admin])
async def delete_dept(
    dept_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    dept = await db.departments.find_one({"_id": ObjectId(dept_id)})
    if not dept:
        return error(404, "部门不存在")
    # 有子部门时禁止删除
    child = await db.departments.find_one({"parentId": dept_id})
    if child:
        return error(400, "该部门下存在子部门，请先删除子部门")
    await db.departments.delete_one({"_id": ObjectId(dept_id)})
    return success(None, "部门已删除")
