/**
 * Vue Router 路由配置
 * 映射原 pages.json 中的 11 个页面
 */
import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/pages/public/login/index'
  },
  // ── 公共页面 ──
  {
    path: '/pages/public/login/index',
    name: 'Login',
    component: () => import('@/pages/public/login/index.vue'),
    meta: { title: '登录', noAuth: true }
  },
  {
    path: '/pages/public/register/index',
    name: 'Register',
    component: () => import('@/pages/public/register/index.vue'),
    meta: { title: '注册', noAuth: true }
  },
  {
    path: '/pages/public/home/index',
    name: 'Home',
    component: () => import('@/pages/public/home/index.vue'),
    meta: { title: '鸿瑞售后服务中心' }
  },
  // ── 报修 ──
  {
    path: '/pages/repair-apply/index',
    name: 'RepairApply',
    component: () => import('@/pages/repair-apply/index.vue'),
    meta: { title: '一键报修' }
  },
  {
    path: '/pages/my-repairs/index',
    name: 'MyRepairs',
    component: () => import('@/pages/my-repairs/index.vue'),
    meta: { title: '我的报修' }
  },
  {
    path: '/pages/repair-detail/index',
    name: 'RepairDetail',
    component: () => import('@/pages/repair-detail/index.vue'),
    meta: { title: '工单详情' }
  },
  // ── 排期 ──
  {
    path: '/pages/schedule/index',
    name: 'Schedule',
    component: () => import('@/pages/schedule/index.vue'),
    meta: { title: '工程师排期' }
  },
  // ── 投诉 ──
  {
    path: '/pages/complaint/index',
    name: 'Complaint',
    component: () => import('@/pages/complaint/index.vue'),
    meta: { title: '投诉建议' }
  },
  // ── 联系 ──
  {
    path: '/pages/contact/index',
    name: 'Contact',
    component: () => import('@/pages/contact/index.vue'),
    meta: { title: '联系我们' }
  },
  // ── 工程师 ──
  {
    path: '/pages/engineer/all-orders/index',
    name: 'AllOrders',
    component: () => import('@/pages/engineer/all-orders/index.vue'),
    meta: { title: '所有工单' }
  },
  {
    path: '/pages/engineer/my-orders/index',
    name: 'MyOrders',
    component: () => import('@/pages/engineer/my-orders/index.vue'),
    meta: { title: '我的工单' }
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 路由守卫 — 登录检查
router.beforeEach((to, _from, next) => {
  document.title = to.meta.title || '鸿瑞售后报修'
  if (to.meta.noAuth) {
    return next()
  }
  const token = localStorage.getItem('token')
  if (!token && to.path !== '/pages/public/login/index') {
    return next('/pages/public/login/index')
  }
  next()
})

export default router
