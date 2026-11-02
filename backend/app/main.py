"""FastAPI 应用工厂"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import ConnectionFailure

from app.core.config import settings
from app.core.response import error
from app.database.connection import connect_db, close_db
from app.database.seed import run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时连接数据库 & 种子数据，关闭时断开连接"""
    # 启动
    db = await connect_db()
    app.state.db = db
    await run_seed(db)
    # 确保上传目录存在
    os.makedirs(settings.upload_dir, exist_ok=True)
    for sub in ["products", "news", "honors", "banners", "avatars", "logos", "vehicles", "knowledge", "finance", "cases"]:
        os.makedirs(os.path.join(settings.upload_dir, sub), exist_ok=True)
    yield
    # 关闭
    await close_db()


app = FastAPI(
    title="鸿瑞办公CMS API",
    version="0.5.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ConnectionFailure)
async def db_connection_exception_handler(request: Request, exc):
    """数据库连接失败：后端可达但数据库不可用，返回 503 与后端服务故障区分"""
    return JSONResponse(status_code=503, content=error(code=503, message="无法连接数据库"))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc):
    return JSONResponse(status_code=500, content=error(code=500, message=str(exc) or "服务器内部错误"))


# ── 注册路由 ─────────────────────────────────────────

from app.routers import auth, users, roles, logs, dashboard, notifications
from app.routers import products, news, honors, brands, cases, leads
from app.routers import config, repairs, complaints, contact, upload, knowledge
from app.routers import uploads_proxy
from app.routers import finance, public
from app.routers import todos, dict as dict_router
from app.routers import depts, reports, recycle
from app.routers import settings as settings_router
from app.routers import addresses, messages

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(roles.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(todos.router, prefix="/api")
app.include_router(dict_router.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(honors.router, prefix="/api")
app.include_router(brands.router, prefix="/api")
app.include_router(cases.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(repairs.router, prefix="/api")
app.include_router(complaints.router, prefix="/api")
app.include_router(contact.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(finance.router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(depts.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(recycle.router, prefix="/api")
app.include_router(addresses.router, prefix="/api")
app.include_router(messages.router, prefix="/api")

# 文件读取代理（SeaweedFS 为主，本地磁盘兜底）
app.include_router(uploads_proxy.router)
