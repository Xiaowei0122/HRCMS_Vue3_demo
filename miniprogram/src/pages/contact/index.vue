<!--
  联系我们页面
  展示工程师信息、公司信息、地图、地址
  与门户网站 ContactDetail.vue 风格对齐
-->
<template>
  <view class="contact-page">
    <scroll-view scroll-y class="page-scroll">
      <!-- 公司信息卡片 -->
      <view class="company-card">
        <view class="company-logo">
          <text class="logo-text">鸿瑞</text>
        </view>
        <text class="company-name">{{ config.siteName || '鸿瑞办公' }}</text>
        <text class="company-desc" v-if="config.description">{{ config.description }}</text>

        <!-- 联系信息 -->
        <view class="contact-info-grid">
          <view class="contact-item" v-if="config.servicePhone">
            <text class="ci-icon">📞</text>
            <view class="ci-content">
              <text class="ci-label">服务热线</text>
              <text class="ci-value">{{ config.servicePhone }}</text>
            </view>
          </view>
          <view class="contact-item" v-if="config.businessPhone">
            <text class="ci-icon">📱</text>
            <view class="ci-content">
              <text class="ci-label">合作电话</text>
              <text class="ci-value">{{ config.businessPhone }}</text>
            </view>
          </view>
          <view class="contact-item" v-if="config.address">
            <text class="ci-icon">📍</text>
            <view class="ci-content">
              <text class="ci-label">公司地址</text>
              <text class="ci-value">{{ config.address }}</text>
            </view>
          </view>
          <view class="contact-item" v-if="config.businessHours">
            <text class="ci-icon">🕐</text>
            <view class="ci-content">
              <text class="ci-label">营业时间</text>
              <text class="ci-value">{{ config.businessHours }}</text>
            </view>
          </view>
        </view>

        <!-- 导航按钮 -->
        <button class="btn-navigate" @click="openMap">
          🗺️ 导航到公司
        </button>
      </view>

      <!-- 工程师团队 -->
      <view class="section-card">
        <view class="section-header">
          <text class="section-title">🔧 工程师团队</text>
          <text class="section-desc">专业认证 · 经验丰富 · 快速响应</text>
        </view>

        <view v-if="engineers.length > 0" class="engineer-grid">
          <view v-for="eng in engineers" :key="eng._id || eng.id" class="engineer-card">
            <view class="eng-avatar">
              <text class="eng-avatar-text">{{ (eng.name || '工').charAt(0) }}</text>
            </view>
            <text class="eng-name">{{ eng.name }}</text>
            <text class="eng-title">{{ eng.skills || eng.team || '技术支持' }}</text>
            <view class="eng-contact-btn" @click="callEngineer(eng.phone)">
              <text>📞 联系</text>
            </view>
          </view>
        </view>

        <EmptyState v-else icon="🔧" text="暂无工程师信息" />
      </view>

      <!-- 公众号二维码 -->
      <view class="section-card" v-if="config.qrcode">
        <view class="section-header">
          <text class="section-title">📱 关注公众号</text>
        </view>
        <img :src="config.qrcode" class="qrcode-img" />
      </view>

      <view class="safe-bottom"></view>
    </scroll-view>

    <!-- 自定义 TabBar -->
    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'
import CustomTabBar from '@/components/CustomTabBar.vue'
import EmptyState from '@/components/EmptyState.vue'

const config = ref({})
const engineers = ref([])

const loadConfig = async () => {
  try {
    const res = await get('/config')
    config.value = res || {}
  } catch { /* 门户静态数据兜底 */ }
}

const loadEngineers = async () => {
  try {
    const res = await get('/contact/engineers')
    engineers.value = Array.isArray(res) ? res : (res?.records || [])
  } catch { /* handled */ }
}

const openMap = () => {
  const { address, lat, lng } = config.value
  if (lat && lng) {
    uni.openLocation({
      latitude: Number(lat),
      longitude: Number(lng),
      name: config.value.siteName || '鸿瑞办公',
      address: address || '',
      scale: 16
    })
  } else if (address) {
    // 无坐标时用 chooseLocation 或直接显示
    uni.showToast({ title: `地址：${address}`, icon: 'none', duration: 3000 })
  }
}

const callEngineer = (phone) => {
  if (phone) {
    uni.makePhoneCall({ phoneNumber: phone })
  }
}

onMounted(() => {
  loadConfig()
  loadEngineers()
})
</script>

<style lang="scss" scoped>
.contact-page {
  min-height: 100vh;
  background: #F7F7F7;
  padding-bottom: 140rpx;
}

.page-scroll { height: 100vh; }

/* 公司卡片 */
.company-card {
  margin: 20rpx 24rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 40rpx 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.company-logo {
  width: 100rpx; height: 100rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #D32223, #B81C1D);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 16rpx;
}

.logo-text { font-size: 40rpx; font-weight: 800; color: #FFFFFF; }

.company-name { font-size: 32rpx; font-weight: 700; color: #222; }
.company-desc { font-size: 24rpx; color: #999; margin-top: 8rpx; text-align: center; }

.contact-info-grid {
  width: 100%;
  margin-top: 32rpx;
}

.contact-item {
  display: flex; align-items: flex-start;
  padding: 16rpx 0;
  border-bottom: 1px solid #F7F7F7;

  &:last-child { border-bottom: none; }
}

.ci-icon { font-size: 36rpx; margin-right: 16rpx; }
.ci-content { flex: 1; }
.ci-label  { font-size: 22rpx; color: #999; display: block; }
.ci-value  { font-size: 26rpx; color: #333; margin-top: 4rpx; }

.btn-navigate {
  width: 100%; height: 80rpx; line-height: 80rpx;
  background: #D32223; color: #FFFFFF;
  font-size: 28rpx; font-weight: 600;
  border: none; border-radius: 50rpx;
  margin-top: 28rpx; text-align: center;

  &:active { opacity: 0.85; }
}

/* 工程师 */
.section-card {
  margin: 0 24rpx 20rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
}

.section-header { margin-bottom: 20rpx; }

.section-title { font-size: 28rpx; font-weight: 700; color: #222; display: block; }
.section-desc  { font-size: 24rpx; color: #999; margin-top: 4rpx; }

.engineer-grid {
  display: flex; flex-wrap: wrap; gap: 16rpx;
}

.engineer-card {
  width: calc(50% - 8rpx);
  background: #F7F7F7;
  border-radius: 16rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s;

  &:active { transform: scale(0.96); }
}

.eng-avatar {
  width: 72rpx; height: 72rpx; border-radius: 50%;
  background: linear-gradient(135deg, #D32223, #E57373);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 12rpx;
}

.eng-avatar-text { font-size: 30rpx; font-weight: 700; color: #FFFFFF; }

.eng-name  { font-size: 28rpx; font-weight: 600; color: #222; }
.eng-title { font-size: 22rpx; color: #999; margin: 4rpx 0 12rpx; }

.eng-contact-btn {
  padding: 6rpx 24rpx;
  background: #FFFFFF; border: 1px solid #D32223;
  border-radius: 30rpx; font-size: 22rpx; color: #D32223;

  &:active { background: #FFF0F0; }
}

/* 二维码 */
.qrcode-img {
  width: 320rpx;
  display: block;
  margin: 0 auto;
}

.safe-bottom { height: 40rpx; }
</style>
