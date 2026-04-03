import { createRouter, createWebHistory } from 'vue-router'

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
        meta: { title: '工单详情', hidden: true } // 详情页通常不在菜单显示
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

  // 简单的登录校验
  const token = localStorage.getItem('admin_token')
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router