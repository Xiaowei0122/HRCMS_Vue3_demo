"""联系我们 — 展示工程师管理（工程师 = roleCode=engineer 的用户）"""
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user, require_permission
from app.core.response import success, error, paginate

router = APIRouter(prefix="/contact", tags=["联系我们"])

_manage = Depends(require_permission("contact"))


@router.get("/engineers")
async def get_contact_engineers(
    page: int = 1,
    size: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """展示工程师列表（showOnMobile=true 的工程师用户）"""
    filter_q = {"roleCode": "engineer", "showOnMobile": True}
    total = await db.users.count_documents(filter_q)
    cursor = db.users.find(filter_q).skip((page - 1) * size).limit(size)
    records = []
    async for u in cursor:
        records.append({
            "id": str(u["_id"]),
            "name": u.get("realName", u.get("username", "")),
            "phone": u.get("phone", ""),
            "avatar": u.get("avatar", ""),
            "skills": u.get("skills", []),
            "desc": u.get("desc", ""),
            "team": u.get("team", ""),
            "showOnMobile": True,
        })
    return success(paginate(records, total, page, size))


@router.get("/candidates")
async def get_contact_engineer_candidates(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    """所有工程师用户（roleCode=engineer），用于「添加展示工程师」联动筛选"""
    cursor = db.users.find({"roleCode": "engineer"})
    records = []
    async for u in cursor:
        records.append({
            "id": str(u["_id"]),
            "name": u.get("realName", u.get("username", "")),
            "phone": u.get("phone", ""),
            "showOnMobile": u.get("showOnMobile", False),
        })
    return success(records)


@router.post("/engineers")
async def create_contact_engineer(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    """将某位工程师用户设为「展示」（showOnMobile=true）并写入展示字段"""
    uid = body.get("id") or body.get("userId")
    if not uid:
        return error(400, "请选择工程师")
    target = await db.users.find_one({"_id": ObjectId(uid), "roleCode": "engineer"})
    if not target:
        return error(404, "该工程师不存在")
    upd = {"showOnMobile": True}
    for f in ("avatar", "skills", "desc", "team"):
        if f in body:
            upd[f] = body[f]
    await db.users.update_one({"_id": ObjectId(uid)}, {"$set": upd})
    return success({"id": uid}, "工程师已加入展示")


@router.put("/engineers/{eng_id}")
async def update_contact_engineer(
    eng_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    """编辑展示字段（avatar/skills/desc/team/showOnMobile）"""
    allowed = {k: v for k, v in body.items() if k in ("avatar", "skills", "desc", "team", "showOnMobile")}
    if not allowed:
        return error(400, "没有可更新的字段")
    await db.users.update_one({"_id": ObjectId(eng_id)}, {"$set": allowed})
    return success(None, "工程师信息已更新")


@router.delete("/engineers/{eng_id}")
async def delete_contact_engineer(
    eng_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = _manage,
):
    """从展示列表移除（showOnMobile=false，不删除用户）"""
    await db.users.update_one({"_id": ObjectId(eng_id)}, {"$set": {"showOnMobile": False}})
    return success(None, "工程师已从展示移除")
