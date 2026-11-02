"""数据报表路由：工单统计 / 成本核算 / 线索转化 / 资产盘点 / 满意度（财务刚需）"""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success
from app.core.timeutil import now_cn

router = APIRouter(
    prefix="/reports",
    tags=["数据报表"],
    dependencies=[Depends(require_permission("report"))],
)

_SETTLED = ["已归档", "已完成"]


def _fee_amount(r: dict) -> float:
    fee = r.get("fee") or {}
    try:
        return float(fee.get("amount") or 0)
    except (TypeError, ValueError):
        return 0.0


def _settled_date(r: dict) -> str:
    return (r.get("confirmedAt") or r.get("completedAt") or r.get("createTime") or "")[:10]


def _parse_date(ymd: str):
    """解析 YYYY-MM-DD，失败返回 None"""
    try:
        return datetime.strptime((ymd or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_range(range_: str, start: str, end: str):
    """解析时间范围 → (开始日期, 结束日期, 分桶粒度 day|month)。
    统一使用北京时间；结束日期取「今日」，避免未到月末/季末导致窗口异常。"""
    today = now_cn().date()
    if range_ == "month":
        s = today.replace(day=1)
        e = today
        mode = "day"
    elif range_ == "quarter":
        q = (today.month - 1) // 3
        s = date(today.year, q * 3 + 1, 1)
        e = today
        mode = "month"
    else:  # year 或 custom
        if range_ == "year":
            s = date(today.year, 1, 1)
            e = today
        else:
            s = _parse_date(start) or date(today.year, 1, 1)
            e = _parse_date(end) or today
            if e < s:
                s, e = e, s
        mode = "month" if (e - s).days > 62 else "day"
    return s, e, mode


def _gen_buckets(s: date, e: date, mode: str) -> list:
    """生成时间桶标签：month → YYYY-MM，day → YYYY-MM-DD"""
    buckets = []
    if mode == "month":
        cur = date(s.year, s.month, 1)
        end = date(e.year, e.month, 1)
        while cur <= end:
            buckets.append(cur.strftime("%Y-%m"))
            cur = date(cur.year + 1, 1, 1) if cur.month == 12 else date(cur.year, cur.month + 1, 1)
    else:
        cur = s
        while cur <= e:
            buckets.append(cur.strftime("%Y-%m-%d"))
            cur += timedelta(days=1)
    return buckets


def _bucket_key(ymd: str, mode: str) -> str:
    return ymd[:7] if mode == "month" else ymd[:10]


def _mom(cur, last):
    """环比百分比：上月为 0 时返回 None（前端隐藏环比标识）"""
    if not last:
        return None
    return round((cur - last) / last * 100, 1)


async def _trend_30d(db) -> dict:
    """近 30 天工单/线索/成本三序列（口径与 dashboard 一致）"""
    today = now_cn().date()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
    start = dates[0]
    repair = {d: 0 for d in dates}
    lead = {d: 0 for d in dates}
    cost = {d: 0.0 for d in dates}

    async for r in db.repairs.find({"createTime": {"$gte": start}}):
        d = (r.get("createTime") or "")[:10]
        if d in repair:
            repair[d] += 1
    async for l in db.leads.find({"createTime": {"$gte": start}}):
        d = (l.get("createTime") or "")[:10]
        if d in lead:
            lead[d] += 1
    async for r in db.repairs.find({"status": {"$in": _SETTLED}}):
        amt = _fee_amount(r)
        if not amt:
            continue
        d = (_settled_date(r) or "")[:10]
        if d in cost:
            cost[d] += amt

    return {
        "dates": dates,
        "repairs": [repair[d] for d in dates],
        "leads": [lead[d] for d in dates],
        "costs": [round(cost[d], 2) for d in dates],
    }


async def _collect_todos(db) -> dict:
    """四类待办各取最近 5 条，供总览待办清单下钻"""
    async def _list(coll, filter_q, mapper, limit=5):
        out = []
        async for doc in getattr(db, coll).find(filter_q).limit(limit).sort("_id", -1):
            out.append(mapper(doc))
        return out

    return {
        "repairs": await _list("repairs", {"status": "待接单"}, lambda r: {
            "id": str(r["_id"]), "orderNo": r.get("orderNo", ""), "company": r.get("company", ""),
            "status": r.get("status", ""), "createTime": r.get("createTime", ""),
        }),
        "confirming": await _list("repairs", {"status": "待确认"}, lambda r: {
            "id": str(r["_id"]), "orderNo": r.get("orderNo", ""), "company": r.get("company", ""),
            "status": r.get("status", ""), "createTime": r.get("createTime", ""),
        }),
        "leads": await _list("leads", {"status": "待跟进"}, lambda l: {
            "id": str(l["_id"]), "name": l.get("name", ""), "category": l.get("category", ""),
            "status": l.get("status", ""), "createTime": l.get("createTime", ""),
        }),
        "complaints": await _list("complaints", {"status": "待处理"}, lambda c: {
            "id": str(c["_id"]), "customer": c.get("customer", c.get("contact", "")),
            "category": c.get("category", c.get("type", "")), "content": c.get("content", ""),
            "status": c.get("status", ""),
        }),
    }


@router.get("/summary")
async def get_report_summary(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """总览：分组 KPI（含环比）+ 近 30 天趋势 + 工单状态分布 + 待办清单。
    口径说明：总览保持「全量累计」，不随顶部时间切换器变化；趋势固定近 30 天。"""
    today = now_cn().date()
    month_prefix = today.strftime("%Y-%m")
    last_month_end = date(today.year, today.month, 1) - timedelta(days=1)
    last_month_prefix = last_month_end.strftime("%Y-%m")

    # 工单：一次遍历统计状态计数 + 本月/上月新建量 + 累计已结成本
    status_counter = {"待接单": 0, "处理中": 0, "待确认": 0, "已归档": 0}
    repair_total = 0
    month_repair = 0
    last_repair = 0
    cost_total = 0.0
    month_cost = 0.0
    last_cost = 0.0
    async for r in db.repairs.find({}):
        repair_total += 1
        st = r.get("status", "")
        if st == "待接单":
            status_counter["待接单"] += 1
        elif st == "处理中":
            status_counter["处理中"] += 1
        elif st == "待确认":
            status_counter["待确认"] += 1
        elif st in _SETTLED:
            status_counter["已归档"] += 1

        ym = (r.get("createTime") or "")[:7]
        if ym == month_prefix:
            month_repair += 1
        elif ym == last_month_prefix:
            last_repair += 1

        if st in _SETTLED:
            amt = _fee_amount(r)
            cost_total += amt
            sm = (_settled_date(r) or "")[:7]
            if sm == month_prefix:
                month_cost += amt
            elif sm == last_month_prefix:
                last_cost += amt

    # 线索：总数 + 待跟进 + 本月/上月新建量
    lead_total = 0
    pending_lead = 0
    month_lead = 0
    last_lead = 0
    async for l in db.leads.find({}):
        lead_total += 1
        if l.get("status") == "待跟进":
            pending_lead += 1
        ym = (l.get("createTime") or "")[:7]
        if ym == month_prefix:
            month_lead += 1
        elif ym == last_month_prefix:
            last_lead += 1

    complaint_total = await db.complaints.count_documents({})
    pending_complaint = await db.complaints.count_documents({"status": "待处理"})
    asset_total = await db.finance_assets.count_documents({})

    return success({
        "repairTotal": repair_total,
        "pendingAssign": status_counter["待接单"],
        "processing": status_counter["处理中"],
        "pendingConfirm": status_counter["待确认"],
        "archived": status_counter["已归档"],
        "costTotal": round(cost_total, 2),
        "monthCost": round(month_cost, 2),
        "lastMonthCost": round(last_cost, 2),
        "costMoM": _mom(month_cost, last_cost),
        "monthRepair": month_repair,
        "lastMonthRepair": last_repair,
        "repairMoM": _mom(month_repair, last_repair),
        "monthLead": month_lead,
        "lastMonthLead": last_lead,
        "leadMoM": _mom(month_lead, last_lead),
        "assetTotal": asset_total,
        "leadTotal": lead_total,
        "pendingLead": pending_lead,
        "complaintTotal": complaint_total,
        "pendingComplaint": pending_complaint,
        "statusDist": [
            {"name": "待接单", "value": status_counter["待接单"]},
            {"name": "处理中", "value": status_counter["处理中"]},
            {"name": "待确认", "value": status_counter["待确认"]},
            {"name": "已归档", "value": status_counter["已归档"]},
        ],
        "trend": await _trend_30d(db),
        "todos": await _collect_todos(db),
    })


@router.get("/repairs")
async def get_report_repairs(
    range: str = "year",
    start: str = "",
    end: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """工单统计（按完结时间口径）：完结工单量 / 工程师折线 / 客户 Top / 分布"""
    s, e, mode = _parse_range(range, start, end)
    buckets = _gen_buckets(s, e, mode)
    bucket_set = set(buckets)

    total = 0
    engineer_buckets = {}   # 工程师 -> {桶: 完结量}
    customer_count = {}     # 客户 -> 上门次数
    by_priority = {}
    by_work_type = {}
    by_device = {}
    duration_sum = 0.0
    duration_n = 0
    rework_count = 0
    active_engineers = set()

    async for r in db.repairs.find({"status": {"$in": _SETTLED}}):
        ymd = (_settled_date(r) or "")[:10]
        key = _bucket_key(ymd, mode)
        if key not in bucket_set:
            continue
        total += 1

        eng = (r.get("engineer") or "").strip() or "未指派"
        eng_data = engineer_buckets.setdefault(eng, {k: 0 for k in buckets})
        eng_data[key] += 1
        if eng != "未指派":
            active_engineers.add(eng)

        comp = (r.get("company") or "").strip()
        if comp:
            customer_count[comp] = customer_count.get(comp, 0) + 1

        p = r.get("priority") or "普通"
        by_priority[p] = by_priority.get(p, 0) + 1
        wt = r.get("workOrderType") or "其他"
        by_work_type[wt] = by_work_type.get(wt, 0) + 1
        dv = r.get("deviceType") or "其他"
        by_device[dv] = by_device.get(dv, 0) + 1

        if r.get("isRework") or (r.get("reworkCount") or 0) > 0:
            rework_count += 1

        cdate = _parse_date((r.get("createTime") or "")[:10])
        sdate = _parse_date(ymd)
        if cdate and sdate:
            duration_sum += (sdate - cdate).days
            duration_n += 1

    # Top5 工程师（按完结总量排序），数据对齐 buckets
    top_engineers = sorted(engineer_buckets.items(), key=lambda kv: -sum(kv[1].values()))[:5]
    engineer_series = [
        {"name": eng, "data": [data[k] for k in buckets]}
        for eng, data in top_engineers
    ]

    avg_days = round(duration_sum / duration_n, 1) if duration_n else 0

    return success({
        "range": range,
        "start": s.isoformat(),
        "end": e.isoformat(),
        "buckets": buckets,
        "total": total,
        "avgDurationDays": avg_days,
        "reworkCount": rework_count,
        "activeEngineers": len(active_engineers),
        "engineerSeries": engineer_series,
        "topCustomers": [
            {"name": k, "value": v}
            for k, v in sorted(customer_count.items(), key=lambda x: -x[1])[:10]
        ],
        "byPriority": [{"name": k, "value": v} for k, v in sorted(by_priority.items(), key=lambda x: -x[1])],
        "byWorkOrderType": [{"name": k, "value": v} for k, v in sorted(by_work_type.items(), key=lambda x: -x[1])],
        "byDeviceType": [{"name": k, "value": v} for k, v in sorted(by_device.items(), key=lambda x: -x[1])],
    })


@router.get("/cost")
async def get_report_cost(
    range: str = "year",
    start: str = "",
    end: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """成本核算（按完结时间口径）：累计成本 / 平均客单价 / 成本与工单量双轴 / 按工程师 / 按费用方式"""
    s, e, mode = _parse_range(range, start, end)
    buckets = _gen_buckets(s, e, mode)
    bucket_set = set(buckets)

    grand = 0.0
    cost_orders = 0
    cost_monthly = {k: 0.0 for k in buckets}
    order_monthly = {k: 0 for k in buckets}
    by_engineer = {}   # 工程师 -> {"cost": float, "count": int}
    by_mode = {}

    async for r in db.repairs.find({"status": {"$in": _SETTLED}}):
        ymd = (_settled_date(r) or "")[:10]
        key = _bucket_key(ymd, mode)
        if key not in bucket_set:
            continue
        order_monthly[key] += 1
        amt = _fee_amount(r)
        if not amt:
            continue
        grand += amt
        cost_orders += 1
        cost_monthly[key] += amt
        eng = (r.get("engineer") or "").strip() or "未指派"
        e_d = by_engineer.setdefault(eng, {"cost": 0.0, "count": 0})
        e_d["cost"] += amt
        e_d["count"] += 1
        mode_ = (r.get("fee") or {}).get("mode", "self")
        by_mode[mode_] = by_mode.get(mode_, 0.0) + amt

    avg = round(grand / cost_orders, 2) if cost_orders else 0
    return success({
        "range": range,
        "start": s.isoformat(),
        "end": e.isoformat(),
        "grand": round(grand, 2),
        "avgOrderValue": avg,
        "settledCount": sum(order_monthly.values()),
        "buckets": buckets,
        "costMonthly": [round(cost_monthly[k], 2) for k in buckets],
        "orderMonthly": [order_monthly[k] for k in buckets],
        "byEngineer": [
            {"name": k, "cost": round(v["cost"], 2), "count": v["count"],
             "avg": round(v["cost"] / v["count"], 2) if v["count"] else 0}
            for k, v in sorted(by_engineer.items(), key=lambda x: -x[1]["cost"])[:10]
        ],
        "byMode": [{"name": "已协商好" if k == "agreed" else "自行协商", "value": round(v, 2)} for k, v in by_mode.items()],
    })


@router.get("/leads")
async def get_report_leads(
    range: str = "year",
    start: str = "",
    end: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """线索转化：线索/转化双轴趋势 + 分类转化率 + 状态分布（按 createTime 口径）"""
    s, e, mode = _parse_range(range, start, end)
    buckets = _gen_buckets(s, e, mode)
    bucket_set = set(buckets)

    total = 0
    converted = 0
    lead_monthly = {k: 0 for k in buckets}
    conv_monthly = {k: 0 for k in buckets}
    by_status = {}
    by_category = {}   # 分类 -> {"total": int, "converted": int}

    async for l in db.leads.find({}):
        ymd = (l.get("createTime") or "")[:10]
        key = _bucket_key(ymd, mode)
        if key not in bucket_set:
            continue
        total += 1
        lead_monthly[key] += 1

        st = l.get("status") or "未知"
        by_status[st] = by_status.get(st, 0) + 1
        cat = l.get("category") or "其他"
        c_d = by_category.setdefault(cat, {"total": 0, "converted": 0})
        c_d["total"] += 1

        # 已成交或存在关联工单号均视为已转化
        is_conv = st in ("已成交", "已转化") or bool(l.get("convertedOrderNo"))
        if is_conv:
            converted += 1
            conv_monthly[key] += 1
            c_d["converted"] += 1

    return success({
        "range": range,
        "start": s.isoformat(),
        "end": e.isoformat(),
        "total": total,
        "converted": converted,
        "conversionRate": round(converted / total * 100, 1) if total else 0,
        "buckets": buckets,
        "leadSeries": [lead_monthly[k] for k in buckets],
        "convertedSeries": [conv_monthly[k] for k in buckets],
        "byStatus": [{"name": k, "value": v} for k, v in sorted(by_status.items(), key=lambda x: -x[1])],
        "byCategory": [
            {"name": k, "value": v["total"], "converted": v["converted"],
             "rate": round(v["converted"] / v["total"] * 100, 1) if v["total"] else 0}
            for k, v in sorted(by_category.items(), key=lambda x: -x[1]["total"])
        ],
    })


@router.get("/assets")
async def get_report_assets(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """资产盘点：分类分布 + 状态分布"""
    total = await db.finance_assets.count_documents({})
    by_category = {}
    by_status = {}
    async for a in db.finance_assets.find({}):
        c = a.get("category") or "其他"
        by_category[c] = by_category.get(c, 0) + 1
        s = a.get("status") or "在用"
        by_status[s] = by_status.get(s, 0) + 1
    return success({
        "total": total,
        "byCategory": [{"name": k, "value": v} for k, v in sorted(by_category.items(), key=lambda x: -x[1])],
        "byStatus": [{"name": k, "value": v} for k, v in sorted(by_status.items(), key=lambda x: -x[1])],
    })


@router.get("/satisfaction")
async def get_report_satisfaction(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """满意度：投诉处理率 + 分类分布"""
    total = await db.complaints.count_documents({})
    resolved = await db.complaints.count_documents({"status": "已解决"})
    by_category = {}
    async for c in db.complaints.find({}):
        cat = c.get("category") or "其他"
        by_category[cat] = by_category.get(cat, 0) + 1
    return success({
        "total": total,
        "resolved": resolved,
        "resolveRate": round(resolved / total * 100, 1) if total else 0,
        "byCategory": [{"name": k, "value": v} for k, v in sorted(by_category.items(), key=lambda x: -x[1])],
    })
