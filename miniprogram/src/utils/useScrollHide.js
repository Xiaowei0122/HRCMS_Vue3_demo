/**
 * 滚动隐藏标题组合式函数
 * 用于「PageNavbar 在上 + 下方 scroll-view」的页面：内容上滑超过阈值时隐藏主标题，
 * 回到顶部再显示。依赖原生 @scroll 事件（scroll-view 在浏览器中是 overflow-y:auto 的 div）。
 *
 * 用法：
 *   const { scrolled, onScroll } = useScrollHide()
 *   <scroll-view scroll-y @scroll="onScroll"> ... </scroll-view>
 *   <PageNavbar :scrolled="scrolled" ... />
 */
import { ref } from 'vue'

export function useScrollHide(threshold = 40) {
  const scrolled = ref(false)

  const onScroll = (e) => {
    const top = e?.target?.scrollTop ?? e?.detail?.scrollTop ?? 0
    scrolled.value = top > threshold
  }

  return { scrolled, onScroll }
}
