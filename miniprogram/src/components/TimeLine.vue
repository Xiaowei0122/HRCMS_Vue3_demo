<!--  时间轴组件 v2 — 企业级设计  -->
<template>
  <view class="timeline">
    <view
      v-for="(item, index) in items"
      :key="index"
      class="tl-node"
      :class="{ 'tl-done': item.status === 'done' || index < currentActive,
                'tl-active': index === currentActive,
                'tl-waiting': index > currentActive }"
    >
      <view class="tl-line-col">
        <view class="tl-dot" :class="dotClass(index)">
          <SvgIcon v-if="index < currentActive" name="check" :size="10" color="#fff" />
        </view>
        <view
          v-if="index < items.length - 1"
          class="tl-line"
          :class="{ 'line-done': index < currentActive }"
        />
      </view>
      <view class="tl-content">
        <text class="tl-time">{{ formatTime(item.time) }}</text>
        <text class="tl-text">{{ item.node || item.content }}</text>
        <text class="tl-desc" v-if="item.remark">{{ item.remark }}</text>
      </view>
    </view>
    <view v-if="!items || items.length === 0" class="tl-empty">
      <text class="empty-text">暂无进度记录</text>
    </view>
  </view>
</template>

<script setup>
import SvgIcon from './SvgIcon.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  currentActive: { type: Number, default: 0 }
})

const dotClass = (i) => {
  if (i < props.currentActive) return 'dot-done'
  if (i === props.currentActive) return 'dot-active'
  return 'dot-waiting'
}

const formatTime = (t) => {
  if (!t) return ''
  const raw = String(t).trim()
  // 纯时间 "HH:MM"（历史数据）：仅显示时间
  if (/^\d{1,2}:\d{2}$/.test(raw)) return raw
  // 完整日期时间 "YYYY-MM-DD HH:MM[:SS]"：显示 年月日 时:分（不依赖 new Date，避免 NaN/兼容问题）
  const m = raw.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{1,2}):(\d{2})/)
  if (m) return `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}`
  // 兜底：其它格式原样返回
  return raw
}
</script>

<style lang="scss" scoped>
.timeline { padding: 4px 0; }

.tl-node { display: flex; min-height: 40px; }

.tl-line-col {
  width: 24px; display: flex; flex-direction: column; align-items: center; flex-shrink: 0;
}

.tl-dot {
  width: 16px; height: 16px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.3s ease; z-index: 1;

  &.dot-done {
    background: #16A34A;
    box-shadow: 0 0 0 3px rgba(22,163,74,0.15);
  }
  &.dot-active {
    background: #0F172A;
    box-shadow: 0 0 0 3px rgba(15,23,42,0.15);
    animation: dot-pulse 2s infinite;
  }
  &.dot-waiting { background: #CBD5E1; }
}

.tl-line {
  width: 2px; flex: 1; min-height: 24px;
  background: #E2E8F0; transition: background 0.5s ease;

  &.line-done { background: #16A34A; }
}

.tl-content {
  flex: 1; padding-left: 14px; padding-bottom: 18px;
  animation: fade-in-left 0.35s ease;
}

.tl-time { font-size: 11px; color: #94A3B8; display: block; margin-bottom: 2px; }
.tl-text { font-size: 13px; color: #334155; font-weight: 500; display: block; }
.tl-desc { font-size: 12px; color: #64748B; margin-top: 2px; display: block; }

.tl-empty { text-align: center; padding: 20px 0; }
.empty-text { font-size: 13px; color: #CBD5E1; }

@keyframes dot-pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(15,23,42,0.15); }
  50%      { box-shadow: 0 0 0 8px rgba(15,23,42,0.06); }
}
@keyframes fade-in-left {
  from { opacity: 0; transform: translateX(-10px); }
  to   { opacity: 1; transform: translateX(0); }
}
</style>
