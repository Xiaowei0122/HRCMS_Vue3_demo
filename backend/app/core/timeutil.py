"""服务器时间工具 — 统一使用北京时间（UTC+8），保证报单时间与本地时间一致"""
from datetime import datetime, timezone, timedelta

CN_TZ = timezone(timedelta(hours=8))


def now_cn() -> datetime:
    """当前北京时间"""
    return datetime.now(CN_TZ)


def now_str() -> str:
    """YYYY-MM-DD HH:MM:SS"""
    return now_cn().strftime("%Y-%m-%d %H:%M:%S")


def now_min() -> str:
    """YYYY-MM-DD HH:MM"""
    return now_cn().strftime("%Y-%m-%d %H:%M")


def today_str() -> str:
    """YYYY-MM-DD"""
    return now_cn().strftime("%Y-%m-%d")
