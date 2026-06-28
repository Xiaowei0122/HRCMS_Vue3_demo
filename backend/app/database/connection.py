"""数据库连接管理"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> AsyncIOMotorDatabase:
    """连接 MongoDB 并返回数据库实例"""
    global _client, _db
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.database_name]
    await _create_indexes(_db)
    return _db


async def close_db():
    global _client
    if _client:
        _client.close()
        _client = None


async def _create_indexes(db: AsyncIOMotorDatabase):
    await db.users.create_index("username", unique=True, sparse=True)
    await db.roles.create_index("code", unique=True, sparse=True)
    await db.repairs.create_index("orderNo", unique=True, sparse=True)
    await db.logs.create_index("time")
    await db.leads.create_index("createTime")
