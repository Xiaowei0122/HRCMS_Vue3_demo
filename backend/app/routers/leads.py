"""线索管理路由"""
import io
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import openpyxl

from app.core.deps import get_db, get_current_user
from app.core.response import success, error, paginate

router = APIRouter(prefix="/leads", tags=["线索管理"])


@router.get("")
async def get_lead_list(
    page: int = 1,
    size: int = 10,
    status: str = "",
    name: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if status:
        filter_q["status"] = status
    if name:
        filter_q["name"] = {"$regex": name, "$options": "i"}

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
        })
    return success(paginate(records, total, page, size))


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
    })


@router.put("/{lead_id}/progress")
async def update_lead_progress(
    lead_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    await db.leads.update_one({"_id": ObjectId(lead_id)}, {"$set": {"status": body.get("status"), "remark": body.get("remark", "")}})
    return success(None, "线索进度已更新")


@router.get("/export")
async def export_leads(
    status: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    filter_q = {}
    if status:
        filter_q["status"] = status
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
