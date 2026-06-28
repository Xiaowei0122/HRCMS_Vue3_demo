"""用户 / 认证 相关模型"""
from pydantic import BaseModel


class LoginIn(BaseModel):
    username: str
    password: str


class PasswordChangeIn(BaseModel):
    oldPassword: str
    newPassword: str


class UserCreate(BaseModel):
    username: str
    realName: str = ""
    role: str = ""
    phone: str = ""
    password: str = "123456"


class UserUpdate(BaseModel):
    realName: str | None = None
    role: str | None = None
    phone: str | None = None


class UserQuery(BaseModel):
    name: str | None = None
    page: int = 1
    size: int = 10
