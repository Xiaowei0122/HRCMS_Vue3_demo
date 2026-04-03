<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'">
      <div class="logo-box">
        <span v-if="!isCollapse" class="logo-text">鸿瑞办公 CMS</span>
        <span v-else class="logo-text">HR</span>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        class="el-menu-vertical"
        :collapse="isCollapse"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>系统概览</template>
        </el-menu-item>
        
        <el-menu-item index="/leads">
          <el-icon><UserFilled /></el-icon>
          <template #title>需求单管理</template>
        </el-menu-item>

        <!-- 售后报修管理模块 -->
      <el-sub-menu index="after_sales">
        <template #title>
          <el-icon><Service /></el-icon>
          <span>售后报修管理</span>
        </template>

          <!-- 1. 报修管理 (管理/用户通用) -->
          <el-menu-item index="/after_sales/repair-apply">
            <el-icon><EditPen /></el-icon>
            <span>一键报修</span>
          </el-menu-item>

          <el-menu-item index="/after_sales/my-repairs">
            <el-icon><List /></el-icon>
            <span>我的报修 / 工单</span>
          </el-menu-item>

          <!-- 2. 工程师池 (仅工程师/管理组可见) -->
          <el-menu-item index="/after_sales/all-tasks">
            <el-icon><Files /></el-icon>
            <span>所有工单 (抢单池)</span>
          </el-menu-item>

          <!-- 3. 调度与期排 (特定用户组可见) -->
          <el-menu-item index="/after_sales/schedule">
            <el-icon><Calendar /></el-icon>
            <span>工程师期排</span>
          </el-menu-item>

          <!-- 4. 互动反馈 -->
          <el-menu-item index="/after_sales/complaints">
            <el-icon><ChatDotSquare /></el-icon>
            <span>投诉建议管理</span>
          </el-menu-item>

          <!-- 5. 资料库 -->
          <el-menu-item index="/after_sales/contact">
            <el-icon><Location /></el-icon>
            <span>联系我们配置</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/products">
          <el-icon><Printer /></el-icon>
          <template #title>产品中心</template>
        </el-menu-item>

        <el-menu-item index="/news">
          <el-icon><ChatLineRound /></el-icon>
          <template #title>新闻中心</template>
        </el-menu-item>

        <el-menu-item index="/honors">
          <el-icon><Medal /></el-icon>
          <template #title>荣誉与相册</template>
        </el-menu-item>

        <el-menu-item index="/cases">
          <el-icon><Suitcase /></el-icon>
          <template #title>合作伙伴与案例</template>
        </el-menu-item>

         <el-menu-item index="/global-config">
          <el-icon><Setting /></el-icon>
          <template #title>门户全局配置</template>
        </el-menu-item>

        <el-sub-menu index="system">
          <template #title>
            <el-icon><Management /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/users"><el-icon><User /></el-icon>成员管理</el-menu-item>
          <el-menu-item index="/system/roles"><el-icon><Lock /></el-icon>权限分配</el-menu-item>
          <el-menu-item index="/system/logs"><el-icon><DocumentCopy /></el-icon>操作日志</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 右侧主体区 -->
    <el-container direction="vertical">
      <!-- 头部 -->
      <el-header class="main-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Expand v-if="isCollapse" />
            <Fold v-else />
          </el-icon>
          <span class="breadcrumb">{{ $route.meta.title || '后台管理' }}</span>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              管理员 <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 页面内容展示区 -->
      <el-main class="main-body">
        <!-- ⭐ 关键：没有这一行，子页面就不会显示 -->
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  DataBoard, Setting, Printer, ChatLineRound, Medal, 
  Suitcase, UserFilled, Management, User, Lock, DocumentCopy,
  Expand, Fold, ArrowDown
} from '@element-plus/icons-vue'

const isCollapse = ref(false)
const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  router.push('/login')
}
</script>

<style scoped>
.layout-container { height: 100vh; width: 100vw; overflow: hidden; }
.el-aside { background-color: #304156; transition: width 0.3s; }
.el-menu { border-right: none; }

.logo-box {
  height: 60px; line-height: 60px; text-align: center;
  background: #2b2f3a; color: #fff; font-weight: bold; font-size: 18px;
}

.main-header {
  height: 60px; background: #fff; border-bottom: 1px solid #e6e6e6;
  display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
}

.header-left { display: flex; align-items: center; gap: 15px; }
.collapse-btn { font-size: 20px; cursor: pointer; color: #606266; }
.breadcrumb { font-size: 14px; color: #606266; }

.user-info { cursor: pointer; color: #409EFF; }

.main-body { background-color: #f0f2f5; padding: 20px; }

/* 页面切换动画 */
.fade-transform-enter-active, .fade-transform-leave-active {
  transition: all 0.3s;
}
.fade-transform-enter-from { opacity: 0; transform: translateX(-20px); }
.fade-transform-leave-to { opacity: 0; transform: translateX(20px); }
</style>