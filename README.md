# 鸿瑞办公CMS后台管理系统 - Vue3 Demo

这是基于 Vue 3 (Vite) 开发的综合管理后台示例。
项目实现了从基础内容管理 (CMS) 到深度业务逻辑（售后报修、工单调度）的全功能集成，采用模块化组件开发，样式统一提取并适配移动端。


## 项目结构（关键文件）
```
HRCMS_VUE3/
├─ package.json
├─ vite.config.js
├─ index.html
├─ src/
│  ├─ main.js
│  ├─ App.vue
│  ├─ layout/
│  │  └─ MainLayout.vue       # 核心布局组件（含侧边栏与导航）
│  ├─ router/
│  │  └─ index.js             # 路由配置中心
│  ├─ views/
│  │  ├─ after_sales/         # 售后业务模块
│  │  │  ├─ AllTasks.vue     # 工单管理主页（看板+列表）
│  │  │  ├─ RepairForm.vue   # 报修表单（弹窗/页面通用）
│  │  │  └─ ...              # 工程师排期、投诉建议等
│  │  ├─ system/              # 系统基础设置
│  │  ├─ Dashboard.vue        # 总览控制台
│  │  └─ Login.vue            # 登录页面
│  └─ assets/                 # 静态资源（Logo、图标等）
└─ public/
   └─ favicon.ico             # 站点图标

## 使用方法

1. 安装依赖：`npm install`  
2. 运行开发服务器：`npm run dev`  
3. 打包：`npm run build`  
4. 预览打包内容：`npm run preview`

## 说明

   UI 框架：全面采用 Element Plus 进行响应式开发。
   布局逻辑：使用 Flex 布局优化了顶部平铺看板，解决了宽屏下显示过短的问题。
   组件复用：RepairForm.vue 采用了高度解耦设计，既可作为独立报修页，也可嵌入弹窗使用。
   状态管理：通过 Vue 3 组合式 API 实现轻量化状态共享。

## Ver0.1版本

   初始化项目架构：搭建 Vue 3 + Vite + Element Plus 基础环境。
   构建 MainLayout：实现侧边栏导航与多级路由联动。
   开发售后核心：新增 AllTasks.vue，实现工单列表展示。

## Ver0.2版本

   视觉体验优化：
      重构了顶部平铺统计看板，采用 Flex 均匀排列并增加左侧色条，消除视觉空洞感。
      引入了状态“呼吸灯”圆点设计，增强工单进度的直观识别度。
   功能逻辑增强：
      在 AllTasks.vue 中集成了搜索与状态快速筛选功能。
      新增了基于时间戳的工单编号自动生成逻辑。

## Ver0.3版本
   交互深度整合：
      将 RepairForm.vue 嵌入到工单列表的“录入”弹窗中。
      优化了弹窗内的表单排版，采用双列布局提升空间利用率。
      添加了提交时的 Loading 状态与 ElMessage 友好提示。
   响应式适配：
      调整了 HeaderBar 在不同分辨率下的间距。
      修复了表格在小屏幕下的横向滚动体验。

## Ver0.4版本
   文档规范化：编写并整合了项目 README 示例文档。
   细节打磨：
      统一了全局 main.css 的品牌配色。
      优化了工单详情页的面包屑导航逻辑。
      预留了高德地图 API 接口用于后续《联系我们》模块的地图展示。

##Ver 0.5版本
版本定位：系统闭环架构初步成型（从业务操作向管理决策升级）

   -新增功能 (New Features)
      🛡️权限与角色体系 (Permission & Roles)
      多维权限分配面板：重构了 Roles 组件，支持左侧角色列表与右侧权限树联动。

      菜单级粒度控制：权限树精准匹配最新菜单结构（售后、内容、门户配置等），支持父子节点关联勾选。

   -预设核心角色：

      超级管理员(admin)：全量操作权限。
      商务部(信息维护)：侧重产品、新闻及门户展示配置。
      工程部(工程师)：侧重工单抢单、期排与个人进度管理。

   -公众号展示配置 (ContactUs Config)
      服务门户管理：新增 ContactUs 组件，专门用于配置微信公众号“联系我们”页面的展示逻辑。
      工程师名片化：支持配置工程师头像、专业领域标签（Tag）、联系电话。
      实时上下线控制：通过 Switch 开关一键控制工程师是否在移动端前端展示。

   -全局系统概览 (Dashboard)
      业务指挥中心：上线全新的仪表盘页面，集成四个核心统计维度。
      可视化监控：模拟展示了近一周的报修增长趋势与业务转化数据。
      情报待办流：新增“快捷指令”与“系统情报”看板，实时提醒待核实投诉与人员调休状态。

   UI/UX 优化 (Optimizations)
      投诉管理组件 (Complaints)：
      由原 ComplaintsTable 正式更名为 Complaints，统一命名规范。
      引入了呼吸灯动效用于“待处理”状态提醒。
      优化了详情展开页（Expand）的描述列表排版。

   -全局视觉统一：
      全线组件适配 Element Plus 风格，强化了卡片式布局（Card）的阴影与圆角设计。
      状态色值规范化：红色（紧急/投诉）、蓝色（进行中）、绿色（已结案/正常）。

   -技术细节 (Technical Improvements)
      组件通信：优化了角色切换时的 nextTick 渲染机制，确保 Tree 组件状态与后端数据同步。
      动态路由预览：在 Dashboard 中集成了常用业务模块的快捷跳转。
      数据结构：定义了标准的 id 映射体系，为下一步前后端联调打下基础。

## Ver 0.6 — 前后端联调 · 报修调度闭环 (2026-06-29)

版本定位：从纯前端 Demo 演进为全栈可运行系统，核心业务链路打通。

---

### 🏗️ 后端服务 (Backend — 新增)

- **技术栈**：FastAPI + MongoDB (Motor) + JWT 认证，运行于 `:8080`
- **项目结构**：
  ```
  backend/
  ├─ app/main.py              # 应用入口 (CORS、路由注册、生命周期)
  ├─ app/core/                # 配置、依赖注入、统一响应、安全工具
  ├─ app/routers/             # 16 个路由模块
  │  ├─ auth.py               # 登录/注册/Token 签发
  │  ├─ repairs.py            # 报修 CRUD + 指派 + 排期 + 工程师
  │  ├─ contact.py            # 联系我们 (公众号展示工程师)
  │  ├─ dashboard.py          # 仪表盘统计
  │  ├─ users.py / roles.py   # 用户与权限管理
  │  ├─ news.py / products.py / cases.py / honors.py / brands.py
  │  ├─ leads.py / complaints.py / config.py / logs.py / upload.py
  ├─ app/database/            # MongoDB 连接 + 种子数据
  ├─ app/models/              # Pydantic 模型定义
  └─ app/services/            # 业务逻辑层
  ```
- **数据库**：MongoDB `hrcms`，含 `repairs`、`repair_schedule`、`engineers`、`users` 等集合
- **环境配置**：`.env` / `.env.development` / `.env.production` 分离开发与生产配置

### 🔌 前端 API 层 (新增)

- **`src/api/`**：16 个 API 模块，覆盖全部后端路由
- **`src/utils/request.js`**：Axios 实例封装，含请求拦截 (JWT Token 注入) 与响应拦截 (统一错误处理)
- **`src/utils/auth.js`**：Token 存取、用户状态管理

### 🔧 核心功能修复与增强

- **报修指派联动排期** (根因修复)：修复 `assignRepair` API 参数双层嵌套 Bug → 指派后自动在 `repair_schedule` 集合创建排期记录
- **工单状态实时同步**：指派后 status 从"待接单" → "处理中"，并在进度流中追加"已指派工程师"节点
- **工程师排期接入真实数据**：`EngineerSchedule.vue` 从 mock 数据切换为 API 驱动 (`fetchEngineers` + `fetchSchedule`)，支持切换工程师自动刷新
- **排期-工单数据关联**：`get_engineer_schedule` 通过 `repairId` 关联查询 repair 表，注入 `orderNo` 和 `progress`
- **指派时间槽选择**：管理员指派时可选择具体时段（上午早/晚、下午早/中/晚、全天），替代硬编码"全天"

### 🔄 全模块前后端对接

- **Login.vue**：接真实登录接口，JWT Token 持久化
- **Dashboard**：统计看板接入 `/repairs/stats` 等实时数据
- **系统管理 (Users / Roles / Logs)**：用户 CRUD、角色权限、操作日志全部对接后端
- **内容管理 (News / Products / Cases / Honors / Leads)**：列表、新增、编辑全部走 API
- **售后模块 (MyRepairs / RepairApply / RepairDetail / Complaints)**：一站式报修流程完整贯通
- **联系我们 (ContactUs)**：公众号展示工程师的增删改查

### ⚙️ 工程化改进

- **Vite 代理**：`vite.config.js` 配置 `/api` 代理到 `:8080`，本地开发无跨域问题
- **路由优化**：`router/index.js` 重组模块分组，修复路由懒加载
- **Store 重构**：`taskStore.js` 全面改为 API 驱动的 Pinia actions

---

> **最后更新**：2026-07-11

---

## Ver 0.7 — 测试环境部署 · 售后数据闭环 · 一键启动 (2026-07-11)

版本定位：测试环境完整可跑，售后模块数据与排期全面联动，开发体验优化。

---

### 🚀 一键启动脚本

- **`start_dev.cmd`**：根目录双击启动，自动检查 MongoDB 连通性 → 启动后端 `:8080` → 启动前端 `:5173` → 打开浏览器
- 纯 ASCII 英文编写，根除 Windows 中文编码导致的闪退和乱码问题
- MongoDB 检测采用 .NET `TcpClient.Connect()`，无冗余输出

### 🗄️ 测试数据库配置

- **服务器**：`192.168.1.111:32769`（远程测试 MongoDB）
- **数据库**：`hrcms_test`
- **管理账号**：`admin` / `123456`
- **`backend/reset_db.py`**：一键删除并重建数据库，便于重置测试环境
- 种子数据在 FastAPI 启动时自动幂等执行（`run_seed` — 检查集合为空才插入）

### 📊 Dashboard 数据真实化

- **根因**：`Dashboard.vue` 的统计卡片和待办列表全部使用硬编码假数据（1,284 访客、15 报修单等）
- **修复**：`onMounted` 生命周期调用 `getDashboardStats()` 和 `getDashboardTodos()` API
- 四个统计卡片改为真实数据：系统用户 / 产品数量 / 报修工单 / 待跟进线索
- 待办列表改为 `v-for` 动态渲染，空态显示"暂无待办事项"

### 🔧 售后模块数据闭环

- **种子数据**（`backend/app/database/seed.py`）：
  - **16 条报修工单**：4 待接单 + 7 处理中 + 5 已完成，覆盖 10+ 企业客户场景
  - **4 条投诉建议**：待处理/处理中/已解决各状态
  - **14 条排期记录**：12 条业务工单 + 2 条内部锁定（培训/年检），均匀分布周一至周五
  - 排期通过 `repairId` 与工单交叉关联，`GET /repairs/schedule` 联表查询注入 `orderNo` 和 `progress`

- **排期矩阵覆盖**（三位工程师 x 五个工作日）：

  | 工程师 | 周一 | 周二 | 周三 | 周四 | 周五 |
  |---|---|---|---|---|---|
  | 张工 | AM2✅ PM1🔵 | AM1✅ | PM2🔵 | PM3🔒 | — |
  | 李工 | AM1🔵 | — | AM1🔵 | AM2✅ PM1🔵 | — |
  | 王工 | — | PM1🔵 PM2✅ | PM1✅ | — | AM2🔵 PM3🔒 |

### 🔗 工单-排期联动修复

- **时间槽映射统一**：`AllTasks.vue` 指派弹窗的 `timeSlotOptions` 从中文标签（"上午 (早)"）改为排期表格 slot ID（`AM1`/`AM2`/`PM1`/`PM2`/`PM3`），确保指派后能在排期矩阵正确定位
- **排期页快捷指派修复**：`taskStore.addTask` 的 business 分支改为两步调用 — `createRepair()` → `assignRepair()`，后者自动在 `repair_schedule` 集合创建排期条目并同步 `repairId` 关联
- **`EngineerSchedule.vue`**：`submitQuickAdd` 新增传递 `engineerId`，确保排期条目与工程师正确绑定
- **数据流转链路**：
  ```
  创建工单(待接单) → AllTasks指派 / 排期页快捷指派
       → PATCH assignRepair → 更新repair + 插入repair_schedule
       → GET /repairs/schedule → 联表查询 → 排期矩阵渲染
  ```

### 📋 数据库集合总览

| 集合 | 数量 | 说明 |
|---|---|---|
| `repairs` | 16 | 报修工单（4 待接单 / 7 处理中 / 5 已完成） |
| `repair_schedule` | 14 | 排期条目（12 业务 + 2 锁定） |
| `complaints` | 4 | 投诉建议 |
| `engineers` | 3 | 张工 / 李工 / 王工 |
| `users` | 3 | admin / zhangsan / lisi |
| `roles` | 4 | 超管 / 销售主管 / 技术支持 / 财务经理 |
| 其他 | — | products(3), news(3), honors(3), brands(3), cases(2), leads(2) |

---

## Ver 0.8 — 售后报修小程序 · 财务模块 · 公开门户 · 权限体系升级 (2026-08-17)

版本定位：系统从「管理后台」扩展为「后台 + 移动端 + 对外门户」三位一体的完整闭环，核心业务下沉到移动端。

---

### 📱 售后报修小程序（miniprogram — 新增）

- **技术栈**：uni-app（Vue 3 + Pinia + Vue Router），可编译发布至微信小程序（mp-weixin）与 H5 双端
- **应用名称**：鸿瑞售后报修（`miniprogram/src/manifest.json`）
- **页面结构**（`src/pages/`，共 11 个页面）：
  - **公共页**：登录 / 注册 / 首页（鸿瑞售后服务中心）
  - **报修主流程**：一键报修（repair-apply）、我的报修（my-repairs）、工单详情（repair-detail，含进度时间线）
  - **业务页**：工程师排期（schedule）、投诉建议（complaint）、联系我们（contact）
  - **工程师端**：所有工单（all-orders）、我的工单（my-orders）
- **组件库**：`CustomTabBar`（自定义底部导航）、`OrderCard`（工单卡片）、`ScheduleTable`（排期表）、`TimeLine`（进度时间线）、`EmptyState`（空状态）、`SvgIcon`（SVG 图标）
- **状态管理**（`src/stores/`）：`auth.js`（登录态 + 四级角色判断）、`repair.js`（工单/排期/工程师/统计）
- **请求封装**（`src/utils/request.js`）：基于 `uni.request`，自动注入 JWT、401 过期跳登录、统一错误 Toast、自动解包 `{ code, data }` 响应
- **状态常量**（`src/utils/repair-status.js`）：状态/优先级/排期时段（AM1~PM3）与 CMS 端完全对齐
- **对接真实 API**：登录/注册、报修 CRUD、工程师接单、管理员指派、进度追加、工单完成、转单、排期、统计全链路
- **路由守卫**：登录检查 + 角色分级权限（工程师/内部员工/外部人员/管理员各自可见页面不同）

### 🔐 权限与角色体系升级（RBAC 重构）

- **四级 userType 体系**：`admin`（管理员）/ `internal`（内部员工）/ `engineer`（工程师）/ `normal`（外部人员）
- **角色命名重构**：由原「超级管理员 / 销售主管 / 技术支持 / 财务经理」统一为「管理员 / 内部员工 / 工程师 / 外部人员」
- **兜底映射**：`deps.py` 新增 `_ROLE_TYPE_MAP` 与 `resolve_user_type()`，老数据按中文角色名自动归位
- **RBAC 守卫**：`require_user_types()` 统一后端接口权限校验，`get_optional_user()` 支持可选认证
- **小程序注册**：新增 `POST /auth/register`，注册默认归属「外部人员」，注册即返回登录态
- **前端路由级访问控制**：`router/index.js` 新增 `ROLE_ACCESS` 映射表 + `canAccessRoute()`，按 userType 精确控制菜单与页面可见性，无权限自动跳转仪表盘

### 💰 财务管理模块（finance — 新增）

- **后端路由** `finance.py`（权限：admin + internal）：
  - **共享文件**：上传 / 列表 / 编辑 / 删除 / 权限控制（可见性），支持分类（发票/报告/政策/合同/其他）、20MB 大小限制、文件类型白名单
  - **资产管理**：资产 CRUD、状态流转（在用/维修/闲置等）、维保记录（maintenance）增查
- **前端页面**：`finance/SharedFiles.vue`（共享文件）、`finance/AssetManage.vue`（资产管理）
- **权限树**：新增「财务管理」节点，含 `finance:files`、`finance:assets` 两个子权限

### 🌐 公开门户接口（public — 新增）

- **定位**：无需登录的只读接口，供官网（HRhomepage_vue3）等公开站点读取
- **`public.py` 路由**：
  - `/public/config`：站点全局配置（轮播/服务/关于/联系/备案号/地图）
  - `/public/banners`、`/public/brands`、`/public/cases`、`/public/honors`：展示数据只读
  - `/public/news` + `/public/news/{id}`：新闻列表与详情，详情自动浏览量自增，仅返回已发布（`isPublished`）内容
  - `/public/products` + `/public/products/{id}`：产品列表与详情
  - `/public/leads`：官网「联系我们」表单提交，自动落库为线索（待跟进）

### ⚙️ 前端工程化与配置增强

- **MainLayout 重构**：侧边栏逻辑组件化整合（原 `Sidebar.vue` 合并），菜单按角色动态渲染，新增「财务管理」入口
- **GlobalConfig 增强**：支持服务板块、关于我们、轮播图、联系信息、地图坐标等官网所需配置
- **config API 模块扩展**：新增 `services` / `about` / `banners` / `contact` / `map` 等接口封装
- **代码清理**：移除冗余的 `style.css`、`counter.js`、`RepairForm.vue` 等历史遗留文件

### 🗄️ 种子数据升级

- **权限树**：新增「财务管理」及两个子权限节点
- **角色体系**：4 种角色（管理员/内部员工/工程师/外部人员）替换原角色，权限码重新分配
- **小程序测试账号**：`user`（外部人员）/ `suser`（内部员工）/ `engineer`（工程师），密码统一 `123456`
- **老数据迁移**：已有 `admin`、`zhangsan`、`lisi` 账号自动补齐 `userType` 字段，实现平滑升级

---

## Ver 0.9 — 报修售后 7 项需求 · 微信登录 · 归档确认/费用/返修/导出 (2026-08-30)

版本定位：报修工单从「三段状态」升级为完整售后闭环（类型/设备 → 指派 → 完结 → 双向确认归档 → 返修），并引入微信统一身份与 Excel 导出。

---

### 🛠️ 工单模型与状态机升级（`repairs.py`）

- **新增字段**：`workOrderType`（售后上门 / 协助送货）、`deviceType`（电脑/打印机/复印机/投影仪/扫描仪/网络设备/大屏/其他）、`latitude`/`longitude`（地图选点，gcj02）、`fee`（费用对象 `{mode,amount,note,paidBy,setBy,settledAt}`）、返修关联 `reworkOf/isRework/reworkReason/reworkNote/reworkCount/reworkChildNo`、完结/确认信息 `completedBy/completedAt/confirmedBy/confirmedAt/confirmRole`、`archived`。
- **状态机**：`待接单 → 处理中 → 待确认 → 已归档`；保留历史 `已完成`，统一 `_is_archived(status) = status in ("已完成","已归档")` 处理统计/返修/导出。
- **双向确认归档**：工程师 `complete` → `待确认`（写入 `completedBy/At`）；客户（`normal`）或业务（`business`）`confirm` → `已归档`（写入 `confirmRole=customer/business`）。工程师不可确认归档。

### 💰 费用 / 返修 / 导出 / 自动填充

- **上门费用**：`PATCH /repairs/{id}/fee` 两种模式 `已协商好(agreed)` / `自行协商(self)`；`create`/`assign` 可选携带费用。
- **返修单**：`POST /repairs/{id}/rework` 复制原单生成新工单并关联原单号（`isRework=true`/`reworkOf`），原单 `reworkCount` 递增、进度追加；默认允许多次返修。
- **Excel 导出**：`GET /repairs/export`（openpyxl）按状态/单位/类型/日期范围导出 21 列表头。
- **二次自动填充**：`GET /repairs/lookup?company=` 按单位名匹配最近一条历史工单返回基础信息，供二次录入自动带出（可改）。

### 🔐 微信登录（统一身份 + 角色分层）

- **身份统一从微信获取**：`POST /auth/wechat-login`（`uni.login`→code→`jscode2session`→openid/unionid），内部员工与外部客户都走微信认证。
- **角色分层**：`admin/business/engineer/normal` 只是角色（admin 分配），对应不同权限；微信新用户自动注册默认 `roleCode=normal`、`status=active`（免审批），`wxOpenid`/`wxUnionid` 落库。
- **兜底**：用户名密码登录保留（`admin/123456` 超管引导账号）；后续 CMS 微信扫码登录复用 `unionid`。
- **配置**：`.env` 增加 `wechat_appid`/`wechat_secret`；`requirements.txt` 增加 `httpx`。

### 🗄️ 种子数据

- 示例工单 16 → **21 条**：新增返修/待确认/已归档演示数据，覆盖新状态与设备类型/费用字段。

---

> **最后更新**：2026-08-30

---