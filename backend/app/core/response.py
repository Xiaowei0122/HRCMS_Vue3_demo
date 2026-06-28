"""统一响应格式"""
from typing import Any


def success(data: Any = None, message: str = "ok") -> dict:
    return {"code": 200, "data": data, "message": message}


def error(code: int = 500, message: str = "服务器内部错误") -> dict:
    return {"code": code, "data": None, "message": message}


def paginate(records: list, total: int, page: int, size: int) -> dict:
    return {
        "records": records,
        "total": total,
        "page": page,
        "size": size,
    }
