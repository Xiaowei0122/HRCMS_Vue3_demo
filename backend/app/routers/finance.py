"""财务管理路由 — 共享文件 + 资产管理"""
import io
import os
import uuid
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
import openpyxl

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success, error, paginate
from app.core.config import settings
from app.core.timeutil import now_cn
from app.services.recycle import soft_delete
from app.services import storage

router = APIRouter(prefix="/finance", tags=["财务管理"])

_files = Depends(require_permission("finance:files"))
_assets = Depends(require_permission("finance:assets"))
_vehicles = Depends(require_permission("finance:vehicle"))

ALLOWED_FILE_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".docx", ".doc", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".txt", ".csv", ".zip"}
FILE_CATEGORIES = {"invoice", "report", "policy", "contract", "other"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


# ─── 共享文件 ──────────────────────────────────────

@router.get("/files", dependencies=[_files])
async def get_file_list(
    page: int = 1,
    size: int = 20,
    category: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    filter_q = {}
    if category and category != "all":
        filter_q["category"] = category
    total = await db.finance_files.count_documents(filter_q)
    cursor = db.finance_files.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for f in cursor:
        records.append(_format_file(f))
    return success(paginate(records, total, page, size))


@router.post("/files", dependencies=[_files])
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(default="other"),
    visibility: str = Form(default="public"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if category not in FILE_CATEGORIES:
        return error(400, f"不支持的文件分类: {category}")
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_FILE_EXTENSIONS:
        return error(400, f"不支持的文件类型: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return error(400, "文件大小不能超过 20MB")

    filename = f"{uuid.uuid4().hex}{ext}"
    url = storage.save("finance", filename, content)

    doc = {
        "name": file.filename,
        "type": ext.lstrip("."),
        "category": category,
        "visibility": visibility,
        "url": url,
        "size": _format_size(len(content)),
        "uploader": "admin",
        "uploadTime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "createdAt": datetime.now(timezone.utc),
    }
    result = await db.finance_files.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "文件上传成功")


@router.put("/files/{file_id}", dependencies=[_files])
async def update_file_meta(
    file_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_files.update_one({"_id": ObjectId(file_id)}, {"$set": body})
    return success(None, "文件信息已更新")


@router.delete("/files/{file_id}", dependencies=[_files])
async def delete_file(
    file_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ok = await soft_delete(db, "finance_files", file_id, user.get("realName") or user.get("username", ""))
    if not ok:
        return error(404, "文件不存在")
    return success(None, "文件已移入回收站")


@router.put("/files/{file_id}/permission", dependencies=[_files])
async def update_file_permission(
    file_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_files.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {"visibility": body.get("visibility", "public")}},
    )
    return success(None, "权限已更新")


# ─── 资产管理 ──────────────────────────────────────

@router.get("/assets", dependencies=[_assets])
async def get_asset_list(
    page: int = 1,
    size: int = 20,
    category: str = "",
    status: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    filter_q = {}
    if category:
        filter_q["category"] = category
    if status:
        filter_q["status"] = status
    total = await db.finance_assets.count_documents(filter_q)
    cursor = db.finance_assets.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for a in cursor:
        records.append(_format_asset(a))
    return success(paginate(records, total, page, size))


@router.post("/assets", dependencies=[_assets])
async def create_asset(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = {**body, "createdAt": datetime.now(timezone.utc)}
    result = await db.finance_assets.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "资产已录入")


@router.put("/assets/{asset_id}", dependencies=[_assets])
async def update_asset(
    asset_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_assets.update_one({"_id": ObjectId(asset_id)}, {"$set": body})
    return success(None, "资产已更新")


@router.delete("/assets/{asset_id}", dependencies=[_assets])
async def delete_asset(
    asset_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ok = await soft_delete(db, "finance_assets", asset_id, user.get("realName") or user.get("username", ""))
    if not ok:
        return error(404, "资产不存在")
    return success(None, "资产已移入回收站")


@router.post("/assets/import", dependencies=[_assets])
async def import_assets(
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """批量导入资产（Excel 首行表头：名称/分类/型号/序列号/部门/位置/状态）"""
    try:
        content = await file.read()
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        ws = wb.active
    except Exception:
        return error(400, "无法解析 Excel 文件")
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return error(400, "Excel 内容为空")
    header = [str(c).strip() if c is not None else "" for c in rows[0]]
    idx = {name: i for i, name in enumerate(header)}
    if "名称" not in idx:
        return error(400, "缺少「名称」列")

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
            "category": str(cell("分类") or "设备") if cell("分类") is not None else "设备",
            "model": str(cell("型号") or "") if cell("型号") is not None else "",
            "serialNo": str(cell("序列号") or "") if cell("序列号") is not None else "",
            "department": str(cell("部门") or "") if cell("部门") is not None else "",
            "location": str(cell("位置") or "") if cell("位置") is not None else "",
            "status": str(cell("状态") or "在用") if cell("状态") is not None else "在用",
            "purchaseDate": "",
            "supplier": "",
            "warrantyExpiry": "",
            "createdAt": now,
        }
        await db.finance_assets.insert_one(doc)
        inserted += 1
    return success({"inserted": inserted, "skipped": skipped}, f"导入完成：新增 {inserted} 条，跳过 {skipped} 条")


@router.put("/assets/{asset_id}/status", dependencies=[_assets])
async def update_asset_status(
    asset_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await db.finance_assets.update_one(
        {"_id": ObjectId(asset_id)},
        {"$set": {"status": body.get("status", "在用")}},
    )
    return success(None, "资产状态已更新")


@router.get("/assets/{asset_id}/maintenance", dependencies=[_assets])
async def get_maintenance_records(
    asset_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    asset = await db.finance_assets.find_one({"_id": ObjectId(asset_id)})
    records = asset.get("maintenance", []) if asset else []
    return success(records)


@router.post("/assets/{asset_id}/maintenance", dependencies=[_assets])
async def add_maintenance_record(
    asset_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    record = {
        "type": body.get("type", "维修"),
        "date": body.get("date", ""),
        "description": body.get("description", ""),
        "cost": body.get("cost"),
        "vendor": body.get("vendor", ""),
        "createdAt": datetime.now(timezone.utc),
    }
    await db.finance_assets.update_one(
        {"_id": ObjectId(asset_id)},
        {"$push": {"maintenance": record}},
    )
    return success(None, "维修记录已保存")


# ─── 车辆管理 ──────────────────────────────────────

_VEHICLE_FIELDS = [
    "plateNo", "brand", "model", "vin", "engineNo", "vehicleType",
    "purchaseDate", "registerDate", "department", "responsible",
    "mileage", "status", "img", "remark", "nextMaintenanceDate", "nextMaintenanceKm",
    "insurances",
]


def _normalize_insurances(items) -> list:
    """为每张保单补齐 id 与默认字段"""
    result = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        result.append({
            "id": it.get("id") or uuid.uuid4().hex,
            "type": it.get("type", "商业险"),
            "insurer": it.get("insurer", ""),
            "policyNo": it.get("policyNo", ""),
            "premium": it.get("premium") or 0,
            "startDate": it.get("startDate", ""),
            "endDate": it.get("endDate", ""),
            "certs": it.get("certs") or [],
            "remark": it.get("remark", ""),
        })
    return result


def _days_left(ymd: str, today) -> int:
    """到期日距今天数：正=未到期、0=今天、负=已逾期；空/非法返回大数（不触发提醒）"""
    if not ymd:
        return 999999
    try:
        d = datetime.strptime(ymd, "%Y-%m-%d").date()
        return (d - today).days
    except ValueError:
        return 999999


@router.get("/vehicles", dependencies=[_vehicles])
async def get_vehicle_list(
    page: int = 1,
    size: int = 20,
    status: str = "",
    department: str = "",
    kw: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    filter_q = {}
    if status:
        filter_q["status"] = status
    if department:
        filter_q["department"] = department
    if kw:
        filter_q["$or"] = [
            {"plateNo": {"$regex": kw, "$options": "i"}},
            {"brand": {"$regex": kw, "$options": "i"}},
            {"model": {"$regex": kw, "$options": "i"}},
            {"responsible": {"$regex": kw, "$options": "i"}},
        ]
    total = await db.finance_vehicles.count_documents(filter_q)
    cursor = db.finance_vehicles.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for v in cursor:
        records.append(_format_vehicle(v))
    return success(paginate(records, total, page, size))


@router.get("/vehicles/expiring", dependencies=[_vehicles])
async def get_vehicle_expiring(
    days: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """到期监测：汇总保险/年检/保养三类到期项（按剩余天数升序）"""
    today = now_cn().date()
    items = []
    async for v in db.finance_vehicles.find({"status": {"$ne": "已处置"}}):
        plate = v.get("plateNo", "")
        vid = str(v["_id"])
        # 保险（每张保单一项）
        for ins in v.get("insurances") or []:
            end = ins.get("endDate", "")
            dl = _days_left(end, today)
            if dl <= days:
                items.append({
                    "vehicleId": vid, "plateNo": plate, "category": "insurance",
                    "label": ins.get("type", "保险"), "detail": ins.get("insurer", ""),
                    "dueDate": end, "daysLeft": dl,
                    "level": "overdue" if dl < 0 else "soon",
                })
        # 年检
        ai = v.get("annualInspectionDate", "")
        dl = _days_left(ai, today)
        if dl <= days:
            items.append({
                "vehicleId": vid, "plateNo": plate, "category": "inspection",
                "label": "年检", "detail": "", "dueDate": ai, "daysLeft": dl,
                "level": "overdue" if dl < 0 else "soon",
            })
        # 保养
        nmd = v.get("nextMaintenanceDate", "")
        dl = _days_left(nmd, today)
        if dl <= days:
            items.append({
                "vehicleId": vid, "plateNo": plate, "category": "maintenance",
                "label": "保养", "detail": f"{v.get('nextMaintenanceKm') or 0}km",
                "dueDate": nmd, "daysLeft": dl,
                "level": "overdue" if dl < 0 else "soon",
            })
    items.sort(key=lambda x: x["daysLeft"])

    total = await db.finance_vehicles.count_documents({})
    in_use = await db.finance_vehicles.count_documents({"status": "在用"})
    overdue = sum(1 for i in items if i["level"] == "overdue")
    soon = sum(1 for i in items if i["level"] == "soon")
    return success({
        "stats": {"total": total, "inUse": in_use, "overdue": overdue, "soon": soon},
        "items": items,
    })


@router.post("/vehicles", dependencies=[_vehicles])
async def create_vehicle(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    plate = (body.get("plateNo") or "").strip()
    if not plate:
        return error(400, "请填写车牌号")
    doc = {
        "plateNo": plate,
        "brand": body.get("brand", ""),
        "model": body.get("model", ""),
        "vin": body.get("vin", ""),
        "engineNo": body.get("engineNo", ""),
        "vehicleType": body.get("vehicleType", "面包车"),
        "purchaseDate": body.get("purchaseDate", ""),
        "registerDate": body.get("registerDate", ""),
        "department": body.get("department", ""),
        "responsible": body.get("responsible", ""),
        "mileage": body.get("mileage") or 0,
        "status": body.get("status", "在用"),
        "img": body.get("img", ""),
        "remark": body.get("remark", ""),
        "insurances": _normalize_insurances(body.get("insurances")),
        "annualInspectionDate": body.get("annualInspectionDate", ""),
        "annualInspectionCerts": body.get("annualInspectionCerts") or [],
        "nextMaintenanceDate": body.get("nextMaintenanceDate", ""),
        "nextMaintenanceKm": body.get("nextMaintenanceKm") or 0,
        "maintenance": body.get("maintenance") or [],
        "createdAt": now_cn(),
        "updatedAt": now_cn(),
    }
    result = await db.finance_vehicles.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "车辆已录入")


@router.get("/vehicles/{vehicle_id}", dependencies=[_vehicles])
async def get_vehicle_detail(
    vehicle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    v = await db.finance_vehicles.find_one({"_id": ObjectId(vehicle_id)})
    if not v:
        return error(404, "车辆不存在")
    return success(_format_vehicle(v))


@router.put("/vehicles/{vehicle_id}", dependencies=[_vehicles])
async def update_vehicle(
    vehicle_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    updates = {k: body.get(k) for k in _VEHICLE_FIELDS if k in body}
    if "insurances" in updates:
        updates["insurances"] = _normalize_insurances(updates["insurances"])
    if updates:
        updates["updatedAt"] = now_cn()
        await db.finance_vehicles.update_one({"_id": ObjectId(vehicle_id)}, {"$set": updates})
    return success(None, "车辆已更新")


@router.delete("/vehicles/{vehicle_id}", dependencies=[_vehicles])
async def delete_vehicle(
    vehicle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ok = await soft_delete(db, "finance_vehicles", vehicle_id, user.get("realName") or user.get("username", ""))
    if not ok:
        return error(404, "车辆不存在")
    return success(None, "车辆已移入回收站")


# ─── 保险 ──────────────────────────────────────────

@router.post("/vehicles/{vehicle_id}/insurances", dependencies=[_vehicles])
async def add_vehicle_insurance(
    vehicle_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    ins = {
        "id": uuid.uuid4().hex,
        "type": body.get("type", "商业险"),
        "insurer": body.get("insurer", ""),
        "policyNo": body.get("policyNo", ""),
        "premium": body.get("premium") or 0,
        "startDate": body.get("startDate", ""),
        "endDate": body.get("endDate", ""),
        "certs": body.get("certs") or [],
        "remark": body.get("remark", ""),
    }
    res = await db.finance_vehicles.update_one({"_id": ObjectId(vehicle_id)}, {"$push": {"insurances": ins}})
    if res.matched_count == 0:
        return error(404, "车辆不存在")
    return success(None, "保单已添加")


@router.put("/vehicles/{vehicle_id}/insurances/{ins_id}", dependencies=[_vehicles])
async def update_vehicle_insurance(
    vehicle_id: str,
    ins_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    allowed = {"type", "insurer", "policyNo", "premium", "startDate", "endDate", "certs", "remark"}
    updates = {f"insurances.$.{k}": v for k, v in body.items() if k in allowed}
    if not updates:
        return error(400, "无有效字段")
    res = await db.finance_vehicles.update_one(
        {"_id": ObjectId(vehicle_id), "insurances.id": ins_id},
        {"$set": updates},
    )
    if res.matched_count == 0:
        return error(404, "保单不存在")
    return success(None, "保单已更新")


@router.delete("/vehicles/{vehicle_id}/insurances/{ins_id}", dependencies=[_vehicles])
async def delete_vehicle_insurance(
    vehicle_id: str,
    ins_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    res = await db.finance_vehicles.update_one(
        {"_id": ObjectId(vehicle_id)},
        {"$pull": {"insurances": {"id": ins_id}}},
    )
    if res.matched_count == 0:
        return error(404, "车辆不存在")
    return success(None, "保单已删除")


# ─── 保养 ──────────────────────────────────────────

@router.post("/vehicles/{vehicle_id}/maintenance", dependencies=[_vehicles])
async def add_vehicle_maintenance(
    vehicle_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    rec = {
        "id": uuid.uuid4().hex,
        "date": body.get("date", ""),
        "km": body.get("km") or 0,
        "item": body.get("item", ""),
        "cost": body.get("cost") or 0,
        "vendor": body.get("vendor", ""),
        "remark": body.get("remark", ""),
    }
    res = await db.finance_vehicles.update_one({"_id": ObjectId(vehicle_id)}, {"$push": {"maintenance": rec}})
    if res.matched_count == 0:
        return error(404, "车辆不存在")
    return success(None, "保养记录已添加")


@router.delete("/vehicles/{vehicle_id}/maintenance/{m_id}", dependencies=[_vehicles])
async def delete_vehicle_maintenance(
    vehicle_id: str,
    m_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    res = await db.finance_vehicles.update_one(
        {"_id": ObjectId(vehicle_id)},
        {"$pull": {"maintenance": {"id": m_id}}},
    )
    if res.matched_count == 0:
        return error(404, "车辆不存在")
    return success(None, "保养记录已删除")


# ─── 年检 ──────────────────────────────────────────

@router.put("/vehicles/{vehicle_id}/inspection", dependencies=[_vehicles])
async def update_vehicle_inspection(
    vehicle_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    updates = {}
    if "annualInspectionDate" in body:
        updates["annualInspectionDate"] = body.get("annualInspectionDate", "")
    if "annualInspectionCerts" in body:
        updates["annualInspectionCerts"] = body.get("annualInspectionCerts") or []
    if updates:
        updates["updatedAt"] = now_cn()
        await db.finance_vehicles.update_one({"_id": ObjectId(vehicle_id)}, {"$set": updates})
    return success(None, "年检信息已更新")


# ─── 格式化辅助 ────────────────────────────────────

def _format_file(f: dict) -> dict:
    return {
        "id": str(f["_id"]),
        "name": f.get("name", ""),
        "type": f.get("type", ""),
        "category": f.get("category", "other"),
        "visibility": f.get("visibility", "public"),
        "url": f.get("url", ""),
        "size": f.get("size", ""),
        "uploader": f.get("uploader", ""),
        "uploadTime": f.get("uploadTime", ""),
    }


def _format_asset(a: dict) -> dict:
    return {
        "id": str(a["_id"]),
        "name": a.get("name", ""),
        "category": a.get("category", ""),
        "model": a.get("model", ""),
        "serialNo": a.get("serialNo", ""),
        "department": a.get("department", ""),
        "location": a.get("location", ""),
        "status": a.get("status", "在用"),
        "purchaseDate": a.get("purchaseDate", ""),
        "supplier": a.get("supplier", ""),
        "warrantyExpiry": a.get("warrantyExpiry", ""),
    }


def _format_vehicle(v: dict) -> dict:
    return {
        "id": str(v["_id"]),
        "plateNo": v.get("plateNo", ""),
        "brand": v.get("brand", ""),
        "model": v.get("model", ""),
        "vin": v.get("vin", ""),
        "engineNo": v.get("engineNo", ""),
        "vehicleType": v.get("vehicleType", ""),
        "purchaseDate": v.get("purchaseDate", ""),
        "registerDate": v.get("registerDate", ""),
        "department": v.get("department", ""),
        "responsible": v.get("responsible", ""),
        "mileage": v.get("mileage", 0),
        "status": v.get("status", "在用"),
        "img": v.get("img", ""),
        "remark": v.get("remark", ""),
        "insurances": v.get("insurances", []),
        "annualInspectionDate": v.get("annualInspectionDate", ""),
        "annualInspectionCerts": v.get("annualInspectionCerts", []),
        "nextMaintenanceDate": v.get("nextMaintenanceDate", ""),
        "nextMaintenanceKm": v.get("nextMaintenanceKm", 0),
        "maintenance": v.get("maintenance", []),
    }


def _format_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / 1024 / 1024:.1f} MB"
