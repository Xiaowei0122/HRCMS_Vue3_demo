"""私信（即时消息）路由：会话列表 + 消息收发 + 未读统计"""
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_db, get_current_user
from app.core.response import success, error
from app.core.timeutil import now_str

router = APIRouter(prefix="/messages", tags=["私信"])


def _uid(user: dict) -> str:
    return str(user.get("_id", ""))


async def _get_owned_conversation(db: AsyncIOMotorDatabase, conversation_id: str, me: str):
    try:
        oid = ObjectId(conversation_id)
    except Exception:
        return None
    return await db.conversations.find_one({"_id": oid, "participants": me})


async def _peer_info(db: AsyncIOMotorDatabase, participants: list, me: str) -> dict:
    peer_id = next((p for p in participants if p != me), "")
    if not peer_id:
        return {"id": "", "name": "系统", "avatar": ""}
    u = await db.users.find_one({"_id": ObjectId(peer_id)}) if peer_id else None
    if not u:
        return {"id": peer_id, "name": "未知用户", "avatar": ""}
    return {
        "id": peer_id,
        "name": u.get("realName") or u.get("username", ""),
        "avatar": u.get("avatar", ""),
        "roleCode": u.get("roleCode", ""),
    }


async def _count_unread(db: AsyncIOMotorDatabase, conversation_id, me: str, last_read) -> int:
    q = {"conversationId": conversation_id, "senderId": {"$ne": me}}
    if last_read:
        q["createdAt"] = {"$gt": last_read}
    return await db.messages.count_documents(q)


@router.get("/conversations")
async def list_conversations(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """我的会话列表（含对方信息、最后一条消息、未读数）"""
    me = _uid(user)
    cursor = db.conversations.find({"participants": me}).sort("lastAt", -1)
    records = []
    async for c in cursor:
        participants = c.get("participants", [])
        peer = await _peer_info(db, participants, me)
        last_read = (c.get("lastReadAt") or {}).get(me)
        records.append({
            "id": str(c["_id"]),
            "peer": peer,
            "lastMessage": c.get("lastMessage", ""),
            "lastAt": c.get("lastAt", ""),
            "unread": await _count_unread(db, c["_id"], me, last_read),
        })
    return success(records)


@router.get("/unread-count")
async def unread_count(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """所有会话未读消息总数（角标用）"""
    me = _uid(user)
    total = 0
    cursor = db.conversations.find({"participants": me})
    async for c in cursor:
        last_read = (c.get("lastReadAt") or {}).get(me)
        total += await _count_unread(db, c["_id"], me, last_read)
    return success({"count": total})


@router.post("/conversations")
async def open_conversation(
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """打开/创建与某用户的会话，返回会话 id 与对方信息"""
    peer_id = (body.get("peerId") or "").strip()
    if not peer_id:
        return error(400, "缺少对方用户")
    me = _uid(user)
    if peer_id == me:
        return error(400, "不能与自己私信")
    try:
        ObjectId(peer_id)
    except Exception:
        return error(400, "对方用户无效")
    peer = await db.users.find_one({"_id": ObjectId(peer_id)})
    if not peer:
        return error(404, "对方用户不存在")

    participants = sorted([me, peer_id])
    conv = await db.conversations.find_one({"participants": participants})
    if conv:
        conv_id = str(conv["_id"])
    else:
        doc = {
            "participants": participants,
            "lastMessage": "",
            "lastAt": now_str(),
            "lastReadAt": {},
            "createdAt": now_str(),
        }
        result = await db.conversations.insert_one(doc)
        conv_id = str(result.inserted_id)
    return success({"id": conv_id, "peer": await _peer_info(db, participants, me)})


@router.get("/conversations/{conversation_id}/messages")
async def list_messages(
    conversation_id: str,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """会话消息（最近 limit 条，正序返回；拉取即视为已读）"""
    me = _uid(user)
    conv = await _get_owned_conversation(db, conversation_id, me)
    if not conv:
        return error(404, "会话不存在")

    cursor = db.messages.find({"conversationId": ObjectId(conversation_id)}) \
        .sort("_id", -1).limit(max(1, min(limit, 200)))
    docs = await cursor.to_list(None)
    docs.reverse()
    records = [{
        "id": str(m["_id"]),
        "conversationId": conversation_id,
        "senderId": m.get("senderId", ""),
        "mine": m.get("senderId", "") == me,
        "content": m.get("content", ""),
        "createdAt": m.get("createdAt", ""),
    } for m in docs]

    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {f"lastReadAt.{me}": now_str()}},
    )
    return success(records)


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    body: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    me = _uid(user)
    conv = await _get_owned_conversation(db, conversation_id, me)
    if not conv:
        return error(404, "会话不存在")

    content = (body.get("content") or "").strip()
    if not content:
        return error(400, "消息内容不能为空")
    if len(content) > 2000:
        return error(400, "消息过长")

    now = now_str()
    doc = {
        "conversationId": ObjectId(conversation_id),
        "senderId": me,
        "content": content,
        "createdAt": now,
    }
    result = await db.messages.insert_one(doc)
    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"lastMessage": content, "lastAt": now}},
    )
    return success({
        "id": str(result.inserted_id),
        "conversationId": conversation_id,
        "senderId": me,
        "mine": True,
        "content": content,
        "createdAt": now,
    })


@router.post("/conversations/{conversation_id}/read")
async def mark_read(
    conversation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    me = _uid(user)
    conv = await _get_owned_conversation(db, conversation_id, me)
    if not conv:
        return error(404, "会话不存在")
    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {f"lastReadAt.{me}": now_str()}},
    )
    return success(None, "已读")
