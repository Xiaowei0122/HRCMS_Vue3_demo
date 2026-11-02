<template>
  <div class="todos-container page-enter">
    <div class="todos-header">
      <div>
        <h2 class="todos-title">我的待办</h2>
        <p class="todos-subtitle">按当前角色聚合最该处理的事项，点击条目一键跳转</p>
      </div>
      <div class="header-actions">
        <el-tag v-if="totalCount" type="warning" effect="dark" round>共 {{ totalCount }} 项</el-tag>
        <el-button :icon="Refresh" @click="loadTodos" :loading="loading">刷新</el-button>
      </div>
    </div>

    <div v-if="groups.length" class="todo-grid">
      <div v-for="g in groups" :key="g.key" class="todo-card card-lift">
        <div class="card-head">
          <div class="card-title-row">
            <span class="card-title">{{ g.title }}</span>
            <el-tag size="small" :type="g.count ? 'danger' : 'info'" effect="light">{{ g.count }}</el-tag>
          </div>
          <p class="card-subtitle">{{ g.subtitle }}</p>
        </div>

        <ul v-if="g.items.length" class="todo-list">
          <li
            v-for="item in g.items"
            :key="item.id"
            class="todo-item"
            @click="go(item.link)"
          >
            <span class="todo-dot"></span>
            <div class="todo-body">
              <span class="todo-text">{{ item.title }}</span>
              <span class="todo-meta">{{ item.subtitle }}</span>
            </div>
            <span class="todo-time">{{ item.time }}</span>
          </li>
        </ul>
        <div v-else class="todo-empty">
          <el-icon :size="32" color="#CBD5E1"><CircleCheck /></el-icon>
          <p>暂无待办</p>
        </div>

        <div class="card-foot" @click="go(g.link)">
          <span>前往处理</span>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <el-empty
      v-else-if="!loading"
      :image-size="180"
      description="当前没有待办事项，去喝杯茶吧 ☕"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh, CircleCheck, ArrowRight } from '@element-plus/icons-vue'
import { getTodos } from '@/api/modules/todos'

const router = useRouter()
const groups = ref([])
const loading = ref(false)

const totalCount = computed(() => groups.value.reduce((s, g) => s + (g.count || 0), 0))

const loadTodos = async () => {
  loading.value = true
  try {
    const res = await getTodos()
    groups.value = (res && res.groups) || []
  } catch {
    // 错误已由拦截器统一处理
  } finally {
    loading.value = false
  }
}

const go = (link) => {
  if (link) router.push(link)
}

onMounted(loadTodos)
</script>

<style scoped>
.todos-container {
  max-width: 1400px;
  margin: 0 auto;
}

.todos-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: var(--space-xl);
}

.todos-title {
  margin: 0;
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.todos-subtitle {
  margin: 6px 0 0;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.todo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--space-xl);
}

.todo-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-card);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  animation: slide-up-fade 0.4s ease-out both;
}

.card-head {
  margin-bottom: var(--space-md);
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.card-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.card-subtitle {
  margin: 4px 0 0;
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.todo-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  max-height: 320px;
  overflow-y: auto;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-sm);
  border-bottom: 1px solid var(--border-color-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.todo-item:hover { background: var(--bg-muted); }

.todo-item:last-child { border-bottom: none; }

.todo-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #DC2626;
  flex-shrink: 0;
}

.todo-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.todo-text {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-meta {
  font-size: var(--text-xs);
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
  flex-shrink: 0;
}

.todo-empty {
  flex: 1;
  text-align: center;
  padding: var(--space-2xl) 0;
  color: var(--text-muted);
}

.todo-empty p {
  margin-top: var(--space-sm);
  font-size: var(--text-sm);
}

.card-foot {
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  font-size: var(--text-sm);
  color: var(--color-accent);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.card-foot:hover { color: var(--color-accent-hover, #0369A1); }
</style>
