"""新闻管理路由"""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error, paginate

router = APIRouter(prefix="/news", tags=["新闻管理"])


@router.get("")
async def get_news_list(
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

    total = await db.news.count_documents(filter_q)
    cursor = db.news.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for n in cursor:
        records.append(_format_news(n))
    return success(paginate(records, total, page, size))


@router.get("/{news_id}")
async def get_news_detail(
    news_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    n = await db.news.find_one({"_id": ObjectId(news_id)})
    if not n:
        return error(404, "新闻不存在")
    return success(_format_news(n))


@router.post("")
async def create_news(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    doc = {
        **body,
        "views": 0,
        "isPublished": body.get("isPublished", False),
        "isPinned": body.get("isPinned", False),
        "createdAt": datetime.now(timezone.utc),
    }
    result = await db.news.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "新闻创建成功")


@router.put("/{news_id}")
async def update_news(
    news_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.news.update_one({"_id": ObjectId(news_id)}, {"$set": body})
    return success(None, "新闻更新成功")


@router.delete("/{news_id}")
async def delete_news(
    news_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.news.delete_one({"_id": ObjectId(news_id)})
    return success(None, "新闻已删除")


@router.patch("/{news_id}/pin")
async def toggle_pin_news(
    news_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    n = await db.news.find_one({"_id": ObjectId(news_id)})
    if not n:
        return error(404, "新闻不存在")
    new_pin = not n.get("isPinned", False)
    await db.news.update_one({"_id": ObjectId(news_id)}, {"$set": {"isPinned": new_pin}})
    return success(new_pin, "已置顶" if new_pin else "已取消置顶")


@router.patch("/{news_id}/publish")
async def publish_news(
    news_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    n = await db.news.find_one({"_id": ObjectId(news_id)})
    if not n:
        return error(404, "新闻不存在")
    new_pub = not n.get("isPublished", False)
    await db.news.update_one({"_id": ObjectId(news_id)}, {"$set": {"isPublished": new_pub}})
    return success(new_pub, "已发布" if new_pub else "已下架")


def _format_news(n: dict) -> dict:
    return {
        "id": str(n["_id"]),
        "title": n.get("title", ""),
        "type": n.get("type", ""),
        "content": n.get("content", ""),
        "cover": n.get("cover", ""),
        "views": n.get("views", 0),
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
