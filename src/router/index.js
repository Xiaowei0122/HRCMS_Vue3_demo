import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getUserInfo } from '@/utils/auth'

// ── 角色菜单访问映射 ──
// 路径前缀 → 允许的 userType 集合
const ROLE_ACCESS = {
  'dashboard':       new Set(['admin', 'internal', 'engineer', 'normal']),
  'leads':           new Set(['admin', 'internal']),
  'after_sales':     new Set(['admin', 'internal', 'engineer', 'normal']),
  'after_sales/repair-apply': new Set(['admin', 'internal', 'engineer', 'normal']),
  'after_sales/my-repairs':   new Set(['admin', 'internal', 'engineer', 'normal']),
  'after_sales/all-tasks':    new Set(['admin', 'internal', 'engineer']),
  'after_sales/schedule':     new Set(['admin', 'internal', 'engineer']),
  'after_sales/complaints':   new Set(['admin', 'internal', 'normal']),
  'after_sales/contact':      new Set(['admin', 'internal', 'engineer', 'normal']),
  'products':        new Set(['admin', 'internal']),
  'news':            new Set(['admin', 'internal']),
  'honors':          new Set(['admin', 'internal']),
  'cases':           new Set(['admin', 'internal']),
  'global-config':   new Set(['admin', 'internal']),
  'finance':         new Set(['admin', 'internal']),
  'system':          new Set(['admin']),
}

function canAccessRoute(path, userType) {
  if (userType === 'admin') return true  // 管理员全部可访问
  // 匹配最具体的路径
  const keys = Object.keys(ROLE_ACCESS).sort((a, b) => b.length - a.length)  // 长路径优先
  for (const key of keys) {
    if (path === `/${key}` || path.startsWith(`/${key}/`)) {
      const allowed = ROLE_ACCESS[key]
      // 内部员工可访问所有非系统管理页面
      if (userType === 'internal' && !path.startsWith('/system')) return true
      return allowed.has(userType)
    }
  }
  // 不在映射表中的路径默认仅 admin
  return userType === 'admin'
}

// 1. 定义路由表
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '安全登录' }
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      // --- 仪表盘 ---
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '系统概览' }
      },

      // --- 售后报修系统 (新模块) ---
      {
        path: 'after_sales/repair-apply',
        name: 'RepairApply',
        component: () => import('../views/after_sales/RepairApply.vue'),
        meta: { title: '一键报修' }
      },
      {
        path: 'after_sales/my-repairs',
        name: 'MyRepairs',
        component: () => import('../views/after_sales/MyRepairs.vue'),
        meta: { title: '我的报修' }
      },
      {
        path: 'after_sales/repair-detail/:id',
        name: 'RepairDetail',
        component: () => import('../views/after_sales/RepairDetail.vue'),
        meta: { title: '工单详情', hidden: true }
      },
      {
        path: 'after_sales/all-tasks',
        name: 'AllTasks',
        component: () => import('../views/after_sales/AllTasks.vue'),
        meta: { title: '所有工单(待接)' }
      },
      {
        path: 'after_sales/schedule',
        name: 'EngineerSchedule',
        component: () => import('../views/after_sales/EngineerSchedule.vue'),
        meta: { title: '工程师期排' }
      },
      {
        path: 'after_sales/complaints',
        name: 'Complaints',
        component: () => import('../views/after_sales/Complaints.vue'),
        meta: { title: '投诉建议' }
      },
      {
        path: 'after_sales/contact',
        name: 'ContactUs',
        component: () => import('../views/after_sales/ContactUs.vue'),
        meta: { title: '联系我们' }
      },

      // --- 门户配置 ---
      {
        path: 'global-config',
        name: 'GlobalConfig',
        component: () => import('../views/GlobalConfig.vue'),
        meta: { title: '门户全局配置' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/Products.vue'),
        meta: { title: '产品中心' }
      },
      {
        path: 'news',
        name: 'News',
        component: () => import('../views/News.vue'),
        meta: { title: '新闻中心' }
      },
      {
        path: 'honors',
        name: 'Honors',
        component: () => import('../views/Honors.vue'),
        meta: { title: '荣誉与相册' }
      },
      {
        path: 'cases',
        name: 'Cases',
        component: () => import('../views/Cases.vue'),
        meta: { title: '合作伙伴与案例' }
      },
      {
        path: 'leads',
        name: 'Leads',
        component: () => import('../views/Leads.vue'),
        meta: { title: '需求单管理' }
      },

      // --- 系统管理 ---
      {
        path: 'system/users',
        name: 'UserManage',
        component: () => import('../views/system/Users.vue'),
        meta: { title: '成员管理' }
      },
      {
        path: 'system/roles',
        name: 'RoleManage',
        component: () => import('../views/system/Roles.vue'),
        meta: { title: '权限分配' }
      },
      {
        path: 'system/logs',
        name: 'SysLogs',
        component: () => import('../views/system/Logs.vue'),
        meta: { title: '操作日志' }
      },

      // --- 财务管理 ---
      {
        path: 'finance/files',
        name: 'FinanceFiles',
        component: () => import('../views/finance/SharedFiles.vue'),
        meta: { title: '共享文件' }
      },
      {
        path: 'finance/assets',
        name: 'FinanceAssets',
        component: () => import('../views/finance/AssetManage.vue'),
        meta: { title: '资产管理' }
      }
    ]
  },
  // 404 兜底路由
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 2. 路由守卫
router.beforeEach((to, from, next) => {
  // 设置标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 鸿瑞办公CMS`
  }

  const token = getToken()

  if (to.name !== 'Login' && !token) {
    // 未登录 → 跳转登录页
    next({ name: 'Login' })
    return
  }

  if (to.name === 'Login' && token) {
    // 已登录 → 跳过登录页，直接进仪表盘
    next({ path: '/dashboard' })
    return
  }

  // 若已登录，校验角色是否有权访问目标路由
  if (token && to.path !== '/dashboard') {
    const userInfo = getUserInfo()
    const userType = userInfo?.userType || ''
    if (!canAccessRoute(to.path, userType)) {
      // 无权限 → 强制跳转仪表盘
      next({ path: '/dashboard' })
      return
    }
  }

  next()
})

export default router
