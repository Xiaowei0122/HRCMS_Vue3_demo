"""角色相关模型"""
from pydantic import BaseModel


class RoleCreate(BaseModel):
    roleName: str
    code: str


class RoleUpdate(BaseModel):
    roleName: str | None = None
    code: str | None = None


class PermSaveIn(BaseModel):
    permissionIds: list[int]
