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


💡 后续计划：
   接入 Pinia 进行用户权限持久化管理。
   完善工程师派单池的拖拽交互功能。