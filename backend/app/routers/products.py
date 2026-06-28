"""产品管理路由"""
import io
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import openpyxl

from app.core.deps import get_db, get_current_user
from app.core.response import success, error, paginate

router = APIRouter(prefix="/products", tags=["产品管理"])


@router.get("")
async def get_product_list(
    page: int = 1,
    size: int = 10,
    category: str = "",
    name: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if category:
        filter_q["category"] = category
    if name:
        filter_q["name"] = {"$regex": name, "$options": "i"}

    total = await db.products.count_documents(filter_q)
    cursor = db.products.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for p in cursor:
        records.append(_format_product(p))
    return success(paginate(records, total, page, size))


@router.get("/{product_id}")
async def get_product_detail(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    p = await db.products.find_one({"_id": ObjectId(product_id)})
    if not p:
        return error(404, "产品不存在")
    return success(_format_product(p))


@router.post("")
async def create_product(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    doc = {**body, "createdAt": datetime.now(timezone.utc), "updatedAt": datetime.now(timezone.utc)}
    result = await db.products.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "产品创建成功")


@router.put("/{product_id}")
async def update_product(
    product_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    body["updatedAt"] = datetime.now(timezone.utc)
    await db.products.update_one({"_id": ObjectId(product_id)}, {"$set": body})
    return success(None, "产品更新成功")


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.products.delete_one({"_id": ObjectId(product_id)})
    return success(None, "产品已删除")


@router.get("/export")
async def export_products(
    category: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if category:
        filter_q["category"] = category
    cursor = db.products.find(filter_q)
    products = []
    async for p in cursor:
        products.append(p)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "产品列表"
    ws.append(["名称", "价格", "识别速度", "功能", "库存", "分类"])
    for p in products:
        ws.append([p.get("name"), p.get("price"), p.get("speed"), p.get("function"), p.get("stock"), p.get("category")])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=products.xlsx"},
    )


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
        "createdAt": _fmt_time(p.get("createdAt")),
        "updatedAt": _fmt_time(p.get("updatedAt")),
    }


def _fmt_time(dt) -> str:
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)
