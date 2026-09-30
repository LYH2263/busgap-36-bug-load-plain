"""Bus bunching: planned headway vs actual arrival gaps.

分档规则（三档互斥,饱和只能加重短间隔一档）:
- 间隔低于串车阈值 + 后车已饱和 -> bunching_saturated(满载串车)
- 间隔低于串车阈值 + 后车未饱和 -> bunching(普通串车)
- 间隔超过大间隔阈值 -> large_gap,与饱和无关,措辞不得被饱和牵动
- 其余 -> normal,与饱和无关
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime

@dataclass
class GapEvent:
    stop_name: str
    earlier_trip: str
    later_trip: str
    gap_min: float
    planned_headway_min: float
    status: str
    suggestion: str
    saturated: bool = False

def classify_gap(gap_min: float, planned_headway_min: float, bunch_threshold: float, large_threshold: float,
                 later_saturated: bool = False) -> tuple[str, str]:
    if gap_min < bunch_threshold:
        if later_saturated:
            return ("bunching_saturated",
                    f"间隔 {gap_min:.1f} 分钟低于串车阈值 {bunch_threshold}，后车已载客饱和，属满载串车，建议优先抽稀。")
        return ("bunching", f"间隔 {gap_min:.1f} 分钟低于串车阈值 {bunch_threshold}，建议后车缓行或抽稀。")
    if gap_min > large_threshold:
        # 大间隔档与饱和勾选完全无关,不得改字
        return ("large_gap", f"间隔 {gap_min:.1f} 分钟超过大间隔阈值 {large_threshold}，建议前车减速或加发。")
    return ("normal", f"间隔接近计划 {planned_headway_min:.1f} 分钟，保持即可。")

def detect_bunching(arrivals: list[dict], planned_headway_min: float, bunch_threshold: float, large_threshold: float) -> list[GapEvent]:
    by_stop: dict[str, list[dict]] = {}
    for a in arrivals:
        by_stop.setdefault(a["stop_name"], []).append(a)
    events: list[GapEvent] = []
    for stop, items in by_stop.items():
        items = sorted(items, key=lambda x: x["actual_arrive"])
        for i in range(1, len(items)):
            prev, cur = items[i - 1], items[i]
            gap_min = (cur["actual_arrive"] - prev["actual_arrive"]).total_seconds() / 60.0
            # 以后车(相邻后一班)的最新饱和勾选为准,每次检测实时读取,不吃调用方旧缓存
            later_saturated = bool(cur.get("saturated", False))
            status, suggestion = classify_gap(gap_min, planned_headway_min, bunch_threshold, large_threshold,
                                              later_saturated=later_saturated)
            events.append(GapEvent(stop, prev["trip_no"], cur["trip_no"], round(gap_min, 2), planned_headway_min,
                                   status, suggestion, status == "bunching_saturated"))
    return events

def events_to_dicts(events: list[GapEvent]) -> list[dict]:
    return [asdict(e) for e in events]
