"""操作日志路由"""
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.deps import get_db, get_current_user
from app.core.response import success, paginate

router = APIRouter(prefix="/logs", tags=["操作日志"])


@router.get("")
async def get_log_list(
    page: int = 1,
    size: int = 20,
    user: str = "",
    startDate: str = "",
    endDate: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    filter_q = {}
    if user:
        filter_q["user"] = {"$regex": user, "$options": "i"}
    if startDate and endDate:
        filter_q["time"] = {"$gte": startDate, "$lte": endDate + " 23:59:59"}

    total = await db.logs.count_documents(filter_q)
    cursor = db.logs.find(filter_q).skip((page - 1) * size).limit(size).sort("_id", -1)
    records = []
    async for log in cursor:
        records.append({
            "id": str(log["_id"]),
            "time": log.get("time", ""),
            "user": log.get("user", ""),
            "module": log.get("module", ""),
            "content": log.get("content", ""),
            "ip": log.get("ip", ""),
            "result": log.get("result", ""),
        })
    return success(paginate(records, total, page, size))
