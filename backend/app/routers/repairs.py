"""报修管理路由 — 12 个端点"""
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_user_types, resolve_user_type
from app.core.response import success, error, paginate
from app.core.security import generate_order_no

router = APIRouter(tags=["报修管理"])

# RBAC 依赖（混合路由：不同端点不同角色）
_engineer = Depends(require_user_types("admin", "internal", "engineer"))
_manage = Depends(require_user_types("admin", "internal"))
_admin = Depends(require_user_types("admin"))
_assign = Depends(require_user_types("admin", "engineer"))


# ─── 报修 CRUD ──────────────────────────────────────

@router.post("/repairs")
async def create_repair(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """创建一个报修工单 — 兼容前端字段名"""
    # 优先级映射 (前端 urgency → 后端 priority)
    urgency_map = {"urgent": "紧急", "normal": "普通", "low": "不急"}
    raw_urgency = body.get("urgency", "normal")
    priority = body.get("priority") or urgency_map.get(raw_urgency, "普通")

    doc = {
        "orderNo": generate_order_no(),
        "company": body.get("company", ""),
        "contact": body.get("contactName") or body.get("contact", ""),
        "phone": body.get("contactPhone") or body.get("phone", ""),
        "address": body.get("address", ""),
        "deviceType": body.get("deviceType", ""),
        "priority": priority,
        "repairDate": body.get("repairDate", ""),
        "description": body.get("description", ""),
        "images": body.get("images", []),
        "engineer": body.get("engineer", ""),
        "engineerId": body.get("engineerId", ""),
        "status": "待接单",
        "progress": [
            {"node": "工单已创建，系统自动派发", "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"), "status": "done"},
        ],
        "createTime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "createdBy": user.get("username", ""),
    }
    result = await db.repairs.insert_one(doc)
    return success({"id": str(result.inserted_id), "orderNo": doc["orderNo"]}, "报修工单创建成功")


@router.get("/repairs/my")
async def get_my_repairs(
    page: int = 1,
    size: int = 10,
    status: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取当前用户的报修列表（联系人匹配 或 创建人匹配）"""
    user_name = user.get("username", "")
    user_real = user.get("realName", user_name)
    filter_q = {"$or": [{"contact": user_real}, {"createdBy": user_name}]}
    if status:
        filter_q["status"] = status
    return await _list_repairs(db, filter_q, page, size)


@router.get("/repairs")
async def get_repair_list(
    page: int = 1,
    size: int = 10,
    status: str = "",
    company: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """获取全部工单列表（管理员/工程师）"""
    filter_q = {}
    if status:
        filter_q["status"] = status
    if company:
        filter_q["company"] = {"$regex": company, "$options": "i"}
    return await _list_repairs(db, filter_q, page, size)


@router.get("/repairs/stats")
async def get_repair_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """报修统计数据"""
    return success({
        "total": await db.repairs.count_documents({}),
        "pending": await db.repairs.count_documents({"status": "待接单"}),
        "processing": await db.repairs.count_documents({"status": "处理中"}),
        "completed": await db.repairs.count_documents({"status": "已完成"}),
    })


# ─── 排期（静态路由，必须在参数化路由 /repairs/{repair_id} 之前）───

@router.get("/repairs/schedule")
async def get_engineer_schedule(
    engineerId: str = "",
    date: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """获取工程师排期"""
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
            "type": s.get("type", ""),
            "company": s.get("company", ""),
            "status": s.get("status", ""),
            "orderNo": "",
            "progress": [],
        }
        # 关联查询 repair 获取工单详情
        repair_id = s.get("repairId", "")
        if repair_id:
            try:
                repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
                if repair:
                    record["orderNo"] = repair.get("orderNo", "")
                    record["progress"] = repair.get("progress", [])
            except Exception:
                pass
        records.append(record)
    return success(records)


@router.post("/repairs/schedule")
async def create_schedule_entry(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _admin,
):
    """创建排期条目"""
    doc = {**body, "createdAt": datetime.now(timezone.utc)}
    result = await db.repair_schedule.insert_one(doc)
    return success({"id": str(result.inserted_id)}, "排期已创建")


@router.delete("/repairs/schedule/{schedule_id}")
async def delete_schedule_entry(
    schedule_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _admin,
):
    """删除排期条目"""
    await db.repair_schedule.delete_one({"_id": ObjectId(schedule_id)})
    return success(None, "排期已删除")


# ─── 工程师列表（静态路由，必须在 /repairs/{repair_id} 之前）─────

@router.get("/repairs/engineers")
async def get_repairs_engineers(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取工程师列表 — /repairs/engineers（前端 store 调用）"""
    return await _get_engineers(db)


# ─── 参数化路由（必须在所有静态路由之后）─────────────

@router.get("/repairs/{repair_id}")
async def get_repair_detail(
    repair_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取工单详情"""
    r = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not r:
        return error(404, "工单不存在")
    return success(_format_repair(r))


@router.patch("/repairs/{repair_id}/assign")
async def assign_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _assign,
):
    """指派工程师 — 管理员可指派任意工程师，工程师仅可自助接单；同步到排期表"""
    if resolve_user_type(user) == "admin":
        # 管理员：指派给指定工程师
        eng_name = body.get("engineerName", "")
        eng_id = body.get("engineerId", "")
    else:
        # 工程师：自助接单，按 username 关联工程师档案，强制指派给自己
        eng_doc = await db.engineers.find_one({"username": user.get("username", "")})
        if eng_doc:
            eng_name = eng_doc.get("name", "")
            eng_id = str(eng_doc["_id"])
        else:
            # 兜底：无关联档案时退化为登录账号身份
            eng_name = user.get("realName", user.get("username", ""))
            eng_id = str(user.get("_id", ""))

    if not eng_name or not eng_id:
        return error(400, "请选择工程师")

    # 获取报修信息用于排期
    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    if not repair:
        return error(404, "工单不存在")

    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {"engineer": eng_name, "engineerId": eng_id, "status": "处理中"}},
    )
    await _add_progress(db, repair_id, f"已指派工程师：{eng_name}", "done")

    # 自动同步到排期表（支持指定日期/时段）
    schedule_date = body.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    existing = await db.repair_schedule.find_one({
        "engineerId": eng_id, "date": schedule_date, "repairId": repair_id
    })
    if not existing:
        await db.repair_schedule.insert_one({
            "engineerId": eng_id,
            "engineer": eng_name,
            "date": schedule_date,
            "timeSlot": body.get("timeSlot", "全天"),
            "type": "business",
            "company": repair.get("company", ""),
            "repairId": repair_id,
            "status": "处理中",
            "createdAt": datetime.now(timezone.utc),
        })

    return success(None, "指派成功")


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
    """完结工单"""
    await _add_progress(db, repair_id, "工单已处理完成，系统自动归档", "done")
    await db.repairs.update_one({"_id": ObjectId(repair_id)}, {"$set": {"status": "已完成"}})
    return success(None, "工单已完结")


@router.patch("/repairs/{repair_id}/transfer")
async def transfer_repair(
    repair_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _engineer,
):
    """转单 — 将工单转给另一位工程师"""
    target_name = body.get("targetEngineerName", body.get("engineerName", ""))
    target_id = body.get("targetEngineerId", body.get("engineerId", ""))

    if not target_name:
        return error(400, "请选择目标工程师")

    repair = await db.repairs.find_one({"_id": ObjectId(repair_id)})
    old_eng = repair.get("engineer", "未知") if repair else "未知"

    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$set": {"engineer": target_name, "engineerId": target_id}},
    )
    await _add_progress(db, repair_id, f"工单已从 [{old_eng}] 转派至 [{target_name}]", "done")
    return success(None, "转单成功")


# ─── 工程师（备用入口 /engineers）─────

@router.get("/engineers")
async def get_engineer_list(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """获取工程师列表 — /engineers"""
    return await _get_engineers(db)


# ─── 辅助函数 ───────────────────────────────────────

async def _get_engineers(db: AsyncIOMotorDatabase):
    """获取工程师列表"""
    cursor = db.engineers.find({})
    records = []
    async for e in cursor:
        records.append({
            "id": str(e["_id"]),
            "name": e.get("name", ""),
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


def _format_repair(r: dict) -> dict:
    return {
        "id": str(r["_id"]),
        "orderNo": r.get("orderNo", ""),
        "company": r.get("company", ""),
        "contact": r.get("contact", ""),
        "phone": r.get("phone", ""),
        "address": r.get("address", ""),
        "deviceType": r.get("deviceType", ""),
        "priority": r.get("priority", "普通"),
        "repairDate": r.get("repairDate", ""),
        "description": r.get("description", ""),
        "images": r.get("images", []),
        "engineer": r.get("engineer", ""),
        "engineerId": r.get("engineerId", ""),
        "status": r.get("status", "待接单"),
        "progress": r.get("progress", []),
        "createTime": r.get("createTime", ""),
        "createdBy": r.get("createdBy", ""),
    }


async def _add_progress(db: AsyncIOMotorDatabase, repair_id: str, node: str, status: str):
    await db.repairs.update_one(
        {"_id": ObjectId(repair_id)},
        {"$push": {"progress": {
            "node": node,
            "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "status": status,
        }}},
    )
