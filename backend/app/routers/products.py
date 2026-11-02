"""产品管理路由"""
import io
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import openpyxl

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success, error, paginate
from app.services.recycle import soft_delete

router = APIRouter(prefix="/products", tags=["产品管理"], dependencies=[Depends(require_permission("products"))])


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
    ok = await soft_delete(db, "products", product_id, user.get("realName") or user.get("username", ""))
    if not ok:
        return error(404, "产品不存在")
    return success(None, "产品已移入回收站")


@router.post("/import")
async def import_products(
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """批量导入产品（Excel 首行为表头：名称/价格/识别速度/功能/库存/分类）"""
    try:
        content = await file.read()
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        ws = wb.active
    except Exception:
        return error(400, "无法解析 Excel 文件，请使用导出模板")
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return error(400, "Excel 内容为空")
    header = [str(c).strip() if c is not None else "" for c in rows[0]]
    # 兼容表头顺序：按列名定位
    idx = {name: i for i, name in enumerate(header)}
    if "名称" not in idx:
        return error(400, "缺少「名称」列，请使用导出模板")

    now = datetime.now(timezone.utc)
    inserted = 0
    skipped = 0
    for row in rows[1:]:
        def cell(col):
            i = idx.get(col)
            return row[i] if i is not None and i < len(row) else None
        name = cell("名称")
        if name is None or not str(name).strip():
            skipped += 1
            continue
        doc = {
            "name": str(name).strip(),
            "price": cell("价格") or 0,
            "speed": str(cell("识别速度") or "") if cell("识别速度") is not None else "",
            "function": str(cell("功能") or "") if cell("功能") is not None else "",
            "stock": cell("库存") or 0,
            "category": str(cell("分类") or "color"),
            "img": "",
            "techSpecs": [],
            "createdAt": now,
            "updatedAt": now,
        }
        await db.products.insert_one(doc)
        inserted += 1
    return success({"inserted": inserted, "skipped": skipped}, f"导入完成：新增 {inserted} 条，跳过 {skipped} 条")


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
