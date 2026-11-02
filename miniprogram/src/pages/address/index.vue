<!--
  地址管理 — 服务地址簿（默认地址优先）
  支持新增 / 编辑 / 删除 / 设为默认
-->
<template>
  <view class="page">
    <PageNavbar title="地址管理" />

    <scroll-view scroll-y class="scroll-body">
      <view v-if="loading" class="loading-box">
        <text class="loading-text">加载中...</text>
      </view>

      <template v-else>
        <view v-if="list.length" class="address-list">
          <view v-for="a in list" :key="a.id" class="address-card">
            <view class="address-card-head">
              <view class="address-user">
                <text class="address-name">{{ a.contactName }}</text>
                <text class="address-phone">{{ a.contactPhone }}</text>
                <text v-if="a.isDefault" class="address-default-tag">默认</text>
              </view>
              <view class="address-actions">
                <view v-if="!a.isDefault" class="addr-act" @click="onSetDefault(a)">
                  <SvgIcon name="check" :size="16" color="#165DFF" />
                  <text>设为默认</text>
                </view>
                <view class="addr-act" @click="onEdit(a)">
                  <SvgIcon name="notePencil" :size="16" color="#4E5969" />
                </view>
                <view class="addr-act" @click="onDelete(a)">
                  <SvgIcon name="x" :size="16" color="#F53F3F" />
                </view>
              </view>
            </view>
            <view class="address-body">
              <SvgIcon name="mapPin" :size="18" color="#165DFF" />
              <text class="address-text">{{ a.address }}</text>
            </view>
          </view>
        </view>

        <EmptyState v-else icon="mapPin" text="暂无收货地址" sub-text="点击下方按钮添加常用地址" />
      </template>

      <view class="safe-bottom" />
    </scroll-view>

    <!-- 底部新增按钮 -->
    <view class="bottom-bar">
      <button class="primary-btn" @click="onAdd">
        <SvgIcon name="plus" :size="18" color="#fff" />
        <text>新增地址</text>
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAddressStore } from '@/stores/address'
import PageNavbar from '@/components/PageNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'
import SvgIcon from '@/components/SvgIcon.vue'

const router = useRouter()
const addressStore = useAddressStore()

const loading = ref(true)
const list = ref([])

const loadList = async () => {
  try {
    list.value = await addressStore.fetchList()
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
}

const onAdd = () => router.push('/pages/address-edit/index')
const onEdit = (a) => router.push(`/pages/address-edit/index?id=${a.id}`)

const onSetDefault = async (a) => {
  try {
    await addressStore.setDefault(a.id)
    uni.showToast({ title: '已设为默认', icon: 'none' })
    loadList()
  } catch { /* 已 toast */ }
}

const onDelete = (a) => {
  uni.showModal({
    title: '提示',
    content: '确定删除该地址吗？',
    success: async (res) => {
      if (!res.confirm) return
      try {
        await addressStore.remove(a.id)
        uni.showToast({ title: '已删除', icon: 'none' })
        loadList()
      } catch { /* 已 toast */ }
    }
  })
}

onMounted(loadList)
</script>

<style lang="scss" scoped>
.page { height: 100vh; background: #F5F7FA; display: flex; flex-direction: column; }
.scroll-body { flex: 1; }

.loading-box { display: flex; justify-content: center; padding: 120rpx 0; }
.loading-text { font-size: 28rpx; color: #86909C; }

.address-list { padding: 24rpx; display: flex; flex-direction: column; gap: 20rpx; }
.address-card {
  background: #fff;
  border-radius: 28rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
}
.address-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}
.address-user { display: flex; align-items: center; gap: 16rpx; flex-wrap: wrap; }
.address-name { font-size: 32rpx; font-weight: 600; color: #1D2129; }
.address-phone { font-size: 26rpx; color: #4E5969; }
.address-default-tag {
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  font-weight: 600;
  background: #E8F3FF;
  color: #165DFF;
}
.address-actions { display: flex; align-items: center; gap: 20rpx; }
.addr-act {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 22rpx;
  color: #4E5969;
  padding: 8rpx 0;
}
.address-body {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #F2F3F5;
}
.address-text { flex: 1; font-size: 28rpx; color: #1D2129; line-height: 1.5; }

/* 底部按钮 */
.bottom-bar {
  flex-shrink: 0;
  padding: 20rpx 24rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #F2F3F5;
}
.primary-btn {
  width: 100%;
  height: 92rpx;
  background: linear-gradient(135deg, #165DFF, #4080FF);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  box-shadow: 0 12rpx 32rpx rgba(22, 93, 255, 0.3);
  &:active { opacity: 0.9; transform: scale(0.98); }
}

.safe-bottom { height: 24rpx; }
</style>
