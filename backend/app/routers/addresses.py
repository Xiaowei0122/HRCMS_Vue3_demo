"""地址管理路由：用户服务地址簿 CRUD（所有登录用户可用，操作仅限本人）"""
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error
from app.core.timeutil import now_str

router = APIRouter(prefix="/addresses", tags=["地址管理"])


def _own_match(user: dict) -> dict:
    return {"userId": str(user.get("_id", ""))}


def _format(a: dict) -> dict:
    return {
        "id": str(a["_id"]),
        "contactName": a.get("contactName", ""),
        "contactPhone": a.get("contactPhone", ""),
        "address": a.get("address", ""),
        "isDefault": a.get("isDefault", False),
        "createdAt": a.get("createdAt", ""),
    }


@router.get("")
async def list_addresses(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """我的地址簿（默认地址优先）"""
    cursor = db.addresses.find(_own_match(user)).sort([("isDefault", -1), ("_id", -1)])
    records = []
    async for a in cursor:
        records.append(_format(a))
    return success(records)


@router.post("")
async def create_address(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    contact_name = (body.get("contactName") or "").strip()
    phone = (body.get("contactPhone") or "").strip()
    address = (body.get("address") or "").strip()
    if not contact_name or not phone or not address:
        return error(400, "联系人、电话、地址均为必填")
    if not (len(phone) >= 7 and phone.isdigit()):
        return error(400, "请填写正确的联系电话")

    count = await db.addresses.count_documents(_own_match(user))
    is_default = bool(body.get("isDefault")) or count == 0  # 首条地址自动设为默认
    if is_default:
        await db.addresses.update_many(_own_match(user), {"$set": {"isDefault": False}})

    doc = {
        "userId": str(user.get("_id", "")),
        "contactName": contact_name,
        "contactPhone": phone,
        "address": address,
        "isDefault": is_default,
        "createdAt": now_str(),
    }
    result = await db.addresses.insert_one(doc)
    doc["_id"] = result.inserted_id
    return success(_format(doc), "已保存")


@router.put("/{address_id}")
async def update_address(
    address_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    a = await db.addresses.find_one({"_id": ObjectId(address_id), **_own_match(user)})
    if not a:
        return error(404, "地址不存在")

    upd = {}
    if "contactName" in body:
        upd["contactName"] = (body.get("contactName") or "").strip()
    if "contactPhone" in body:
        upd["contactPhone"] = (body.get("contactPhone") or "").strip()
    if "address" in body:
        upd["address"] = (body.get("address") or "").strip()
    if not upd:
        return error(400, "无更新内容")
    if any(not v for v in upd.values()):
        return error(400, "联系人、电话、地址不能为空")

    if body.get("isDefault"):
        await db.addresses.update_many(_own_match(user), {"$set": {"isDefault": False}})
        upd["isDefault"] = True

    await db.addresses.update_one({"_id": ObjectId(address_id)}, {"$set": upd})
    fresh = await db.addresses.find_one({"_id": ObjectId(address_id)})
    return success(_format(fresh), "已更新")


@router.delete("/{address_id}")
async def delete_address(
    address_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    a = await db.addresses.find_one({"_id": ObjectId(address_id), **_own_match(user)})
    if not a:
        return error(404, "地址不存在")
    await db.addresses.delete_one({"_id": ObjectId(address_id)})

    # 若删除的是默认地址，把最新一条补为默认
    if a.get("isDefault"):
        latest = await db.addresses.find(_own_match(user)).sort("_id", -1).limit(1).to_list(1)
        if latest:
            await db.addresses.update_one({"_id": latest[0]["_id"]}, {"$set": {"isDefault": True}})
    return success(None, "已删除")


@router.post("/{address_id}/default")
async def set_default(
    address_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    a = await db.addresses.find_one({"_id": ObjectId(address_id), **_own_match(user)})
    if not a:
        return error(404, "地址不存在")
    await db.addresses.update_many(_own_match(user), {"$set": {"isDefault": False}})
    await db.addresses.update_one({"_id": ObjectId(address_id)}, {"$set": {"isDefault": True}})
    return success(None, "已设为默认")
