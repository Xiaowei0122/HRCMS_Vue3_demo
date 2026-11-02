<!--
  技术知识库 — 文章列表（GET /public/knowledge，免登录）
  分类Tab + 搜索 + 热门搜索 + 文章卡片
-->
<template>
  <view class="page">
    <PageNavbar title="技术知识库" />

    <!-- 搜索栏（渐变蓝延展） -->
    <view class="search-header">
      <view class="search-box">
        <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          v-model="keywordInput"
          type="text"
          placeholder="搜索文章，如：打印机驱动、网络故障..."
          confirm-type="search"
          @confirm="doSearch"
        />
        <button class="search-btn" @click="doSearch">搜索</button>
      </view>
    </view>

    <!-- 分类Tab（「全部」固定左侧 + 分类可滑动） -->
    <view class="category-tabs">
      <view
        class="category-tab category-tab-all"
        :class="{ active: activeCategory === '' }"
        @click="activeCategory = ''"
      >
        <text>全部</text>
        <text v-if="totalCount > 0" class="count">{{ totalCount }}</text>
      </view>
      <view class="tab-divider"></view>
      <view class="tab-scroll">
        <view
          v-for="c in categoryTabs"
          :key="c.value"
          class="category-tab"
          :class="{ active: activeCategory === c.value }"
          @click="activeCategory = c.value"
        >
          <text>{{ c.label }}</text>
          <text v-if="c.count > 0" class="count">{{ c.count }}</text>
        </view>
      </view>
    </view>

    <scroll-view
      scroll-y
      class="scroll-body"
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <view v-if="loading" class="loading-box">
        <text class="loading-text">加载中...</text>
      </view>

      <template v-else>
        <!-- 热门搜索 -->
        <view v-if="!searchKeyword" class="hot-search">
          <view class="hot-search-title">
            <svg viewBox="0 0 24 24"><path d="M12 2c1 3 3 5 3 8a3 3 0 0 1-6 0c0-3 2-5 3-8z"/><path d="M5 12a7 7 0 0 0 14 0"/><path d="M12 19v3"/></svg>
            热门搜索
          </view>
          <view class="hot-search-tags">
            <text
              v-for="(t, i) in hotTags"
              :key="t"
              class="hot-search-tag"
              :class="{ hot: i < 2 }"
              @click="applyHotTag(t)"
            >{{ t }}</text>
          </view>
        </view>

        <!-- 文章列表 -->
        <view v-if="filteredArticles.length" class="article-list">
          <view v-for="a in filteredArticles" :key="a.id" class="article-card" @click="openArticle(a)">
            <view class="article-thumb" :class="a.style">
              <img v-if="a.cover" :src="a.cover" class="thumb-img" />
              <template v-else>
              <!-- 驱动安装 -->
              <svg v-if="a.style === 'printer'" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
              <!-- 故障案例 -->
              <svg v-else-if="a.style === 'case'" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              <!-- 系统维护 -->
              <svg v-else-if="a.style === 'system'" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
              <!-- 网络运维 -->
              <svg v-else-if="a.style === 'network'" viewBox="0 0 24 24"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>
              <!-- 监控安防 -->
              <svg v-else-if="a.style === 'camera'" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
              <svg v-else viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
              </template>
            </view>
            <view class="article-content">
              <view class="article-main">
                <text class="article-title">{{ a.title }}</text>
                <text v-if="a.desc" class="article-desc">{{ a.desc }}</text>
              </view>
              <view class="article-meta">
                <text class="article-tag" :class="a.tagClass">{{ a.tag }}</text>
                <text v-if="a.pinned" class="article-pin">置顶</text>
                <text class="article-views">
                  <svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  {{ a.views }}
                </text>
              </view>
            </view>
          </view>
        </view>

        <EmptyState v-else icon="info" text="未找到相关文章" sub-text="换个关键词或分类试试" />
      </template>

      <view class="safe-bottom" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRepairStore } from '@/stores/repair'
import PageNavbar from '@/components/PageNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'
import { CATEGORIES, articleStyle, tagClassFor, formatViews } from '@/utils/knowledge'

const router = useRouter()
const repairStore = useRepairStore()

const loading = ref(true)
const refreshing = ref(false)
const allArticles = ref([])
const activeCategory = ref('')
const keywordInput = ref('')
const searchKeyword = ref('')

const hotTags = ['打印机驱动安装', '统信UOS教程', '电脑蓝屏', '网络不通', 'POE摄像头', '门禁离线']

const totalCount = computed(() => allArticles.value.length)
const categoryTabs = computed(() =>
  CATEGORIES.map((c) => ({
    label: c,
    value: c,
    count: allArticles.value.filter((a) => a.typeLabel === c).length
  }))
)

const filteredArticles = computed(() => {
  let list = allArticles.value
  if (activeCategory.value) list = list.filter((a) => a.typeLabel === activeCategory.value)
  const kw = searchKeyword.value.trim()
  if (kw) {
    const lower = kw.toLowerCase()
    list = list.filter((a) => `${a.title} ${a.desc || ''}`.toLowerCase().includes(lower))
  }
  return list
})

const loadList = async () => {
  try {
    const data = await repairStore.fetchKnowledge({ page: 1, size: 1000 })
    const records = Array.isArray(data) ? data : (data?.records || [])
    allArticles.value = records.map((n) => {
      const style = articleStyle(n)
      return {
        id: n.id,
        style,
        typeLabel: n.type || '',
        tag: n.type || '技术知识',
        tagClass: tagClassFor(style),
        title: n.title,
        desc: n.summary || '',
        views: formatViews(n.views),
        pinned: !!n.isPinned,
        cover: n.cover || ''
      }
    })
  } catch {
    allArticles.value = []
  }
}

const doSearch = () => {
  searchKeyword.value = keywordInput.value
}
const applyHotTag = (t) => {
  keywordInput.value = t
  searchKeyword.value = t
}

const onRefresh = async () => {
  refreshing.value = true
  await loadList()
  refreshing.value = false
}

const openArticle = (a) => router.push(`/pages/knowledge-detail/index?id=${a.id}`)

onMounted(async () => {
  await loadList()
  loading.value = false
})
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
}

/* ── 搜索栏（渐变蓝延展） ── */
.search-header {
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%);
  padding: 0 32rpx 32rpx;
  flex-shrink: 0;
}
.search-box {
  height: 84rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 42rpx;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
  gap: 16rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}
.search-box svg {
  width: 36rpx;
  height: 36rpx;
  stroke: #86909C;
  stroke-width: 2;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
  flex-shrink: 0;
}
.search-box input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 28rpx;
  color: #1D2129;
}
.search-box input::placeholder { color: #C9CDD4; }
.search-btn {
  padding: 10rpx 28rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 26rpx;
  font-weight: 500;
  border-radius: 28rpx;
  border: none;
  line-height: 1.4;
  flex-shrink: 0;
}

/* ── 分类Tab（「全部」固定 + 分段可滑动） ── */
.category-tabs {
  background: #fff;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding: 20rpx 24rpx 24rpx;
  overflow: hidden;
}
.category-tab-all {
  flex-shrink: 0;
}
.tab-divider {
  width: 1rpx;
  height: 40rpx;
  background: #E5E6EB;
  margin: 0 20rpx;
  flex-shrink: 0;
}
.tab-scroll {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 16rpx;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
}
.tab-scroll::-webkit-scrollbar { display: none; }
.category-tab {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 14rpx 28rpx;
  font-size: 26rpx;
  color: #4E5969;
  font-weight: 500;
  white-space: nowrap;
  background: #F7F8FA;
  border-radius: 32rpx;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.category-tab.active {
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 6rpx 16rpx rgba(22, 93, 255, 0.25);
}
.category-tab .count {
  font-size: 22rpx;
  background: rgba(0, 0, 0, 0.05);
  color: #86909C;
  padding: 2rpx 12rpx;
  border-radius: 16rpx;
  font-weight: 500;
  line-height: 1.4;
}
.category-tab.active .count {
  background: rgba(255, 255, 255, 0.28);
  color: #fff;
}

/* ── 热门搜索 ── */
.hot-search {
  margin: 24rpx 32rpx;
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx 32rpx;
}
.hot-search-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #1D2129;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.hot-search-title svg {
  width: 32rpx;
  height: 32rpx;
  fill: #FF7D00;
  stroke: none;
}
.hot-search-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.hot-search-tag {
  padding: 12rpx 24rpx;
  background: #F7F8FA;
  border-radius: 28rpx;
  font-size: 24rpx;
  color: #4E5969;
}
.hot-search-tag.hot {
  background: #FFF3E8;
  color: #FF7D00;
}

/* ── 文章列表 ── */
.scroll-body { flex: 1; }
.loading-box {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}
.loading-text { font-size: 28rpx; color: #86909C; }

.article-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 8rpx 32rpx 20rpx;
}
.article-card {
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx;
  display: flex;
  gap: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
}
.article-thumb {
  width: 192rpx;
  height: 192rpx;
  border-radius: 20rpx;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;

  &.printer { background: linear-gradient(135deg, #E8F3FF, #BEDAFF); }
  &.case    { background: linear-gradient(135deg, #FFF3E8, #FFD8A8); }
  &.system  { background: linear-gradient(135deg, #E8FFEA, #A8E6B0); }
  &.network { background: linear-gradient(135deg, #F0E8FF, #D4BFFF); }
  &.camera  { background: linear-gradient(135deg, #FFE8E8, #FFC8C8); }
}
.thumb-img { width: 100%; height: 100%; object-fit: cover; border-radius: 20rpx; }

.article-thumb svg {
  width: 84rpx;
  height: 84rpx;
  stroke-width: 1.5;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.article-thumb.printer svg { stroke: #165DFF; }
.article-thumb.case svg    { stroke: #FF7D00; }
.article-thumb.system svg  { stroke: #00B42A; }
.article-thumb.network svg { stroke: #722ED1; }
.article-thumb.camera svg  { stroke: #F53F3F; }

.article-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}
.article-main { display: flex; flex-direction: column; }
.article-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1D2129;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.article-desc {
  font-size: 24rpx;
  color: #86909C;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 8rpx;
}
.article-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 16rpx;
  flex-wrap: wrap;
}
.article-tag {
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  font-weight: 500;
}
.tag-tutorial { background: #E8F3FF; color: #165DFF; }
.tag-case     { background: #FFF3E8; color: #FF7D00; }
.tag-guide    { background: #E8FFEA; color: #00B42A; }
.tag-network  { background: #F0E8FF; color: #722ED1; }
.tag-camera   { background: #FFE8E8; color: #F53F3F; }
.article-pin {
  font-size: 20rpx;
  color: #FF7D00;
  background: #FFF3E8;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-weight: 500;
}
.article-views {
  margin-left: auto;
  font-size: 22rpx;
  color: #C9CDD4;
  display: flex;
  align-items: center;
  gap: 6rpx;
}
.article-views svg {
  width: 24rpx;
  height: 24rpx;
  stroke: #C9CDD4;
  fill: none;
  stroke-width: 2;
}

.safe-bottom { height: 40rpx; }
</style>
