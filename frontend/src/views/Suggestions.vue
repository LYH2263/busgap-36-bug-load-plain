<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { api } from '../api'
import { onDataChanged, unifyStatusLabel } from '../viewHints'
const tips = ref<any[]>([])
async function load() {
  tips.value = (await api('/reports/suggestions?line_id=1')).suggestions
}
let off: (() => void) | undefined
onMounted(async () => {
  await load()
  off = onDataChanged(load)
})
onUnmounted(() => off?.())
function label(s: string) {
  return unifyStatusLabel(s)
}
function badgeClass(s: string) {
  return s === 'bunching' ? 'badge-bad' : s === 'bunching_saturated' ? 'badge-severe' : s === 'large_gap' ? 'badge-warn' : 'badge-ok'
}
</script>
<template>
  <h1>建议</h1>
  <p class="sub">针对串车与大间隔的调班提示</p>
  <div class="card" v-for="(t,i) in tips" :key="i">
    <div>
      <strong>{{ t.stop_name }}</strong> · {{ t.earlier_trip }} → {{ t.later_trip }} · 间隔 {{ t.gap_min }} 分
      <span class="badge" :class="badgeClass(t.status)">{{ label(t.status) }}</span>
    </div>
    <p class="muted">{{ t.suggestion }}</p>
  </div>
  <p v-if="!tips.length" class="muted">暂无异常建议</p>
</template>
