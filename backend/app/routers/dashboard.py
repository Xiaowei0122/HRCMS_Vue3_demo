"""仪表盘路由"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.deps import get_db, require_user_types
from app.core.response import success

router = APIRouter(
    prefix="/dashboard",
    tags=["仪表盘"],
    dependencies=[Depends(require_user_types("admin", "internal"))],
)


@router.get("/stats")
async def get_dashboard_stats(db: AsyncIOMotorDatabase = Depends(get_db)):
    return success({
        "userCount": await db.users.count_documents({}),
        "productCount": await db.products.count_documents({}),
        "newsCount": await db.news.count_documents({}),
        "repairCount": await db.repairs.count_documents({}),
        "todayRepairs": await db.repairs.count_documents({"createTime": {"$regex": _today()}}),
        "pendingLeads": await db.leads.count_documents({"status": "待跟进"}),
    })


@router.get("/trends")
async def get_dashboard_trends(
    type: str = "repair",
    days: int = 7,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """返回最近 N 天（默认 7 天）的报修量与线索量趋势"""
    days = max(1, min(days, 30))
    now = datetime.now(timezone.utc)
    dates = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]
    start_date = dates[0]

    repair_counts = {d: 0 for d in dates}
    lead_counts = {d: 0 for d in dates}

    async for r in db.repairs.find({"createTime": {"$gte": start_date}}):
        d = (r.get("createTime", "") or "")[:10]
        if d in repair_counts:
            repair_counts[d] += 1

    async for l in db.leads.find({"createTime": {"$gte": start_date}}):
        d = (l.get("createTime", "") or "")[:10]
        if d in lead_counts:
            lead_counts[d] += 1

    return success({
        "dates": dates,
        "repairs": [repair_counts[d] for d in dates],
        "leads": [lead_counts[d] for d in dates],
    })


@router.get("/todos")
async def get_dashboard_todos(db: AsyncIOMotorDatabase = Depends(get_db)):
    # 待接单工单（未指派，需管理员分派）
    repairs_cursor = db.repairs.find({"status": "待接单"}).limit(5).sort("_id", -1)
    repairs = []
    async for r in repairs_cursor:
        repairs.append({"id": str(r["_id"]), "orderNo": r.get("orderNo", ""), "company": r.get("company", ""), "status": r.get("status", ""), "createTime": r.get("createTime", "")})

    # 待跟进线索
    leads_cursor = db.leads.find({"status": "待跟进"}).limit(5).sort("_id", -1)
    leads = []
    async for l in leads_cursor:
        leads.append({"id": str(l["_id"]), "name": l.get("name", ""), "category": l.get("category", ""), "status": l.get("status", ""), "createTime": l.get("createTime", "")})

    # 待处理投诉
    complaints_cursor = db.complaints.find({"status": "待处理"}).limit(5).sort("_id", -1)
    complaints = []
    async for c in complaints_cursor:
        complaints.append({"id": str(c["_id"]), "customer": c.get("customer", ""), "category": c.get("category", ""), "content": c.get("content", ""), "status": c.get("status", "")})

    return success({"repairs": repairs, "leads": leads, "complaints": complaints})


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
