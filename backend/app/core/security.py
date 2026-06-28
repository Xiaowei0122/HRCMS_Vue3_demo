"""安全相关：密码哈希、JWT 令牌、工单号生成"""
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from .config import settings


# ─── 密码 ────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ─── JWT ─────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


# ─── 工单号 ──────────────────────────────────────────

def generate_order_no() -> str:
    """生成工单号: HR + 年月日 + 4位随机数"""
    now = datetime.now()
    import random
    suffix = str(random.randint(0, 9999)).zfill(4)
    return f"HR{now.strftime('%Y%m%d')}{suffix}"
