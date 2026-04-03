<template>
  <el-menu
    :default-active="$route.path"
    class="sidebar-menu"
    router
    :collapse="isCollapse"
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409EFF"
  >
    <!-- 1. 仪表盘 -->
    <el-menu-item index="/dashboard">
      <el-icon><DataBoard /></el-icon>
      <template #title>控制台首页</template>
    </el-menu-item>

    <!-- 2. 门户内容管理 (新整合) -->
    <el-sub-menu index="portal">
      <template #header>
        <el-icon><Monitor /></el-icon>
        <span>门户内容管理</span>
      </template>
      <el-menu-item index="/system/config">
        <el-icon><Setting /></el-icon>
        <span>全局配置 (地图/Logo)</span>
      </el-menu-item>
      <el-menu-item index="/portal/news">
        <el-icon><ChatLineRound /></el-icon>
        <span>新闻动态发布</span>
      </el-menu-item>
      <el-menu-item index="/portal/honors">
        <el-icon><Medal /></el-icon>
        <span>荣誉资质管理</span>
      </el-menu-item>
    </el-sub-menu>

    <!-- 3. 核心业务模块 (产品中心) -->
    <el-sub-menu index="business">
      <template #header>
        <el-icon><Goods /></el-icon>
        <span>核心业务管理</span>
      </template>
      <el-menu-item index="/business/products">
        <el-icon><Printer /></el-icon>
        <span>产品中心 (设备录入)</span>
      </el-menu-item>
      <el-menu-item index="/business/leads">
        <el-icon><UserFilled /></el-icon>
        <span>需求线索跟进</span>
      </el-menu-item>
    </el-sub-menu>

    <!-- 4. 系统权限 -->
    <el-sub-menu index="system">
      <template #header>
        <el-icon><Management /></el-icon>
        <span>系统安全审计</span>
      </template>
      <el-menu-item index="/system/users">成员管理</el-menu-item>
      <el-menu-item index="/system/roles">权限分配</el-menu-item>
      <el-menu-item index="/system/logs">操作日志</el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<script setup>
import { 
  DataBoard, Monitor, Setting, ChatLineRound, 
  Medal, Goods, Printer, UserFilled, Management 
} from '@element-plus/icons-vue'

// 接收父组件传来的折叠状态
defineProps(['isCollapse'])
</script>