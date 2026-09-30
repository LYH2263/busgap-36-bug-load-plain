import { ref } from 'vue'

// 饱和勾选提交成功后的重算信号。
// 只允许在 PATCH 成功返回(后端已 commit)之后 bump,
// 这样所有监听者重新拉取的检测结果必然基于新勾选,不会吃改前缓存。
export const saturationVersion = ref(0)

export function bumpSaturation(): void {
  saturationVersion.value += 1
}
