<!--
  联系我们 V2 — 透明 Navbar 压公司 hero + 信息卡 + 地图占位 + 工程师团队
-->
<template>
  <view class="page">
    <PageNavbar title="联系我们" transparent />

    <scroll-view scroll-y class="scroll-body">
      <!-- 公司 hero -->
      <view class="company-hero">
        <view class="company-logo"><text>{{ (config.siteName || '鸿瑞').charAt(0) }}</text></view>
        <text class="company-name">{{ config.siteName || '西安鸿瑞办公' }}</text>
        <text class="company-slogan" v-if="config.description">{{ config.description }}</text>
      </view>

      <!-- 公司信息卡（负 margin 叠在 hero 上） -->
      <view class="company-info-card">
        <view class="company-info-item" v-if="config.servicePhone">
          <view class="company-info-icon blue"><SvgIcon name="phone" :size="18" color="#fff" /></view>
          <view class="company-info-text">
            <text class="company-info-label">服务热线</text>
            <text class="company-info-value">{{ config.servicePhone }}</text>
          </view>
        </view>
        <view class="company-info-item" v-if="config.address">
          <view class="company-info-icon green"><SvgIcon name="mapPin" :size="18" color="#fff" /></view>
          <view class="company-info-text">
            <text class="company-info-label">公司地址</text>
            <text class="company-info-value">{{ config.address }}</text>
          </view>
        </view>
        <view class="company-info-item" v-if="config.businessHours">
          <view class="company-info-icon orange"><SvgIcon name="clock" :size="18" color="#fff" /></view>
          <view class="company-info-text">
            <text class="company-info-label">营业时间</text>
            <text class="company-info-value">{{ config.businessHours }}</text>
          </view>
        </view>
      </view>

      <!-- 地图占位 -->
      <view class="map-placeholder" @click="openMap">
        <view class="map-road map-road-1"></view>
        <view class="map-road map-road-2"></view>
        <view class="map-road map-road-3"></view>
        <view class="map-road map-road-4"></view>
        <view class="map-pin-pulse"></view>
        <view class="map-pin"><view class="map-pin-icon"></view></view>
        <view class="map-info-tag" v-if="config.address">
          <SvgIcon name="mapPin" :size="14" color="#165DFF" />
          <text>{{ config.address }}</text>
        </view>
        <view class="map-nav-btn" @click.stop="openMap">
          <SvgIcon name="mapPin" :size="16" color="#fff" />
          <text>导航到公司</text>
        </view>
      </view>

      <!-- 工程师团队 -->
      <view class="engineer-section-title">
        <SvgIcon name="user" :size="18" color="#165DFF" />
        <text class="engineer-section-main">工程师团队</text>
        <view class="engineer-section-divider"></view>
        <text class="engineer-section-slogan">专业认证 · 经验丰富 · 快速响应</text>
      </view>

      <view v-if="engineers.length" class="engineer-list">
        <EngineerCard v-for="(e, i) in engineers" :key="e._id || e.id" :engineer="e" :index="i" />
      </view>
      <EmptyState v-else icon="user" text="暂无工程师信息" />

      <view v-if="config.qrcode" class="qr-card">
        <view class="qr-title">
          <SvgIcon name="deviceMobile" :size="20" color="#165DFF" />
          <text>关注公众号</text>
        </view>
        <image :src="config.qrcode" class="qr-img" mode="widthFix" />
      </view>

      <view class="safe-bottom" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'
import PageNavbar from '@/components/PageNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'
import SvgIcon from '@/components/SvgIcon.vue'
import EngineerCard from '@/components/EngineerCard.vue'

const config = ref({})
const engineers = ref([])

const loadConfig = async () => { try { config.value = await get('/config') || {} } catch {} }
const loadEngineers = async () => { try { const r = await get('/public/engineers'); engineers.value = Array.isArray(r) ? r : (r?.records || []) } catch {} }

const openMap = () => {
  const c = config.value
  if (c.lat && c.lng) uni.openLocation({ latitude: Number(c.lat), longitude: Number(c.lng), name: c.siteName || '鸿瑞办公', address: c.address || '', scale: 16 })
  else if (c.address) uni.showToast({ title: `地址：${c.address}`, icon: 'none', duration: 3000 })
}

onMounted(() => { loadConfig(); loadEngineers() })
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F5F7FA; display: flex; flex-direction: column; position: relative; }
.scroll-body { flex: 1; }

/* 公司 hero（顶部让位给透明 Navbar） */
.company-hero {
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%);
  padding: calc(env(safe-area-inset-top) + 150rpx) 32rpx 100rpx;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.company-hero::before {
  content: '';
  position: absolute;
  top: -100rpx;
  right: -80rpx;
  width: 320rpx;
  height: 320rpx;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
  border-radius: 50%;
}
.company-logo {
  width: 128rpx;
  height: 128rpx;
  border-radius: 32rpx;
  background: rgba(255, 255, 255, 0.2);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24rpx;
  position: relative;
  z-index: 1;
  color: #fff;
  font-size: 56rpx;
  font-weight: 800;
  backdrop-filter: blur(8px);
}
.company-name { color: #fff; font-size: 40rpx; font-weight: 700; display: block; position: relative; z-index: 1; }
.company-slogan { color: rgba(255, 255, 255, 0.8); font-size: 26rpx; display: block; margin-top: 8rpx; position: relative; z-index: 1; }

/* 信息卡（负 margin 叠在 hero 上） */
.company-info-card {
  margin: -60rpx 24rpx 0;
  background: #fff;
  border-radius: 32rpx;
  padding: 16rpx 28rpx;
  box-shadow: 0 16rpx 60rpx rgba(22, 93, 255, 0.12);
  position: relative;
  z-index: 2;
}
.company-info-item {
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #F2F3F5;
  &:last-child { border-bottom: none; }
}
.company-info-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.blue   { background: linear-gradient(135deg, #165DFF, #4080FF); }
  &.green  { background: linear-gradient(135deg, #00B42A, #23C343); }
  &.orange { background: linear-gradient(135deg, #FF7D00, #FF9A2E); }
}
.company-info-text { flex: 1; min-width: 0; }
.company-info-label { font-size: 24rpx; color: #86909C; display: block; margin-bottom: 6rpx; }
.company-info-value { font-size: 28rpx; color: #1D2129; font-weight: 500; line-height: 1.5; }

/* 地图占位 */
.map-placeholder {
  margin: 24rpx 24rpx 0;
  height: 320rpx;
  border-radius: 32rpx;
  background: linear-gradient(135deg, #E8F0FE 0%, #F0F4FF 50%, #E8F0FE 100%);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(22, 93, 255, 0.08);
}
.map-placeholder::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image:
    linear-gradient(90deg, rgba(22, 93, 255, 0.06) 1px, transparent 1px),
    linear-gradient(rgba(22, 93, 255, 0.06) 1px, transparent 1px);
  background-size: 60rpx 60rpx;
}
.map-road {
  position: absolute;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8rpx;
}
.map-road-1 { top: 80rpx; left: -20rpx; right: -20rpx; height: 24rpx; transform: rotate(-3deg); }
.map-road-2 { top: 180rpx; left: -20rpx; right: -20rpx; height: 20rpx; transform: rotate(2deg); }
.map-road-3 { top: -20rpx; bottom: -20rpx; left: 120rpx; width: 20rpx; transform: rotate(1deg); }
.map-road-4 { top: -20rpx; bottom: -20rpx; right: 160rpx; width: 16rpx; transform: rotate(-2deg); }
.map-pin {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -100%);
  z-index: 2;
}
.map-pin-icon {
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #F53F3F, #F76560);
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(245, 63, 63, 0.4);
  border: 6rpx solid #fff;
}
.map-pin-icon::after {
  content: '';
  width: 24rpx;
  height: 24rpx;
  background: #fff;
  border-radius: 50%;
  transform: rotate(45deg);
}
.map-pin-pulse {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: rgba(245, 63, 63, 0.2);
  animation: pulse 2s ease-out infinite;
}
@keyframes pulse {
  0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}
.map-info-tag {
  position: absolute;
  top: 24rpx;
  left: 24rpx;
  max-width: 80%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 16rpx 20rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  gap: 10rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
  z-index: 3;

  text {
    font-size: 22rpx;
    color: #4E5969;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

/* 悬浮在地图右下角的导航按钮 */
.map-nav-btn {
  position: absolute;
  right: 24rpx;
  bottom: 24rpx;
  z-index: 3;
  padding: 16rpx 32rpx;
  border-radius: 40rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 24rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8rpx;
  box-shadow: 0 8rpx 20rpx rgba(22, 93, 255, 0.35);
  &:active { opacity: 0.9; transform: scale(0.97); }
}

/* 工程师团队标题 */
.engineer-section-title {
  padding: 24rpx 32rpx 20rpx;
  display: flex;
  align-items: center;
  gap: 10rpx;
}
.engineer-section-main { font-size: 32rpx; font-weight: 700; color: #1D2129; white-space: nowrap; }
.engineer-section-divider { width: 2rpx; height: 28rpx; background: #E5E6EB; margin: 0 8rpx; }
.engineer-section-slogan { font-size: 24rpx; color: #86909C; font-weight: 400; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.engineer-list { padding: 0 24rpx; }

.qr-card {
  margin: 24rpx;
  background: #fff;
  border-radius: 28rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.qr-title { display: flex; align-items: center; gap: 8rpx; font-size: 30rpx; font-weight: 700; color: #1D2129; }
.qr-img { width: 320rpx; margin-top: 20rpx; }

.safe-bottom { height: 40rpx; }
</style>
