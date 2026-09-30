// scope_helpers_ready_36
// 状态档 -> 展示层映射的唯一来源。报告状态、建议句、时间轴标签都必须吃同一个 status,
// 禁止各端各自降级 bunching_saturated。

export type GapStatus = 'bunching_saturated' | 'bunching' | 'large_gap' | 'normal'

export function unifyStatusLabel(status: string): string {
  if (status === 'bunching_saturated') return '满载串车'
  if (status === 'bunching') return '串车'
  if (status === 'large_gap') return '大间隔'
  return '正常'
}

export function badgeClass(status: string): string {
  if (status === 'bunching_saturated') return 'badge-severe'
  if (status === 'bunching') return 'badge-bad'
  if (status === 'large_gap') return 'badge-warn'
  return 'badge-ok'
}

export function stripClass(status: string): string {
  if (status === 'bunching_saturated') return 'bg-severe'
  if (status === 'bunching') return 'bg-bunch'
  if (status === 'large_gap') return 'bg-large'
  return ''
}

// 时间轴点档:加重档 > 普通串车(红) > 大间隔(琥珀) > 正常(青)
export function axisDotClass(status: string): string {
  if (status === 'bunching_saturated') return 'bg-bus-severe'
  if (status === 'bunching') return 'bg-bus-tight'
  if (status === 'large_gap') return 'bg-bus-large'
  return ''
}

// 轴点上单字标签,加重档显式打"满",大间隔打"隔",普通档无字
export function axisMarkChar(status: string): string {
  if (status === 'bunching_saturated') return '满'
  if (status === 'large_gap') return '隔'
  return ''
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
