"""我的待办中心路由：GET /todos

按角色聚合「该用户当前最该处理的事项」，是个人能力（登录即有、内容按角色过滤），
不占用权限位。前端 /todos 页面据此渲染分组卡片，点击条目一键跳转到对应处理页。
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success
from app.core.timeutil import now_cn

router = APIRouter(prefix="/todos", tags=["待办中心"])

# 每个角色需要聚合的待办分组（顺序即展示顺序）
_ROLE_GROUPS = {
    "super_admin": ["pending_assign", "pending_confirm", "pending_lead", "pending_complaint", "pending_user", "vehicle_expiring"],
    "admin": ["pending_assign", "pending_confirm", "pending_lead", "pending_complaint", "pending_user", "vehicle_expiring"],
    "business": ["my_pending_confirm", "my_pending_assign", "pending_lead", "pending_complaint"],
    "finance": ["pending_confirm", "vehicle_expiring"],
    "operation": ["pending_complaint"],
    "engineer": ["grab_pool", "my_processing"],
    "normal": ["my_repairs"],
}

# 分组元信息（title / link 用于前端展示与跳转）
_GROUP_META = {
    "pending_assign": {"title": "待接单工单", "subtitle": "等待指派 / 抢单", "link": "/after_sales/all-tasks"},
    "pending_confirm": {"title": "待确认归档", "subtitle": "已完结，等待确认归档", "link": "/after_sales/all-tasks"},
    "my_pending_confirm": {"title": "待我确认归档", "subtitle": "我负责确认的已完结工单", "link": "/after_sales/all-tasks"},
    "my_pending_assign": {"title": "我录入的待接单", "subtitle": "我发起、尚无工程师接单的工单", "link": "/after_sales/all-tasks"},
    "pending_lead": {"title": "待跟进线索", "subtitle": "需求单待跟进", "link": "/leads"},
    "pending_complaint": {"title": "待处理投诉", "subtitle": "投诉建议待处理", "link": "/after_sales/complaints"},
    "pending_user": {"title": "待审批用户", "subtitle": "注册申请待审批", "link": "/system/users"},
    "grab_pool": {"title": "待接单（抢单池）", "subtitle": "可抢的待接单工单", "link": "/after_sales/all-tasks"},
    "my_processing": {"title": "我的处理中", "subtitle": "指派给我的进行中工单", "link": "/after_sales/all-tasks"},
    "my_repairs": {"title": "我的报修", "subtitle": "我发起的报修进度", "link": "/after_sales/my-repairs"},
    "vehicle_expiring": {"title": "车辆到期提醒", "subtitle": "保险 / 年检 / 保养即将到期或已逾期", "link": "/finance/vehicles"},
}

_LIMIT = 50  # 单组最多返回条数
_VEHICLE_REMIND_DAYS = 30  # 车辆到期提醒：30 天内到期或已逾期


def _fmt_time(v) -> str:
    return (v or "") if isinstance(v, str) else ""


def _ymd_days_left(ymd) -> int | None:
    """到期日距今天数：负=已逾期、0=今天、正=未到期；空/非法返回 None（不触发提醒）"""
    if not ymd:
        return None
    try:
        return (datetime.strptime(str(ymd)[:10], "%Y-%m-%d").date() - now_cn().date()).days
    except ValueError:
        return None


async def _collect_vehicle_expiring(db: AsyncIOMotorDatabase) -> list[dict]:
    """车辆到期提醒：保险 / 年检 / 保养 即将到期(≤30天)或已逾期，按紧急度升序"""
    rows = []  # (days_left, title, subtitle)
    async for v in db.finance_vehicles.find({"status": {"$ne": "已处置"}}):
        plate = v.get("plateNo", "")
        # 保险（每张保单一项）
        for ins in v.get("insurances") or []:
            dl = _ymd_days_left(ins.get("endDate"))
            if dl is None or dl > _VEHICLE_REMIND_DAYS:
                continue
            detail = ins.get("insurer") or ins.get("policyNo") or ""
            sub = ins.get("endDate") + (f" · {detail}" if detail else "")
            rows.append((dl, f"{plate} · {ins.get('type') or '保险'}", sub))
        # 年检
        dl = _ymd_days_left(v.get("annualInspectionDate"))
        if dl is not None and dl <= _VEHICLE_REMIND_DAYS:
            rows.append((dl, f"{plate} · 年检", v.get("annualInspectionDate") or ""))
        # 下次保养
        dl = _ymd_days_left(v.get("nextMaintenanceDate"))
        if dl is not None and dl <= _VEHICLE_REMIND_DAYS:
            km = v.get("nextMaintenanceKm")
            sub = v.get("nextMaintenanceDate") or ""
            if km:
                sub += f" · {km}km"
            rows.append((dl, f"{plate} · 保养", sub))
    rows.sort(key=lambda x: x[0])
    items = []
    for dl, title, subtitle in rows[:_LIMIT]:
        if dl < 0:
            time = f"已逾期{-dl}天"
        elif dl == 0:
            time = "今日到期"
        else:
            time = f"剩{dl}天"
        items.append({
            "id": f"{title}-{subtitle}", "title": title, "subtitle": subtitle,
            "time": time, "link": "/finance/vehicles",
        })
    return items


async def _collect(db: AsyncIOMotorDatabase, key: str, user: dict) -> list[dict]:
    """按分组 key 拉取条目（返回 [{id,title,subtitle,time,link}]）"""
    uid = str(user.get("_id", ""))
    uname = user.get("username", "")
    meta = _GROUP_META[key]
    link = meta["link"]
    items = []

    if key in ("pending_assign", "grab_pool"):
        cursor = db.repairs.find({"status": "待接单"}).sort("_id", -1).limit(_LIMIT)
        async for r in cursor:
            items.append({
                "id": str(r["_id"]), "title": r.get("orderNo", ""), "subtitle": r.get("company", ""),
                "time": _fmt_time(r.get("createTime")), "link": link,
            })
    elif key == "pending_confirm":
        cursor = db.repairs.find({"status": "待确认"}).sort("_id", -1).limit(_LIMIT)
        async for r in cursor:
            items.append({
                "id": str(r["_id"]), "title": r.get("orderNo", ""), "subtitle": r.get("company", ""),
                "time": _fmt_time(r.get("createTime")), "link": link,
            })
    elif key == "my_pending_confirm":
        # 业务「待我确认归档」：仅当前用户为确认人的待确认工单，深链到详情页操作
        cursor = db.repairs.find({"confirmUserId": uid, "status": "待确认"}).sort("_id", -1).limit(_LIMIT)
        async for r in cursor:
            rid = str(r["_id"])
            items.append({
                "id": rid, "title": r.get("orderNo", ""), "subtitle": r.get("company", ""),
                "time": _fmt_time(r.get("createTime")), "link": f"/after_sales/repair-detail/{rid}",
            })
    elif key == "my_pending_assign":
        # 业务「我录入的待接单」：自己发起、尚无工程师接单的工单，深链到详情页预约指派
        cursor = db.repairs.find({"createdBy": uname, "status": "待接单"}).sort("_id", -1).limit(_LIMIT)
        async for r in cursor:
            rid = str(r["_id"])
            items.append({
                "id": rid, "title": r.get("orderNo", ""), "subtitle": r.get("company", ""),
                "time": _fmt_time(r.get("createTime")), "link": f"/after_sales/repair-detail/{rid}",
            })
    elif key == "my_processing":
        cursor = db.repairs.find({"engineerId": uid, "status": "处理中"}).sort("_id", -1).limit(_LIMIT)
        async for r in cursor:
            items.append({
                "id": str(r["_id"]), "title": r.get("orderNo", ""), "subtitle": r.get("company", ""),
                "time": _fmt_time(r.get("createTime")), "link": link,
            })
    elif key == "my_repairs":
        cursor = db.repairs.find(
            {"createdBy": uname, "status": {"$in": ["待接单", "处理中", "待确认"]}}
        ).sort("_id", -1).limit(_LIMIT)
        async for r in cursor:
            items.append({
                "id": str(r["_id"]), "title": r.get("orderNo", ""), "subtitle": r.get("status", ""),
                "time": _fmt_time(r.get("createTime")), "link": link,
            })
    elif key == "pending_lead":
        cursor = db.leads.find({"status": "待跟进"}).sort("_id", -1).limit(_LIMIT)
        async for l in cursor:
            items.append({
                "id": str(l["_id"]), "title": l.get("name", ""), "subtitle": l.get("category", ""),
                "time": _fmt_time(l.get("createTime")), "link": link,
            })
    elif key == "pending_complaint":
        cursor = db.complaints.find({"status": "待处理"}).sort("_id", -1).limit(_LIMIT)
        async for c in cursor:
            items.append({
                "id": str(c["_id"]), "title": c.get("customer", ""), "subtitle": c.get("category", ""),
                "time": _fmt_time(c.get("date")), "link": link,
            })
    elif key == "pending_user":
        cursor = db.users.find({"status": "pending"}).sort("_id", -1).limit(_LIMIT)
        async for u in cursor:
            items.append({
                "id": str(u["_id"]), "title": u.get("realName", "") or u.get("username", ""),
                "subtitle": u.get("username", ""), "time": "", "link": link,
            })
    elif key == "vehicle_expiring":
        items = await _collect_vehicle_expiring(db)
    return items


@router.get("")
async def get_todos(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """聚合当前角色的待办分组；无分组的角色返回空列表"""
    role_code = user.get("roleCode", "")
    keys = _ROLE_GROUPS.get(role_code, [])
    groups = []
    for key in keys:
        items = await _collect(db, key, user)
        meta = _GROUP_META[key]
        groups.append({
            "key": key,
            "title": meta["title"],
            "subtitle": meta["subtitle"],
            "link": meta["link"],
            "count": len(items),
            "items": items,
        })
    return success({"groups": groups, "roleCode": role_code})
