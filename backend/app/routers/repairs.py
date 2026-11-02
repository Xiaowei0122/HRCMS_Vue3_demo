"""报修管理路由 — 报修 CRUD + 指派/接单/预约 + 完结/确认归档 + 费用 + 返修 + 转单 + 导出"""
import io
import re
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import openpyxl

from app.core.deps import get_db, get_current_user, require_permission, resolve_user_role, _resolve_role_code
from app.core.response import success, error, paginate
from app.core.security import generate_order_no
from app.core.timeutil import now_cn, now_str, now_min, today_str
from app.services import notify

router = APIRouter(tags=["报修管理"])

# RBAC 依赖（混合路由：不同端点不同权限 code）
_engineer = Depends(require_permission("repair:all"))
_create = Depends(require_permission("repair:create"))
_my = Depends(require_permission("repair:my"))
_schedule = Depends(require_permission("repair:schedule"))
_create_or_all = Depends(require_permission("repair:create", "repair:all"))  # lookup
_my_or_all = Depends(require_permission("repair:my", "repair:all"))          # confirm/rework
# 只读/调阅（财务成本核算用）：可查看列表/详情/统计/排期并导出，无任何写操作
_audit = Depends(require_permission("repair:all", "repair:audit"))
_schedule_view = Depends(require_permission("repair:schedule", "repair:audit"))
_detail = Depends(require_permission("repair:my", "repair:all", "repair:audit"))


# ─── 报修 CRUD ──────────────────────────────────────

@router.post("/repairs")
async def create_repair(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _create,
):
    """创建一个报修工单 — 兼容前端字段名"""
    # 优先级映射 (前端 urgency → 后端 priority)
    urgency_map = {"urgent": "紧急", "normal": "普通", "low": "不急"}
    raw_urgency = body.get("urgency", "normal")
    priority = body.get("priority") or urgency_map.get(raw_urgency, "普通")

    work_order_type = body.get("workOrderType", "售后上门")
    device_type = body.get("deviceType", "")
    if work_order_type == "售后上门" and not device_type:
        return error(400, "售后上门工单请选择设备类型")

    doc = {
        "orderNo": generate_order_no(),
        "company": body.get("company", ""),
        "contact": body.get("contactName") or body.get("contact", ""),
        "phone": body.get("contactPhone") or body.get("phone", ""),
        "address": body.get("address", ""),
        "deviceType": device_type,
        "workOrderType": work_order_type,
        "priority": priority,
        "repairDate": body.get("repairDate", ""),
        "preferredTimeSlot": body.get("preferredTimeSlot", "全天"),
        "preferredDate": body.get("preferredDate", ""),
        "description": body.get("description", ""),
        "images": body.get("images", []),
        "latitude": _to_float(body.get("latitude")),
        "longitude": _to_float(body.get("longitude")),
        "fee": _build_fee(body.get("fee"), user),
        "engineer": body.get("engineer", ""),
        "engineerId": body.get("engineerId", ""),
        "status": "待接单",
        "progress": [
            {"node": "工单已创建，系统自动派发", "time": now_min(), "status": "done"},
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
        "scheduledDate": "",
        "scheduledTimeSlot": "",
        "slotSpan": 1,
        "acceptedAt": "",
        "escalated": False,
        "escalateReason": "",
        "escalatedBy": "",
        "escalatedAt": "",
        "transferRequest": None,
        "cancelledBy": "",
        "cancelledAt": "",
        "cancelReason": "",
        "cancelNote": "",
        "confirmUserId": "",
        "confirmUserName": "",
    }
    # 确认人：业务/客户本人报修 → 发起人自己；非业务角色（财务/运营/工程师/管理员/超管）→ 必选业务确认人
    # 「本人工单」：工程师本人接电话直接建单 → 记本人名下、无需接单/指派、本人自行归档
    user_role = _resolve_role_code(user)
    self_order = bool(body.get("selfOrder")) and user_role == "engineer"
    confirm_user_id = (body.get("confirmUserId") or "").strip()
    confirm_user_name = (body.get("confirmUserName") or "").strip()
    if self_order:
        confirm_user_id = str(user.get("_id", ""))
        confirm_user_name = user.get("realName", user.get("username", ""))
    elif user_role in ("business", "normal"):
        confirm_user_id = str(user.get("_id", ""))
        confirm_user_name = user.get("realName", user.get("username", ""))
    elif not confirm_user_id:
        return error(400, "请选择业务确认人")
    # 兜底：仅传 id 时按 id 补确认人姓名
    if confirm_user_id and not confirm_user_name:
        try:
            cu = await db.users.find_one({"_id": ObjectId(confirm_user_id)})
            if cu:
                confirm_user_name = cu.get("realName", cu.get("username", ""))
        except Exception:
            pass
    doc["confirmUserId"] = confirm_user_id
    doc["confirmUserName"] = confirm_user_name

    # 内部人员直接预约：工程师 + 预约日期 + 具体时段齐全且空闲 → 「已预约」并锁定该时段
    # 不填或填「全天」→ 进抢单池（待接单，工程师自主接单）
    engineer_id = (body.get("engineerId") or "").strip()
    engineer_name = (body.get("engineerName") or "").strip()
    preferred_date = doc.get("preferredDate", "")
    preferred_slot = doc.get("preferredTimeSlot", "全天")
    if engineer_id and not engineer_name:
        try:
            eng = await db.users.find_one({"_id": ObjectId(engineer_id), "roleCode": "engineer"})
            if eng:
                engineer_name = eng.get("realName", eng.get("username", ""))
        except Exception:
            pass
    if self_order:
        doc["engineer"] = user.get("realName", user.get("username", ""))
        doc["engineerId"] = str(user.get("_id", ""))
        doc["status"] = "处理中"
        doc["progress"].append({
            "node": "本人工单：工程师直接接单并开始处理",
            "time": now_min(),
            "status": "done",
        })
    elif engineer_id and engineer_name and preferred_date and preferred_slot != "全天":
        if await _slot_occupied(db, engineer_id, preferred_date, preferred_slot):
            return error(409, "该工程师该时段已被占用，请选择其他时段")
        doc["engineer"] = engineer_name
        doc["engineerId"] = engineer_id
        doc["status"] = "已预约"
        doc["reservedBy"] = user.get("realName", user.get("username", ""))
        doc["reservedAt"] = now_str()
        doc["progress"].append({
            "node": f"已预约工程师 [{engineer_name}] 上门 {preferred_date} {preferred_slot}，等待工程师接单",
            "time": now_min(),
            "status": "done",
        })

    result = await db.repairs.insert_one(doc)

    # 直接预约成功后写入排期（锁定该时段，避免重复预约）
    if doc.get("status") == "已预约" and doc.get("engineerId"):
        await db.repair_schedule.insert_one({
            "engineerId": doc["engineerId"],
            "engineer": doc["engineer"],
            "date": doc.get("preferredDate", ""),
            "timeSlot": preferred_slot,
            "type": "business",
            "company": doc.get("company", ""),
            "repairId": str(result.inserted_id),
            "status": "已预约",
            "createdAt": now_str(),
        })
        await notify.push_notify(
            db,
            type_="repair_reserve",
            title="新工单预约",
            content=f"工单 {doc.get('orderNo', '')}（{doc.get('company', '')}）已预约给你 {preferred_date} {preferred_slot}，请接单",
            link=f"/after_sales/repair-detail/{str(result.inserted_id)}",
            user_ids=[doc["engineerId"]],
        )
    elif doc.get("status") == "待接单":
        # 普通建单进入抢单池：提醒管理员「待指派」、提醒工程师「待接单」
        await notify.push_notify(
            db,
            type_="repair_new_unassigned",
            title="新工单待指派",
            content=f"工单 {doc.get('orderNo', '')}（{doc.get('company', '')}）已进入待接单，请指派工程师",
            link="/after_sales/all-tasks?status=待接单",
            role_codes=["admin", "super_admin"],
        )
        await notify.push_notify(
            db,
            type_="repair_new_pending",
            title="新工单待接单",
            content=f"工单 {doc.get('orderNo', '')}（{doc.get('company', '')}）等待接单",
            link="/after_sales/all-tasks?status=待接单",
            role_codes=["engineer"],
        )

    return success({"id": str(result.inserted_id), "orderNo": doc["orderNo"]}, "报修工单创建成功")


@router.get("/repairs/my")
async def get_my_repairs(
    page: int = 1,
    size: int = 10,
    status: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _my,
):
    """获取当前用户的报修列表（联系人匹配 或 创建人匹配）"""
    user_name = user.get("username", "")
    user_real = user.get("realName", user_name)
    filter_q = {"$or": [{"contact": user_real}, {"createdBy": user_name}]}
    if status:
        filter_q["status"] = status
    return await _list_repairs(db, filter_q, page, size)


@router.get("/repairs/my/stats")
async def get_my_repair_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _my,
):
    """当前用户的报修统计（工程师按 engineerId，其余按联系人/创建人）"""
    if _resolve_role_code(user) == "engineer":
        base = {"engineerId": str(user.get("_id", ""))}
    else:
        uname = user.get("username", "")
        real = user.get("realName", uname)
        base = {"$or": [{"contact": real}, {"createdBy": uname}]}

    async def _count(extra=None):
        q = dict(base)
        if extra:
            q.update(extra)
        return await db.repairs.count_documents(q)

    return success({
        "total": await _count(),
        "pending": await _count({"status": "待接单"}),
        "processing": await _count({"status": "处理中"}),
        "confirming": await _count({"status": "待确认"}),
        "completed": await _count({"status": {"$in": ["已完成", "已归档"]}}),
    })


@router.get("/repairs")
async def get_repair_list(
    page: int = 1,
    size: int = 10,
    status: str = "",
    company: str = "",
    workOrderType: str = "",
    isRework: bool | None = None,
    engineerId: str = "",
    startDate: str = "",
    endDate: str = "",
    pendingFor: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _audit,
):
    """获取全部工单列表（管理员/工程师/财务调阅；可按工程师/日期过滤）

    pendingFor=<engineerId> 命中时返回「待接单」全局抢单池 + 指派给该工程师的「已预约」单
    （工程师「待接单」视图；此时忽略 status 过滤）。
    """
    filter_q = _build_filter(status, company, workOrderType, isRework, engineerId, startDate, endDate, pendingFor)
    return await _list_repairs(db, filter_q, page, size)


@router.get("/repairs/stats")
async def get_repair_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _audit,
):
    """报修统计数据"""
    return success({
        "total": await db.repairs.count_documents({}),
        "pending": await db.repairs.count_documents({"status": "待接单"}),
        "reserved": await db.repairs.count_documents({"status": "已预约"}),
        "processing": await db.repairs.count_documents({"status": "处理中"}),
        "confirming": await db.repairs.count_documents({"status": "待确认"}),
        "completed": await db.repairs.count_documents({"status": {"$in": ["已完成", "已归档"]}}),
        "archived": await db.repairs.count_documents({"status": "已归档"}),
        "done": await db.repairs.count_documents({"status": "已完成"}),
    })


# ─── 排期（静态路由，必须在参数化路由 /repairs/{repair_id} 之前）───

@router.get("/repairs/schedule")
async def get_engineer_schedule(
    engineerId: str = "",
    date: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _schedule_view,
):
    """获取工程师排期（财务可只读调阅）"""
    filter_q = {}
    if engineerId:
        filter_q["engineerId"] = engineerId
    if date:
        filter_q["date"] = date
    cursor = db.repair_schedule.find(filter_q).sort("_id", -1)
    records = []
    async for s in cursor:
        record = {
            "id": str(s["_id"]),
            "repairId": s.get("repairId", ""),
            "engineerId": s.get("engineerId", ""),
            "engineer": s.get("engineer", ""),
            "date": s.get("date", ""),
            "timeSlot": s.get("timeSlot", ""),
            "slotSpan": s.get("slotSpan", 1) or 1,
            "type": s.get("type", ""),
            "company": s.get("company", ""),
            "note": s.get("note", ""),
            "status": s.get("status", ""),
            "acceptedAt": s.get("acceptedAt", ""),
            "orderNo": "",
            "description": "",
            "repairStatus": "",
            "escalated": False,
            "escalateReason": "",
            "progress": [],
        }
        # 关联查询 repair 获取工单详情
        repair_id = s.get("repairId", "")
        if repair_id:
            try:
                repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
                if repair:
                    record["orderNo"] = repair.get("orderNo", "")
                    record["description"] = repair.get("description", "")
                    record["repairStatus"] = repair.get("status", "")
                    record["escalated"] = repair.get("escalated", False)
                    record["escalateReason"] = repair.get("escalateReason", "")
                    record["progress"] = repair.get("progress", [])
                    if not record["slotSpan"]:
                        record["slotSpan"] = repair.get("slotSpan", 1) or 1
                    if not record["acceptedAt"]:
                        record["acceptedAt"] = repair.get("acceptedAt", "")
            except Exception:
                pass
        records.append(record)
    return success(records)


# 时段顺序（每天 5 格，一单可占连续多格）
_SLOTS = ["AM1", "AM2", "PM1", "PM2", "PM3"]
_SLOT_IDX = {s: i for i, s in enumerate(_SLOTS)}


def _next_date(date_str: str) -> str:
    """YYYY-MM-DD → 次日（非法/空返回原值）"""
    try:
        return (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return date_str


# 时段 → 结束时间映射（用于判断当日已过期时段）
_SLOT_END_TIMES: dict[str, int] = {
    "AM1": 10,   # 08:30-10:00 → 10:00 后不可选
    "AM2": 12,   # 10:00-11:50 → 11:50≈12:00 后不可选
    "PM1": 15,   # 13:30-15:00 → 15:00 后不可选
    "PM2": 17,   # 15:00-16:30 → 16:30≈17:00 后不可选
    "PM3": 18,   # 16:30-18:00 → 18:00 后不可选
}


def _expired_slots_for_date(date_str: str) -> list[str]:
    """返回指定日期已过期的时段列表（仅当日有效，非当日返回空）"""
    if not date_str or date_str != today_str():
        return []
    now = now_cn()
    expired: list[str] = []
    for slot, end_hour in _SLOT_END_TIMES.items():
        if now.hour >= end_hour:
            expired.append(slot)
    return expired


@router.get("/repairs/schedule/availability")
async def get_schedule_availability(
    engineerId: str = "",
    date: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _audit,
):
    """返回某工程师某日已被占用的时段列表（接单/指派时灰显不可选时段）"""
    occupied: list[str] = []
    # 1. 当日已过期时段（如当前 23:42，当日所有时段均已过期）
    occupied.extend(_expired_slots_for_date(date))
    # 2. 数据库中已被占用的时段（含该工程师的异常锁定，status="已锁定"）
    filter_q = {"date": date}
    if engineerId:
        filter_q["engineerId"] = engineerId
    cursor = db.repair_schedule.find(filter_q)
    async for s in cursor:
        if s.get("status") in ("已结束", "已完成", "已归档"):
            continue
        ts = s.get("timeSlot", "")
        if not ts or ts == "全天":
            continue
        idx = _SLOT_IDX.get(ts)
        if idx is None:
            continue
        span = max(1, int(s.get("slotSpan", 1) or 1))
        for k in range(span):
            if idx + k < len(_SLOTS):
                occupied.append(_SLOTS[idx + k])
    return success({"occupied": list(set(occupied))})


@router.post("/repairs/schedule")
async def create_schedule_entry(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _schedule,
):
    """创建排期条目"""
    doc = {**body, "createdAt": now_str()}
    result = await db.repair_schedule.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "排期已创建")


@router.delete("/repairs/schedule/{schedule_id}")
async def delete_schedule_entry(
    schedule_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _schedule,
):
    """删除排期条目"""
    await db.repair_schedule.delete_one({"_id": ObjectId(schedule_id)})
    return success(None, "排期已删除")


# ─── 异常锁定 CRUD ──────────────────────────────────

@router.get("/repairs/schedule/locks")
async def get_schedule_locks(
    engineerId: str = "",
    date: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _schedule_view,
):
    """获取异常锁定列表（按工程师/日期过滤）"""
    filter_q = {"status": "已锁定"}
    if engineerId:
        filter_q["engineerId"] = engineerId
    if date:
        filter_q["date"] = date
    cursor = db.repair_schedule.find(filter_q).sort("date", 1)
    items = []
    async for s in cursor:
        s["id"] = str(s["_id"])
        items.append(s)
    return success(items)


@router.post("/repairs/schedule/locks")
async def create_schedule_lock(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _schedule,
):
    """创建异常锁定（培训/驻场/请假/其他，仅锁指定工程师）"""
    date = body.get("date", "")
    time_slot = body.get("timeSlot", "")
    lock_type = body.get("type", "other")  # training / onsite / leave / other
    engineer_id = body.get("engineerId", "")
    engineer_name = body.get("engineer", "")
    note = body.get("note", body.get("remark", ""))  # note 为主，兼容旧字段 remark

    if not date or not time_slot:
        return error(400, "日期和时段不能为空")
    if not engineer_id:
        return error(400, "锁定必须指定工程师 engineerId")
    if lock_type not in ("training", "onsite", "leave", "other"):
        return error(400, "锁定类型无效，可选：training/onsite/leave/other")

    # 检查冲突：该工程师该日该时段是否已有有效排期或锁定
    if await _slot_occupied(db, engineer_id, date, time_slot):
        return error(409, "该时段已被占用，无法锁定")

    doc = {
        "engineerId": engineer_id,
        "engineer": engineer_name,
        "date": date,
        "timeSlot": time_slot,
        "type": lock_type,
        "status": "已锁定",
        "note": note,
        "createdAt": now_str(),
        "createdBy": user.get("username", ""),
    }
    result = await db.repair_schedule.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "异常锁定已创建")


@router.delete("/repairs/schedule/locks/{lock_id}")
async def delete_schedule_lock(
    lock_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _schedule,
):
    """删除异常锁定"""
    r = await db.repair_schedule.find_one({"_id": ObjectId(lock_id), "status": "已锁定"})
    if not r:
        return error(404, "锁定记录不存在")
    await db.repair_schedule.delete_one({"_id": ObjectId(lock_id)})
    return success(None, "异常锁定已解除")


# ─── 工程师列表（静态路由，必须在 /repairs/{repair_id} 之前）─────

@router.get("/repairs/engineers")
async def get_repairs_engineers(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _audit,
):
    """获取工程师列表 — /repairs/engineers（前端 store 调用）"""
    return await _get_engineers(db)


@router.get("/repairs/confirmers")
async def get_repairs_confirmers(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _create,
):
    """获取确认人候选 — 业务用户（客户/后勤/管理员由发起人自动确定，不在此列）"""
    cursor = db.users.find({"roleCode": "business"})
    records = []
    async for u in cursor:
        records.append({
            "id": str(u["_id"]),
            "name": u.get("realName", u.get("username", "")),
            "username": u.get("username", ""),
        })
    return success(records)


# ─── 单位名匹配（静态路由，用于二次自动填充）─────────────

@router.get("/repairs/lookup")
async def lookup_company(
    company: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _create_or_all,
):
    """按单位名称匹配最近一条历史工单，返回基础信息供自动填充"""
    if not company.strip():
        return success({"found": False})
    r = await db.repairs.find_one(
        {"company": {"$regex": re.escape(company.strip()), "$options": "i"}},
        sort=[("_id", -1)],
    )
    if not r:
        return success({"found": False})
    return success({
        "found": True,
        "company": r.get("company", ""),
        "contact": r.get("contact", ""),
        "phone": r.get("phone", ""),
        "address": r.get("address", ""),
        "deviceType": r.get("deviceType", ""),
        "workOrderType": r.get("workOrderType", "售后上门"),
    })


# ─── 工单导出（静态路由，必须在 /repairs/{repair_id} 之前）─────

@router.get("/repairs/export")
async def export_repairs(
    status: str = "",
    company: str = "",
    workOrderType: str = "",
    startDate: str = "",
    endDate: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _audit,
):
    """导出工单 Excel（openpyxl，财务可只读导出）"""
    filter_q = _build_filter(status, company, workOrderType)
    if startDate:
        filter_q["createTime"] = {**filter_q.get("createTime", {}), "$gte": startDate + " 00:00:00"}
    if endDate:
        filter_q["createTime"] = {**filter_q.get("createTime", {}), "$lte": endDate + " 23:59:59"}

    # 时间区间校验：最多导出一年内的数据
    if startDate and endDate:
        try:
            _start = datetime.strptime(startDate, "%Y-%m-%d")
            _end = datetime.strptime(endDate, "%Y-%m-%d")
        except ValueError:
            return error(400, "日期格式不正确，应为 YYYY-MM-DD")
        if _end < _start:
            return error(400, "结束日期不能早于开始日期")
        if (_end - _start).days > 366:
            return error(400, "最多只能导出一年内的工单数据，请分次导出")

    cursor = db.repairs.find(filter_q).sort("_id", -1)
    repairs = []
    async for r in cursor:
        repairs.append(r)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "工单列表"
    ws.append([
        "工单号", "工单类型", "报修单位", "联系人", "电话", "地址", "设备类型",
        "紧急程度", "报修日期", "故障描述", "工程师", "状态", "费用金额", "费用方式",
        "支付方", "是否返修", "返修原单", "创建时间", "完结时间", "确认时间", "确认角色",
    ])
    for r in repairs:
        fee = r.get("fee") or {}
        ws.append([
            r.get("orderNo", ""),
            r.get("workOrderType", "售后上门"),
            r.get("company", ""),
            r.get("contact", ""),
            r.get("phone", ""),
            r.get("address", ""),
            r.get("deviceType", ""),
            r.get("priority", ""),
            r.get("repairDate", ""),
            r.get("description", ""),
            r.get("engineer", ""),
            r.get("status", ""),
            fee.get("amount", ""),
            fee.get("mode", ""),
            fee.get("paidBy", ""),
            "是" if r.get("isRework") else "否",
            r.get("reworkOf", ""),
            r.get("createTime", ""),
            r.get("completedAt", ""),
            r.get("confirmedAt", ""),
            r.get("confirmRole", ""),
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=repairs.xlsx"},
    )


# ─── 参数化路由（必须在所有静态路由之后）─────────────

@router.get("/repairs/{repair_id}")
async def get_repair_detail(
    repair_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _detail,
):
    """获取工单详情（本人/管理员/财务调阅）"""
    r = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not r:
        return error(404, "工单不存在")
    return success(_format_repair(r))


@router.patch("/repairs/{repair_id}/assign")
async def assign_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """指派工程师 — 仅管理员可指派任意工程师；同步到排期表（工程师请走「接单」）"""
    caller_role = await resolve_user_role(user, db)
    if not (caller_role and caller_role.get("rank", 99) <= 1):
        return error(403, "仅管理员可指派工程师，工程师请使用「接单」")

    eng_name = body.get("engineerName", "")
    eng_id = body.get("engineerId", "")
    if not eng_name or not eng_id:
        return error(400, "请选择工程师")

    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") not in ("待接单", "已预约"):
        return error(400, "仅「待接单/已预约」的工单可指派")

    schedule_date = body.get("date") or today_str()
    time_slot = body.get("timeSlot", "全天")
    slot_span = max(1, int(body.get("slotSpan", 1) or 1))
    escalate = bool(body.get("escalate"))
    escalate_reason = (body.get("escalateReason") or "").strip()
    if escalate and not escalate_reason:
        return error(400, "加急置顶需填写原因")

    # 清除直接预约产生的「已预约」排期条目，避免重复占位
    await db.repair_schedule.delete_many({"repairId": repair_id, "status": "已预约"})

    accepted_at = now_str()
    if escalate:
        # 加急置顶：写入排期后置顶重排（放不下自动顺延次日）
        await db.repair_schedule.insert_one({
            "engineerId": str(eng_id), "engineer": eng_name, "date": schedule_date,
            "timeSlot": time_slot if time_slot != "全天" else _SLOTS[0],
            "slotSpan": slot_span, "acceptedAt": accepted_at,
            "type": "business", "company": repair.get("company", ""),
            "repairId": repair_id, "status": "处理中", "createdAt": accepted_at,
        })
        blocks = await _get_day_blocks(db, str(eng_id), schedule_date)
        ordered = [b for b in blocks if b["repairId"] == repair_id] + [b for b in blocks if b["repairId"] != repair_id]
        assignments, _needs_manual = await _repack_and_apply(db, str(eng_id), schedule_date, ordered)
        final_date = assignments.get(repair_id, {}).get("date", schedule_date)
        final_slot = assignments.get(repair_id, {}).get("timeSlot", time_slot)
        await _notify_postpone(db, assignments, schedule_date)
    else:
        if await _slot_occupied(db, str(eng_id), schedule_date, time_slot, exclude_repair_id=repair_id, slot_span=slot_span):
            return error(409, "该工程师该时段已有工单/排期，请选择其他时段")
        existing = await db.repair_schedule.find_one({
            "engineerId": str(eng_id), "date": schedule_date, "repairId": repair_id
        })
        if not existing:
            await db.repair_schedule.insert_one({
                "engineerId": str(eng_id), "engineer": eng_name, "date": schedule_date,
                "timeSlot": time_slot, "slotSpan": slot_span, "acceptedAt": accepted_at,
                "type": "business", "company": repair.get("company", ""),
                "repairId": repair_id, "status": "处理中", "createdAt": accepted_at,
            })
        final_date, final_slot = schedule_date, time_slot

    update_set = {
        "engineer": eng_name, "engineerId": str(eng_id), "status": "处理中",
        "scheduledDate": final_date, "scheduledTimeSlot": final_slot, "slotSpan": slot_span,
        "acceptedAt": accepted_at,
    }
    if escalate:
        update_set["escalated"] = True
        update_set["escalateReason"] = escalate_reason
        update_set["escalatedBy"] = user.get("realName", user.get("username", ""))
        update_set["escalatedAt"] = accepted_at
    fee = body.get("fee")
    if isinstance(fee, dict) and fee.get("amount") is not None:
        update_set["fee"] = _build_fee(fee, user)
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": update_set},
    )
    await _add_progress(db, repair_id, f"管理员已指派工程师：{eng_name}", "done")

    await notify.push_notify(
        db,
        type_="repair_assign",
        title="新工单指派",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）已指派给你",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[str(eng_id)],
    )
    return success(None, "指派成功")


@router.patch("/repairs/{repair_id}/accept")
async def accept_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """工程师接单 — 自助接单并预约日期/时段；时段已被占用则拒绝"""
    if _resolve_role_code(user) != "engineer":
        return error(403, "仅工程师可接单")

    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") not in ("待接单", "已预约"):
        return error(400, "仅「待接单/已预约」的工单可接单")

    eng_doc = await db.users.find_one({"username": user.get("username", ""), "roleCode": "engineer"})
    if eng_doc:
        eng_name = eng_doc.get("realName", eng_doc.get("username", ""))
        eng_id = str(eng_doc["_id"])
    else:
        eng_name = user.get("realName", user.get("username", ""))
        eng_id = str(user.get("_id", ""))

    # 直接预约的工单（已绑定具体工程师）仅限该工程师接单
    reserved_eng_id = (repair.get("engineerId") or "").strip()
    if reserved_eng_id and reserved_eng_id != eng_id:
        return error(403, "该工单已预约给其他工程师，仅预约工程师可接单")

    date = body.get("date") or today_str()
    time_slot = body.get("timeSlot", "全天")
    slot_span = max(1, int(body.get("slotSpan", 1) or 1))
    escalate = bool(body.get("escalate"))
    escalate_reason = (body.get("escalateReason") or "").strip()
    reschedule_reason = (body.get("reason") or "").strip()
    if escalate and not escalate_reason:
        return error(400, "加急置顶需填写原因")

    # 清除直接预约产生的「已预约」排期条目，避免重复占位
    await db.repair_schedule.delete_many({"repairId": repair_id, "status": "已预约"})

    accepted_at = now_str()
    if escalate:
        # 加急置顶：写入排期后置顶重排（放不下自动顺延次日）
        await db.repair_schedule.insert_one({
            "engineerId": eng_id, "engineer": eng_name, "date": date,
            "timeSlot": time_slot if time_slot != "全天" else _SLOTS[0],
            "slotSpan": slot_span, "acceptedAt": accepted_at,
            "type": "business", "company": repair.get("company", ""),
            "repairId": repair_id, "status": "处理中", "createdAt": accepted_at,
        })
        blocks = await _get_day_blocks(db, eng_id, date)
        ordered = [b for b in blocks if b["repairId"] == repair_id] + [b for b in blocks if b["repairId"] != repair_id]
        assignments, _needs_manual = await _repack_and_apply(db, eng_id, date, ordered)
        final_date = assignments.get(repair_id, {}).get("date", date)
        final_slot = assignments.get(repair_id, {}).get("timeSlot", time_slot)
        await _notify_postpone(db, assignments, date)
    else:
        if await _slot_occupied(db, eng_id, date, time_slot, exclude_repair_id=repair_id, slot_span=slot_span):
            return error(409, "该时段已有工单/排期，请选择其他时段")
        await db.repair_schedule.insert_one({
            "engineerId": eng_id,
            "engineer": eng_name,
            "date": date,
            "timeSlot": time_slot,
            "slotSpan": slot_span,
            "acceptedAt": accepted_at,
            "type": "business",
            "company": repair.get("company", ""),
            "repairId": repair_id,
            "status": "处理中",
            "createdAt": accepted_at,
        })
        final_date, final_slot = date, time_slot

    update_set = {
        "engineer": eng_name, "engineerId": eng_id, "status": "处理中",
        "scheduledDate": final_date, "scheduledTimeSlot": final_slot, "slotSpan": slot_span,
        "acceptedAt": accepted_at,
    }
    if escalate:
        update_set["escalated"] = True
        update_set["escalateReason"] = escalate_reason
        update_set["escalatedBy"] = user.get("realName", user.get("username", ""))
        update_set["escalatedAt"] = accepted_at
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": update_set},
    )
    accept_node = f"工程师 [{eng_name}] 已接单，预约 {final_date} {final_slot}"
    if reschedule_reason:
        accept_node += f"（改派原因：{reschedule_reason}）"
    await _add_progress(db, repair_id, accept_node, "done")

    await notify.push_notify(
        db,
        type_="repair_accept",
        title="工单已被接单",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）已由 {eng_name} 接单，预约 {final_date} {final_slot}",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin", "business"],
    )
    return success(None, "接单成功")


@router.post("/repairs/{repair_id}/reserve/reject")
async def reject_reserved_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """退回预约工单 — 预约工程师退回「已预约」工单，工单返回「待接单」调度池，需填写原因"""
    if _resolve_role_code(user) != "engineer":
        return error(403, "仅工程师可退回预约工单")

    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") != "已预约":
        return error(400, "仅「已预约」的工单可退回")

    reserved_eng_id = (repair.get("engineerId") or "").strip()
    if reserved_eng_id and reserved_eng_id != str(user.get("_id", "")):
        return error(403, "该工单已预约给其他工程师，仅预约工程师可退回")

    reason = (body.get("reason") or "").strip()
    if not reason:
        return error(400, "请填写退回原因")

    operator = user.get("realName", user.get("username", ""))
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {
            "status": "待接单",
            "engineer": "",
            "engineerId": "",
            "reservedBy": "",
            "reservedAt": "",
        }},
    )
    # 清除直接预约产生的「已预约」排期条目，释放该时段
    await db.repair_schedule.delete_many({"repairId": repair_id, "status": "已预约"})
    await _add_progress(db, repair_id, f"工程师 [{operator}] 已退回预约工单，原因：{reason}", "done")

    await notify.push_notify(
        db,
        type_="repair_reserve_rejected",
        title="预约工单已退回",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）被 {operator} 退回，原因：{reason}",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin", "business"],
    )
    return success(None, "已退回预约工单，工单返回待接单")


@router.post("/repairs/{repair_id}/reserve")
async def reserve_repair(
    repair_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _create_or_all,
):
    """业务/内部人员确认预约 — 工单进入「已预约」，等待工程师接单确定时间"""
    if _resolve_role_code(user) == "normal":
        return error(403, "仅内部人员可预约工程师")

    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") != "待接单":
        return error(400, "仅「待接单」的工单可确认预约")

    operator = user.get("realName", user.get("username", ""))
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {"status": "已预约", "reservedBy": operator, "reservedAt": now_str()}},
    )
    await _add_progress(db, repair_id, f"{operator} 已确认预约，等待工程师接单", "done")
    await notify.push_notify(
        db,
        type_="repair_reserve",
        title="新工单待接单",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）已确认预约，请尽快接单",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["engineer"],
    )
    return success(None, "已确认预约，等待工程师接单")


@router.post("/repairs/{repair_id}/progress")
async def add_repair_progress(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """添加工单进度"""
    node = body.get("node", "")
    node_status = body.get("status", "doing")
    await _add_progress(db, repair_id, node, node_status)
    return success(None, "进度已添加")


@router.patch("/repairs/{repair_id}/complete")
async def complete_repair(
    repair_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """工程师完结工单 → 待确认（等待客户/业务确认归档）"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") != "处理中":
        return error(400, "仅「处理中」的工单可完结")

    now = now_str()
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {
            "status": "待确认",
            "completedBy": user.get("realName", user.get("username", "")),
            "completedAt": now,
            "archived": False,
        }},
    )
    # 释放排期时段：工程师完结后该时段立即可被新工单占用
    await db.repair_schedule.update_many(
        {"repairId": repair_id},
        {"$set": {"status": "已完成", "completedAt": now}},
    )
    await _add_progress(db, repair_id, "工单已处理完成，等待客户确认", "done")
    confirm_user_id = repair.get("confirmUserId", "")
    await notify.push_notify(
        db,
        type_="repair_confirm",
        title="工单待确认归档",
        content=f"工单 {repair.get('orderNo', '')} 已完结，等待确认归档",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[confirm_user_id] if confirm_user_id else [],
        role_codes=["admin", "super_admin"],
    )
    return success(None, "工单已完结，等待客户/业务确认归档")


@router.post("/repairs/{repair_id}/confirm")
async def confirm_repair(
    repair_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _my_or_all,
):
    """客户或业务确认归档 → 已归档"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") != "待确认":
        return error(400, "仅「待确认」的工单可确认归档")

    role = await resolve_user_role(user, db)
    code = role.get("code", "") if role else ""
    # 确认人本人可确认；管理员/超管兜底；旧数据（无确认人）回退到角色判断
    confirm_user_id = repair.get("confirmUserId", "")
    is_admin = code in ("admin", "super_admin")
    is_confirm_user = bool(confirm_user_id) and str(user.get("_id", "")) == str(confirm_user_id)
    legacy_ok = (not confirm_user_id) and (
        code == "business" or (code == "normal" and _is_owner(repair, user))
    )
    if not (is_admin or is_confirm_user or legacy_ok):
        return error(403, "仅确认人或管理员可确认归档")

    now = now_str()
    confirm_role = "customer" if code == "normal" else "business"
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {
            "status": "已归档",
            "confirmedBy": user.get("realName", user.get("username", "")),
            "confirmedAt": now,
            "confirmRole": confirm_role,
            "archived": True,
        }},
    )
    node = "客户已确认，工单归档" if confirm_role == "customer" else "业务已确认，工单归档"
    await _add_progress(db, repair_id, node, "done")
    # 排期标记为已归档（已完成→已归档，或处理中→已归档）
    await db.repair_schedule.update_many(
        {"repairId": repair_id},
        {"$set": {"status": "已归档"}},
    )
    await notify.push_notify(
        db,
        type_="repair_archived",
        title="工单已归档",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）已归档，可核算成本",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin", "finance"],
    )
    return success(None, "工单已归档")


@router.post("/repairs/{repair_id}/cancel")
async def cancel_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """工程师取消工单（处理中 → 已取消，终态；抄送发起人与管理员）"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") != "处理中":
        return error(400, "仅「处理中」的工单可取消")

    reason = (body.get("reason") or "").strip()
    if not reason:
        return error(400, "请填写取消原因")
    note = (body.get("note") or "").strip()

    now = now_str()
    operator = user.get("realName", user.get("username", ""))
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {
            "status": "已取消",
            "cancelledBy": operator,
            "cancelledAt": now,
            "cancelReason": reason,
            "cancelNote": note,
        }},
    )
    # 释放排期时段：取消后该时段可被新工单占用
    await db.repair_schedule.update_many(
        {"repairId": repair_id},
        {"$set": {"status": "已结束"}},
    )
    await _add_progress(db, repair_id, f"工单已取消（{reason}）", "done")

    # 抄送：发起人 + 管理员/超管；若取消方非工程师，额外通知对应工程师
    creator = await db.users.find_one({"username": repair.get("createdBy", "")})
    user_ids = [str(creator["_id"])] if creator else []
    if _resolve_role_code(user) != "engineer" and repair.get("engineerId"):
        eng_id = str(repair.get("engineerId"))
        if eng_id not in user_ids:
            user_ids.append(eng_id)
    await notify.push_notify(
        db,
        type_="repair_cancelled",
        title="工单已取消",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）已被 {operator} 取消（原因：{reason}）",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=user_ids,
        role_codes=["admin", "super_admin"],
    )
    return success(None, "工单已取消")


@router.patch("/repairs/{repair_id}/fee")
async def set_repair_fee(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """工程师填写/更新上门费用"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    mode = body.get("mode", "self")
    if mode not in ("agreed", "self"):
        return error(400, "费用方式不合法")
    amount = _to_float(body.get("amount"))
    if amount is None or amount < 0:
        return error(400, "请填写正确的费用金额")

    fee_doc = {
        "mode": mode,
        "amount": amount,
        "note": body.get("note", ""),
        "paidBy": body.get("paidBy", ""),
        "setBy": user.get("realName", user.get("username", "")),
        "settledAt": now_str(),
    }
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {"fee": fee_doc}},
    )
    return success(fee_doc, "费用已保存")


@router.post("/repairs/{repair_id}/rework")
async def rework_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _my_or_all,
):
    """返修：复制原单生成新工单并关联原单号"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if not _is_archived(repair.get("status")):
        return error(400, "仅已归档/已完成的工单可发起返修")

    role = await resolve_user_role(user, db)
    code = role.get("code", "") if role else ""
    if code not in ("normal", "business", "admin", "super_admin"):
        return error(403, "仅客户或业务可发起返修")
    if code == "normal" and not _is_owner(repair, user):
        return error(403, "无权对该工单发起返修")

    reason = body.get("reason", "其他")
    note = body.get("note", "")
    new_order_no = generate_order_no()
    now = now_cn()
    new_doc = {
        "orderNo": new_order_no,
        "company": repair.get("company", ""),
        "contact": repair.get("contact", ""),
        "phone": repair.get("phone", ""),
        "address": repair.get("address", ""),
        "deviceType": repair.get("deviceType", ""),
        "workOrderType": repair.get("workOrderType", "售后上门"),
        "priority": "普通",
        "repairDate": repair.get("repairDate", ""),
        "description": repair.get("description", ""),
        "images": [],
        "latitude": repair.get("latitude"),
        "longitude": repair.get("longitude"),
        "engineer": "",
        "engineerId": "",
        "status": "待接单",
        "progress": [
            {"node": f"返修工单已创建（原单：{repair.get('orderNo', '')}）", "time": now.strftime("%Y-%m-%d %H:%M"), "status": "done"},
        ],
        "createTime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "createdBy": user.get("username", ""),
        "isRework": True,
        "reworkOf": repair.get("orderNo", ""),
        "reworkReason": reason,
        "reworkNote": note,
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
        "cancelledBy": "",
        "cancelledAt": "",
        "cancelReason": "",
        "cancelNote": "",
        "confirmUserId": repair.get("confirmUserId", "") or str(user.get("_id", "")),
        "confirmUserName": repair.get("confirmUserName", "") or user.get("realName", user.get("username", "")),
    }
    result = await db.repairs.insert_one(new_doc)

    # 更新原单：返修计数 + 最新子单号 + 进度
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {
            "$inc": {"reworkCount": 1},
            "$set": {"reworkChildNo": new_order_no},
            "$push": {"progress": {"node": f"已发起返修 → {new_order_no}", "time": now.strftime("%Y-%m-%d %H:%M"), "status": "done"}},
        },
    )
    return success({"id": str(result.inserted_id), "orderNo": new_order_no}, "返修单已创建")


@router.patch("/repairs/{repair_id}/transfer")
async def transfer_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """转单申请 — 提交转单请求，待目标工程师接受后生效（保留历史节点）"""
    target_id = body.get("targetEngineerId", body.get("engineerId", ""))
    target_name = body.get("targetEngineerName", body.get("engineerName", ""))
    if not target_id:
        return error(400, "请选择目标工程师")

    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") != "处理中":
        return error(400, "仅「处理中」的工单可发起转单")

    cur_eng_id = str(repair.get("engineerId", ""))
    if str(target_id) == cur_eng_id:
        return error(400, "不能转单给当前处理人")

    if not target_name:
        t = await db.users.find_one({"_id": ObjectId(str(target_id))})
        if t:
            target_name = t.get("realName", t.get("username", ""))
    if not target_name:
        return error(400, "未找到目标工程师")

    from_name = repair.get("engineer", user.get("realName", user.get("username", "")))
    req = {
        "fromEngineer": from_name,
        "fromEngineerId": cur_eng_id,
        "toEngineer": target_name,
        "toEngineerId": str(target_id),
        "status": "pending",
        "requestedAt": now_str(),
        "resolvedAt": "",
    }
    await db.repairs.update_one({"_id": ObjectId(repair_id)}, {"$set": {"transferRequest": req}})
    await _add_progress(db, repair_id, f"工程师 [{from_name}] 提交转单申请，待 [{target_name}] 接受", "doing")
    await notify.push_notify(
        db,
        type_="repair_transfer",
        title="转单申请",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）由 {from_name} 转单给你，请处理",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[str(target_id)],
    )
    await notify.push_notify(
        db,
        type_="repair_transfer",
        title="转单申请",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）{from_name} → {target_name} 转单申请已提交",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin"],
    )
    return success(None, "转单申请已提交")


@router.post("/repairs/{repair_id}/transfer/accept")
async def accept_transfer(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """接受转单 — 目标工程师选择时段后接受，工单正式改派并同步排期"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    req = repair.get("transferRequest") or {}
    if req.get("status") != "pending":
        return error(400, "没有待处理的转单申请")
    if str(req.get("toEngineerId", "")) != str(user.get("_id", "")):
        return error(403, "仅目标工程师可接受转单")

    to_name = req.get("toEngineer", user.get("realName", user.get("username", "")))
    to_id = str(req.get("toEngineerId", ""))
    from_name = req.get("fromEngineer", "")
    from_id = str(req.get("fromEngineerId", ""))

    # 时段选择
    schedule_date = body.get("date") or today_str()
    time_slot = body.get("timeSlot", "全天")
    slot_span = max(1, int(body.get("slotSpan", 1) or 1))
    if await _slot_occupied(db, to_id, schedule_date, time_slot, exclude_repair_id=repair_id, slot_span=slot_span):
        return error(409, "该时段已有工单/排期，请选择其他时段")

    accepted_at = now_str()
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {
            "engineer": to_name,
            "engineerId": to_id,
            "scheduledDate": schedule_date,
            "scheduledTimeSlot": time_slot,
            "slotSpan": slot_span,
            "acceptedAt": accepted_at,
            "transferRequest": {**req, "status": "accepted", "resolvedAt": accepted_at,
                                "confirmedDate": schedule_date, "confirmedTimeSlot": time_slot},
        }},
    )
    await _add_progress(db, repair_id, f"工单已从 [{from_name}] 转派至 [{to_name}]，预约 {schedule_date} {time_slot}（转单完成）", "done")

    # 同步排期表：更新工程师 + 日期 + 时段
    await db.repair_schedule.update_many(
        {"repairId": repair_id},
        {"$set": {"engineerId": to_id, "engineer": to_name, "date": schedule_date, "timeSlot": time_slot, "slotSpan": slot_span, "acceptedAt": accepted_at}},
    )

    await notify.push_notify(
        db,
        type_="repair_transfer_done",
        title="转单已接受",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）已由 {to_name} 接受，预计 {schedule_date} {time_slot} 开始处理",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[from_id] if from_id else None,
    )
    await notify.push_notify(
        db,
        type_="repair_transfer_done",
        title="转单已完成",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）{from_name} → {to_name} 转单完成，{schedule_date} {time_slot}",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin"],
    )
    return success(None, "转单已接受")


@router.post("/repairs/{repair_id}/transfer/reject")
async def reject_transfer(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """退回转单 — 目标工程师退回，需填写原因，工单仍由原工程师处理"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    req = repair.get("transferRequest") or {}
    if req.get("status") != "pending":
        return error(400, "没有待处理的转单申请")
    if str(req.get("toEngineerId", "")) != str(user.get("_id", "")):
        return error(403, "仅目标工程师可退回转单")

    reject_reason = (body.get("reason") or "").strip()
    if not reject_reason:
        return error(400, "请填写退回原因")

    to_name = req.get("toEngineer", user.get("realName", user.get("username", "")))
    from_id = str(req.get("fromEngineerId", ""))
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {"transferRequest": {**req, "status": "rejected", "rejectReason": reject_reason, "resolvedAt": now_str()}}},
    )
    await _add_progress(db, repair_id, f"{to_name} 已退回转单申请，原因：{reject_reason}", "done")
    await notify.push_notify(
        db,
        type_="repair_transfer_rejected",
        title="转单申请已退回",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）的转单申请被 {to_name} 退回，原因：{reject_reason}",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[from_id] if from_id else None,
    )
    await notify.push_notify(
        db,
        type_="repair_transfer_rejected",
        title="转单申请已退回",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）转单申请被 {to_name} 退回，原因：{reject_reason}",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin"],
    )
    return success(None, "转单申请已退回")


@router.post("/repairs/{repair_id}/transfer/cancel")
async def cancel_transfer(
    repair_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """取消转单 — 原工程师撤销待处理的转单申请"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    req = repair.get("transferRequest") or {}
    if req.get("status") != "pending":
        return error(400, "没有待处理的转单申请")
    if str(req.get("fromEngineerId", "")) != str(user.get("_id", "")):
        return error(403, "仅发起人可取消转单")

    from_name = req.get("fromEngineer", user.get("realName", user.get("username", "")))
    to_id = str(req.get("toEngineerId", ""))
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {"transferRequest": {**req, "status": "cancelled", "resolvedAt": now_str()}}},
    )
    await _add_progress(db, repair_id, f"{from_name} 已取消转单申请", "done")
    await notify.push_notify(
        db,
        type_="repair_transfer_cancelled",
        title="转单申请已取消",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）的转单申请已被 {from_name} 取消",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[to_id] if to_id else None,
    )
    await notify.push_notify(
        db,
        type_="repair_transfer_cancelled",
        title="转单申请已取消",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）转单申请已被 {from_name} 取消",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin"],
    )
    return success(None, "转单申请已取消")


# ─── 预约指派（业务/管理员指定工程师，工程师确认时段）─────

@router.post("/repairs/{repair_id}/reserve-assign")
async def reserve_assign(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _create_or_all,
):
    """预约指派 — 业务/管理员指定工程师发起预约，待工程师确认时段"""
    if _resolve_role_code(user) == "normal":
        return error(403, "仅内部人员可发起预约指派")

    target_id = body.get("targetEngineerId", "")
    target_name = body.get("targetEngineerName", "")
    if not target_id or not target_name:
        return error(400, "请选择目标工程师")

    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") != "待接单":
        return error(400, "仅「待接单」的工单可发起预约指派")

    operator = user.get("realName", user.get("username", ""))
    req = {
        "targetEngineerId": str(target_id),
        "targetEngineerName": target_name,
        "preferredDate": body.get("preferredDate", ""),
        "preferredTimeSlot": body.get("preferredTimeSlot", ""),
        "note": body.get("note", ""),
        "requestedBy": operator,
        "requestedAt": now_str(),
        "status": "pending",
        "resolvedAt": "",
    }
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {"reservationRequest": req, "status": "预约中"}},
    )
    await _add_progress(db, repair_id, f"{operator} 已向工程师 [{target_name}] 发起预约指派", "doing")

    preferred_info = ""
    if req["preferredDate"]:
        preferred_info = f"，期望 {req['preferredDate']}"
        if req["preferredTimeSlot"]:
            preferred_info += f" {req['preferredTimeSlot']}"

    await notify.push_notify(
        db,
        type_="repair_reserve_assign",
        title="工单预约申请",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）由 {operator} 向您发起预约指派{preferred_info}，请确认处理时段",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[str(target_id)],
    )
    await notify.push_notify(
        db,
        type_="repair_reserve_assign",
        title="预约指派已发起",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）{operator} → {target_name} 预约指派已发起",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin"],
    )
    return success(None, "预约指派已发起")


@router.post("/repairs/{repair_id}/reserve-assign/accept")
async def accept_reserve_assign(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """确认预约 — 目标工程师确认时段，工单直接进入「处理中」"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    req = repair.get("reservationRequest") or {}
    if req.get("status") != "pending":
        return error(400, "没有待处理的预约申请")
    if str(req.get("targetEngineerId", "")) != str(user.get("_id", "")):
        return error(403, "仅目标工程师可确认预约")

    eng_name = req.get("targetEngineerName", user.get("realName", user.get("username", "")))
    eng_id = str(req.get("targetEngineerId", ""))

    schedule_date = body.get("date") or today_str()
    time_slot = body.get("timeSlot", "全天")
    slot_span = max(1, int(body.get("slotSpan", 1) or 1))
    if await _slot_occupied(db, eng_id, schedule_date, time_slot, exclude_repair_id=repair_id, slot_span=slot_span):
        return error(409, "该时段已有工单/排期，请选择其他时段")

    accepted_at = now_str()
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {
            "engineer": eng_name,
            "engineerId": eng_id,
            "status": "处理中",
            "scheduledDate": schedule_date,
            "scheduledTimeSlot": time_slot,
            "slotSpan": slot_span,
            "acceptedAt": accepted_at,
            "reservationRequest": {**req, "status": "accepted", "resolvedAt": accepted_at,
                                   "confirmedDate": schedule_date, "confirmedTimeSlot": time_slot},
        }},
    )
    await _add_progress(db, repair_id, f"工程师 [{eng_name}] 已确认预约，{schedule_date} {time_slot} 开始处理", "done")

    # 写入排期表
    existing = await db.repair_schedule.find_one({
        "engineerId": eng_id, "date": schedule_date, "repairId": repair_id,
    })
    if not existing:
        await db.repair_schedule.insert_one({
            "engineerId": eng_id,
            "engineer": eng_name,
            "date": schedule_date,
            "timeSlot": time_slot,
            "slotSpan": slot_span,
            "acceptedAt": accepted_at,
            "type": "business",
            "company": repair.get("company", ""),
            "repairId": repair_id,
            "status": "处理中",
            "createdAt": accepted_at,
        })

    await notify.push_notify(
        db,
        type_="repair_reserve_assign_done",
        title="预约已确认",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）工程师 {eng_name} 已确认预约，预计 {schedule_date} {time_slot} 开始处理",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[str(req.get("requestedBy", ""))] if req.get("requestedBy") else None,
    )
    await notify.push_notify(
        db,
        type_="repair_reserve_assign_done",
        title="预约已确认",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）{eng_name} 已确认预约，{schedule_date} {time_slot}",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin"],
    )
    return success(None, "预约已确认，工单进入处理中")


@router.post("/repairs/{repair_id}/escalate")
async def escalate_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """加急置顶（插队）— 工程师本人当天 / 管理员全局；必填原因"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") != "处理中":
        return error(400, "仅「处理中」的工单可加急置顶")

    reason = (body.get("reason") or "").strip()
    if not reason:
        return error(400, "请填写加急原因")

    eng_id = str(body.get("targetEngineerId") or repair.get("engineerId", "") or "")
    if not eng_id:
        return error(400, "工单尚未指派工程师，无法置顶")

    caller_role = await resolve_user_role(user, db)
    is_admin = bool(caller_role and caller_role.get("rank", 99) <= 1)
    if not is_admin and str(eng_id) != str(user.get("_id", "")):
        return error(403, "仅可对自己当天的工单置顶")

    eng_name = body.get("targetEngineerName") or repair.get("engineer", "")
    if str(eng_id) != str(repair.get("engineerId", "")) or not eng_name:
        e = await db.users.find_one({"_id": ObjectId(eng_id)})
        if e:
            eng_name = e.get("realName", e.get("username", ""))
    if not eng_name:
        return error(400, "未找到目标工程师")

    target_date = body.get("targetDate") or repair.get("scheduledDate") or today_str()
    span = max(1, int(repair.get("slotSpan", 1) or 1))
    operator = user.get("realName", user.get("username", ""))
    now = now_str()

    # 换人时同步工程师字段
    if str(eng_id) != str(repair.get("engineerId", "")) or eng_name != repair.get("engineer", ""):
        await db.repairs.update_one(
            {"_id": ObjectId(repair_id)},
            {"$set": {"engineerId": eng_id, "engineer": eng_name}},
        )
        await db.repair_schedule.update_many(
            {"repairId": repair_id, "status": {"$nin": ["已结束", "已完成", "已归档"]}},
            {"$set": {"engineerId": eng_id, "engineer": eng_name}},
        )

    # 确保存在本单的有效排期块（repack 只 update，不 insert）
    active = await db.repair_schedule.find_one(
        {"repairId": repair_id, "status": {"$nin": ["已结束", "已完成", "已归档"]}}
    )
    if not active:
        await db.repair_schedule.insert_one({
            "engineerId": eng_id, "engineer": eng_name, "date": target_date,
            "timeSlot": _SLOTS[0], "slotSpan": span,
            "acceptedAt": repair.get("acceptedAt", "") or now,
            "type": "business", "company": repair.get("company", ""),
            "repairId": repair_id, "status": "处理中", "createdAt": now,
        })

    target_block = {"repairId": repair_id, "slotSpan": span, "acceptedAt": repair.get("acceptedAt", "") or now}
    blocks = await _get_day_blocks(db, eng_id, target_date)
    others = [b for b in blocks if b["repairId"] != repair_id]
    ordered = [target_block] + others
    assignments, needs_manual = await _repack_and_apply(db, eng_id, target_date, ordered)

    final = assignments.get(repair_id, {})
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {
            "escalated": True, "escalateReason": reason,
            "escalatedBy": operator, "escalatedAt": now,
            "scheduledDate": final.get("date", target_date),
            "scheduledTimeSlot": final.get("timeSlot", repair.get("scheduledTimeSlot", "")),
        }},
    )
    await _add_progress(db, repair_id, f"工单已加急置顶，原因：{reason}", "done")
    await _notify_postpone(db, assignments, target_date)

    msg = "已加急置顶"
    if needs_manual:
        msg += f"，另有 {len(needs_manual)} 个工单次日已满，请手动派时间"
    return success({"message": msg, "overflow": len(needs_manual)}, msg)


@router.post("/repairs/{repair_id}/reorder")
async def reorder_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """排期挪动 — top/up/down 当天内调整顺序；extend 拉长本单占格并顺延后续（溢出自动顺延次日）"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    if repair.get("status") != "处理中":
        return error(400, "仅「处理中」的工单可调整排期")

    direction = body.get("direction", "top")
    if direction not in ("top", "up", "down", "extend"):
        return error(400, "direction 仅支持 top/up/down/extend")

    eng_id = str(repair.get("engineerId", "") or "")
    if not eng_id:
        return error(400, "工单尚未指派工程师")

    caller_role = await resolve_user_role(user, db)
    is_admin = bool(caller_role and caller_role.get("rank", 99) <= 1)
    if not is_admin and str(eng_id) != str(user.get("_id", "")):
        return error(403, "仅可调整自己当天的排期")

    date = repair.get("scheduledDate") or today_str()
    blocks = await _get_day_blocks(db, eng_id, date)
    idx = next((i for i, b in enumerate(blocks) if b["repairId"] == repair_id), None)
    if idx is None:
        return error(400, "该工单当天未排期，无法调整")

    if direction == "extend":
        blocks[idx]["slotSpan"] = min(len(_SLOTS), blocks[idx]["slotSpan"] + 1)
        ordered = blocks
    elif direction == "top":
        ordered = [blocks[idx]] + blocks[:idx] + blocks[idx + 1:]
    elif direction == "up":
        if idx == 0:
            return error(400, "已在最前，无法上移")
        ordered = list(blocks)
        ordered[idx], ordered[idx - 1] = ordered[idx - 1], ordered[idx]
    else:  # down
        if idx == len(blocks) - 1:
            return error(400, "已在最后，无法下移")
        ordered = list(blocks)
        ordered[idx], ordered[idx + 1] = ordered[idx + 1], ordered[idx]

    assignments, needs_manual = await _repack_and_apply(db, eng_id, date, ordered)
    await _notify_postpone(db, assignments, date)

    msg = "排期已调整"
    if needs_manual:
        msg += f"，{len(needs_manual)} 个工单次日已满，请手动派时间"
    return success({"message": msg, "overflow": len(needs_manual)}, msg)


@router.post("/repairs/{repair_id}/reserve-assign/reject")
async def reject_reserve_assign(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """退回预约 — 目标工程师退回预约，需填写原因，工单回到「待接单」"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    req = repair.get("reservationRequest") or {}
    if req.get("status") != "pending":
        return error(400, "没有待处理的预约申请")
    if str(req.get("targetEngineerId", "")) != str(user.get("_id", "")):
        return error(403, "仅目标工程师可退回预约")

    reject_reason = (body.get("reason") or "").strip()
    if not reject_reason:
        return error(400, "请填写退回原因")

    eng_name = req.get("targetEngineerName", user.get("realName", user.get("username", "")))
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {
            "status": "待接单",
            "reservationRequest": {**req, "status": "rejected", "rejectReason": reject_reason, "resolvedAt": now_str()},
        }},
    )
    await _add_progress(db, repair_id, f"工程师 [{eng_name}] 已退回预约申请，原因：{reject_reason}", "done")

    await notify.push_notify(
        db,
        type_="repair_reserve_assign_rejected",
        title="预约申请已退回",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）工程师 {eng_name} 已退回预约申请，原因：{reject_reason}",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[str(req.get("requestedBy", ""))] if req.get("requestedBy") else None,
    )
    await notify.push_notify(
        db,
        type_="repair_reserve_assign_rejected",
        title="预约申请已退回",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）预约申请被 {eng_name} 退回，原因：{reject_reason}",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin"],
    )
    return success(None, "预约申请已退回")


@router.post("/repairs/{repair_id}/reserve-assign/cancel")
async def cancel_reserve_assign(
    repair_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _create_or_all,
):
    """取消预约 — 发起人取消待处理的预约申请"""
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")
    req = repair.get("reservationRequest") or {}
    if req.get("status") != "pending":
        return error(400, "没有待处理的预约申请")

    operator = user.get("realName", user.get("username", ""))
    target_id = str(req.get("targetEngineerId", ""))
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {
            "status": "待接单",
            "reservationRequest": {**req, "status": "cancelled", "resolvedAt": now_str()},
        }},
    )
    await _add_progress(db, repair_id, f"{operator} 已取消预约申请", "done")

    await notify.push_notify(
        db,
        type_="repair_reserve_assign_cancelled",
        title="预约申请已取消",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）的预约申请已被 {operator} 取消",
        link=f"/after_sales/repair-detail/{repair_id}",
        user_ids=[target_id] if target_id else None,
    )
    await notify.push_notify(
        db,
        type_="repair_reserve_assign_cancelled",
        title="预约申请已取消",
        content=f"工单 {repair.get('orderNo', '')}（{repair.get('company', '')}）预约申请已被 {operator} 取消",
        link=f"/after_sales/repair-detail/{repair_id}",
        role_codes=["admin", "super_admin"],
    )
    return success(None, "预约申请已取消")


# ─── 工程师（备用入口 /engineers）─────

@router.get("/engineers")
async def get_engineer_list(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _audit,
):
    """获取工程师列表 — /engineers（财务只读可访问）"""
    return await _get_engineers(db)


# ─── 辅助函数 ───────────────────────────────────────

async def _get_engineers(db: AsyncIOMotorDatabase):
    """获取工程师列表 — 工程师 = roleCode=engineer 的用户"""
    cursor = db.users.find({"roleCode": "engineer"})
    records = []
    async for e in cursor:
        records.append({
            "id": str(e["_id"]),
            "name": e.get("realName", e.get("username", "")),
            "username": e.get("username", ""),
            "phone": e.get("phone", ""),
            "avatar": e.get("avatar", ""),
            "skills": e.get("skills", []),
            "showOnMobile": e.get("showOnMobile", True),
            "desc": e.get("desc", ""),
            "team": e.get("team", ""),
        })
    return success(records)


async def _list_repairs(db: AsyncIOMotorDatabase, filter_q: dict, page: int, size: int) -> dict:
    total = await db.repairs.count_documents(filter_q)
    cursor = db.repairs.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for r in cursor:
        records.append(_format_repair(r))
    return success(paginate(records, total, page, size))


def _build_filter(status: str = "", company: str = "", work_order_type: str = "", is_rework: bool | None = None, engineer_id: str = "", start_date: str = "", end_date: str = "", pending_for: str = "") -> dict:
    """构造工单列表/导出过滤条件"""
    filter_q = {}
    if pending_for:
        # 工程师「待接单」视图：全局抢单池 + 指派给我的预约单
        filter_q["$or"] = [
            {"status": "待接单"},
            {"status": "已预约", "engineerId": pending_for},
        ]
    else:
        if status:
            filter_q["status"] = status
        if engineer_id:
            filter_q["engineerId"] = engineer_id
    if company:
        filter_q["company"] = {"$regex": re.escape(company), "$options": "i"}
    if work_order_type:
        filter_q["workOrderType"] = work_order_type
    if is_rework is not None:
        filter_q["isRework"] = is_rework
    # 日期范围按 createTime 字符串过滤（格式 YYYY-MM-DD HH:MM:SS，前缀比较即可）
    if start_date or end_date:
        time_filter: dict = {}
        if start_date:
            time_filter["$gte"] = start_date
        if end_date:
            time_filter["$lte"] = end_date + " 23:59:59"
        filter_q["createTime"] = time_filter
    return filter_q


def _is_archived(status: str) -> bool:
    """历史「已完成」与新增「已归档」均视为已归档"""
    return status in ("已完成", "已归档")


def _is_owner(repair: dict, user: dict) -> bool:
    """判断当前用户是否为该工单的归属（客户）"""
    return (
        repair.get("contact") == user.get("realName")
        or repair.get("createdBy") == user.get("username")
        or repair.get("phone") == user.get("phone")
    )


def _to_float(v):
    """安全转 float，空值/非法返回 None"""
    try:
        return float(v) if v is not None and v != "" else None
    except (TypeError, ValueError):
        return None


def _build_fee(fee, user) -> dict | None:
    """把前端 fee 结构规范化为存储格式；无金额则返回 None"""
    if not isinstance(fee, dict) or fee.get("amount") is None:
        return None
    amount = _to_float(fee.get("amount"))
    if amount is None:
        return None
    return {
        "mode": fee.get("mode", "agreed") if fee.get("mode") in ("agreed", "self") else "agreed",
        "amount": amount,
        "note": fee.get("note", ""),
        "paidBy": fee.get("paidBy", ""),
        "setBy": user.get("realName", user.get("username", "")),
        "settledAt": now_str(),
    }


def _format_repair(r: dict) -> dict:
    fee = r.get("fee")
    return {
        "id": str(r["_id"]),
        "orderNo": r.get("orderNo", ""),
        "company": r.get("company", ""),
        "contact": r.get("contact", ""),
        "phone": r.get("phone", ""),
        "address": r.get("address", ""),
        "deviceType": r.get("deviceType", ""),
        "workOrderType": r.get("workOrderType", "售后上门"),
        "priority": r.get("priority", "普通"),
        "repairDate": r.get("repairDate", ""),
        "preferredTimeSlot": r.get("preferredTimeSlot", "全天"),
        "preferredDate": r.get("preferredDate", ""),
        "description": r.get("description", ""),
        "images": r.get("images", []),
        "engineer": r.get("engineer", ""),
        "engineerId": r.get("engineerId", ""),
        "status": r.get("status", "待接单"),
        "progress": r.get("progress", []),
        "latitude": r.get("latitude"),
        "longitude": r.get("longitude"),
        "fee": fee if isinstance(fee, dict) else None,
        "isRework": r.get("isRework", False),
        "reworkOf": r.get("reworkOf", ""),
        "reworkReason": r.get("reworkReason", ""),
        "reworkNote": r.get("reworkNote", ""),
        "reworkCount": r.get("reworkCount", 0),
        "reworkChildNo": r.get("reworkChildNo", ""),
        "completedBy": r.get("completedBy", ""),
        "completedAt": r.get("completedAt", ""),
        "confirmedBy": r.get("confirmedBy", ""),
        "confirmedAt": r.get("confirmedAt", ""),
        "confirmRole": r.get("confirmRole", ""),
        "archived": r.get("archived", False),
        "reservedBy": r.get("reservedBy", ""),
        "reservedAt": r.get("reservedAt", ""),
        "scheduledDate": r.get("scheduledDate", ""),
        "scheduledTimeSlot": r.get("scheduledTimeSlot", ""),
        "slotSpan": r.get("slotSpan", 1) or 1,
        "acceptedAt": r.get("acceptedAt", ""),
        "escalated": r.get("escalated", False),
        "escalateReason": r.get("escalateReason", ""),
        "escalatedBy": r.get("escalatedBy", ""),
        "escalatedAt": r.get("escalatedAt", ""),
        "transferRequest": r.get("transferRequest") or None,
        "reservationRequest": r.get("reservationRequest") or None,
        "cancelledBy": r.get("cancelledBy", ""),
        "cancelledAt": r.get("cancelledAt", ""),
        "cancelReason": r.get("cancelReason", ""),
        "cancelNote": r.get("cancelNote", ""),
        "confirmUserId": r.get("confirmUserId", ""),
        "confirmUserName": r.get("confirmUserName", ""),
        "createTime": r.get("createTime", ""),
        "createdBy": r.get("createdBy", ""),
    }


async def _add_progress(db: AsyncIOMotorDatabase, repair_id: str, node: str, status: str):
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$push": {"progress": {
            "node": node,
            "time": now_min(),
            "status": status,
        }}},
    )


async def _slot_occupied(
    db: AsyncIOMotorDatabase,
    engineer_id: str,
    date: str,
    time_slot: str,
    exclude_repair_id: str | None = None,
    slot_span: int = 1,
) -> bool:
    """判断某工程师某日 [time_slot, time_slot+slot_span) 是否已被有效工单/排期/锁定占用（全天/空时段不参与冲突检测）"""
    if not time_slot or time_slot == "全天":
        return False
    start_idx = _SLOT_IDX.get(time_slot)
    if start_idx is None:
        return False
    span = max(1, int(slot_span or 1))
    end_idx = start_idx + span
    if end_idx > len(_SLOTS):
        return True  # 越界不可选
    # 当日已过期时段不可预约
    if time_slot in _expired_slots_for_date(date):
        return True
    cursor = db.repair_schedule.find({"engineerId": engineer_id, "date": date})
    async for s in cursor:
        if s.get("status") in ("已结束", "已完成", "已归档"):
            continue
        if exclude_repair_id and str(s.get("repairId", "")) == exclude_repair_id:
            continue
        s_slot = s.get("timeSlot", "")
        if not s_slot or s_slot == "全天":
            continue
        s_idx = _SLOT_IDX.get(s_slot)
        if s_idx is None:
            continue
        s_span = max(1, int(s.get("slotSpan", 1) or 1))
        s_end = s_idx + s_span
        if start_idx < s_end and s_idx < end_idx:  # 区间重叠即冲突
            return True
    return False


_SLOT_LABELS = {"AM1": "上午(早)", "AM2": "上午(晚)", "PM1": "下午(早)", "PM2": "下午(中)", "PM3": "下午(晚)"}


def _place_block(occupied: set, locked: set, span: int):
    """在 0..4 找一段连续 span 个槽（未被占且未锁定），返回起始索引或 None"""
    span = max(1, int(span))
    for i in range(len(_SLOTS) - span + 1):
        if all((i + k) not in occupied and (i + k) not in locked for k in range(span)):
            return i
    return None


async def _get_day_blocks(db: AsyncIOMotorDatabase, engineer_id: str, date: str) -> list[dict]:
    """返回某工程师某日的有效业务排期块（按 timeSlot 排序，排除锁定/已结束）"""
    blocks = []
    cursor = db.repair_schedule.find({"engineerId": engineer_id, "date": date})
    async for s in cursor:
        if s.get("status") in ("已结束", "已完成", "已归档", "已锁定"):
            continue
        rid = str(s.get("repairId", ""))
        if not rid:
            continue
        ts = s.get("timeSlot", "")
        blocks.append({
            "repairId": rid,
            "slotSpan": max(1, int(s.get("slotSpan", 1) or 1)),
            "acceptedAt": s.get("acceptedAt", ""),
            "timeSlot": ts,
            "idx": _SLOT_IDX.get(ts, 99),
        })
    blocks.sort(key=lambda b: b["idx"])
    return blocks


async def _repack_and_apply(
    db: AsyncIOMotorDatabase,
    engineer_id: str,
    date: str,
    ordered_blocks: list[dict],
) -> tuple[dict, list]:
    """按 ordered_blocks 顺序紧凑重排某日排期（避开锁定），溢出按 acceptedAt 顺延次日；次日也满则记入 needs_manual。

    同步更新 repair_schedule 与 repairs 的 scheduledDate/scheduledTimeSlot/slotSpan。
    返回 (assignments, needs_manual)：assignments = {repairId: {date, timeSlot, slotSpan}}。
    """
    locked = set()
    async for s in db.repair_schedule.find({"engineerId": engineer_id, "date": date, "status": "已锁定"}):
        idx = _SLOT_IDX.get(s.get("timeSlot", ""))
        if idx is not None:
            locked.add(idx)

    occupied = set()
    assignments: dict = {}
    overflow: list = []
    for b in ordered_blocks:
        span = max(1, int(b.get("slotSpan", 1) or 1))
        start = _place_block(occupied, locked, span)
        if start is None:
            overflow.append(b)
        else:
            for k in range(span):
                occupied.add(start + k)
            assignments[b["repairId"]] = {"date": date, "timeSlot": _SLOTS[start], "slotSpan": span}

    needs_manual: list = []
    if overflow:
        overflow.sort(key=lambda b: b.get("acceptedAt", "") or "")
        next_date = _next_date(date)
        nlocked = set()
        async for s in db.repair_schedule.find({"engineerId": engineer_id, "date": next_date, "status": "已锁定"}):
            idx = _SLOT_IDX.get(s.get("timeSlot", ""))
            if idx is not None:
                nlocked.add(idx)
        noccupied = set()
        async for s in db.repair_schedule.find({"engineerId": engineer_id, "date": next_date}):
            if s.get("status") in ("已结束", "已完成", "已归档"):
                continue
            idx = _SLOT_IDX.get(s.get("timeSlot", ""))
            if idx is None:
                continue
            noccupied.add(idx)
        for b in overflow:
            span = max(1, int(b.get("slotSpan", 1) or 1))
            start = _place_block(noccupied, nlocked, span)
            if start is None:
                needs_manual.append(b)
            else:
                for k in range(span):
                    noccupied.add(start + k)
                assignments[b["repairId"]] = {"date": next_date, "timeSlot": _SLOTS[start], "slotSpan": span}

    for rid, a in assignments.items():
        await db.repair_schedule.update_many(
            {"repairId": rid, "status": {"$nin": ["已结束", "已完成", "已归档"]}},
            {"$set": {"date": a["date"], "timeSlot": a["timeSlot"], "slotSpan": a["slotSpan"]}},
        )
        try:
            await db.repairs.update_one(
                {"_id": ObjectId(rid)},
                {"$set": {"scheduledDate": a["date"], "scheduledTimeSlot": a["timeSlot"], "slotSpan": a["slotSpan"]}},
            )
        except Exception:
            pass
    return assignments, needs_manual


async def _notify_postpone(db: AsyncIOMotorDatabase, assignments: dict, base_date: str):
    """给被顺延到次日的工单追加温和进度节点（客户可见，不说插队/顺延真实原因）"""
    for rid, a in assignments.items():
        if a["date"] != base_date:
            try:
                label = _SLOT_LABELS.get(a["timeSlot"], a["timeSlot"])
                await _add_progress(
                    db, rid,
                    f"因排期调整，您的工单预计将于 {a['date']} {label} 上门处理，给您带来不便敬请谅解。",
                    "doing",
                )
            except Exception:
                pass
