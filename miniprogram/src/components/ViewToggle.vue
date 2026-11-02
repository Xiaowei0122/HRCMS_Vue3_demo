<!--
  列表 / 详情 视图切换按钮 — 放在状态筛选 Tab 行最右侧
  props: mode（'list' | 'detail'），点击 emit toggle
  显示「将要切换到的模式」图标：详情模式显示列表图标，列表模式显示详情图标
-->
<template>
  <view class="view-toggle" @click="$emit('toggle')">
    <img :src="targetIcon" class="view-toggle-img" alt="切换视图" />
  </view>
</template>

<script setup>
import { computed } from 'vue'
import listModeImg from '@/img/list-mode.png'
import detailModeImg from '@/img/detail-mode.png'

const props = defineProps({
  mode: { type: String, default: 'detail' }
})

defineEmits(['toggle'])

const targetIcon = computed(() => (props.mode === 'list' ? detailModeImg : listModeImg))
</script>

<style lang="scss" scoped>
.view-toggle {
  flex-shrink: 0;
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  background: #F2F3F5;
  border: 1.5px solid #E5E6EB;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;

  &:active {
    background: #E8F3FF;
    border-color: #165DFF;
  }
}

.view-toggle-img {
  width: 40rpx;
  height: 40rpx;
  display: block;
}
</style>
