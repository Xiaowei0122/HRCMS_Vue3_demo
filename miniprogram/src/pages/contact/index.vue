<!--
  联系我们
-->
<template>
  <view class="page">
    <scroll-view scroll-y class="scroll-body">
      <!-- 公司信息 -->
      <view class="card company-card">
        <view class="logo-circle"><text class="logo-t">鸿瑞</text></view>
        <text class="cname">{{ config.siteName || '鸿瑞办公' }}</text>
        <text class="cdesc" v-if="config.description">{{ config.description }}</text>

        <view class="info-list">
          <view class="info-item" v-if="config.servicePhone">
            <SvgIcon name="phone" :size="18" class="ii-icon" />
            <view class="ii-body"><text class="ii-label">服务热线</text><text class="ii-val">{{ config.servicePhone }}</text></view>
          </view>
          <view class="info-item" v-if="config.businessPhone">
            <SvgIcon name="deviceMobile" :size="18" class="ii-icon" />
            <view class="ii-body"><text class="ii-label">合作电话</text><text class="ii-val">{{ config.businessPhone }}</text></view>
          </view>
          <view class="info-item" v-if="config.address">
            <SvgIcon name="mapPin" :size="18" class="ii-icon" />
            <view class="ii-body"><text class="ii-label">公司地址</text><text class="ii-val">{{ config.address }}</text></view>
          </view>
          <view class="info-item" v-if="config.businessHours">
            <SvgIcon name="clock" :size="18" class="ii-icon" />
            <view class="ii-body"><text class="ii-label">营业时间</text><text class="ii-val">{{ config.businessHours }}</text></view>
          </view>
        </view>

        <button class="btn-nav" @click="openMap"><SvgIcon name="mapPin" :size="16" /><text>导航到公司</text></button>
      </view>

      <!-- 工程师团队 -->
      <view class="card">
        <view class="sec-head">
          <view class="sec-row"><SvgIcon name="wrench" :size="20" /><text class="sec-title">工程师团队</text></view>
          <text class="sec-desc">专业认证 · 经验丰富 · 快速响应</text>
        </view>
        <view v-if="engineers.length" class="eng-grid">
          <view v-for="e in engineers" :key="e._id || e.id" class="eng-card">
            <view class="eng-avatar"><text class="eng-at">{{ (e.name || '工').charAt(0) }}</text></view>
            <text class="eng-name">{{ e.name }}</text>
            <text class="eng-skill">{{ e.skills || e.team || '技术支持' }}</text>
            <view class="eng-call" @click="callEngineer(e.phone)"><SvgIcon name="phone" :size="12" /><text>联系</text></view>
          </view>
        </view>
        <EmptyState v-else icon="wrench" text="暂无工程师信息" />
      </view>

      <view v-if="config.qrcode" class="card qr-card">
        <view class="sec-row"><SvgIcon name="deviceMobile" :size="20" /><text class="sec-title">关注公众号</text></view>
        <image :src="config.qrcode" class="qr-img" mode="widthFix" />
      </view>

      <view class="safe-bottom" />
    </scroll-view>
    <CustomTabBar />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '@/utils/request'
import CustomTabBar from '@/components/CustomTabBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import SvgIcon from '@/components/SvgIcon.vue'

const config = ref({})
const engineers = ref([])

const loadConfig = async () => { try { config.value = await get('/config') || {} } catch {} }
const loadEngineers = async () => { try { const r = await get('/contact/engineers'); engineers.value = Array.isArray(r) ? r : (r?.records || []) } catch {} }

const openMap = () => {
  const c = config.value
  if (c.lat && c.lng) uni.openLocation({ latitude: Number(c.lat), longitude: Number(c.lng), name: c.siteName || '鸿瑞办公', address: c.address || '', scale: 16 })
  else if (c.address) uni.showToast({ title: `地址：${c.address}`, icon: 'none', duration: 3000 })
}
const callEngineer = (phone) => { if (phone) uni.makePhoneCall({ phoneNumber: phone }) }

onMounted(() => { loadConfig(); loadEngineers() })
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F8FAFC; display: flex; flex-direction: column; }
.scroll-body { flex: 1; }

.card { margin: 16rpx 24rpx; background: #fff; border-radius: 16rpx; padding: 28rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,.04); }

/* 公司卡片 */
.company-card { display: flex; flex-direction: column; align-items: center; padding: 40rpx 32rpx; }
.logo-circle { width: 100rpx; height: 100rpx; border-radius: 50%; background: #0F172A; display: flex; align-items: center; justify-content: center; margin-bottom: 16rpx; }
.logo-t { font-size: 40rpx; font-weight: 800; color: #fff; }
.cname { font-size: 32rpx; font-weight: 700; color: #020617; }
.cdesc { font-size: 24rpx; color: #64748B; margin-top: 8rpx; text-align: center; }

.info-list { width: 100%; margin-top: 32rpx; }
.info-item { display: flex; align-items: flex-start; padding: 16rpx 0; border-bottom: 1px solid #E2E8F0; }
.info-item:last-child { border-bottom: none; }
.ii-icon { margin-right: 16rpx; flex-shrink: 0; color: #0369A1; margin-top: 4rpx; }
.ii-body { flex: 1; }
.ii-label { font-size: 22rpx; color: #64748B; display: block; }
.ii-val { font-size: 26rpx; color: #334155; margin-top: 4rpx; }

.btn-nav { width: 100%; height: 80rpx; line-height: 80rpx; background: #0F172A; color: #fff; font-size: 28rpx; font-weight: 600; border: none; border-radius: 40rpx; margin-top: 28rpx; display: flex; align-items: center; justify-content: center; gap: 8rpx; }
.btn-nav:active { opacity: .85; }

/* 工程师 */
.sec-head { margin-bottom: 20rpx; }
.sec-row { display: flex; align-items: center; gap: 8rpx; }
.sec-title { font-size: 28rpx; font-weight: 700; color: #020617; }
.sec-desc { font-size: 24rpx; color: #64748B; margin-top: 4rpx; }

.eng-grid { display: flex; flex-wrap: wrap; gap: 16rpx; }
.eng-card { width: calc(50% - 8rpx); background: #F1F5F9; border-radius: 14rpx; padding: 24rpx; display: flex; flex-direction: column; align-items: center; transition: all .25s; }
.eng-card:active { transform: scale(.96); }
.eng-avatar { width: 72rpx; height: 72rpx; border-radius: 50%; background: #0F172A; display: flex; align-items: center; justify-content: center; margin-bottom: 12rpx; }
.eng-at { font-size: 30rpx; font-weight: 700; color: #fff; }
.eng-name { font-size: 28rpx; font-weight: 600; color: #020617; }
.eng-skill { font-size: 22rpx; color: #64748B; margin: 4rpx 0 12rpx; }
.eng-call { display: flex; align-items: center; gap: 6rpx; padding: 6rpx 24rpx; background: #fff; border: 1px solid #0369A1; border-radius: 30rpx; font-size: 22rpx; color: #0369A1; }
.eng-call:active { background: #F0F9FF; }

.qr-card { display: flex; flex-direction: column; align-items: center; }
.qr-img { width: 320rpx; margin-top: 16rpx; }

.safe-bottom { height: 32rpx; }
</style>
