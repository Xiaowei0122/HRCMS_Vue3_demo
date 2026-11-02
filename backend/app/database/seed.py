"""种子数据：管理员账号 + 角色 + 权限树 + 示例数据"""
from datetime import datetime, timezone
from app.core.security import hash_password


# homepage 静态内容（与 HRhomepage_vue3 保持一致，CMS 配置缺失时回填）
_HOMEPAGE_SERVICES = [
    {"id": "sales", "icon": "🖨️", "title": "办公设备/耗材/文具销售", "desc": "提供打印机、复印机、投影等主流办公设备采购与配置。"},
    {"id": "repair", "icon": "🛠️", "title": "打印机/复印机设备维修", "desc": "全国服务网络，快速到场、原厂配件与专业工程师保障。"},
    {"id": "supplies", "icon": "📦", "title": "鸿瑞供应链配送服务", "desc": "稳定供货与库存管理，支持协议客户优先配送。"},
    {"id": "solutions", "icon": "💡", "title": "智能化办公方案", "desc": "OA集成、打印管控与设备运维一体化，提升管理效率。"},
]

_HOMEPAGE_ABOUT = {
    "intro": "鸿瑞办公深耕办公设备与运维服务领域，覆盖企业、政府、教育等行业。我们不仅提供优选设备与耗材，更通过标准化运维体系与数字化平台，保障设备稳定运行，帮助客户持续降低成本与提升效率。",
    "stats": [
        {"num": "全平台", "label": "省市区级、央采、军采入驻"},
        {"num": "30+", "label": "专业业务团队"},
        {"num": "500+", "label": "企、事业、单位客户"},
        {"num": "24/7", "label": "售后响应"},
    ],
    "culture": [
        {"title": "企业愿景", "desc": "构建员工实现自我价值的平台，全体员工的收入处于行业领先水平", "icon": "bi bi-eye-fill"},
        {"title": "企业使命", "desc": "以客户为中心、以奋斗者为本、长期艰苦奋斗", "icon": "bi bi-lightning-charge-fill"},
        {"title": "核心价值观", "desc": "诚信、前瞻、凝聚、务实、温暖、共赢", "icon": "bi bi-heart-fill"},
    ],
    "depts": [
        {"name": "直销大客户部", "duty": "负责省市区级机关事业单位招标与项目交付。"},
        {"name": "技术运维部", "duty": "专业工程师，负责驻场运维与售后保障。"},
        {"name": "分销与渠道拓展部", "duty": "负责公司产品的渠道建设、战略合作伙伴关系的拓展与管理。"},
        {"name": "仓储物流部", "duty": "一站式耗材配送与设备库存实时管理。"},
        {"name": "后勤保障部", "duty": "日常运营中的商务支持、采购管理、物资保障及后勤服务"},
        {"name": "财务与内控管理部", "duty": "负责公司资金管理、预算编制、成本核算、税务筹划及财务风险管控，为业务运营提供专业财务支撑与决策依据。"},
    ],
    "album": [],
}


# ── 权限树种子（顶层 + 子项；id 为数字 _id，与前端树 node-key 对齐）──
# 父级分组 id（3=售后、8=门户、9=系统、10=财务）仅作树分组，不直接授权。
# 排序与左侧主菜单一致：概览(1) 需求(2) 售后(3) 产品(4) 门户(8) 报表(11) 财务(10) 系统(9)。
_PERMISSION_SEED = [
    {"_id": 1, "label": "系统概览", "code": "dashboard", "icon": "Monitor", "sort": 1, "parentId": None},
    {"_id": 2, "label": "需求单管理", "code": "demand", "icon": "Document", "sort": 2, "parentId": None},
    {"_id": 3, "label": "售后报修管理", "code": "repair", "icon": "Headset", "sort": 3, "parentId": None,
     "children": [
         {"_id": 31, "label": "一键报修", "code": "repair:create"},
         {"_id": 32, "label": "我的报修 / 工单", "code": "repair:my"},
         {"_id": 33, "label": "所有工单", "code": "repair:all"},
         {"_id": 34, "label": "工程师排期", "code": "repair:schedule"},
         {"_id": 35, "label": "投诉建议管理", "code": "complaints"},
         {"_id": 37, "label": "工单调阅/导出", "code": "repair:audit"},
     ]},
    {"_id": 12, "label": "小程序管理", "code": "miniapp", "icon": "Cellphone", "sort": 4, "parentId": None,
     "children": [
         {"_id": 36, "label": "联系我们配置", "code": "contact"},
         {"_id": 38, "label": "知识库管理", "code": "knowledge"},
     ]},
    {"_id": 4, "label": "产品中心", "code": "products", "icon": "Box", "sort": 5, "parentId": None},
    {"_id": 8, "label": "门户网站管理", "code": "portal", "icon": "Setting", "sort": 6, "parentId": None,
     "children": [
         {"_id": 81, "label": "全局配置", "code": "config"},
         {"_id": 82, "label": "新闻中心", "code": "news"},
         {"_id": 83, "label": "荣誉与相册", "code": "honors"},
         {"_id": 84, "label": "合作伙伴与案例", "code": "cases"},
     ]},
    {"_id": 11, "label": "数据报表", "code": "report", "icon": "DataAnalysis", "sort": 7, "parentId": None},
    {"_id": 10, "label": "财务管理", "code": "finance", "icon": "Wallet", "sort": 8, "parentId": None,
     "children": [
         {"_id": 101, "label": "共享文件", "code": "finance:files"},
         {"_id": 102, "label": "资产管理", "code": "finance:assets"},
         {"_id": 103, "label": "车辆管理", "code": "finance:vehicle"},
     ]},
    {"_id": 9, "label": "系统管理", "code": "system", "icon": "Setting", "sort": 9, "parentId": None,
     "children": [
         {"_id": 91, "label": "成员管理", "code": "system:users"},
         {"_id": 92, "label": "权限设置", "code": "system:roles"},
         {"_id": 93, "label": "操作日志", "code": "system:logs"},
         {"_id": 94, "label": "数据字典", "code": "system:dict"},
         {"_id": 95, "label": "部门管理", "code": "system:depts"},
         {"_id": 96, "label": "系统设置", "code": "system:settings"},
         {"_id": 97, "label": "回收站", "code": "system:recycle"},
     ]},
]

# 父级分组权限 id（仅树分组，不直接授权）
_PARENT_PERM_IDS = {3, 8, 9, 10, 12}

# 门户权限树重构：旧叶子 id → 新叶子 id（一次性重映射自定义角色的历史权限）
_REMAP_PERMS = {5: 82, 6: 83, 7: 84, 8: 81}

# RBAC 迁移版本号（一次性对齐默认权限/合并陈旧角色时递增）
_RBAC_VERSION = 8

# ── 角色种子（7 种，rank 越小权限越高；builtin 角色禁删、code 不可改）──
# 注：permissionIds 只存叶子权限；父级分组 id 仅作树分组，不存储。
_ROLE_SEED = [
    {"roleName": "超级管理员", "code": "super_admin", "rank": 0, "builtin": True,
     "permissionIds": [1, 2, 31, 32, 33, 34, 35, 36, 38, 37, 4, 81, 82, 83, 84, 91, 92, 93, 94, 95, 96, 97, 101, 102, 103, 11]},
    {"roleName": "管理员", "code": "admin", "rank": 1, "builtin": True,
     "permissionIds": [1, 2, 31, 32, 33, 34, 35, 36, 38, 37, 4, 81, 82, 83, 84, 91, 93, 94, 95, 96, 97, 101, 102, 103, 11]},
    {"roleName": "业务", "code": "business", "rank": 2, "builtin": False,
     "permissionIds": [1, 2, 31, 32, 33, 35]},
    {"roleName": "财务", "code": "finance", "rank": 2, "builtin": False,
     "permissionIds": [1, 37, 101, 102, 103, 11]},
    {"roleName": "运营", "code": "operation", "rank": 2, "builtin": False,
     "permissionIds": [1, 35, 36, 38, 4, 81, 82, 83, 84]},
    {"roleName": "工程师", "code": "engineer", "rank": 2, "builtin": False,
     "permissionIds": [1, 31, 32, 33, 34]},
    {"roleName": "普通用户", "code": "normal", "rank": 3, "builtin": False,
     "permissionIds": [1, 31, 32]},
]

# 旧角色 code → 新角色 code（角色重命名迁移）
_LEGACY_ROLE_CODE = {
    "admin": "super_admin",
    "internal": "business",
}

# 陈旧角色 code → 目标角色 code（合并：删除陈旧角色 + 用户 remap）
_LEGACY_ROLE_MERGE = {
    "sales": "business",
    "support": "business",
    "operator": "operation",
    "logistics": "operation",
}

# 旧用户 role 中文名 → (新 roleName, 新 roleCode)
_LEGACY_USER_ROLE = {
    "管理员": ("超级管理员", "super_admin"),
    "内部员工": ("业务", "business"),
    "外部人员": ("普通用户", "normal"),
    "工程师": ("工程师", "engineer"),
    "超级管理员": ("超级管理员", "super_admin"),
    "后勤": ("运营", "operation"),
    "财务": ("财务", "finance"),
    "销售": ("业务", "business"),
    "售后支持": ("业务", "business"),
    "运营专员": ("运营", "operation"),
}

# 旧用户 userType → 新 roleCode
_LEGACY_USER_TYPE = {
    "admin": "super_admin",
    "internal": "business",
    "engineer": "engineer",
    "normal": "normal",
    "business": "business",
    "logistics": "operation",
    "super_admin": "super_admin",
    "finance": "finance",
    "sales": "business",
    "support": "business",
    "operator": "operation",
    "operation": "operation",
}


# ── 数据字典种子（集中维护业务枚举；业务下拉后续统一改从字典读）──
# 每项：(分组 type, 显示 label, 存储 value)
_DICT_SEED = [
    ("产品分类", "彩色办公", "color"),
    ("产品分类", "高效黑白", "bw"),
    ("设备类型", "电脑", "电脑"),
    ("设备类型", "打印机", "打印机"),
    ("设备类型", "复印机", "复印机"),
    ("设备类型", "投影仪", "投影仪"),
    ("设备类型", "扫描仪", "扫描仪"),
    ("设备类型", "网络设备", "网络设备"),
    ("设备类型", "大屏", "大屏"),
    ("设备类型", "其他", "其他"),
    ("工单类型", "售后上门", "售后上门"),
    ("工单类型", "协助送货", "协助送货"),
    ("工单类型", "设备培训", "设备培训"),
    ("投诉分类", "服务态度", "服务态度"),
    ("投诉分类", "响应速度", "响应速度"),
    ("投诉分类", "配件质量", "配件质量"),
    ("投诉分类", "设备质量", "设备质量"),
    ("优先级", "普通", "普通"),
    ("优先级", "紧急", "紧急"),
    ("优先级", "特急", "特急"),
    ("资产分类", "车辆", "车辆"),
    ("资产分类", "设备", "设备"),
    ("资产分类", "办公家具", "办公家具"),
    ("资产分类", "IT设备", "IT设备"),
    ("资产分类", "其他", "其他"),
    ("文件分类", "发票登记", "invoice"),
    ("文件分类", "财务报表", "report"),
    ("文件分类", "制度文件", "policy"),
    ("文件分类", "合同存档", "contract"),
    ("文件分类", "其他", "other"),
]


# ── 组织架构种子（部门树，顶层 parentId 为空；资产/用户下拉改从本集合读）──
_DEPARTMENT_SEED = [
    {"name": "总经办", "parentId": None, "leader": "", "sort": 1},
    {"name": "财务部", "parentId": None, "leader": "", "sort": 2},
    {"name": "销售部", "parentId": None, "leader": "", "sort": 3},
    {"name": "售后部", "parentId": None, "leader": "", "sort": 4},
    {"name": "行政部", "parentId": None, "leader": "", "sort": 5},
    {"name": "技术部", "parentId": None, "leader": "", "sort": 6},
]


# ── 系统设置种子（对内系统配置，与门户 global_config 区分）──
_SYSTEM_SETTINGS_DEFAULT = {
    "_id": "system",
    "siteName": "鸿瑞办公CMS",
    "logo": "",
    "loginStrategy": "password",       # password / approval
    "approvalSwitch": False,           # 新用户注册审批开关
    "notificationSwitch": True,        # 站内通知总开关
    "passwordPolicy": {"minLength": 6, "expireDays": 0},
    "dataRetention": {"repairDays": 365, "logDays": 180},
    "updatedAt": None,
}


async def _migrate_permissions(db):
    """幂等同步权限节点：以种子为准补齐缺失节点、清理孤儿节点与陈旧子项（含子项迁移）"""
    # 0) 清理不在种子中的顶级节点（权限树重构后遗留的孤儿节点，如旧新闻/荣誉/案例/全局配置）
    seed_ids = {perm["_id"] for perm in _PERMISSION_SEED}
    async for doc in db.permissions.find({}):
        if doc["_id"] not in seed_ids:
            await db.permissions.delete_one({"_id": doc["_id"]})
    for perm in _PERMISSION_SEED:
        existing = await db.permissions.find_one({"_id": perm["_id"]})
        if existing is None:
            await db.permissions.insert_one(dict(perm))
            continue
        # 同步 label/code/icon/sort/parentId + 子项（子项以种子为准，覆盖增删与分组迁移）
        update = {k: perm[k] for k in ("label", "code", "icon", "sort", "parentId") if k in perm}
        update["children"] = perm.get("children", [])
        await db.permissions.update_one({"_id": perm["_id"]}, {"$set": update})


async def _migrate_roles(db):
    """旧角色改名/改码 + 补 rank/builtin + 补齐缺失角色（不覆盖已自定义的 permissionIds）"""
    # 0) 权限树重构重映射（幂等）：旧叶子 id → 新叶子 id，需在父级清理之前执行，
    #    否则 8 被当成分组 id 清掉、自定义角色会丢失「全局配置」权限。
    async for r in db.roles.find({}):
        ids = r.get("permissionIds") or []
        new_ids = list(dict.fromkeys(_REMAP_PERMS.get(pid, pid) for pid in ids))
        if new_ids != ids:
            await db.roles.update_one({"_id": r["_id"]}, {"$set": {"permissionIds": new_ids}})
    # 1) 旧 code 改名/改码（保留 permissionIds）
    for old_code, new_code in _LEGACY_ROLE_CODE.items():
        role = await db.roles.find_one({"code": old_code})
        if role is None:
            continue
        # 目标 code 已存在（迁移已完成）→ 跳过改名，避免唯一索引冲突。
        if await db.roles.find_one({"code": new_code}) is not None:
            continue
        target = next((r for r in _ROLE_SEED if r["code"] == new_code), None)
        await db.roles.update_one(
            {"_id": role["_id"]},
            {"$set": {
                "roleName": target["roleName"] if target else role.get("roleName"),
                "code": new_code,
                "rank": target["rank"] if target else 2,
                "builtin": target["builtin"] if target else False,
            }},
        )
    # 2) normal/engineer 补 rank/builtin + 显示名（code 不变）
    for code, name, rank, builtin in (("normal", "普通用户", 3, False), ("engineer", "工程师", 2, False)):
        await db.roles.update_one(
            {"code": code},
            {"$set": {"roleName": name, "rank": rank, "builtin": builtin}},
        )
    # 3) 补齐缺失角色（按 code）
    existing_codes = {r["code"] async for r in db.roles.find()}
    for role in _ROLE_SEED:
        if role["code"] not in existing_codes:
            await db.roles.insert_one(dict(role))
    # 4) 去除父级分组 id（仅树分组，直接授权无意义），避免级联树误显/重存越权
    async for r in db.roles.find({}):
        ids = r.get("permissionIds") or []
        cleaned = [pid for pid in ids if pid not in _PARENT_PERM_IDS]
        if cleaned != ids:
            await db.roles.update_one({"_id": r["_id"]}, {"$set": {"permissionIds": cleaned}})


async def _migrate_rbac_v2(db):
    """一次性迁移（版本门控）：合并陈旧角色 + 对齐 7 角色默认权限"""
    meta = await db.meta.find_one({"_id": "rbac"})
    if meta and meta.get("version", 0) >= _RBAC_VERSION:
        return
    # 1) 合并陈旧角色：删除陈旧角色（用户 remap 在 _migrate_users 中处理）
    for stale_code in _LEGACY_ROLE_MERGE.keys():
        stale = await db.roles.find_one({"code": stale_code})
        if stale is not None:
            await db.roles.delete_one({"_id": stale["_id"]})
    # 2) 对齐 7 个标准角色的名称/rank/builtin/默认权限
    for seed_role in _ROLE_SEED:
        await db.roles.update_one(
            {"code": seed_role["code"]},
            {"$set": {
                "roleName": seed_role["roleName"],
                "rank": seed_role["rank"],
                "builtin": seed_role["builtin"],
                "permissionIds": seed_role["permissionIds"],
            }},
        )
    # 3) 打版本标记
    await db.meta.update_one({"_id": "rbac"}, {"$set": {"version": _RBAC_VERSION}}, upsert=True)


async def _migrate_users(db):
    """用户：status 布尔→枚举、roleCode 重映射、role 显示名更新为 7 角色体系（幂等）"""
    async for u in db.users.find({}):
        updates = {}
        # status: bool → enum
        st = u.get("status")
        if isinstance(st, bool):
            updates["status"] = "active" if st else "disabled"
        elif st not in ("pending", "active", "disabled"):
            updates["status"] = "active"
        # roleCode：陈旧 code 重映射 → 旧 code 改名 → userType/role 兜底
        rc = u.get("roleCode")
        if rc in _LEGACY_ROLE_MERGE:
            rc = _LEGACY_ROLE_MERGE[rc]
        elif rc in _LEGACY_ROLE_CODE:
            rc = _LEGACY_ROLE_CODE[rc]
        elif not rc:
            ut = u.get("userType")
            rc = _LEGACY_USER_TYPE.get(ut) if ut else None
            if not rc:
                _, rc = _LEGACY_USER_ROLE.get(u.get("role", ""), ("", None))
        if rc and rc != u.get("roleCode"):
            updates["roleCode"] = rc
        # role 显示名
        old_role = u.get("role", "")
        new_name, _ = _LEGACY_USER_ROLE.get(old_role, (old_role, None))
        if new_name != old_role:
            updates["role"] = new_name
        if updates:
            await db.users.update_one({"_id": u["_id"]}, {"$set": updates})


# 工程师画像（统一 roleCode=engineer 用户；username 关联登录账号）
_ENGINEER_PROFILES = [
    {"username": "engineer", "name": "张工", "phone": "13811110001", "skills": ["门禁维修", "网络调试"], "desc": "10年安防设备维修经验", "team": "维保一组"},
    {"username": "lisi", "name": "李工", "phone": "13811110002", "skills": ["车牌识别", "道闸维修"], "desc": "8年停车系统维护经验", "team": "维保二组"},
    {"username": "wanggong", "name": "王工", "phone": "13811110003", "skills": ["人脸识别", "软件调试"], "desc": "5年智能硬件维修经验", "team": "维保一组"},
]

_ENGINEER_NAME_TO_USERNAME = {p["name"]: p["username"] for p in _ENGINEER_PROFILES}


async def _upsert_engineer_users(db):
    """确保工程师画像以用户（roleCode=engineer）形式存在（幂等）"""
    for ep in _ENGINEER_PROFILES:
        existing = await db.users.find_one({"username": ep["username"]})
        if existing is None:
            await db.users.insert_one({
                "username": ep["username"],
                "realName": ep["name"],
                "role": "工程师",
                "roleCode": "engineer",
                "phone": ep["phone"],
                "hashedPassword": hash_password("123456"),
                "status": "active",
                "avatar": "",
                "skills": ep["skills"],
                "showOnMobile": True,
                "desc": ep["desc"],
                "team": ep["team"],
                "lastLogin": None,
                "createdAt": datetime.now(timezone.utc),
            })
        else:
            await db.users.update_one(
                {"username": ep["username"]},
                {"$set": {
                    "role": "工程师",
                    "roleCode": "engineer",
                    "realName": ep["name"],
                    "phone": existing.get("phone") or ep["phone"],
                    "skills": existing.get("skills") or ep["skills"],
                    "showOnMobile": existing.get("showOnMobile", True),
                    "desc": existing.get("desc") or ep["desc"],
                    "team": existing.get("team") or ep["team"],
                }},
            )


async def _migrate_engineers(db):
    """旧 db.engineers → 工程师用户；更新排期/工单 engineerId（旧库一次性迁移，幂等）"""
    old_engs = await db.engineers.find({}).to_list(None)
    if not old_engs:
        return
    id_map = {}   # 旧 engineer _id → 用户 _id
    name_map = {}  # 旧 engineer name → 用户 _id
    for e in old_engs:
        name = e.get("name", "")
        uname = e.get("username") or _ENGINEER_NAME_TO_USERNAME.get(name) or ""
        user = await db.users.find_one({"username": uname}) if uname else None
        profile = {
            "role": "工程师",
            "roleCode": "engineer",
            "realName": name,
            "avatar": e.get("avatar", ""),
            "skills": e.get("skills", []),
            "showOnMobile": e.get("showOnMobile", True),
            "desc": e.get("desc", ""),
            "team": e.get("team", ""),
        }
        if user is None:
            if not uname:
                uname = f"engineer_{name or str(e['_id'])[-6:]}"
            profile.update({
                "username": uname,
                "phone": e.get("phone", ""),
                "hashedPassword": hash_password("123456"),
                "status": "active",
                "lastLogin": None,
                "createdAt": datetime.now(timezone.utc),
            })
            res = await db.users.insert_one(profile)
            new_id = str(res.inserted_id)
        else:
            await db.users.update_one({"_id": user["_id"]}, {"$set": profile})
            new_id = str(user["_id"])
        id_map[str(e["_id"])] = new_id
        name_map[name] = new_id
    # 更新排期 engineerId
    async for s in db.repair_schedule.find({}):
        new_id = id_map.get(s.get("engineerId", "")) or name_map.get(s.get("engineer", ""))
        if new_id and s.get("engineerId") != new_id:
            await db.repair_schedule.update_one({"_id": s["_id"]}, {"$set": {"engineerId": new_id}})
    # 更新工单 engineerId（按名称）
    for name, new_id in name_map.items():
        if name:
            await db.repairs.update_many({"engineer": name}, {"$set": {"engineerId": new_id}})


async def run_seed(db):
    """初始化种子数据（幂等：已存在则跳过）"""

    # ── 权限树 ──────────────────────────────────────
    await _migrate_permissions(db)

    # ── 角色 ────────────────────────────────────────
    await _migrate_roles(db)
    await _migrate_rbac_v2(db)

    # ── 超级管理员（CMS 共用，原 admin 升级）────────
    if await db.users.count_documents({"username": "admin"}) == 0:
        await db.users.insert_one({
            "username": "admin",
            "realName": "系统管理员",
            "role": "超级管理员",
            "roleCode": "super_admin",
            "phone": "13800000000",
            "hashedPassword": hash_password("123456"),
            "status": "active",
            "lastLogin": None,
            "createdAt": datetime.now(timezone.utc),
        })

    # ── 小程序测试账号 ──────────────────────────────
    test_accounts = [
        {"username": "user", "realName": "外部人员", "role": "普通用户", "roleCode": "normal", "phone": "13800000101"},
        {"username": "suser", "realName": "内部员工", "role": "业务", "roleCode": "business", "phone": "13800000102"},
        {"username": "engineer", "realName": "维修工程师", "role": "工程师", "roleCode": "engineer", "phone": "13800000103"},
        {"username": "finance", "realName": "财务专员", "role": "财务", "roleCode": "finance", "phone": "13800000104"},
        {"username": "operator", "realName": "运营专员", "role": "运营", "roleCode": "operation", "phone": "13800000105"},
    ]
    for acct in test_accounts:
        if await db.users.count_documents({"username": acct["username"]}) == 0:
            await db.users.insert_one({
                "username": acct["username"],
                "realName": acct["realName"],
                "role": acct["role"],
                "roleCode": acct["roleCode"],
                "phone": acct["phone"],
                "hashedPassword": hash_password("123456"),
                "status": "active",
                "lastLogin": None,
                "createdAt": datetime.now(timezone.utc),
            })

    # ── 示例用户 ────────────────────────────────────
    if await db.users.count_documents({"username": "zhangsan"}) == 0:
        await db.users.insert_many([
            {"username": "zhangsan", "realName": "张三", "role": "业务", "roleCode": "business",
             "phone": "13800000001",
             "hashedPassword": hash_password("123456"), "status": "active", "lastLogin": None,
             "createdAt": datetime.now(timezone.utc)},
            {"username": "lisi", "realName": "李四", "role": "工程师", "roleCode": "engineer",
             "phone": "13800000002",
             "hashedPassword": hash_password("123456"), "status": "active", "lastLogin": None,
             "createdAt": datetime.now(timezone.utc)},
        ])

    # ── 迁移历史用户（status 枚举 + roleCode + role 改名），幂等 ──
    await _migrate_users(db)

    # ── 示例产品 ────────────────────────────────────
    if await db.products.count_documents({}) == 0:
        await db.products.insert_many([
            {"name": "智能门禁终端 X1", "price": 12800, "speed": "0.2秒识别", "function": "人脸+指纹+刷卡",
             "stock": 200, "img": "", "techSpecs": ["7寸触摸屏", "200万双目摄像头", "IP65防水"],
             "category": "门禁设备", "createdAt": datetime.now(timezone.utc), "updatedAt": datetime.now(timezone.utc)},
            {"name": "车牌识别一体机 P300", "price": 25800, "speed": "0.1秒抬杆", "function": "车牌+车型识别",
             "stock": 80, "img": "", "techSpecs": ["500万像素", "支持新能源车牌", "夜间全彩"],
             "category": "停车设备", "createdAt": datetime.now(timezone.utc), "updatedAt": datetime.now(timezone.utc)},
            {"name": "人行通道闸 Q2", "price": 36000, "speed": "30人/分钟", "function": "人脸识别+防尾随",
             "stock": 50, "img": "", "techSpecs": ["304不锈钢", "红外防夹", "断电自动开门"],
             "category": "通道设备", "createdAt": datetime.now(timezone.utc), "updatedAt": datetime.now(timezone.utc)},
        ])

    # ── 示例新闻 ────────────────────────────────────
    if await db.news.count_documents({}) == 0:
        await db.news.insert_many([
            {"title": "鸿瑞科技荣获2024年度智慧安防创新奖", "type": "公司新闻",
             "content": "<p>2024年12月，鸿瑞科技凭借在智慧安防领域的持续创新...</p>",
             "cover": "", "views": 1250, "isPublished": True, "isPinned": True,
             "date": "2024-12-15", "createdAt": datetime.now(timezone.utc)},
            {"title": "新品发布：AI智能分析平台V3.0正式上线", "type": "产品动态",
             "content": "<p>全新升级的AI智能分析平台V3.0正式发布...</p>",
             "cover": "", "views": 890, "isPublished": True, "isPinned": False,
             "date": "2024-11-20", "createdAt": datetime.now(timezone.utc)},
            {"title": "2025年春节放假通知", "type": "通知公告",
             "content": "<p>根据国家法定节假日安排...</p>",
             "cover": "", "views": 2300, "isPublished": True, "isPinned": True,
             "date": "2025-01-20", "createdAt": datetime.now(timezone.utc)},
        ])

    # ── 示例技术知识库（小程序专用，独立于新闻中心）────────
    if await db.knowledge.count_documents({}) == 0:
        await db.knowledge.insert_many([
            {"title": "统信UOS国产系统安装打印机驱动完整教程", "type": "驱动安装",
             "content": "<p>适配惠普、佳能、爱普生等主流品牌，一步一步教你搞定：</p><ol><li>下载对应型号的 UOS 驱动包；</li><li>进入「打印管理器」添加打印机；</li><li>选择 PPD 文件并完成安装；</li><li>打印测试页验证。</li></ol>",
             "author": "张工", "cover": "", "views": 2300, "isPublished": True, "isPinned": True,
             "date": "2025-06-12", "createdAt": datetime.now(timezone.utc)},
            {"title": "打印机卡纸的快速处理与预防", "type": "故障案例",
             "content": "<p>打印机卡纸是售后最常见的问题之一。处理步骤：</p><ol><li>关机断电，打开纸盒与后盖；</li><li>沿出纸方向缓慢抽出卡纸，切勿逆向拉扯；</li><li>清理搓纸轮与纸屑，检查纸张是否受潮。</li></ol><p>预防：使用合格纸张，避免过厚或受潮，定期清洁搓纸轮。</p>",
             "author": "李工", "cover": "", "views": 320, "isPublished": True, "isPinned": True,
             "date": "2025-06-01", "createdAt": datetime.now(timezone.utc)},
            {"title": "车牌识别道闸不抬杆排查指南", "type": "故障案例",
             "content": "<p>现场常见原因：</p><ul><li>车牌脏污或反光导致识别失败；</li><li>地感线圈失效；</li><li>道闸控制板与相机联动线松动。</li></ul><p>先检查识别日志，再逐项排查硬件连线。</p>",
             "author": "王工", "cover": "", "views": 210, "isPublished": True, "isPinned": False,
             "date": "2025-05-20", "createdAt": datetime.now(timezone.utc)},
            {"title": "人脸识别终端固件升级操作手册", "type": "系统维护",
             "content": "<p>升级前务必备份配置：</p><ol><li>导出设备配置文件；</li><li>通过管理平台下发升级包；</li><li>升级完成后恢复配置并验证识别。</li></ol>",
             "author": "陈工", "cover": "", "views": 95, "isPublished": True, "isPinned": False,
             "date": "2025-04-12", "createdAt": datetime.now(timezone.utc)},
            {"title": "门禁控制器离线故障处理：网络与供电双维度排查", "type": "网络运维",
             "content": "<p>控制器离线通常与<strong>网络</strong>或<strong>供电</strong>相关：</p><ul><li>ping 网关确认网络连通；</li><li>检查 POE 交换机端口供电；</li><li>观察控制器指示灯状态。</li></ul><p>如属固件问题，需远程升级至最新版本。</p>",
             "author": "张工", "cover": "", "views": 150, "isPublished": True, "isPinned": True,
             "date": "2025-05-08", "createdAt": datetime.now(timezone.utc)},
            {"title": "海康POE摄像头离线排查：从交换机到网线的完整检测链路", "type": "监控安防",
             "content": "<p>供电不足、IP冲突、网线老化逐一排除：</p><ol><li>确认交换机端口供电功率是否足够；</li><li>检查摄像头 IP 是否与局域网冲突；</li><li>更换网线或端口测试连通性。</li></ol>",
             "author": "刘工", "cover": "", "views": 986, "isPublished": True, "isPinned": False,
             "date": "2025-05-15", "createdAt": datetime.now(timezone.utc)},
        ])

    # ── 示例荣誉 ────────────────────────────────────
    if await db.honors.count_documents({}) == 0:
        await db.honors.insert_many([
            {"title": "ISO 9001质量管理体系认证", "type": "cert", "url": "", "date": "2024-03-15"},
            {"title": "2024安防行业十大品牌", "type": "cert", "url": "", "date": "2024-06-20"},
            {"title": "公司年会团建活动", "type": "photo", "url": "", "date": "2024-09-10"},
        ])

    # ── 示例品牌 ────────────────────────────────────
    if await db.brands.count_documents({}) == 0:
        await db.brands.insert_many([
            {"name": "海康威视", "logo": "", "level": "战略合作伙伴", "url": "https://www.hikvision.com"},
            {"name": "大华股份", "logo": "", "level": "金牌代理", "url": "https://www.dahuatech.com"},
            {"name": "华为", "logo": "", "level": "技术合作伙伴", "url": "https://www.huawei.com"},
        ])

    # ── 示例案例 ────────────────────────────────────
    if await db.cases.count_documents({}) == 0:
        await db.cases.insert_many([
            {"client": "万科物业", "industry": "物业管理", "device": "门禁+车牌识别",
             "mode": "整体解决方案", "summary": "覆盖全国200+小区，日均通行100万人次",
             "date": "2024-08-01", "createdAt": datetime.now(timezone.utc)},
            {"client": "万达广场", "industry": "商业地产", "device": "智能停车+人行通道",
             "mode": "软硬件集成", "summary": "日均车流量5000+，人流量8万+",
             "date": "2024-06-15", "createdAt": datetime.now(timezone.utc)},
        ])

    # ── 示例线索 ────────────────────────────────────
    if await db.leads.count_documents({}) == 0:
        await db.leads.insert_many([
            {"name": "张先生", "phone": "13900001111", "category": "产品咨询", "content": "想了解门禁产品报价",
             "status": "待跟进", "remark": "", "createTime": "2025-01-15 10:30"},
            {"name": "李女士", "phone": "13900002222", "category": "售后报修", "content": "小区门禁无法识别",
             "status": "处理中", "remark": "已派工程师", "createTime": "2025-01-18 14:20"},
        ])

    # ── 工程师画像（roleCode=engineer 用户，统一排期/展示/联系我们）─────
    await _upsert_engineer_users(db)
    await _migrate_engineers(db)

    # ── 示例报修工单 + 排期联动（16 条工单 + 2 条锁定）────
    if await db.repairs.count_documents({}) == 0:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        today = now.date()
        monday = today - timedelta(days=today.weekday())
        dseq = now.strftime("%Y%m%d")

        # 工程师用户（roleCode=engineer）→ _id（排期/工单引用）
        eng_docs = await db.users.find({"roleCode": "engineer"}).to_list(None)
        eng_map = {e.get("realName", ""): str(e["_id"]) for e in eng_docs}

        def _r(seq, company, contact, phone, addr, priority, desc, engineer, status, progress, createdBy, hours_ago=0,
               device_type="", work_order_type="售后上门", fee=None,
               completed_by="", completed_at="", confirmed_by="", confirmed_at="", confirm_role="",
               is_rework=False, rework_of="", rework_reason=""):
            return {
                "orderNo": f"HR{dseq}{seq:03d}", "company": company, "contact": contact,
                "phone": phone, "address": addr, "priority": priority, "description": desc,
                "engineer": engineer, "engineerId": eng_map.get(engineer, ""),
                "status": status, "progress": progress,
                "createTime": (now - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S"),
                "createdBy": createdBy,
                "workOrderType": work_order_type,
                "deviceType": device_type,
                "fee": fee,
                "isRework": is_rework, "reworkOf": rework_of, "reworkReason": rework_reason,
                "reworkNote": "", "reworkCount": 0, "reworkChildNo": "",
                "completedBy": completed_by, "completedAt": completed_at,
                "confirmedBy": confirmed_by, "confirmedAt": confirmed_at, "confirmRole": confirm_role,
                "archived": status == "已归档",
            }

        # ────── 待接单 (4条) ──────
        repairs_data = [
            _r(1, "万科物业", "赵经理", "13900001111", "深圳市南山区万科云城3栋",
               "紧急", "小区西门门禁控制器故障，无法刷卡开门，影响业主出入",
               "", "待接单",
               [{"node": "工单已创建，系统自动派发", "time": "09:30", "status": "done"}],
               "admin", 2),
            _r(2, "万达广场", "孙主管", "13900002222", "深圳市宝安区万达广场B2停车场",
               "高", "停车场出口车牌识别一体机频繁误识别，抬杆延迟严重",
               "", "待接单",
               [{"node": "工单已创建，系统自动派发", "time": "10:15", "status": "done"}],
               "zhangsan", 3),
            _r(3, "华为基地", "周工", "13900003333", "深圳市龙岗区坂田华为基地F区",
               "普通", "员工通道人脸识别终端网络偶发断连，需排查",
               "", "待接单",
               [{"node": "工单已创建，系统自动派发", "time": "11:00", "status": "done"}],
               "admin", 4),
            _r(4, "招商银行", "林行长", "13900008888", "深圳市福田区招商银行大厦18层",
               "普通", "员工食堂消费POS机与门禁系统时间不同步",
               "", "待接单",
               [{"node": "工单已创建，系统自动派发", "time": "14:20", "status": "done"}],
               "admin", 1),
        ]

        # ────── 处理中 (7条) ──────
        repairs_data += [
            _r(5, "龙湖地产", "吴经理", "13900004444", "深圳市福田区龙湖春江天玺营销中心",
               "紧急", "营销中心人行通道闸机翼门不回弹，有安全隐患",
               "李工", "处理中",
               [{"node": "工单已创建，系统自动派发", "time": "08:30", "status": "done"},
                {"node": "已指派工程师：李工", "time": "08:45", "status": "done"},
                {"node": "工程师已到达现场，正在排查", "time": "09:30", "status": "doing"}],
               "admin", 5),
            _r(6, "平安大厦", "陈主任", "13900005555", "深圳市福田区益田路平安金融中心",
               "高", "大厦12层指纹门禁读头损坏，需更换备件",
               "王工", "处理中",
               [{"node": "工单已创建，系统自动派发", "time": "13:30", "status": "done"},
                {"node": "已指派工程师：王工", "time": "13:45", "status": "done"}],
               "zhangsan", 6),
            _r(7, "华润置地", "谢主管", "13900009999", "深圳市南山区华润万象天地B1",
               "高", "停车场管理系统无法自动计费，需紧急修复",
               "张工", "处理中",
               [{"node": "工单已创建，系统自动派发", "time": "14:00", "status": "done"},
                {"node": "已指派工程师：张工", "time": "14:10", "status": "done"},
                {"node": "正在排查计费服务器日志", "time": "15:00", "status": "doing"}],
               "admin", 7),
            _r(8, "恒大中心", "郭经理", "13900001010", "深圳市罗湖区恒大中心A座",
               "紧急", "监控室多路画面黑屏，安保系统瘫痪",
               "李工", "处理中",
               [{"node": "工单已创建，系统自动派发", "time": "09:00", "status": "done"},
                {"node": "已指派工程师：李工", "time": "09:10", "status": "done"},
                {"node": "已定位NVR主机硬盘故障，等待备件", "time": "10:30", "status": "doing"}],
               "admin", 8),
            _r(9, "中兴通讯", "唐工", "13900001112", "深圳市南山区科技园中兴研发大楼",
               "普通", "办公区网络门禁控制器离线，影响3个楼层通行",
               "李工", "处理中",
               [{"node": "工单已创建，系统自动派发", "time": "08:00", "status": "done"},
                {"node": "已指派工程师：李工", "time": "08:15", "status": "done"}],
               "lisi", 9),
            _r(10, "比亚迪", "冯工", "13900001113", "深圳市坪山区比亚迪研发中心",
               "普通", "厂区侧门门禁电源模块频繁跳闸",
               "张工", "处理中",
               [{"node": "工单已创建，系统自动派发", "time": "10:00", "status": "done"},
                {"node": "已指派工程师：张工", "time": "10:15", "status": "done"},
                {"node": "正在更换电源模块", "time": "11:00", "status": "doing"}],
               "admin", 10),
            _r(11, "联想大厦", "曹主任", "13900001114", "深圳市南山区联想大厦7层",
               "高", "人脸识别门禁一体机频繁重启，影响员工考勤",
               "王工", "处理中",
               [{"node": "工单已创建，系统自动派发", "time": "14:30", "status": "done"},
                {"node": "已指派工程师：王工", "time": "14:45", "status": "done"},
                {"node": "已确定固件版本问题，正在远程升级", "time": "15:30", "status": "doing"}],
               "zhangsan", 11),
        ]

        # ────── 已完成 (5条) ──────
        repairs_data += [
            _r(12, "腾讯滨海大厦", "郑工", "13900006666", "深圳市南山区科技中一路腾讯滨海大厦",
               "普通", "访客登记系统一体机触屏失灵",
               "张工", "已完成",
               [{"node": "工单已创建，系统自动派发", "time": "09:00", "status": "done"},
                {"node": "已指派工程师：张工", "time": "09:10", "status": "done"},
                {"node": "现场更换触摸屏模组", "time": "11:00", "status": "done"},
                {"node": "测试验证通过，客户签字确认", "time": "11:30", "status": "done"},
                {"node": "工单已处理完成，系统自动归档", "time": "11:45", "status": "done"}],
               "admin", 48),
            _r(13, "华侨城物业", "刘主管", "13900007777", "深圳市南山区华侨城纯水岸会所",
               "普通", "会所侧门读卡器雨天进水导致短路，已临时断电",
               "李工", "已完成",
               [{"node": "工单已创建，系统自动派发", "time": "14:00", "status": "done"},
                {"node": "已指派工程师：李工", "time": "14:15", "status": "done"},
                {"node": "更换防水读卡器并重新布线", "time": "16:00", "status": "done"},
                {"node": "工单已处理完成，系统自动归档", "time": "17:30", "status": "done"}],
               "lisi", 72),
            _r(14, "招商局大厦", "许经理", "13900001115", "深圳市南山区蛇口招商局广场",
               "普通", "大厦访客管理系统软件版本过旧需升级",
               "张工", "已完成",
               [{"node": "工单已创建，系统自动派发", "time": "08:00", "status": "done"},
                {"node": "已指派工程师：张工", "time": "08:10", "status": "done"},
                {"node": "完成V4.2版本升级，数据库迁移成功", "time": "10:00", "status": "done"},
                {"node": "工单已处理完成，系统自动归档", "time": "10:30", "status": "done"}],
               "admin", 60),
            _r(15, "大疆创新", "韩工", "13900001116", "深圳市南山区大疆天空之城",
               "普通", "新装闸机联动测试，需工程师现场配合",
               "王工", "已完成",
               [{"node": "工单已创建，系统自动派发", "time": "13:00", "status": "done"},
                {"node": "已指派工程师：王工", "time": "13:10", "status": "done"},
                {"node": "配合完成闸机与消防系统联动测试", "time": "16:00", "status": "done"},
                {"node": "工单已处理完成，系统自动归档", "time": "16:30", "status": "done"}],
               "admin", 55),
            _r(16, "小米科技", "罗经理", "13900001117", "深圳市南山区小米科技园",
               "普通", "停车管理系统从旧服务器迁移至新服务器",
               "王工", "已完成",
               [{"node": "工单已创建，系统自动派发", "time": "09:00", "status": "done"},
                {"node": "已指派工程师：王工", "time": "09:15", "status": "done"},
                {"node": "数据迁移与系统切换完成", "time": "12:00", "status": "done"},
                {"node": "工单已处理完成，系统自动归档", "time": "12:30", "status": "done"}],
               "lisi", 68),
        ]

        # ────── 新增状态演示：返修 + 待确认 + 已归档（req 2/3/4/5）──────
        _fmt_m = "%Y-%m-%d %H:%M"
        _rework_of = repairs_data[0]["orderNo"] if repairs_data else "HR0000000000"
        repairs_data += [
            _r(17, "腾讯滨海大厦", "郑工", "13900006666", "深圳市南山区科技中一路腾讯滨海大厦",
               "普通", "访客登记系统一体机触屏再次失灵（返修）",
               "", "待接单",
               [{"node": f"返修工单已创建（原单：{_rework_of}）", "time": (now - timedelta(hours=1)).strftime(_fmt_m), "status": "done"}],
               "admin", 1, "打印机", "售后上门", None, "", "", "", "", "",
               True, _rework_of, "故障再次出现"),
            _r(18, "龙湖地产", "吴经理", "13900004444", "深圳市福田区龙湖春江天玺营销中心",
               "高", "通道闸机翼门更换后待客户验收",
               "李工", "待确认",
               [{"node": "工单已创建，系统自动派发", "time": (now - timedelta(hours=3)).strftime(_fmt_m), "status": "done"},
                {"node": "已指派工程师：李工", "time": (now - timedelta(hours=3)).strftime(_fmt_m), "status": "done"},
                {"node": "工单已处理完成，等待客户确认", "time": (now - timedelta(hours=1)).strftime(_fmt_m), "status": "done"}],
               "admin", 3, "门禁设备", "售后上门", {"mode": "agreed", "amount": 200, "note": "含上门费", "paidBy": "客户"},
               "李工", (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")),
            _r(19, "平安大厦", "陈主任", "13900005555", "深圳市福田区益田路平安金融中心",
               "普通", "12层网络门禁控制器离线，已更换备件",
               "王工", "待确认",
               [{"node": "工单已创建，系统自动派发", "time": (now - timedelta(hours=5)).strftime(_fmt_m), "status": "done"},
                {"node": "已指派工程师：王工", "time": (now - timedelta(hours=5)).strftime(_fmt_m), "status": "done"},
                {"node": "工单已处理完成，等待客户确认", "time": (now - timedelta(hours=2)).strftime(_fmt_m), "status": "done"}],
               "zhangsan", 5, "网络设备", "售后上门", {"mode": "self", "amount": 350, "note": "现场议价", "paidBy": "客户"},
               "王工", (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
            _r(20, "招商银行", "林行长", "13900008888", "深圳市福田区招商银行大厦18层",
               "普通", "协助配送办公耗材及打印纸 20 箱",
               "李工", "已归档",
               [{"node": "工单已创建，系统自动派发", "time": (now - timedelta(hours=30)).strftime(_fmt_m), "status": "done"},
                {"node": "已指派工程师：李工", "time": (now - timedelta(hours=30)).strftime(_fmt_m), "status": "done"},
                {"node": "工单已处理完成，等待客户确认", "time": (now - timedelta(hours=28)).strftime(_fmt_m), "status": "done"},
                {"node": "客户已确认，工单归档", "time": (now - timedelta(hours=28)).strftime(_fmt_m), "status": "done"}],
               "admin", 30, "", "协助送货", None,
               "李工", (now - timedelta(hours=28)).strftime("%Y-%m-%d %H:%M:%S"),
               "林行长", (now - timedelta(hours=27)).strftime("%Y-%m-%d %H:%M:%S"), "customer"),
            _r(21, "华为基地", "周工", "13900003333", "深圳市龙岗区坂田华为基地F区",
               "普通", "大屏显示系统画面卡顿，已完成优化",
               "张工", "已归档",
               [{"node": "工单已创建，系统自动派发", "time": (now - timedelta(hours=50)).strftime(_fmt_m), "status": "done"},
                {"node": "已指派工程师：张工", "time": (now - timedelta(hours=50)).strftime(_fmt_m), "status": "done"},
                {"node": "工单已处理完成，等待客户确认", "time": (now - timedelta(hours=47)).strftime(_fmt_m), "status": "done"},
                {"node": "业务已确认，工单归档", "time": (now - timedelta(hours=46)).strftime(_fmt_m), "status": "done"}],
               "admin", 52, "大屏", "售后上门", {"mode": "agreed", "amount": 800, "note": "调试优化", "paidBy": "公司"},
               "张工", (now - timedelta(hours=47)).strftime("%Y-%m-%d %H:%M:%S"),
               "suser", (now - timedelta(hours=46)).strftime("%Y-%m-%d %H:%M:%S"), "business"),
        ]

        # 归一化进度时间：样例里是 "HH:MM"，补全年月日（取工单创建日期）
        for _rd in repairs_data:
            _ct = _rd.get("createTime", "")
            _date = _ct.split(" ")[0] if " " in _ct else ""
            for _p in _rd.get("progress", []):
                _t = _p.get("time", "")
                if _date and _t and ":" in _t and " " not in _t:
                    _p["time"] = f"{_date} {_t}"

        # 批量插入并记住 ID
        inserted = []
        for rd in repairs_data:
            r = await db.repairs.insert_one(rd)
            inserted.append((rd, str(r.inserted_id)))

        # ── 同步排期（14 条：12 条业务 + 2 条内部锁定）──
        if await db.repair_schedule.count_documents({}) == 0:
            def _s(d, slot, eng, company, rid, status):
                return {
                    "engineerId": eng_map.get(eng, ""),
                    "engineer": eng,
                    "date": (monday + timedelta(days=d)).strftime("%Y-%m-%d"),
                    "timeSlot": slot,
                    "type": "business",
                    "company": company,
                    "repairId": rid,
                    "status": status,
                    "createdAt": datetime.now(timezone.utc),
                }

            sched = [
                # ── 周一 Mon ──
                _s(0, "AM1", "李工", "龙湖地产", inserted[4][1], "处理中"),
                _s(0, "AM2", "张工", "招商局大厦", inserted[13][1], "已完成"),
                _s(0, "PM1", "张工", "华润置地", inserted[6][1], "处理中"),

                # ── 周二 Tue ──
                _s(1, "AM1", "张工", "腾讯滨海大厦", inserted[11][1], "已完成"),
                _s(1, "PM1", "王工", "平安大厦", inserted[5][1], "处理中"),
                _s(1, "PM2", "王工", "大疆创新", inserted[14][1], "已完成"),

                # ── 周三 Wed ──
                _s(2, "AM1", "李工", "恒大中心", inserted[7][1], "处理中"),
                _s(2, "PM1", "王工", "小米科技", inserted[15][1], "已完成"),
                _s(2, "PM2", "张工", "比亚迪", inserted[9][1], "处理中"),

                # ── 周四 Thu ──
                _s(3, "AM2", "李工", "华侨城物业", inserted[12][1], "已完成"),
                _s(3, "PM1", "李工", "中兴通讯", inserted[8][1], "处理中"),
                _s(3, "PM3", "张工", "设备培训(内部-锁定)", "", "已完成"),

                # ── 周五 Fri ──
                _s(4, "AM2", "王工", "联想大厦", inserted[10][1], "处理中"),
                _s(4, "PM3", "王工", "设备年检(内部-锁定)", "", "已完成"),
            ]

            # 内部任务标记为 break 类型（显示为锁定格）
            for e in sched:
                if "内部-锁定" in e["company"]:
                    e["type"] = "break"

            await db.repair_schedule.insert_many(sched)

    # ── 示例投诉建议 ────────────────────────────────
    if await db.complaints.count_documents({}) == 0:
        await db.complaints.insert_many([
            {
                "date": "2025-01-10", "customer": "黄女士", "target": "维修工程师张工",
                "category": "服务态度", "priority": "高",
                "status": "待处理",
                "content": "工程师上门维修时未穿工服，态度生硬，维修完成后未清理现场",
                "result": "",
            },
            {
                "date": "2025-01-12", "customer": "钱先生", "target": "客服热线",
                "category": "响应速度", "priority": "紧急",
                "status": "待处理",
                "content": "门禁故障报修后超过4小时无人响应，业主群投诉激增",
                "result": "",
            },
            {
                "date": "2025-01-08", "customer": "杨经理", "target": "备件供应",
                "category": "配件质量", "priority": "普通",
                "status": "处理中",
                "content": "更换的门禁控制板使用一周后再次故障，怀疑配件非原厂正品",
                "result": "已协调供应商提供原厂批次证明，安排工程师二次上门",
            },
            {
                "date": "2024-12-28", "customer": "马主任", "target": "道闸设备",
                "category": "设备质量", "priority": "普通",
                "status": "已解决",
                "content": "新安装的车牌识别道闸频繁死机，需要每天手动重启",
                "result": "确认为固件版本过旧导致，已升级至最新固件V4.2.1，连续运行7天无异常",
            },
        ])

    # ── 示例车辆（含「即将到期」与「已逾期」，演示到期提醒）────
    if await db.finance_vehicles.count_documents({}) == 0:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        d = now.date()

        def _d(delta_days):
            return (d + timedelta(days=delta_days)).strftime("%Y-%m-%d")

        await db.finance_vehicles.insert_many([
            {
                "plateNo": "粤B·F8K21", "brand": "五菱", "model": "宏光S", "vehicleType": "面包车",
                "vin": "LZWADAGA6ME000001", "engineNo": "M8C00001",
                "purchaseDate": _d(-900), "registerDate": _d(-880),
                "department": "售后部", "responsible": "张工", "mileage": 52000,
                "status": "在用", "img": "", "remark": "售后上门主力用车",
                "insurances": [
                    {"id": "s1", "type": "交强险", "insurer": "平安保险", "policyNo": "PA20260001",
                     "premium": 950, "startDate": _d(-355), "endDate": _d(10), "certs": [], "remark": ""},
                    {"id": "s2", "type": "商业险", "insurer": "平安保险", "policyNo": "PA20260002",
                     "premium": 3200, "startDate": _d(-355), "endDate": _d(10), "certs": [], "remark": ""},
                ],
                "annualInspectionDate": _d(120), "annualInspectionCerts": [],
                "nextMaintenanceDate": _d(25), "nextMaintenanceKm": 60000,
                "maintenance": [
                    {"id": "m1", "date": _d(-120), "km": 48000, "item": "更换机油机滤", "cost": 380, "vendor": "途虎养车", "remark": ""},
                ],
                "createdAt": now, "updatedAt": now,
            },
            {
                "plateNo": "粤B·3A6T9", "brand": "江铃", "model": "全顺", "vehicleType": "货车",
                "vin": "LJXCMFCB0MT000002", "engineNo": "JX000002",
                "purchaseDate": _d(-1200), "registerDate": _d(-1180),
                "department": "仓储物流部", "responsible": "李工", "mileage": 88000,
                "status": "在用", "img": "", "remark": "大件耗材配送",
                "insurances": [
                    {"id": "s3", "type": "交强险", "insurer": "人保财险", "policyNo": "RB20250009",
                     "premium": 1200, "startDate": _d(-370), "endDate": _d(-5), "certs": [], "remark": "已逾期，待续保"},
                ],
                "annualInspectionDate": _d(-15), "annualInspectionCerts": [],
                "nextMaintenanceDate": _d(5), "nextMaintenanceKm": 90000,
                "maintenance": [],
                "createdAt": now, "updatedAt": now,
            },
            {
                "plateNo": "粤B·9D2H7", "brand": "比亚迪", "model": "汉EV", "vehicleType": "轿车",
                "vin": "LGXCE6CD0P0000003", "engineNo": "EV000003",
                "purchaseDate": _d(-200), "registerDate": _d(-190),
                "department": "总经办", "responsible": "王总", "mileage": 15000,
                "status": "在用", "img": "", "remark": "商务接待",
                "insurances": [
                    {"id": "s4", "type": "商业险", "insurer": "太平洋保险", "policyNo": "TP20260003",
                     "premium": 6800, "startDate": _d(-180), "endDate": _d(185), "certs": [], "remark": ""},
                ],
                "annualInspectionDate": _d(200), "annualInspectionCerts": [],
                "nextMaintenanceDate": _d(90), "nextMaintenanceKm": 20000,
                "maintenance": [],
                "createdAt": now, "updatedAt": now,
            },
        ])

    # ── 全局配置 ────────────────────────────────────
    if await db.global_config.count_documents({}) == 0:
        await db.global_config.insert_one({
            "_id": "global",
            "basic": {
                "siteName": "鸿瑞科技",
                "logo": "",
                "favicon": "",
                "footer": "© 2024 鸿瑞科技 版权所有",
                "seoKeywords": "安防,智慧社区,门禁系统",
                "seoDescription": "鸿瑞科技 — 智慧安防解决方案提供商",
                "qrcode": "",
                "icp": "",
                "gongan": "",
            },
            "banners": [],
            "contact": {
                "address": "广东省深圳市南山区科技园路88号",
                "phone": "400-888-9999",
                "businessPhone": "400-888-9999",
                "email": "contact@hongrui.com",
                "workingHours": "周一至周五 9:00-18:00",
            },
            "map": {
                "latitude": 22.5431,
                "longitude": 113.949,
                "zoom": 15,
            },
            "services": _HOMEPAGE_SERVICES,
            "about": _HOMEPAGE_ABOUT,
        })
    else:
        # 补齐新版本新增字段（对已存在的库，幂等）
        existing = await db.global_config.find_one({"_id": "global"})
        if existing is not None:
            updates = {}
            # 服务/关于内容缺失或为空时，回填 homepage 既有内容
            if not existing.get("services"):
                updates["services"] = _HOMEPAGE_SERVICES
            if not existing.get("about"):
                updates["about"] = _HOMEPAGE_ABOUT
            basic = existing.get("basic", {})
            for k in ("qrcode", "icp", "gongan"):
                if k not in basic:
                    updates[f"basic.{k}"] = ""
            if updates:
                await db.global_config.update_one({"_id": "global"}, {"$set": updates})

    # ── 数据字典 ────────────────────────────────────
    if await db.dict_items.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        _sort = {}
        dict_docs = []
        for _type, _label, _value in _DICT_SEED:
            _sort[_type] = _sort.get(_type, 0) + 1
            dict_docs.append({
                "type": _type,
                "label": _label,
                "value": _value,
                "sort": _sort[_type],
                "enabled": True,
                "createdAt": now,
            })
        await db.dict_items.insert_many(dict_docs)

    # ── 部门架构（组织树）────────────────────────────
    if await db.departments.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        dept_docs = [{**d, "createdAt": now} for d in _DEPARTMENT_SEED]
        await db.departments.insert_many(dept_docs)

    # ── 系统设置（对内系统配置）──────────────────────
    if await db.system_settings.count_documents({}) == 0:
        await db.system_settings.insert_one(dict(_SYSTEM_SETTINGS_DEFAULT))

    # ── 示例日志 ────────────────────────────────────
    if await db.logs.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        await db.logs.insert_many([
            {"time": now.strftime("%Y-%m-%d %H:%M:%S"), "user": "admin", "module": "登录",
             "content": "管理员登录系统", "ip": "127.0.0.1", "result": "成功"},
            {"time": now.strftime("%Y-%m-%d %H:%M:%S"), "user": "admin", "module": "成员管理",
             "content": "新增成员：张三", "ip": "127.0.0.1", "result": "成功"},
        ])

    # ── 演示站内通知（空库回填，便于看到铃铛效果）────
    if await db.notifications.count_documents({}) == 0:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        await db.notifications.insert_many([
            {"type": "repair_archived", "title": "工单已归档",
             "content": "有工单已归档，可核算成本", "link": "/after_sales/all-tasks",
             "roleCodes": ["admin", "super_admin", "finance"], "userIds": [], "readBy": [],
             "createdAt": now - timedelta(minutes=5)},
            {"type": "repair_confirm", "title": "工单待确认归档",
             "content": "有工单已完结，等待客户/业务确认归档", "link": "/after_sales/all-tasks",
             "roleCodes": ["admin", "super_admin", "business"], "userIds": [], "readBy": [],
             "createdAt": now - timedelta(hours=1)},
            {"type": "complaint_new", "title": "新增投诉建议",
             "content": "有新的投诉建议待处理", "link": "/after_sales/complaints",
             "roleCodes": ["operation", "business", "admin", "super_admin"], "userIds": [], "readBy": [],
             "createdAt": now - timedelta(hours=3)},
        ])
