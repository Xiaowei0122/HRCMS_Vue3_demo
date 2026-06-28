"""通用模型"""
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10
