import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './utils/uni-polyfill.js'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

// 启动时从 localStorage 恢复登录态（Pinia 已激活）
const authStore = useAuthStore()
authStore.checkLogin()

app.use(router)
app.mount('#app')
