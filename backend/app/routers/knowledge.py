"""技术知识库管理路由（小程序专用，与门户新闻中心 news 相互独立）"""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success, error, paginate
from app.services.recycle import soft_delete

router = APIRouter(prefix="/knowledge", tags=["知识库管理"], dependencies=[Depends(require_permission("knowledge"))])


@router.get("")
async def get_knowledge_list(
    page: int = 1,
    size: int = 10,
    type: str = "",
    title: str = "",
    isPublished: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if type:
        filter_q["type"] = type
    if title:
        filter_q["title"] = {"$regex": title, "$options": "i"}
    if isPublished == "true":
        filter_q["isPublished"] = True
    elif isPublished == "false":
        filter_q["isPublished"] = False

    total = await db.knowledge.count_documents(filter_q)
    cursor = db.knowledge.find(filter_q).skip((page - 1) * size).limit(size).sort([("isPinned", -1), ("_id", -1)])
    records = []
    async for n in cursor:
        records.append(_format_knowledge(n))
    return success(paginate(records, total, page, size))


@router.get("/{article_id}")
async def get_knowledge_detail(
    article_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    n = await db.knowledge.find_one({"_id": ObjectId(article_id)})
    if not n:
        return error(404, "文章不存在")
    return success(_format_knowledge(n))


@router.post("")
async def create_knowledge(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    doc = {
        **body,
        "views": 0,
        "author": body.get("author") or user.get("realName") or user.get("username", ""),
        "isPublished": body.get("isPublished", False),
        "isPinned": body.get("isPinned", False),
        "createdAt": datetime.now(timezone.utc),
    }
    result = await db.knowledge.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "文章创建成功")


@router.put("/{article_id}")
async def update_knowledge(
    article_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.knowledge.update_one({"_id": ObjectId(article_id)}, {"$set": body})
    return success(None, "文章更新成功")


@router.delete("/{article_id}")
async def delete_knowledge(
    article_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ok = await soft_delete(db, "knowledge", article_id, user.get("realName") or user.get("username", ""))
    if not ok:
        return error(404, "文章不存在")
    return success(None, "文章已移入回收站")


@router.patch("/{article_id}/pin")
async def toggle_pin_knowledge(
    article_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    n = await db.knowledge.find_one({"_id": ObjectId(article_id)})
    if not n:
        return error(404, "文章不存在")
    new_pin = not n.get("isPinned", False)
    await db.knowledge.update_one({"_id": ObjectId(article_id)}, {"$set": {"isPinned": new_pin}})
    return success(new_pin, "已置顶" if new_pin else "已取消置顶")


@router.patch("/{article_id}/publish")
async def publish_knowledge(
    article_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    n = await db.knowledge.find_one({"_id": ObjectId(article_id)})
    if not n:
        return error(404, "文章不存在")
    new_pub = not n.get("isPublished", False)
    await db.knowledge.update_one({"_id": ObjectId(article_id)}, {"$set": {"isPublished": new_pub}})
    return success(new_pub, "已发布" if new_pub else "已下架")


def _format_knowledge(n: dict) -> dict:
    return {
        "id": str(n["_id"]),
        "title": n.get("title", ""),
        "type": n.get("type", ""),
        "content": n.get("content", ""),
        "cover": n.get("cover", ""),
        "views": n.get("views", 0),
        "author": n.get("author", ""),
        "isPublished": n.get("isPublished", False),
        "isPinned": n.get("isPinned", False),
        "date": n.get("date", ""),
        "createdAt": _fmt(n.get("createdAt")),
    }


def _fmt(dt) -> str:
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)
