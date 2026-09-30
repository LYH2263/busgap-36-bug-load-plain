<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { api } from '../api'
import { onDataChanged, unifyStatusLabel } from '../viewHints'
const data = ref<{ stop_name: string; marks: any[] }>({ stop_name: '', marks: [] })
let off: (() => void) | undefined
async function load() {
  data.value = await api('/reports/timeline?line_id=1')
}
onMounted(async () => {
  await load()
  off = onDataChanged(load)
})
onUnmounted(() => off?.())
</script>
<template>
  <h1>时间轴明细</h1>
  <p class="sub">站点「{{ data.stop_name }}」到站分布（顶部已展示发车间隔轴）</p>
  <div class="card">
    <div class="tl-track">
      <div v-for="m in data.marks" :key="m.trip_no" class="tl-mark"
        :class="'tl-' + m.status"
        :style="{ left: m.pct + '%' }"
        :title="m.trip_no + ' ' + m.actual_arrive + ' · ' + unifyStatusLabel(m.status)" />
    </div>
    <table>
      <thead><tr><th>班次</th><th>到站时间</th><th>相对位置</th><th>档位标签</th><th>建议</th></tr></thead>
      <tbody>
        <tr v-for="m in data.marks" :key="m.trip_no">
          <td>{{ m.trip_no }}</td><td>{{ m.actual_arrive }}</td><td>{{ m.pct }}%</td>
          <td><span class="badge" :class="{
            'badge-severe': m.status === 'bunching_saturated',
            'badge-bad': m.status === 'bunching',
            'badge-warn': m.status === 'large_gap',
            'badge-ok': m.status === 'normal',
          }">{{ unifyStatusLabel(m.status) }}</span></td>
          <td class="muted">{{ m.suggestion || '—' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
