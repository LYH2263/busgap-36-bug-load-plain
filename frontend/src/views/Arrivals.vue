<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { notifyDataChanged } from '../viewHints'
const rows = ref<any[]>([])
onMounted(async () => { rows.value = await api('/arrivals') })
async function toggleSaturated(r: any, ev: Event) {
  const saturated = (ev.target as HTMLInputElement).checked
  // 以服务端确认的新勾选为准,提交完成瞬间广播重算,不保留改前缓存
  const saved = await api(`/arrivals/${r.id}`, { method: 'PATCH', body: JSON.stringify({ saturated }) })
  r.saturated = saved.saturated
  notifyDataChanged()
}
</script>
<template>
  <h1>到站</h1>
  <p class="sub">各班次实际到站记录,可单站登记载客饱和</p>
  <div class="card">
    <table>
      <thead><tr><th>班次</th><th>站序</th><th>站点</th><th>实际到站</th><th>饱和</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id ?? JSON.stringify(r)">
          <td>{{ r.trip_no }}</td><td>{{ r.stop_seq }}</td><td>{{ r.stop_name }}</td><td>{{ r.actual_arrive }}</td>
          <td>
            <label class="sat-check">
              <input type="checkbox" :checked="r.saturated" @change="toggleSaturated(r, $event)" />
              <span v-if="r.saturated" class="badge badge-severe">满载</span>
            </label>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
