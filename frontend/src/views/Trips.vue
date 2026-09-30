<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { api } from '../api'
import { notifyDataChanged, onDataChanged, unifyStatusLabel } from '../viewHints'
const trips = ref<any[]>([])
const events = ref<any[]>([])
async function refreshEvents() {
  // 每次按库内最新勾选现算
  try {
    events.value = (await api('/reports/run?line_id=1', { method: 'POST' })).events || []
  } catch { events.value = [] }
}
let off: (() => void) | undefined
onMounted(async () => {
  trips.value = await api('/trips')
  await refreshEvents()
  off = onDataChanged(refreshEvents)
})
onUnmounted(() => off?.())
async function toggleSaturated(r: any, ev: Event) {
  const saturated = (ev.target as HTMLInputElement).checked
  const saved = await api(`/trips/${r.id}`, { method: 'PATCH', body: JSON.stringify({ saturated }) })
  r.saturated = saved.saturated
  // 提交瞬间先按新勾选重算,再广播给顶部轴等视图
  await refreshEvents()
  notifyDataChanged()
}
function stripClass(s: string) {
  return s === 'bunching' ? 'bg-bunch' : s === 'bunching_saturated' ? 'bg-severe' : s === 'large_gap' ? 'bg-large' : ''
}
function label(s: string) {
  return unifyStatusLabel(s)
}
function badgeClass(s: string) {
  return s === 'bunching' ? 'badge-bad' : s === 'bunching_saturated' ? 'badge-severe' : s === 'large_gap' ? 'badge-warn' : 'badge-ok'
}
</script>
<template>
  <h1>班次 · 间隔条带</h1>
  <p class="sub">左侧班次清单(可勾载客饱和),右侧串车/间隔竖直条带</p>
  <p class="muted">状态、建议句与时间轴标签同源同档</p>
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
          <p class="muted">{{ e.suggestion }}</p>
        </div>
      </article>
      <p v-if="!events.length" class="muted">暂无间隔事件</p>
    </div>
  </div>
</template>
