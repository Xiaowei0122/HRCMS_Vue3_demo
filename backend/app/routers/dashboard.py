"""仪表盘路由：统计 / 趋势(含成本) / 成本概览 / 今日排期 / 待办"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success
from app.core.timeutil import now_cn

router = APIRouter(
    prefix="/dashboard",
    tags=["仪表盘"],
    dependencies=[Depends(require_permission("dashboard"))],
)

# 已结状态：成本只计入这两类工单（未结不纳入）
_SETTLED = ["已归档", "已完成"]


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """返回全量统计超集，前端按角色选取展示哪些指标"""
    uname = user.get("username", "")
    uid = str(user.get("_id", ""))
    month_prefix = now_cn().strftime("%Y-%m")

    # 成本汇总（仅已结工单费用）
    month_cost = 0.0
    total_cost = 0.0
    async for r in db.repairs.find({"status": {"$in": _SETTLED}, "fee.amount": {"$exists": True}}):
        amt = _fee_amount(r)
        if not amt:
            continue
        total_cost += amt
        if (_settled_date(r) or "")[:7] == month_prefix:
            month_cost += amt

    return success({
        # 全量（超管/管理员）
        "userCount": await db.users.count_documents({}),
        "productCount": await db.products.count_documents({}),
        "newsCount": await db.news.count_documents({}),
        "caseCount": await db.cases.count_documents({}),
        "assetCount": await db.finance_assets.count_documents({}),
        "repairCount": await db.repairs.count_documents({}),
        "todayRepairs": await db.repairs.count_documents({"createTime": {"$regex": _today()}}),
        "pendingLeads": await db.leads.count_documents({"status": "待跟进"}),
        "pendingComplaints": await db.complaints.count_documents({"status": "待处理"}),
        # 工单状态分布
        "pendingAssign": await db.repairs.count_documents({"status": "待接单"}),
        "processing": await db.repairs.count_documents({"status": "处理中"}),
        "pendingConfirm": await db.repairs.count_documents({"status": "待确认"}),
        "archived": await db.repairs.count_documents({"status": {"$in": _SETTLED}}),
        # 成本
        "monthCost": round(month_cost, 2),
        "totalCost": round(total_cost, 2),
        # 我的（按创建人或被指派）
        "myCreated": await db.repairs.count_documents({"createdBy": uname}),
        "myAssigned": await db.repairs.count_documents({"engineerId": uid}),
        "todaySchedules": await db.repair_schedule.count_documents({"date": _today()}),
    })


@router.get("/trends")
async def get_dashboard_trends(
    type: str = "repair",
    days: int = 7,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """返回最近 N 天（默认 7 天）的报修量 / 线索量 / 成本趋势"""
    days = max(1, min(days, 30))
    now = now_cn()
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

    costs = await _cost_series(db, dates)

    return success({
        "dates": dates,
        "repairs": [repair_counts[d] for d in dates],
        "leads": [lead_counts[d] for d in dates],
        "costs": [round(costs[d], 2) for d in dates],
    })


@router.get("/cost")
async def get_dashboard_cost(
    days: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """成本概览：本月/累计成本、费用方式分布、最近 N 天成本趋势（仅已结工单）"""
    month_prefix = now_cn().strftime("%Y-%m")
    now = now_cn()
    dates = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]

    month_total = 0.0
    grand_total = 0.0
    archived_count = 0
    pending_confirm = 0
    by_mode = {"agreed": 0.0, "self": 0.0}
    daily = {d: 0.0 for d in dates}

    async for r in db.repairs.find({}):
        st = r.get("status", "")
        if st in _SETTLED:
            archived_count += 1
            amt = _fee_amount(r)
            if amt:
                grand_total += amt
                mode = (r.get("fee") or {}).get("mode", "self")
                if mode in by_mode:
                    by_mode[mode] += amt
                d = (_settled_date(r) or "")[:10]
                if d in daily:
                    daily[d] += amt
                if (_settled_date(r) or "").startswith(month_prefix):
                    month_total += amt
        elif st == "待确认":
            pending_confirm += 1

    return success({
        "monthTotal": round(month_total, 2),
        "grandTotal": round(grand_total, 2),
        "archivedCount": archived_count,
        "pendingConfirm": pending_confirm,
        "byMode": [
            {"name": "已协商好", "value": round(by_mode["agreed"], 2)},
            {"name": "自行协商", "value": round(by_mode["self"], 2)},
        ],
        "trend": {"dates": dates, "values": [round(daily[d], 2) for d in dates]},
    })


@router.get("/schedule-today")
async def get_schedule_today(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """今日排期（横向时间轴用）"""
    today = _today()
    cursor = db.repair_schedule.find({"date": today}).sort("timeSlot", 1)
    items = []
    async for s in cursor:
        items.append({
            "id": str(s["_id"]),
            "engineer": s.get("engineer", ""),
            "timeSlot": s.get("timeSlot", ""),
            "company": s.get("company", ""),
            "type": s.get("type", ""),
            "status": s.get("status", ""),
        })
    return success(items)


@router.get("/todos")
async def get_dashboard_todos(db: AsyncIOMotorDatabase = Depends(get_db)):
    # 待接单工单（未指派，需管理员分派）
    repairs_cursor = db.repairs.find({"status": "待接单"}).limit(5).sort("_id", -1)
    repairs = []
    async for r in repairs_cursor:
        repairs.append({"id": str(r["_id"]), "orderNo": r.get("orderNo", ""), "company": r.get("company", ""), "status": r.get("status", ""), "createTime": r.get("createTime", "")})

    # 待确认归档工单（财务/业务需处理）
    confirming_cursor = db.repairs.find({"status": "待确认"}).limit(5).sort("_id", -1)
    confirming = []
    async for r in confirming_cursor:
        confirming.append({"id": str(r["_id"]), "orderNo": r.get("orderNo", ""), "company": r.get("company", ""), "status": r.get("status", ""), "createTime": r.get("createTime", "")})

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

    # 车辆到期提醒（保险/年检/保养，已逾期或 30 天内到期）
    vehicles = await _vehicle_reminders(db)

    return success({"repairs": repairs, "confirming": confirming, "leads": leads, "complaints": complaints, "vehicles": vehicles})


# ─── 辅助函数 ───────────────────────────────────────

def _today() -> str:
    return now_cn().strftime("%Y-%m-%d")


def _fee_amount(r: dict) -> float:
    fee = r.get("fee") or {}
    try:
        return float(fee.get("amount") or 0)
    except (TypeError, ValueError):
        return 0.0


def _settled_date(r: dict) -> str:
    """结算日期：优先归档时间，其次完结时间，兜底创建时间"""
    return (r.get("confirmedAt") or r.get("completedAt") or r.get("createTime") or "")[:10]


async def _cost_series(db: AsyncIOMotorDatabase, dates: list[str]) -> dict[str, float]:
    """按结算日汇总最近若干天的已结成本"""
    costs = {d: 0.0 for d in dates}
    async for r in db.repairs.find({"status": {"$in": _SETTLED}}):
        amt = _fee_amount(r)
        if not amt:
            continue
        d = _settled_date(r)
        if d in costs:
            costs[d] += amt
    return costs


def _ymd_days_left(ymd: str) -> int | None:
    """到期日距今天数：负=已逾期；空/非法返回 None"""
    if not ymd:
        return None
    try:
        return (datetime.strptime(str(ymd)[:10], "%Y-%m-%d").date() - now_cn().date()).days
    except ValueError:
        return None


async def _vehicle_reminders(db: AsyncIOMotorDatabase) -> list[dict]:
    """车辆到期提醒：保险/年检/保养 已逾期或 30 天内到期，按紧急度升序（上限 20 条）"""
    today = now_cn().date()
    rows = []
    async for v in db.finance_vehicles.find({"status": {"$ne": "已处置"}}):
        plate = v.get("plateNo", "")
        # 保险
        for ins in v.get("insurances") or []:
            dl = _ymd_days_left(ins.get("endDate"))
            if dl is not None and dl <= 30:
                rows.append((dl, plate, ins.get("type") or "保险", ins.get("endDate", "")))
        # 年检
        dl = _ymd_days_left(v.get("annualInspectionDate"))
        if dl is not None and dl <= 30:
            rows.append((dl, plate, "年检", v.get("annualInspectionDate", "")))
        # 保养
        dl = _ymd_days_left(v.get("nextMaintenanceDate"))
        if dl is not None and dl <= 30:
            rows.append((dl, plate, "保养", v.get("nextMaintenanceDate", "")))
    rows.sort(key=lambda x: x[0])
    return [
        {"plateNo": p, "label": lbl, "dueDate": due, "daysLeft": dl,
         "level": "overdue" if dl < 0 else "soon"}
        for dl, p, lbl, due in rows[:20]
    ]
