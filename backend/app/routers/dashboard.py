"""仪表盘路由"""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.deps import get_db, get_current_user
from app.core.response import success

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
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
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """返回最近7天或30天的趋势数据"""
    return success({
        "dates": [],
        "repairs": [],
        "leads": [],
    })


@router.get("/todos")
async def get_dashboard_todos(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    # 待处理报修
    repairs_cursor = db.repairs.find({"status": {"$nin": ["已完成", "已取消"]}}).limit(5).sort("_id", -1)
    repairs = []
    async for r in repairs_cursor:
        repairs.append({"id": str(r["_id"]), "orderNo": r.get("orderNo", ""), "company": r.get("company", ""), "status": r.get("status", ""), "createTime": r.get("createTime", "")})

    # 待跟进线索
    leads_cursor = db.leads.find({"status": "待跟进"}).limit(5).sort("_id", -1)
    leads = []
    async for l in leads_cursor:
        leads.append({"id": str(l["_id"]), "name": l.get("name", ""), "category": l.get("category", ""), "status": l.get("status", ""), "createTime": l.get("createTime", "")})

    return success({"repairs": repairs, "leads": leads})


def _today() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
