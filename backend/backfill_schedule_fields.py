"""历史数据回填 — 为已有工单补齐排期字段
scheduledDate / scheduledTimeSlot / slotSpan / acceptedAt

- 数据来源：repair_schedule 表（按 repairId 关联，取有效业务排期）
- 规则：从排期表反推日期/时段/占格；缺省 slotSpan=1；「全天」归一化为 AM1 + 5 格
- 幂等：仅补齐空字段，已存在的字段不覆盖

用法：
    cd backend
    python backfill_schedule_fields.py
"""
import os
from pymongo import MongoClient

URI = os.getenv("MONGODB_URI", "mongodb://admin:123456@127.0.0.1:27017")
DB_NAME = os.getenv("DATABASE_NAME", "hrcms_test")

# 每天 5 格，一单可占连续多格
SLOTS = ["AM1", "AM2", "PM1", "PM2", "PM3"]
SLOT_IDX = {s: i for i, s in enumerate(SLOTS)}


def normalize_slot(slot: str, span):
    """「全天」/空时段归一化：全天 → AM1 + 5 格；空 → AM1 + 1 格"""
    span = max(1, int(span or 1))
    if not slot or slot == "全天":
        return SLOTS[0], (5 if slot == "全天" else span)
    return slot, span


def main():
    print(f"Connecting to {URI} ...")
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        print("[OK] MongoDB connected")
    except Exception as e:
        print(f"[ERROR] Cannot connect: {e}")
        exit(1)

    db = client[DB_NAME]

    # 有效业务排期（排除锁定/已结束的排期条目）
    schedules = {}
    for s in db.repair_schedule.find({"type": "business"}):
        rid = s.get("repairId", "")
        if not rid:
            continue
        # 优先保留「处理中」等有效条目，避免被已归档覆盖
        existing = schedules.get(rid)
        if existing and existing.get("status") == "处理中":
            continue
        schedules[rid] = s

    updated = 0
    skipped = 0
    total = 0

    for repair in db.repairs.find({}):
        total += 1
        rid = str(repair.get("_id"))
        s = schedules.get(rid)
        if not s:
            skipped += 1
            continue

        # 只补空字段，保留已有值（幂等）
        patch = {}
        if not repair.get("scheduledDate"):
            patch["scheduledDate"] = s.get("date", "") or ""
        if not repair.get("scheduledTimeSlot"):
            patch["scheduledTimeSlot"] = s.get("timeSlot", "") or ""
        if not repair.get("slotSpan"):
            patch["slotSpan"] = max(1, int(s.get("slotSpan", 1) or 1))
        if not repair.get("acceptedAt"):
            patch["acceptedAt"] = s.get("acceptedAt", "") or ""

        # 归一化「全天」时段
        slot = patch.get("scheduledTimeSlot", repair.get("scheduledTimeSlot", "") or "")
        span = patch.get("slotSpan", repair.get("slotSpan", 1) or 1)
        norm_slot, norm_span = normalize_slot(slot, span)
        if norm_slot != slot:
            patch["scheduledTimeSlot"] = norm_slot
        if norm_span != span:
            patch["slotSpan"] = norm_span

        if not patch:
            skipped += 1
            continue

        db.repairs.update_one({"_id": repair["_id"]}, {"$set": patch})
        updated += 1

    # 同步：让排期表本身也补齐 slotSpan（老数据可能缺该字段）
    schedule_updated = 0
    for s in db.repair_schedule.find({"type": "business"}):
        if not s.get("slotSpan"):
            slot = s.get("timeSlot", "")
            span = 5 if slot == "全天" else 1
            db.repair_schedule.update_one(
                {"_id": s["_id"]},
                {"$set": {"slotSpan": span, "timeSlot": SLOTS[0] if slot == "全天" else slot}},
            )
            schedule_updated += 1

    client.close()
    print()
    print(f"[OK] 工单总数：{total}")
    print(f"[OK] 已回填工单字段：{updated}")
    print(f"[OK] 已回填排期表 slotSpan：{schedule_updated}")
    print(f"[--] 无需处理：{skipped}")
    print()
    print("回填完成。字段：scheduledDate / scheduledTimeSlot / slotSpan / acceptedAt")


if __name__ == "__main__":
    main()
