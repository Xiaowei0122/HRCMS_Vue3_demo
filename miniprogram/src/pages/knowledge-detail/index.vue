<!--
  知识详情 — 技术知识库文章详情（GET /public/knowledge/{id}，免登录）
  富文本正文 + 相关推荐 + 点赞/收藏/联系客服
-->
<template>
  <view class="page">
    <PageNavbar title="知识详情">
      <template #right>
        <view class="nav-share" @click="onShare">
          <svg viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
        </view>
      </template>
    </PageNavbar>

    <scroll-view scroll-y class="scroll-body">
      <view v-if="loading" class="loading-box">
        <text class="loading-text">加载中...</text>
      </view>

      <template v-else-if="article">
        <view class="detail-article">
          <text class="detail-title">{{ article.title }}</text>

          <view class="detail-meta">
            <text v-if="article.type" class="detail-tag">{{ article.type }}</text>
            <text v-if="article.date" class="detail-date">{{ article.date }}</text>
            <text class="detail-views">
              <svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              {{ article.views }} 次阅读
            </text>
            <view v-if="article.author" class="detail-author">
              <text class="detail-author-avatar">{{ authorInitial }}</text>
              <text>{{ article.author }}整理</text>
            </view>
          </view>

          <image v-if="article.cover" :src="article.cover" class="article-cover" mode="widthFix" />

          <view class="detail-body" v-html="article.content"></view>

          <!-- 相关推荐 -->
          <view v-if="related.length" class="detail-related">
            <view class="detail-related-title">相关推荐</view>
            <view v-for="r in related" :key="r.id" class="related-item" @click="goRelated(r.id)">
              <view class="related-item-icon" :class="r.style">
                <svg v-if="r.style === 'printer'" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
                <svg v-else-if="r.style === 'case'" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/></svg>
                <svg v-else-if="r.style === 'system'" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/></svg>
                <svg v-else-if="r.style === 'network'" viewBox="0 0 24 24"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/></svg>
                <svg v-else-if="r.style === 'camera'" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                <svg v-else viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/></svg>
              </view>
              <text class="related-item-text">{{ r.title }}</text>
              <svg class="related-item-arrow" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
            </view>
          </view>
        </view>
      </template>

      <EmptyState v-else icon="info" text="文章不存在或已下架" sub-text="请返回知识库查看其他内容" />

      <view class="safe-bottom" />
    </scroll-view>

    <!-- 底部操作栏 -->
    <view v-if="article" class="bottom-bar">
      <view class="action like" :class="{ active: liked }" @click="toggleLike">
        <svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
        <text class="action-label">点赞</text>
      </view>
      <view class="action fav" :class="{ active: faved }" @click="toggleFav">
        <svg viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        <text class="action-label">收藏</text>
      </view>
      <button class="contact-btn" @click="goContact">
        <svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
        无法解决？点击联系客服
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRepairStore } from '@/stores/repair'
import PageNavbar from '@/components/PageNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'
import { articleStyle } from '@/utils/knowledge'

const route = useRoute()
const router = useRouter()
const repairStore = useRepairStore()

const loading = ref(true)
const article = ref(null)
const related = ref([])
const liked = ref(false)
const faved = ref(false)

const authorInitial = computed(() => (article.value?.author || '鸿').charAt(0))

// ── 点赞 / 收藏（本地持久化，免登录即可用）──
const readIds = (key) => {
  try {
    const v = uni.getStorageSync(key)
    return Array.isArray(v) ? v : []
  } catch {
    return []
  }
}
const toggleId = (key, id) => {
  const set = new Set(readIds(key))
  if (set.has(id)) set.delete(id)
  else set.add(id)
  uni.setStorageSync(key, [...set])
  return set.has(id)
}

const toggleLike = () => {
  if (!article.value) return
  liked.value = toggleId('likedKnowledge', article.value.id)
}
const toggleFav = () => {
  if (!article.value) return
  faved.value = toggleId('favKnowledge', article.value.id)
}

const loadDetail = async (id) => {
  loading.value = true
  try {
    article.value = await repairStore.fetchKnowledgeDetail(id)
    liked.value = readIds('likedKnowledge').includes(id)
    faved.value = readIds('favKnowledge').includes(id)
    loadRelated(article.value?.type, id)
  } catch {
    article.value = null
  } finally {
    loading.value = false
  }
}

const loadRelated = async (type, currentId) => {
  related.value = []
  if (!type) return
  try {
    const data = await repairStore.fetchKnowledge({ page: 1, size: 5, type })
    const records = Array.isArray(data) ? data : (data?.records || [])
    related.value = records
      .filter((r) => r.id !== currentId)
      .slice(0, 3)
      .map((r) => ({ id: r.id, title: r.title, style: articleStyle(r) }))
  } catch {
    related.value = []
  }
}

const goRelated = (id) => router.replace(`/pages/knowledge-detail/index?id=${id}`)
const goContact = () => router.push('/pages/contact/index')

const onShare = () => {
  const url = `${location.origin}${location.pathname}#/pages/knowledge-detail/index?id=${article.value?.id || ''}`
  const done = () => uni.showToast({ title: '链接已复制，快去分享吧', icon: 'none' })
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(done).catch(done)
  } else {
    done()
  }
}

watch(
  () => route.query.id,
  (val) => {
    if (val) loadDetail(val)
  }
)

onMounted(() => {
  const id = route.query.id || route.params.id
  if (id) loadDetail(id)
  else loading.value = false
})
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.nav-share {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-share svg {
  width: 40rpx;
  height: 40rpx;
  stroke: #fff;
  stroke-width: 2;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.scroll-body { flex: 1; }
.loading-box {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}
.loading-text { font-size: 28rpx; color: #86909C; }

.detail-article {
  padding: 40rpx 36rpx 60rpx;
}
.detail-title {
  font-size: 44rpx;
  font-weight: 700;
  color: #1D2129;
  line-height: 1.4;
  display: block;
  margin-bottom: 28rpx;
}
.detail-meta {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 40rpx;
  padding-bottom: 32rpx;
  border-bottom: 1rpx solid #F2F3F5;
  flex-wrap: wrap;
}
.detail-tag {
  padding: 6rpx 20rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
  font-weight: 500;
  background: #E8F3FF;
  color: #165DFF;
}
.detail-date { font-size: 24rpx; color: #86909C; }
.detail-views {
  font-size: 24rpx;
  color: #86909C;
  display: flex;
  align-items: center;
  gap: 6rpx;
}
.detail-views svg {
  width: 26rpx;
  height: 26rpx;
  stroke: #86909C;
  fill: none;
  stroke-width: 2;
}
.detail-author {
  margin-left: auto;
  font-size: 24rpx;
  color: #86909C;
  display: flex;
  align-items: center;
  gap: 8rpx;
}
.detail-author-avatar {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 20rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.article-cover {
  width: 100%;
  display: block;
  border-radius: 16rpx;
  background: #F2F3F5;
  margin-bottom: 32rpx;
}

/* ── 富文本正文 ── */
.detail-body {
  font-size: 30rpx;
  color: #4E5969;
  line-height: 1.8;
  word-break: break-word;

  :deep(p) { margin-bottom: 28rpx; }
  :deep(h1), :deep(h2), :deep(h3), :deep(h4) {
    font-size: 34rpx;
    font-weight: 700;
    color: #1D2129;
    margin: 48rpx 0 24rpx;
    display: flex;
    align-items: center;
    gap: 16rpx;
    line-height: 1.4;
  }
  :deep(h1)::before, :deep(h2)::before, :deep(h3)::before, :deep(h4)::before {
    content: '';
    width: 8rpx;
    height: 36rpx;
    background: linear-gradient(180deg, #165DFF, #4080FF);
    border-radius: 4rpx;
    flex-shrink: 0;
  }
  :deep(ul), :deep(ol) { margin-bottom: 28rpx; padding-left: 40rpx; }
  :deep(li) { margin-bottom: 16rpx; line-height: 1.7; }
  :deep(li::marker) { color: #165DFF; }
  :deep(strong) { color: #1D2129; font-weight: 700; }
  :deep(em) { font-style: normal; color: #F53F3F; }
  :deep(code) {
    background: #F2F3F5;
    padding: 4rpx 12rpx;
    border-radius: 8rpx;
    font-size: 26rpx;
    color: #F53F3F;
    font-family: 'Courier New', monospace;
  }
  :deep(img) { max-width: 100%; border-radius: 16rpx; margin: 16rpx 0; }
  :deep(a) { color: #165DFF; }
  :deep(blockquote) {
    border-left: 6rpx solid #165DFF;
    background: #F7F8FA;
    padding: 20rpx 24rpx;
    margin: 16rpx 0;
    border-radius: 8rpx;
    color: #4E5969;
  }
  // 设计稿中的提示框（如内容里带此类名）
  :deep(.tip-box) {
    background: #E8F3FF;
    border-left: 6rpx solid #165DFF;
    border-radius: 16rpx;
    padding: 24rpx 28rpx;
    margin: 32rpx 0;
    font-size: 26rpx;
    color: #4E5969;
    line-height: 1.6;
  }
  :deep(.tip-box strong) { color: #165DFF; }
  :deep(.warning-box) {
    background: #FFF7E8;
    border-left: 6rpx solid #FF7D00;
    border-radius: 16rpx;
    padding: 24rpx 28rpx;
    margin: 32rpx 0;
    font-size: 26rpx;
    color: #4E5969;
    line-height: 1.6;
  }
  :deep(.warning-box strong) { color: #FF7D00; }
  :deep(.step-num) {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44rpx;
    height: 44rpx;
    background: linear-gradient(135deg, #165DFF, #4080FF);
    color: #fff;
    border-radius: 50%;
    font-size: 24rpx;
    font-weight: 700;
    margin-right: 12rpx;
  }
}

/* ── 相关推荐 ── */
.detail-related {
  margin: 48rpx -36rpx 0;
  padding: 40rpx 36rpx;
  background: #F7F8FA;
}
.detail-related-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1D2129;
  margin-bottom: 28rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.detail-related-title::before {
  content: '';
  width: 8rpx;
  height: 36rpx;
  background: linear-gradient(180deg, #165DFF, #4080FF);
  border-radius: 4rpx;
}
.related-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx 28rpx;
  margin-bottom: 16rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
}
.related-item-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.printer { background: #E8F3FF; }
  &.case    { background: #FFF3E8; }
  &.system  { background: #E8FFEA; }
  &.network { background: #F0E8FF; }
  &.camera  { background: #FFE8E8; }
}
.related-item-icon svg {
  width: 36rpx;
  height: 36rpx;
  stroke-width: 2;
  fill: none;
  stroke-linecap: round;
}
.related-item-icon.printer svg { stroke: #165DFF; }
.related-item-icon.case svg    { stroke: #FF7D00; }
.related-item-icon.system svg  { stroke: #00B42A; }
.related-item-icon.network svg { stroke: #722ED1; }
.related-item-icon.camera svg  { stroke: #F53F3F; }
.related-item-text {
  flex: 1;
  font-size: 26rpx;
  color: #4E5969;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.related-item-arrow {
  width: 28rpx;
  height: 28rpx;
  stroke: #C9CDD4;
  stroke-width: 2;
  fill: none;
  stroke-linecap: round;
  flex-shrink: 0;
}

/* ── 底部操作栏 ── */
.bottom-bar {
  display: flex;
  align-items: center;
  padding: 20rpx 32rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #F2F3F5;
  gap: 24rpx;
  flex-shrink: 0;
}
.action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  flex-shrink: 0;
}
.action svg {
  width: 44rpx;
  height: 44rpx;
  stroke-width: 2;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke: #86909C;
}
.action.like.active svg { stroke: #F53F3F; fill: #F53F3F; }
.action.fav.active svg { stroke: #FF7D00; fill: #FF7D00; }
.action-label { font-size: 20rpx; color: #86909C; }
.action.active .action-label { color: #165DFF; }

.contact-btn {
  flex: 1;
  height: 84rpx;
  border-radius: 42rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 8rpx 24rpx rgba(22, 93, 255, 0.3);
}
.contact-btn svg {
  width: 36rpx;
  height: 36rpx;
  stroke: #fff;
  stroke-width: 2;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.safe-bottom { height: 40rpx; }
</style>
