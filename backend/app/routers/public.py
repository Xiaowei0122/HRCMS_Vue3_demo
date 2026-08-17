"""公开接口 — 供官网（HRhomepage_vue3）等公开站点读取，无需登录"""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db
from app.core.response import success, error, paginate

router = APIRouter(prefix="/public", tags=["公开门户"])


# ─── 站点全局配置 ──────────────────────────────────

@router.get("/config")
async def get_public_config(db: AsyncIOMotorDatabase = Depends(get_db)):
    """返回官网需要的完整站点配置（含轮播/服务/关于/联系方式/备案号等）"""
    config = await db.global_config.find_one({"_id": "global"})
    if not config:
        return success({})
    basic = config.get("basic", {})
    contact = config.get("contact", {})
    return success({
        "siteName": basic.get("siteName", "鸿瑞科技"),
        "logo": basic.get("logo", ""),
        "favicon": basic.get("favicon", ""),
        "footer": basic.get("footer", ""),
        "seoKeywords": basic.get("seoKeywords", ""),
        "seoDescription": basic.get("seoDescription", ""),
        "qrcode": basic.get("qrcode", ""),
        "icp": basic.get("icp", ""),
        "gongan": basic.get("gongan", ""),
        "contact": {
            "address": contact.get("address", ""),
            "phone": contact.get("phone", ""),
            "email": contact.get("email", ""),
            "workingHours": contact.get("workingHours", ""),
            "businessPhone": contact.get("businessPhone", contact.get("phone", "")),
        },
        "map": config.get("map", {}),
        "banners": config.get("banners", []),
        "services": config.get("services", []),
        "about": config.get("about", {}),
    })


@router.get("/banners")
async def get_public_banners(db: AsyncIOMotorDatabase = Depends(get_db)):
    config = await db.global_config.find_one({"_id": "global"})
    return success(config.get("banners", []) if config else [])


# ─── 新闻 ──────────────────────────────────────────

@router.get("/news")
async def get_public_news(
    page: int = 1,
    size: int = 10,
    type: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    filter_q = {"isPublished": True}
    if type:
        filter_q["type"] = type
    total = await db.news.count_documents(filter_q)
    cursor = db.news.find(filter_q).skip((page - 1) * size).limit(size).sort([("isPinned", -1), ("_id", -1)])
    records = []
    async for n in cursor:
        records.append({
            "id": str(n["_id"]),
            "title": n.get("title", ""),
            "type": n.get("type", ""),
            "content": n.get("content", ""),
            "cover": n.get("cover", ""),
            "views": n.get("views", 0),
            "isPinned": n.get("isPinned", False),
            "date": n.get("date", ""),
            "summary": _strip_html(n.get("content", ""))[:120],
        })
    return success(paginate(records, total, page, size))


@router.get("/news/{news_id}")
async def get_public_news_detail(
    news_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    n = await db.news.find_one({"_id": ObjectId(news_id), "isPublished": True})
    if not n:
        return error(404, "新闻不存在或已下架")
    await db.news.update_one({"_id": ObjectId(news_id)}, {"$inc": {"views": 1}})
    return success({
        "id": str(n["_id"]),
        "title": n.get("title", ""),
        "type": n.get("type", ""),
        "content": n.get("content", ""),
        "cover": n.get("cover", ""),
        "views": n.get("views", 0) + 1,
        "date": n.get("date", ""),
    })


# ─── 产品 ──────────────────────────────────────────

@router.get("/products")
async def get_public_products(
    page: int = 1,
    size: int = 20,
    category: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    filter_q = {}
    if category:
        filter_q["category"] = category
    total = await db.products.count_documents(filter_q)
    cursor = db.products.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for p in cursor:
        records.append(_format_product(p))
    return success(paginate(records, total, page, size))


@router.get("/products/{product_id}")
async def get_public_product_detail(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    p = await db.products.find_one({"_id": ObjectId(product_id)})
    if not p:
        return error(404, "产品不存在")
    return success(_format_product(p))


# ─── 品牌 / 案例 / 荣誉 ─────────────────────────────

@router.get("/brands")
async def get_public_brands(db: AsyncIOMotorDatabase = Depends(get_db)):
    cursor = db.brands.find({}).sort("_id", -1)
    records = []
    async for b in cursor:
        records.append({
            "id": str(b["_id"]),
            "name": b.get("name", ""),
            "logo": b.get("logo", ""),
            "level": b.get("level", ""),
            "url": b.get("url", ""),
        })
    return success(records)


@router.get("/cases")
async def get_public_cases(db: AsyncIOMotorDatabase = Depends(get_db)):
    cursor = db.cases.find({}).sort("_id", -1)
    records = []
    async for c in cursor:
        records.append({
            "id": str(c["_id"]),
            "client": c.get("client", ""),
            "industry": c.get("industry", ""),
            "device": c.get("device", ""),
            "mode": c.get("mode", ""),
            "summary": c.get("summary", ""),
            "date": c.get("date", ""),
        })
    return success(records)


@router.get("/honors")
async def get_public_honors(
    type: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    filter_q = {}
    if type:
        filter_q["type"] = type
    cursor = db.honors.find(filter_q).sort("_id", -1)
    records = []
    async for h in cursor:
        records.append({
            "id": str(h["_id"]),
            "title": h.get("title", ""),
            "type": h.get("type", ""),
            "url": h.get("url", ""),
            "date": h.get("date", ""),
        })
    return success(records)


# ─── 需求单 / 线索提交（官网「联系我们」表单）───────

@router.post("/leads")
async def submit_public_lead(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    name = body.get("name", "").strip()
    phone = body.get("phone", "").strip()
    if not name or not phone:
        return error(400, "姓名和电话为必填项")
    doc = {
        "name": name,
        "phone": phone,
        "category": body.get("category", body.get("type", "产品咨询")),
        "content": body.get("content", body.get("message", "")),
        "status": "待跟进",
        "remark": "",
        "createTime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }
    result = await db.leads.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "提交成功，我们会尽快与您联系")


# ─── 辅助函数 ───────────────────────────────────────

def _format_product(p: dict) -> dict:
    return {
        "id": str(p["_id"]),
        "name": p.get("name", ""),
        "price": p.get("price", 0),
        "speed": p.get("speed", ""),
        "function": p.get("function", ""),
        "stock": p.get("stock", 0),
        "img": p.get("img", ""),
        "techSpecs": p.get("techSpecs", []),
        "category": p.get("category", ""),
    }


def _strip_html(html: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", html or "").strip()
