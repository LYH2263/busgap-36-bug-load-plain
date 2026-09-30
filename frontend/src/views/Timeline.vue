<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { api } from '../api'
import { unifyStatusLabel, badgeClass, axisDotClass, axisMarkChar } from '../viewHints'
import { saturationVersion } from '../saturationBus'
const data = ref<{ stop_name: string; marks: any[] }>({ stop_name: '', marks: [] })
async function load() {
  data.value = await api('/reports/timeline?line_id=1')
}
onMounted(load)
watch(saturationVersion, load)
</script>
<template>
  <h1>时间轴明细</h1>
  <p class="sub">站点「{{ data.stop_name }}」到站分布（顶部已展示发车间隔轴）· 轴点档位与报告同源</p>
  <div class="card">
    <div class="tl-track">
      <div v-for="m in data.marks" :key="m.trip_no" class="tl-mark"
        :class="axisDotClass(m.status)"
        :title="m.trip_no + ' ' + m.actual_arrive + ' ' + unifyStatusLabel(m.status)">
        <span v-if="axisMarkChar(m.status)" class="tl-mark-char">{{ axisMarkChar(m.status) }}</span>
      </div>
    </div>
    <table>
      <thead><tr><th>班次</th><th>到站时间</th><th>相对位置</th><th>状态</th></tr></thead>
      <tbody>
        <tr v-for="m in data.marks" :key="m.trip_no">
          <td>{{ m.trip_no }}</td><td>{{ m.actual_arrive }}</td><td>{{ m.pct }}%</td>
          <td><span class="badge" :class="badgeClass(m.status)">{{ unifyStatusLabel(m.status) }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
