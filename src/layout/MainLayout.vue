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
          <el-menu-item index="/after_sales/contact" v-if="canAccess('after_sales/contact')">
            <el-icon><Location /></el-icon>
            <span>联系我们配置</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/products" v-if="canAccess('products')">
          <el-icon><Printer /></el-icon>
          <template #title>产品中心</template>
        </el-menu-item>

        <el-menu-item index="/news" v-if="canAccess('news')">
          <el-icon><ChatLineRound /></el-icon>
          <template #title>新闻中心</template>
        </el-menu-item>

        <el-menu-item index="/honors" v-if="canAccess('honors')">
          <el-icon><Medal /></el-icon>
          <template #title>荣誉与相册</template>
        </el-menu-item>

        <el-menu-item index="/cases" v-if="canAccess('cases')">
          <el-icon><Suitcase /></el-icon>
          <template #title>合作伙伴与案例</template>
        </el-menu-item>

        <el-menu-item index="/global-config" v-if="canAccess('global-config')">
          <el-icon><Setting /></el-icon>
          <template #title>门户全局配置</template>
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
                <el-dropdown-item divided @click="openChangePwd">
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
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  DataBoard, Setting, Printer, ChatLineRound, Medal,
  Suitcase, UserFilled, Management, User, Lock, DocumentCopy,
  Expand, Fold, ArrowDown, Service, EditPen, List, Files,
  Calendar, ChatDotSquare, Location, Platform, Clock, SwitchButton,
  Wallet, Folder, Cpu
} from '@element-plus/icons-vue'
import { clearAuth, getUserInfo } from '@/utils/auth'
import { logout as apiLogout, changePassword } from '@/api/modules/auth'

const isCollapse = ref(false)
const router = useRouter()

const currentUser = computed(() => {
  return getUserInfo() || { realName: '管理员' }
})

// ── 角色菜单权限 ──
// 根据 userType/role 返回用户能访问的菜单路径前缀集合
const menuPermissions = computed(() => {
  const info = getUserInfo()
  if (!info) return new Set()
  const ut = info.userType || ''
  const role = info.role || ''

  // 管理员 可见全部
  if (ut === 'admin' || role === '管理员') {
    return new Set(['all'])
  }

  // 内部员工 可见除系统管理外的所有模块
  if (ut === 'internal' || role === '内部员工') {
    return new Set([
      'all-non-system',  // 全部非系统管理板块
      'dashboard', 'leads',
      'after_sales',
      'products', 'news', 'honors', 'cases', 'global-config',
      'finance',
    ])
  }

  // 工程师 仅售后报修相关
  if (ut === 'engineer' || role === '工程师') {
    return new Set([
      'dashboard',
      'after_sales',
    ])
  }

  // 外部人员 最受限
  if (ut === 'normal' || role === '外部人员') {
    return new Set([
      'dashboard',
      'after_sales/repair-apply',
      'after_sales/my-repairs',
      'after_sales/contact',
    ])
  }

  // fallback 最受限
  return new Set(['dashboard'])
})

const canAccess = (path) => {
  const perms = menuPermissions.value
  if (perms.has('all')) return true
  if (perms.has('all-non-system') && !path.startsWith('system')) return true
  if (perms.has(path)) return true
  // check if any prefix matches
  for (const p of perms) {
    if (p.endsWith('/') && path.startsWith(p)) return true
  }
  // 售后模块批量匹配
  if (perms.has('after_sales') && path.startsWith('after_sales')) return true
  return false
}

const pwdDialogVisible = ref(false)
const pwdForm = reactive({ oldPassword: '', newPassword: '', confirm: '' })

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
