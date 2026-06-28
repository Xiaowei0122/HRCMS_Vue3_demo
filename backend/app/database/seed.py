"""种子数据：管理员账号 + 角色 + 权限树 + 示例数据"""
from datetime import datetime, timezone
from app.core.security import hash_password


async def run_seed(db):
    """初始化种子数据（幂等：已存在则跳过）"""

    # ── 权限树 ──────────────────────────────────────
    if await db.permissions.count_documents({}) == 0:
        await db.permissions.insert_many([
            {"_id": 1, "label": "系统概览", "code": "dashboard", "icon": "Monitor", "sort": 1, "parentId": None},
            {"_id": 2, "label": "需求单管理", "code": "demand", "icon": "Document", "sort": 2, "parentId": None},
            {"_id": 3, "label": "售后报修管理", "code": "repair", "icon": "Headset", "sort": 3, "parentId": None,
             "children": [
                 {"_id": 31, "label": "一键报修", "code": "repair:create"},
                 {"_id": 32, "label": "我的报修/工单", "code": "repair:my"},
                 {"_id": 33, "label": "所有工单", "code": "repair:all"},
                 {"_id": 34, "label": "工程师排期", "code": "repair:schedule"},
                 {"_id": 35, "label": "投诉建议管理", "code": "complaints"},
                 {"_id": 36, "label": "联系我们配置", "code": "contact"},
             ]},
            {"_id": 4, "label": "产品中心", "code": "products", "icon": "Box", "sort": 4, "parentId": None},
            {"_id": 5, "label": "新闻中心", "code": "news", "icon": "ChatDotSquare", "sort": 5, "parentId": None},
            {"_id": 6, "label": "荣誉与相册", "code": "honors", "icon": "Trophy", "sort": 6, "parentId": None},
            {"_id": 7, "label": "合作伙伴与案例", "code": "cases", "icon": "Briefcase", "sort": 7, "parentId": None},
            {"_id": 8, "label": "门户全局配置", "code": "config", "icon": "Setting", "sort": 8, "parentId": None},
            {"_id": 9, "label": "系统管理", "code": "system", "icon": "Setting", "sort": 9, "parentId": None,
             "children": [
                 {"_id": 91, "label": "成员管理", "code": "system:users"},
                 {"_id": 92, "label": "权限设置", "code": "system:roles"},
                 {"_id": 93, "label": "操作日志", "code": "system:logs"},
             ]},
        ])

    # ── 角色 ────────────────────────────────────────
    if await db.roles.count_documents({}) == 0:
        await db.roles.insert_many([
            {"roleName": "超级管理员", "code": "admin", "permissionIds": [1,2,3,31,32,33,34,35,36,4,5,6,7,8,9,91,92,93]},
            {"roleName": "销售主管", "code": "sales", "permissionIds": [2,4,5,6,7,8]},
            {"roleName": "技术支持", "code": "support", "permissionIds": [3,31,32,33,34,35,36]},
            {"roleName": "财务经理", "code": "finance", "permissionIds": [1,2]},
        ])

    # ── 管理员 ──────────────────────────────────────
    if await db.users.count_documents({"username": "admin"}) == 0:
        await db.users.insert_one({
            "username": "admin",
            "realName": "系统管理员",
            "role": "超级管理员",
            "phone": "13800000000",
            "hashedPassword": hash_password("123456"),
            "status": True,
            "lastLogin": None,
            "createdAt": datetime.now(timezone.utc),
        })

    # ── 示例用户 ────────────────────────────────────
    if await db.users.count_documents({"username": "zhangsan"}) == 0:
        await db.users.insert_many([
            {"username": "zhangsan", "realName": "张三", "role": "销售主管", "phone": "13800000001",
             "hashedPassword": hash_password("123456"), "status": True, "lastLogin": None,
             "createdAt": datetime.now(timezone.utc)},
            {"username": "lisi", "realName": "李四", "role": "技术支持", "phone": "13800000002",
             "hashedPassword": hash_password("123456"), "status": True, "lastLogin": None,
             "createdAt": datetime.now(timezone.utc)},
        ])

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

    # ── 示例工程师 ──────────────────────────────────
    if await db.engineers.count_documents({}) == 0:
        await db.engineers.insert_many([
            {"name": "张工", "phone": "13811110001", "avatar": "", "skills": ["门禁维修", "网络调试"], "showOnMobile": True,
             "desc": "10年安防设备维修经验", "team": "维保一组"},
            {"name": "李工", "phone": "13811110002", "avatar": "", "skills": ["车牌识别", "道闸维修"], "showOnMobile": True,
             "desc": "8年停车系统维护经验", "team": "维保二组"},
            {"name": "王工", "phone": "13811110003", "avatar": "", "skills": ["人脸识别", "软件调试"], "showOnMobile": True,
             "desc": "5年智能硬件维修经验", "team": "维保一组"},
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
            },
            "banners": [],
            "contact": {
                "address": "广东省深圳市南山区科技园路88号",
                "phone": "400-888-9999",
                "email": "contact@hongrui.com",
                "workingHours": "周一至周五 9:00-18:00",
            },
            "map": {
                "latitude": 22.5431,
                "longitude": 113.949,
                "zoom": 15,
            },
        })

    # ── 示例日志 ────────────────────────────────────
    if await db.logs.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        await db.logs.insert_many([
            {"time": now.strftime("%Y-%m-%d %H:%M:%S"), "user": "admin", "module": "登录",
             "content": "管理员登录系统", "ip": "127.0.0.1", "result": "成功"},
            {"time": now.strftime("%Y-%m-%d %H:%M:%S"), "user": "admin", "module": "成员管理",
             "content": "新增成员：张三", "ip": "127.0.0.1", "result": "成功"},
        ])
