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
            {"_id": 10, "label": "财务管理", "code": "finance", "icon": "Wallet", "sort": 10, "parentId": None,
             "children": [
                 {"_id": 101, "label": "共享文件", "code": "finance:files"},
                 {"_id": 102, "label": "资产管理", "code": "finance:assets"},
             ]},
        ])

    # ── 角色 ────────────────────────────────────────
    # 4 种角色：管理员(全部权限)、内部员工、工程师(售后)、外部人员(受限)
    if await db.roles.count_documents({}) == 0:
        await db.roles.insert_many([
            {"roleName": "管理员", "code": "admin", "permissionIds": [1,2,3,31,32,33,34,35,36,4,5,6,7,8,9,91,92,93,10,101,102]},
            {"roleName": "内部员工", "code": "internal", "permissionIds": [1,2,3,31,32,33,34,35,36,4,5,6,7,8,10,101,102]},
            {"roleName": "工程师", "code": "engineer", "permissionIds": [1,3,31,32,33,34]},
            {"roleName": "外部人员", "code": "normal", "permissionIds": [1,3,31,32,35]},
        ])

    # ── 管理员（CMS 共用）──────────────────────────
    if await db.users.count_documents({"username": "admin"}) == 0:
        await db.users.insert_one({
            "username": "admin",
            "realName": "系统管理员",
            "role": "管理员",
            "userType": "admin",
            "phone": "13800000000",
            "hashedPassword": hash_password("123456"),
            "status": True,
            "lastLogin": None,
            "createdAt": datetime.now(timezone.utc),
        })
    else:
        # 已有 admin → 补 userType + 更新 role 为新体系
        await db.users.update_one(
            {"username": "admin", "role": "超级管理员"},
            {"$set": {"role": "管理员", "userType": "admin"}},
        )

    # ── 小程序测试账号 ──────────────────────────────
    test_accounts = [
        {"username": "user", "realName": "外部人员", "role": "外部人员", "userType": "normal", "phone": "13800000101"},
        {"username": "suser", "realName": "内部员工", "role": "内部员工", "userType": "internal", "phone": "13800000102"},
        {"username": "engineer", "realName": "维修工程师", "role": "工程师", "userType": "engineer", "phone": "13800000103"},
    ]
    for acct in test_accounts:
        if await db.users.count_documents({"username": acct["username"]}) == 0:
            await db.users.insert_one({
                "username": acct["username"],
                "realName": acct["realName"],
                "role": acct["role"],
                "userType": acct["userType"],
                "phone": acct["phone"],
                "hashedPassword": hash_password("123456"),
                "status": True,
                "lastLogin": None,
                "createdAt": datetime.now(timezone.utc),
            })
        else:
            # 已有账号 → 更新 role + userType 为新体系
            await db.users.update_one(
                {"username": acct["username"]},
                {"$set": {"role": acct["role"], "userType": acct["userType"]}},
            )

    # ── 示例用户 ────────────────────────────────────
    if await db.users.count_documents({"username": "zhangsan"}) == 0:
        await db.users.insert_many([
            {"username": "zhangsan", "realName": "张三", "role": "内部员工", "userType": "internal",
             "phone": "13800000001",
             "hashedPassword": hash_password("123456"), "status": True, "lastLogin": None,
             "createdAt": datetime.now(timezone.utc)},
            {"username": "lisi", "realName": "李四", "role": "工程师", "userType": "engineer",
             "phone": "13800000002",
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

    # ── 示例工程师（username 关联登录账号，供工程师自助接单定位到自己）─────
    if await db.engineers.count_documents({}) == 0:
        await db.engineers.insert_many([
            {"name": "张工", "username": "engineer", "phone": "13811110001", "avatar": "", "skills": ["门禁维修", "网络调试"], "showOnMobile": True,
             "desc": "10年安防设备维修经验", "team": "维保一组"},
            {"name": "李工", "username": "lisi", "phone": "13811110002", "avatar": "", "skills": ["车牌识别", "道闸维修"], "showOnMobile": True,
             "desc": "8年停车系统维护经验", "team": "维保二组"},
            {"name": "王工", "username": "", "phone": "13811110003", "avatar": "", "skills": ["人脸识别", "软件调试"], "showOnMobile": True,
             "desc": "5年智能硬件维修经验", "team": "维保一组"},
        ])
    else:
        # 已存在 → 幂等补齐 username 关联（王工暂无对应登录账号）
        _eng_links = {"张工": "engineer", "李工": "lisi", "王工": ""}
        for _name, _uname in _eng_links.items():
            await db.engineers.update_one(
                {"name": _name, "username": {"$exists": False}},
                {"$set": {"username": _uname}},
            )

    # ── 示例报修工单 + 排期联动（16 条工单 + 2 条锁定）────
    if await db.repairs.count_documents({}) == 0:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        today = now.date()
        monday = today - timedelta(days=today.weekday())
        dseq = now.strftime("%Y%m%d")

        def _r(seq, company, contact, phone, addr, priority, desc, engineer, status, progress, createdBy, hours_ago=0):
            return {
                "orderNo": f"HR{dseq}{seq:03d}", "company": company, "contact": contact,
                "phone": phone, "address": addr, "priority": priority, "description": desc,
                "engineer": engineer, "engineerId": "",
                "status": status, "progress": progress,
                "createTime": (now - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S"),
                "createdBy": createdBy,
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
            eng_docs = await db.engineers.find({}).to_list(None)
            eng_map = {e["name"]: str(e["_id"]) for e in eng_docs}

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
            "services": [
                {"id": "sales", "icon": "🛒", "title": "办公设备销售", "desc": "打印机、复印机、硒鼓耗材等全品类办公设备供应"},
                {"id": "repair", "icon": "🔧", "title": "售后维修", "desc": "快速响应上门维修，专业工程师团队全程保障"},
                {"id": "supplies", "icon": "📦", "title": "耗材供应", "desc": "原装正品耗材，稳定供货，价格透明"},
                {"id": "solutions", "icon": "💡", "title": "解决方案", "desc": "门禁、停车、安防等智慧办公整体解决方案"},
            ],
            "about": {
                "intro": "二十年办公设备与服务沉淀",
                "stats": [
                    {"num": "20+", "label": "全平台服务年限"},
                    {"num": "30+", "label": "服务品牌"},
                    {"num": "500+", "label": "服务企业客户"},
                    {"num": "24/7", "label": "全天候响应"},
                ],
                "culture": [
                    {"title": "客户至上", "desc": "以客户需求为中心，持续创造价值", "icon": "🤝"},
                    {"title": "技术创新", "desc": "拥抱新技术，驱动智慧办公升级", "icon": "💡"},
                    {"title": "诚信经营", "desc": "诚实守信，与伙伴共同成长", "icon": "🏆"},
                ],
                "depts": [
                    {"name": "总经办", "duty": "战略规划与综合管理"},
                    {"name": "销售部", "duty": "客户开拓与产品销售"},
                    {"name": "售后部", "duty": "维修保养与技术支持"},
                    {"name": "技术部", "duty": "方案设计与系统集成"},
                    {"name": "财务部", "duty": "财务核算与资产管理"},
                    {"name": "行政部", "duty": "行政后勤与人事管理"},
                ],
                "album": [],
            },
        })
    else:
        # 补齐新版本新增字段（对已存在的库，幂等）
        existing = await db.global_config.find_one({"_id": "global"})
        if existing is not None:
            updates = {}
            if "services" not in existing:
                updates["services"] = []
            if "about" not in existing:
                updates["about"] = {}
            basic = existing.get("basic", {})
            for k in ("qrcode", "icp", "gongan"):
                if k not in basic:
                    updates[f"basic.{k}"] = ""
            if updates:
                await db.global_config.update_one({"_id": "global"}, {"$set": updates})

    # ── 示例日志 ────────────────────────────────────
    if await db.logs.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        await db.logs.insert_many([
            {"time": now.strftime("%Y-%m-%d %H:%M:%S"), "user": "admin", "module": "登录",
             "content": "管理员登录系统", "ip": "127.0.0.1", "result": "成功"},
            {"time": now.strftime("%Y-%m-%d %H:%M:%S"), "user": "admin", "module": "成员管理",
             "content": "新增成员：张三", "ip": "127.0.0.1", "result": "成功"},
        ])
