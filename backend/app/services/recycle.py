"""软删除 / 回收站服务：关键数据删除前快照到 deleted_items，可恢复。

只对「内容型」集合启用软删除（产品/新闻/荣誉/品牌/案例/共享文件/资产），
角色/用户/字典等管理配置仍走硬删除（由各自路由处理）。
"""
from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

# 参与软删除的集合 → 中文名（回收站展示用）
_SOFT_DELETE_COLLECTIONS = {
    "products": "产品",
    "news": "新闻",
    "honors": "荣誉",
    "brands": "品牌",
    "cases": "案例",
    "finance_files": "共享文件",
    "finance_assets": "资产",
    "finance_vehicles": "车辆",
}

# 用于提取「可读标题」的候选字段（按优先级）
_LABEL_KEYS = ("name", "title", "client", "company", "realName", "username", "orderNo", "customer", "plateNo")


def _label_for(collection: str, doc: dict) -> str:
    for key in _LABEL_KEYS:
        value = doc.get(key)
        if value:
            return str(value)
    return f"{collection}#{str(doc.get('_id', ''))[:6]}"


async def soft_delete(
    db: AsyncIOMotorDatabase,
    collection: str,
    doc_id: str,
    operator: str = "",
) -> bool:
    """软删除：快照原文档 → 写入 deleted_items → 从原集合移除。返回是否成功。"""
    if collection not in _SOFT_DELETE_COLLECTIONS:
        return False
    try:
        oid = ObjectId(doc_id)
    except Exception:
        return False
    doc = await db[collection].find_one({"_id": oid})
    if doc is None:
        return False
    await db.deleted_items.insert_one({
        "collection": collection,
        "collectionName": _SOFT_DELETE_COLLECTIONS[collection],
        "originalId": str(doc["_id"]),
        "label": _label_for(collection, doc),
        "data": dict(doc),
        "operator": operator,
        "deletedAt": datetime.now(timezone.utc),
    })
    await db[collection].delete_one({"_id": oid})
    return True


async def restore(db: AsyncIOMotorDatabase, deleted_id: str) -> str | None:
    """恢复：从 deleted_items 回写原集合。返回目标集合名，失败返回 None。"""
    try:
        oid = ObjectId(deleted_id)
    except Exception:
        return None
    item = await db.deleted_items.find_one({"_id": oid})
    if item is None:
        return None
    collection = item.get("collection", "")
    data = dict(item.get("data") or {})
    data.pop("_id", None)  # 回写时重新分配 _id，避免与现有文档冲突
    if not collection:
        await db.deleted_items.delete_one({"_id": oid})
        return None
    await db[collection].insert_one(data)
    await db.deleted_items.delete_one({"_id": oid})
    return collection


async def purge(db: AsyncIOMotorDatabase, deleted_id: str) -> bool:
    """彻底删除：从 deleted_items 移除快照，不可恢复。"""
    try:
        oid = ObjectId(deleted_id)
    except Exception:
        return False
    res = await db.deleted_items.delete_one({"_id": oid})
    return res.deleted_count > 0
