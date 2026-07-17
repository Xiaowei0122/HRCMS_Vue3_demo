import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'

const _dirname = fileURLToPath(new URL('.', import.meta.url))

/**
 * Vite 插件：将 uni-app 的 rpx 单位转换为 px（1rpx ≈ 0.5px）
 */
function rpxToPx() {
  const RpxRE = /(\d+(?:\.\d+)?)rpx/g
  return {
    name: 'rpx-to-px',
    enforce: 'pre',
    transform(code, id) {
      if (!/(\.vue|\.scss|\.css|\.sass)/.test(id)) return
      if (!RpxRE.test(code)) return
      RpxRE.lastIndex = 0
      return {
        code: code.replace(RpxRE, (_, num) => {
          const px = Math.round(Number(num) * 0.5)
          return px > 0 ? px + 'px' : '1px'
        }),
        map: null
      }
    }
  }
}

export default defineConfig({
  plugins: [
    rpxToPx(),
    vue()
  ],
  resolve: {
    alias: {
      '@': path.resolve(_dirname, 'src'),
    }
  },
  server: {
    port: 5174,
    host: '0.0.0.0'
  },
  css: {
    preprocessorOptions: {
      scss: {
        silenceDeprecations: ['legacy-js-api', 'import'],
        quietDeps: true
      }
    }
  }
})
