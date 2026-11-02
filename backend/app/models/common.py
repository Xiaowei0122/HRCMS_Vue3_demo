"""通用模型"""
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10


class DictItemIn(BaseModel):
    type: str
    label: str
    value: str = ""
    sort: int = 0
    enabled: bool = True
