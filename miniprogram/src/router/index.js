/**
 * Vue Router 路由配置
 * 映射原 pages.json 中的 11 个页面
 */
import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/pages/public/home/index'
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
    meta: { title: '首页', noAuth: true }
  },
  {
    path: '/pages/public/profile/index',
    name: 'Profile',
    component: () => import('@/pages/public/profile/index.vue'),
    meta: { title: '个人中心', noAuth: true }
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
  // ── 消息通知 ──
  {
    path: '/pages/notifications/index',
    name: 'Notifications',
    component: () => import('@/pages/notifications/index.vue'),
    meta: { title: '消息通知' }
  },
  // ── 私信 ──
  {
    path: '/pages/messages/index',
    name: 'Messages',
    component: () => import('@/pages/messages/index.vue'),
    meta: { title: '私信' }
  },
  {
    path: '/pages/chat/index',
    name: 'Chat',
    component: () => import('@/pages/chat/index.vue'),
    meta: { title: '聊天' }
  },
  // ── 地址管理 ──
  {
    path: '/pages/address/index',
    name: 'Address',
    component: () => import('@/pages/address/index.vue'),
    meta: { title: '地址管理' }
  },
  {
    path: '/pages/address-edit/index',
    name: 'AddressEdit',
    component: () => import('@/pages/address-edit/index.vue'),
    meta: { title: '编辑地址' }
  },
  // ── 技术知识库 ──
  {
    path: '/pages/knowledge/index',
    name: 'Knowledge',
    component: () => import('@/pages/knowledge/index.vue'),
    meta: { title: '技术知识库', noAuth: true }
  },
  {
    path: '/pages/knowledge-detail/index',
    name: 'KnowledgeDetail',
    component: () => import('@/pages/knowledge-detail/index.vue'),
    meta: { title: '知识详情', noAuth: true }
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

// 路由守卫 — 登录检查 + 权限校验（权限码与后端 require_permission 对齐）
router.beforeEach((to, _from, next) => {
  document.title = to.meta.title || '鸿瑞售后报修'
  if (to.meta.noAuth) {
    return next()
  }
  const token = uni.getStorageSync('token')
  if (!token) {
    return next('/pages/public/login/index')
  }

  const userInfo = uni.getStorageSync('userInfo') || {}
  const roleCode = userInfo.roleCode || userInfo.userType || 'normal'
  const perms = roleCode === 'super_admin' ? ['*'] : (userInfo.permissions || [])
  const hasPerm = (...codes) => perms.includes('*') || codes.some((c) => perms.includes(c))

  // 页面 → 所需权限码（任一命中即放行；未列出页面对所有登录用户开放）
  const required = {
    '/pages/repair-apply/index': ['repair:create'],
    '/pages/my-repairs/index': ['repair:my'],
    '/pages/repair-detail/index': ['repair:my', 'repair:all', 'repair:audit'],
    '/pages/schedule/index': ['repair:schedule', 'repair:audit'],
    '/pages/engineer/all-orders/index': ['repair:all'],
    '/pages/engineer/my-orders/index': ['repair:all'],
  }[to.path]

  if (required && !hasPerm(...required)) {
    return next('/pages/public/home/index')
  }

  next()
})

export default router
