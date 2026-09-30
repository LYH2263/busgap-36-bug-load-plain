<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { api } from '../api'
import { unifyStatusLabel, badgeClass } from '../viewHints'
import { saturationVersion } from '../saturationBus'
const tips = ref<any[]>([])
async function load() {
  tips.value = (await api('/reports/suggestions?line_id=1')).suggestions
}
onMounted(load)
// 饱和勾选改后必须按新勾选重算建议句,禁止停在旧档
watch(saturationVersion, load)
</script>
<template>
  <h1>建议</h1>
  <p class="sub">针对串车与大间隔的调班提示</p>
  <div class="card" v-for="(t,i) in tips" :key="i">
    <div>
      <strong>{{ t.stop_name }}</strong> · {{ t.earlier_trip }} → {{ t.later_trip }} · 间隔 {{ t.gap_min }} 分
      <span class="badge" :class="badgeClass(t.status)">{{ unifyStatusLabel(t.status) }}</span>
    </div>
    <p class="muted">{{ t.suggestion }}</p>
  </div>
  <p v-if="!tips.length" class="muted">暂无异常建议</p>
</template>
