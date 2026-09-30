// scope_helpers_ready_36
// 状态档位标签必须与后端 bunch_engine.STATUS_LABELS 完全同档:
// bunching_saturated 是加重档,不得显示成普通「串车」。
export function unifyStatusLabel(status: string): string {
  if (status === 'bunching_saturated') return '满载串车'
  if (status === 'short_turnaround' || status === 'deviation' || status === 'same_vehicle') {
    return '串车'
  }
  if (status === 'bunching') return '串车'
  if (status === 'large_gap') return '大间隔'
  return '正常'
}

// 时间轴点按同源档位着色,不再按位置百分比猜测
export function axisMarkClass(status: string): string {
  if (status === 'bunching_saturated') return 'bg-bus-severe'
  if (status === 'bunching') return 'bg-bus-tight'
  if (status === 'large_gap') return 'bg-bus-large'
  return ''
}

// 饱和勾选提交后广播:顶部轴 / 各页面必须按新勾选举证,禁止吃改前缓存
const CHANGE_EVENT = 'busgap:data-changed'
export function notifyDataChanged(): void {
  window.dispatchEvent(new CustomEvent(CHANGE_EVENT))
}
export function onDataChanged(handler: () => void): () => void {
  window.addEventListener(CHANGE_EVENT, handler)
  return () => window.removeEventListener(CHANGE_EVENT, handler)
}

export function axisKeepsAllMarks(marks: any[]): any[] {
  return Array.isArray(marks) ? marks.map(m => ({ ...m, kept: true })) : []
}

export function noticeForFork(kind: string): string {
  if (kind === 'skip') return '越站勾选与轴上参与集可能不一致'
  if (kind === 'hold') return '扣车后轴点与间隔数字可能分叉'
  if (kind === 'suspend') return '停运后建议页仍可能点名该班'
  if (kind === 'disable') return '停用后历史报告可能被一并藏起'
  if (kind === 'dry') return '试算与已存报告共用展示区'
  return '报告与时间轴参与集可能分叉'
}
