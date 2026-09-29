<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
const trips = ref<any[]>([])
const events = ref<any[]>([])
async function refreshEvents() {
  try {
    events.value = (await api('/reports/run?line_id=1', { method: 'POST' })).events || []
  } catch { events.value = [] }
}
onMounted(async () => {
  trips.value = await api('/trips')
  await refreshEvents()
})
async function toggleSaturated(r: any, ev: Event) {
  const saturated = (ev.target as HTMLInputElement).checked
  await api(`/trips/${r.id}`, { method: 'PATCH', body: JSON.stringify({ saturated }) })
  r.saturated = saturated
  await refreshEvents()
}
function stripClass(s: string) {
  return s === 'bunching' ? 'bg-bunch' : s === 'bunching_saturated' ? 'bg-severe' : s === 'large_gap' ? 'bg-large' : ''
}
function label(s: string) {
  return s === 'bunching' || s === 'bunching_saturated' ? '串车' : s === 'large_gap' ? '大间隔' : '正常'
}
function badgeClass(s: string) {
  return s === 'bunching' ? 'badge-bad' : s === 'bunching_saturated' ? 'badge-severe' : s === 'large_gap' ? 'badge-warn' : 'badge-ok'
}
</script>
<template>
  <h1>班次 · 间隔条带</h1>
  <p class="sub">左侧班次清单(可勾载客饱和),右侧串车/间隔竖直条带</p>
  <p class="muted">业务页与检测读口未强制同参与集</p>
  <div class="bg-split">
    <aside class="bg-trip-col">
      <h2>班次列表</h2>
      <div v-for="r in trips" :key="r.id ?? r.trip_no" class="bg-trip-row">
        <div>
          <div>
            {{ r.trip_no }}
            <span v-if="r.saturated" class="badge badge-severe">满载</span>
          </div>
          <div class="bg-trip-meta">线路 {{ r.line_id }} · 车 {{ r.vehicle_no }}</div>
          <label class="sat-check">
            <input type="checkbox" :checked="r.saturated" @change="toggleSaturated(r, $event)" /> 载客饱和
          </label>
        </div>
        <div class="bg-trip-meta">{{ r.planned_depart }}</div>
      </div>
    </aside>
    <div class="bg-strip-col">
      <article
        v-for="(e, i) in events"
        :key="i"
        class="bg-gap-strip"
        :class="stripClass(e.status)"
      >
        <header>{{ e.stop_name }}</header>
        <div class="bg-gap-body">
          <div class="bg-gap-val">{{ e.gap_min }}′</div>
          <div>计划 {{ e.planned_headway_min }}′</div>
          <div>{{ e.earlier_trip }} → {{ e.later_trip }}</div>
          <span class="badge" :class="badgeClass(e.status)">
            {{ label(e.status) }}
          </span>
        </div>
      </article>
      <p v-if="!events.length" class="muted">暂无间隔事件</p>
    </div>
  </div>
</template>
