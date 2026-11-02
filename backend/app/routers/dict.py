"""数据字典路由：集中维护业务枚举（分类 / 部门 / 优先级 / 工单类型 等）

- 管理接口（GET/POST/PUT/DELETE）需 system:dict 权限。
- GET /dict/options 仅需登录，供业务页下拉框读取（后续下拉统一改从字典读）。
"""
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success, error
from app.models.common import DictItemIn

router = APIRouter(prefix="/dict", tags=["数据字典"])


def _format(item: dict) -> dict:
    return {
        "id": str(item["_id"]),
        "type": item.get("type", ""),
        "label": item.get("label", ""),
        "value": item.get("value", "") or item.get("label", ""),
        "sort": item.get("sort", 0),
        "enabled": item.get("enabled", True),
    }


@router.get("/types", dependencies=[Depends(require_permission("system:dict"))])
async def get_dict_types(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """返回所有字典分组（type）及其条目数"""
    types = await db.dict_items.distinct("type")
    result = []
    for t in types:
        count = await db.dict_items.count_documents({"type": t})
        result.append({"type": t, "count": count})
    # 按条目数降序，稳定的可读顺序
    result.sort(key=lambda x: (-x["count"], x["type"]))
    return success(result)


@router.get("/items", dependencies=[Depends(require_permission("system:dict"))])
async def get_dict_items(
    type: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """返回某分组下的字典项（按 sort 升序）"""
    filter_q = {"type": type} if type else {}
    cursor = db.dict_items.find(filter_q).sort([("sort", 1), ("_id", 1)])
    records = []
    async for item in cursor:
        records.append(_format(item))
    return success(records)


@router.post("/items", dependencies=[Depends(require_permission("system:dict"))])
async def create_dict_item(
    body: DictItemIn,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not body.type.strip():
        return error(400, "字典分组不能为空")
    if not body.label.strip():
        return error(400, "字典项名称不能为空")
    dup = await db.dict_items.find_one({"type": body.type, "value": body.value or body.label})
    if dup:
        return error(400, f"分组 [{body.type}] 下已存在相同值 [{body.value or body.label}]")
    doc = {
        "type": body.type.strip(),
        "label": body.label.strip(),
        "value": (body.value or body.label).strip(),
        "sort": body.sort,
        "enabled": body.enabled,
        "createdAt": datetime.now(timezone.utc),
    }
    await db.dict_items.insert_one(doc)
    return success(None, "字典项已新增")


@router.put("/items/{item_id}", dependencies=[Depends(require_permission("system:dict"))])
async def update_dict_item(
    item_id: str,
    body: DictItemIn,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    item = await db.dict_items.find_one({"_id": ObjectId(item_id)})
    if not item:
        return error(404, "字典项不存在")
    update = {
        "type": body.type.strip(),
        "label": body.label.strip(),
        "value": (body.value or body.label).strip(),
        "sort": body.sort,
        "enabled": body.enabled,
    }
    await db.dict_items.update_one({"_id": ObjectId(item_id)}, {"$set": update})
    return success(None, "字典项已更新")


@router.delete("/items/{item_id}", dependencies=[Depends(require_permission("system:dict"))])
async def delete_dict_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    item = await db.dict_items.find_one({"_id": ObjectId(item_id)})
    if not item:
        return error(404, "字典项不存在")
    await db.dict_items.delete_one({"_id": ObjectId(item_id)})
    return success(None, "字典项已删除")


@router.get("/options")
async def get_dict_options(
    type: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """业务下拉读取（登录即可）：返回启用项 [{label, value}]"""
    cursor = db.dict_items.find({"type": type, "enabled": True}).sort([("sort", 1), ("_id", 1)])
    records = []
    async for item in cursor:
        records.append({"label": item.get("label", ""), "value": item.get("value", "") or item.get("label", "")})
    return success(records)
