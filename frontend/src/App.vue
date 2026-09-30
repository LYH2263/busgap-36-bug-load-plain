<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { api } from './api'
import { axisMarkClass, onDataChanged } from './viewHints'

const marks = ref<any[]>([])
const stopName = ref('')
let off: (() => void) | undefined

async function loadTimeline() {
  // 每次都重新请求,勾选饱和提交后必须按新勾选重算,禁止吃改前缓存
  try {
    const data = await api('/reports/timeline?line_id=1')
    marks.value = data.marks || []
    stopName.value = data.stop_name || ''
  } catch {
    marks.value = []
  }
}

onMounted(async () => {
  await loadTimeline()
  off = onDataChanged(loadTimeline)
})
onUnmounted(() => off?.())
</script>
<template>
  <div class="bg-shell">
    <header class="bg-headway">
      <div class="bg-headway-meta">
        <span class="bg-brand">BusGap · 串车检测</span>
        <span class="bg-stop">发车间隔轴 · {{ stopName || '主站' }}</span>
      </div>
      <div class="bg-rail">
        <div class="bg-rail-ticks">
          <span v-for="t in 11" :key="t">{{ (t - 1) * 10 }}%</span>
        </div>
        <div class="bg-rail-track">
          <div
            v-for="m in marks"
            :key="m.trip_no"
            class="bg-bus-dot"
            :class="axisMarkClass(m.status)"
            :style="{ left: m.pct + '%' }"
            :title="`${m.trip_no} ${m.actual_arrive} · ${m.status_label}${m.suggestion ? '｜' + m.suggestion : ''}`"
          >
            <span class="bg-bus-label">{{ m.trip_no }}{{ m.status_label && m.status_label !== '正常' ? ' ' + m.status_label : '' }}</span>
          </div>
        </div>
      </div>
      <nav class="bg-segments">
        <RouterLink to="/timeline">时间轴</RouterLink>
        <RouterLink to="/trips">班次</RouterLink>
        <RouterLink to="/arrivals">到站</RouterLink>
        <RouterLink to="/reports">串车报告</RouterLink>
        <RouterLink to="/lines">线路</RouterLink>
        <RouterLink to="/suggestions">建议</RouterLink>
      </nav>
    </header>
    <div class="bg-deck">
      <RouterView />
    </div>
  </div>
</template>
