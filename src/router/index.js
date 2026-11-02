import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/auth'
import { hasPerm } from '@/utils/permission'

// ── 路由路径 → 所需权限 code ──
const ROUTE_PERMS = {
  '/dashboard': ['dashboard'],
  '/leads': ['demand'],
  '/after_sales/repair-apply': ['repair:create'],
  '/after_sales/my-repairs': ['repair:my'],
  '/after_sales/all-tasks': ['repair:all', 'repair:audit'],
  '/after_sales/schedule': ['repair:schedule', 'repair:audit'],
  '/after_sales/complaints': ['complaints'],
  '/miniapp/contact': ['contact'],
  '/miniapp/knowledge': ['knowledge'],
  '/products': ['products'],
  '/news': ['news'],
  '/honors': ['honors'],
  '/cases': ['cases'],
  '/global-config': ['config'],
  '/finance/files': ['finance:files'],
  '/finance/assets': ['finance:assets'],
  '/finance/vehicles': ['finance:vehicle'],
  '/system/users': ['system:users'],
  '/system/roles': ['system:roles'],
  '/system/logs': ['system:logs'],
  '/system/dict': ['system:dict'],
  '/system/depts': ['system:depts'],
  '/system/settings': ['system:settings'],
  '/system/recycle': ['system:recycle'],
  '/reports': ['report'],
}

function canAccessRoute(path) {
  const codes = ROUTE_PERMS[path]
  if (codes) return hasPerm(...codes)
  // 工单详情为动态路由，归属于「我的报修 / 所有工单」（财务只读调阅也可查看）
  if (path.startsWith('/after_sales/repair-detail')) return hasPerm('repair:my', 'repair:all', 'repair:audit')
  // 未映射路径（404 兜底等）默认放行，由后端鉴权兜底
  return true
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

      // --- 个人能力（登录即有，不占权限位）---
      {
        path: 'todos',
        name: 'Todos',
        component: () => import('../views/Todos.vue'),
        meta: { title: '我的待办' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { title: '个人中心' }
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
        meta: { title: '工程师排期' }
      },
      {
        path: 'after_sales/complaints',
        name: 'Complaints',
        component: () => import('../views/after_sales/Complaints.vue'),
        meta: { title: '投诉建议' }
      },
      // --- 小程序管理 (新模块) ---
      {
        path: 'miniapp/contact',
        name: 'MiniappContact',
        component: () => import('../views/miniapp/ContactUs.vue'),
        meta: { title: '联系我们配置' }
      },
      {
        path: 'miniapp/knowledge',
        name: 'MiniappKnowledge',
        component: () => import('../views/miniapp/Knowledge.vue'),
        meta: { title: '知识库管理' }
      },

      // --- 门户配置 ---
      {
        path: 'global-config',
        name: 'GlobalConfig',
        component: () => import('../views/GlobalConfig.vue'),
        meta: { title: '全局配置' }
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
      {
        path: 'system/dict',
        name: 'DictManage',
        component: () => import('../views/system/Dict.vue'),
        meta: { title: '数据字典' }
      },
      {
        path: 'system/depts',
        name: 'DeptManage',
        component: () => import('../views/system/Depts.vue'),
        meta: { title: '部门管理' }
      },
      {
        path: 'system/settings',
        name: 'SystemSettings',
        component: () => import('../views/system/Settings.vue'),
        meta: { title: '系统设置' }
      },
      {
        path: 'system/recycle',
        name: 'RecycleBin',
        component: () => import('../views/system/Recycle.vue'),
        meta: { title: '回收站' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('../views/Reports.vue'),
        meta: { title: '数据报表' }
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
      },
      {
        path: 'finance/vehicles',
        name: 'FinanceVehicles',
        component: () => import('../views/finance/VehicleManage.vue'),
        meta: { title: '车辆管理' }
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

// 2. 路由守卫（vue-router 5：直接返回目标，不再使用 next() 回调）
router.beforeEach((to) => {
  // 设置标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 鸿瑞办公CMS`
  }

  const token = getToken()

  // 未登录 → 跳转登录页
  if (to.name !== 'Login' && !token) {
    return { name: 'Login' }
  }

  // 已登录 → 跳过登录页，直接进仪表盘
  if (to.name === 'Login' && token) {
    return { path: '/dashboard' }
  }

  // 已登录且访问非仪表盘路由 → 校验权限，无权限则强制回仪表盘
  if (token && to.path !== '/dashboard' && !canAccessRoute(to.path)) {
    return { path: '/dashboard' }
  }

  return true
})

export default router
