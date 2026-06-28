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

> **最后更新**：2026-06-29