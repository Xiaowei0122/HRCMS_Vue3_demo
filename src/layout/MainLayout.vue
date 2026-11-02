<template>
  <el-container class="layout-container">
    <!-- ═══ 侧边栏 ═══ -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo-box">
        <div class="logo-icon">
          <el-icon :size="22"><Platform /></el-icon>
        </div>
        <transition name="fade-transform">
          <span v-if="!isCollapse" class="logo-text">鸿瑞办公 CMS</span>
        </transition>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
        :collapse="isCollapse"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>系统概览</template>
        </el-menu-item>

        <el-menu-item index="/todos">
          <el-icon><Finished /></el-icon>
          <template #title>我的待办</template>
        </el-menu-item>

        <el-menu-item index="/leads" v-if="canAccess('leads')">
          <el-icon><UserFilled /></el-icon>
          <template #title>需求单管理</template>
        </el-menu-item>

        <el-sub-menu index="after_sales" v-if="canAccess('after_sales')">
          <template #title>
            <el-icon><Service /></el-icon>
            <span>售后报修管理</span>
          </template>
          <el-menu-item index="/after_sales/repair-apply" v-if="canAccess('after_sales/repair-apply')">
            <el-icon><EditPen /></el-icon>
            <span>一键报修</span>
          </el-menu-item>
          <el-menu-item index="/after_sales/my-repairs" v-if="canAccess('after_sales/my-repairs')">
            <el-icon><List /></el-icon>
            <span>我的报修 / 工单</span>
          </el-menu-item>
          <el-menu-item index="/after_sales/all-tasks" v-if="canAccess('after_sales/all-tasks')">
            <el-icon><Files /></el-icon>
            <span>所有工单 (抢单池)</span>
          </el-menu-item>
          <el-menu-item index="/after_sales/schedule" v-if="canAccess('after_sales/schedule')">
            <el-icon><Calendar /></el-icon>
            <span>工程师排期</span>
          </el-menu-item>
          <el-menu-item index="/after_sales/complaints" v-if="canAccess('after_sales/complaints')">
            <el-icon><ChatDotSquare /></el-icon>
            <span>投诉建议管理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="miniapp" v-if="canAccess('miniapp')">
          <template #title>
            <el-icon><Cellphone /></el-icon>
            <span>小程序管理</span>
          </template>
          <el-menu-item index="/miniapp/contact" v-if="canAccess('miniapp/contact')">
            <el-icon><Location /></el-icon>
            <span>联系我们配置</span>
          </el-menu-item>
          <el-menu-item index="/miniapp/knowledge" v-if="canAccess('miniapp/knowledge')">
            <el-icon><Notebook /></el-icon>
            <span>知识库管理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/products" v-if="canAccess('products')">
          <el-icon><Printer /></el-icon>
          <template #title>产品中心</template>
        </el-menu-item>

        <el-sub-menu index="portal" v-if="canAccess('portal')">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>门户网站管理</span>
          </template>
          <el-menu-item index="/global-config" v-if="canAccess('global-config')">
            <el-icon><Tools /></el-icon>
            <span>全局配置</span>
          </el-menu-item>
          <el-menu-item index="/news" v-if="canAccess('news')">
            <el-icon><ChatLineRound /></el-icon>
            <span>新闻中心</span>
          </el-menu-item>
          <el-menu-item index="/honors" v-if="canAccess('honors')">
            <el-icon><Medal /></el-icon>
            <span>荣誉与相册</span>
          </el-menu-item>
          <el-menu-item index="/cases" v-if="canAccess('cases')">
            <el-icon><Suitcase /></el-icon>
            <span>合作伙伴与案例</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/reports" v-if="canAccess('reports')">
          <el-icon><TrendCharts /></el-icon>
          <template #title>数据报表</template>
        </el-menu-item>

        <el-sub-menu index="finance" v-if="canAccess('finance')">
          <template #title>
            <el-icon><Wallet /></el-icon>
            <span>财务管理</span>
          </template>
          <el-menu-item index="/finance/files" v-if="canAccess('finance/files')">
            <el-icon><Folder /></el-icon>
            <span>共享文件</span>
          </el-menu-item>
          <el-menu-item index="/finance/assets" v-if="canAccess('finance/assets')">
            <el-icon><Cpu /></el-icon>
            <span>资产管理</span>
          </el-menu-item>
          <el-menu-item index="/finance/vehicles" v-if="canAccess('finance/vehicles')">
            <el-icon><Van /></el-icon>
            <span>车辆管理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="system" v-if="canAccess('system')">
          <template #title>
            <el-icon><Management /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/users" v-if="canAccess('system/users')">
            <el-icon><User /></el-icon>
            <span>成员管理</span>
          </el-menu-item>
          <el-menu-item index="/system/roles" v-if="canAccess('system/roles')">
            <el-icon><Lock /></el-icon>
            <span>权限分配</span>
          </el-menu-item>
          <el-menu-item index="/system/logs" v-if="canAccess('system/logs')">
            <el-icon><DocumentCopy /></el-icon>
            <span>操作日志</span>
          </el-menu-item>
          <el-menu-item index="/system/dict" v-if="canAccess('system/dict')">
            <el-icon><Collection /></el-icon>
            <span>数据字典</span>
          </el-menu-item>
          <el-menu-item index="/system/depts" v-if="canAccess('system/depts')">
            <el-icon><OfficeBuilding /></el-icon>
            <span>部门管理</span>
          </el-menu-item>
          <el-menu-item index="/system/settings" v-if="canAccess('system/settings')">
            <el-icon><Tools /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
          <el-menu-item index="/system/recycle" v-if="canAccess('system/recycle')">
            <el-icon><RefreshLeft /></el-icon>
            <span>回收站</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- ═══ 右侧主体 ═══ -->
    <el-container direction="vertical">
      <!-- 头部 -->
      <el-header class="main-header">
        <div class="header-left">
          <el-button
            class="collapse-btn"
            :icon="isCollapse ? Expand : Fold"
            text
            @click="isCollapse = !isCollapse"
          />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">
              {{ $route.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 全局搜索 -->
          <div class="search-trigger" @click="openSearch">
            <el-icon><Search /></el-icon>
            <span class="search-hint">搜索</span>
            <span class="search-kbd">Ctrl K</span>
          </div>

          <!-- 通知铃铛 -->
          <el-popover
            placement="bottom-end"
            :width="360"
            trigger="click"
            @show="onNotifPanelShow"
          >
            <template #reference>
              <div class="bell-wrap">
                <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99">
                  <el-button class="bell-btn" :icon="Bell" text />
                </el-badge>
              </div>
            </template>
            <div class="notif-panel">
              <div class="notif-head">
                <span class="notif-title">通知消息</span>
                <el-button
                  v-if="notifications.length"
                  link
                  type="primary"
                  size="small"
                  @click="readAll"
                >全部已读</el-button>
              </div>
              <ul v-if="notifications.length" class="notif-list">
                <li
                  v-for="n in notifications"
                  :key="n.id"
                  :class="['notif-item', { unread: !n.read }]"
                  @click="openNotif(n)"
                >
                  <div class="notif-dot"></div>
                  <div class="notif-body">
                    <p class="notif-msg">{{ n.title }}</p>
                    <span class="notif-time">{{ formatTime(n.createdAt) }}</span>
                    <div v-if="notifChip(n)" class="notif-chip" :class="notifChip(n).cls" @click.stop="openNotif(n)">
                      {{ notifChip(n).label }}
                      <el-icon :size="12"><ArrowRight /></el-icon>
                    </div>
                  </div>
                </li>
              </ul>
              <div v-else class="notif-empty">
                <el-icon :size="36" color="#CBD5E1"><Bell /></el-icon>
                <p>暂无通知</p>
              </div>
            </div>
          </el-popover>

          <el-dropdown trigger="click">
            <span class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ currentUser.realName?.charAt(0) || 'A' }}
              </el-avatar>
              <span class="user-name">{{ currentUser.realName || '管理员' }}</span>
              <el-icon class="arrow-icon"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <el-icon><User /></el-icon>
                  {{ currentUser.realName || '管理员' }}
                </el-dropdown-item>
                <el-dropdown-item disabled>
                  <el-icon><Clock /></el-icon>
                  最后登录: {{ currentUser.lastLogin || '刚刚' }}
                </el-dropdown-item>
                <el-dropdown-item divided @click="goProfile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item @click="openChangePwd">
                  <el-icon><Lock /></el-icon>
                  修改密码
                </el-dropdown-item>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 页面内容 -->
      <el-main class="main-body">
        <router-view :key="$route.fullPath" />
      </el-main>
    </el-container>

    <!-- 全局搜索弹窗 -->
    <el-dialog
      v-model="searchVisible"
      width="560px"
      :show-close="false"
      append-to-body
      class="global-search-dialog"
    >
      <template #header>
        <div class="search-dialog-head">
          <el-icon><Search /></el-icon>
          <span>全局搜索</span>
          <span class="search-esc-hint">ESC 关闭</span>
        </div>
      </template>
      <div class="search-box">
        <el-input
          ref="searchInputRef"
          v-model="searchKeyword"
          placeholder="搜索页面 / 功能，如：工单、字典、成员…"
          size="large"
          clearable
          @keydown="onSearchKeydown"
        />
        <ul v-if="filteredResults.length" class="search-results">
          <li
            v-for="(item, i) in filteredResults"
            :key="item.path"
            :class="['search-item', { active: i === activeIndex }]"
            @mouseenter="activeIndex = i"
            @click="selectResult(item)"
          >
            <el-icon class="search-item-icon"><Platform /></el-icon>
            <span class="search-item-label">{{ item.label }}</span>
            <span class="search-item-path">{{ item.path }}</span>
          </li>
        </ul>
        <div v-else class="search-empty">未找到匹配的页面</div>
      </div>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="420px" append-to-body>
      <el-form :model="pwdForm" label-width="90px">
        <el-form-item label="旧密码">
          <el-input v-model="pwdForm.oldPassword" type="password" show-password placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="pwdForm.confirm" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitChangePwd">确认修改</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, computed, reactive, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataBoard, Setting, Printer, ChatLineRound, Medal,
  Suitcase, UserFilled, Management, User, Lock, DocumentCopy,
  Expand, Fold, ArrowDown, Service, EditPen, List, Files,
  Calendar, ChatDotSquare, Location, Platform, Clock, SwitchButton,
  Wallet, Folder, Cpu, Bell, Finished, Collection, Search,
  OfficeBuilding, Tools, RefreshLeft, TrendCharts, Van, Cellphone, Notebook, ArrowRight
} from '@element-plus/icons-vue'
import { clearAuth, getUserInfo, setUserInfo } from '@/utils/auth'
import { logout as apiLogout, changePassword, getUserInfo as apiGetUserInfo } from '@/api/modules/auth'
import { getNotifications, getUnreadCount, markNotificationRead } from '@/api/modules/notifications'

const isCollapse = ref(false)
const router = useRouter()

// 用户信息（响应式；挂载时向后端刷新一次，避免旧缓存缺失 permissions/rank）
const user = ref(getUserInfo() || {})

const currentUser = computed(() => user.value || { realName: '管理员' })

// ── 菜单权限（按权限 code 动态判定）──
const permSet = computed(() => {
  const u = user.value
  if (!u) return new Set()
  if (u.roleCode === 'super_admin') return new Set(['*'])
  return new Set(u.permissions || [])
})

const MENU_PERMS = {
  'dashboard': ['dashboard'],
  'leads': ['demand'],
  'after_sales': ['repair:create', 'repair:my', 'repair:all', 'repair:schedule', 'repair:audit', 'complaints'],
  'after_sales/repair-apply': ['repair:create'],
  'after_sales/my-repairs': ['repair:my'],
  'after_sales/all-tasks': ['repair:all', 'repair:audit'],
  'after_sales/schedule': ['repair:schedule', 'repair:audit'],
  'after_sales/complaints': ['complaints'],
  'miniapp': ['contact', 'knowledge'],
  'miniapp/contact': ['contact'],
  'miniapp/knowledge': ['knowledge'],
  'portal': ['config', 'news', 'honors', 'cases'],
  'products': ['products'],
  'news': ['news'],
  'honors': ['honors'],
  'cases': ['cases'],
  'global-config': ['config'],
  'finance': ['finance:files', 'finance:assets', 'finance:vehicle'],
  'finance/files': ['finance:files'],
  'finance/assets': ['finance:assets'],
  'finance/vehicles': ['finance:vehicle'],
  'reports': ['report'],
  'system': ['system:users', 'system:roles', 'system:logs', 'system:dict', 'system:depts', 'system:settings', 'system:recycle'],
  'system/users': ['system:users'],
  'system/roles': ['system:roles'],
  'system/logs': ['system:logs'],
  'system/dict': ['system:dict'],
  'system/depts': ['system:depts'],
  'system/settings': ['system:settings'],
  'system/recycle': ['system:recycle'],
}

const canAccess = (path) => {
  const codes = MENU_PERMS[path]
  if (!codes) return true
  if (permSet.value.has('*')) return true
  return codes.some((c) => permSet.value.has(c))
}

let notifTimer = null

onMounted(async () => {
  try {
    const fresh = await apiGetUserInfo()
    setUserInfo(fresh)
    user.value = fresh
  } catch { /* 忽略，沿用缓存 */ }
  loadUnread()
  notifTimer = setInterval(loadUnread, 60000)
  window.addEventListener('keydown', onGlobalKeydown)
})

onBeforeUnmount(() => {
  if (notifTimer) clearInterval(notifTimer)
  window.removeEventListener('keydown', onGlobalKeydown)
})

// 路由跳转后刷新未读数（关键路由：抢单池 / 我的工单 / 工单详情）
watch(() => router.currentRoute.value.fullPath, () => { loadUnread() })

// ── 通知 ──
const unreadCount = ref(0)
const notifications = ref([])

const loadUnread = async () => {
  try {
    const n = await getUnreadCount()
    unreadCount.value = (n && n.count) || 0
  } catch { /* ignore */ }
}

const loadNotifications = async () => {
  try {
    const list = await getNotifications(20)
    notifications.value = Array.isArray(list) ? list : []
  } catch { /* ignore */ }
}

const onNotifPanelShow = () => {
  loadNotifications()
  loadUnread()
}

// 类型 → 醒目直达 chip（颜色用状态色，点击走 n.link 深链）
const NOTIF_CHIP_MAP = {
  repair_new_unassigned: { label: '去指派', cls: 'chip-pending' },
  repair_new_pending: { label: '待接单', cls: 'chip-pending' },
  repair_reserve: { label: '去接单', cls: 'chip-reserved' },
  repair_assign: { label: '去处理', cls: 'chip-processing' },
  repair_transfer: { label: '去处理', cls: 'chip-processing' },
  repair_reserve_assign: { label: '去处理', cls: 'chip-confirming' },
  repair_confirm: { label: '去确认', cls: 'chip-confirming' },
  repair_archived: { label: '去查看', cls: 'chip-archived' },
}
const notifChip = (n) => NOTIF_CHIP_MAP[n.type] || null

const openNotif = async (n) => {
  if (!n.read) {
    try {
      await markNotificationRead({ id: n.id })
      n.read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch { /* ignore */ }
  }
  if (n.link) router.push(n.link)
}

const readAll = async () => {
  try {
    await markNotificationRead({ all: true })
    notifications.value = notifications.value.map((n) => ({ ...n, read: true }))
    unreadCount.value = 0
  } catch { /* ignore */ }
}

const formatTime = (t) => {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return String(t || '')
  const pad = (x) => String(x).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// ── 全局搜索 (Ctrl+K) ──
const searchIndex = [
  { label: '系统概览', path: '/dashboard', access: 'dashboard' },
  { label: '我的待办', path: '/todos', access: null },
  { label: '个人中心', path: '/profile', access: null },
  { label: '需求单管理', path: '/leads', access: 'leads' },
  { label: '一键报修', path: '/after_sales/repair-apply', access: 'after_sales/repair-apply' },
  { label: '我的报修 / 工单', path: '/after_sales/my-repairs', access: 'after_sales/my-repairs' },
  { label: '所有工单', path: '/after_sales/all-tasks', access: 'after_sales/all-tasks' },
  { label: '工程师排期', path: '/after_sales/schedule', access: 'after_sales/schedule' },
  { label: '投诉建议管理', path: '/after_sales/complaints', access: 'after_sales/complaints' },
  { label: '联系我们配置', path: '/miniapp/contact', access: 'miniapp/contact' },
  { label: '知识库管理', path: '/miniapp/knowledge', access: 'miniapp/knowledge' },
  { label: '产品中心', path: '/products', access: 'products' },
  { label: '新闻中心', path: '/news', access: 'news' },
  { label: '荣誉与相册', path: '/honors', access: 'honors' },
  { label: '合作伙伴与案例', path: '/cases', access: 'cases' },
  { label: '全局配置', path: '/global-config', access: 'global-config' },
  { label: '共享文件', path: '/finance/files', access: 'finance/files' },
  { label: '资产管理', path: '/finance/assets', access: 'finance/assets' },
  { label: '车辆管理', path: '/finance/vehicles', access: 'finance/vehicles' },
  { label: '成员管理', path: '/system/users', access: 'system/users' },
  { label: '权限分配', path: '/system/roles', access: 'system/roles' },
  { label: '操作日志', path: '/system/logs', access: 'system/logs' },
  { label: '数据字典', path: '/system/dict', access: 'system/dict' },
  { label: '部门管理', path: '/system/depts', access: 'system/depts' },
  { label: '系统设置', path: '/system/settings', access: 'system/settings' },
  { label: '回收站', path: '/system/recycle', access: 'system/recycle' },
  { label: '数据报表', path: '/reports', access: 'reports' },
]

const searchVisible = ref(false)
const searchKeyword = ref('')
const activeIndex = ref(0)
const searchInputRef = ref(null)

const filteredResults = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase()
  return searchIndex
    .filter((item) => !item.access || canAccess(item.access))
    .filter((item) => !kw || item.label.toLowerCase().includes(kw) || item.path.toLowerCase().includes(kw))
})

watch(searchKeyword, () => { activeIndex.value = 0 })

const openSearch = () => {
  searchKeyword.value = ''
  activeIndex.value = 0
  searchVisible.value = true
  nextTick(() => searchInputRef.value?.focus())
}

const moveActive = (delta) => {
  const len = filteredResults.value.length
  if (!len) return
  activeIndex.value = (activeIndex.value + delta + len) % len
}

const chooseActive = () => {
  const item = filteredResults.value[activeIndex.value]
  if (item) selectResult(item)
}

const selectResult = (item) => {
  searchVisible.value = false
  searchKeyword.value = ''
  if (item.path && item.path !== router.currentRoute.value.path) {
    router.push(item.path)
  }
}

const onSearchKeydown = (e) => {
  if (e.key === 'ArrowDown') { e.preventDefault(); moveActive(1) }
  else if (e.key === 'ArrowUp') { e.preventDefault(); moveActive(-1) }
  else if (e.key === 'Enter') { e.preventDefault(); chooseActive() }
  else if (e.key === 'Escape') { searchVisible.value = false }
}

const onGlobalKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
    e.preventDefault()
    openSearch()
  }
}

const pwdDialogVisible = ref(false)
const pwdForm = reactive({ oldPassword: '', newPassword: '', confirm: '' })

const goProfile = () => {
  router.push('/profile')
}

const openChangePwd = () => {
  pwdForm.oldPassword = ''
  pwdForm.newPassword = ''
  pwdForm.confirm = ''
  pwdDialogVisible.value = true
}

const submitChangePwd = async () => {
  if (!pwdForm.oldPassword || !pwdForm.newPassword) {
    ElMessage.warning('请填写旧密码与新密码')
    return
  }
  if (pwdForm.newPassword.length < 6) {
    ElMessage.warning('新密码长度至少6位')
    return
  }
  if (pwdForm.newPassword !== pwdForm.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  try {
    await changePassword({ oldPassword: pwdForm.oldPassword, newPassword: pwdForm.newPassword })
    ElMessage.success('密码修改成功，请重新登录')
    pwdDialogVisible.value = false
    clearAuth()
    router.push('/login')
  } catch { /* ignore */ }
}

const handleLogout = async () => {
  try {
    await apiLogout()
  } catch { /* ignore */ }
  clearAuth()
  router.push('/login')
}
</script>

<style scoped>
/* ═══ 布局容器 ═══ */
.layout-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* ═══ 侧边栏 ═══ */
.layout-aside {
  background-color: var(--sidebar-bg);
  transition: width var(--transition-base);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo-box {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: 0 var(--space-lg);
  background: rgba(0, 0, 0, 0.15);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-accent);
  color: #fff;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.logo-text {
  color: var(--text-inverse);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  white-space: nowrap;
  letter-spacing: 0.02em;
}

/* ═══ 菜单 ═══ */
.sidebar-menu {
  border-right: none !important;
  background-color: transparent !important;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  color: var(--sidebar-text);
  transition: all var(--transition-fast);
  margin: 2px 8px;
  border-radius: var(--radius-md);
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: var(--sidebar-item-hover) !important;
  color: var(--sidebar-text-active);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--sidebar-item-active) !important;
  color: var(--sidebar-text-active) !important;
  font-weight: var(--font-semibold);
}

.sidebar-menu :deep(.el-sub-menu .el-menu) {
  background-color: rgba(0, 0, 0, 0.12) !important;
}

.sidebar-menu :deep(.el-sub-menu .el-menu .el-menu-item) {
  padding-left: 56px !important;
}

/* 侧边栏滚动条暗色适配 */
.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}
.sidebar-menu::-webkit-scrollbar-track {
  background: transparent;
}
.sidebar-menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 3px;
}
.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* ═══ 头部 ═══ */
.main-header {
  height: var(--header-height);
  background: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
  box-shadow: var(--shadow-xs);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.collapse-btn {
  font-size: 18px;
  color: var(--text-secondary);
  padding: 6px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

/* ═══ 全局搜索 ═══ */
.search-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  background: var(--bg-muted);
  transition: all var(--transition-fast);
}

.search-trigger:hover {
  color: var(--text-primary);
  border-color: var(--color-accent);
}

.search-kbd {
  font-size: var(--text-xs);
  color: var(--text-muted);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 1px 6px;
}

.global-search-dialog :deep(.el-dialog__header) {
  padding: 16px 20px 8px;
  margin-right: 0;
}

.search-dialog-head {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.search-esc-hint {
  margin-left: auto;
  font-size: var(--text-xs);
  font-weight: var(--font-normal);
  color: var(--text-muted);
}

.global-search-dialog :deep(.el-dialog__body) {
  padding: 12px 20px 20px;
}

.search-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-results {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 320px;
  overflow-y: auto;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--text-sm);
  color: var(--text-primary);
  transition: background var(--transition-fast);
}

.search-item.active {
  background: var(--color-info-bg);
}

.search-item-icon {
  color: var(--text-muted);
}

.search-item-label {
  flex: 1;
}

.search-item-path {
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.search-empty {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--text-sm);
  padding: var(--space-xl) 0;
}

/* ═══ 通知铃铛 ═══ */
.bell-wrap {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.bell-btn {
  font-size: 18px;
  color: var(--text-secondary);
  padding: 6px;
}

.bell-btn:hover {
  color: var(--text-primary);
}

.notif-panel {
  display: flex;
  flex-direction: column;
}

.notif-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-color-light);
  margin-bottom: var(--space-sm);
}

.notif-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.notif-list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 360px;
  overflow-y: auto;
}

.notif-item {
  display: flex;
  gap: var(--space-sm);
  align-items: flex-start;
  padding: var(--space-md) var(--space-sm);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.notif-item:hover {
  background: var(--bg-muted);
}

.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #DC2626;
  margin-top: 6px;
  flex-shrink: 0;
}

.notif-item:not(.unread) .notif-dot {
  background: #CBD5E1;
}

.notif-body {
  flex: 1;
  min-width: 0;
}

.notif-msg {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
  line-height: 1.5;
}

.notif-item:not(.unread) .notif-msg {
  color: var(--text-muted);
  font-weight: var(--font-normal);
}

.notif-time {
  display: inline-block;
  margin-top: 4px;
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.notif-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  transition: opacity var(--transition-fast);
  &:hover { opacity: 0.8; }

  &.chip-pending    { background: #FFF3E8; color: #FF7D00; }
  &.chip-reserved   { background: #FFF3E8; color: #FF7D00; }
  &.chip-processing { background: #E8F3FF; color: #165DFF; }
  &.chip-confirming { background: #F3E8FF; color: #722ED1; }
  &.chip-archived   { background: #F2F3F5; color: #86909C; }
}

.notif-empty {
  text-align: center;
  padding: var(--space-xl) 0;
  color: var(--text-muted);
}

.notif-empty p {
  margin-top: var(--space-sm);
  font-size: var(--text-sm);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.user-info:hover {
  background: var(--bg-muted);
}

.user-avatar {
  background: var(--color-accent);
  color: #fff;
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
}

.user-name {
  font-size: var(--text-base);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.arrow-icon {
  font-size: var(--text-xs);
  color: var(--text-muted);
  transition: transform var(--transition-fast);
}

/* ═══ 内容区 ═══ */
.main-body {
  background-color: var(--bg-page);
  padding: var(--space-xl);
  overflow-y: auto;
  height: calc(100vh - var(--header-height));
}
</style>
