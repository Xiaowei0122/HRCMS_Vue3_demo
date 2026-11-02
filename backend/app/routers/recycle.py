"""回收站路由：查看软删除快照 / 恢复 / 彻底删除"""
from datetime import datetime

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success, error, paginate
from app.services.recycle import restore, purge

router = APIRouter(
    prefix="/recycle",
    tags=["回收站"],
    dependencies=[Depends(require_permission("system:recycle"))],
)


def _fmt(dt) -> str:
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


@router.get("")
async def get_recycle_list(
    page: int = 1,
    size: int = 20,
    collection: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if collection:
        filter_q["collection"] = collection
    total = await db.deleted_items.count_documents(filter_q)
    cursor = db.deleted_items.find(filter_q).skip((page - 1) * size).limit(size).sort("deletedAt", -1)
    records = []
    async for item in cursor:
        records.append({
            "id": str(item["_id"]),
            "collection": item.get("collection", ""),
            "collectionName": item.get("collectionName", ""),
            "label": item.get("label", ""),
            "operator": item.get("operator", ""),
            "deletedAt": _fmt(item.get("deletedAt")),
        })
    return success(paginate(records, total, page, size))


@router.post("/{item_id}/restore")
async def restore_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    collection = await restore(db, item_id)
    if collection is None:
        return error(404, "回收站条目不存在或无法恢复")
    return success({"collection": collection}, "已恢复")


@router.delete("/{item_id}")
async def purge_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ok = await purge(db, item_id)
    if not ok:
        return error(404, "回收站条目不存在")
    return success(None, "已彻底删除")
