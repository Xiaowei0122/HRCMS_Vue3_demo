"""线索管理路由"""
import io
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import openpyxl

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success, error, paginate
from app.core.security import generate_order_no
from app.core.timeutil import now_str, now_min, today_str
from app.services import notify

router = APIRouter(prefix="/leads", tags=["线索管理"], dependencies=[Depends(require_permission("demand"))])

# 维修类需求类别（官网提交的英文值 + 中文值）
_REPAIR_CATEGORIES = ("service", "维修", "报修", "用户维护报修")


def _is_repair_category(category: str) -> bool:
    c = (category or "").strip()
    return c in _REPAIR_CATEGORIES or "维修" in c or "报修" in c


@router.get("")
async def get_lead_list(
    page: int = 1,
    size: int = 10,
    status: str = "",
    name: str = "",
    startDate: str = "",
    endDate: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if status:
        filter_q["status"] = status
    if name:
        filter_q["name"] = {"$regex": name, "$options": "i"}
    # 日期范围筛选：createTime 是字符串格式 "YYYY-MM-DD HH:mm:ss"
    if startDate or endDate:
        date_filter = {}
        if startDate:
            date_filter["$gte"] = startDate + " 00:00:00"
        if endDate:
            date_filter["$lte"] = endDate + " 23:59:59"
        filter_q["createTime"] = date_filter

    total = await db.leads.count_documents(filter_q)
    cursor = db.leads.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for l in cursor:
        records.append({
            "id": str(l["_id"]),
            "name": l.get("name", ""),
            "phone": l.get("phone", ""),
            "category": l.get("category", ""),
            "content": l.get("content", ""),
            "status": l.get("status", ""),
            "remark": l.get("remark", ""),
            "createTime": l.get("createTime", ""),
            "convertedOrderNo": l.get("convertedOrderNo", ""),
        })
    return success(paginate(records, total, page, size))


@router.get("/export")
async def export_leads(
    status: str = "",
    startDate: str = "",
    endDate: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if status:
        filter_q["status"] = status
    # 日期范围筛选：createTime 是字符串格式 "YYYY-MM-DD HH:mm:ss"
    if startDate or endDate:
        date_filter = {}
        if startDate:
            date_filter["$gte"] = startDate + " 00:00:00"
        if endDate:
            date_filter["$lte"] = endDate + " 23:59:59"
        filter_q["createTime"] = date_filter
    cursor = db.leads.find(filter_q)
    leads = []
    async for l in cursor:
        leads.append(l)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "线索列表"
    ws.append(["姓名", "电话", "类别", "内容", "状态", "备注", "创建时间"])
    for l in leads:
        ws.append([l.get("name"), l.get("phone"), l.get("category"), l.get("content"), l.get("status"), l.get("remark"), l.get("createTime")])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=leads.xlsx"},
    )


@router.get("/{lead_id}")
async def get_lead_detail(
    lead_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    l = await db.leads.find_one({"_id": ObjectId(lead_id)})
    if not l:
        return error(404, "线索不存在")
    return success({
        "id": str(l["_id"]),
        "name": l.get("name", ""),
        "phone": l.get("phone", ""),
        "category": l.get("category", ""),
        "content": l.get("content", ""),
        "status": l.get("status", ""),
        "remark": l.get("remark", ""),
        "createTime": l.get("createTime", ""),
        "convertedOrderNo": l.get("convertedOrderNo", ""),
    })


@router.post("/{lead_id}/convert")
async def convert_lead_to_repair(
    lead_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """一键转工单：维修类需求 → 报修工单（待接单），需求标记为已成交"""
    l = await db.leads.find_one({"_id": ObjectId(lead_id)})
    if not l:
        return error(404, "需求不存在")
    if l.get("status") == "已成交":
        return error(400, "该需求已转工单")
    if not _is_repair_category(l.get("category", "")):
        return error(400, "仅维修类需求支持一键转工单")

    doc = {
        "orderNo": generate_order_no(),
        "company": "",
        "contact": l.get("name", ""),
        "phone": l.get("phone", ""),
        "address": "",
        "deviceType": body.get("deviceType", ""),
        "workOrderType": body.get("workOrderType", "售后上门"),
        "priority": body.get("priority", "普通"),
        "repairDate": body.get("repairDate", today_str()),
        "description": body.get("description") or l.get("content", ""),
        "images": body.get("images", []),
        "latitude": None,
        "longitude": None,
        "fee": None,
        "engineer": "",
        "engineerId": "",
        "status": "待接单",
        "progress": [
            {"node": "工单已由需求单转换生成", "time": now_min(), "status": "done"},
        ],
        "createTime": now_str(),
        "createdBy": user.get("username", ""),
        "isRework": False,
        "reworkOf": "",
        "reworkReason": "",
        "reworkNote": "",
        "reworkCount": 0,
        "reworkChildNo": "",
        "completedBy": "",
        "completedAt": "",
        "confirmedBy": "",
        "confirmedAt": "",
        "confirmRole": "",
        "archived": False,
        "reservedBy": "",
        "reservedAt": "",
        "transferRequest": None,
    }
    result = await db.repairs.insert_one(doc)
    await db.leads.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": {"status": "已成交", "convertedOrderNo": doc["orderNo"], "remark": f"已转工单 {doc['orderNo']}"}},
    )
    await notify.push_notify(
        db,
        type_="repair_new",
        title="新增工单",
        content=f"需求「{l.get('name', '')}」已一键转为工单 {doc['orderNo']}",
        link="/repairs",
        role_codes=["super_admin", "admin"],
    )
    return success({"id": str(result.inserted_id), "orderNo": doc["orderNo"]}, "已转为工单")


@router.put("/{lead_id}/progress")
async def update_lead_progress(
    lead_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.leads.update_one({"_id": ObjectId(lead_id)}, {"$set": {"status": body.get("status"), "remark": body.get("remark", "")}})
    return success(None, "线索进度已更新")
