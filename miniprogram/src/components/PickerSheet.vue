<!--
  通用底部选择器（单列）— 替代小程序 <picker mode="selector">
  props: modelValue(是否显示) / title(标题) / options([{label, value, sub?}]) / value(当前选中值)
  emits: update:modelValue / select(选中 value)
-->
<template>
  <view v-if="modelValue" class="ps-overlay" @click="close">
    <view class="ps-card" @click.stop>
      <view class="ps-head">
        <text class="ps-title">{{ title }}</text>
        <view class="ps-close" @click="close">
          <SvgIcon name="x" :size="18" color="#86909C" />
        </view>
      </view>

      <scroll-view scroll-y class="ps-list">
        <view
          v-for="opt in options"
          :key="opt.value"
          class="ps-item"
          :class="{ active: value === opt.value, disabled: opt.disabled }"
          @click="select(opt)"
        >
          <view class="ps-item-main">
            <text class="ps-item-label">{{ opt.label }}</text>
            <text v-if="opt.sub" class="ps-item-sub">{{ opt.sub }}</text>
          </view>
          <SvgIcon v-if="value === opt.value" name="check" :size="18" color="#165DFF" />
        </view>
        <view v-if="!options.length" class="ps-empty">
          <text>暂无选项</text>
        </view>
      </scroll-view>

      <view class="ps-safe" />
    </view>
  </view>
</template>

<script setup>
import SvgIcon from './SvgIcon.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  value: { type: [String, Number], default: '' }
})

const emit = defineEmits(['update:modelValue', 'select'])

const close = () => emit('update:modelValue', false)
const select = (opt) => {
  if (opt.disabled) return
  emit('select', opt.value)
  emit('update:modelValue', false)
}
</script>

<style lang="scss" scoped>
.ps-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}
.ps-card {
  width: 100%;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  overflow: hidden;
  animation: ps-in 0.22s ease;
}
@keyframes ps-in {
  from { transform: translateY(40%); opacity: 0.6; }
  to { transform: translateY(0); opacity: 1; }
}

.ps-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx 32rpx 20rpx;
  border-bottom: 1rpx solid #F2F3F5;
}
.ps-title { font-size: 32rpx; font-weight: 700; color: #1D2129; }
.ps-close {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F2F3F5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ps-list { max-height: 60vh; }
.ps-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 32rpx;
  border-bottom: 1rpx solid #F7F8FA;
  &:active { background: #F7F8FA; }
  &.active { background: #F0F6FF; }
  &.disabled {
    pointer-events: none;
    .ps-item-label { color: #C9CDD4; }
    .ps-item-sub { color: #C9CDD4; }
  }
}
.ps-item-main { flex: 1; min-width: 0; margin-right: 16rpx; }
.ps-item-label { font-size: 30rpx; color: #1D2129; }
.ps-item.active .ps-item-label { color: #165DFF; font-weight: 600; }
.ps-item-sub { display: block; font-size: 24rpx; color: #86909C; margin-top: 4rpx; }

.ps-empty {
  padding: 80rpx 0;
  text-align: center;
  font-size: 26rpx;
  color: #86909C;
}

.ps-safe { height: env(safe-area-inset-bottom); }
</style>
