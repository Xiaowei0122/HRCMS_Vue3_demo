import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue' // 必须引入这个插件

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue() // 必须在这里调用插件
  ],
})